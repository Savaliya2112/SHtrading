from risk import build_risk_plan


def test_position_size_respects_risk_and_notional_limits():
    plan = build_risk_plan(
        entry=100,
        stop=95,
        account_eur=3000,
        risk_pct=1.0,
        max_notional_pct=25.0,
    )

    assert plan.quantity == 6
    assert plan.risk_eur == 30.0
    assert plan.notional_eur == 600.0


def test_invalid_stop_returns_zero_quantity():
    plan = build_risk_plan(
        entry=100,
        stop=100,
        account_eur=3000,
        risk_pct=1.0,
        max_notional_pct=25.0,
    )

    assert plan.quantity == 0
