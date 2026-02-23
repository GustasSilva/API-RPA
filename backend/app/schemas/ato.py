from pydantic import BaseModel
from datetime import date
from uuid import UUID
from typing import Optional
from datetime import date
from pydantic import BaseModel


class AtoBase(BaseModel):
    tipo_ato: str
    numero_ato: str
    orgao_unidade: str
    publicacao: date
    ementa: str


class AtoCreate(AtoBase):
    pass

class AtoUpdate(BaseModel):
    tipo_ato: Optional[str] = None
    numero_ato: Optional[str] = None
    orgao_unidade: Optional[str] = None
    publicacao: Optional[date] = None
    ementa: Optional[str] = None


class AtoResponse(AtoBase):
    id: UUID

    class Config:
        from_attributes = True