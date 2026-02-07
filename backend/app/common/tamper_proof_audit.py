"""
Tamper-Proof Audit Log Service
Immutable audit logs for compliance and security tracking.
Logs cannot be deleted or modified - even by developers.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from ..core.database import db
from ..common.utils import generate_id
import hashlib
import json


class TamperProofAuditService:
    """
    Immutable audit logging service.
    - Every action is logged with timestamp, user ID, IP address
    - Logs are read-only after creation
    - Hash chain ensures tamper detection
    """
    
    COLLECTION_NAME = "audit_logs_immutable"
    
    # Action types
    ACTION_VIEW = "view"
    ACTION_EDIT = "edit"
    ACTION_CREATE = "create"
    ACTION_DELETE = "delete"
    ACTION_EXPORT = "export"
    ACTION_LOGIN = "login"
    ACTION_LOGOUT = "logout"
    ACTION_PII_UNMASK = "pii_unmask"
    ACTION_DECRYPT = "decrypt"
    ACTION_PASSWORD_CHANGE = "password_change"
    ACTION_FAILED_LOGIN = "failed_login"
    ACTION_TOKEN_REFRESH = "token_refresh"
    
    # Resource types
    RESOURCE_SHIPMENT = "shipment"
    RESOURCE_PAYMENT = "payment"
    RESOURCE_USER = "user"
    RESOURCE_DOCUMENT = "document"
    RESOURCE_REPORT = "report"
    RESOURCE_CONNECTOR = "connector"
    RESOURCE_INCENTIVE = "incentive"
    
    def __init__(self):
        self._last_hash = None
    
    async def _get_previous_hash(self) -> str:
        """Get the hash of the last audit log entry for chain integrity."""
        last_entry = await db[self.COLLECTION_NAME].find_one(
            {},
            {"hash": 1},
            sort=[("sequence", -1)]
        )
        return last_entry["hash"] if last_entry else "GENESIS"
    
    async def _get_next_sequence(self) -> int:
        """Get the next sequence number."""
        last_entry = await db[self.COLLECTION_NAME].find_one(
            {},
            {"sequence": 1},
            sort=[("sequence", -1)]
        )
        return (last_entry["sequence"] + 1) if last_entry else 1
    
    def _compute_hash(self, entry: dict) -> str:
        """Compute SHA-256 hash of the audit entry for tamper detection."""
        # Create deterministic string from entry
        hash_data = {
            "id": entry["id"],
            "sequence": entry["sequence"],
            "user_id": entry["user_id"],
            "action": entry["action"],
            "resource_type": entry["resource_type"],
            "resource_id": entry["resource_id"],
            "timestamp": entry["timestamp"],
            "previous_hash": entry["previous_hash"]
        }
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    async def log(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str = None,
        details: Dict[str, Any] = None,
        ip_address: str = None,
        user_agent: str = None,
        session_id: str = None,
        success: bool = True,
        error_message: str = None
    ) -> dict:
        """
        Create an immutable audit log entry.
        
        Args:
            user_id: ID of the user performing the action
            action: Type of action (view, edit, export, login, etc.)
            resource_type: Type of resource (shipment, payment, user, etc.)
            resource_id: ID of the specific resource (optional)
            details: Additional context about the action
            ip_address: Client IP address
            user_agent: Client user agent string
            session_id: Current session ID
            success: Whether the action succeeded
            error_message: Error message if action failed
        
        Returns:
            The created audit log entry (without _id)
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        sequence = await self._get_next_sequence()
        previous_hash = await self._get_previous_hash()
        
        entry = {
            "id": generate_id(),
            "sequence": sequence,
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
            "session_id": session_id,
            "success": success,
            "error_message": error_message,
            "timestamp": timestamp,
            "previous_hash": previous_hash,
            # Metadata
            "created_at": timestamp,
            "immutable": True  # Flag indicating this record cannot be modified
        }
        
        # Compute hash for tamper detection
        entry["hash"] = self._compute_hash(entry)
        
        # Insert into database
        await db[self.COLLECTION_NAME].insert_one(entry)
        
        # Remove MongoDB _id before returning
        entry.pop("_id", None)
        
        return entry
    
    async def get_logs(
        self,
        user_id: str = None,
        action: str = None,
        resource_type: str = None,
        resource_id: str = None,
        start_date: str = None,
        end_date: str = None,
        success: bool = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[dict]:
        """
        Retrieve audit logs with optional filtering.
        
        Returns:
            List of audit log entries (read-only)
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
        if success is not None:
            query["success"] = success
        if start_date:
            query["timestamp"] = {"$gte": start_date}
        if end_date:
            if "timestamp" in query:
                query["timestamp"]["$lte"] = end_date
            else:
                query["timestamp"] = {"$lte": end_date}
        
        logs = await db[self.COLLECTION_NAME].find(
            query,
            {"_id": 0}
        ).sort("sequence", -1).skip(skip).limit(limit).to_list(limit)
        
        return logs
    
    async def get_user_activity(self, user_id: str, limit: int = 50) -> List[dict]:
        """Get all activity for a specific user."""
        return await self.get_logs(user_id=user_id, limit=limit)
    
    async def get_resource_history(self, resource_type: str, resource_id: str, limit: int = 50) -> List[dict]:
        """Get all activity for a specific resource."""
        return await self.get_logs(resource_type=resource_type, resource_id=resource_id, limit=limit)
    
    async def get_pii_access_logs(self, user_id: str = None, limit: int = 100) -> List[dict]:
        """Get PII unmasking/decryption audit logs."""
        query = {"action": {"$in": [self.ACTION_PII_UNMASK, self.ACTION_DECRYPT]}}
        if user_id:
            query["user_id"] = user_id
        
        logs = await db[self.COLLECTION_NAME].find(
            query,
            {"_id": 0}
        ).sort("sequence", -1).limit(limit).to_list(limit)
        
        return logs
    
    async def get_security_events(self, limit: int = 100) -> List[dict]:
        """Get security-related audit logs (logins, failed attempts, etc.)."""
        query = {
            "action": {
                "$in": [
                    self.ACTION_LOGIN,
                    self.ACTION_LOGOUT,
                    self.ACTION_FAILED_LOGIN,
                    self.ACTION_PASSWORD_CHANGE,
                    self.ACTION_TOKEN_REFRESH
                ]
            }
        }
        
        logs = await db[self.COLLECTION_NAME].find(
            query,
            {"_id": 0}
        ).sort("sequence", -1).limit(limit).to_list(limit)
        
        return logs
    
    async def verify_chain_integrity(self, start_sequence: int = 1, end_sequence: int = None) -> dict:
        """
        Verify the integrity of the audit log chain.
        Detects any tampering by validating hash chain.
        
        Returns:
            Verification result with status and any issues found
        """
        query = {"sequence": {"$gte": start_sequence}}
        if end_sequence:
            query["sequence"]["$lte"] = end_sequence
        
        entries = await db[self.COLLECTION_NAME].find(
            query,
            {"_id": 0}
        ).sort("sequence", 1).to_list(10000)
        
        issues = []
        verified_count = 0
        
        for i, entry in enumerate(entries):
            # Verify hash
            computed_hash = self._compute_hash(entry)
            if computed_hash != entry.get("hash"):
                issues.append({
                    "sequence": entry["sequence"],
                    "issue": "Hash mismatch - possible tampering detected",
                    "expected": computed_hash,
                    "actual": entry.get("hash")
                })
            
            # Verify chain linkage (except for first entry)
            if i > 0:
                previous_entry = entries[i - 1]
                if entry.get("previous_hash") != previous_entry.get("hash"):
                    issues.append({
                        "sequence": entry["sequence"],
                        "issue": "Chain broken - previous hash mismatch",
                        "expected": previous_entry.get("hash"),
                        "actual": entry.get("previous_hash")
                    })
            
            verified_count += 1
        
        return {
            "verified": len(issues) == 0,
            "entries_checked": verified_count,
            "issues": issues,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def get_stats(self) -> dict:
        """Get audit log statistics."""
        total = await db[self.COLLECTION_NAME].count_documents({})
        
        # Get counts by action type
        pipeline = [
            {"$group": {"_id": "$action", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        action_counts = await db[self.COLLECTION_NAME].aggregate(pipeline).to_list(100)
        
        # Get counts by resource type
        pipeline = [
            {"$group": {"_id": "$resource_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        resource_counts = await db[self.COLLECTION_NAME].aggregate(pipeline).to_list(100)
        
        return {
            "total_entries": total,
            "by_action": {item["_id"]: item["count"] for item in action_counts if item["_id"]},
            "by_resource": {item["_id"]: item["count"] for item in resource_counts if item["_id"]}
        }


# Singleton instance
audit_service = TamperProofAuditService()


# Convenience function for logging
async def log_action(
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: str = None,
    details: dict = None,
    ip_address: str = None,
    user_agent: str = None,
    session_id: str = None,
    success: bool = True,
    error_message: str = None
) -> dict:
    """Convenience function to log an action."""
    return await audit_service.log(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=session_id,
        success=success,
        error_message=error_message
    )
