from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.models.ato import Ato
from app.models.rpa_log import RpaLog
import time

def _chunks(data: list[dict], size: int):
    for i in range(0, len(data), size):
        yield data[i:i + size]

def salvar_lote_atos(db: Session, atos_data: list[dict], chunk_size: int = 500):
    inicio = time.time()
    total = 0
    status = "SUCESSO"
    error_message = None

    try:
        for chunk in _chunks(atos_data, chunk_size):
            stmt = (
                insert(Ato)
                .values(chunk)
                .on_conflict_do_nothing(constraint="uq_ato_unico")
            )
            result = db.execute(stmt)
            total += result.rowcount or 0

        db.commit()

    except Exception as exc:
        db.rollback()
        status = "ERRO"
        error_message = str(exc)

    tempo_execucao = time.time() - inicio

    log = RpaLog(
        total_registros=total,
        status=status,
        error_message=error_message,
        execution_time=tempo_execucao,
    )
    db.add(log)
    db.commit()

    return {
        "status": status.lower(),
        "total_registros": total,
        "execution_time": tempo_execucao,
        "error_message": error_message,
    }