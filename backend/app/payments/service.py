from typing import List
from datetime import datetime, timezone
from ..core.database import db
from ..common.utils import generate_id, now_iso
from .models import PaymentCreate, PaymentResponse
from ..common.metrics import track_db_operation_sync
from fastapi import HTTPException
import time

class PaymentService:
    @staticmethod
    async def create(data: PaymentCreate, user: dict) -> PaymentResponse:
        # IDOR protection: verify shipment belongs to user's company
        shipment = await db.shipments.find_one({
            "id": data.shipment_id, 
            "company_id": user.get("company_id", user["id"])
        }, {"_id": 0})
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")
        
        # Currency consistency validation: payment currency must match shipment currency
        shipment_currency = shipment.get("currency", "USD")
        if data.currency != shipment_currency:
            raise HTTPException(
                status_code=400, 
                detail=f"Payment currency ({data.currency}) must match shipment currency ({shipment_currency}). Cross-currency payments require explicit exchange rate conversion."
            )
        
        payment_id = generate_id()
        payment_doc = {
            "id": payment_id,
            **data.model_dump(),
            "status": "received",
            "company_id": user.get("company_id", user["id"]),
            "created_by": user["id"],
            "created_at": now_iso()
        }
        start = time.time()
        await db.payments.insert_one(payment_doc)
        track_db_operation_sync("insert", "payments", "success", time.time() - start)
        return PaymentResponse(**{k: v for k, v in payment_doc.items() if k in PaymentResponse.model_fields})

    @staticmethod
    async def get_by_shipment(shipment_id: str, user: dict) -> List[PaymentResponse]:
        # IDOR protection
        company_id = user.get("company_id", user["id"])
        start = time.time()
        payments = await db.payments.find(
            {"shipment_id": shipment_id, "company_id": company_id}, 
            {"_id": 0}
        ).to_list(100)
        track_db_operation_sync("find", "payments", "success", time.time() - start)
        return [PaymentResponse(**{k: v for k, v in p.items() if k in PaymentResponse.model_fields}) for p in payments]

    @staticmethod
    async def get_receivables(user: dict) -> List[dict]:
        company_id = user.get("company_id", user["id"])
        shipments = await db.shipments.find({"company_id": company_id, "status": {"$ne": "paid"}}, {"_id": 0}).to_list(500)
        
        now = datetime.now(timezone.utc)
        receivables = []
        for s in shipments:
            payments = await db.payments.find({"shipment_id": s["id"], "company_id": company_id}, {"_id": 0}).to_list(100)
            total_paid = sum(p.get("amount", 0) for p in payments)
            outstanding = s["total_value"] - total_paid
            if outstanding > 0:
                # Calculate days outstanding
                created = datetime.fromisoformat(s["created_at"].replace("Z", "+00:00"))
                days_outstanding = (now - created).days
                
                receivables.append({
                    "shipment_id": s["id"],
                    "shipment_number": s["shipment_number"],
                    "buyer_name": s["buyer_name"],
                    "buyer_country": s.get("buyer_country", ""),
                    "total_value": s["total_value"],
                    "currency": s["currency"],
                    "paid": total_paid,
                    "outstanding": outstanding,
                    "status": s["status"],
                    "days_outstanding": days_outstanding,
                    "created_at": s["created_at"]
                })
        return receivables

    @staticmethod
    async def get_aging(user: dict) -> dict:
        company_id = user.get("company_id", user["id"])
        shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
        
        aging = {"current": 0, "30_days": 0, "60_days": 0, "90_days": 0, "over_90": 0}
        now = datetime.now(timezone.utc)
        
        for s in shipments:
            payments = await db.payments.find({"shipment_id": s["id"], "company_id": company_id}, {"_id": 0}).to_list(100)
            total_paid = sum(p.get("amount", 0) for p in payments)
            outstanding = s["total_value"] - total_paid
            
            if outstanding > 0:
                created = datetime.fromisoformat(s["created_at"].replace("Z", "+00:00"))
                days = (now - created).days
                
                if days <= 30:
                    aging["current"] += outstanding
                elif days <= 60:
                    aging["30_days"] += outstanding
                elif days <= 90:
                    aging["60_days"] += outstanding
                elif days <= 120:
                    aging["90_days"] += outstanding
                else:
                    aging["over_90"] += outstanding
        
        return aging

    @staticmethod
    async def get_aging_dashboard(user: dict) -> dict:
        """Get comprehensive receivables aging dashboard"""
        company_id = user.get("company_id", user["id"])
        shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
        
        now = datetime.now(timezone.utc)
        
        # Aging buckets with detailed breakdown
        buckets = {
            "0_30": {"label": "0-30 Days", "amount": 0, "count": 0, "shipments": [], "color": "#10B981"},
            "31_60": {"label": "31-60 Days", "amount": 0, "count": 0, "shipments": [], "color": "#3B82F6"},
            "61_90": {"label": "61-90 Days", "amount": 0, "count": 0, "shipments": [], "color": "#F59E0B"},
            "91_plus": {"label": "90+ Days", "amount": 0, "count": 0, "shipments": [], "color": "#EF4444"}
        }
        
        total_receivables = 0
        total_overdue = 0
        overdue_shipments = []
        
        for s in shipments:
            payments = await db.payments.find({"shipment_id": s["id"], "company_id": company_id}, {"_id": 0}).to_list(100)
            total_paid = sum(p.get("amount", 0) for p in payments)
            outstanding = s["total_value"] - total_paid
            
            if outstanding > 0:
                created = datetime.fromisoformat(s["created_at"].replace("Z", "+00:00"))
                days = (now - created).days
                
                shipment_data = {
                    "shipment_id": s["id"],
                    "shipment_number": s["shipment_number"],
                    "buyer_name": s["buyer_name"],
                    "buyer_country": s.get("buyer_country", ""),
                    "total_value": s["total_value"],
                    "outstanding": outstanding,
                    "currency": s["currency"],
                    "days_outstanding": days,
                    "status": s["status"]
                }
                
                total_receivables += outstanding
                
                if days <= 30:
                    buckets["0_30"]["amount"] += outstanding
                    buckets["0_30"]["count"] += 1
                    buckets["0_30"]["shipments"].append(shipment_data)
                elif days <= 60:
                    buckets["31_60"]["amount"] += outstanding
                    buckets["31_60"]["count"] += 1
                    buckets["31_60"]["shipments"].append(shipment_data)
                elif days <= 90:
                    buckets["61_90"]["amount"] += outstanding
                    buckets["61_90"]["count"] += 1
                    buckets["61_90"]["shipments"].append(shipment_data)
                    total_overdue += outstanding
                    overdue_shipments.append(shipment_data)
                else:
                    buckets["91_plus"]["amount"] += outstanding
                    buckets["91_plus"]["count"] += 1
                    buckets["91_plus"]["shipments"].append(shipment_data)
                    total_overdue += outstanding
                    overdue_shipments.append(shipment_data)
        
        # Sort overdue by days (most overdue first)
        overdue_shipments.sort(key=lambda x: x["days_outstanding"], reverse=True)
        
        # Calculate percentages
        for key in buckets:
            if total_receivables > 0:
                buckets[key]["percentage"] = round(buckets[key]["amount"] / total_receivables * 100, 1)
            else:
                buckets[key]["percentage"] = 0
            # Limit shipments list to top 10
            buckets[key]["shipments"] = buckets[key]["shipments"][:10]
        
        return {
            "summary": {
                "total_receivables": round(total_receivables, 2),
                "total_overdue": round(total_overdue, 2),
                "overdue_percentage": round(total_overdue / total_receivables * 100, 1) if total_receivables > 0 else 0,
                "total_shipments_with_outstanding": sum(b["count"] for b in buckets.values())
            },
            "buckets": buckets,
            "chart_data": [
                {"name": buckets[k]["label"], "value": buckets[k]["amount"], "count": buckets[k]["count"], "color": buckets[k]["color"]}
                for k in ["0_30", "31_60", "61_90", "91_plus"]
            ],
            "overdue_alerts": overdue_shipments[:10],
            "currency": "INR"
        }
