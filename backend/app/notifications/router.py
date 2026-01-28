from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from ..core.dependencies import get_current_user
from .service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str
    type: str = "info"

@router.post("/send")
async def send_notification(data: NotificationCreate, user: dict = Depends(get_current_user)):
    return await NotificationService.send(data.user_id, data.title, data.message, data.type)

@router.get("/history")
async def get_notifications(user: dict = Depends(get_current_user)):
    return await NotificationService.get_history(user["id"])
