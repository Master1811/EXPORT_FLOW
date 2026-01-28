from fastapi import APIRouter, Depends, HTTPException
from ..core.database import db
from ..core.dependencies import get_current_user
from ..common.utils import now_iso
from .models import JobStatusResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str, user: dict = Depends(get_current_user)):
    job = await db.jobs.find_one({"id": job_id}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatusResponse(
        job_id=job_id,
        status=job.get("status", "unknown"),
        progress=job.get("progress", 0),
        result=job.get("result"),
        created_at=job.get("created_at", now_iso())
    )
