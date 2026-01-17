import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, col, delete, func, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.core.config import settings
from app.models import (
    Aparelho,
    AparelhoCreate,
    AparelhoPublic,
    AparelhosPublic,
    AparelhoUpdate,
)

router = APIRouter(prefix="/aparelhos", tags=["aparelhos"])


@router.get("/", response_model=AparelhosPublic)
def read_aparelhos(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """Retrieve aparelhos."""
    count_statement = select(func.count()).select_from(Aparelho)
    count = session.exec(count_statement).one()

    statement = select(Aparelho).offset(skip).limit(limit)
    aparelhos = session.exec(statement).all()

    return AparelhosPublic(data=aparelhos, count=count)


@router.post("/", response_model=AparelhoPublic)
def create_aparelho(*, session: SessionDep, aparelho_in: AparelhoCreate) -> Any:
    """Create new aparelho."""
    aparelho = Aparelho.model_validate(aparelho_in)
    session.add(aparelho)
    session.commit()
    session.refresh(aparelho)
    return aparelho


@router.get("/{aparelho_id}", response_model=AparelhoPublic)
def read_aparelho(aparelho_id: uuid.UUID, session: SessionDep) -> Any:
    """Get a specific aparelho by id."""
    aparelho = session.get(Aparelho, aparelho_id)
    if not aparelho:
        raise HTTPException(status_code=404, detail="Aparelho not found")
    return aparelho


@router.patch(
    "/{aparelho_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=AparelhoPublic,
)
def update_aparelho(
    *,
    session: SessionDep,
    aparelho_id: uuid.UUID,
    aparelho_in: AparelhoUpdate,
) -> Any:
    """Update an aparelho."""
    aparelho = session.get(Aparelho, aparelho_id)
    if not aparelho:
        raise HTTPException(status_code=404, detail="Aparelho not found")

    update_data = aparelho_in.model_dump(exclude_unset=True)
    aparelho.sqlmodel_update(update_data)
    session.add(aparelho)
    session.commit()
    session.refresh(aparelho)
    return aparelho


@router.delete(
    "/{aparelho_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_aparelho(aparelho_id: uuid.UUID, session: SessionDep) -> dict:
    """Delete an aparelho."""
    aparelho = session.get(Aparelho, aparelho_id)
    if not aparelho:
        raise HTTPException(status_code=404, detail="Aparelho not found")

    session.delete(aparelho)
    session.commit()
    return {"message": "Aparelho deleted successfully"}
