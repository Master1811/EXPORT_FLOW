from typing import List, Optional
from ..core.database import db
from ..common.utils import generate_id, now_iso
from .models import ShipmentCreate, ShipmentResponse, ShipmentUpdate
from fastapi import HTTPException

class ShipmentService:
    @staticmethod
    async def create(data: ShipmentCreate, user: dict) -> ShipmentResponse:
        shipment_id = generate_id()
        shipment_doc = {
            "id": shipment_id,
            **data.model_dump(),
            "company_id": user.get("company_id", user["id"]),
            "created_by": user["id"],
            "created_at": now_iso(),
            "updated_at": now_iso()
        }
        await db.shipments.insert_one(shipment_doc)
        return ShipmentResponse(**{k: v for k, v in shipment_doc.items() if k in ShipmentResponse.model_fields})

    @staticmethod
    async def get_all(user: dict, status: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[ShipmentResponse]:
        query = {"company_id": user.get("company_id", user["id"])}
        if status:
            query["status"] = status
        
        shipments = await db.shipments.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
        return [ShipmentResponse(**{k: v for k, v in s.items() if k in ShipmentResponse.model_fields}) for s in shipments]

    @staticmethod
    async def get(shipment_id: str) -> ShipmentResponse:
        shipment = await db.shipments.find_one({"id": shipment_id}, {"_id": 0})
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")
        return ShipmentResponse(**{k: v for k, v in shipment.items() if k in ShipmentResponse.model_fields})

    @staticmethod
    async def update(shipment_id: str, data: ShipmentUpdate) -> ShipmentResponse:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        update_data["updated_at"] = now_iso()
        await db.shipments.update_one({"id": shipment_id}, {"$set": update_data})
        shipment = await db.shipments.find_one({"id": shipment_id}, {"_id": 0})
        return ShipmentResponse(**{k: v for k, v in shipment.items() if k in ShipmentResponse.model_fields})

    @staticmethod
    async def delete(shipment_id: str) -> dict:
        result = await db.shipments.delete_one({"id": shipment_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Shipment not found")
        return {"message": "Shipment deleted"}
