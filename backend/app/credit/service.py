from ..core.database import db
from ..common.utils import generate_id, now_iso

class CreditService:
    @staticmethod
    async def get_buyer_score(buyer_id: str, user: dict) -> dict:
        payments = await db.payments.find({"buyer_id": buyer_id}, {"_id": 0}).to_list(100)
        
        on_time = len([p for p in payments if p.get("status") == "on_time"])
        delayed = len([p for p in payments if p.get("status") == "delayed"])
        total = len(payments)
        
        score = 750 if total == 0 else int(500 + (on_time / max(total, 1)) * 350)
        risk_level = "low" if score >= 700 else "medium" if score >= 500 else "high"
        
        return {
            "buyer_id": buyer_id,
            "buyer_name": "Sample Buyer",
            "credit_score": score,
            "risk_level": risk_level,
            "payment_history": {"on_time": on_time, "delayed": delayed, "total": total},
            "recommendation": "Safe to extend credit" if risk_level == "low" else "Recommend advance payment terms"
        }

    @staticmethod
    async def get_company_score(user: dict) -> dict:
        company_id = user.get("company_id", user["id"])
        shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
        total_export_value = sum(s.get("total_value", 0) for s in shipments)
        
        return {
            "company_score": 780,
            "factors": {
                "export_volume": {"score": 85, "trend": "up"},
                "payment_collection": {"score": 78, "trend": "stable"},
                "compliance_history": {"score": 90, "trend": "up"},
                "buyer_diversity": {"score": 70, "trend": "stable"}
            },
            "credit_limit_eligible": total_export_value * 0.5,
            "recommendations": ["Apply for export credit guarantee", "Consider ECGC coverage"]
        }

    @staticmethod
    async def get_payment_behavior(user: dict) -> dict:
        return {
            "average_collection_days": 45,
            "on_time_percentage": 78,
            "trend": "improving",
            "by_region": {
                "USA": {"avg_days": 38, "on_time": 85},
                "Europe": {"avg_days": 42, "on_time": 80},
                "Middle East": {"avg_days": 55, "on_time": 65}
            }
        }
