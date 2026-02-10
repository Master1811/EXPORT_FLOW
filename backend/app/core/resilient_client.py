"""
Resilient External API Client
- Exponential backoff with tenacity
- Timeout management with asyncio.wait_for
- Circuit breaker pattern for external services
"""
import asyncio
import aiohttp
from typing import Any, Dict, Optional, Callable
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryError
)
import logging
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreaker:
    """
    Circuit breaker implementation for external services
    """
    name: str
    failure_threshold: int = 5  # Failures before opening
    recovery_timeout: int = 30  # Seconds before trying again
    success_threshold: int = 2  # Successes needed to close
    
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    
    def can_execute(self) -> bool:
        """Check if request can proceed"""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time:
                if datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.recovery_timeout):
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    logger.info(f"Circuit breaker {self.name} entering half-open state")
                    return True
            return False
        
        # HALF_OPEN - allow limited requests
        return True
    
    def record_success(self):
        """Record a successful request"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info(f"Circuit breaker {self.name} closed - service recovered")
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0
    
    def record_failure(self):
        """Record a failed request"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker {self.name} opened - service still failing")
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker {self.name} opened after {self.failure_count} failures")


# Circuit breakers for external services
circuit_breakers: Dict[str, CircuitBreaker] = {
    "gst_api": CircuitBreaker(name="gst_api"),
    "icegate_api": CircuitBreaker(name="icegate_api"),
    "bank_aa_api": CircuitBreaker(name="bank_aa_api"),
    "gemini_api": CircuitBreaker(name="gemini_api"),
}


class ExternalAPIError(Exception):
    """Exception for external API failures"""
    def __init__(self, service: str, message: str, status_code: int = None):
        self.service = service
        self.status_code = status_code
        super().__init__(f"{service}: {message}")


class ResilientClient:
    """
    Resilient HTTP client for external APIs
    - Automatic retries with exponential backoff
    - Configurable timeouts
    - Circuit breaker integration
    """
    
    DEFAULT_TIMEOUT = 15  # seconds
    MAX_RETRIES = 3
    MAX_DELAY = 10  # seconds
    
    def __init__(
        self,
        service_name: str,
        base_url: str = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES
    ):
        self.service_name = service_name
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.circuit = circuit_breakers.get(service_name, CircuitBreaker(name=service_name))
    
    def _get_retry_decorator(self):
        """Get configured retry decorator"""
        return retry(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=self.MAX_DELAY),
            retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
            before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING),
            reraise=True
        )
    
    async def _request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with timeout"""
        async with aiohttp.ClientSession() as session:
            async with asyncio.timeout(self.timeout):
                async with session.request(method, url, **kwargs) as response:
                    if response.status >= 400:
                        text = await response.text()
                        raise ExternalAPIError(
                            self.service_name,
                            f"HTTP {response.status}: {text[:200]}",
                            response.status
                        )
                    return await response.json()
    
    async def request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a resilient HTTP request
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (will be joined with base_url)
            **kwargs: Additional arguments for aiohttp
            
        Returns:
            Response JSON
            
        Raises:
            ExternalAPIError: If request fails after retries
        """
        # Check circuit breaker
        if not self.circuit.can_execute():
            raise ExternalAPIError(
                self.service_name,
                "Service temporarily unavailable (circuit breaker open)"
            )
        
        url = f"{self.base_url}/{endpoint}" if self.base_url else endpoint
        
        retry_decorator = self._get_retry_decorator()
        
        @retry_decorator
        async def _do_request():
            return await self._request(method, url, **kwargs)
        
        try:
            result = await _do_request()
            self.circuit.record_success()
            return result
        except RetryError as e:
            self.circuit.record_failure()
            logger.error(
                "External API request failed after retries",
                service=self.service_name,
                endpoint=endpoint,
                error=str(e.last_attempt.exception())
            )
            raise ExternalAPIError(
                self.service_name,
                f"Request failed after {self.max_retries} attempts: {e.last_attempt.exception()}"
            )
        except Exception as e:
            self.circuit.record_failure()
            raise ExternalAPIError(self.service_name, str(e))
    
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """GET request"""
        return await self.request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """POST request"""
        return await self.request("POST", endpoint, **kwargs)
    
    async def put(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """PUT request"""
        return await self.request("PUT", endpoint, **kwargs)


# Pre-configured clients for common external services
def get_gst_client() -> ResilientClient:
    """Get GST API client"""
    return ResilientClient(
        service_name="gst_api",
        base_url="https://api.gst.gov.in",  # Placeholder
        timeout=15,
        max_retries=3
    )


def get_icegate_client() -> ResilientClient:
    """Get ICEGATE API client"""
    return ResilientClient(
        service_name="icegate_api", 
        base_url="https://api.icegate.gov.in",  # Placeholder
        timeout=15,
        max_retries=3
    )


def get_bank_aa_client() -> ResilientClient:
    """Get Bank Account Aggregator client"""
    return ResilientClient(
        service_name="bank_aa_api",
        timeout=20,  # Longer timeout for bank APIs
        max_retries=3
    )


async def with_timeout(coro, timeout_seconds: int = 15):
    """
    Wrapper to apply timeout to any coroutine
    
    Args:
        coro: Coroutine to execute
        timeout_seconds: Maximum execution time
        
    Returns:
        Result of coroutine
        
    Raises:
        asyncio.TimeoutError: If timeout exceeded
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        logger.warning(f"Operation timed out after {timeout_seconds}s")
        raise


def get_circuit_breaker_status() -> Dict[str, Dict[str, Any]]:
    """Get status of all circuit breakers for monitoring"""
    return {
        name: {
            "state": cb.state.value,
            "failure_count": cb.failure_count,
            "success_count": cb.success_count,
            "last_failure": cb.last_failure_time.isoformat() if cb.last_failure_time else None
        }
        for name, cb in circuit_breakers.items()
    }
