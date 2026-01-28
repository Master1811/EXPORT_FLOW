import uuid
from datetime import datetime, timezone

def generate_id() -> str:
    return str(uuid.uuid4())

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def format_currency(value: float, currency: str = "INR") -> str:
    if currency == "INR":
        if value >= 10000000:
            return f"₹{value / 10000000:.2f}Cr"
        if value >= 100000:
            return f"₹{value / 100000:.2f}L"
        return f"₹{value:,.0f}"
    return f"{currency} {value:,.2f}"
