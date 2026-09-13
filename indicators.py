from __future__ import annotations

import numpy as np
import pandas as pd


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()

    close = x["Close"]
    high = x["High"]
    low = x["Low"]
    volume = x["Volume"]

    x["SMA20"] = close.rolling(20).mean()
    x["SMA50"] = close.rolling(50).mean()
    x["EMA20"] = close.ewm(span=20, adjust=False).mean()
    x["EMA50"] = close.ewm(span=50, adjust=False).mean()

    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    x["RSI14"] = 100 - (100 / (1 + rs))

    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    x["ATR14"] = tr.rolling(14).mean()

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    x["MACD"] = ema12 - ema26
    x["MACD_SIGNAL"] = x["MACD"].ewm(span=9, adjust=False).mean()

    x["VOL20"] = volume.rolling(20).mean()
    x["VOL_RATIO"] = volume / x["VOL20"]

    x["RET20"] = close.pct_change(20)
    x["HIGH20"] = high.rolling(20).max()
    x["LOW20"] = low.rolling(20).min()

    return x.dropna().copy()
