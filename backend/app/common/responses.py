from pydantic import BaseModel
from typing import Any, Optional

class APIResponse(BaseModel):
    success: bool = True
    message: str = ""
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
