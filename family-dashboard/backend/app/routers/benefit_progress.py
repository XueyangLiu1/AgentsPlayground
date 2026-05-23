from .. import models, schemas
from ._generic import make_router

router = make_router(
    "/benefit-progress", "benefit_progress",
    models.BenefitProgress,
    schemas.BenefitProgressCreate,
    schemas.BenefitProgressRead,
    schemas.BenefitProgressUpdate,
)
