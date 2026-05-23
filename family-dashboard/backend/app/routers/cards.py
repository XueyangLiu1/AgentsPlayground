from .. import models, schemas
from ._generic import make_router

router = make_router(
    "/cards", "cards",
    models.Card,
    schemas.CardCreate,
    schemas.CardRead,
    schemas.CardUpdate,
)
