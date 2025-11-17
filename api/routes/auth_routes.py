from fastapi import APIRouter, Depends, HTTPException, status , Header
from sqlalchemy.orm import Session
from db.auth import get_db
from api.schemas.user_schemas import UserLogin, TokenPair, EmployeeCreate, UserResponse, PasswordResetRequest, PasswordResetConfirm
from api.models.users import User
from api.models.user_roles import UserRole
from api.utils.hashing import verify_password, hash_password
from api.utils.jwt_handler import create_access_token, create_refresh_token, decode_token
from core.security import require_admin, get_current_user
from api.models.password_reset_tokens import PasswordResetToken
from datetime import datetime, timedelta, timezone
import uuid
from api.utils.mailer import EmailService
from core.config import settings



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


# ------------------ PASSWORD RESET: REQUEST ------------------
@router.post("/password/reset-request")
async def request_password_reset(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email, User.deleted_at.is_(None)).first()

    # Always return success message to avoid email enumeration
    if not user:
        return {"detail": "If the email exists, a reset link will be sent."}

    token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(hours=1)

    prt = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    db.add(prt)
    db.commit()

    # Construct reset link (temporary frontend URL)
    reset_link = f"{settings.FRONTEND_RESET_URL}?token={token}"

    html = f"""
    <h3>Password Reset Request</h3>
    <p>Hello {user.full_name},</p>
    <p>You requested a password reset.</p>
    <p>
        <a href="{reset_link}"
           style="padding: 10px 20px; background-color: #007bff; color:white; text-decoration:none; border-radius:5px;">
            Reset Password
        </a>
    </p>
    <p>If you did not request this, you can safely ignore this email.</p>
    """

    # 🎯 send email using pluggable service
    await EmailService.send_email(
        to=[user.email],
        subject="Password Reset Request",
        html=html
    )

    return {"detail": "If the email exists, a reset link will be sent."}


# ------------------ PASSWORD RESET: CONFIRM ------------------
@router.post("/password/reset")
def confirm_password_reset(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    token_row = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token == payload.token,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.deleted_at.is_(None)
        )
        .first()
    )

    if not token_row:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    if token_row.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token expired")

    user = db.query(User).filter(User.id == token_row.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(payload.new_password)
    token_row.used_at = datetime.utcnow()

    db.commit()

    return {"detail": "Password reset successful"}

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
