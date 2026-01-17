import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, col, delete, func, select

from app import crud
from app.api.deps import SessionDep, get_current_active_superuser
from app.core.config import settings
from app.models import (
    Agricultor,
    AgricultorCreate,
    AgricultorPublic,
    AgricultoresPublic,
    AgricultorUpdate,
)

router = APIRouter(prefix="/agricultores", tags=["agricultores"])


@router.get("/", response_model=AgricultoresPublic)
def read_agricultores(
    session: SessionDep, skip: int = 0, limit: int = 100
) -> Any:
    """Retrieve agricultores."""
    count_statement = select(func.count()).select_from(Agricultor)
    count = session.exec(count_statement).one()

    statement = select(Agricultor).offset(skip).limit(limit)
    agricultores = session.exec(statement).all()

    return AgricultoresPublic(data=agricultores, count=count)


@router.post("/", response_model=AgricultorPublic)
def create_agricultor(
    *, session: SessionDep, agricultor_in: AgricultorCreate
) -> Any:
    """Create new agricultor."""
    agricultor = Agricultor.model_validate(agricultor_in)
    session.add(agricultor)
    session.commit()
    session.refresh(agricultor)
    return agricultor


@router.get("/{agricultor_id}", response_model=AgricultorPublic)
def read_agricultor(agricultor_id: uuid.UUID, session: SessionDep) -> Any:
    """Get a specific agricultor by id."""
    agricultor = session.get(Agricultor, agricultor_id)
    if not agricultor:
        raise HTTPException(status_code=404, detail="Agricultor not found")
    return agricultor


@router.patch(
    "/{agricultor_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=AgricultorPublic,
)
def update_agricultor(
    *,
    session: SessionDep,
    agricultor_id: uuid.UUID,
    agricultor_in: AgricultorUpdate,
) -> Any:
    """Update an agricultor."""
    agricultor = session.get(Agricultor, agricultor_id)
    if not agricultor:
        raise HTTPException(status_code=404, detail="Agricultor not found")

    update_data = agricultor_in.model_dump(exclude_unset=True)
    agricultor.sqlmodel_update(update_data)
    session.add(agricultor)
    session.commit()
    session.refresh(agricultor)
    return agricultor


@router.delete(
    "/{agricultor_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_agricultor(agricultor_id: uuid.UUID, session: SessionDep) -> dict:
    """Delete an agricultor."""
    agricultor = session.get(Agricultor, agricultor_id)
    if not agricultor:
        raise HTTPException(status_code=404, detail="Agricultor not found")

    session.delete(agricultor)
    session.commit()
    return {"message": "Agricultor deleted successfully"}
