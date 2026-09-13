from dataclasses import dataclass
import math


@dataclass
class RiskPlan:
    quantity: int
    risk_eur: float
    notional_eur: float
    risk_per_share: float
    entry_price: float
    stop_price: float


def build_risk_plan(
    entry,
    stop,
    account_eur,
    risk_pct,
    max_position_pct,
):
    entry = float(entry)
    stop = float(stop)
    account_eur = float(account_eur)
    risk_pct = float(risk_pct)
    max_position_pct = float(max_position_pct)

    risk_per_share = abs(entry - stop)

    # Invalid inputs
    if entry <= 0:
        return RiskPlan(
            0, 0.0, 0.0, risk_per_share, entry, stop
        )

    if stop <= 0:
        return RiskPlan(
            0, 0.0, 0.0, risk_per_share, entry, stop
        )

    if account_eur <= 0:
        return RiskPlan(
            0, 0.0, 0.0, risk_per_share, entry, stop
        )

    if risk_pct <= 0:
        return RiskPlan(
            0, 0.0, 0.0, risk_per_share, entry, stop
        )

    if max_position_pct <= 0:
        return RiskPlan(
            0, 0.0, 0.0, risk_per_share, entry, stop
        )

    if risk_per_share <= 0:
        return RiskPlan(
            0, 0.0, 0.0, 0.0, entry, stop
        )

    # Maximum amount we are allowed to lose
    risk_budget = (
        account_eur * risk_pct / 100.0
    )

    # Maximum position value
    max_notional = (
        account_eur * max_position_pct / 100.0
    )

    # Position size based on risk
    quantity_by_risk = math.floor(
        risk_budget / risk_per_share
    )

    # Position size based on maximum position value
    quantity_by_notional = math.floor(
        max_notional / entry
    )

    # Use the more conservative limit
    quantity = max(
        0,
        min(
            quantity_by_risk,
            quantity_by_notional,
        ),
    )

    risk_eur = quantity * risk_per_share
    notional_eur = quantity * entry

    return RiskPlan(
        quantity=quantity,
        risk_eur=round(risk_eur, 2),
        notional_eur=round(notional_eur, 2),
        risk_per_share=round(risk_per_share, 4),
        entry_price=round(entry, 4),
        stop_price=round(stop, 4),
    )
