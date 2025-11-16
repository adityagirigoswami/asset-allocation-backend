from sqlalchemy import Column, Integer, Text, TIMESTAMP
from sqlalchemy.sql import func
from db.config import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True))
