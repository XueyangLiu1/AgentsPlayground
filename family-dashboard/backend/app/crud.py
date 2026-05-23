"""Generic CRUD helpers and period calculation."""

from datetime import date
from typing import Type, TypeVar, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from . import models
from pydantic import BaseModel

ModelT = TypeVar("ModelT")


def get(db: Session, model: Type[ModelT], obj_id: int) -> Optional[ModelT]:
    return db.get(model, obj_id)


def list_all(db: Session, model: Type[ModelT], **filters) -> list[ModelT]:
    stmt = select(model)
    for key, value in filters.items():
        if value is not None and hasattr(model, key):
            stmt = stmt.where(getattr(model, key) == value)
    return list(db.execute(stmt).scalars().all())


def create(db: Session, model: Type[ModelT], data: BaseModel) -> ModelT:
    obj = model(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, obj, data: BaseModel):
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, obj) -> None:
    db.delete(obj)
    db.commit()


def period_for(frequency: models.Frequency, d: Optional[date] = None) -> str:
    """Compute period string for a frequency."""
    d = d or date.today()
    if frequency == models.Frequency.monthly:
        return f"{d.year:04d}-{d.month:02d}"
    if frequency == models.Frequency.quarterly:
        q = (d.month - 1) // 3 + 1
        return f"{d.year:04d}-Q{q}"
    if frequency == models.Frequency.yearly:
        return f"{d.year:04d}"
    return str(d)
