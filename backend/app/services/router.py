"""
API Routes for Export Features:
- DGFT Excel Generator
- Audit Vault
- RBI Risk Clock
- OFAC Screening
- Secure File Operations
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, UploadFile, File
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel

from ..core.dependencies import get_current_user
from .dgft_service import DGFTExcelService
from .audit_vault_service import AuditVaultService
from .risk_clock_service import RiskClockService
from .ofac_screening_service import OFACScreeningService
from .credit_scoring_service import CreditScoringService
from .secure_storage_service import SecureStorageService
from .document_service import EnhancedDocumentService
from .tenant_auth_service import TenantAuthService
from ..core.database import db

router = APIRouter(tags=["Export Features"])


# ============== DGFT Excel Generator Routes ==============

@router.get("/dgft/export", summary="Download DGFT eBRC Excel")
async def download_dgft_excel(
    status: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    user: dict = Depends(get_current_user)
):
    """Generate DGFT-compliant Excel for eBRC bulk upload."""
    company_id = TenantAuthService.get_company_id(user)
    filters = {}
    if status:
        filters["status"] = status
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date
    
    return await DGFTExcelService.generate_dgft_excel(company_id, user.get("id"), filters or None)


@router.get("/dgft/validate", summary="Validate DGFT Data")
async def validate_dgft_data(user: dict = Depends(get_current_user)):
    """Validate data against DGFT schema requirements."""
    return await DGFTExcelService.validate_dgft_data(TenantAuthService.get_company_id(user))


# ============== Audit Vault Routes ==============

@router.post("/audit-vault/generate/{shipment_id}", summary="Generate Audit Package")
async def generate_audit_package(
    shipment_id: str,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Generate audit package with PDF cover sheet and FEMA compliance check."""
    return await AuditVaultService.create_audit_package(
        shipment_id, TenantAuthService.get_company_id(user), user.get("id"), background_tasks
    )


