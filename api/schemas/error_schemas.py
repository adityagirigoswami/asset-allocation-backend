"""Common error response schemas"""
from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    """Standard error response format"""
    status_code: int
    error: str
    success: bool = False


class SuccessResponse(BaseModel):
    """Standard success response format"""
    status_code: int
    message: str
    success: bool = True
    data: Optional[dict] = None

