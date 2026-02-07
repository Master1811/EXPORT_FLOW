from fastapi import APIRouter, Depends, UploadFile, File, Query
from typing import Dict, Any, List
from ..core.dependencies import get_current_user
from .models import InvoiceCreate, DocumentResponse
from .service import DocumentService
from .ocr_service import OCRService

router = APIRouter(tags=["Documents"])

@router.post("/shipments/{shipment_id}/invoice", response_model=DocumentResponse)
async def create_invoice(shipment_id: str, data: InvoiceCreate, user: dict = Depends(get_current_user)):
    return await DocumentService.create_invoice(shipment_id, data, user)

@router.post("/shipments/{shipment_id}/packing-list", response_model=DocumentResponse)
async def create_packing_list(shipment_id: str, data: Dict[str, Any], user: dict = Depends(get_current_user)):
    return await DocumentService.create_packing_list(shipment_id, data, user)

@router.post("/shipments/{shipment_id}/shipping-bill", response_model=DocumentResponse)
async def create_shipping_bill(shipment_id: str, data: Dict[str, Any], user: dict = Depends(get_current_user)):
    return await DocumentService.create_shipping_bill(shipment_id, data, user)

@router.get("/shipments/{shipment_id}/documents", response_model=List[DocumentResponse])
async def get_shipment_documents(shipment_id: str, user: dict = Depends(get_current_user)):
    return await DocumentService.get_shipment_documents(shipment_id)

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """Upload a document file (PDF, PNG, JPG)"""
    content = await file.read()
    return await OCRService.save_uploaded_file(content, file.filename, user)

@router.post("/documents/ocr/process")
async def process_document_ocr(
    file_id: str = Query(...),
    document_type: str = Query(..., description="invoice, shipping_bill, or packing_list"),
    user: dict = Depends(get_current_user)
):
    """Process uploaded document with OCR to extract data"""
    return await OCRService.process_document(file_id, document_type, user)

@router.get("/documents/ocr/jobs/{job_id}")
async def get_ocr_job(job_id: str, user: dict = Depends(get_current_user)):
    """Get OCR job status and results"""
    return await OCRService.get_ocr_job(job_id, user)

@router.get("/documents/uploads")
async def list_uploaded_files(limit: int = 20, user: dict = Depends(get_current_user)):
    """List uploaded files"""
    return await OCRService.list_uploaded_files(user, limit)

@router.post("/documents/ocr/extract")
async def extract_document_legacy(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """Legacy OCR endpoint - upload and process in one step"""
    # Save file
    content = await file.read()
    file_info = await OCRService.save_uploaded_file(content, file.filename, user)
    # Process with OCR (default to invoice)
    return await OCRService.process_document(file_info["file_id"], "invoice", user)

@router.post("/invoices/bulk-upload")
async def bulk_upload_invoices(files: List[UploadFile] = File(...), user: dict = Depends(get_current_user)):
    """Bulk upload multiple invoices"""
    results = []
    for file in files:
        content = await file.read()
        file_info = await OCRService.save_uploaded_file(content, file.filename, user)
        results.append(file_info)
    return {"uploaded": len(results), "files": results}
