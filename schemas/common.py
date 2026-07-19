from pydantic import BaseModel
from typing import Optional, Any


class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str
    detail: Optional[str] = None
