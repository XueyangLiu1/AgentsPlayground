"""Pydantic schemas (v2)."""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from .models import (
    Issuer,
    CardStatus,
    Frequency,
    CycleType,
    Category,
    ReminderStatus,
    Recurring,
)


class _ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Cardholder
class CardholderBase(BaseModel):
    name: str
    color_tag: str = "#3b82f6"


class CardholderCreate(CardholderBase):
    pass


class CardholderRead(_ORMModel, CardholderBase):
    id: int
    created_at: datetime
    updated_at: datetime


class CardholderUpdate(BaseModel):
    name: Optional[str] = None
    color_tag: Optional[str] = None


# Card
class CardBase(BaseModel):
    cardholder_id: int
    issuer: Issuer
    name: str
    opened_date: date
    annual_fee: float = 0.0
    fee_waived_first_year: bool = False
    status: CardStatus = CardStatus.active
    next_fee_date: date
    can_close_after_date: date
    notes: Optional[str] = None


class CardCreate(CardBase):
    pass


class CardRead(_ORMModel, CardBase):
    id: int
    created_at: datetime
    updated_at: datetime


class CardUpdate(BaseModel):
    cardholder_id: Optional[int] = None
    issuer: Optional[Issuer] = None
    name: Optional[str] = None
    opened_date: Optional[date] = None
    annual_fee: Optional[float] = None
    fee_waived_first_year: Optional[bool] = None
    status: Optional[CardStatus] = None
    next_fee_date: Optional[date] = None
    can_close_after_date: Optional[date] = None
    notes: Optional[str] = None


# Benefit
class BenefitBase(BaseModel):
    card_id: int
    name: str
    amount: float = 0.0
    frequency: Frequency
    cycle_type: CycleType
    category: Category = Category.credit
    notes: Optional[str] = None


class BenefitCreate(BenefitBase):
    pass


class BenefitRead(_ORMModel, BenefitBase):
    id: int
    created_at: datetime
    updated_at: datetime


class BenefitUpdate(BaseModel):
    card_id: Optional[int] = None
    name: Optional[str] = None
    amount: Optional[float] = None
    frequency: Optional[Frequency] = None
    cycle_type: Optional[CycleType] = None
    category: Optional[Category] = None
    notes: Optional[str] = None


# BenefitProgress
class BenefitProgressBase(BaseModel):
    benefit_id: int
    period: str
    claimed_amount: float = 0.0
    claimed_date: date
    claimed_by: Optional[str] = None
    notes: Optional[str] = None


class BenefitProgressCreate(BenefitProgressBase):
    pass


class BenefitProgressRead(_ORMModel, BenefitProgressBase):
    id: int
    created_at: datetime
    updated_at: datetime


class BenefitProgressUpdate(BaseModel):
    benefit_id: Optional[int] = None
    period: Optional[str] = None
    claimed_amount: Optional[float] = None
    claimed_date: Optional[date] = None
    claimed_by: Optional[str] = None
    notes: Optional[str] = None


class BenefitClaimRequest(BaseModel):
    claimed_amount: Optional[float] = None
    claimed_date: Optional[date] = None
    claimed_by: Optional[str] = None
    notes: Optional[str] = None


# SignUpBonus
class SignUpBonusBase(BaseModel):
    card_id: int
    required_spend: float
    deadline_date: date
    reward_description: str
    current_spend: float = 0.0
    completed: bool = False


class SignUpBonusCreate(SignUpBonusBase):
    pass


class SignUpBonusRead(_ORMModel, SignUpBonusBase):
    id: int
    created_at: datetime
    updated_at: datetime


class SignUpBonusUpdate(BaseModel):
    card_id: Optional[int] = None
    required_spend: Optional[float] = None
    deadline_date: Optional[date] = None
    reward_description: Optional[str] = None
    current_spend: Optional[float] = None
    completed: Optional[bool] = None


# Reminder
class ReminderBase(BaseModel):
    card_id: Optional[int] = None
    title: str
    due_date: date
    status: ReminderStatus = ReminderStatus.pending
    recurring: Recurring = Recurring.none


class ReminderCreate(ReminderBase):
    pass


class ReminderRead(_ORMModel, ReminderBase):
    id: int
    created_at: datetime
    updated_at: datetime


class ReminderUpdate(BaseModel):
    card_id: Optional[int] = None
    title: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[ReminderStatus] = None
    recurring: Optional[Recurring] = None


# Dashboard
class UnclaimedBenefit(BaseModel):
    benefit_id: int
    benefit_name: str
    card_id: int
    card_name: str
    cardholder_id: int
    cardholder_name: str
    amount: float
    period: str


class SubGap(BaseModel):
    card_id: int
    card_name: str
    cardholder_name: str
    required_spend: float
    current_spend: float
    remaining_spend: float
    remaining_days: int
    deadline_date: date


class CardSummary(BaseModel):
    card_id: int
    card_name: str
    cardholder_name: str
    next_fee_date: Optional[date] = None
    can_close_after_date: Optional[date] = None
    annual_fee: float = 0.0


class FamilySummary(BaseModel):
    month: str
    claimed_amount: float
    total_amount: float


class DashboardOverview(BaseModel):
    unclaimed_this_period: List[UnclaimedBenefit]
    sub_gaps: List[SubGap]
    fee_due_soon: List[CardSummary]
    closable_soon: List[CardSummary]
    family_summary: FamilySummary


# Card with progress summary
class BenefitProgressSummary(BaseModel):
    benefit_id: int
    benefit_name: str
    amount: float
    claimed_amount: float
    period: str


class CardWithProgress(CardRead):
    period_total: float = 0.0
    period_claimed: float = 0.0
    benefit_summaries: List[BenefitProgressSummary] = []


# Presets
class PresetBenefit(BaseModel):
    name: str
    amount: float
    frequency: Frequency
    cycle_type: CycleType
    category: Category
    notes: Optional[str] = None


class PresetCard(BaseModel):
    issuer: Issuer
    name: str
    annual_fee: float
    benefits: List[PresetBenefit]
