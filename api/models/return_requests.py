import uuid
from sqlalchemy import Column, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from db.config import Base

class ReturnRequest(Base):
    __tablename__ = "return_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    allocation_id = Column(ForeignKey("allocations.id"), nullable=False)
    requested_by = Column(ForeignKey("users.id"), nullable=False)
    description = Column(Text)
    approved_at = Column(TIMESTAMP(timezone=True))
    decision_note = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True))
