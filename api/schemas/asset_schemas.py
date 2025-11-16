# api/schemas/asset_schemas.py
from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Any, Optional
from api.utils.enums import AssetStatus

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