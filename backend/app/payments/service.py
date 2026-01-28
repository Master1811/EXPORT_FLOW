from typing import List
from datetime import datetime, timezone
from ..core.database import db
from ..common.utils import generate_id, now_iso
from .models import PaymentCreate, PaymentResponse

class PaymentService:
    @staticmethod
    async def create(data: PaymentCreate, user: dict) -> PaymentResponse:
        payment_id = generate_id()
        payment_doc = {
            "id": payment_id,
            **data.model_dump(),
            "status": "received",
            "company_id": user.get("company_id", user["id"]),
            "created_by": user["id"],
            "created_at": now_iso()
        }
        await db.payments.insert_one(payment_doc)
        return PaymentResponse(**{k: v for k, v in payment_doc.items() if k in PaymentResponse.model_fields})

    @staticmethod
    async def get_by_shipment(shipment_id: str) -> List[PaymentResponse]:
        payments = await db.payments.find({"shipment_id": shipment_id}, {"_id": 0}).to_list(100)
        return [PaymentResponse(**{k: v for k, v in p.items() if k in PaymentResponse.model_fields}) for p in payments]

    @staticmethod
    async def get_receivables(user: dict) -> List[dict]:
        company_id = user.get("company_id", user["id"])
        shipments = await db.shipments.find({"company_id": company_id, "status": {"$ne": "paid"}}, {"_id": 0}).to_list(500)
        
        receivables = []
        for s in shipments:
            payments = await db.payments.find({"shipment_id": s["id"]}, {"_id": 0}).to_list(100)
            total_paid = sum(p.get("amount", 0) for p in payments)
            outstanding = s["total_value"] - total_paid
            if outstanding > 0:
                receivables.append({
                    "shipment_id": s["id"],
                    "shipment_number": s["shipment_number"],
                    "buyer_name": s["buyer_name"],
                    "total_value": s["total_value"],
                    "currency": s["currency"],
                    "paid": total_paid,
                    "outstanding": outstanding,
                    "status": s["status"]
                })
        return receivables

    @staticmethod
    async def get_aging(user: dict) -> dict:
        company_id = user.get("company_id", user["id"])
        shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
        
        aging = {"current": 0, "30_days": 0, "60_days": 0, "90_days": 0, "over_90": 0}
        now = datetime.now(timezone.utc)
        
        for s in shipments:
            payments = await db.payments.find({"shipment_id": s["id"]}, {"_id": 0}).to_list(100)
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
