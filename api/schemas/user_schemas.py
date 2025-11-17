from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional
from ._base import BaseSchema


class EmployeeCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    employee_code: str | None = None
    phone: str | None = None
    
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponse(BaseSchema):
    id: UUID
    email: EmailStr
    full_name: str
    role_id: int
    employee_code: str | None
    phone: str | None


class UserUpdate(BaseModel):
    full_name: Optional[str]
    password: Optional[str]
    employee_code: Optional[str]
    phone: Optional[str]