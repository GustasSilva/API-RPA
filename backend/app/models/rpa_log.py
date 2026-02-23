import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.database.base import Base


class RpaLog(Base):
    __tablename__ = "rpa_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_date = Column(DateTime, default=datetime.utcnow)
    total_registros = Column(Integer)
    status = Column(String(50))
    error_message = Column(Text, nullable=True)
    execution_time = Column(Float)