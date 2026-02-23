from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.rpa_log import ScheduleRequest
from app.database.deps import get_db
from app.services.rpa_service import executar_rpa
from app.core.scheduler import scheduler
from app.core.security import verificar_token

router = APIRouter(prefix="/rpa", tags=["RPA"])


@router.post("/executar")
def executar(
    user: str = Depends(verificar_token),
):
    return executar_rpa()

@router.post("/schedule")
def schedule_rpa(request: ScheduleRequest):

    if request.trigger not in ["interval", "cron"]:
        raise HTTPException(status_code=400, detail="Trigger deve ser 'interval' ou 'cron'")

    job_id = f"rpa_job_{datetime.utcnow().timestamp()}"

    if request.trigger == "interval":
        if not request.hours and not request.minutes:
            raise HTTPException(status_code=400, detail="Informe hours ou minutes para interval")

        scheduler.add_job(
            executar_rpa,
            trigger="interval",
            hours=request.hours,
            minutes=request.minutes,
            id=job_id,
            replace_existing=True
        )

    elif request.trigger == "cron":
        if request.hours is None or request.minutes is None:
            raise HTTPException(status_code=400, detail="Informe hours e minutes para cron")

        scheduler.add_job(
            executar_rpa,
            trigger="cron",
            hour=request.hours,
            minute=request.minutes,
            id=job_id,
            replace_existing=True
        )

    return {
        "status": "agendado",
        "job_id": job_id,
        "trigger": request.trigger
    }

@router.get("/schedules")
def list_schedules():
    jobs = scheduler.get_jobs()

    return [
        {
            "id": job.id,
            "next_run": str(job.next_run_time),
            "trigger": str(job.trigger)
        }
        for job in jobs
    ]

@router.delete("/schedule/{job_id}")
def remove_schedule(job_id: str):
    job = scheduler.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")

    scheduler.remove_job(job_id)

    return {"status": "removido", "job_id": job_id}