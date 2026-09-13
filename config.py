import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Risk / signal settings
MIN_SCORE = int(os.getenv("MIN_SCORE", "5"))
MAX_ALERTS = int(os.getenv("MAX_ALERTS", "10"))
ALERT_COOLDOWN_MINUTES = int(os.getenv("ALERT_COOLDOWN_MINUTES", "240"))

# Data settings
DAILY_PERIOD = os.getenv("DAILY_PERIOD", "1y")
INTRADAY_PERIOD = os.getenv("INTRADAY_PERIOD", "60d")
INTERVALS = ("1d", "1h")

# Broad watchlist. The Nasdaq-100 is refreshed dynamically by scanner.py.
INDEX_TICKERS = [
    "^NDX", "^N225", "^TOPX",
    "QQQ", "QQQM", "SPY", "DIA", "IWM"
]

# Fallback list if Wikipedia cannot be reached.
NASDAQ100_FALLBACK = [
    "AAPL","ABNB","ADBE","ADI","ADP","ADSK","AEP","AMAT","AMD","AMGN",
    "AMZN","ANSS","APP","ARM","ASML","AVGO","AXON","AZN","BIIB","BKNG",
    "BKR","CCEP","CDNS","CDW","CEG","CHTR","CMCSA","COST","CPRT","CRWD",
    "CSCO","CSGP","CSX","CTAS","CTSH","DASH","DDOG","DXCM","EA","EXC",
    "FANG","FAST","FER","FTNT","GEHC","GFS","GILD","GOOG","GOOGL","HON",
    "IDXX","ILMN","INTC","INTU","ISRG","KDP","KHC","KLAC","LIN","LRCX",
    "LULU","MAR","MCHP","MDB","MDLZ","MELI","META","MNST","MRVL","MSFT",
    "MSTR","MU","NFLX","NVDA","NXPI","ODFL","ON","ORLY","PANW","PAYX",
    "PCAR","PDD","PEP","PLTR","PYPL","QCOM","REGN","ROP","ROST","SBUX",
    "SHOP","SNPS","TEAM","TMUS","TRGP","TSLA","TTD","TTWO","TXN","VRSK",
    "VRTX","WBD","WDAY","WDC","WMT","XEL","ZS"
]

WATCHLIST = NASDAQ100_FALLBACK + INDEX_TICKERS

NEWS_RESULTS = int(os.getenv("NEWS_RESULTS", "5"))
NEWS_MAX_AGE_HOURS = int(os.getenv("NEWS_MAX_AGE_HOURS", "48"))

STATE_FILE = os.getenv("STATE_FILE", "signal_state.json")
