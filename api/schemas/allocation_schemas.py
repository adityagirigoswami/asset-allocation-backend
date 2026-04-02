# api/schemas/allocation_schemas.py
from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from ._base import BaseSchema

class AllocationCreate(BaseSchema):
    asset_id: UUID
    employee_id: UUID
    allocation_date: date
    notes: Optional[str] = None

class AllocationOut(BaseSchema):
    id: UUID
    asset_id: UUID
    employee_id: UUID
    allocated_by: UUID
    allocation_date: date
    returned_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    # NEW FIELDS
    asset_name: Optional[str] = None
    employee_name: Optional[str] = None
    allocated_by_name: Optional[str] = None

    class Config:
        from_attributes = True

