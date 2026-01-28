from pydantic import BaseModel
from typing import List, Optional

class IncentiveCalculateRequest(BaseModel):
    shipment_id: str
    hs_codes: List[str]
    fob_value: float
    currency: str = "INR"

class IncentiveResponse(BaseModel):
    id: str
    shipment_id: str
    scheme: str
    hs_code: str
    fob_value: float
    rate_percent: float
    incentive_amount: float
    status: str
    created_at: str
