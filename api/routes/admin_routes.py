from fastapi import APIRouter, Depends, HTTPException, status, Query , Body
from uuid import UUID
from sqlalchemy.orm import Session
from typing import List, Optional
from db.auth import get_db
from api.models.users import User
from api.schemas.user_schemas import UserResponse, UserUpdate, EmployeeCreate
from core.security import require_admin, get_current_user
from api.utils.hashing import hash_password, verify_password
from api.models.user_roles import UserRole


router = APIRouter(prefix="/admin/employees", tags=["Admin"])
employees_router = APIRouter(prefix="/employees/me", tags=["employees"])



# ADMIN-ONLY: create employee
@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_employee(payload: EmployeeCreate,
                    db: Session = Depends(get_db),
                    admin = Depends(require_admin)):
    employee_role = db.query(UserRole).filter(UserRole.name == "employee").first()
    if not employee_role:
        raise HTTPException(status_code=500, detail="Employee role missing. Run seeding.")

    # Check for case-insensitive employee_code uniqueness
    if payload.employee_code:
        existing = db.query(User).filter(
            User.employee_code.ilike(payload.employee_code),
            User.deleted_at.is_(None)
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Employee code '{payload.employee_code}' already exists (case-insensitive)"
            )

    new_user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role_id=employee_role.id,
        employee_code=payload.employee_code,
        phone=payload.phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# List users (admin-only) with pagination + search
@router.get("", response_model=List[UserResponse], dependencies=[Depends(require_admin)])
def list_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = Query(25, le=200),
    q: Optional[str] = Query(None, description="search email or name")
):
    query = db.query(User).filter(User.deleted_at == None)
    if q:
        q_like = f"%{q}%"
        query = query.filter((User.email.ilike(q_like)) | (User.full_name.ilike(q_like)))
    users = query.offset(skip).limit(limit).all()
    return users

# Get single user (admin-only)
@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)])
def get_user(user_id: str, db: Session = Depends(get_db)):
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user = db.query(User).filter(User.id == user_id, User.deleted_at == None).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Update user (admin-only)
@router.put("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)])
def update_user(user_id: str, payload: Optional[UserUpdate] = Body(None), db: Session = Depends(get_db)):

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail="Invalid payload: Request body must contain the update object."
        )
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    
    user = db.query(User).filter(User.id == user_id, User.deleted_at == None).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.full_name is not None:
            user.full_name = payload.full_name
    if payload.employee_code is not None:
            # Check for case-insensitive employee_code uniqueness (excluding current user)
            existing = db.query(User).filter(
                User.employee_code.ilike(payload.employee_code),
                User.id != user_id,
                User.deleted_at.is_(None)
            ).first()
            if existing:
                raise HTTPException(
                    status_code=409,
                    detail=f"Employee code '{payload.employee_code}' already exists (case-insensitive)"
                )
            user.employee_code = payload.employee_code
    if payload.phone is not None:
            user.phone = payload.phone
    if payload.password:
            user.password_hash = hash_password(payload.password)


    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Soft-delete user (admin-only)
@router.delete("/{user_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_user(user_id: str, db: Session = Depends(get_db)):
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user = db.query(User).filter(User.id == user_id, User.deleted_at == None).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    from datetime import datetime, timezone
    user.deleted_at = datetime.now(tz=timezone.utc)
    db.add(user)
    db.commit()
    return

# Get currently authenticated user (any logged-in user)
@employees_router.get("", response_model=UserResponse)
def me(current_user = Depends(get_current_user)):
    return current_user