from __future__ import annotations
from indicators import add_indicators
from data_provider import download_history
from strategy import generate_signal
import config

def scan_symbol(symbol, period=None):
    try:
        df=download_history(symbol,period or config.HISTORY_PERIOD,"1d")
        if df.empty: return None
        ind=add_indicators(df)
        return generate_signal(symbol,ind,config.MIN_SCORE)
    except Exception:
        return None

def backward_scan(symbol, lookback_days=None):
    df=download_history(symbol,config.HISTORY_PERIOD,"1d")
    ind=add_indicators(df)
    if ind.empty: return []
    n=min(lookback_days or config.LOOKBACK_DAYS,len(ind))
    found=[]
    for i in range(max(0,len(ind)-n),len(ind)):
        window=ind.iloc[:i+1]
        s=generate_signal(symbol,window,config.MIN_SCORE)
        if s: found.append({"date":str(ind.index[i]),"signal":s})
    return found

def scan_universe(symbols):
    return [(s,scan_symbol(s)) for s in symbols]
