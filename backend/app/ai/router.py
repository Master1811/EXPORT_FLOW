"""
Secure AI Router with:
- Rate limiting on all endpoints
- Input validation
- Usage tracking endpoint
- Session management
"""
from fastapi import APIRouter, Depends, Query, Request, Response
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from ..core.dependencies import get_current_user
from ..core.rate_limiting import limiter, ai_chat_limit
from .service import AIService, MAX_QUERY_LENGTH, MIN_QUERY_LENGTH

router = APIRouter(prefix="/ai", tags=["AI & Forecasting"])


class AIQueryRequest(BaseModel):
    """AI query request with validation"""
    query: str = Field(
        ...,
        min_length=MIN_QUERY_LENGTH,
        max_length=MAX_QUERY_LENGTH,
        description=f"Query text ({MIN_QUERY_LENGTH}-{MAX_QUERY_LENGTH} characters)"
    )
    session_id: Optional[str] = Field(
        None,
        max_length=100,
        description="Session ID for continuing a conversation"
    )
    
    @field_validator('query')
    @classmethod
    def validate_query_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


@router.post("/query")
@ai_chat_limit  # Rate limited: 60/hour per company
async def ai_query(request: Request, response: Response, data: AIQueryRequest, user: dict = Depends(get_current_user)):
    """
    Ask the AI assistant any export-related question.
    
    **Security Features:**
    - Rate limited: 60 requests/hour per company
    - Daily limit: 500 requests/day per company
    - Query length: 3-5000 characters
    - Prompt injection protection
    - Response caching (5 min)
    - Usage tracked for billing
    
    **Session Management:**
    - Provide `session_id` to continue a conversation
    - Sessions are user-specific (cannot access other users' sessions)
    """
    return await AIService.query(data.query, user, data.session_id)


@router.get("/chat-history")
@limiter.limit("30/minute")
async def get_chat_history(
    request: Request,
    response: Response,
    session_id: Optional[str] = Query(None, max_length=100),
    limit: int = Query(default=20, ge=1, le=100),
    user: dict = Depends(get_current_user)
):
    """
    Get chat history for the current user.
    
    **Security:** Only returns the user's own history.
    Cannot access other users' sessions.
    """
    return await AIService.get_chat_history(user, session_id, limit)


@router.get("/sessions")
@limiter.limit("30/minute")
async def get_sessions(request: Request, response: Response, user: dict = Depends(get_current_user)):
    """
    Get all chat sessions for the current user.
    
    Returns list of sessions with last activity and message count.
    """
    return await AIService.get_sessions(user)


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, user: dict = Depends(get_current_user)):
    """
    Delete a chat session and all its history.
    
    **Security:** Can only delete own sessions.
    """
    success = await AIService.delete_session(user, session_id)
    if success:
        return {"message": "Session deleted", "session_id": session_id}
    return {"message": "Session not found or already deleted"}


@router.get("/analyze-shipment/{shipment_id}")
@ai_chat_limit
async def analyze_shipment(request: Request, response: Response, shipment_id: str, user: dict = Depends(get_current_user)):
    """
    Get AI analysis of a specific shipment.
    
    **Security:**
    - Rate limited (counts toward AI quota)
    - Only analyzes shipments belonging to user's company
    - PII is anonymized before sending to AI
    """
    return await AIService.analyze_shipment(shipment_id, user)


@router.get("/refund-forecast")
@limiter.limit("30/minute")
async def get_refund_forecast(request: Request, response: Response, user: dict = Depends(get_current_user)):
    """
    Get expected refund forecast based on shipments.
    
    Calculates potential RoDTEP, RoSCTL, and Drawback refunds.
    """
    return await AIService.get_refund_forecast(user)


@router.get("/cashflow-forecast")
@limiter.limit("30/minute")
async def get_cashflow_forecast(request: Request, response: Response, user: dict = Depends(get_current_user)):
    """
    Get cashflow forecast based on receivables.
    """
    return await AIService.get_cashflow_forecast(user)


@router.get("/incentive-optimizer")
@limiter.limit("30/minute")
async def get_incentive_optimizer(request: Request, response: Response, user: dict = Depends(get_current_user)):
    """
    Get recommendations to optimize incentive claims.
    """
    return await AIService.get_incentive_optimizer(user)


@router.get("/risk-alerts")
@limiter.limit("30/minute")
async def get_risk_alerts(request: Request, user: dict = Depends(get_current_user)):
    """
    Get risk alerts (overdue payments, e-BRC deadlines, etc.)
    """
    return await AIService.get_risk_alerts(user)


@router.get("/usage")
@limiter.limit("30/minute")
async def get_usage_stats(request: Request, user: dict = Depends(get_current_user)):
    """
    Get AI usage statistics for billing and monitoring.
    
    Returns:
    - Total requests in period
    - Estimated token usage
    - Estimated cost
    - Success rate
    """
    return await AIService.get_usage_stats(user)
