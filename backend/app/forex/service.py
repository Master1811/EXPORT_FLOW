from typing import List
from ..core.database import db
from ..common.utils import generate_id, now_iso
from .models import ForexRateCreate, ForexRateResponse

DEFAULT_RATES = {
    "USD": 83.50, "EUR": 91.20, "GBP": 106.50, 
    "AED": 22.75, "JPY": 0.56, "CNY": 11.50, "SGD": 62.30
}

class ForexService:
    @staticmethod
    async def create_rate(data: ForexRateCreate, user: dict) -> ForexRateResponse:
        rate_id = generate_id()
        rate_doc = {
            "id": rate_id,
            "currency": data.currency,
            "rate": data.rate,
            "source": data.source,
            "company_id": user.get("company_id", user["id"]),
            "timestamp": now_iso()
        }
        await db.forex_rates.insert_one(rate_doc)
        return ForexRateResponse(**{k: v for k, v in rate_doc.items() if k in ForexRateResponse.model_fields})

    @staticmethod
    async def get_latest() -> dict:
        currencies = ["USD", "EUR", "GBP", "AED", "JPY", "CNY", "SGD"]
        rates = {}
        for curr in currencies:
            rate = await db.forex_rates.find_one({"currency": curr}, {"_id": 0}, sort=[("timestamp", -1)])
            rates[curr] = rate["rate"] if rate else DEFAULT_RATES.get(curr, 1.0)
        return {"rates": rates, "base": "INR", "timestamp": now_iso()}

    @staticmethod
    async def get_history(currency: str, days: int = 30) -> dict:
        rates = await db.forex_rates.find({"currency": currency}, {"_id": 0}).sort("timestamp", -1).limit(days).to_list(days)
        return {"currency": currency, "history": rates}
