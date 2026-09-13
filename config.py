from __future__ import annotations

import os


# ============================================================
# TELEGRAM
# ============================================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


# ============================================================
# SCANNING
# ============================================================

# Background monitor checks every 2 minutes.
SCAN_INTERVAL_MINUTES = 2

# Historical market-data period used by the scanner.
HISTORY_PERIOD = os.getenv(
    "HISTORY_PERIOD",
    "1y",
)

# Number of historical trading days considered
# for backward analysis.
LOOKBACK_DAYS = int(
    os.getenv(
        "LOOKBACK_DAYS",
        "120",
    )
)


# ============================================================
# SIGNAL SETTINGS
# ============================================================

# Minimum technical score required before
# a BUY signal can generate an alert.
MIN_SCORE = float(
    os.getenv(
        "MIN_SCORE",
        "3",
    )
)


# ============================================================
# RISK / POSITION INFORMATION
# ============================================================

# These values are used for analysis only.
# The bot does NOT place orders.

ACCOUNT_EUR = float(
    os.getenv(
        "ACCOUNT_EUR",
        "10000",
    )
)

RISK_PER_TRADE_PCT = float(
    os.getenv(
        "RISK_PER_TRADE_PCT",
        "1",
    )
)

MAX_NOTIONAL_PCT = float(
    os.getenv(
        "MAX_NOTIONAL_PCT",
        "20",
    )
)


# ============================================================
# ALERT SETTINGS
# ============================================================

# Prevent duplicate notifications for the same
# unchanged signal.
DEDUPLICATE_ALERTS = True

# Only send Telegram notifications for qualifying
# signals. The monitor continues running otherwise.
ALERT_ONLY = True


# ============================================================
# MARKET UNIVERSE
# ============================================================

# Nasdaq-100 + Japan indexes + selected index funds.
ENABLE_NASDAQ100 = True
ENABLE_JAPAN_INDEXES = True
ENABLE_INDEX_FUNDS = True


# ============================================================
# NEWS
# ============================================================

ENABLE_NEWS = True

# Maximum number of news items retrieved per symbol.
NEWS_LIMIT = int(
    os.getenv(
        "NEWS_LIMIT",
        "5",
    )
)


# ============================================================
# DATA PROVIDER
# ============================================================

# Timeout for market/news requests, in seconds.
REQUEST_TIMEOUT_SECONDS = int(
    os.getenv(
        "REQUEST_TIMEOUT_SECONDS",
        "15",
    )
)


# ============================================================
# SAFETY
# ============================================================

# Explicitly disable any broker/order functionality.
ENABLE_ORDER_EXECUTION = False
