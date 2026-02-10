from fastapi import APIRouter, Depends, UploadFile, File, Query, Request, HTTPException
from typing import Dict, Any, List
from ..core.dependencies import get_current_user
from ..core.rate_limiting import ocr_process_limit, limiter
from .models import InvoiceCreate, DocumentResponse
from .service import DocumentService
from .ocr_service import OCRService

router = APIRouter(tags=["Documents"])

# File validation constants
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.webp', '.gif'}
BLOCKED_EXTENSIONS = {'.exe', '.bat', '.cmd', '.sh', '.zip', '.rar', '.7z', '.tar', '.gz', '.js', '.py', '.php'}


def validate_file(file: UploadFile, content: bytes):
    """Validate uploaded file for size and type"""
    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)} MB"
        )
    
    # Get file extension
    filename = file.filename or ""
    ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
    
    # Block dangerous file types
    if ext in BLOCKED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"File type '{ext}' is not allowed. Blocked for security reasons."
        )
    
    # Check if extension is allowed
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Invalid file type '{ext}'. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check content type
    content_type = file.content_type or ""
    valid_content_types = {
        'application/pdf',
        'image/png',
        'image/jpeg',
        'image/jpg',
        'image/webp',
        'image/gif'
    }
    
    if content_type and content_type not in valid_content_types:
        raise HTTPException(
            status_code=415,
            detail=f"Invalid content type '{content_type}'"
        )
    
    return True


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
    """Upload a document file (PDF, PNG, JPG). Max 20MB."""
    content = await file.read()
    
    # Validate file before processing
    validate_file(file, content)
    
    return await OCRService.save_uploaded_file(content, file.filename, user)

@router.post("/documents/ocr/process")
@ocr_process_limit
async def process_document_ocr(
    request: Request,
    file_id: str = Query(...),
    document_type: str = Query(..., description="invoice, shipping_bill, or packing_list"),
    user: dict = Depends(get_current_user)
):
    """Process uploaded document with OCR to extract data. Rate limited: 20/hour per company."""
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
@ocr_process_limit
async def extract_document_legacy(request: Request, file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """Legacy OCR endpoint - upload and process in one step. Rate limited: 20/hour per company."""
    # Save file
    content = await file.read()
    file_info = await OCRService.save_uploaded_file(content, file.filename, user)
    # Process with OCR (default to invoice)
    return await OCRService.process_document(file_info["file_id"], "invoice", user)

@router.post("/invoices/bulk-upload")
@limiter.limit("5/hour")
async def bulk_upload_invoices(request: Request, files: List[UploadFile] = File(...), user: dict = Depends(get_current_user)):
    """Bulk upload multiple invoices. Rate limited: 5/hour per company."""
    results = []
    for file in files:
        content = await file.read()
        file_info = await OCRService.save_uploaded_file(content, file.filename, user)
        results.append(file_info)
    return {"uploaded": len(results), "files": results}
