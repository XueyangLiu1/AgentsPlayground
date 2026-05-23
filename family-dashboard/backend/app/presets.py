"""Card presets for Chase / Amex. Amounts approximate; user can adjust."""

from .schemas import PresetCard, PresetBenefit
from .models import Issuer, Frequency, CycleType, Category


PRESETS: list[PresetCard] = [
    # Chase
    PresetCard(
        issuer=Issuer.Chase,
        name="Sapphire Reserve",
        annual_fee=550.0,
        benefits=[
            PresetBenefit(name="Annual Travel Credit", amount=300.0,
                          frequency=Frequency.yearly, cycle_type=CycleType.anniversary_year,
                          category=Category.credit, notes="Auto-applied to travel charges"),
            PresetBenefit(name="DoorDash DashPass", amount=120.0,
                          frequency=Frequency.yearly, cycle_type=CycleType.calendar_year,
                          category=Category.credit, notes="Activate via Chase"),
            PresetBenefit(name="Priority Pass Lounge", amount=0.0,
                          frequency=Frequency.yearly, cycle_type=CycleType.anniversary_year,
                          category=Category.lounge),
        ],
    ),
    PresetCard(
        issuer=Issuer.Chase,
        name="Sapphire Preferred",
        annual_fee=95.0,
        benefits=[
            PresetBenefit(name="$50 Hotel Credit", amount=50.0,
                          frequency=Frequency.yearly, cycle_type=CycleType.anniversary_year,
                          category=Category.credit),
            PresetBenefit(name="10% Anniversary Points Bonus", amount=0.0,
                          frequency=Frequency.yearly, cycle_type=CycleType.anniversary_year,
                          category=Category.points),
        ],
    ),
    PresetCard(
        issuer=Issuer.Chase,
        name="Freedom Unlimited",
        annual_fee=0.0,
        benefits=[],
    ),
    PresetCard(
        issuer=Issuer.Chase,
        name="Ink Business Preferred",
        annual_fee=95.0,
        benefits=[],
    ),
    # Amex
    PresetCard(
        issuer=Issuer.Amex,
        name="Platinum",
        annual_fee=695.0,
        benefits=[
            PresetBenefit(name="Uber Cash", amount=15.0,
                          frequency=Frequency.monthly, cycle_type=CycleType.statement_month,
                          category=Category.credit, notes="$35 in December"),
            PresetBenefit(name="Digital Entertainment Credit", amount=20.0,
                          frequency=Frequency.monthly, cycle_type=CycleType.statement_month,
                          category=Category.credit, notes="NYT, Disney+, etc."),
            PresetBenefit(name="Saks Credit", amount=50.0,
                          frequency=Frequency.monthly, cycle_type=CycleType.statement_month,
                          category=Category.credit, notes="Jan-Jun / Jul-Dec halves"),
            PresetBenefit(name="Airline Fee Credit", amount=200.0,
                          frequency=Frequency.yearly, cycle_type=CycleType.calendar_year,
                          category=Category.credit),
            PresetBenefit(name="Hotel Credit (FHR/THC)", amount=200.0,
                          frequency=Frequency.yearly, cycle_type=CycleType.calendar_year,
                          category=Category.credit),
            PresetBenefit(name="Centurion Lounge Access", amount=0.0,
                          frequency=Frequency.yearly, cycle_type=CycleType.calendar_year,
                          category=Category.lounge),
            # TODO: refine actual current amounts; some terms changed in 2025+
        ],
    ),
    PresetCard(
        issuer=Issuer.Amex,
        name="Gold",
        annual_fee=325.0,
        benefits=[
            PresetBenefit(name="Dining Credit", amount=10.0,
                          frequency=Frequency.monthly, cycle_type=CycleType.statement_month,
                          category=Category.credit, notes="Grubhub, Cheesecake Factory, etc."),
            PresetBenefit(name="Uber Cash", amount=10.0,
                          frequency=Frequency.monthly, cycle_type=CycleType.statement_month,
                          category=Category.credit),
            PresetBenefit(name="Resy Credit", amount=50.0,
                          frequency=Frequency.monthly, cycle_type=CycleType.statement_month,
                          category=Category.credit, notes="Jan-Jun / Jul-Dec halves"),
            # TODO: confirm latest benefits
        ],
    ),
    PresetCard(
        issuer=Issuer.Amex,
        name="Green",
        annual_fee=150.0,
        benefits=[
            PresetBenefit(name="CLEAR Credit", amount=199.0,
                          frequency=Frequency.yearly, cycle_type=CycleType.calendar_year,
                          category=Category.credit),
            PresetBenefit(name="LoungeBuddy Credit", amount=100.0,
                          frequency=Frequency.yearly, cycle_type=CycleType.calendar_year,
                          category=Category.lounge),
        ],
    ),
    PresetCard(
        issuer=Issuer.Amex,
        name="Blue Cash Preferred",
        annual_fee=95.0,
        benefits=[
            PresetBenefit(name="Disney Bundle Credit", amount=7.0,
                          frequency=Frequency.monthly, cycle_type=CycleType.statement_month,
                          category=Category.credit),
        ],
    ),
]
