from risk import build_risk_plan


def test_invalid_account_returns_zero_quantity():
    plan = build_risk_plan(
        entry=100,
        stop=95,
        account_eur=0,
        risk_pct=1.0,
        max_notional_pct=25.0,
    )

    assert plan.quantity == 0


def test_invalid_risk_percentage_returns_zero_quantity():
    plan = build_risk_plan(
        entry=100,
        stop=95,
        account_eur=3000,
        risk_pct=0,
        max_notional_pct=25.0,
    )

    assert plan.quantity == 0


def test_invalid_entry_returns_zero_quantity():
    plan = build_risk_plan(
        entry=0,
        stop=95,
        account_eur=3000,
        risk_pct=1.0,
        max_notional_pct=25.0,
    )

    assert plan.quantity == 0
