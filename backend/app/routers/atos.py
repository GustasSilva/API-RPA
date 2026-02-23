from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date
from uuid import UUID
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import func
from datetime import date
from app.schemas.ato import AtoUpdate
from app.database.deps import get_db
from app.models.ato import Ato
from app.schemas.ato import AtoCreate, AtoResponse
from app.services.ato_service import salvar_lote_atos
from app.core.security import verificar_token

router = APIRouter(prefix="/atos", tags=["Atos"])

@router.post("/", response_model=AtoResponse)
def create_ato(ato: AtoCreate, db: Session = Depends(get_db), user: str = Depends(verificar_token)):
    novo_ato = Ato(**ato.dict())
    db.add(novo_ato)
    db.commit()
    db.refresh(novo_ato)
    return novo_ato

@router.post("/batch")
def create_atos_batch(
    atos: list[AtoCreate],
    db: Session = Depends(get_db),
    user: str = Depends(verificar_token)
):
    return salvar_lote_atos(
        db,
        [ato.model_dump() for ato in atos]
    )


@router.get("/", response_model=list[AtoResponse])
def get_atos(
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
    search: str | None = Query(None),
    db: Session = Depends(get_db)
):

    query = db.query(Ato).filter(Ato.deleted_at.is_(None))

    # Filtro por data inicial
    if data_inicio:
        query = query.filter(Ato.publicacao >= data_inicio)

    # Filtro por data final
    if data_fim:
        query = query.filter(Ato.publicacao <= data_fim)

    # Filtro de busca textual
    if search:
        query = query.filter(
            or_(
                Ato.tipo_ato.ilike(f"%{search}%"),
                Ato.numero_ato.ilike(f"%{search}%"),
                Ato.orgao_unidade.ilike(f"%{search}%"),
                Ato.ementa.ilike(f"%{search}%"),
            )
        )

    atos = query.order_by(Ato.publicacao.desc()).all()

    return atos


@router.put("/{ato_id}", response_model=AtoResponse)
def update_ato(
    ato_id: UUID,
    ato_update: AtoUpdate,
    db: Session = Depends(get_db),
    user: str = Depends(verificar_token)
):
    ato = db.query(Ato).filter(
        Ato.id == ato_id,
        Ato.deleted_at.is_(None)
    ).first()

    if not ato:
        raise HTTPException(status_code=404, detail="Ato não encontrado")

    for field, value in ato_update.dict(exclude_unset=True).items():
        setattr(ato, field, value)

    ato.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(ato)

    return ato


@router.delete("/{ato_id}")
def delete_ato(
    ato_id: UUID,
    db: Session = Depends(get_db),
    user: str = Depends(verificar_token)
):
    ato = db.query(Ato).filter(
        Ato.id == ato_id,
        Ato.deleted_at.is_(None)
    ).first()

    if not ato:
        raise HTTPException(status_code=404, detail="Ato não encontrado")

    ato.deleted_at = datetime.utcnow()

    db.commit()

    return {"message": "Ato excluído com sucesso"}

@router.get("/dashboard")
def dashboard(
    data_inicio: date | None = None,
    data_fim: date | None = None,
    db: Session = Depends(get_db)
):
    query_base = db.query(Ato).filter(Ato.deleted_at.is_(None))

    # Aplicando filtro por período
    if data_inicio:
        query_base = query_base.filter(Ato.publicacao >= data_inicio)

    if data_fim:
        query_base = query_base.filter(Ato.publicacao <= data_fim)

    # Total de atos
    total_atos = query_base.count()

    # Quantidade por órgão
    por_orgao = (
        query_base.with_entities(
            Ato.orgao_unidade,
            func.count(Ato.id).label("quantidade")
        )
        .group_by(Ato.orgao_unidade)
        .all()
    )

    # Quantidade por tipo de ato
    por_tipo = (
        query_base.with_entities(
            Ato.tipo_ato,
            func.count(Ato.id).label("quantidade")
        )
        .group_by(Ato.tipo_ato)
        .all()
    )

    return {
        "total_atos": total_atos,
        "por_orgao": [
            {"orgao_unidade": orgao, "quantidade": qtd}
            for orgao, qtd in por_orgao
        ],
        "por_tipo": [
            {"tipo_ato": tipo, "quantidade": qtd}
            for tipo, qtd in por_tipo
        ]
    }

