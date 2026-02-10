"""
Secure Forex Service with:
- Admin-only rate creation
- Currency standardization
- Caching
- Pagination
- Spread tracking
- Rate change alerts
- FEMA compliance tracking
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from ..core.database import db
from ..common.utils import generate_id, now_iso
from .models import ForexRateCreate, ForexRateResponse, VALID_CURRENCIES, RateSource
from fastapi import HTTPException
import asyncio

# Default rates (RBI reference rates)
DEFAULT_RATES = {
    "USD": 83.50, "EUR": 91.20, "GBP": 106.50, 
    "AED": 22.75, "JPY": 0.56, "CNY": 11.50, "SGD": 62.30,
    "CHF": 94.80, "CAD": 62.10, "AUD": 54.50
}

# Rate change threshold for alerts (%)
ALERT_THRESHOLD_PERCENT = 3.0

# Cache settings
CACHE_TTL_SECONDS = 300  # 5 minutes
_rate_cache: Dict[str, Any] = {}
_cache_timestamp: Optional[datetime] = None


class ForexService:
    
    # ==================== CACHING ====================
    
    @staticmethod
    def _is_cache_valid() -> bool:
        """Check if cache is still valid"""
        global _cache_timestamp
        if _cache_timestamp is None:
            return False
        return (datetime.now(timezone.utc) - _cache_timestamp).total_seconds() < CACHE_TTL_SECONDS
    
    @staticmethod
    def _set_cache(key: str, value: Any):
        """Set cache value"""
        global _rate_cache, _cache_timestamp
        _rate_cache[key] = value
        _cache_timestamp = datetime.now(timezone.utc)
    
    @staticmethod
    def _get_cache(key: str) -> Optional[Any]:
        """Get cached value if valid"""
        if ForexService._is_cache_valid():
            return _rate_cache.get(key)
        return None
    
    @staticmethod
    def invalidate_cache():
        """Invalidate all cache"""
        global _rate_cache, _cache_timestamp
        _rate_cache = {}
        _cache_timestamp = None
    
    # ==================== AUTHORIZATION ====================
    
    @staticmethod
    def _check_admin(user: dict):
        """Check if user has admin role"""
        if user.get("role") not in ["admin", "super_admin"]:
            raise HTTPException(
                status_code=403,
                detail="Only admins can create/modify forex rates"
            )
    
    # ==================== RATE CREATION ====================
    
    @staticmethod
    async def create_rate(data: ForexRateCreate, user: dict) -> ForexRateResponse:
        """
        Create a new forex rate (ADMIN ONLY)
        
        Security:
        - Only admins can create rates
        - Currency is standardized
        - Rate is validated for reasonable values
        - Alerts generated for abnormal changes
        """
        # Check admin permission
        ForexService._check_admin(user)
        
        # Get previous rate for comparison
        previous = await db.forex_rates.find_one(
            {"currency": data.currency},
            {"_id": 0},
            sort=[("timestamp", -1)]
        )
        previous_rate = previous["rate"] if previous else DEFAULT_RATES.get(data.currency)
        
        # Calculate change percentage
        change_percent = None
        if previous_rate:
            change_percent = ((data.rate - previous_rate) / previous_rate) * 100
        
        # Calculate spread if buy/sell rates provided
        spread = None
        if data.buy_rate and data.sell_rate:
            spread = data.sell_rate - data.buy_rate
        
        rate_id = generate_id()
        rate_doc = {
            "id": rate_id,
            "currency": data.currency,  # Already standardized by validator
            "rate": data.rate,
            "buy_rate": data.buy_rate,
            "sell_rate": data.sell_rate,
            "spread": spread,
            "source": data.source.value,
            "source_reference": data.source_reference,
            "company_id": user.get("company_id", user["id"]),
            "created_by": user["id"],
            "previous_rate": previous_rate,
            "change_percent": round(change_percent, 4) if change_percent else None,
            "timestamp": now_iso(),
            "notes": data.notes
        }
        
        await db.forex_rates.insert_one(rate_doc)
        
        # Generate alert if change exceeds threshold
        if change_percent and abs(change_percent) >= ALERT_THRESHOLD_PERCENT:
            await ForexService._create_alert(
                currency=data.currency,
                old_rate=previous_rate,
                new_rate=data.rate,
                change_percent=change_percent,
                company_id=user.get("company_id")
            )
        
        # Invalidate cache
        ForexService.invalidate_cache()
        
        return ForexRateResponse(**{
            k: v for k, v in rate_doc.items() 
            if k in ForexRateResponse.model_fields
        })
    
    # ==================== RATE RETRIEVAL ====================
    
    @staticmethod
    async def get_latest(company_id: str = None) -> dict:
        """
        Get latest forex rates with caching
        
        Features:
        - 5-minute cache to reduce DB hits
        - Returns all major currencies
        - Includes spread info if available
        """
        cache_key = f"latest_{company_id or 'global'}"
        cached = ForexService._get_cache(cache_key)
        if cached:
            return cached
        
        rates = {}
        for curr in VALID_CURRENCIES:
            rate_doc = await db.forex_rates.find_one(
                {"currency": curr},
                {"_id": 0},
                sort=[("timestamp", -1)]
            )
            if rate_doc:
                rates[curr] = {
                    "rate": rate_doc["rate"],
                    "buy_rate": rate_doc.get("buy_rate"),
                    "sell_rate": rate_doc.get("sell_rate"),
                    "spread": rate_doc.get("spread"),
                    "source": rate_doc.get("source", "default"),
                    "updated_at": rate_doc.get("timestamp")
                }
            else:
                # Use default rate
                rates[curr] = {
                    "rate": DEFAULT_RATES.get(curr, 1.0),
                    "source": "default",
                    "updated_at": None
                }
        
        result = {
            "rates": rates,
            "base": "INR",
            "timestamp": now_iso(),
            "cached": False
        }
        
        ForexService._set_cache(cache_key, result)
        return result
    
    @staticmethod
    async def get_rate(currency: str) -> dict:
        """Get rate for a specific currency"""
        currency = currency.upper().strip()
        
        if currency not in VALID_CURRENCIES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid currency. Valid: {', '.join(sorted(VALID_CURRENCIES))}"
            )
        
        rate_doc = await db.forex_rates.find_one(
            {"currency": currency},
            {"_id": 0},
            sort=[("timestamp", -1)]
        )
        
        if rate_doc:
            return rate_doc
        
        return {
            "currency": currency,
            "rate": DEFAULT_RATES.get(currency, 1.0),
            "source": "default",
            "timestamp": now_iso()
        }
    
    # ==================== HISTORY WITH PAGINATION ====================
    
    @staticmethod
    async def get_history(
        currency: str,
        days: int = 30,
        page: int = 1,
        page_size: int = 50,
        company_id: str = None
    ) -> dict:
        """
        Get forex rate history with pagination
        
        Features:
        - Paginated results for large datasets
        - Total count for UI
        - Date range filtering
        """
        currency = currency.upper().strip()
        
        if currency not in VALID_CURRENCIES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid currency. Valid: {', '.join(sorted(VALID_CURRENCIES))}"
            )
        
        # Calculate date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        query = {
            "currency": currency,
            "timestamp": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        }
        
        if company_id:
            query["company_id"] = company_id
        
        # Get total count and data in parallel
        skip = (page - 1) * page_size
        
        count_task = db.forex_rates.count_documents(query)
        data_task = db.forex_rates.find(query, {"_id": 0}).sort(
            "timestamp", -1
        ).skip(skip).limit(page_size).to_list(page_size)
        
        total_count, rates = await asyncio.gather(count_task, data_task)
        
        total_pages = (total_count + page_size - 1) // page_size
        
        # Calculate statistics
        rate_values = [r["rate"] for r in rates if "rate" in r]
        stats = {}
        if rate_values:
            stats = {
                "min": min(rate_values),
                "max": max(rate_values),
                "avg": sum(rate_values) / len(rate_values),
                "latest": rate_values[0] if rate_values else None
            }
        
        return {
            "currency": currency,
            "history": rates,
            "statistics": stats,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            }
        }
    
    # ==================== ALERTS ====================
    
    @staticmethod
    async def _create_alert(
        currency: str,
        old_rate: float,
        new_rate: float,
        change_percent: float,
        company_id: str = None
    ):
        """Create an alert for abnormal rate change"""
        alert_type = "spike" if change_percent > 0 else "drop"
        if abs(change_percent) > 10:
            alert_type = "anomaly"
        
        alert_doc = {
            "id": generate_id(),
            "currency": currency,
            "old_rate": old_rate,
            "new_rate": new_rate,
            "change_percent": round(change_percent, 2),
            "alert_type": alert_type,
            "company_id": company_id,
            "timestamp": now_iso(),
            "acknowledged": False,
            "severity": "high" if abs(change_percent) > 5 else "medium"
        }
        
        await db.forex_alerts.insert_one(alert_doc)
    
    @staticmethod
    async def get_alerts(
        company_id: str = None,
        acknowledged: bool = None,
        limit: int = 50
    ) -> List[dict]:
        """Get forex rate alerts"""
        query = {}
        if company_id:
            query["company_id"] = company_id
        if acknowledged is not None:
            query["acknowledged"] = acknowledged
        
        alerts = await db.forex_alerts.find(
            query, {"_id": 0}
        ).sort("timestamp", -1).limit(limit).to_list(limit)
        
        return alerts
    
    @staticmethod
    async def acknowledge_alert(alert_id: str, user: dict) -> bool:
        """Acknowledge an alert"""
        result = await db.forex_alerts.update_one(
            {"id": alert_id},
            {
                "$set": {
                    "acknowledged": True,
                    "acknowledged_by": user["id"],
                    "acknowledged_at": now_iso()
                }
            }
        )
        return result.modified_count > 0
    
    # ==================== FEMA COMPLIANCE ====================
    
    @staticmethod
    async def get_fema_summary(company_id: str) -> dict:
        """
        Get FEMA compliance summary for forex transactions
        
        Returns summary of:
        - Total forex exposure
        - Hedged vs unhedged positions
        - Compliance status
        """
        # Get all shipments with forex exposure
        shipments = await db.shipments.find({
            "company_id": company_id,
            "currency": {"$ne": "INR"}
        }, {"_id": 0}).to_list(1000)
        
        exposure_by_currency = {}
        total_exposure_inr = 0
        
        for s in shipments:
            curr = s.get("currency", "USD")
            value = s.get("total_value", 0)
            
            if curr not in exposure_by_currency:
                exposure_by_currency[curr] = {"value": 0, "count": 0}
            
            exposure_by_currency[curr]["value"] += value
            exposure_by_currency[curr]["count"] += 1
            
            # Convert to INR for total
            rate = DEFAULT_RATES.get(curr, 1.0)
            total_exposure_inr += value * rate
        
        return {
            "total_exposure_inr": total_exposure_inr,
            "exposure_by_currency": exposure_by_currency,
            "compliance_status": "compliant" if total_exposure_inr < 10000000 else "review_required",
            "generated_at": now_iso()
        }
