from fastapi import APIRouter, Depends, Query, Request
from typing import Optional, List
from ..core.dependencies import get_current_user
from .models import ShipmentCreate, ShipmentResponse, ShipmentUpdate, EBRCUpdateRequest
from .service import ShipmentService
from ..common.audit_service import audit_service
from ..common.tamper_proof_audit import audit_service as tamper_audit, TamperProofAuditService

router = APIRouter(prefix="/shipments", tags=["Shipments"])

def get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None

@router.post("", response_model=ShipmentResponse)
async def create_shipment(data: ShipmentCreate, user: dict = Depends(get_current_user)):
    return await ShipmentService.create(data, user)

@router.get("", response_model=List[ShipmentResponse])
async def get_shipments(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    user: dict = Depends(get_current_user)
):
    return await ShipmentService.get_all(user, status, skip, limit)

@router.get("/paginated")
async def get_shipments_paginated(
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", enum=["created_at", "total_value", "shipment_number"]),
    sort_order: str = Query("desc", enum=["asc", "desc"]),
    user: dict = Depends(get_current_user)
):
    """
    Get shipments with server-side pagination, search, and sorting.
    
    Optimized for high-volume data (10K+ records):
    - Server-side filtering and pagination
    - Indexed search queries
    - Returns total count for pagination UI
    """
    return await ShipmentService.get_paginated(
        user=user,
        status=status,
        search=search,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.get("/ebrc-dashboard")
async def get_ebrc_dashboard(user: dict = Depends(get_current_user)):
    """Get e-BRC monitoring dashboard with alerts"""
    return await ShipmentService.get_ebrc_dashboard(user)

@router.get("/{shipment_id}", response_model=ShipmentResponse)
async def get_shipment(shipment_id: str, user: dict = Depends(get_current_user)):
    # IDOR protection: pass user to ensure company_id check
    return await ShipmentService.get(shipment_id, user)

@router.get("/{shipment_id}/unmasked", response_model=ShipmentResponse)
async def get_shipment_unmasked(
    shipment_id: str, 
    request: Request,
    user: dict = Depends(get_current_user)
):
    """
    Get shipment with unmasked/decrypted PII.
    
    ON-DEMAND DECRYPTION: Data is only unmasked when explicitly requested.
    This action is LOGGED to tamper-proof audit trail.
    
    Logged details:
    - User ID
    - Timestamp  
    - IP Address
    - Accessed fields
    """
    # Get the shipment with unmasked PII
    shipment = await ShipmentService.get(shipment_id, user, mask_sensitive=False)
    
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    
    # Log to tamper-proof audit trail
    await tamper_audit.log(
        user_id=user["id"],
        action=TamperProofAuditService.ACTION_PII_UNMASK,
        resource_type=TamperProofAuditService.RESOURCE_SHIPMENT,
        resource_id=shipment_id,
        details={
            "shipment_number": shipment.shipment_number,
            "buyer_name": shipment.buyer_name,
            "accessed_fields": ["buyer_phone", "buyer_pan", "buyer_bank_account", "buyer_email", "total_value"],
            "action_description": "User explicitly requested unmasked PII data"
        },
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    # Also log to legacy audit service
    await audit_service.log_event(
        user_id=user["id"],
        action="pii_unmask",
        resource_type="shipment",
        resource_id=shipment_id,
        details={
            "shipment_number": shipment.shipment_number,
            "buyer_name": shipment.buyer_name,
            "accessed_fields": ["buyer_phone", "buyer_pan", "buyer_bank_account", "buyer_email"]
        },
        ip_address=client_ip
    )
    
    return shipment

@router.put("/{shipment_id}", response_model=ShipmentResponse)
async def update_shipment(shipment_id: str, data: ShipmentUpdate, user: dict = Depends(get_current_user)):
    return await ShipmentService.update(shipment_id, data, user)

@router.put("/{shipment_id}/ebrc", response_model=ShipmentResponse)
async def update_ebrc_status(shipment_id: str, data: EBRCUpdateRequest, user: dict = Depends(get_current_user)):
    """Update e-BRC status for a shipment"""
    return await ShipmentService.update_ebrc(shipment_id, data, user)

@router.delete("/{shipment_id}")
async def delete_shipment(shipment_id: str, user: dict = Depends(get_current_user)):
    return await ShipmentService.delete(shipment_id, user)
