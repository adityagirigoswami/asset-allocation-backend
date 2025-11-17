# api/schemas/_base.py
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Any

class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={UUID: lambda v: str(v)}  # convert UUID -> str
    )
