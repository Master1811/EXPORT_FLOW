from typing import List
from ..core.database import db
from ..common.utils import generate_id, now_iso

class NotificationService:
    @staticmethod
    async def send(user_id: str, title: str, message: str, type: str = "info") -> dict:
        notif_id = generate_id()
        notif_doc = {
            "id": notif_id,
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": type,
            "read": False,
            "created_at": now_iso()
        }
        await db.notifications.insert_one(notif_doc)
        return {"id": notif_id, "message": "Notification sent"}

    @staticmethod
    async def get_history(user_id: str, limit: int = 50) -> List[dict]:
        notifications = await db.notifications.find(
            {"user_id": user_id}, 
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        return notifications
