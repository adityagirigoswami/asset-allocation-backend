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
    role: str   
    token_type: str = "bearer"

class UserResponse(BaseSchema):
    id: UUID
    email: EmailStr
    full_name: str
    role_id: int
    employee_code: str | None
    phone: str | None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None
    employee_code: Optional[str] = None
    phone: Optional[str] = None