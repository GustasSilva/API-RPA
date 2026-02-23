import uuid
from sqlalchemy import Column, String, Date, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import UniqueConstraint
from datetime import datetime

from app.database.base import Base

class Ato(Base):
    __tablename__ = "atos"

    __table_args__ = (
        UniqueConstraint("numero_ato", "publicacao", "orgao_unidade", name="uq_ato_unico"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo_ato = Column(String(255), nullable=False)
    numero_ato = Column(String(100), nullable=False)
    orgao_unidade = Column(String(255), nullable=False)
    publicacao = Column(Date, nullable=False)
    ementa = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)