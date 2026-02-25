from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ScheduleRequest(BaseModel):
    trigger: str = Field(..., description="interval ou cron")
    hours: Optional[int] = None
    minutes: Optional[int] = None


class RpaLogBase(BaseModel):
    total_registros: int
    status: str
    execution_time: float
    error_message: Optional[str] = None


class RpaLogResponse(RpaLogBase):
    id: UUID
    execution_date: datetime

    class Config:
        from_attributes = True


class RpaLogListResponse(BaseModel):
    page: int
    size: int
    total: int
    items: list[RpaLogResponse]
