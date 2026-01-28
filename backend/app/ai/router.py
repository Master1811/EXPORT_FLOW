from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from ..core.dependencies import get_current_user
from .service import AIService

router = APIRouter(prefix="/ai", tags=["AI & Forecasting"])

class AIQueryRequest(BaseModel):
    query: str
    context: Optional[str] = None

@router.post("/query")
async def ai_query(data: AIQueryRequest, user: dict = Depends(get_current_user)):
    return await AIService.query(data.query, user)

@router.get("/refund-forecast")
async def get_refund_forecast(user: dict = Depends(get_current_user)):
    return await AIService.get_refund_forecast(user)

@router.get("/cashflow-forecast")
async def get_cashflow_forecast(user: dict = Depends(get_current_user)):
    return await AIService.get_cashflow_forecast(user)

@router.get("/incentive-optimizer")
async def get_incentive_optimizer(user: dict = Depends(get_current_user)):
    return await AIService.get_incentive_optimizer(user)

@router.get("/risk-alerts")
async def get_risk_alerts(user: dict = Depends(get_current_user)):
    return await AIService.get_risk_alerts(user)
