import os


# ============================================================
# TELEGRAM
# ============================================================

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
)

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
)


# ============================================================
# ACCOUNT / RISK
# ============================================================

ACCOUNT_BALANCE_EUR = float(
    os.getenv(
        "ACCOUNT_BALANCE_EUR",
        "3000",
    )
)

RISK_PER_TRADE_PCT = float(
    os.getenv(
        "RISK_PER_TRADE_PCT",
        "1.0",
    )
)

MAX_NOTIONAL_PCT = float(
    os.getenv(
        "MAX_NOTIONAL_PCT",
        "25",
    )
)

# Compatibility with existing code
MAX_POSITION_PCT = MAX_NOTIONAL_PCT

MAX_OPEN_POSITIONS = int(
    os.getenv(
        "MAX_OPEN_POSITIONS",
        "5",
    )
)

MAX_PORTFOLIO_EXPOSURE_PCT = float(
    os.getenv(
        "MAX_PORTFOLIO_EXPOSURE_PCT",
        "60",
    )
)

MAX_DAILY_LOSS_PCT = float(
    os.getenv(
        "MAX_DAILY_LOSS_PCT",
        "3",
    )
)


# ============================================================
# MARKET DATA
# ============================================================

DAILY_PERIOD = os.getenv(
    "DAILY_PERIOD",
    "1y",
)

INTRADAY_PERIOD = os.getenv(
    "INTRADAY_PERIOD",
    "60d",
)


# ============================================================
# TIMEFRAMES
# ============================================================

INTRADAY_TIMEFRAMES = [
    "1h",
]

SWING_TIMEFRAME = "1d"


# ============================================================
# INDEX / ETF UNIVERSE
# ============================================================

INDEX_WATCHLIST = [
    # Nasdaq / US
    "QQQ",
    "SPY",
    "DIA",
    "IWM",
    "MDY",
    "VTI",
    "RSP",

    # International
    "EFA",
    "IEMG",
    "FEZ",

    # Germany
    "^GDAXI",

    # Japan
    "^N225",
]


# ============================================================
# IMPORTANT STOCKS
# ============================================================

CORE_STOCKS = [
    "NVDA",
    "AAPL",
    "MSFT",
    "AMZN",
    "META",
    "GOOGL",
    "GOOG",
    "AVGO",
    "TSLA",
    "AMD",
    "NFLX",
    "COST",
    "QCOM",
    "INTC",
    "MU",
]


# ============================================================
# NASDAQ-100
#
# The scanner can use this list directly.
# We will make the final data-provider version capable of
# refreshing the constituent list instead of relying forever
# on a manually maintained list.
# ============================================================

NASDAQ_100 = [
    "ADBE",
    "ADI",
    "ADP",
    "ADSK",
    "AEP",
    "AMAT",
    "AMD",
    "AMGN",
    "AMZN",
    "ANSS",
    "APP",
    "ARM",
    "ASML",
    "AVGO",
    "AXON",
    "BKNG",
    "BKR",
    "CDNS",
    "CDW",
    "CEG",
    "CHTR",
    "CMCSA",
    "COST",
    "CPRT",
    "CRWD",
    "CSCO",
    "CSGP",
    "CSX",
    "CTAS",
    "CTSH",
    "DASH",
    "DDOG",
    "DXCM",
    "EA",
    "EXC",
    "FANG",
    "FAST",
    "FER",
    "FTNT",
    "GEHC",
    "GILD",
    "GOOG",
    "GOOGL",
    "HON",
    "IDXX",
    "ILMN",
    "INTC",
    "INTU",
    "ISRG",
    "KDP",
    "KHC",
    "KLAC",
    "LIN",
    "LRCX",
    "MAR",
    "MCHP",
    "MDLZ",
    "MELI",
    "META",
    "MNST",
    "MRVL",
    "MSFT",
    "MSTR",
    "MU",
    "NFLX",
    "NVDA",
    "NXPI",
    "ODFL",
    "ORLY",
    "PANW",
    "PAYX",
    "PCAR",
    "PDD",
    "PEP",
    "PLTR",
    "PYPL",
    "QCOM",
    "REGN",
    "ROP",
    "ROST",
    "SBUX",
    "SHOP",
    "SNPS",
    "TEAM",
    "TMUS",
    "TSLA",
    "TTWO",
    "TXN",
    "VRSK",
    "VRTX",
    "WBD",
    "WDAY",
    "WDC",
    "WMT",
    "XEL",
    "ZS",
]


