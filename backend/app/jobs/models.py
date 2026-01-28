from pydantic import BaseModel
from typing import Optional, Dict, Any

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    result: Optional[Dict[str, Any]]
    created_at: str
