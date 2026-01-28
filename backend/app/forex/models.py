from pydantic import BaseModel
from typing import Optional

class ForexRateCreate(BaseModel):
    currency: str
    rate: float
    source: str = "manual"

class ForexRateResponse(BaseModel):
    id: str
    currency: str
    rate: float
    source: str
    timestamp: str
