import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, col, delete, func, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.core.config import settings
from app.models import (
    Comando,
    ComandoCreate,
    ComandoPublic,
    ComandosPublic,
    ComandoUpdate,
)

router = APIRouter(prefix="/comandos", tags=["comandos"])


@router.get("/", response_model=ComandosPublic)
def read_comandos(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """Retrieve comandos."""
    count_statement = select(func.count()).select_from(Comando)
    count = session.exec(count_statement).one()

    statement = select(Comando).offset(skip).limit(limit)
    comandos = session.exec(statement).all()

    return ComandosPublic(data=comandos, count=count)


@router.post("/", response_model=ComandoPublic)
def create_comando(*, session: SessionDep, comando_in: ComandoCreate) -> Any:
    """Create new comando."""
    comando = Comando.model_validate(comando_in)
    session.add(comando)
    session.commit()
    session.refresh(comando)
    return comando


@router.get("/{comando_id}", response_model=ComandoPublic)
def read_comando(comando_id: uuid.UUID, session: SessionDep) -> Any:
    """Get a specific comando by id."""
    comando = session.get(Comando, comando_id)
    if not comando:
        raise HTTPException(status_code=404, detail="Comando not found")
    return comando


@router.get("/controlador/{controlador_id}", response_model=ComandosPublic)
def read_comandos_por_controlador(
    controlador_id: uuid.UUID, session: SessionDep, skip: int = 0, limit: int = 100
) -> Any:
    """Get all comandos for a specific controlador (pendentes ou não)."""
    count_statement = select(func.count()).select_from(Comando).where(
        Comando.controlador_id == controlador_id,
        Comando.status == "pendente",
    )
    count = session.exec(count_statement).one()

    statement = (
        select(Comando)
        .where(Comando.controlador_id == controlador_id , Comando.status == "pendente")
        .offset(skip)
        .limit(limit)
    )
    comandos = session.exec(statement).all()

    return ComandosPublic(data=comandos, count=count)

@router.patch(
    "/{comando_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ComandoPublic,
)
def update_comando(
    *,
    session: SessionDep,
    comando_id: uuid.UUID,
    comando_in: ComandoUpdate,
) -> Any:
    """Update a comando."""
    comando = session.get(Comando, comando_id)
    if not comando:
        raise HTTPException(status_code=404, detail="Comando not found")

    update_data = comando_in.model_dump(exclude_unset=True)
    comando.sqlmodel_update(update_data)
    session.add(comando)
    session.commit()
    session.refresh(comando)
    return comando


@router.delete(
    "/{comando_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_comando(comando_id: uuid.UUID, session: SessionDep) -> dict:
    """Delete a comando."""
    comando = session.get(Comando, comando_id)
    if not comando:
        raise HTTPException(status_code=404, detail="Comando not found")

    session.delete(comando)
    session.commit()
    return {"message": "Comando deleted successfully"}
