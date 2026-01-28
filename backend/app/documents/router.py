from fastapi import APIRouter, Depends, UploadFile, File
from typing import Dict, Any, List
from ..core.dependencies import get_current_user
from .models import InvoiceCreate, DocumentResponse
from .service import DocumentService

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

@router.post("/documents/ocr/extract")
async def extract_document(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    return await DocumentService.ocr_extract(file.filename, user)

@router.post("/invoices/bulk-upload")
async def bulk_upload_invoices(files: List[UploadFile] = File(...), user: dict = Depends(get_current_user)):
    return await DocumentService.bulk_upload(len(files), user)
