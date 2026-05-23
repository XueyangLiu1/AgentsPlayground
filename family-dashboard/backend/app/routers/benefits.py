from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from .. import models, schemas, crud
from ..database import get_db
from ._generic import make_router

router = make_router(
    "/benefits", "benefits",
    models.Benefit,
    schemas.BenefitCreate,
    schemas.BenefitRead,
    schemas.BenefitUpdate,
)


@router.post("/{benefit_id}/claim", response_model=schemas.BenefitProgressRead, status_code=201)
def claim_benefit(benefit_id: int, req: schemas.BenefitClaimRequest, db: Session = Depends(get_db)):
    benefit = crud.get(db, models.Benefit, benefit_id)
    if not benefit:
        raise HTTPException(404, "Benefit not found")
    claimed_date = req.claimed_date or date.today()
    period = crud.period_for(benefit.frequency, claimed_date)
    amount = req.claimed_amount if req.claimed_amount is not None else benefit.amount
    progress = models.BenefitProgress(
        benefit_id=benefit.id,
        period=period,
        claimed_amount=amount,
        claimed_date=claimed_date,
        claimed_by=req.claimed_by,
        notes=req.notes,
    )
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress
