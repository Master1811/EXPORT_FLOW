from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import List
import os
from ..core.dependencies import get_current_user
from .models import ExportRequest
from .service import ExportService

router = APIRouter(prefix="/exports", tags=["Exports"])

@router.post("")
async def create_export(data: ExportRequest, user: dict = Depends(get_current_user)):
    """
    Create an async export job.
    
    Supported export types: shipments, payments, receivables, incentives
    Supported formats: csv, xlsx, pdf
    
    Returns a job_id to track progress.
    """
    if data.export_type not in ["shipments", "payments", "receivables", "incentives"]:
        raise HTTPException(status_code=400, detail="Invalid export type")
    
    if data.format not in ["csv", "xlsx", "pdf"]:
        raise HTTPException(status_code=400, detail="Invalid format. Use csv, xlsx, or pdf")
    
    return await ExportService.create_export_job(
        data.export_type,
        data.format,
        user,
        data.filters
    )

@router.get("/jobs")
async def list_export_jobs(limit: int = 10, user: dict = Depends(get_current_user)):
    """List recent export jobs"""
    return await ExportService.list_jobs(user, limit)

@router.get("/jobs/{job_id}")
async def get_export_job_status(job_id: str, user: dict = Depends(get_current_user)):
    """Get export job status"""
    return await ExportService.get_job_status(job_id, user)

@router.get("/download/{job_id}")
async def download_export(job_id: str, user: dict = Depends(get_current_user)):
    """Download completed export file"""
    file_path, file_name = await ExportService.get_file_path(job_id, user)
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found or export not complete")
    
    # Determine media type
    media_types = {
        "csv": "text/csv",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pdf": "application/pdf"
    }
    ext = file_name.split(".")[-1]
    media_type = media_types.get(ext, "application/octet-stream")
    
    return FileResponse(
        file_path,
        media_type=media_type,
        filename=file_name,
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )
