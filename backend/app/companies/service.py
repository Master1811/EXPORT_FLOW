from ..core.database import db
from ..common.utils import generate_id, now_iso
from .models import CompanyCreate, CompanyResponse
from ..common.metrics import track_db_operation_sync, companies_active
from fastapi import HTTPException
import time

class CompanyService:
    @staticmethod
    async def create(data: CompanyCreate, user: dict) -> CompanyResponse:
        company_id = generate_id()
        company_doc = {
            "id": company_id,
            "name": data.name,
            "gstin": data.gstin,
            "pan": data.pan,
            "iec_code": data.iec_code,
            "address": data.address,
            "city": data.city,
            "state": data.state,
            "country": data.country,
            "bank_account": data.bank_account,
            "bank_ifsc": data.bank_ifsc,
            "owner_id": user["id"],
            "created_at": now_iso()
        }
        start = time.time()
        await db.companies.insert_one(company_doc)
        track_db_operation_sync("insert", "companies", "success", time.time() - start)
        
        # Update active companies metric
        total_companies = await db.companies.count_documents({})
        companies_active.set(total_companies)
        
        await db.users.update_one({"id": user["id"]}, {"$set": {"company_id": company_id}})
        
        return CompanyResponse(**{k: v for k, v in company_doc.items() if k in CompanyResponse.model_fields})

    @staticmethod
    async def get(company_id: str) -> CompanyResponse:
        start = time.time()
        company = await db.companies.find_one({"id": company_id}, {"_id": 0})
        track_db_operation_sync("find", "companies", "success" if company else "not_found", time.time() - start)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return CompanyResponse(**{k: v for k, v in company.items() if k in CompanyResponse.model_fields})

    @staticmethod
    async def update(company_id: str, data: CompanyCreate) -> CompanyResponse:
        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_at"] = now_iso()
        start = time.time()
        await db.companies.update_one({"id": company_id}, {"$set": update_data})
        track_db_operation_sync("update", "companies", "success", time.time() - start)
        company = await db.companies.find_one({"id": company_id}, {"_id": 0})
        return CompanyResponse(**{k: v for k, v in company.items() if k in CompanyResponse.model_fields})
