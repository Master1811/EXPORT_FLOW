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
    product_description: Optional[str] = None
    hs_codes: Optional[List[str]] = []

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
    expected_ship_date: Optional[str]
    product_description: Optional[str]
    hs_codes: List[str]
    company_id: str
    created_at: str
    updated_at: str

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
    product_description: Optional[str] = None
    hs_codes: Optional[List[str]] = None
