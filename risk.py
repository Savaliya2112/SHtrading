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
        e,s,a,r,m=map(float,(entry,stop,account_eur,risk_pct,max_notional_pct))
    except (TypeError,ValueError):
        return RiskPlan(0,0,0,0,0,0,0,0)
    if e<=0 or a<=0 or r<=0 or m<=0 or e==s:
        return RiskPlan(e,s,a,r,m,0,0,0)
    risk_amount=a*r/100
    notional=a*m/100
    quantity=max(0,min(int(risk_amount/abs(e-s)),int(notional/e)))
    return RiskPlan(e,s,a,r,m,risk_amount,notional,quantity)

def calculate_position_size(entry,stop,account_eur,risk_pct=1,max_notional_pct=20):
    return build_risk_plan(entry,stop,account_eur,risk_pct,max_notional_pct)
