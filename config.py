# ============================================================
# ACCOUNT / RISK
# ============================================================

ACCOUNT_BALANCE_EUR = float(
    os.getenv("ACCOUNT_BALANCE_EUR", "3000")
)

RISK_PER_TRADE_PCT = float(
    os.getenv("RISK_PER_TRADE_PCT", "1.0")
)

MAX_POSITION_PCT = float(
    os.getenv("MAX_POSITION_PCT", "25")
)

MAX_OPEN_POSITIONS = int(
    os.getenv("MAX_OPEN_POSITIONS", "5")
)

MAX_PORTFOLIO_EXPOSURE_PCT = float(
    os.getenv("MAX_PORTFOLIO_EXPOSURE_PCT", "60")
)

MAX_DAILY_LOSS_PCT = float(
    os.getenv("MAX_DAILY_LOSS_PCT", "3")
)
