# api/schemas/asset_schemas.py
from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Any, Optional
from api.utils.enums import AssetStatus
from uuid import UUID
from ._base import BaseSchema


# ---------- Categories ----------
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None

class CategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ---------- Assets ----------
class AssetCreate(BaseModel):
    category_id: int
    name: str
    tag_code: Optional[str] = None
    serial_number: Optional[str] = None
    status: AssetStatus = AssetStatus.available
    purchase_date: Optional[date] = None
    purchase_cost: Optional[float] = None
    warranty_expiry: Optional[date] = None
    specs: Optional[dict[str, Any]] = None

class AssetUpdate(BaseSchema):
    category_id: Optional[int] = None
    name: Optional[str] = None
    tag_code: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_cost: Optional[float] = None
    warranty_expiry: Optional[date] = None
    specs: Optional[dict[str, Any]] = None

class AssetOut(BaseModel):
    id: UUID
    category_id: Optional[int] = None
    name: str
    tag_code: Optional[str] = None
    serial_number: Optional[str] = None
    status: AssetStatus
    purchase_date: Optional[date] = None
    purchase_cost: Optional[float] = None
    warranty_expiry: Optional[date] = None
    specs: Optional[dict] = None
    created_at: Optional[datetime] = None


class AssetStatusUpdate(BaseModel):
    status: AssetStatus
    event_metadata: Optional[dict] = None

# ---------- History ----------
class AssetHistoryOut(BaseSchema):
    id: int
    asset_id: UUID
    user_id: Optional[UUID] = None
    from_status: Optional[AssetStatus] = None
    to_status: AssetStatus
    event_metadata: Optional[dict] = None
    occurred_at: Optional[datetime] = None

