from fastapi import APIRouter, Depends, HTTPException, status , Header
from sqlalchemy.orm import Session
from db.auth import get_db
from api.schemas.user_schemas import UserLogin, TokenPair, EmployeeCreate, UserResponse
from api.models.users import User
from api.models.user_roles import UserRole
from api.utils.hashing import verify_password, hash_password
from api.utils.jwt_handler import create_access_token, create_refresh_token, decode_token
from core.security import require_admin, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenPair)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(user.password_hash, payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return TokenPair(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id))
    )

@router.post("/refresh", response_model=TokenPair)
def refresh_token(refresh_token: str = Header(..., alias="X-Refresh-Token"),
    db: Session = Depends(get_db)):
    """
    Accepts refresh token in body (simple). I'll move it to httpOnly cookie later.
    """
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return TokenPair(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id))
    )

# ADMIN-ONLY: create employee
@router.post("/employees", response_model=UserResponse)
def create_employee(payload: EmployeeCreate,
                    db: Session = Depends(get_db),
                    admin = Depends(require_admin)):
    employee_role = db.query(UserRole).filter(UserRole.name == "employee").first()
    if not employee_role:
        raise HTTPException(status_code=500, detail="Employee role missing. Run seeding.")

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
