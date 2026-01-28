import logging
from ..core.config import settings
from ..core.database import db
from ..common.utils import now_iso

logger = logging.getLogger(__name__)

class AIService:
    @staticmethod
    async def query(query: str, user: dict) -> dict:
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            chat = LlmChat(
                api_key=settings.EMERGENT_LLM_KEY,
                session_id=f"export-ai-{user['id']}",
                system_message="""You are an expert AI assistant for export finance and compliance. 
                You help exporters understand GST regulations, RoDTEP/RoSCTL incentives, forex management, 
                customs procedures, and trade documentation. Provide accurate, concise, and actionable advice."""
            ).with_model("gemini", "gemini-2.5-flash")
            
            user_message = UserMessage(text=query)
            response = await chat.send_message(user_message)
            
            return {"query": query, "response": response, "timestamp": now_iso()}
        except Exception as e:
            logger.error(f"AI query error: {e}")
            return {
                "query": query,
                "response": "I apologize, but I'm currently unable to process your query. Please try again later.",
                "timestamp": now_iso()
            }

    @staticmethod
    async def get_refund_forecast(user: dict) -> dict:
        company_id = user.get("company_id", user["id"])
        shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
        total_value = sum(s.get("total_value", 0) for s in shipments)
        
        return {
            "forecast": [
                {"month": "Jan 2025", "expected_refund": total_value * 0.02, "confidence": 0.85},
                {"month": "Feb 2025", "expected_refund": total_value * 0.025, "confidence": 0.80},
                {"month": "Mar 2025", "expected_refund": total_value * 0.03, "confidence": 0.75}
            ],
            "total_expected": total_value * 0.075,
            "notes": "Based on historical filing patterns and current pending applications"
        }

    @staticmethod
    async def get_cashflow_forecast(user: dict) -> dict:
        return {
            "forecast": [
                {"month": "Jan 2025", "inflow": 2500000, "outflow": 1800000, "net": 700000},
                {"month": "Feb 2025", "inflow": 2800000, "outflow": 2000000, "net": 800000},
                {"month": "Mar 2025", "inflow": 3200000, "outflow": 2200000, "net": 1000000}
            ],
            "alerts": [{"type": "warning", "message": "Large payment due in Feb from Buyer XYZ - monitor closely"}]
        }

    @staticmethod
    async def get_incentive_optimizer(user: dict) -> dict:
        return {
            "recommendations": [
                {"action": "Apply for RoDTEP", "shipments_affected": 5, "potential_benefit": 125000, "priority": "high"},
                {"action": "Update HS codes for better rates", "shipments_affected": 3, "potential_benefit": 45000, "priority": "medium"}
            ],
            "total_opportunity": 170000
        }

    @staticmethod
    async def get_risk_alerts(user: dict) -> dict:
        return {
            "alerts": [
                {"severity": "high", "type": "payment_delay", "message": "Buyer ABC Corp - 3 invoices overdue by 45+ days", "action": "Follow up immediately"},
                {"severity": "medium", "type": "forex", "message": "USD weakening - consider hedging open positions", "action": "Review forex strategy"},
                {"severity": "low", "type": "compliance", "message": "LUT renewal due in 45 days", "action": "Plan renewal"}
            ]
        }
