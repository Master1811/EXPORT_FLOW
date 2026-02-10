from typing import List, Optional
from datetime import datetime, timezone, timedelta
from ..core.database import db
from ..common.utils import generate_id, now_iso
from ..common.encryption_service import encrypt_field, decrypt_field, mask_field, SENSITIVE_FIELDS
from ..common.tamper_proof_audit import audit_service, TamperProofAuditService
from .models import ShipmentCreate, ShipmentResponse, ShipmentUpdate, EBRCUpdateRequest
from fastapi import HTTPException

# e-BRC deadline is 60 days from shipment date
EBRC_DEADLINE_DAYS = 60

# Fields to encrypt in shipments
SHIPMENT_ENCRYPTED_FIELDS = [
    "buyer_name", "buyer_phone", "buyer_pan", 
    "buyer_bank_account", "buyer_email", "total_value"
]

def mask_pii(value: str, visible_chars: int = 4) -> str:
    """Mask sensitive data showing only last few characters"""
    if not value or len(value) <= visible_chars:
        return value
    return '*' * (len(value) - visible_chars) + value[-visible_chars:]

def calculate_ebrc_due_date(ship_date: str) -> str:
    """Calculate e-BRC due date (60 days from shipment)"""
    try:
        if ship_date:
            ship_dt = datetime.fromisoformat(ship_date.replace("Z", "+00:00"))
            due_date = ship_dt + timedelta(days=EBRC_DEADLINE_DAYS)
            return due_date.isoformat()
    except:
        pass
    return None

def calculate_ebrc_days_remaining(due_date: str) -> int:
    """Calculate days remaining until e-BRC deadline"""
    if not due_date:
        return None
    try:
        due_dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        return (due_dt - now).days
    except:
        return None

class ShipmentService:
    @staticmethod
    async def create(data: ShipmentCreate, user: dict) -> ShipmentResponse:
        shipment_id = generate_id()
        shipment_dict = data.model_dump()
        
        # Calculate e-BRC due date if actual_ship_date provided
        ship_date = shipment_dict.get("actual_ship_date") or shipment_dict.get("expected_ship_date")
        if ship_date:
            shipment_dict["ebrc_due_date"] = calculate_ebrc_due_date(ship_date)
        
        shipment_doc = {
            "id": shipment_id,
            **shipment_dict,
            "company_id": user.get("company_id", user["id"]),
            "created_by": user["id"],
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "version": 1  # Initialize version for optimistic locking
        }
        await db.shipments.insert_one(shipment_doc)
        return ShipmentService._to_response(shipment_doc)

    @staticmethod
    async def get_all(user: dict, status: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[ShipmentResponse]:
        query = {"company_id": user.get("company_id", user["id"])}
        if status:
            query["status"] = status
        
        shipments = await db.shipments.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
        return [ShipmentService._to_response(s) for s in shipments]

    @staticmethod
    async def get_paginated(
        user: dict,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> dict:
        """
        Get paginated shipments with server-side search and sorting.
        Optimized for large datasets using indexed queries.
        """
        company_id = user.get("company_id", user["id"])
        
        # Build query with indexed fields
        query = {"company_id": company_id}
        
        if status:
            query["status"] = status
        
        # Server-side search on indexed fields
        if search:
            query["$or"] = [
                {"shipment_number": {"$regex": search, "$options": "i"}},
                {"buyer_name": {"$regex": search, "$options": "i"}},
                {"buyer_country": {"$regex": search, "$options": "i"}},
            ]
        
        # Calculate skip
        skip = (page - 1) * page_size
        
        # Sort direction
        sort_direction = -1 if sort_order == "desc" else 1
        
        # Execute queries in parallel for performance
        import asyncio
        
        # Get total count and data in parallel
        count_task = db.shipments.count_documents(query)
        data_task = db.shipments.find(query, {"_id": 0}).sort(
            sort_by, sort_direction
        ).skip(skip).limit(page_size).to_list(page_size)
        
        total_count, shipments = await asyncio.gather(count_task, data_task)
        
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size
        
        return {
            "data": [ShipmentService._to_response(s) for s in shipments],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }

    @staticmethod
    async def get(shipment_id: str, user: dict = None, mask_sensitive: bool = True) -> ShipmentResponse:
        query = {"id": shipment_id}
        # IDOR protection: ensure user can only access their company's data
        if user:
            query["company_id"] = user.get("company_id", user["id"])
        
        shipment = await db.shipments.find_one(query, {"_id": 0})
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")
        return ShipmentService._to_response(shipment, mask_sensitive)

    @staticmethod
    async def update(shipment_id: str, data: ShipmentUpdate, user: dict = None) -> ShipmentResponse:
        # IDOR protection
        query = {"id": shipment_id}
        if user:
            query["company_id"] = user.get("company_id", user["id"])
        
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        
        # Optimistic locking - check version if provided
        provided_version = update_data.pop("version", None)
        
        update_data["updated_at"] = now_iso()
        
        # Recalculate e-BRC due date if ship date changed
        if "actual_ship_date" in update_data:
            update_data["ebrc_due_date"] = calculate_ebrc_due_date(update_data["actual_ship_date"])
        
        # If version provided, use optimistic locking
        if provided_version is not None:
            query["version"] = provided_version
            update_data["version"] = provided_version + 1
            
            result = await db.shipments.update_one(query, {"$set": update_data})
            if result.matched_count == 0:
                # Check if shipment exists at all
                exists = await db.shipments.find_one({"id": shipment_id}, {"_id": 0})
                if exists:
                    raise HTTPException(
                        status_code=409, 
                        detail="Conflict: The shipment has been modified by another user. Please refresh and try again."
                    )
                raise HTTPException(status_code=404, detail="Shipment not found")
        else:
            # No version provided - use regular update with version increment
            result = await db.shipments.update_one(
                query, 
                {"$set": update_data, "$inc": {"version": 1}}
            )
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Shipment not found")
        
        shipment = await db.shipments.find_one({"id": shipment_id}, {"_id": 0})
        return ShipmentService._to_response(shipment)

    @staticmethod
    async def delete(shipment_id: str, user: dict = None) -> dict:
        query = {"id": shipment_id}
        if user:
            query["company_id"] = user.get("company_id", user["id"])
        
        result = await db.shipments.delete_one(query)
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Shipment not found")
        return {"message": "Shipment deleted"}

    @staticmethod
    async def update_ebrc(shipment_id: str, data: EBRCUpdateRequest, user: dict) -> ShipmentResponse:
        """Update e-BRC status for a shipment"""
        # P0 Fix: Enforce rejection_reason when status is 'rejected'
        if data.ebrc_status == "rejected" and not data.rejection_reason:
            raise HTTPException(
                status_code=422, 
                detail="rejection_reason is required when status is 'rejected'"
            )
        
        query = {"id": shipment_id, "company_id": user.get("company_id", user["id"])}
        
        update_data = {
            "ebrc_status": data.ebrc_status,
            "updated_at": now_iso()
        }
        if data.ebrc_filed_date:
            update_data["ebrc_filed_date"] = data.ebrc_filed_date
        if data.ebrc_number:
            update_data["ebrc_number"] = data.ebrc_number
        if data.rejection_reason:
            update_data["ebrc_rejection_reason"] = data.rejection_reason
        
        result = await db.shipments.update_one(query, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Shipment not found")
        
        shipment = await db.shipments.find_one({"id": shipment_id}, {"_id": 0})
        return ShipmentService._to_response(shipment)

    @staticmethod
    async def get_ebrc_dashboard(user: dict) -> dict:
        """Get e-BRC monitoring dashboard data"""
        company_id = user.get("company_id", user["id"])
        shipments = await db.shipments.find(
            {"company_id": company_id, "status": {"$in": ["shipped", "delivered", "completed"]}},
            {"_id": 0}
        ).to_list(500)
        
        now = datetime.now(timezone.utc)
        
        # Categorize by e-BRC status
        pending = []
        filed = []
        approved = []
        rejected = []
        overdue = []
        due_soon = []  # Due within 15 days
        
        for s in shipments:
            ebrc_status = s.get("ebrc_status", "pending")
            due_date_str = s.get("ebrc_due_date")
            days_remaining = calculate_ebrc_days_remaining(due_date_str) if due_date_str else None
            
            shipment_summary = {
                "id": s["id"],
                "shipment_number": s["shipment_number"],
                "buyer_name": s["buyer_name"],
                "total_value": s["total_value"],
                "currency": s["currency"],
                "ebrc_status": ebrc_status,
                "ebrc_due_date": due_date_str,
                "days_remaining": days_remaining,
                "ebrc_number": s.get("ebrc_number")
            }
            
            if ebrc_status == "pending":
                pending.append(shipment_summary)
                if days_remaining is not None:
                    if days_remaining < 0:
                        overdue.append(shipment_summary)
                    elif days_remaining <= 15:
                        due_soon.append(shipment_summary)
            elif ebrc_status == "filed":
                filed.append(shipment_summary)
            elif ebrc_status == "approved":
                approved.append(shipment_summary)
            elif ebrc_status == "rejected":
                rejected.append(shipment_summary)
        
        # Calculate totals
        total_pending_value = sum(s["total_value"] for s in pending)
        total_overdue_value = sum(s["total_value"] for s in overdue)
        total_approved_value = sum(s["total_value"] for s in approved)
        
        return {
            "summary": {
                "total_shipments": len(shipments),
                "pending_count": len(pending),
                "filed_count": len(filed),
                "approved_count": len(approved),
                "rejected_count": len(rejected),
                "overdue_count": len(overdue),
                "due_soon_count": len(due_soon)
            },
            "values": {
                "total_pending": total_pending_value,
                "total_overdue": total_overdue_value,
                "total_approved": total_approved_value
            },
            "alerts": {
                "overdue": overdue,
                "due_soon": due_soon
            },
            "by_status": {
                "pending": pending,
                "filed": filed,
                "approved": approved,
                "rejected": rejected
            }
        }

    @staticmethod
    def _to_response(shipment: dict, mask_sensitive: bool = True) -> ShipmentResponse:
        """Convert shipment dict to response model with PII masking"""
        response_data = {}
        for key in ShipmentResponse.model_fields:
            if key in shipment:
                value = shipment[key]
                # Apply PII masking
                if mask_sensitive and key in ["buyer_pan", "buyer_bank_account", "buyer_phone"]:
                    value = mask_pii(value) if value else None
                response_data[key] = value
            else:
                # Set default values for optional fields
                if key == "version":
                    response_data[key] = shipment.get("version", 1)
                else:
                    response_data[key] = None
        
        # Calculate e-BRC days remaining
        if shipment.get("ebrc_due_date"):
            response_data["ebrc_days_remaining"] = calculate_ebrc_days_remaining(shipment["ebrc_due_date"])
        
        return ShipmentResponse(**response_data)
