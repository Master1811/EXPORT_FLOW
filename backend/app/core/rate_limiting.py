"""
Rate Limiting Configuration
Protects heavy endpoints from abuse and ensures fair resource usage
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from typing import Callable
import logging

logger = logging.getLogger(__name__)


def get_company_id_or_ip(request: Request) -> str:
    """
    Get rate limit key based on authenticated user's company_id or IP address
    Uses company_id for authenticated requests, IP for unauthenticated
    """
    # Try to get company_id from request state (set by auth middleware)
    if hasattr(request.state, "user") and request.state.user:
        return f"company:{request.state.user.get('company_id', request.state.user.get('id'))}"
    
    # Fall back to IP address
    return f"ip:{get_remote_address(request)}"


def get_ip_address(request: Request) -> str:
    """Get IP address for rate limiting"""
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(
    key_func=get_company_id_or_ip,
    default_limits=["1000/minute"],  # Default: 1000 requests per minute
    headers_enabled=True,  # Add rate limit headers to responses
    strategy="fixed-window",  # Use fixed window strategy
)


# Rate limit configurations for different endpoint categories
RATE_LIMITS = {
    # Authentication - strict limits to prevent brute force
    "auth_login": "5/minute",  # 5 attempts per minute per IP
    "auth_register": "3/minute",  # 3 registrations per minute per IP
    "auth_refresh": "30/minute",  # 30 token refreshes per minute
    "auth_password_change": "3/hour",  # 3 password changes per hour
    
    # Heavy processing endpoints
    "ocr_process": "20/hour",  # 20 OCR jobs per hour per company
    "ai_chat": "60/hour",  # 60 AI interactions per hour per company
    "export_data": "10/hour",  # 10 data exports per hour per company
    
    # Data sync endpoints
    "sync_gst": "10/hour",  # 10 GST syncs per hour per company
    "sync_bank": "10/hour",  # 10 bank syncs per hour per company
    "sync_customs": "10/hour",  # 10 customs syncs per hour per company
    
    # Standard CRUD operations
    "create": "100/minute",  # 100 creates per minute per company
    "read": "500/minute",  # 500 reads per minute per company
    "update": "100/minute",  # 100 updates per minute per company
    "delete": "50/minute",  # 50 deletes per minute per company
    
    # Bulk operations
    "bulk_create": "10/minute",  # 10 bulk creates per minute
    "bulk_update": "10/minute",  # 10 bulk updates per minute
    
    # Dashboard - frequently accessed
    "dashboard": "120/minute",  # 2 per second for dashboard
}


def setup_rate_limiting(app):
    """
    Setup rate limiting for the FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    # Add limiter to app state
    app.state.limiter = limiter
    
    # Add rate limit exceeded handler
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    logger.info("Rate limiting configured successfully")


def get_rate_limit_decorator(category: str) -> Callable:
    """
    Get a rate limit decorator for a specific category
    
    Args:
        category: Rate limit category from RATE_LIMITS
        
    Returns:
        Limiter.limit decorator with appropriate limits
    """
    limit = RATE_LIMITS.get(category, "100/minute")
    return limiter.limit(limit)


# Pre-configured decorators for common use cases
auth_login_limit = limiter.limit(RATE_LIMITS["auth_login"], key_func=get_ip_address)
auth_register_limit = limiter.limit(RATE_LIMITS["auth_register"], key_func=get_ip_address)
ocr_process_limit = limiter.limit(RATE_LIMITS["ocr_process"])
ai_chat_limit = limiter.limit(RATE_LIMITS["ai_chat"])
export_limit = limiter.limit(RATE_LIMITS["export_data"])
sync_limit = limiter.limit(RATE_LIMITS["sync_gst"])  # Generic sync limit
dashboard_limit = limiter.limit(RATE_LIMITS["dashboard"])
