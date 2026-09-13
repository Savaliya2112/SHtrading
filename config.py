import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
MIN_SCORE = float(os.getenv("MIN_SCORE", "3"))
ACCOUNT_EUR = float(os.getenv("ACCOUNT_EUR", "10000"))
RISK_PER_TRADE_PCT = float(os.getenv("RISK_PER_TRADE_PCT", "1"))
MAX_NOTIONAL_PCT = float(os.getenv("MAX_NOTIONAL_PCT", "20"))
HISTORY_PERIOD = os.getenv("HISTORY_PERIOD", "1y")
SCAN_INTERVAL_MINUTES = int(os.getenv("SCAN_INTERVAL_MINUTES", "60"))
LOOKBACK_DAYS = int(os.getenv("LOOKBACK_DAYS", "120"))
