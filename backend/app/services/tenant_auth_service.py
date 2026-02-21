"""
Tenant Authorization Service
Strict multi-tenant data isolation with comprehensive access control.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException
import logging

from ..core.database import db
from ..common.utils import generate_id, now_iso

logger = logging.getLogger(__name__)


class TenantAuthorizationError(HTTPException):
    """Custom exception for tenant authorization failures"""
    def __init__(self, detail: str, resource_type: str = None, resource_id: str = None):
        super().__init__(status_code=403, detail=detail)
        self.resource_type = resource_type
        self.resource_id = resource_id


class TenantAuthService:
    """
    Enforces strict tenant ownership across all resources.
    Every data access must pass through this service for IDOR protection.
    """
    
    # Resource to collection mapping with ownership field
    RESOURCE_CONFIG = {
        "shipment": {"collection": "shipments", "owner_field": "company_id"},
        "document": {"collection": "documents", "owner_field": "company_id"},
        "payment": {"collection": "payments", "owner_field": "company_id"},
        "buyer": {"collection": "buyers", "owner_field": "company_id"},
        "company": {"collection": "companies", "owner_field": "id"},
        "connector": {"collection": "connectors", "owner_field": "company_id"},
        "gst_credit": {"collection": "gst_credits", "owner_field": "company_id"},
        "incentive": {"collection": "incentives", "owner_field": "company_id"},
        "audit_package": {"collection": "audit_packages", "owner_field": "company_id"},
        "generated_document": {"collection": "generated_documents", "owner_field": "company_id"},
        "score": {"collection": "credit_scores", "owner_field": "company_id"},
        "audit_log": {"collection": "audit_logs", "owner_field": "company_id"},
        "job": {"collection": "jobs", "owner_field": "company_id"},
        "notification": {"collection": "notifications", "owner_field": "company_id"},
        "uploaded_file": {"collection": "uploaded_files", "owner_field": "company_id"},
    }
    
    @staticmethod
    def get_company_id(user: dict) -> str:
        """Extract company_id from user context"""
        return user.get("company_id") or user.get("id")
    
    @staticmethod
    async def verify_ownership(
        resource_type: str,
        resource_id: str,
        user: dict,
        raise_on_fail: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Verify that a resource belongs to the user's company.
        
        Args:
            resource_type: Type of resource (shipment, document, etc.)
            resource_id: Unique identifier of the resource
            user: Authenticated user context
            raise_on_fail: Whether to raise exception on failure
            
        Returns:
            Resource document if authorized, None otherwise
            
        Raises:
            TenantAuthorizationError: If access denied and raise_on_fail=True
        """
        if resource_type not in TenantAuthService.RESOURCE_CONFIG:
            if raise_on_fail:
                raise TenantAuthorizationError(
                    detail=f"Unknown resource type: {resource_type}",
                    resource_type=resource_type
                )
            return None
        
        config = TenantAuthService.RESOURCE_CONFIG[resource_type]
        collection = db[config["collection"]]
        owner_field = config["owner_field"]
        company_id = TenantAuthService.get_company_id(user)
        
        # Build query with ownership check
        query = {"id": resource_id}
        if owner_field == "id":
            # For companies, the id IS the ownership
            query["id"] = company_id
        else:
            query[owner_field] = company_id
        
        resource = await collection.find_one(query, {"_id": 0})
        
        if not resource:
            # Log potential unauthorized access attempt
            await TenantAuthService._log_access_attempt(
                resource_type, resource_id, company_id, success=False
            )
            
            if raise_on_fail:
                raise TenantAuthorizationError(
                    detail="Resource not found or access denied",
                    resource_type=resource_type,
                    resource_id=resource_id
                )
            return None
        
        # Log successful access
        await TenantAuthService._log_access_attempt(
            resource_type, resource_id, company_id, success=True
        )
        
        return resource
    
    @staticmethod
    async def verify_batch_ownership(
        resource_type: str,
        resource_ids: List[str],
        user: dict
    ) -> List[Dict[str, Any]]:
        """
        Verify ownership of multiple resources.
        Only returns resources that belong to the user's company.
        """
        if resource_type not in TenantAuthService.RESOURCE_CONFIG:
            raise TenantAuthorizationError(
                detail=f"Unknown resource type: {resource_type}",
                resource_type=resource_type
            )
        
        config = TenantAuthService.RESOURCE_CONFIG[resource_type]
        collection = db[config["collection"]]
        owner_field = config["owner_field"]
        company_id = TenantAuthService.get_company_id(user)
        
        query = {
            "id": {"$in": resource_ids},
            owner_field: company_id
        }
        
        resources = await collection.find(query, {"_id": 0}).to_list(len(resource_ids))
        
        # Log if any resources were filtered out
        if len(resources) < len(resource_ids):
            found_ids = {r["id"] for r in resources}
            missing_ids = set(resource_ids) - found_ids
            for missing_id in missing_ids:
                await TenantAuthService._log_access_attempt(
                    resource_type, missing_id, company_id, success=False
                )
        
        return resources
    
    @staticmethod
    async def filter_by_company(
        collection_name: str,
        user: dict,
        additional_filters: Optional[Dict] = None,
        projection: Optional[Dict] = None,
        limit: int = 1000,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query a collection with automatic company_id filtering.
        This is the preferred method for listing resources.
        """
        company_id = TenantAuthService.get_company_id(user)
        
        query = {"company_id": company_id}
        if additional_filters:
            query.update(additional_filters)
        
        # Ensure _id is excluded
        if projection is None:
            projection = {"_id": 0}
        else:
            projection["_id"] = 0
        
        cursor = db[collection_name].find(query, projection)
        
        if sort:
            cursor = cursor.sort(sort)
        
        return await cursor.limit(limit).to_list(limit)
    
    @staticmethod
    async def create_with_ownership(
        collection_name: str,
        data: Dict[str, Any],
        user: dict
    ) -> Dict[str, Any]:
        """
        Create a document with automatic company_id assignment.
        """
        company_id = TenantAuthService.get_company_id(user)
        
        # Ensure company_id is set
        data["company_id"] = company_id
        data["created_by"] = user.get("id")
        data["created_at"] = now_iso()
        
        # Generate ID if not present
        if "id" not in data:
            data["id"] = generate_id()
        
        await db[collection_name].insert_one(data)
        
        # Remove MongoDB _id before returning
        data.pop("_id", None)
        return data
    
    @staticmethod
    async def update_with_ownership(
        resource_type: str,
        resource_id: str,
        update_data: Dict[str, Any],
        user: dict
    ) -> Optional[Dict[str, Any]]:
        """
        Update a resource after verifying ownership.
        """
        # Verify ownership first
        resource = await TenantAuthService.verify_ownership(
            resource_type, resource_id, user, raise_on_fail=True
        )
        
        config = TenantAuthService.RESOURCE_CONFIG[resource_type]
        collection = db[config["collection"]]
        
        # Add update metadata
        update_data["updated_at"] = now_iso()
        update_data["updated_by"] = user.get("id")
        
        await collection.update_one(
            {"id": resource_id},
            {"$set": update_data}
        )
        
        return await collection.find_one({"id": resource_id}, {"_id": 0})
    
    @staticmethod
    async def delete_with_ownership(
        resource_type: str,
        resource_id: str,
        user: dict
    ) -> bool:
        """
        Delete a resource after verifying ownership.
        """
        # Verify ownership first
        await TenantAuthService.verify_ownership(
            resource_type, resource_id, user, raise_on_fail=True
        )
        
        config = TenantAuthService.RESOURCE_CONFIG[resource_type]
        collection = db[config["collection"]]
        
        result = await collection.delete_one({"id": resource_id})
        return result.deleted_count > 0
    
    @staticmethod
    async def _log_access_attempt(
        resource_type: str,
        resource_id: str,
        company_id: str,
        success: bool
    ):
        """Log access attempts for security auditing"""
        try:
            await db.security_access_logs.insert_one({
                "id": generate_id(),
                "resource_type": resource_type,
                "resource_id": resource_id,
                "company_id": company_id,
                "access_granted": success,
                "timestamp": now_iso()
            })
        except Exception as e:
            logger.error(f"Failed to log access attempt: {e}")
