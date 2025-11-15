import uuid
from sqlalchemy import Column, Text, TIMESTAMP, Integer, Numeric, Date, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from db.config import Base
from sqlalchemy.orm import relationship
from api.utils.enums import AssetStatus

from sqlalchemy import Enum as SAEnum

class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(Integer, ForeignKey("categories.id"))
    name = Column(Text, nullable=False)
    tag_code = Column(Text, unique=True)
    serial_number = Column(Text, unique=True)
    status = Column(SAEnum(AssetStatus, name="asset_status"), nullable=False, server_default=AssetStatus.available.value)
    purchase_date = Column(Date)
    purchase_cost = Column(Numeric(12,2))
    warranty_expiry = Column(Date)
    specs = Column(JSON)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True))

    category = relationship("Category")
