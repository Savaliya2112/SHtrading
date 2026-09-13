NASDAQ100_FALLBACK = [
"ADBE","AMD","ABNB","ALNY","AMAT","APP","ARM","ASML","AVGO","AXON",
"BKNG","BKR","CCEP","CDNS","CEG","CHTR","CMCSA","COST","CPRT","CRWD",
"CSCO","CSGP","CSX","CTAS","CTSH","DASH","DDOG","DXCM","EA","EXC",
"FANG","FAST","FER","FTNT","GEHC","GILD","GOOG","GOOGL","HON","IDXX",
"INSM","INTC","INTU","ISRG","KDP","KHC","KLAC","LIN","LRCX","MAR",
"MCHP","MDB","MDLZ","MELI","META","MNST","MPWR","MRVL","MSFT","MSTR",
"MU","NFLX","NVDA","NXPI","ODFL","ON","ORLY","PANW","PAYX","PCAR",
"PDD","PEP","PLTR","PYPL","QCOM","REGN","ROP","ROST","SBUX","SHOP",
"SNPS","TEAM","TMUS","TRGP","TSLA","TTWO","TXN","VRSK","VRTX","WBD",
"WDAY","WDC","WMT","XEL","ZS"
]

JAPAN_INDEXES = ["^N225", "^TOPX"]
INDEX_FUNDS = ["QQQ", "QQQM", "VOO", "VTI", "SPY", "DIA", "IWM", "EFA", "EEM"]

def get_nasdaq100():
    try:
        import pandas as pd
        tables = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")
        for t in tables:
            cols = {str(c).lower(): c for c in t.columns}
            ticker_col = next((c for k,c in cols.items() if "ticker" in k or "symbol" in k), None)
            if ticker_col:
                vals = [str(x).replace(".", "-").strip() for x in t[ticker_col].dropna()]
                if len(vals) >= 80:
                    return sorted(set(vals))
    except Exception:
        pass
    return NASDAQ100_FALLBACK.copy()

def all_symbols():
    return get_nasdaq100() + JAPAN_INDEXES + INDEX_FUNDS
