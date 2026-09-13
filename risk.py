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
    max_notional_pct=None,
    max_position_pct=None,
):
    """
    Calculate a position size from account risk
    and maximum position exposure.

    max_notional_pct is the primary parameter used
    by the existing test suite.

    max_position_pct is retained as a compatibility
    alias for the bot/configuration code.
    """

    entry = float(entry)
    stop = float(stop)
    account_eur = float(account_eur)
    risk_pct = float(risk_pct)

    if max_notional_pct is None:
        max_notional_pct = max_position_pct

    if max_notional_pct is None:
        max_notional_pct = 25.0

    max_notional_pct = float(
        max_notional_pct
    )

    risk_per_share = abs(
        entry - stop
    )

    # --------------------------------------------------------
    # Validate inputs
    # --------------------------------------------------------

    if entry <= 0:
        return RiskPlan(
            0,
            0.0,
            0.0,
            risk_per_share,
            entry,
            stop,
        )

    if stop <= 0:
        return RiskPlan(
            0,
            0.0,
            0.0,
            risk_per_share,
            entry,
            stop,
        )

    if account_eur <= 0:
        return RiskPlan(
            0,
            0.0,
            0.0,
            risk_per_share,
            entry,
            stop,
        )

    if risk_pct <= 0:
        return RiskPlan(
            0,
            0.0,
            0.0,
            risk_per_share,
            entry,
            stop,
        )

    if max_notional_pct <= 0:
        return RiskPlan(
            0,
            0.0,
            0.0,
            risk_per_share,
            entry,
            stop,
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

    # --------------------------------------------------------
    # Risk budget
    # --------------------------------------------------------

    risk_budget = (
        account_eur
        * risk_pct
        / 100.0
    )

    # --------------------------------------------------------
    # Maximum position value
    # --------------------------------------------------------

    max_notional = (
        account_eur
        * max_notional_pct
        / 100.0
    )

    # --------------------------------------------------------
    # Quantity limits
    # --------------------------------------------------------

    quantity_by_risk = math.floor(
        risk_budget
        / risk_per_share
    )

    quantity_by_notional = math.floor(
        max_notional
        / entry
    )

    quantity = max(
        0,
        min(
            quantity_by_risk,
            quantity_by_notional,
        ),
    )

    # --------------------------------------------------------
    # Final values
    # --------------------------------------------------------

    risk_eur = (
        quantity
        * risk_per_share
    )

    notional_eur = (
        quantity
        * entry
    )

    return RiskPlan(
        quantity=quantity,
        risk_eur=round(
            risk_eur,
            2,
        ),
        notional_eur=round(
            notional_eur,
            2,
        ),
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
