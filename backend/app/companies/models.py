from pydantic import BaseModel
from typing import Optional

class CompanyCreate(BaseModel):
    name: str
    gstin: Optional[str] = None
    pan: Optional[str] = None
    iec_code: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    bank_account: Optional[str] = None
    bank_ifsc: Optional[str] = None

class CompanyResponse(BaseModel):
    id: str
    name: str
    gstin: Optional[str] = None
    pan: Optional[str] = None
    iec_code: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str
    created_at: str
