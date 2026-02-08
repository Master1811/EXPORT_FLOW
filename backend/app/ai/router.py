from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from ..core.dependencies import get_current_user
from .service import AIService

router = APIRouter(prefix="/ai", tags=["AI & Forecasting"])

class AIQueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    context: Optional[str] = None

@router.post("/query")
async def ai_query(data: AIQueryRequest, user: dict = Depends(get_current_user)):
    """Ask the AI assistant any export-related question"""
    return await AIService.query(data.query, user, data.session_id)

@router.get("/chat-history")
async def get_chat_history(
    session_id: Optional[str] = None,
    limit: int = 20,
    user: dict = Depends(get_current_user)
):
    """Get chat history"""
    return await AIService.get_chat_history(user, session_id, limit)

@router.get("/analyze-shipment/{shipment_id}")
async def analyze_shipment(shipment_id: str, user: dict = Depends(get_current_user)):
    """Get AI analysis of a specific shipment"""
    return await AIService.analyze_shipment(shipment_id, user)

@router.get("/refund-forecast")
async def get_refund_forecast(user: dict = Depends(get_current_user)):
    """Get expected refund forecast based on shipments"""
    return await AIService.get_refund_forecast(user)

@router.get("/cashflow-forecast")
async def get_cashflow_forecast(user: dict = Depends(get_current_user)):
    """Get cashflow forecast"""
    return await AIService.get_cashflow_forecast(user)

@router.get("/incentive-optimizer")
async def get_incentive_optimizer(user: dict = Depends(get_current_user)):
    """Get recommendations to optimize incentive claims"""
    return await AIService.get_incentive_optimizer(user)

@router.get("/risk-alerts")
async def get_risk_alerts(user: dict = Depends(get_current_user)):
    """Get risk alerts (overdue payments, e-BRC deadlines, etc.)"""
    return await AIService.get_risk_alerts(user)
