from pydantic import BaseModel
from typing import Optional

class PaymentCreate(BaseModel):
    shipment_id: str
    amount: float
    currency: str
    payment_date: str
    payment_mode: str
    bank_reference: Optional[str] = None
    exchange_rate: Optional[float] = None
    inr_amount: Optional[float] = None

class PaymentResponse(BaseModel):
    id: str
    shipment_id: str
    amount: float
    currency: str
    payment_date: str
    payment_mode: str
    bank_reference: Optional[str]
    exchange_rate: Optional[float]
    inr_amount: Optional[float]
    status: str
    created_at: str
