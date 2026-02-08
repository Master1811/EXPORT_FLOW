import logging
import os
from dotenv import load_dotenv
from ..core.config import settings
from ..core.database import db
from ..common.utils import generate_id, now_iso

load_dotenv()
logger = logging.getLogger(__name__)

# Export compliance system prompt
EXPORT_AI_SYSTEM_PROMPT = """You are ExportFlow AI, an expert assistant for Indian exporters specializing in:

1. **Export Incentives**: RoDTEP, RoSCTL, Drawback schemes - eligibility, rates, application process
2. **GST Compliance**: IGST refunds, LUT (Letter of Undertaking), ITC (Input Tax Credit)
3. **Forex Management**: FEMA regulations, forward contracts, payment realization
4. **Trade Documents**: Commercial Invoice, Packing List, Shipping Bill, e-BRC requirements
5. **Customs**: HS code classification, DGFT procedures, ICEGATE portal navigation
6. **Banking**: Bank Realization Certificate, FIRC, export LC documentation

Guidelines:
- Provide accurate, actionable advice based on current Indian export regulations
- When citing rates or deadlines, mention they may change - verify with official sources
- For complex queries, break down into steps
- If uncertain, recommend consulting a customs broker or CA
- Use INR (₹) for amounts unless asked otherwise
- Reference specific forms/portals when applicable (e.g., DGFT, ICEGATE, GST portal)

Context: You're helping exporters manage their business efficiently through the ExportFlow platform."""