# ============================================================
# COMPLETE SCANNER UNIVERSE
# ============================================================

WATCHLIST = list(
    dict.fromkeys(
        NASDAQ_100
        + CORE_STOCKS
        + INDEX_WATCHLIST
    )
)


# ============================================================
# TECHNICAL INDICATORS
# ============================================================

SMA_FAST = int(
    os.getenv(
        "SMA_FAST",
        "20",
    )
)

SMA_SLOW = int(
    os.getenv(
        "SMA_SLOW",
        "50",
    )
)

EMA_FAST = int(
    os.getenv(
        "EMA_FAST",
        "12",
    )
)

EMA_SLOW = int(
    os.getenv(
        "EMA_SLOW",
        "26",
    )
)

RSI_PERIOD = int(
    os.getenv(
        "RSI_PERIOD",
        "14",
    )
)

MACD_FAST = int(
    os.getenv(
        "MACD_FAST",
        "12",
    )
)

MACD_SLOW = int(
    os.getenv(
        "MACD_SLOW",
        "26",
    )
)

MACD_SIGNAL = int(
    os.getenv(
        "MACD_SIGNAL",
        "9",
    )
)

BB_PERIOD = int(
    os.getenv(
        "BB_PERIOD",
        "20",
    )
)

BB_STD = float(
    os.getenv(
        "BB_STD",
        "2",
    )
)

ATR_PERIOD = int(
    os.getenv(
        "ATR_PERIOD",
        "14",
    )
)

VOLUME_LOOKBACK = int(
    os.getenv(
        "VOLUME_LOOKBACK",
        "20",
    )
)


# ============================================================
# STRATEGY
# ============================================================

MIN_SIGNAL_SCORE = int(
    os.getenv(
        "MIN_SIGNAL_SCORE",
        "4",
    )
)

VOLUME_SPIKE_MULTIPLIER = float(
    os.getenv(
        "VOLUME_SPIKE_MULTIPLIER",
        "1.5",
    )
)

ATR_STOP_MULTIPLIER = float(
    os.getenv(
        "ATR_STOP_MULTIPLIER",
        "1.5",
    )
)

MIN_STOP_PCT = float(
    os.getenv(
        "MIN_STOP_PCT",
        "0.01",
    )
)

REWARD_RISK_RATIO = float(
    os.getenv(
        "REWARD_RISK_RATIO",
        "2.0",
    )
)


# ============================================================
# ALERT SYSTEM
# ============================================================

MAX_ALERTS = int(
    os.getenv(
        "MAX_ALERTS",
        "15",
    )
)

NEWS_RESULTS = int(
    os.getenv(
        "NEWS_RESULTS",
        "5",
    )
)

NEWS_PER_TICKER = int(
    os.getenv(
        "NEWS_PER_TICKER",
        "2",
    )
)

# Prevent repeated alerts for the same setup
ALERT_COOLDOWN_MINUTES = int(
    os.getenv(
        "ALERT_COOLDOWN_MINUTES",
        "60",
    )
)


# ============================================================
# BACKTESTING
# ============================================================

TRANSACTION_COST_PCT = float(
    os.getenv(
        "TRANSACTION_COST_PCT",
        "0.10",
    )
)


# ============================================================
# GENERAL
# ============================================================

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO",
)

REQUEST_TIMEOUT = int(
    os.getenv(
        "REQUEST_TIMEOUT",
        "30",
    )
)
