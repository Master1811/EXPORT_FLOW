from typing import Dict
from ..core.database import db
from ..common.utils import generate_id, now_iso

class ConnectorService:
    @staticmethod
    async def initiate_bank(data: Dict, user: dict) -> dict:
        job_id = generate_id()
        connector_doc = {
            "id": generate_id(),
            "job_id": job_id,
            "connector_type": "bank",
            "company_id": user.get("company_id", user["id"]),
            "status": "initiating",
            "created_at": now_iso()
        }
        await db.connectors.insert_one(connector_doc)
        return {"job_id": job_id, "status": "initiating", "message": "Bank connection initiated via Account Aggregator"}

    @staticmethod
    async def bank_consent(data: Dict, user: dict) -> dict:
        return {"status": "consent_pending", "consent_url": "https://aa.example.com/consent", "expires_in": 300}

    @staticmethod
    async def sync_bank(user: dict) -> dict:
        return {
            "status": "synced",
            "last_sync": now_iso(),
            "accounts": [
                {"account_number": "****1234", "bank": "HDFC Bank", "balance": 1250000, "type": "current"},
                {"account_number": "****5678", "bank": "ICICI Bank", "balance": 850000, "type": "EEFC"}
            ]
        }

    @staticmethod
    async def link_gst(data: Dict, user: dict) -> dict:
        company_id = user.get("company_id", user["id"])
        gst_doc = {
            "id": generate_id(),
            "company_id": company_id,
            "gstin": data.get("gstin"),
            "connector_type": "gst",
            "status": "linked",
            "created_at": now_iso()
        }
        await db.connectors.insert_one(gst_doc)
        return {"status": "linked", "gstin": data.get("gstin")}

    @staticmethod
    async def sync_gst(user: dict) -> dict:
        return {
            "status": "synced",
            "last_sync": now_iso(),
            "data": {"gstr1_filed": True, "gstr3b_filed": True, "pending_returns": [], "input_credit_balance": 125000}
        }

    @staticmethod
    async def link_customs(data: Dict, user: dict) -> dict:
        company_id = user.get("company_id", user["id"])
        customs_doc = {
            "id": generate_id(),
            "company_id": company_id,
            "iec_code": data.get("iec_code"),
            "connector_type": "customs",
            "status": "linked",
            "created_at": now_iso()
        }
        await db.connectors.insert_one(customs_doc)
        return {"status": "linked", "iec_code": data.get("iec_code")}

    @staticmethod
    async def sync_customs(user: dict) -> dict:
        return {
            "status": "synced",
            "last_sync": now_iso(),
            "data": {"shipping_bills": 45, "pending_assessments": 2, "duty_drawback_pending": 75000}
        }
