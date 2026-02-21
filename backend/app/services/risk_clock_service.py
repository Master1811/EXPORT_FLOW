"""
Feature 3: RBI 9-Month Risk Clock (EDPMS Monitoring)
Monitors outstanding shipments against RBI's 9-month realization mandate.
Uses MongoDB aggregation pipelines for scalable scoring.
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from enum import Enum
import logging
from fastapi import HTTPException

from ..core.database import db
from ..core.config import settings
from ..common.utils import generate_id, now_iso
from .tenant_auth_service import TenantAuthService

logger = logging.getLogger(__name__)

# RBI EDPMS Buckets
CRITICAL_THRESHOLD = 240  # >240 days
WARNING_THRESHOLD = 210   # >210 days
MONITOR_THRESHOLD = 180   # >180 days
RBI_DEADLINE_DAYS = 270   # 9 months

RBI_LETTER_SYSTEM_MESSAGE = """You are an expert trade finance compliance assistant specializing in RBI regulations for export receivables. Draft formal letters to RBI for extension requests under FEMA guidelines.

Include:
1. Formal business letter format
2. Relevant RBI circulars and FEMA regulations
3. Mandatory details: IEC, Shipping Bill No., Invoice details, Current realization status
4. Reason for delay and proposed timeline
5. Professional, concise, regulatory-compliant language"""


class RiskClockService:
    """Service for RBI 9-month risk monitoring and compliance."""
    
    @staticmethod
    async def get_risk_clock_data(company_id: str) -> Dict[str, Any]:
        """
        MongoDB aggregation pipeline to calculate shipment aging.
        Categorizes into CRITICAL, WARNING, MONITOR buckets.
        """
        now = datetime.now(timezone.utc)
        
        # Aggregation pipeline for risk calculation
        pipeline = [
            {"$match": {
                "company_id": company_id,
                "status": {"$in": ["shipped", "delivered", "in_transit"]},
                "ebrc_status": {"$ne": "approved"}
            }},
            {"$project": {
                "_id": 0, "id": 1, "shipment_number": 1, "buyer_name": 1, "buyer_country": 1,
                "total_value": 1, "currency": 1, "status": 1, "ebrc_status": 1,
                "shipping_bill_date": {"$ifNull": ["$actual_ship_date", "$expected_ship_date", "$created_at"]},
                "created_at": 1
            }},
            {"$addFields": {
                "shipping_date_parsed": {"$dateFromString": {"dateString": "$shipping_bill_date", "onError": now}}
            }},
            {"$addFields": {
                "age_days": {"$divide": [{"$subtract": [now, "$shipping_date_parsed"]}, 1000 * 60 * 60 * 24]}
            }},
            {"$addFields": {
                "age_days": {"$floor": "$age_days"},
                "days_remaining": {"$subtract": [RBI_DEADLINE_DAYS, {"$floor": "$age_days"}]}
            }},
            {"$addFields": {
                "risk_category": {
                    "$switch": {
                        "branches": [
                            {"case": {"$gte": ["$age_days", CRITICAL_THRESHOLD]}, "then": "CRITICAL"},
                            {"case": {"$gte": ["$age_days", WARNING_THRESHOLD]}, "then": "WARNING"},
                            {"case": {"$gte": ["$age_days", MONITOR_THRESHOLD]}, "then": "MONITOR"}
                        ],
                        "default": "SAFE"
                    }
                }
            }},
            {"$sort": {"age_days": -1}}
        ]
        
        shipments = await db.shipments.aggregate(pipeline).to_list(1000)
        
        # Get payment data
        shipment_ids = [s["id"] for s in shipments]
        payments = await db.payments.find({
            "shipment_id": {"$in": shipment_ids},
            "company_id": company_id
        }, {"_id": 0}).to_list(2000)
        
        payments_by_shipment = {}
        for p in payments:
            sid = p.get("shipment_id")
            payments_by_shipment.setdefault(sid, []).append(p)
        
        # Enrich with realization data
        for shipment in shipments:
            sid = shipment["id"]
            ship_payments = payments_by_shipment.get(sid, [])
            total_value = shipment.get("total_value", 0)
            realized = sum(p.get("amount", 0) for p in ship_payments if p.get("status") in ["completed", "received", "paid"])
            
            shipment["realized_amount"] = realized
            shipment["pending_amount"] = max(0, total_value - realized)
            shipment["realization_percentage"] = round((realized / total_value * 100) if total_value > 0 else 0, 1)
            shipment["urgency_score"] = min(100, max(0, int((shipment.get("age_days", 0) - 180) / 0.9)))
        
        critical = [s for s in shipments if s.get("risk_category") == "CRITICAL"]
        warning = [s for s in shipments if s.get("risk_category") == "WARNING"]
        monitor = [s for s in shipments if s.get("risk_category") == "MONITOR"]
        safe = [s for s in shipments if s.get("risk_category") == "SAFE"]
        
        total_at_risk = sum(s.get("pending_amount", 0) for s in critical + warning + monitor)
        
        return {
            "summary": {
                "total_shipments": len(shipments),
                "critical_count": len(critical),
                "warning_count": len(warning),
                "monitor_count": len(monitor),
                "safe_count": len(safe),
                "total_at_risk_value": total_at_risk,
                "critical_value": sum(s.get("pending_amount", 0) for s in critical),
                "warning_value": sum(s.get("pending_amount", 0) for s in warning),
                "monitor_value": sum(s.get("pending_amount", 0) for s in monitor)
            },
            "buckets": {"critical": critical, "warning": warning, "monitor": monitor, "safe": safe[:10]},
            "thresholds": {"critical": CRITICAL_THRESHOLD, "warning": WARNING_THRESHOLD, "monitor": MONITOR_THRESHOLD, "deadline": RBI_DEADLINE_DAYS},
            "generated_at": now_iso()
        }
    
    @staticmethod
    async def mark_as_realized(shipment_id: str, company_id: str, user_id: str, payment_data: Dict) -> Dict[str, Any]:
        """Mark a shipment payment as realized."""
        await TenantAuthService.verify_ownership("shipment", shipment_id, {"company_id": company_id})
        
        shipment = await db.shipments.find_one({"id": shipment_id, "company_id": company_id}, {"_id": 0})
        
        payment_id = generate_id()
        payment_doc = {
            "id": payment_id, "shipment_id": shipment_id, "company_id": company_id,
            "amount": payment_data.get("amount"),
            "currency": payment_data.get("currency", shipment.get("currency", "USD")),
            "payment_mode": payment_data.get("payment_mode", "wire_transfer"),
            "reference_number": payment_data.get("reference_number"),
            "received_date": payment_data.get("received_date", now_iso()),
            "bank_name": payment_data.get("bank_name"),
            "status": "received", "created_by": user_id, "created_at": now_iso()
        }
        await db.payments.insert_one(payment_doc)
        
        all_payments = await db.payments.find({"shipment_id": shipment_id, "status": {"$in": ["completed", "received", "paid"]}}, {"_id": 0}).to_list(100)
        total_realized = sum(p.get("amount", 0) for p in all_payments)
        total_value = shipment.get("total_value", 0)
        
        update_data = {"updated_at": now_iso()}
        if total_realized >= total_value:
            update_data["ebrc_status"] = "filed"
        
        await db.shipments.update_one({"id": shipment_id}, {"$set": update_data})
        
        # Audit log
        await db.audit_logs.insert_one({
            "id": generate_id(), "action_type": "payment_realized",
            "resource_type": "payment", "resource_id": payment_id,
            "company_id": company_id, "user_id": user_id,
            "details": {"shipment_id": shipment_id, "amount": payment_data.get("amount"), "total_realized": total_realized},
            "timestamp": now_iso()
        })
        
        return {
            "payment_id": payment_id, "shipment_id": shipment_id,
            "amount_realized": total_realized, "total_value": total_value,
            "realization_percentage": round((total_realized / total_value * 100) if total_value > 0 else 0, 1),
            "fully_realized": total_realized >= total_value
        }
    
    @staticmethod
    async def draft_rbi_extension_letter(
        shipment_id: str, company_id: str, user_id: str,
        reason: str = "delayed_payment", extension_days: int = 90
    ) -> Dict[str, Any]:
        """Use Gemini AI to draft RBI extension letter."""
        await TenantAuthService.verify_ownership("shipment", shipment_id, {"company_id": company_id})
        
        shipment = await db.shipments.find_one({"id": shipment_id, "company_id": company_id}, {"_id": 0})
        company = await db.companies.find_one({"id": company_id}, {"_id": 0}) or {}
        
        payments = await db.payments.find({"shipment_id": shipment_id}, {"_id": 0}).to_list(100)
        total_realized = sum(p.get("amount", 0) for p in payments if p.get("status") in ["completed", "received", "paid"])
        total_value = shipment.get("total_value", 0)
        pending = total_value - total_realized
        
        ship_date_str = shipment.get("actual_ship_date") or shipment.get("expected_ship_date")
        age_days = 0
        if ship_date_str:
            try:
                ship_date = datetime.fromisoformat(str(ship_date_str).replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - ship_date).days
            except:
                pass
        
        reason_descriptions = {
            "delayed_payment": "The buyer has faced temporary cash flow constraints and has requested additional time for payment.",
            "dispute": "There is an ongoing commercial dispute regarding product quality/specifications which is being resolved.",
            "banking_delay": "Banking channels have faced delays in processing the international transfer.",
            "force_majeure": "Unforeseen circumstances (natural disaster/pandemic/political situation) have affected the buyer's ability to make timely payment.",
            "documentation": "Documentation requirements from the buyer's bank have caused procedural delays."
        }
        
        prompt = f"""Draft a formal RBI extension letter for export receivables realization.

