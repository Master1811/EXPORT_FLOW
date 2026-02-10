from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from ..core.database import db
from ..common.utils import generate_id, now_iso
from .models import GSTInputCreditCreate, GSTSummaryResponse


def get_month_date_range(year: int, month: int) -> tuple:
    """Get start and end datetime for a specific month (ISO format strings)"""
    start_date = datetime(year, month, 1, tzinfo=timezone.utc)
    # Calculate end of month
    if month == 12:
        end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc) - timedelta(microseconds=1)
    else:
        end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc) - timedelta(microseconds=1)
    return start_date.isoformat(), end_date.isoformat()


class GSTService:
    @staticmethod
    async def add_input_credit(data: GSTInputCreditCreate, user: dict) -> dict:
        credit_id = generate_id()
        credit_doc = {
            "id": credit_id,
            **data.model_dump(),
            "company_id": user.get("company_id", user["id"]),
            "status": "pending",
            "created_at": now_iso()
        }
        await db.gst_credits.insert_one(credit_doc)
        return {"id": credit_id, "message": "GST input credit added"}

    @staticmethod
    async def get_monthly_summary(user: dict, year: int = None) -> List[GSTSummaryResponse]:
        company_id = user.get("company_id", user["id"])
        year = year or datetime.now().year
        
        months = []
        for m in range(1, 13):
            # Use indexed range queries instead of regex for performance
            start_date, end_date = get_month_date_range(year, m)
            shipments = await db.shipments.find({
                "company_id": company_id,
                "created_at": {"$gte": start_date, "$lt": end_date}
            }, {"_id": 0}).to_list(500)
            
            total_value = sum(s.get("total_value", 0) for s in shipments)
            igst_paid = total_value * 0.18
            month_str = f"{year}-{m:02d}"
            
            months.append(GSTSummaryResponse(
                month=month_str,
                total_export_value=total_value,
                total_igst_paid=igst_paid,
                refund_eligible=igst_paid,
                refund_claimed=igst_paid * 0.6,
                refund_pending=igst_paid * 0.4
            ))
        return months

    @staticmethod
    async def get_expected_refund(user: dict) -> dict:
        company_id = user.get("company_id", user["id"])
        shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
        
        total_export_value = sum(s.get("total_value", 0) for s in shipments)
        expected_refund = total_export_value * 0.18 * 0.4
        
        return {
            "total_export_value": total_export_value,
            "igst_paid": total_export_value * 0.18,
            "refund_claimed": total_export_value * 0.18 * 0.6,
            "refund_expected": expected_refund,
            "estimated_date": (datetime.now(timezone.utc) + timedelta(days=45)).isoformat()
        }

    @staticmethod
    async def get_refund_status(user: dict) -> dict:
        return {
            "pending_applications": 3,
            "total_pending_amount": 245000,
            "applications": [
                {"ref_number": "GST-REF-2024-001", "amount": 85000, "status": "processing", "filed_date": "2024-01-15"},
                {"ref_number": "GST-REF-2024-002", "amount": 92000, "status": "under_review", "filed_date": "2024-01-28"},
                {"ref_number": "GST-REF-2024-003", "amount": 68000, "status": "approved", "filed_date": "2024-02-10"}
            ]
        }

    @staticmethod
    async def get_lut_status(user: dict) -> dict:
        company_id = user.get("company_id", user["id"])
        lut = await db.compliance.find_one({"company_id": company_id, "type": "lut"}, {"_id": 0})
        
        if lut:
            return lut
        return {"status": "not_filed", "message": "LUT not filed for current financial year", "action_required": True}

    @staticmethod
    async def link_lut(data: Dict[str, str], user: dict) -> dict:
        company_id = user.get("company_id", user["id"])
        lut_doc = {
            "id": generate_id(),
            "company_id": company_id,
            "type": "lut",
            "lut_number": data.get("lut_number"),
            "financial_year": data.get("financial_year", "2024-25"),
            "valid_from": data.get("valid_from"),
            "valid_until": data.get("valid_until"),
            "status": "active",
            "created_at": now_iso()
        }
        await db.compliance.insert_one(lut_doc)
        return {"message": "LUT linked successfully", "lut_number": data.get("lut_number")}
