from fastapi import APIRouter, Depends, Query
from typing import Optional
from ..core.dependencies import get_current_user
from ..common.audit_service import audit_service

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/logs")
async def get_audit_logs(
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    limit: int = Query(default=100, le=500),
    skip: int = 0,
    user: dict = Depends(get_current_user)
):
    """Get audit logs with optional filtering"""
    logs = await audit_service.get_logs(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        limit=limit,
        skip=skip
    )
    return {"logs": logs, "count": len(logs)}

@router.get("/pii-access")
async def get_pii_access_logs(
    limit: int = Query(default=50, le=200),
    user: dict = Depends(get_current_user)
):
    """Get PII unmasking audit logs for compliance"""
    logs = await audit_service.get_pii_access_logs(limit=limit)
    return {"logs": logs, "count": len(logs)}
