from fastapi import APIRouter, Depends, Query
from ..core.dependencies import get_current_user
from .models import IncentiveCalculateRequest, IncentiveResponse
from .service import IncentiveService

router = APIRouter(prefix="/incentives", tags=["Incentives"])

@router.get("/rodtep-eligibility")
async def check_rodtep_eligibility(hs_code: str = Query(...)):
    return await IncentiveService.check_eligibility(hs_code)

@router.post("/calculate", response_model=IncentiveResponse)
async def calculate_incentive(data: IncentiveCalculateRequest, user: dict = Depends(get_current_user)):
    return await IncentiveService.calculate(data, user)

@router.get("/lost-money")
async def get_lost_incentives(user: dict = Depends(get_current_user)):
    return await IncentiveService.get_lost_money(user)

@router.get("/summary")
async def get_incentives_summary(user: dict = Depends(get_current_user)):
    return await IncentiveService.get_summary(user)
