from typing import List, Dict, Any
from ..core.database import db
from ..common.utils import generate_id, now_iso
from .models import InvoiceCreate, DocumentResponse

class DocumentService:
    @staticmethod
    async def create_invoice(shipment_id: str, data: InvoiceCreate, user: dict) -> DocumentResponse:
        doc_id = generate_id()
        doc = {
            "id": doc_id,
            "document_type": "invoice",
            "shipment_id": shipment_id,
            "document_number": data.invoice_number,
            "data": data.model_dump(),
            "company_id": user.get("company_id", user["id"]),
            "created_by": user["id"],
            "created_at": now_iso()
        }
        await db.documents.insert_one(doc)
        return DocumentResponse(**{k: v for k, v in doc.items() if k in DocumentResponse.model_fields})

    @staticmethod
    async def create_packing_list(shipment_id: str, data: Dict[str, Any], user: dict) -> DocumentResponse:
        doc_id = generate_id()
        doc = {
            "id": doc_id,
            "document_type": "packing_list",
            "shipment_id": shipment_id,
            "document_number": data.get("packing_list_number", f"PL-{shipment_id[:8]}"),
            "data": data,
            "company_id": user.get("company_id", user["id"]),
            "created_by": user["id"],
            "created_at": now_iso()
        }
        await db.documents.insert_one(doc)
        return DocumentResponse(**{k: v for k, v in doc.items() if k in DocumentResponse.model_fields})

    @staticmethod
    async def create_shipping_bill(shipment_id: str, data: Dict[str, Any], user: dict) -> DocumentResponse:
        doc_id = generate_id()
        doc = {
            "id": doc_id,
            "document_type": "shipping_bill",
            "shipment_id": shipment_id,
            "document_number": data.get("sb_number", f"SB-{shipment_id[:8]}"),
            "data": data,
            "company_id": user.get("company_id", user["id"]),
            "created_by": user["id"],
            "created_at": now_iso()
        }
        await db.documents.insert_one(doc)
        return DocumentResponse(**{k: v for k, v in doc.items() if k in DocumentResponse.model_fields})

    @staticmethod
    async def get_shipment_documents(shipment_id: str) -> List[DocumentResponse]:
        docs = await db.documents.find({"shipment_id": shipment_id}, {"_id": 0}).to_list(100)
        return [DocumentResponse(**{k: v for k, v in d.items() if k in DocumentResponse.model_fields}) for d in docs]

    @staticmethod
    async def ocr_extract(filename: str, user: dict) -> dict:
        job_id = generate_id()
        job_doc = {
            "id": job_id,
            "type": "ocr_extraction",
            "status": "processing",
            "company_id": user.get("company_id", user["id"]),
            "filename": filename,
            "created_at": now_iso()
        }
        await db.jobs.insert_one(job_doc)
        return {"job_id": job_id, "status": "processing", "message": "Document queued for OCR extraction"}

    @staticmethod
    async def bulk_upload(file_count: int, user: dict) -> dict:
        job_id = generate_id()
        job_doc = {
            "id": job_id,
            "type": "bulk_invoice_upload",
            "status": "processing",
            "company_id": user.get("company_id", user["id"]),
            "file_count": file_count,
            "created_at": now_iso()
        }
        await db.jobs.insert_one(job_doc)
        return {"job_id": job_id, "status": "processing", "files_queued": file_count}
