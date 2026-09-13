import os

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

DAILY_PERIOD = os.getenv(
    "DAILY_PERIOD",
    "1y"
)

INTRADAY_PERIOD = os.getenv(
    "INTRADAY_PERIOD",
    "60d"
)


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
    # United States
    "NVDA",
    "AAPL",
    "MSFT",
    "AMZN",
    "META",
    "GOOGL",
    "TSLA",

    # Major US indices / ETFs
    "SPY",
    "QQQ",

    # Germany / Europe
    "SAP.DE",
    "SIE.DE",
    "ALV.DE",
    "DAX",

    # Japan
    "^N225",
]


# ============================================================
# TECHNICAL INDICATORS
# ============================================================

SMA_FAST = int(
    os.getenv("SMA_FAST", "20")
)

SMA_SLOW = int(
    os.getenv("SMA_SLOW", "50")
)

EMA_FAST = int(
    os.getenv("EMA_FAST", "12")
)

EMA_SLOW = int(
    os.getenv("EMA_SLOW", "26")
)

RSI_PERIOD = int(
    os.getenv("RSI_PERIOD", "14")
)

MACD_FAST = int(
    os.getenv("MACD_FAST", "12")
)

MACD_SLOW = int(
    os.getenv("MACD_SLOW", "26")
)

MACD_SIGNAL = int(
    os.getenv("MACD_SIGNAL", "9")
)

BB_PERIOD = int(
    os.getenv("BB_PERIOD", "20")
)

BB_STD = float(
    os.getenv("BB_STD", "2")
)

ATR_PERIOD = int(
    os.getenv("ATR_PERIOD", "14")
)

VOLUME_LOOKBACK = int(
    os.getenv("VOLUME_LOOKBACK", "20")
)


# ============================================================
# STRATEGY
# ============================================================

MIN_SIGNAL_SCORE = int(
    os.getenv("MIN_SIGNAL_SCORE", "4")
)

VOLUME_SPIKE_MULTIPLIER = float(
    os.getenv("VOLUME_SPIKE_MULTIPLIER", "1.5")
)

ATR_STOP_MULTIPLIER = float(
    os.getenv("ATR_STOP_MULTIPLIER", "1.5")
)

MIN_STOP_PCT = float(
    os.getenv("MIN_STOP_PCT", "0.01")
)

REWARD_RISK_RATIO = float(
    os.getenv("REWARD_RISK_RATIO", "2.0")
)
