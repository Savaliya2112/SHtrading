import os


# ============================================================
# TELEGRAM
# ============================================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


# ============================================================
# ACCOUNT / RISK
# ============================================================

ACCOUNT_BALANCE_EUR = float(os.getenv("ACCOUNT_BALANCE_EUR", "3000"))
RISK_PER_TRADE_PCT = float(os.getenv("RISK_PER_TRADE_PCT", "1.0"))
MAX_POSITION_PCT = float(os.getenv("MAX_POSITION_PCT", "25"))
MAX_OPEN_POSITIONS = int(os.getenv("MAX_OPEN_POSITIONS", "5"))


# ============================================================
# STRATEGY
# ============================================================

SMA_FAST = 20
SMA_SLOW = 50

EMA_FAST = 9
EMA_SLOW = 21

RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

BB_PERIOD = 20
BB_STD = 2.0

ATR_PERIOD = 14
ATR_STOP_MULTIPLIER = 1.5

REWARD_RISK_RATIO = 2.0
MIN_STOP_PCT = 0.005

VOLUME_LOOKBACK = 20
VOLUME_SPIKE_MULTIPLIER = 1.5

MIN_SIGNAL_SCORE = 4


# ============================================================
# TRANSACTION COST
# ============================================================

TRANSACTION_COST_PCT = 0.05


# ============================================================
# MARKETS
# ============================================================

US_STOCKS = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "META",
    "GOOGL",
    "TSLA",
    "AMD",
    "NFLX",
    "AVGO",
    "JPM",
    "XOM",
]

EUROPE_STOCKS = [
    "SAP.DE",
    "SIE.DE",
    "AIR.PA",
    "OR.PA",
    "MC.PA",
    "ASML.AS",
]

# Japan = indexes only
JAPAN_INDEXES = [
    "^N225",
    "^TOPX",
]

WATCHLIST = (
    US_STOCKS
    + EUROPE_STOCKS
    + JAPAN_INDEXES
)


# ============================================================
# TIMEFRAMES
# ============================================================

INTRADAY_TIMEFRAMES = [
    "15m",
]

SWING_TIMEFRAME = "1d"


# ============================================================
# DATA PERIODS
# ============================================================

INTRADAY_PERIOD = "30d"
DAILY_PERIOD = "2y"


# ============================================================
# ALERTS
# ============================================================

MAX_ALERTS = 10


# ============================================================
# NEWS
# ============================================================

NEWS_RESULTS = 8
NEWS_PER_TICKER = 2


# ============================================================
# AI
# ============================================================

AI_ENABLED = False
