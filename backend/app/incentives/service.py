from ..core.database import db
from ..common.utils import generate_id, now_iso
from .models import IncentiveCalculateRequest, IncentiveResponse

RODTEP_RATES = {
    "61": 4.0, "62": 4.0, "63": 4.0,
    "84": 2.5, "85": 2.5,
    "87": 3.0,
    "90": 2.0,
    "94": 3.5,
}

class IncentiveService:
    @staticmethod
    async def check_eligibility(hs_code: str) -> dict:
        chapter = hs_code[:2]
        rate = RODTEP_RATES.get(chapter, 0)
        
        return {
            "hs_code": hs_code,
            "chapter": chapter,
            "eligible": rate > 0,
            "rate_percent": rate,
            "scheme": "RoDTEP",
            "notes": f"Chapter {chapter} products eligible for {rate}% RoDTEP benefit" if rate > 0 else "Not eligible for RoDTEP"
        }

    @staticmethod
    async def calculate(data: IncentiveCalculateRequest, user: dict) -> IncentiveResponse:
        primary_hs = data.hs_codes[0] if data.hs_codes else "00"
        chapter = primary_hs[:2]
        rate = RODTEP_RATES.get(chapter, 0)
        total_incentive = data.fob_value * (rate / 100)
        
        incentive_id = generate_id()
        incentive_doc = {
            "id": incentive_id,
            "shipment_id": data.shipment_id,
            "scheme": "RoDTEP",
            "hs_code": primary_hs,
            "fob_value": data.fob_value,
            "rate_percent": rate,
            "incentive_amount": total_incentive,
            "status": "calculated",
            "company_id": user.get("company_id", user["id"]),
            "created_at": now_iso()
        }
        await db.incentives.insert_one(incentive_doc)
        
        return IncentiveResponse(**{k: v for k, v in incentive_doc.items() if k in IncentiveResponse.model_fields})

    @staticmethod
    async def get_lost_money(user: dict) -> dict:
        company_id = user.get("company_id", user["id"])
        shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
        claimed_shipments = await db.incentives.distinct("shipment_id", {"company_id": company_id})
        
        unclaimed = [s for s in shipments if s["id"] not in claimed_shipments]
        potential_loss = sum(s.get("total_value", 0) * 0.03 for s in unclaimed)
        
        return {
            "unclaimed_shipments": len(unclaimed),
            "potential_incentive_loss": potential_loss,
            "recommendation": f"Claim incentives for {len(unclaimed)} shipments to recover ₹{potential_loss:,.2f}"
        }

    @staticmethod
    async def get_summary(user: dict) -> dict:
        company_id = user.get("company_id", user["id"])
        incentives = await db.incentives.find({"company_id": company_id}, {"_id": 0}).to_list(500)
        
        total = sum(i.get("incentive_amount", 0) for i in incentives)
        claimed = sum(i.get("incentive_amount", 0) for i in incentives if i.get("status") == "claimed")
        pending = sum(i.get("incentive_amount", 0) for i in incentives if i.get("status") in ["calculated", "submitted"])
        
        return {
            "total_incentives": total,
            "claimed": claimed,
            "pending": pending,
            "count": len(incentives),
            "by_scheme": {
                "RoDTEP": sum(i.get("incentive_amount", 0) for i in incentives if i.get("scheme") == "RoDTEP"),
                "RoSCTL": sum(i.get("incentive_amount", 0) for i in incentives if i.get("scheme") == "RoSCTL")
            }
        }
