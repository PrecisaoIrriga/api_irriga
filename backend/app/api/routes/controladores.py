import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, col, delete, func, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.core.config import settings
from app.models import (
    Controlador,
    ControladorCreate,
    ControladorPublic,
    ControladoresPublic,
    ControladorUpdate,
)

router = APIRouter(prefix="/controladores", tags=["controladores"])


@router.get("/", response_model=ControladoresPublic)
def read_controladores(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """Retrieve controladores."""
    count_statement = select(func.count()).select_from(Controlador)
    count = session.exec(count_statement).one()

    statement = select(Controlador).offset(skip).limit(limit)
    controladores = session.exec(statement).all()

    return ControladoresPublic(data=controladores, count=count)


@router.post("/", response_model=ControladorPublic)
def create_controlador(
    *, session: SessionDep, controlador_in: ControladorCreate
) -> Any:
    """Create new controlador."""
    controlador = Controlador.model_validate(controlador_in)
    session.add(controlador)
    session.commit()
    session.refresh(controlador)
    return controlador


@router.get("/{controlador_id}", response_model=ControladorPublic)
def read_controlador(controlador_id: uuid.UUID, session: SessionDep) -> Any:
    """Get a specific controlador by id."""
    controlador = session.get(Controlador, controlador_id)
    if not controlador:
        raise HTTPException(status_code=404, detail="Controlador not found")
    return controlador


@router.patch(
    "/{controlador_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ControladorPublic,
)
def update_controlador(
    *,
    session: SessionDep,
    controlador_id: uuid.UUID,
    controlador_in: ControladorUpdate,
) -> Any:
    """Update a controlador."""
    controlador = session.get(Controlador, controlador_id)
    if not controlador:
        raise HTTPException(status_code=404, detail="Controlador not found")

    update_data = controlador_in.model_dump(exclude_unset=True)
    controlador.sqlmodel_update(update_data)
    session.add(controlador)
    session.commit()
    session.refresh(controlador)
    return controlador


@router.delete(
    "/{controlador_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_controlador(controlador_id: uuid.UUID, session: SessionDep) -> dict:
    """Delete a controlador."""
    controlador = session.get(Controlador, controlador_id)
    if not controlador:
        raise HTTPException(status_code=404, detail="Controlador not found")

    session.delete(controlador)
    session.commit()
    return {"message": "Controlador deleted successfully"}
