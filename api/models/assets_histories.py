from sqlalchemy import Column, TIMESTAMP, BigInteger, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from db.config import Base
from api.utils.enums import AssetStatus
from sqlalchemy import Enum as SAEnum

class AssetHistory(Base):
    __tablename__ = "assets_histories"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    asset_id = Column(ForeignKey("assets.id"), nullable=False)
    user_id = Column(ForeignKey("users.id"))
    from_status = Column(SAEnum(AssetStatus, name="asset_status"), nullable=True)
    to_status = Column(SAEnum(AssetStatus, name="asset_status"), nullable=False)
    event_metadata = Column(JSON)
    occurred_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True))