@router.get("/audit-vault/status/{job_id}", summary="Check Job Status")
async def get_audit_package_status(job_id: str, user: dict = Depends(get_current_user)):
    """Get audit package generation status."""
    company_id = TenantAuthService.get_company_id(user)
    job = await db.jobs.find_one({"id": job_id, "company_id": company_id}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/audit-vault/download/{package_id}", summary="Download Audit Package")
async def download_audit_package(package_id: str, user: dict = Depends(get_current_user)):
    """Download the audit package ZIP file."""
    data, filename = await AuditVaultService.download_package(
        package_id, TenantAuthService.get_company_id(user)
    )
    return Response(content=data, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename={filename}"})


# ============== RBI Risk Clock Routes ==============

@router.get("/risk-clock", summary="Get RBI Risk Clock Data")
async def get_risk_clock(user: dict = Depends(get_current_user)):
    """Get 9-month risk clock dashboard with CRITICAL/WARNING/MONITOR buckets."""
    return await RiskClockService.get_risk_clock_data(TenantAuthService.get_company_id(user))


@router.get("/risk-clock/aging-summary", summary="Get Aging Summary")
async def get_aging_summary(user: dict = Depends(get_current_user)):
    """Get aging distribution for dashboard charts."""
    return await RiskClockService.get_aging_summary(TenantAuthService.get_company_id(user))


class RealizePaymentRequest(BaseModel):
    amount: float
    currency: Optional[str] = None
    payment_mode: Optional[str] = "wire_transfer"
    reference_number: Optional[str] = None
    received_date: Optional[str] = None
    bank_name: Optional[str] = None


@router.post("/risk-clock/realize/{shipment_id}", summary="Mark Payment as Realized")
async def mark_as_realized(shipment_id: str, payment: RealizePaymentRequest, user: dict = Depends(get_current_user)):
    """Record payment realization for a shipment."""
    return await RiskClockService.mark_as_realized(
        shipment_id, TenantAuthService.get_company_id(user), user.get("id"), payment.model_dump()
    )


class DraftLetterRequest(BaseModel):
    reason: str = "delayed_payment"
    extension_days: int = 90


@router.post("/risk-clock/draft-letter/{shipment_id}", summary="Draft RBI Extension Letter")
async def draft_rbi_letter(shipment_id: str, request: DraftLetterRequest, user: dict = Depends(get_current_user)):
    """Use AI to draft RBI extension letter."""
    return await RiskClockService.draft_rbi_extension_letter(
        shipment_id, TenantAuthService.get_company_id(user), user.get("id"),
        request.reason, request.extension_days
    )


@router.get("/risk-clock/letter/{letter_id}", summary="Get Generated Letter")
async def get_letter(letter_id: str, user: dict = Depends(get_current_user)):
    """Retrieve a previously generated RBI extension letter."""
    company_id = TenantAuthService.get_company_id(user)
    letter = await db.generated_documents.find_one({"id": letter_id, "company_id": company_id}, {"_id": 0})
    if not letter:
        raise HTTPException(status_code=404, detail="Letter not found")
    return letter


# ============== OFAC Screening Routes ==============

class ScreenEntityRequest(BaseModel):
    entity_name: str
    entity_type: str = "buyer"  # buyer, company, individual
    country_code: Optional[str] = None


@router.post("/compliance/ofac-screen", summary="Screen Entity Against OFAC")
async def screen_entity(request: ScreenEntityRequest, user: dict = Depends(get_current_user)):
    """Screen entity against OFAC sanctions list."""
    result = await OFACScreeningService.screen_entity(
        entity_name=request.entity_name,
        entity_type=request.entity_type,
        country_code=request.country_code,
        company_id=TenantAuthService.get_company_id(user)
    )
    return result.to_dict()


@router.get("/compliance/ofac-history", summary="Get OFAC Screening History")
async def get_ofac_history(
    entity_name: Optional[str] = None,
    limit: int = 100,
    user: dict = Depends(get_current_user)
):
    """Get OFAC screening history for audit purposes."""
    return await OFACScreeningService.get_screening_history(
        TenantAuthService.get_company_id(user), entity_name, limit
    )


# ============== Credit Scoring Routes (Replacing Mock) ==============

@router.get("/credit/buyer-score/{buyer_id}", summary="Get Buyer Credit Score")
async def get_buyer_score(buyer_id: str, user: dict = Depends(get_current_user)):
    """Get real aggregation-based buyer credit score."""
    return await CreditScoringService.calculate_buyer_score(
        buyer_id, TenantAuthService.get_company_id(user), user.get("id")
    )


@router.get("/credit/company-score", summary="Get Company Credit Score")
async def get_company_score(user: dict = Depends(get_current_user)):
    """Get real aggregation-based company credit score."""
    return await CreditScoringService.calculate_company_score(
        TenantAuthService.get_company_id(user), user.get("id")
    )


@router.get("/credit/payment-behavior", summary="Get Payment Behavior Analysis")
async def get_payment_behavior(user: dict = Depends(get_current_user)):
    """Get aggregation-based payment behavior analysis."""
    return await CreditScoringService.get_payment_behavior_analysis(
        TenantAuthService.get_company_id(user), user.get("id")
    )


# ============== Secure File Operations ==============

@router.post("/files/secure-upload", summary="Secure File Upload")
async def secure_upload(
    file: UploadFile = File(...),
    doc_type: str = Query("document"),
    shipment_id: Optional[str] = Query(None),
    user: dict = Depends(get_current_user)
):
    """Upload file with magic-byte validation and tenant-scoped storage."""
    return await SecureStorageService.upload_file(
        file=file,
        company_id=TenantAuthService.get_company_id(user),
        doc_type=doc_type,
        shipment_id=shipment_id,
        user_id=user.get("id")
    )


@router.get("/files/secure/{file_id}", summary="Get Secure File")
async def get_secure_file(file_id: str, user: dict = Depends(get_current_user)):
    """Get file with tenant verification."""
    content, metadata = await SecureStorageService.get_file(
        file_id, TenantAuthService.get_company_id(user)
    )
    return Response(
        content=content,
        media_type=metadata.get("content_type", "application/octet-stream"),
        headers={"Content-Disposition": f"attachment; filename={metadata.get('original_filename', 'file')}"}
    )


@router.delete("/files/secure/{file_id}", summary="Delete Secure File")
async def delete_secure_file(file_id: str, user: dict = Depends(get_current_user)):
    """Delete file with tenant verification."""
    await SecureStorageService.delete_file(
        file_id, TenantAuthService.get_company_id(user), user.get("id")
    )
    return {"message": "File deleted"}


@router.get("/files/list", summary="List Files")
async def list_files(
    shipment_id: Optional[str] = None,
    doc_type: Optional[str] = None,
    limit: int = 100,
    user: dict = Depends(get_current_user)
):
    """List files for tenant."""
    return await SecureStorageService.list_files(
        TenantAuthService.get_company_id(user), shipment_id, doc_type, limit
    )


# ============== Enhanced Document Service Routes ==============

@router.post("/documents/upload", summary="Upload Document")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Query("other"),
    shipment_id: Optional[str] = Query(None),
    user: dict = Depends(get_current_user)
):
    """Upload document with validation."""
    return await EnhancedDocumentService.upload_document(
        file=file,
        company_id=TenantAuthService.get_company_id(user),
        user_id=user.get("id"),
        doc_type=doc_type,
        shipment_id=shipment_id
    )


@router.get("/documents/{document_id}", summary="Get Document")
async def get_document(document_id: str, user: dict = Depends(get_current_user)):
    """Get document with tenant verification."""
    return await EnhancedDocumentService.fetch_document(
        document_id, TenantAuthService.get_company_id(user)
    )


@router.delete("/documents/{document_id}", summary="Delete Document")
async def delete_document(document_id: str, user: dict = Depends(get_current_user)):
    """Delete document with tenant verification."""
    await EnhancedDocumentService.delete_document(
        document_id, TenantAuthService.get_company_id(user), user.get("id")
    )
    return {"message": "Document deleted"}


@router.post("/documents/{document_id}/ai-process", summary="AI Process Document")
async def ai_process_document(
    document_id: str,
    extraction_type: str = Query("auto"),
    user: dict = Depends(get_current_user)
):
    """Process document with AI for data extraction."""
    return await EnhancedDocumentService.ai_process_document(
        document_id, TenantAuthService.get_company_id(user), user.get("id"), extraction_type
    )


@router.post("/documents/{document_id}/validate", summary="Validate Document")
async def validate_document(document_id: str, user: dict = Depends(get_current_user)):
    """Validate document against business rules."""
    return await EnhancedDocumentService.validate_document(
        document_id, TenantAuthService.get_company_id(user)
    )
