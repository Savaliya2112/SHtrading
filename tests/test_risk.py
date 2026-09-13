from risk import build_risk_plan

def test_position_size_respects_both_limits():
    p = build_risk_plan(100, 95, 10000, 1, 20)
    assert p.risk_amount_eur == 100
    assert p.notional_limit_eur == 2000
    assert p.quantity == 20

def test_invalid_input_is_safe():
    p = build_risk_plan(100, 100, 10000, 1, 20)
    assert p.quantity == 0
