from .. import models, schemas
from ._generic import make_router

router = make_router(
    "/sign-up-bonuses", "sign_up_bonuses",
    models.SignUpBonus,
    schemas.SignUpBonusCreate,
    schemas.SignUpBonusRead,
    schemas.SignUpBonusUpdate,
)
