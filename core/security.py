from fastapi import Depends, HTTPException, status
from uuid import UUID
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from api.utils.jwt_handler import decode_token
from db.auth import get_db
from api.models.users import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing user ID in token"
        )

    try:
        user_uuid = UUID(user_id_str)   # << FIXED!
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject (user ID format)"
        )

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    # admin role_id will be seeded as the 'admin' role's id
    if getattr(user.role, "name", None) != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return user