**Exporter Details:**
- Company Name: {company.get('name') or company.get('company_name', 'N/A')}
- IEC Code: {company.get('iec_code') or company.get('iec', 'N/A')}
- Address: {company.get('address', 'N/A')}

**Shipment Details:**
- Shipping Bill No: {shipment.get('shipment_number')}
- Shipping Bill Date: {shipment.get('actual_ship_date') or shipment.get('expected_ship_date')}
- Invoice Value: {shipment.get('currency')} {total_value:,.2f}
- Buyer: {shipment.get('buyer_name')}, {shipment.get('buyer_country')}
- Port of Export: {shipment.get('origin_port')}

**Realization Status:**
- Total Invoice Value: {shipment.get('currency')} {total_value:,.2f}
- Amount Realized: {shipment.get('currency')} {total_realized:,.2f}
- Amount Pending: {shipment.get('currency')} {pending:,.2f}
- Age of Shipment: {age_days} days
- Original Deadline: 270 days

**Extension Request:**
- Reason: {reason_descriptions.get(reason, reason)}
- Extension Period: {extension_days} days

Draft a complete formal letter to RBI Regional Office."""
        
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            api_key = settings.EMERGENT_LLM_KEY
            if not api_key:
                raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY not configured")
            
            chat = LlmChat(
                api_key=api_key,
                session_id=f"rbi_letter_{shipment_id}",
                system_message=RBI_LETTER_SYSTEM_MESSAGE
            ).with_model("gemini", "gemini-3-flash-preview")
            
            letter_content = await chat.send_message(UserMessage(text=prompt))
            
            letter_id = generate_id()
            letter_doc = {
                "id": letter_id, "type": "rbi_extension_letter", "shipment_id": shipment_id,
                "company_id": company_id, "user_id": user_id, "content": letter_content,
                "reason": reason, "extension_days": extension_days, "status": "draft", "created_at": now_iso()
            }
            await db.generated_documents.insert_one(letter_doc)
            
            await db.ai_usage.insert_one({
                "id": generate_id(), "company_id": company_id, "user_id": user_id,
                "feature": "rbi_extension_letter", "model": "gemini-3-flash-preview", "created_at": now_iso()
            })
            
            # Audit log
            await db.audit_logs.insert_one({
                "id": generate_id(), "action_type": "rbi_letter_drafted",
                "resource_type": "generated_document", "resource_id": letter_id,
                "company_id": company_id, "user_id": user_id,
                "details": {"shipment_id": shipment_id, "reason": reason, "extension_days": extension_days},
                "timestamp": now_iso()
            })
            
            return {
                "letter_id": letter_id, "shipment_id": shipment_id, "content": letter_content,
                "reason": reason, "extension_days": extension_days, "status": "draft"
            }
            
        except ImportError:
            raise HTTPException(status_code=500, detail="AI service not available")
        except Exception as e:
            logger.error(f"AI letter generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to generate letter: {str(e)}")
    
    @staticmethod
    async def get_aging_summary(company_id: str) -> Dict[str, Any]:
        """Get aging summary for receivables dashboard."""
        risk_data = await RiskClockService.get_risk_clock_data(company_id)
        buckets = risk_data["buckets"]
        
        return {
            "summary": risk_data["summary"],
            "aging_distribution": [
                {"bucket": "0-180 days", "category": "SAFE", "count": len(buckets["safe"]), "value": sum(s.get("pending_amount", 0) for s in buckets["safe"]), "color": "#10B981"},
                {"bucket": "180-210 days", "category": "MONITOR", "count": len(buckets["monitor"]), "value": sum(s.get("pending_amount", 0) for s in buckets["monitor"]), "color": "#F59E0B"},
                {"bucket": "210-240 days", "category": "WARNING", "count": len(buckets["warning"]), "value": sum(s.get("pending_amount", 0) for s in buckets["warning"]), "color": "#F97316"},
                {"bucket": "240+ days", "category": "CRITICAL", "count": len(buckets["critical"]), "value": sum(s.get("pending_amount", 0) for s in buckets["critical"]), "color": "#EF4444"}
            ],
            "thresholds": risk_data["thresholds"],
            "generated_at": now_iso()
        }
