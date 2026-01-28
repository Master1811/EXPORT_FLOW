from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class InvoiceCreate(BaseModel):
    invoice_number: str
    invoice_date: str
    items: List[Dict[str, Any]]
    subtotal: float
    tax_amount: float = 0
    total_amount: float
    payment_terms: Optional[str] = None

class DocumentResponse(BaseModel):
    id: str
    document_type: str
    shipment_id: str
    document_number: str
    created_at: str
    data: Dict[str, Any]
