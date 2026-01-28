from fastapi import APIRouter, Depends
from ..core.dependencies import get_current_user
from .service import CreditService

router = APIRouter(prefix="/credit", tags=["Credit Intelligence"])

@router.get("/buyer-score/{buyer_id}")
async def get_buyer_score(buyer_id: str, user: dict = Depends(get_current_user)):
    return await CreditService.get_buyer_score(buyer_id, user)

@router.get("/company-score")
async def get_company_score(user: dict = Depends(get_current_user)):
    return await CreditService.get_company_score(user)

@router.get("/payment-behavior")
async def get_payment_behavior(user: dict = Depends(get_current_user)):
    return await CreditService.get_payment_behavior(user)
