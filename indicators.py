from __future__ import annotations
import numpy as np
import pandas as pd

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    x = df.copy()
    if isinstance(x.columns, pd.MultiIndex):
        x.columns = x.columns.get_level_values(0)
    close, high, low, volume = x["Close"], x["High"], x["Low"], x["Volume"]
    x["SMA20"] = close.rolling(20).mean()
    x["SMA50"] = close.rolling(50).mean()
    x["EMA20"] = close.ewm(span=20, adjust=False).mean()
    x["EMA50"] = close.ewm(span=50, adjust=False).mean()

    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    x["RSI14"] = 100 - (100 / (1 + rs))
    x.loc[(loss == 0) & gain.notna(), "RSI14"] = 100.0

    prev = close.shift(1)
    tr = pd.concat([(high-low), (high-prev).abs(), (low-prev).abs()], axis=1).max(axis=1)
    x["ATR14"] = tr.rolling(14).mean()

    e12 = close.ewm(span=12, adjust=False).mean()
    e26 = close.ewm(span=26, adjust=False).mean()
    x["MACD"] = e12-e26
    x["MACD_SIGNAL"] = x["MACD"].ewm(span=9, adjust=False).mean()
    x["MACD_HIST"] = x["MACD"]-x["MACD_SIGNAL"]

    x["VOL20"] = volume.rolling(20).mean()
    x["VOL_RATIO"] = volume/x["VOL20"]
    x["RET20"] = close.pct_change(20)
    x["HIGH20"] = high.rolling(20).max()
    x["LOW20"] = low.rolling(20).min()

    for a,b in {
        "sma_fast":"SMA20","sma_slow":"SMA50","ema_fast":"EMA20","ema_slow":"EMA50",
        "rsi":"RSI14","macd":"MACD","macd_signal":"MACD_SIGNAL",
        "macd_hist":"MACD_HIST","atr":"ATR14","vol_ratio":"VOL_RATIO"
    }.items():
        x[a]=x[b]
    x["bb_mid"]=close.rolling(20).mean()
    std=close.rolling(20).std(ddof=0)
    x["bb_upper"]=x["bb_mid"]+2*std
    x["bb_lower"]=x["bb_mid"]-2*std
    return x.dropna().copy()

def compute_all_indicators(df: pd.DataFrame, config=None) -> pd.DataFrame:
    return add_indicators(df)