class AIService:
    @staticmethod
    async def query(query: str, user: dict, session_id: str = None) -> dict:
        """Process AI query with chat history"""
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            # Use provided session_id or create one
            if not session_id:
                session_id = f"export-ai-{user['id']}"
            
            # Get API key
            api_key = os.environ.get("EMERGENT_LLM_KEY") or settings.EMERGENT_LLM_KEY
            if not api_key:
                raise ValueError("EMERGENT_LLM_KEY not configured")
            
            # Create chat with Gemini
            chat = LlmChat(
                api_key=api_key,
                session_id=session_id,
                system_message=EXPORT_AI_SYSTEM_PROMPT
            ).with_model("gemini", "gemini-3-flash-preview")
            
            # Send message
            user_message = UserMessage(text=query)
            response = await chat.send_message(user_message)
            
            # Store in chat history
            chat_doc = {
                "id": generate_id(),
                "session_id": session_id,
                "user_id": user["id"],
                "company_id": user.get("company_id", user["id"]),
                "query": query,
                "response": response,
                "created_at": now_iso()
            }
            await db.ai_chat_history.insert_one(chat_doc)
            
            return {
                "query": query,
                "response": response,
                "session_id": session_id,
                "timestamp": now_iso()
            }
        except Exception as e:
            logger.error(f"AI query error: {e}")
            return {
                "query": query,
                "response": f"I apologize, but I encountered an error: {str(e)}. Please try again.",
                "timestamp": now_iso(),
                "error": str(e)
            }

    @staticmethod
    async def get_chat_history(user: dict, session_id: str = None, limit: int = 20) -> list:
        """Get chat history for user"""
        query = {"user_id": user["id"]}
        if session_id:
            query["session_id"] = session_id
        
        history = await db.ai_chat_history.find(
            query, {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        return history

    @staticmethod
    async def analyze_shipment(shipment_id: str, user: dict) -> dict:
        """AI analysis of a specific shipment"""
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            # Get shipment data
            shipment = await db.shipments.find_one({
                "id": shipment_id,
                "company_id": user.get("company_id", user["id"])
            }, {"_id": 0})
            
            if not shipment:
                return {"error": "Shipment not found"}
            
            # Get related data
            payments = await db.payments.find({"shipment_id": shipment_id}, {"_id": 0}).to_list(10)
            documents = await db.documents.find({"shipment_id": shipment_id}, {"_id": 0}).to_list(10)
            
            # Build context
            context = f"""
            Analyze this export shipment and provide recommendations:
            
            Shipment: {shipment.get('shipment_number')}
            Buyer: {shipment.get('buyer_name')} ({shipment.get('buyer_country')})
            Value: ₹{shipment.get('total_value', 0):,.2f}
            HS Codes: {', '.join(shipment.get('hs_codes', []))}
            Status: {shipment.get('status')}
            e-BRC Status: {shipment.get('ebrc_status', 'pending')}
            
            Payments Received: {len(payments)} (Total: ₹{sum(p.get('amount', 0) for p in payments):,.2f})
            Documents: {len(documents)}
            
            Provide:
            1. Incentive eligibility check (RoDTEP/RoSCTL/Drawback)
            2. Compliance status and any pending actions
            3. Risk assessment
            4. Recommendations to maximize benefits
            """
            
            api_key = os.environ.get("EMERGENT_LLM_KEY") or settings.EMERGENT_LLM_KEY
            
            chat = LlmChat(
                api_key=api_key,
                session_id=f"shipment-analysis-{shipment_id}",
                system_message="You are an export compliance analyst. Analyze shipments and provide actionable insights."
            ).with_model("gemini", "gemini-3-flash-preview")
            
            user_message = UserMessage(text=context)
            response = await chat.send_message(user_message)
            
            return {
                "shipment_id": shipment_id,
                "shipment_number": shipment.get("shipment_number"),
                "analysis": response,
                "timestamp": now_iso()
            }
        except Exception as e:
            logger.error(f"Shipment analysis error: {e}")
            return {"error": str(e)}

    @staticmethod
    async def get_refund_forecast(user: dict) -> dict:
        company_id = user.get("company_id", user["id"])
        shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
        total_value = sum(s.get("total_value", 0) for s in shipments)
        
        # Calculate based on HS codes and rates
        from ..incentives.hs_database import get_hs_code_info
        
        total_potential = 0
        for s in shipments:
            hs_codes = s.get("hs_codes", [])
            if hs_codes:
                for code in hs_codes:
                    info = get_hs_code_info(code)
                    rate = info.get("rodtep", 0) + info.get("drawback", 0)
                    total_potential += s.get("total_value", 0) * rate / 100 / len(hs_codes)
        
        return {
            "forecast": [
                {"month": "Current", "expected_refund": total_potential * 0.4, "confidence": 0.90},
                {"month": "Next Month", "expected_refund": total_potential * 0.35, "confidence": 0.80},
                {"month": "2 Months", "expected_refund": total_potential * 0.25, "confidence": 0.70}
            ],
            "total_expected": total_potential,
            "notes": "Based on shipment values and applicable RoDTEP/Drawback rates"
        }

    @staticmethod
    async def get_cashflow_forecast(user: dict) -> dict:
        company_id = user.get("company_id", user["id"])
        shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
        
        total_receivables = 0
        for s in shipments:
            payments = await db.payments.find({"shipment_id": s["id"]}, {"_id": 0}).to_list(10)
            paid = sum(p.get("amount", 0) for p in payments)
            total_receivables += s.get("total_value", 0) - paid
        
        return {
            "forecast": [
                {"month": "Current", "inflow": total_receivables * 0.4, "outflow": total_receivables * 0.2, "net": total_receivables * 0.2},
                {"month": "Next Month", "inflow": total_receivables * 0.35, "outflow": total_receivables * 0.2, "net": total_receivables * 0.15},
                {"month": "2 Months", "inflow": total_receivables * 0.25, "outflow": total_receivables * 0.1, "net": total_receivables * 0.15}
            ],
            "total_receivables": total_receivables,
            "alerts": []
        }

    @staticmethod
    async def get_incentive_optimizer(user: dict) -> dict:
        company_id = user.get("company_id", user["id"])
        shipments = await db.shipments.find({
            "company_id": company_id,
            "status": {"$in": ["shipped", "delivered", "completed"]}
        }, {"_id": 0}).to_list(500)
        
        # Check which shipments have unclaimed incentives
        from ..incentives.hs_database import get_hs_code_info
        
        recommendations = []
        total_opportunity = 0
        
        unclaimed_rodtep = []
        for s in shipments:
            hs_codes = s.get("hs_codes", [])
            if hs_codes:
                for code in hs_codes:
                    info = get_hs_code_info(code)
                    if info.get("rodtep", 0) > 0:
                        potential = s.get("total_value", 0) * info["rodtep"] / 100
                        total_opportunity += potential
                        unclaimed_rodtep.append(s.get("shipment_number"))
        
        if unclaimed_rodtep:
            recommendations.append({
                "action": "Claim RoDTEP benefits",
                "shipments_affected": len(set(unclaimed_rodtep)),
                "potential_benefit": total_opportunity,
                "priority": "high"
            })
        
        return {
            "recommendations": recommendations,
            "total_opportunity": total_opportunity
        }

    @staticmethod
    async def get_risk_alerts(user: dict) -> dict:
        company_id = user.get("company_id", user["id"])
        alerts = []
        
        # Check overdue payments
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        shipments = await db.shipments.find({"company_id": company_id}, {"_id": 0}).to_list(500)
        
        for s in shipments:
            payments = await db.payments.find({"shipment_id": s["id"]}, {"_id": 0}).to_list(10)
            paid = sum(p.get("amount", 0) for p in payments)
            outstanding = s.get("total_value", 0) - paid
            
            if outstanding > 0:
                try:
                    created_str = s.get("created_at", "")
                    if created_str:
                        # Handle both timezone-aware and naive datetime strings
                        if "+" not in created_str and "Z" not in created_str:
                            created_str += "+00:00"
                        created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                        days = (now - created).days
                        
                        if days > 60:
                            alerts.append({
                                "severity": "high",
                                "type": "payment_delay",
                                "message": f"{s.get('buyer_name')} - ₹{outstanding:,.0f} overdue by {days} days",
                                "action": "Follow up immediately",
                                "shipment_id": s["id"]
                            })
                except Exception:
                    pass
        
        # Check e-BRC deadlines
        for s in shipments:
            if s.get("ebrc_status") == "pending" and s.get("ebrc_due_date"):
                try:
                    due_str = s.get("ebrc_due_date", "")
                    if due_str:
                        if "+" not in due_str and "Z" not in due_str:
                            due_str += "+00:00"
                        due = datetime.fromisoformat(due_str.replace("Z", "+00:00"))
                        days_remaining = (due - now).days
                        
                        if days_remaining < 0:
                            alerts.append({
                                "severity": "high",
                                "type": "compliance",
                                "message": f"e-BRC OVERDUE for {s.get('shipment_number')} - {abs(days_remaining)} days past deadline",
                                "action": "File immediately",
                                "shipment_id": s["id"]
                            })
                        elif days_remaining <= 15:
                            alerts.append({
                                "severity": "medium",
                                "type": "compliance",
                                "message": f"e-BRC due in {days_remaining} days for {s.get('shipment_number')}",
                                "action": "Prepare filing",
                                "shipment_id": s["id"]
                            })
                except Exception:
                    pass
        
        return {"alerts": alerts}
