from fastapi import APIRouter, Depends
from ..core.dependencies import get_current_user
from .models import ForexRateCreate, ForexRateResponse
from .service import ForexService

router = APIRouter(prefix="/forex", tags=["Forex"])

@router.post("/rate", response_model=ForexRateResponse)
async def create_forex_rate(data: ForexRateCreate, user: dict = Depends(get_current_user)):
    return await ForexService.create_rate(data, user)

@router.get("/latest")
async def get_latest_forex():
    return await ForexService.get_latest()

@router.get("/history/{currency}")
async def get_forex_history(currency: str, days: int = 30, user: dict = Depends(get_current_user)):
    return await ForexService.get_history(currency, days)
