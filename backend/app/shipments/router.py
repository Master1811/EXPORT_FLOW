from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from ..core.dependencies import get_current_user
from .models import ShipmentCreate, ShipmentResponse, ShipmentUpdate
from .service import ShipmentService

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

@router.get("/{shipment_id}", response_model=ShipmentResponse)
async def get_shipment(shipment_id: str, user: dict = Depends(get_current_user)):
    return await ShipmentService.get(shipment_id)

@router.put("/{shipment_id}", response_model=ShipmentResponse)
async def update_shipment(shipment_id: str, data: ShipmentUpdate, user: dict = Depends(get_current_user)):
    return await ShipmentService.update(shipment_id, data)

@router.delete("/{shipment_id}")
async def delete_shipment(shipment_id: str, user: dict = Depends(get_current_user)):
    return await ShipmentService.delete(shipment_id)
