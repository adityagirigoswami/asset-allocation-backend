import uuid
from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from sqlalchemy.orm import relationship
from db.config import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(CITEXT, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    full_name = Column(Text, nullable=False)
    role_id = Column(ForeignKey("user_roles.id"), nullable=False)
    employee_code = Column(Text, unique=True)
    phone = Column(Text)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True))

    role = relationship("UserRole")