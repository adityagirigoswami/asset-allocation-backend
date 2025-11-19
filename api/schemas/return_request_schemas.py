# api/schemas/return_request_schemas.py
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from ._base import BaseSchema


class ReturnRequestCreate(BaseModel):
    allocation_id: str
    description: Optional[str] = None

class ReturnRequestOut(BaseSchema):
    id: UUID
    allocation_id: UUID
    requested_by: UUID
    description: Optional[str] = None
    approved_at: Optional[datetime] = None
    decision_note: Optional[str] = None
    created_at: Optional[datetime] = None

    # NEW
    asset_name: Optional[str] = None
    employee_name: Optional[str] = None

    class Config:
        from_attributes = True


class ReturnRequestApprove(BaseModel):
    decision_note: Optional[str] = None
