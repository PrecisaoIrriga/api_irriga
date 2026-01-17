import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, col, delete, func, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.core.config import settings
from app.models import (
    Setor,
    SetorCreate,
    SetorPublic,
    SetoresPublic,
    SetorUpdate,
)

router = APIRouter(prefix="/setores", tags=["setores"])


@router.get("/", response_model=SetoresPublic)
def read_setores(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """Retrieve setores."""
    count_statement = select(func.count()).select_from(Setor)
    count = session.exec(count_statement).one()

    statement = select(Setor).offset(skip).limit(limit)
    setores = session.exec(statement).all()

    return SetoresPublic(data=setores, count=count)


@router.post("/", response_model=SetorPublic)
def create_setor(*, session: SessionDep, setor_in: SetorCreate) -> Any:
    """Create new setor."""
    setor = Setor.model_validate(setor_in)
    session.add(setor)
    session.commit()
    session.refresh(setor)
    return setor


@router.get("/{setor_id}", response_model=SetorPublic)
def read_setor(setor_id: uuid.UUID, session: SessionDep) -> Any:
    """Get a specific setor by id."""
    setor = session.get(Setor, setor_id)
    if not setor:
        raise HTTPException(status_code=404, detail="Setor not found")
    return setor


@router.patch(
    "/{setor_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=SetorPublic,
)
def update_setor(
    *,
    session: SessionDep,
    setor_id: uuid.UUID,
    setor_in: SetorUpdate,
) -> Any:
    """Update a setor."""
    setor = session.get(Setor, setor_id)
    if not setor:
        raise HTTPException(status_code=404, detail="Setor not found")

    update_data = setor_in.model_dump(exclude_unset=True)
    setor.sqlmodel_update(update_data)
    session.add(setor)
    session.commit()
    session.refresh(setor)
    return setor


@router.delete(
    "/{setor_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_setor(setor_id: uuid.UUID, session: SessionDep) -> dict:
    """Delete a setor."""
    setor = session.get(Setor, setor_id)
    if not setor:
        raise HTTPException(status_code=404, detail="Setor not found")

    session.delete(setor)
    session.commit()
    return {"message": "Setor deleted successfully"}
