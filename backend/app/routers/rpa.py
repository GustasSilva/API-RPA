from datetime import datetime, date, time
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.rpa_log import ScheduleRequest
from app.database.deps import get_db
from app.services.rpa_service import executar_rpa
from app.core.scheduler import scheduler
from app.core.security import verificar_token
from app.models.rpa_log import RpaLog
from app.schemas.rpa_log import RpaLogListResponse

router = APIRouter(prefix="/rpa", tags=["RPA"])


@router.post("/executar")
def executar(
    user: str = Depends(verificar_token),
):
    return executar_rpa()

@router.post("/schedule")
def schedule_rpa(
    request: ScheduleRequest, 
    user: str = Depends(verificar_token)):

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
def list_schedules(user: str = Depends(verificar_token)):
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
def remove_schedule(
    job_id: str,
    user: str = Depends(verificar_token)
):

    job = scheduler.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")

    scheduler.remove_job(job_id)

    return {"status": "removido", "job_id": job_id}

@router.get("/logs", response_model=RpaLogListResponse)
def list_rpa_logs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
    db: Session = Depends(get_db),
    user: str = Depends(verificar_token),
):
    query = db.query(RpaLog)

    if status:
        query = query.filter(RpaLog.status.ilike(f"%{status}%"))

    if data_inicio:
        query = query.filter(
            RpaLog.execution_date >= datetime.combine(data_inicio, time.min)
        )

    if data_fim:
        query = query.filter(
            RpaLog.execution_date <= datetime.combine(data_fim, time.max)
        )

    total = query.count()

    items = (
        query.order_by(RpaLog.execution_date.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "page": page,
        "size": size,
        "total": total,
        "items": [
            {
                "id": str(log.id),
                "execution_date": log.execution_date,
                "total_registros": log.total_registros,
                "status": log.status,
                "error_message": log.error_message,
                "execution_time": log.execution_time,
            }
            for log in items
        ],
    }