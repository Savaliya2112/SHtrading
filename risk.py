"""
Risk management module.

This module calculates position size.
It does NOT place trades.
"""

from dataclasses import dataclass


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
    max_notional_pct=25.0,
):
    """
    Calculate position size based on:

    1. Maximum account risk.
    2. Maximum position notional.

    Example:

    Account = €3,000
    Risk = 1%
    Maximum risk = €30
    """

    if entry <= 0:
        return RiskPlan(
            0, 0, 0, 0, entry, stop
        )

    risk_per_share = abs(entry - stop)

    if risk_per_share <= 0:
        return RiskPlan(
            0, 0, 0, 0, entry, stop
        )

    risk_budget = (
        account_eur *
        risk_pct /
        100
    )

    max_notional = (
        account_eur *
        max_notional_pct /
        100
    )

    quantity_by_risk = int(
        risk_budget /
        risk_per_share
    )

    quantity_by_notional = int(
        max_notional /
        entry
    )

    quantity = min(
        quantity_by_risk,
        quantity_by_notional,
    )

    quantity = max(quantity, 0)

    risk_eur = (
        quantity *
        risk_per_share
    )

    notional_eur = (
        quantity *
        entry
    )

    return RiskPlan(
        quantity=quantity,
        risk_eur=round(risk_eur, 2),
        notional_eur=round(notional_eur, 2),
        risk_per_share=round(
            risk_per_share,
            4
        ),
        entry_price=round(entry, 4),
        stop_price=round(stop, 4),
    )
