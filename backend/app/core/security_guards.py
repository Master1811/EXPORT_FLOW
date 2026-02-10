"""
Security Guards - Global IDOR Protection & Resource Validation
Implements company_id ownership verification for all resource access
"""
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, Depends, Request
from functools import wraps
import logging
from .database import db
from .dependencies import get_current_user

logger = logging.getLogger(__name__)


class IDORGuard:
    """
    Global IDOR (Insecure Direct Object Reference) Protection
    Ensures users can only access resources belonging to their company
    """
    
    # Resource to collection mapping
    RESOURCE_COLLECTIONS = {
        "shipment": "shipments",
        "document": "documents", 
        "payment": "payments",
        "incentive": "incentives",
        "connector": "connectors",
        "gst_credit": "gst_credits",
        "compliance": "compliance",
        "uploaded_file": "uploaded_files",
        "ocr_job": "ocr_jobs",
        "notification": "notification_logs",
    }
    
    @staticmethod
    async def verify_ownership(
        resource_type: str,
        resource_id: str,
        user: dict,
        raise_on_not_found: bool = True
    ) -> Optional[dict]:
        """
        Verify that the resource belongs to the user's company
        
        Args:
            resource_type: Type of resource (shipment, document, etc.)
            resource_id: ID of the resource
            user: Current user dict
            raise_on_not_found: If True, raise 404 when not found
            
        Returns:
            Resource document if found and owned, None otherwise
            
        Raises:
            HTTPException 404 if resource not found (when raise_on_not_found=True)
            HTTPException 403 if user doesn't own the resource
        """
        collection_name = IDORGuard.RESOURCE_COLLECTIONS.get(resource_type)
        if not collection_name:
            raise HTTPException(status_code=400, detail=f"Invalid resource type: {resource_type}")
        
        company_id = user.get("company_id", user.get("id"))
        
        # First check if resource exists at all
        resource = await db[collection_name].find_one({"id": resource_id}, {"_id": 0})
        
        if not resource:
            if raise_on_not_found:
                raise HTTPException(status_code=404, detail=f"{resource_type.title()} not found")
            return None
        
        # Verify ownership
        resource_company_id = resource.get("company_id")
        if resource_company_id != company_id:
            logger.warning(
                f"IDOR attempt blocked: User {user.get('id')} from company {company_id} "
                f"tried to access {resource_type} {resource_id} owned by {resource_company_id}"
            )
            raise HTTPException(
                status_code=403, 
                detail="Access denied: You don't have permission to access this resource"
            )
        
        return resource
    
    @staticmethod
    async def verify_bulk_ownership(
        resource_type: str,
        resource_ids: List[str],
        user: dict
    ) -> List[dict]:
        """
        Verify ownership for multiple resources
        
        Returns:
            List of resources that belong to the user's company
        """
        collection_name = IDORGuard.RESOURCE_COLLECTIONS.get(resource_type)
        if not collection_name:
            raise HTTPException(status_code=400, detail=f"Invalid resource type: {resource_type}")
        
        company_id = user.get("company_id", user.get("id"))
        
        # Query only resources belonging to user's company
        resources = await db[collection_name].find({
            "id": {"$in": resource_ids},
            "company_id": company_id
        }, {"_id": 0}).to_list(len(resource_ids))
        
        # Check if any requested IDs are missing (potentially IDOR attempt)
        found_ids = {r["id"] for r in resources}
        missing_ids = set(resource_ids) - found_ids
        
        if missing_ids:
            # Check if missing resources exist but belong to another company
            other_resources = await db[collection_name].find({
                "id": {"$in": list(missing_ids)}
            }, {"_id": 0, "id": 1, "company_id": 1}).to_list(len(missing_ids))
            
            for other in other_resources:
                if other.get("company_id") != company_id:
                    logger.warning(
                        f"IDOR bulk attempt blocked: User {user.get('id')} "
                        f"tried to access {resource_type} {other['id']} owned by another company"
                    )
                    raise HTTPException(
                        status_code=403,
                        detail="Access denied: One or more resources don't belong to your company"
                    )
        
        return resources
    
    @staticmethod
    def build_company_query(user: dict, additional_filters: dict = None) -> dict:
        """
        Build a MongoDB query that automatically includes company_id filter
        
        Args:
            user: Current user dict
            additional_filters: Additional query filters to include
            
        Returns:
            Query dict with company_id and any additional filters
        """
        company_id = user.get("company_id", user.get("id"))
        query = {"company_id": company_id}
        
        if additional_filters:
            query.update(additional_filters)
        
        return query


# Dependency for routes that need IDOR verification
async def verify_shipment_access(
    shipment_id: str,
    user: dict = Depends(get_current_user)
) -> dict:
    """FastAPI dependency to verify shipment access"""
    return await IDORGuard.verify_ownership("shipment", shipment_id, user)


async def verify_document_access(
    document_id: str,
    user: dict = Depends(get_current_user)
) -> dict:
    """FastAPI dependency to verify document access"""
    return await IDORGuard.verify_ownership("document", document_id, user)


async def verify_payment_access(
    payment_id: str,
    user: dict = Depends(get_current_user)
) -> dict:
    """FastAPI dependency to verify payment access"""
    return await IDORGuard.verify_ownership("payment", payment_id, user)


# Generic IDOR verification dependency factory
def verify_resource_access(resource_type: str):
    """Factory for creating IDOR verification dependencies"""
    async def _verify(
        resource_id: str,
        user: dict = Depends(get_current_user)
    ) -> dict:
        return await IDORGuard.verify_ownership(resource_type, resource_id, user)
    return _verify
