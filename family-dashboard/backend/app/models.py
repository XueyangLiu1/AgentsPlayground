"""SQLAlchemy ORM models."""

from datetime import datetime, date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Text,
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship
import enum

from .database import Base


class Issuer(str, enum.Enum):
    Chase = "Chase"
    Amex = "Amex"
    Other = "Other"


class CardStatus(str, enum.Enum):
    active = "active"
    pending_downgrade = "pending_downgrade"
    pending_close = "pending_close"
    closed = "closed"


class Frequency(str, enum.Enum):
    monthly = "monthly"
    quarterly = "quarterly"
    yearly = "yearly"


class CycleType(str, enum.Enum):
    calendar_year = "calendar_year"
    anniversary_year = "anniversary_year"
    statement_month = "statement_month"


class Category(str, enum.Enum):
    credit = "credit"
    lounge = "lounge"
    points = "points"
    experience = "experience"


class ReminderStatus(str, enum.Enum):
    pending = "pending"
    done = "done"
    dismissed = "dismissed"


class Recurring(str, enum.Enum):
    none = "none"
    yearly = "yearly"
    monthly = "monthly"


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Cardholder(Base, TimestampMixin):
    __tablename__ = "cardholders"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    color_tag = Column(String, nullable=False, default="#3b82f6")

    cards = relationship("Card", back_populates="cardholder", cascade="all, delete-orphan")


class Card(Base, TimestampMixin):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True)
    cardholder_id = Column(Integer, ForeignKey("cardholders.id"), nullable=False)
    issuer = Column(SAEnum(Issuer), nullable=False)
    name = Column(String, nullable=False)
    opened_date = Column(Date, nullable=False)
    annual_fee = Column(Float, nullable=False, default=0.0)
    fee_waived_first_year = Column(Boolean, nullable=False, default=False)
    status = Column(SAEnum(CardStatus), nullable=False, default=CardStatus.active)
    next_fee_date = Column(Date, nullable=False)
    can_close_after_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)

    cardholder = relationship("Cardholder", back_populates="cards")
    benefits = relationship("Benefit", back_populates="card", cascade="all, delete-orphan")
    sub = relationship("SignUpBonus", back_populates="card", cascade="all, delete-orphan", uselist=False)
    reminders = relationship("Reminder", back_populates="card", cascade="all, delete-orphan")


class Benefit(Base, TimestampMixin):
    __tablename__ = "benefits"

    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    frequency = Column(SAEnum(Frequency), nullable=False)
    cycle_type = Column(SAEnum(CycleType), nullable=False)
    category = Column(SAEnum(Category), nullable=False, default=Category.credit)
    notes = Column(Text, nullable=True)

    card = relationship("Card", back_populates="benefits")
    progress = relationship("BenefitProgress", back_populates="benefit", cascade="all, delete-orphan")


class BenefitProgress(Base, TimestampMixin):
    __tablename__ = "benefit_progress"

    id = Column(Integer, primary_key=True)
    benefit_id = Column(Integer, ForeignKey("benefits.id"), nullable=False)
    period = Column(String, nullable=False)
    claimed_amount = Column(Float, nullable=False, default=0.0)
    claimed_date = Column(Date, nullable=False, default=date.today)
    claimed_by = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    benefit = relationship("Benefit", back_populates="progress")


class SignUpBonus(Base, TimestampMixin):
    __tablename__ = "sign_up_bonuses"

    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False)
    required_spend = Column(Float, nullable=False)
    deadline_date = Column(Date, nullable=False)
    reward_description = Column(String, nullable=False)
    current_spend = Column(Float, nullable=False, default=0.0)
    completed = Column(Boolean, nullable=False, default=False)

    card = relationship("Card", back_populates="sub")


class Reminder(Base, TimestampMixin):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=True)
    title = Column(String, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(SAEnum(ReminderStatus), nullable=False, default=ReminderStatus.pending)
    recurring = Column(SAEnum(Recurring), nullable=False, default=Recurring.none)

    card = relationship("Card", back_populates="reminders")
