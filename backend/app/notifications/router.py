from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from ..core.dependencies import get_current_user
from .service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str
    type: str = "info"

class EmailAlertRequest(BaseModel):
    email: Optional[str] = None  # If not provided, use user's email

@router.post("/send")
async def send_notification(data: NotificationCreate, user: dict = Depends(get_current_user)):
    return await NotificationService.send(data.user_id, data.title, data.message, data.type)

@router.get("/history")
async def get_notifications(user: dict = Depends(get_current_user)):
    return await NotificationService.get_history(user["id"])

@router.post("/email/send-alerts")
async def send_email_alerts(data: EmailAlertRequest = None, user: dict = Depends(get_current_user)):
    """Check and send email alerts for e-BRC deadlines and overdue payments"""
    try:
        from .email_service import NotificationService as EmailService
        email = data.email if data and data.email else user.get("email")
        if not email:
            return {"error": "No email address provided"}
        
        company_id = user.get("company_id", user["id"])
        result = await EmailService.check_and_send_alerts(company_id, email)
        return {
            "success": True,
            "alerts_sent": result,
            "email": email
        }
    except ValueError as e:
        return {"error": str(e), "message": "SendGrid API key not configured"}
    except Exception as e:
        return {"error": str(e)}

@router.get("/email/log")
async def get_email_log(limit: int = 50, user: dict = Depends(get_current_user)):
    """Get email notification history"""
    try:
        from .email_service import NotificationService as EmailService
        company_id = user.get("company_id", user["id"])
        return await EmailService.get_notification_log(company_id, limit)
    except Exception as e:
        return {"error": str(e)}
