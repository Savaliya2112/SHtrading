import os

# ============================================================
# TELEGRAM
# ============================================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


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


# ============================================================
# MARKET DATA
# ============================================================

DAILY_PERIOD = os.getenv("DAILY_PERIOD", "1y")
INTRADAY_PERIOD = os.getenv("INTRADAY_PERIOD", "60d")


# ============================================================
# TIMEFRAMES
# ============================================================

INTRADAY_TIMEFRAMES = [
    "1h",
]

SWING_TIMEFRAME = "1d"


# ============================================================
# WATCHLIST
# ============================================================

WATCHLIST = [
    "NVDA",
    "AAPL",
    "MSFT",
    "AMZN",
    "META",
    "GOOGL",
    "TSLA",

    "SPY",
    "QQQ",

    "SAP.DE",
    "SIE.DE",
    "ALV.DE",

    "DAX",

    "^N225",
]


# ============================================================
# TECHNICAL INDICATORS
# ============================================================

SMA_FAST = int(os.getenv("SMA_FAST", "20"))
SMA_SLOW = int(os.getenv("SMA_SLOW", "50"))

EMA_FAST = int(os.getenv("EMA_FAST", "12"))
EMA_S
