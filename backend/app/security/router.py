"""
Security & Audit Router
Provides endpoints for audit logs dashboard and security verification.
"""

from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from ..core.dependencies import get_current_user
from ..common.tamper_proof_audit import audit_service, TamperProofAuditService

router = APIRouter(prefix="/security", tags=["Security & Audit"])

def get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None

@router.get("/audit-logs")
async def get_audit_logs(
    request: Request,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    success: Optional[bool] = None,
    limit: int = Query(default=50, le=500),
    skip: int = 0,
    user: dict = Depends(get_current_user)
):
    """
    Get audit logs for the current user's company.
    
    Shows every single access attempt on your data:
    - Timestamp
    - User ID
    - IP Address
    - Action type (view, edit, export, login, etc.)
    - Resource accessed
    
    Logs are IMMUTABLE - cannot be deleted or modified.
    """
    # Log this access itself
    await audit_service.log(
        user_id=user["id"],
        action=TamperProofAuditService.ACTION_VIEW,
        resource_type="audit_logs",
        details={"filters": {"action": action, "resource_type": resource_type}},
        ip_address=get_client_ip(request)
    )
    
    # Get logs for user's activity (or all if admin)
    logs = await audit_service.get_logs(
        user_id=user["id"] if user.get("role") != "admin" else None,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date,
        success=success,
        limit=limit,
        skip=skip
    )
    
    return {
        "logs": logs,
        "count": len(logs),
        "filters": {
            "action": action,
            "resource_type": resource_type,
            "start_date": start_date,
            "end_date": end_date
        }
    }

@router.get("/my-activity")
async def get_my_activity(
    limit: int = Query(default=50, le=200),
    user: dict = Depends(get_current_user)
):
    """
    Get all activity for the current user.
    
    Every view, edit, export action you've performed.
    """
    logs = await audit_service.get_user_activity(user["id"], limit=limit)
    return {"logs": logs, "count": len(logs)}

@router.get("/pii-access-logs")
async def get_pii_access_logs(
    request: Request,
    limit: int = Query(default=100, le=500),
    user: dict = Depends(get_current_user)
):
    """
    Get all PII unmasking/decryption events.
    
    Shows exactly when sensitive data was viewed:
    - Who viewed it (user ID)
    - When (timestamp)
    - What was accessed (resource ID)
    - From where (IP address)
    
    Critical for compliance and security auditing.
    """
    # Only show user's own PII access unless admin
    user_id = None if user.get("role") == "admin" else user["id"]
    logs = await audit_service.get_pii_access_logs(user_id=user_id, limit=limit)
    
    return {
        "logs": logs,
        "count": len(logs),
        "description": "All PII unmasking and decryption events"
    }

@router.get("/security-events")
async def get_security_events(
    limit: int = Query(default=100, le=500),
    user: dict = Depends(get_current_user)
):
    """
    Get security-related events.
    
    - Logins (successful and failed)
    - Logouts
    - Password changes
    - Token refreshes
    
    Helps detect suspicious activity on your account.
    """
    logs = await audit_service.get_security_events(limit=limit)
    
    # Filter to user's own events unless admin
    if user.get("role") != "admin":
        logs = [l for l in logs if l.get("user_id") == user["id"] or l.get("user_id") == user["email"]]
    
    return {
        "logs": logs,
        "count": len(logs)
    }

@router.get("/resource-history/{resource_type}/{resource_id}")
async def get_resource_history(
    resource_type: str,
    resource_id: str,
    request: Request,
    limit: int = Query(default=50, le=200),
    user: dict = Depends(get_current_user)
):
    """
    Get all activity for a specific resource (shipment, payment, etc.).
    
    Shows complete audit trail:
    - Who created it
    - Who viewed it
    - Who edited it
    - When each action occurred
    """
    # Log this view
    await audit_service.log(
        user_id=user["id"],
        action=TamperProofAuditService.ACTION_VIEW,
        resource_type="resource_history",
        resource_id=resource_id,
        details={"viewed_resource_type": resource_type},
        ip_address=get_client_ip(request)
    )
    
    logs = await audit_service.get_resource_history(resource_type, resource_id, limit=limit)
    
    return {
        "resource_type": resource_type,
        "resource_id": resource_id,
        "logs": logs,
        "count": len(logs)
    }

@router.get("/verify-integrity")
async def verify_audit_integrity(
    start_sequence: int = Query(default=1, ge=1),
    end_sequence: Optional[int] = None,
    user: dict = Depends(get_current_user)
):
    """
    Verify integrity of audit log chain.
    
    Uses cryptographic hashes to detect any tampering.
    Each log entry contains hash of previous entry - any modification breaks the chain.
    
    TAMPER-PROOF: Even developers cannot modify logs without detection.
    """
    # Admin only
    if user.get("role") != "admin":
        return {"error": "Admin access required for integrity verification"}
    
    result = await audit_service.verify_chain_integrity(start_sequence, end_sequence)
    
    return {
        "verification": result,
        "message": "Audit log chain is intact" if result["verified"] else "TAMPERING DETECTED - Audit log chain broken"
    }

@router.get("/stats")
async def get_audit_stats(
    user: dict = Depends(get_current_user)
):
    """
    Get audit log statistics.
    
    Overview of all logged actions:
    - Total entries
    - Breakdown by action type
    - Breakdown by resource type
    """
    stats = await audit_service.get_stats()
    return stats

@router.get("/action-types")
async def get_action_types():
    """Get list of all action types for filtering."""
    return {
        "action_types": [
            {"value": "view", "label": "View/Read"},
            {"value": "edit", "label": "Edit/Update"},
            {"value": "create", "label": "Create"},
            {"value": "delete", "label": "Delete"},
            {"value": "export", "label": "Export/Download"},
            {"value": "login", "label": "Login"},
            {"value": "logout", "label": "Logout"},
            {"value": "pii_unmask", "label": "PII Unmask"},
            {"value": "decrypt", "label": "Decrypt"},
            {"value": "password_change", "label": "Password Change"},
            {"value": "failed_login", "label": "Failed Login"},
            {"value": "token_refresh", "label": "Token Refresh"}
        ],
        "resource_types": [
            {"value": "shipment", "label": "Shipment"},
            {"value": "payment", "label": "Payment"},
            {"value": "user", "label": "User"},
            {"value": "document", "label": "Document"},
            {"value": "report", "label": "Report"},
            {"value": "connector", "label": "Connector"},
            {"value": "incentive", "label": "Incentive"}
        ]
    }
