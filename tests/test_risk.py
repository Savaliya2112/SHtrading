from risk import build_risk_plan
def test_risk():
    p=build_risk_plan(100,95,10000,1,20)
    assert p.risk_amount_eur==100
    assert p.quantity==20
