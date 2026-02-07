from datetime import datetime, timezone
from ..core.database import db
from ..common.utils import generate_id

class AuditService:
    """Service for logging audit events for compliance and security tracking"""
    
    @staticmethod
    async def log_event(
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: dict = None,
        ip_address: str = None
    ) -> dict:
        """
        Log an audit event to the database.
        
        Args:
            user_id: ID of the user performing the action
            action: Type of action (e.g., 'pii_unmask', 'data_export', 'login')
            resource_type: Type of resource (e.g., 'shipment', 'payment', 'user')
            resource_id: ID of the resource being accessed/modified
            details: Additional context about the event
            ip_address: IP address of the request (optional)
        
        Returns:
            The created audit log entry
        """
        audit_log = {
            "id": generate_id(),
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": ip_address,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.audit_logs.insert_one(audit_log)
        
        # Remove MongoDB _id before returning
        audit_log.pop('_id', None)
        return audit_log
    
    @staticmethod
    async def get_logs(
        user_id: str = None,
        action: str = None,
        resource_type: str = None,
        resource_id: str = None,
        limit: int = 100,
        skip: int = 0
    ) -> list:
        """
        Retrieve audit logs with optional filtering.
        
        Args:
            user_id: Filter by user ID
            action: Filter by action type
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            limit: Maximum number of logs to return
            skip: Number of logs to skip (for pagination)
        
        Returns:
            List of audit log entries
        """
        query = {}
        if user_id:
            query["user_id"] = user_id
        if action:
            query["action"] = action
        if resource_type:
            query["resource_type"] = resource_type
        if resource_id:
            query["resource_id"] = resource_id
        
        logs = await db.audit_logs.find(
            query, 
            {"_id": 0}
        ).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)
        
        return logs
    
    @staticmethod
    async def get_pii_access_logs(user_id: str = None, limit: int = 50) -> list:
        """
        Get PII unmasking access logs for compliance reporting.
        
        Args:
            user_id: Optional filter by user
            limit: Maximum logs to return
        
        Returns:
            List of PII access audit logs
        """
        query = {"action": "pii_unmask"}
        if user_id:
            query["user_id"] = user_id
        
        logs = await db.audit_logs.find(
            query,
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit).to_list(limit)
        
        return logs


# Singleton instance
audit_service = AuditService()
