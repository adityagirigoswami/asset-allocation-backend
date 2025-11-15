from datetime import datetime, timedelta, timezone
from typing import Optional, Literal
import jwt
from core.config import settings

def _exp(minutes: int = 0, days: int = 0):
    return datetime.now(tz=timezone.utc) + timedelta(minutes=minutes, days=days)

def create_access_token(sub: str) -> str:
    payload = {
        "sub": sub,
        "type": "access",
        "exp": _exp(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(sub: str) -> str:
    payload = {
        "sub": sub,
        "type": "refresh",
        "exp": _exp(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
