from pydantic import BaseModel
from typing import Optional, List

class ShipmentCreate(BaseModel):
    shipment_number: str
    buyer_name: str
    buyer_country: str
    destination_port: str
    origin_port: str
    incoterm: str = "FOB"
    currency: str = "USD"
    total_value: float
    status: str = "draft"
    expected_ship_date: Optional[str] = None
    actual_ship_date: Optional[str] = None
    product_description: Optional[str] = None
    hs_codes: Optional[List[str]] = []
    # e-BRC fields
    ebrc_status: str = "pending"  # pending, filed, approved, rejected
    ebrc_filed_date: Optional[str] = None
    ebrc_number: Optional[str] = None
    ebrc_due_date: Optional[str] = None
    # Buyer contact (for PII masking)
    buyer_email: Optional[str] = None
    buyer_phone: Optional[str] = None
    buyer_pan: Optional[str] = None
    buyer_bank_account: Optional[str] = None

class ShipmentResponse(BaseModel):
    id: str
    shipment_number: str
    buyer_name: str
    buyer_country: str
    destination_port: str
    origin_port: str
    incoterm: str
    currency: str
    total_value: float
    status: str
    expected_ship_date: Optional[str] = None
    actual_ship_date: Optional[str] = None
    product_description: Optional[str] = None
    hs_codes: List[str] = []
    company_id: str
    created_at: str
    updated_at: str
    # e-BRC fields
    ebrc_status: Optional[str] = "pending"
    ebrc_filed_date: Optional[str] = None
    ebrc_number: Optional[str] = None
    ebrc_due_date: Optional[str] = None
    ebrc_days_remaining: Optional[int] = None
    # Buyer contact (masked by default)
    buyer_email: Optional[str] = None
    buyer_phone: Optional[str] = None
    buyer_pan: Optional[str] = None
    buyer_bank_account: Optional[str] = None

class ShipmentUpdate(BaseModel):
    buyer_name: Optional[str] = None
    buyer_country: Optional[str] = None
    destination_port: Optional[str] = None
    origin_port: Optional[str] = None
    incoterm: Optional[str] = None
    currency: Optional[str] = None
    total_value: Optional[float] = None
    status: Optional[str] = None
    expected_ship_date: Optional[str] = None
    actual_ship_date: Optional[str] = None
    product_description: Optional[str] = None
    hs_codes: Optional[List[str]] = None
    # e-BRC fields
    ebrc_status: Optional[str] = None
    ebrc_filed_date: Optional[str] = None
    ebrc_number: Optional[str] = None
    # Buyer contact
    buyer_email: Optional[str] = None
    buyer_phone: Optional[str] = None
    buyer_pan: Optional[str] = None
    buyer_bank_account: Optional[str] = None

class EBRCUpdateRequest(BaseModel):
    ebrc_status: str
    ebrc_filed_date: Optional[str] = None
    ebrc_number: Optional[str] = None
