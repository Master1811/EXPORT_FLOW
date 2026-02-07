from typing import List, Optional
from ..core.database import db
from ..common.utils import generate_id, now_iso
from .models import IncentiveCalculateRequest, IncentiveResponse
from .hs_database import (
    get_hs_code_info, 
    calculate_incentives, 
    search_hs_codes,
    HS_CODE_DATABASE,
    CHAPTER_DEFAULTS
)

class IncentiveService:
    @staticmethod
    async def check_eligibility(hs_code: str) -> dict:
        """Check RoDTEP/RoSCTL eligibility for an HS code"""
        hs_info = get_hs_code_info(hs_code)
        
        return {
            "hs_code": hs_code,
            "found": hs_info["found"],
            "exact_match": hs_info.get("exact_match", False),
            "description": hs_info.get("description", "Unknown"),
            "chapter": hs_info.get("chapter", hs_code[:2]),
            "rates": {
                "rodtep": hs_info["rodtep"],
                "rosctl": hs_info["rosctl"],
                "drawback": hs_info["drawback"],
                "total": round(hs_info["rodtep"] + hs_info["rosctl"] + hs_info["drawback"], 2)
            },
            "eligible": {
                "rodtep": hs_info["rodtep"] > 0,
                "rosctl": hs_info["rosctl"] > 0,
                "drawback": hs_info["drawback"] > 0
            },
            "notes": IncentiveService._get_eligibility_notes(hs_info)
        }

    @staticmethod
    def _get_eligibility_notes(hs_info: dict) -> str:
        notes = []
        if hs_info["rodtep"] > 0:
            notes.append(f"RoDTEP eligible at {hs_info['rodtep']}%")
        if hs_info["rosctl"] > 0:
            notes.append(f"RoSCTL eligible at {hs_info['rosctl']}% (textiles only)")
        if hs_info["drawback"] > 0:
            notes.append(f"Duty Drawback at {hs_info['drawback']}%")
        if not notes:
            notes.append("No incentives applicable for this HS code")
        return " | ".join(notes)

    @staticmethod
    async def search_hs_codes(query: str, limit: int = 20) -> List[dict]:
        """Search HS codes by description or code"""
        return search_hs_codes(query, limit)

    @staticmethod
    async def calculate(data: IncentiveCalculateRequest, user: dict) -> dict:
        """Calculate incentives for a shipment"""
        # Get exchange rate if needed
        exchange_rate = 1.0
        if data.currency != "INR":
            forex_rate = await db.forex_rates.find_one({"currency": data.currency}, sort=[("timestamp", -1)])
            if forex_rate:
                exchange_rate = forex_rate["rate"]
            else:
                # Default rates
                default_rates = {"USD": 83.5, "EUR": 91.2, "GBP": 106.5, "AED": 22.75}
                exchange_rate = default_rates.get(data.currency, 83.5)
        
        # Calculate for primary HS code
        primary_hs = data.hs_codes[0] if data.hs_codes else "0000"
        calculation = calculate_incentives(data.fob_value, primary_hs, data.currency, exchange_rate)
        
        # Store the calculation
        incentive_id = generate_id()
        incentive_doc = {
            "id": incentive_id,
            "shipment_id": data.shipment_id,
            "hs_codes": data.hs_codes,
            "primary_hs_code": primary_hs,
            "fob_value": data.fob_value,
            "fob_value_inr": calculation["fob_value_inr"],
            "currency": data.currency,
            "exchange_rate": exchange_rate,
            "incentives": calculation["incentives"],
            "total_incentive": calculation["total_incentive"],
            "total_rate": calculation["total_rate"],
            "status": "calculated",
            "company_id": user.get("company_id", user["id"]),
            "created_at": now_iso()
        }
        await db.incentives.insert_one(incentive_doc)
        
        return {
            "id": incentive_id,
            "shipment_id": data.shipment_id,
            **calculation,
            "status": "calculated"
        }

    @staticmethod
    async def get_lost_money(user: dict) -> dict:
        """Calculate potential lost incentives from unclaimed shipments"""
        company_id = user.get("company_id", user["id"])
        
        # Get all shipments
        shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
        
        # Get claimed shipments
        claimed_ids = await db.incentives.distinct("shipment_id", {"company_id": company_id})
        
        # Analyze unclaimed
        unclaimed_shipments = []
        total_potential_loss = 0
        
        for shipment in shipments:
            if shipment["id"] not in claimed_ids:
                # Estimate potential incentive (conservative 3% average)
                hs_codes = shipment.get("hs_codes", [])
                if hs_codes:
                    primary_hs = hs_codes[0]
                    hs_info = get_hs_code_info(primary_hs)
                    total_rate = hs_info["rodtep"] + hs_info["rosctl"] + hs_info["drawback"]
                else:
                    total_rate = 3.0  # Conservative estimate
                
                potential = shipment.get("total_value", 0) * (total_rate / 100)
                total_potential_loss += potential
                
                unclaimed_shipments.append({
                    "shipment_id": shipment["id"],
                    "shipment_number": shipment["shipment_number"],
                    "buyer_name": shipment["buyer_name"],
                    "total_value": shipment["total_value"],
                    "currency": shipment["currency"],
                    "hs_codes": hs_codes,
                    "estimated_incentive": round(potential, 2),
                    "estimated_rate": round(total_rate, 2)
                })
        
        return {
            "unclaimed_shipments_count": len(unclaimed_shipments),
            "total_potential_loss": round(total_potential_loss, 2),
            "unclaimed_shipments": unclaimed_shipments[:20],  # Limit for response
            "currency": "INR",
            "recommendation": f"You have {len(unclaimed_shipments)} shipments without incentive claims. Potential recovery: ₹{total_potential_loss:,.2f}",
            "priority_action": "high" if total_potential_loss > 100000 else "medium" if total_potential_loss > 10000 else "low"
        }

    @staticmethod
    async def get_summary(user: dict) -> dict:
        """Get incentives summary with breakdown"""
        company_id = user.get("company_id", user["id"])
        incentives = await db.incentives.find({"company_id": company_id}, {"_id": 0}).to_list(500)
        
        # Calculate totals
        total_rodtep = sum(i.get("incentives", {}).get("rodtep", {}).get("amount", 0) for i in incentives)
        total_rosctl = sum(i.get("incentives", {}).get("rosctl", {}).get("amount", 0) for i in incentives)
        total_drawback = sum(i.get("incentives", {}).get("drawback", {}).get("amount", 0) for i in incentives)
        total = total_rodtep + total_rosctl + total_drawback
        
        # By status
        claimed = sum(i.get("total_incentive", 0) for i in incentives if i.get("status") == "claimed")
        pending = sum(i.get("total_incentive", 0) for i in incentives if i.get("status") in ["calculated", "submitted"])
        
        return {
            "total_incentives": round(total, 2),
            "claimed": round(claimed, 2),
            "pending": round(pending, 2),
            "count": len(incentives),
            "by_scheme": {
                "rodtep": round(total_rodtep, 2),
                "rosctl": round(total_rosctl, 2),
                "drawback": round(total_drawback, 2)
            },
            "currency": "INR"
        }

    @staticmethod
    async def get_shipment_analysis(user: dict) -> List[dict]:
        """Get detailed shipment-by-shipment incentive analysis"""
        company_id = user.get("company_id", user["id"])
        
        # Get all shipments
        shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
        
        # Get all incentive claims
        incentives = await db.incentives.find({"company_id": company_id}, {"_id": 0}).to_list(500)
        incentive_map = {i["shipment_id"]: i for i in incentives}
        
        analysis = []
        for shipment in shipments:
            claimed = incentive_map.get(shipment["id"])
            
            # Calculate potential if not claimed
            hs_codes = shipment.get("hs_codes", [])
            if hs_codes:
                primary_hs = hs_codes[0]
                hs_info = get_hs_code_info(primary_hs)
            else:
                hs_info = {"rodtep": 3.0, "rosctl": 0, "drawback": 1.0}
            
            fob_value = shipment.get("total_value", 0)
            potential_rodtep = fob_value * (hs_info["rodtep"] / 100)
            potential_rosctl = fob_value * (hs_info["rosctl"] / 100)
            potential_drawback = fob_value * (hs_info["drawback"] / 100)
            total_potential = potential_rodtep + potential_rosctl + potential_drawback
            
            analysis.append({
                "shipment_id": shipment["id"],
                "shipment_number": shipment["shipment_number"],
                "buyer_name": shipment["buyer_name"],
                "status": shipment["status"],
                "fob_value": fob_value,
                "currency": shipment["currency"],
                "hs_codes": hs_codes,
                "incentive_status": "claimed" if claimed else "unclaimed",
                "claimed_amount": claimed.get("total_incentive", 0) if claimed else 0,
                "potential_incentive": round(total_potential, 2),
                "potential_breakdown": {
                    "rodtep": round(potential_rodtep, 2),
                    "rosctl": round(potential_rosctl, 2),
                    "drawback": round(potential_drawback, 2)
                },
                "leakage": round(total_potential - (claimed.get("total_incentive", 0) if claimed else 0), 2)
            })
        
        # Sort by leakage (highest first)
        analysis.sort(key=lambda x: x["leakage"], reverse=True)
        
        return analysis

    @staticmethod
    async def get_leakage_dashboard(user: dict) -> dict:
        """Get comprehensive leakage dashboard data"""
        company_id = user.get("company_id", user["id"])
        
        # Get shipment analysis
        analysis = await IncentiveService.get_shipment_analysis(user)
        
        # Calculate dashboard metrics
        total_fob = sum(a["fob_value"] for a in analysis)
        total_potential = sum(a["potential_incentive"] for a in analysis)
        total_claimed = sum(a["claimed_amount"] for a in analysis)
        total_leakage = total_potential - total_claimed
        
        # Get lost money details
        lost_money = await IncentiveService.get_lost_money(user)
        
        # Leakage by status
        unclaimed_count = len([a for a in analysis if a["incentive_status"] == "unclaimed"])
        claimed_count = len([a for a in analysis if a["incentive_status"] == "claimed"])
        
        # Top leaking shipments
        top_leaking = [a for a in analysis if a["leakage"] > 0][:5]
        
        return {
            "summary": {
                "total_exports": round(total_fob, 2),
                "total_potential_incentives": round(total_potential, 2),
                "total_claimed": round(total_claimed, 2),
                "total_leakage": round(total_leakage, 2),
                "recovery_rate": round((total_claimed / total_potential * 100) if total_potential > 0 else 0, 1)
            },
            "shipment_stats": {
                "total": len(analysis),
                "claimed": claimed_count,
                "unclaimed": unclaimed_count,
                "claim_rate": round((claimed_count / len(analysis) * 100) if analysis else 0, 1)
            },
            "money_left_on_table": {
                "amount": round(total_leakage, 2),
                "formatted": f"₹{total_leakage:,.2f}",
                "unclaimed_shipments": unclaimed_count,
                "priority": "critical" if total_leakage > 500000 else "high" if total_leakage > 100000 else "medium" if total_leakage > 10000 else "low"
            },
            "top_leaking_shipments": top_leaking,
            "action_required": lost_money["unclaimed_shipments"][:10],
            "currency": "INR"
        }
