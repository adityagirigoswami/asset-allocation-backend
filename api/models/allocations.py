import uuid
from sqlalchemy import Column, TIMESTAMP, Text, DateTime, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from db.config import Base
from sqlalchemy.orm import relationship

class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(ForeignKey("assets.id"), nullable=False)
    employee_id = Column(ForeignKey("users.id"), nullable=False)
    allocated_by = Column(ForeignKey("users.id"), nullable=False)
    allocation_date = Column(Date, nullable=False)
    returned_at = Column(TIMESTAMP(timezone=True))
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True))

    asset = relationship("Asset")
    employee = relationship("User", foreign_keys=[employee_id])
    allocator = relationship("User", foreign_keys=[allocated_by])
