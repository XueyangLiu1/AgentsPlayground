from fastapi import APIRouter
from .. import models, schemas
from ._generic import make_router

router = make_router(
    "/cardholders", "cardholders",
    models.Cardholder,
    schemas.CardholderCreate,
    schemas.CardholderRead,
    schemas.CardholderUpdate,
)
