from pydantic import BaseModel
from typing import Optional

class RpaLogCreate(BaseModel):
    total_capturado: int
    total_sucesso: int
    total_erros: int
    status: str
    execution_time: float
    error_message: Optional[str] = None


class RpaLogResponse(RpaLogCreate):
    id: str

    class Config:
        from_attributes = True

class ScheduleRequest(BaseModel):
    trigger: str  # "interval" ou "cron"
    hours: Optional[int] = None
    minutes: Optional[int] = None