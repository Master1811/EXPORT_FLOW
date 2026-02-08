from fastapi import APIRouter, Depends, Query, Request
from typing import Optional, List
from ..core.dependencies import get_current_user
from .models import ShipmentCreate, ShipmentResponse, ShipmentUpdate, EBRCUpdateRequest
from .service import ShipmentService
from ..common.audit_service import audit_service

router = APIRouter(prefix="/shipments", tags=["Shipments"])

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
    """Get shipment with unmasked PII (explicit request) - Logged for audit trail"""
    # Get the shipment with unmasked PII
    shipment = await ShipmentService.get(shipment_id, user, mask_sensitive=False)
    
    # Log the PII access to audit trail (TC-SEC-03)
    client_ip = request.client.host if request.client else None
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
