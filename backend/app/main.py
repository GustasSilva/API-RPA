from fastapi import FastAPI
from sqlalchemy.exc import OperationalError
from app.core.scheduler import scheduler
from app.database.session import engine
from app.database.base import Base
from app.routers import atos
from app.core import auth


# Importar models para registrar no metadata

app = FastAPI()

from app.routers import rpa

app.include_router(rpa.router)
app.include_router(atos.router)


@app.on_event("startup")
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as e:
        raise RuntimeError("Falha ao conectar no banco. Verifique DATABASE_URL e se o Postgres está ativo.") from e


@app.on_event("startup")
def start_scheduler():
    scheduler.start()

@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()

app.include_router(auth.router)