from fastapi import APIRouter, Depends
from typing import List
from ..core.dependencies import get_current_user
from .models import PaymentCreate, PaymentResponse
from .service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("", response_model=PaymentResponse)
async def create_payment(data: PaymentCreate, user: dict = Depends(get_current_user)):
    return await PaymentService.create(data, user)

@router.get("/shipment/{shipment_id}", response_model=List[PaymentResponse])
async def get_shipment_payments(shipment_id: str, user: dict = Depends(get_current_user)):
    return await PaymentService.get_by_shipment(shipment_id, user)

@router.get("/receivables")
async def get_receivables(user: dict = Depends(get_current_user)):
    return await PaymentService.get_receivables(user)

@router.get("/receivables/aging")
async def get_receivables_aging(user: dict = Depends(get_current_user)):
    return await PaymentService.get_aging(user)

@router.get("/receivables/aging-dashboard")
async def get_aging_dashboard(user: dict = Depends(get_current_user)):
    """Get comprehensive receivables aging dashboard with buckets and alerts"""
    return await PaymentService.get_aging_dashboard(user)
