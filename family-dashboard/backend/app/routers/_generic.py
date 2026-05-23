from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from .. import crud, models, schemas
from ..database import get_db


def make_router(prefix: str, tag: str, model, create_schema, read_schema, update_schema):
    router = APIRouter(prefix=prefix, tags=[tag])

    @router.get("", response_model=list[read_schema])
    def list_items(db: Session = Depends(get_db),
                   cardholder_id: Optional[int] = Query(None),
                   card_id: Optional[int] = Query(None),
                   benefit_id: Optional[int] = Query(None)):
        return crud.list_all(db, model,
                             cardholder_id=cardholder_id,
                             card_id=card_id,
                             benefit_id=benefit_id)

    @router.get("/{obj_id}", response_model=read_schema)
    def get_item(obj_id: int, db: Session = Depends(get_db)):
        obj = crud.get(db, model, obj_id)
        if not obj:
            raise HTTPException(404, f"{tag} not found")
        return obj

    @router.post("", response_model=read_schema, status_code=201)
    def create_item(data: create_schema, db: Session = Depends(get_db)):
        return crud.create(db, model, data)

    @router.patch("/{obj_id}", response_model=read_schema)
    def update_item(obj_id: int, data: update_schema, db: Session = Depends(get_db)):
        obj = crud.get(db, model, obj_id)
        if not obj:
            raise HTTPException(404, f"{tag} not found")
        return crud.update(db, obj, data)

    @router.delete("/{obj_id}", status_code=204)
    def delete_item(obj_id: int, db: Session = Depends(get_db)):
        obj = crud.get(db, model, obj_id)
        if not obj:
            raise HTTPException(404, f"{tag} not found")
        crud.delete(db, obj)
        return None

    return router
