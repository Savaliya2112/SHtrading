from __future__ import annotations

import numpy as np
import pandas as pd


def compute_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    data = df.copy()

    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in required if c not in data.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    close = pd.to_numeric(data["Close"], errors="coerce")
    high = pd.to_numeric(data["High"], errors="coerce")
    low = pd.to_numeric(data["Low"], errors="coerce")
    volume = pd.to_numeric(data["Volume"], errors="coerce")

    # Moving averages
    data["SMA20"] = close.rolling(20).mean()
    data["SMA50"] = close.rolling(50).mean()

    # RSI 14
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    data["RSI14"] = 100 - (100 / (1 + rs))

    # Keep compatibility with strategy.py
    data["RSI"] = data["RSI14"]

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()

    data["MACD"] = ema12 - ema26
    data["MACD_SIGNAL"] = data["MACD"].ewm(
        span=9,
        adjust=False
    ).mean()

    data["MACD_HIST"] = (
        data["MACD"] - data["MACD_SIGNAL"]
    )

    # ATR 14
    previous_close = close.shift(1)

    tr = pd.concat(
        [
            high - low,
            (high - previous_close).abs(),
            (low - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    data["ATR14"] = tr.rolling(14).mean()

    # Keep compatibility with strategy.py
    data["ATR"] = data["ATR14"]

    # Average volume
    data["Volume_SMA20"] = volume.rolling(20).mean()

    return data


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compatibility wrapper used by scanner.py.
    """
    return compute_all_indicators(df)
