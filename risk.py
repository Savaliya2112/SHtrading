from dataclasses import dataclass

@dataclass(frozen=True)
class RiskPlan:
    entry: float
    stop: float
    account_eur: float
    risk_pct: float
    max_notional_pct: float
    risk_amount_eur: float
    notional_limit_eur: float
    quantity: int

def build_risk_plan(entry, stop, account_eur, risk_pct, max_notional_pct):
    try:
        e, s, a, r, m = map(float, (entry, stop, account_eur, risk_pct, max_notional_pct))
    except (TypeError, ValueError):
        return RiskPlan(0, 0, 0, 0, 0, 0, 0, 0)
    if e <= 0 or a <= 0 or r <= 0 or m <= 0 or e == s:
        return RiskPlan(e, s, a, r, m, 0.0, 0.0, 0)
    risk_amount = a * r / 100.0
    notional_limit = a * m / 100.0
    per_unit_risk = abs(e - s)
    by_risk = int(risk_amount / per_unit_risk)
    by_notional = int(notional_limit / e)
    quantity = max(0, min(by_risk, by_notional))
    return RiskPlan(e, s, a, r, m, risk_amount, notional_limit, quantity)

def calculate_position_size(entry, stop, account_eur, risk_pct=1.0, max_notional_pct=20.0):
    return build_risk_plan(entry, stop, account_eur, risk_pct, max_notional_pct)
