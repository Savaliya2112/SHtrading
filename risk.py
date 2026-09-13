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
    max_notional_pct,
    max_position_pct=None,
):
    """
    Calculate a conservative position size.

    The function supports max_notional_pct because this is
    the interface used by the repository test suite.

    max_position_pct is retained as a compatibility alias.
    """

    try:
        entry = float(entry)
        stop = float(stop)
        account_eur = float(account_eur)
        risk_pct = float(risk_pct)
        max_notional_pct = float(max_notional_pct)
    except (TypeError, ValueError):
        return RiskPlan(
            quantity=0,
            risk_eur=0.0,
            notional_eur=0.0,
            risk_per_share=0.0,
            entry_price=0.0,
            stop_price=0.0,
        )

    if entry <= 0:
        return RiskPlan(
            0, 0.0, 0.0, 0.0, entry, stop
        )

    if stop <= 0:
        return RiskPlan(
            0,
            0.0,
            0.0,
            abs(entry - stop),
            entry,
            stop,
        )

    if account_eur <= 0:
        return RiskPlan(
            0,
            0.0,
            0.0,
            abs(entry - stop),
            entry,
            stop,
        )

    if risk_pct <= 0:
        return RiskPlan(
            0,
            0.0,
            0.0,
            abs(entry - stop),
            entry,
            stop,
        )

    if max_notional_pct <= 0:
        return RiskPlan(
            0,
            0.0,
            0.0,
            abs(entry - stop),
            entry,
            stop,
        )

    risk_per_share = abs(
        entry - stop
    )

    if risk_per_share <= 0:
        return RiskPlan(
            0,
            0.0,
            0.0,
            0.0,
            entry,
            stop,
        )

    risk_budget = (
        account_eur
        * risk_pct
        / 100.0
    )

    max_notional = (
        account_eur
        * max_notional_pct
        / 100.0
    )

    quantity_by_risk = math.floor(
        risk_budget / risk_per_share
    )

    quantity_by_notional = math.floor(
        max_notional / entry
    )

    quantity = max(
        0,
        min(
            quantity_by_risk,
            quantity_by_notional,
        ),
    )

    risk_eur = (
        quantity * risk_per_share
    )

    notional_eur = (
        quantity * entry
    )

    return RiskPlan(
        quantity=quantity,
        risk_eur=round(risk_eur, 2),
        notional_eur=round(notional_eur, 2),
        risk_per_share=round(
            risk_per_share,
            4,
        ),
        entry_price=round(
            entry,
            4,
        ),
        stop_price=round(
            stop,
            4,
        ),
    )
