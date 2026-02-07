from pydantic import BaseModel
from typing import Optional, List

class ExportRequest(BaseModel):
    export_type: str  # shipments, payments, receivables, incentives
    format: str  # csv, xlsx, pdf
    filters: Optional[dict] = None

class ExportJobResponse(BaseModel):
    job_id: str
    status: str
    progress: int = 0
    total_rows: int = 0
    file_name: Optional[str] = None
    download_url: Optional[str] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

class ExportJobListResponse(BaseModel):
    jobs: List[ExportJobResponse]
