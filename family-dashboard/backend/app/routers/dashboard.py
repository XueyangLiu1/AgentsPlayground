"""Dashboard overview + cardholder cards summary."""

from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from .. import models, schemas, crud
from ..database import get_db

router = APIRouter(tags=["dashboard"])


def _period_for_benefit(benefit: models.Benefit, today: date) -> str:
    return crud.period_for(benefit.frequency, today)


@router.get("/dashboard/overview", response_model=schemas.DashboardOverview)
def overview(db: Session = Depends(get_db)):
    today = date.today()
    soon = today + timedelta(days=30)

    cards = db.execute(select(models.Card).where(models.Card.status != models.CardStatus.closed)).scalars().all()

    unclaimed = []
    family_total = 0.0
    family_claimed = 0.0
    month_period = f"{today.year:04d}-{today.month:02d}"

    for card in cards:
        for benefit in card.benefits:
            period = _period_for_benefit(benefit, today)
            existing = [p for p in benefit.progress if p.period == period]
            already_claimed = sum(p.claimed_amount for p in existing)
            if already_claimed < benefit.amount:
                unclaimed.append(schemas.UnclaimedBenefit(
                    benefit_id=benefit.id,
                    benefit_name=benefit.name,
                    card_id=card.id,
                    card_name=card.name,
                    cardholder_id=card.cardholder_id,
                    cardholder_name=card.cardholder.name,
                    amount=benefit.amount - already_claimed,
                    period=period,
                ))
            # Family month summary: only monthly benefits count for "this month"
            if benefit.frequency == models.Frequency.monthly and period == month_period:
                family_total += benefit.amount
                family_claimed += already_claimed

    unclaimed.sort(key=lambda u: u.amount, reverse=True)

    # SUB gaps
    subs = db.execute(select(models.SignUpBonus).where(models.SignUpBonus.completed == False)).scalars().all()
    sub_gaps = []
    for sub in subs:
        remaining_days = (sub.deadline_date - today).days
        sub_gaps.append(schemas.SubGap(
            card_id=sub.card_id,
            card_name=sub.card.name,
            cardholder_name=sub.card.cardholder.name,
            required_spend=sub.required_spend,
            current_spend=sub.current_spend,
            remaining_spend=max(0.0, sub.required_spend - sub.current_spend),
            remaining_days=remaining_days,
            deadline_date=sub.deadline_date,
        ))

    fee_due_soon = []
    closable_soon = []
    for card in cards:
        if card.next_fee_date and today <= card.next_fee_date <= soon:
            fee_due_soon.append(schemas.CardSummary(
                card_id=card.id,
                card_name=card.name,
                cardholder_name=card.cardholder.name,
                next_fee_date=card.next_fee_date,
                annual_fee=card.annual_fee,
            ))
        if card.can_close_after_date and today <= card.can_close_after_date <= soon:
            closable_soon.append(schemas.CardSummary(
                card_id=card.id,
                card_name=card.name,
                cardholder_name=card.cardholder.name,
                can_close_after_date=card.can_close_after_date,
            ))

    return schemas.DashboardOverview(
        unclaimed_this_period=unclaimed,
        sub_gaps=sub_gaps,
        fee_due_soon=fee_due_soon,
        closable_soon=closable_soon,
        family_summary=schemas.FamilySummary(
            month=month_period,
            claimed_amount=family_claimed,
            total_amount=family_total,
        ),
    )


@router.get("/cardholders/{cardholder_id}/cards", response_model=list[schemas.CardWithProgress])
def cardholder_cards(cardholder_id: int, db: Session = Depends(get_db)):
    holder = crud.get(db, models.Cardholder, cardholder_id)
    if not holder:
        raise HTTPException(404, "Cardholder not found")
    today = date.today()
    result = []
    for card in holder.cards:
        summaries = []
        period_total = 0.0
        period_claimed = 0.0
        for benefit in card.benefits:
            period = _period_for_benefit(benefit, today)
            claimed = sum(p.claimed_amount for p in benefit.progress if p.period == period)
            summaries.append(schemas.BenefitProgressSummary(
                benefit_id=benefit.id,
                benefit_name=benefit.name,
                amount=benefit.amount,
                claimed_amount=claimed,
                period=period,
            ))
            period_total += benefit.amount
            period_claimed += claimed
        result.append(schemas.CardWithProgress(
            **schemas.CardRead.model_validate(card).model_dump(),
            period_total=period_total,
            period_claimed=period_claimed,
            benefit_summaries=summaries,
        ))
    return result
