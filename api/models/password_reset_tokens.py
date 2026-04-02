import uuid
from sqlalchemy import Column, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from db.config import Base
from sqlalchemy import ForeignKey

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    token = Column(Text, unique=True, nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    used_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True))
