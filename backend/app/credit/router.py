from fastapi import APIRouter, Depends
from ..core.dependencies import get_current_user
from ..services.credit_scoring_service import CreditScoringService
from ..services.tenant_auth_service import TenantAuthService

router = APIRouter(prefix="/credit", tags=["Credit Intelligence"])

@router.get("/buyer-score/{buyer_id}")
async def get_buyer_score(buyer_id: str, user: dict = Depends(get_current_user)):
    """Get real aggregation-based buyer credit score."""
    return await CreditScoringService.calculate_buyer_score(
        buyer_id, TenantAuthService.get_company_id(user), user.get("id")
    )

@router.get("/company-score")
async def get_company_score(user: dict = Depends(get_current_user)):
    """Get real aggregation-based company credit score."""
    return await CreditScoringService.calculate_company_score(
        TenantAuthService.get_company_id(user), user.get("id")
    )

@router.get("/payment-behavior")
async def get_payment_behavior(user: dict = Depends(get_current_user)):
    """Get aggregation-based payment behavior analysis."""
    return await CreditScoringService.get_payment_behavior_analysis(
        TenantAuthService.get_company_id(user), user.get("id")
    )
