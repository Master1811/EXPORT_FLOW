from pydantic import BaseModel
from typing import Optional, List

class GSTInputCreditCreate(BaseModel):
    invoice_number: str
    supplier_gstin: str
    invoice_date: str
    taxable_value: float
    igst: float = 0
    cgst: float = 0
    sgst: float = 0
    total_tax: float

class GSTSummaryResponse(BaseModel):
    month: str
    total_export_value: float
    total_igst_paid: float
    refund_eligible: float
    refund_claimed: float
    refund_pending: float
