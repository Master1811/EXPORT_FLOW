"""
Secure Forex Router with:
- Rate limiting
- Admin-only rate creation
- Pagination
- Alert management
"""
from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from ..core.dependencies import get_current_user
from ..core.rate_limiting import limiter
from .models import ForexRateCreate, ForexRateResponse
from .service import ForexService

router = APIRouter(prefix="/forex", tags=["Forex"])


@router.post("/rate", response_model=ForexRateResponse)
@limiter.limit("10/minute")  # Rate limit: 10 rate creations per minute
async def create_forex_rate(
    request: Request,
    data: ForexRateCreate,
    user: dict = Depends(get_current_user)
):
    """
    Create a new forex rate.
    
    **ADMIN ONLY** - Only users with admin role can create rates.
    
    Features:
    - Currency code is standardized (USD, not usd or Us D)
    - Rate must be positive and reasonable (< 1,000,000)
    - Alerts generated if rate changes by more than 3%
    - Buy/sell rates tracked for spread calculation
    
    Rate limited: 10/minute per company.
    """
    return await ForexService.create_rate(data, user)


@router.get("/latest")
@limiter.limit("60/minute")  # Rate limit: 60 reads per minute
async def get_latest_forex(request: Request, response: Response):
    """
    Get latest forex rates for all currencies.
    
    Features:
    - 5-minute cache to reduce DB load
    - Returns buy/sell rates and spreads when available
    - Includes rate source and last update time
    
    Rate limited: 60/minute.
    """
    return await ForexService.get_latest()


@router.get("/rate/{currency}")
@limiter.limit("60/minute")
async def get_forex_rate(
    request: Request,
    response: Response,
    currency: str
):
    """
    Get current rate for a specific currency.
    
    Currency codes are case-insensitive (USD, usd, Usd all work).
    """
    return await ForexService.get_rate(currency)


@router.get("/history/{currency}")
@limiter.limit("30/minute")  # Rate limit: 30 history queries per minute
async def get_forex_history(
    request: Request,
    currency: str,
    days: int = Query(default=30, ge=1, le=365, description="Number of days of history"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=50, ge=1, le=200, description="Items per page"),
    user: dict = Depends(get_current_user)
):
    """
    Get forex rate history with pagination.
    
    Features:
    - Paginated results for large datasets
    - Statistics (min, max, avg) for the period
    - Date range filtering
    
    Rate limited: 30/minute per company.
    """
    return await ForexService.get_history(
        currency=currency,
        days=days,
        page=page,
        page_size=page_size,
        company_id=user.get("company_id")
    )


@router.get("/alerts")
async def get_forex_alerts(
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledged status"),
    limit: int = Query(default=50, ge=1, le=200),
    user: dict = Depends(get_current_user)
):
    """
    Get forex rate alerts for abnormal rate changes.
    
    Alerts are generated when:
    - Rate changes by more than 3% (medium severity)
    - Rate changes by more than 5% (high severity)
    - Anomalous changes detected (>10%)
    """
    return await ForexService.get_alerts(
        company_id=user.get("company_id"),
        acknowledged=acknowledged,
        limit=limit
    )


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_forex_alert(
    alert_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Acknowledge a forex rate alert.
    """
    success = await ForexService.acknowledge_alert(alert_id, user)
    if success:
        return {"message": "Alert acknowledged", "alert_id": alert_id}
    return {"message": "Alert not found or already acknowledged"}


@router.get("/fema/summary")
async def get_fema_summary(user: dict = Depends(get_current_user)):
    """
    Get FEMA compliance summary for forex exposure.
    
    Returns:
    - Total forex exposure in INR
    - Exposure breakdown by currency
    - Compliance status
    """
    return await ForexService.get_fema_summary(user.get("company_id", user["id"]))
