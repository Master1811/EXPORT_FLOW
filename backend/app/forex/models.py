"""
Forex Models with Strict Validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from enum import Enum
import re


# Valid currency codes (ISO 4217)
VALID_CURRENCIES = {
    "USD", "EUR", "GBP", "AED", "JPY", "CNY", "SGD", 
    "CHF", "CAD", "AUD", "NZD", "HKD", "SAR", "KWD",
    "QAR", "OMR", "BHD", "MYR", "THB", "IDR", "KRW"
}

# Rate sources
class RateSource(str, Enum):
    MANUAL = "manual"
    RBI = "rbi"
    BANK = "bank"
    API = "api"
    MARKET = "market"


class ForexRateCreate(BaseModel):
    """Create a forex rate with strict validation"""
    
    currency: str = Field(
        ...,
        min_length=3,
        max_length=3,
        description="ISO 4217 currency code (e.g., USD, EUR)"
    )
    
    rate: float = Field(
        ...,
        gt=0,  # Must be positive
        lt=1000000,  # Reasonable upper limit
        description="Exchange rate against INR"
    )
    
    buy_rate: Optional[float] = Field(
        None,
        gt=0,
        lt=1000000,
        description="Bank buying rate"
    )
    
    sell_rate: Optional[float] = Field(
        None,
        gt=0,
        lt=1000000,
        description="Bank selling rate"
    )
    
    source: RateSource = Field(
        default=RateSource.MANUAL,
        description="Source of the rate"
    )
    
    source_reference: Optional[str] = Field(
        None,
        max_length=200,
        description="Reference ID from source (e.g., RBI circular number)"
    )
    
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Additional notes"
    )
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Standardize and validate currency code"""
        # Normalize: uppercase, strip whitespace
        normalized = v.strip().upper()
        
        # Check against valid currencies
        if normalized not in VALID_CURRENCIES:
            raise ValueError(f"Invalid currency code '{v}'. Valid codes: {', '.join(sorted(VALID_CURRENCIES))}")
        
        return normalized
    
    @field_validator('rate', 'buy_rate', 'sell_rate')
    @classmethod
    def validate_rate(cls, v: Optional[float]) -> Optional[float]:
        """Validate rate is reasonable"""
        if v is not None:
            if v <= 0:
                raise ValueError("Rate must be positive")
            if v > 500000:
                raise ValueError("Rate seems unreasonably high. Please verify.")
        return v


class ForexRateResponse(BaseModel):
    """Response model for forex rate"""
    id: str
    currency: str
    rate: float
    buy_rate: Optional[float] = None
    sell_rate: Optional[float] = None
    spread: Optional[float] = None
    source: str
    source_reference: Optional[str] = None
    company_id: Optional[str] = None
    created_by: Optional[str] = None
    timestamp: str
    previous_rate: Optional[float] = None
    change_percent: Optional[float] = None


class ForexHistoryQuery(BaseModel):
    """Query parameters for forex history"""
    currency: str = Field(..., min_length=3, max_length=3)
    days: int = Field(default=30, ge=1, le=365)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        return v.strip().upper()


class ForexAlert(BaseModel):
    """Alert for abnormal rate changes"""
    id: str
    currency: str
    old_rate: float
    new_rate: float
    change_percent: float
    alert_type: str  # "spike", "drop", "anomaly"
    timestamp: str
    acknowledged: bool = False
