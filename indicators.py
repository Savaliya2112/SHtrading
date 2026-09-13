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
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    close = pd.to_numeric(
        data["Close"],
        errors="coerce",
    )

    high = pd.to_numeric(
        data["High"],
        errors="coerce",
    )

    low = pd.to_numeric(
        data["Low"],
        errors="coerce",
    )

    volume = pd.to_numeric(
        data["Volume"],
        errors="coerce",
    )

    # ========================================================
    # SMA
    # ========================================================

    data["SMA20"] = close.rolling(
        window=20,
        min_periods=20,
    ).mean()

    data["SMA50"] = close.rolling(
        window=50,
        min_periods=50,
    ).mean()

    # ========================================================
    # RSI 14
    # ========================================================

    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(
        window=14,
        min_periods=14,
    ).mean()

    avg_loss = loss.rolling(
        window=14,
        min_periods=14,
    ).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (
        100 / (1 + rs)
    )

    # No losses but gains exist = RSI 100
    rsi = rsi.mask(
        (avg_loss == 0) & (avg_gain > 0),
        100.0,
    )

    # No gains and no losses = neutral RSI
    rsi = rsi.mask(
        (avg_gain == 0) & (avg_loss == 0),
        50.0,
    )

    # Warm-up period: use neutral 50 rather than NaN.
    # This keeps the indicator defined for every row.
    rsi = rsi.fillna(50.0)

    data["RSI14"] = rsi.clip(
        lower=0,
        upper=100,
    )

    # Compatibility
    data["RSI"] = data["RSI14"]

    # ========================================================
    # MACD
    # ========================================================

    ema12 = close.ewm(
        span=12,
        adjust=False,
        min_periods=12,
    ).mean()

    ema26 = close.ewm(
        span=26,
        adjust=False,
        min_periods=26,
    ).mean()

    data["MACD"] = ema12 - ema26

    data["MACD_SIGNAL"] = data["MACD"].ewm(
        span=9,
        adjust=False,
        min_periods=9,
    ).mean()

    data["MACD_HIST"] = (
        data["MACD"]
        - data["MACD_SIGNAL"]
    )

    # ========================================================
    # ATR 14
    # ========================================================

    previous_close = close.shift(1)

    true_range = pd.concat(
        [
            high - low,
            (high - previous_close).abs(),
            (low - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    data["ATR14"] = true_range.rolling(
        window=14,
        min_periods=14,
    ).mean()

    data["ATR"] = data["ATR14"]

    # ========================================================
    # Average Volume
    # ========================================================

    data["Volume_SMA20"] = volume.rolling(
        window=20,
        min_periods=20,
    ).mean()

    return data


def add_indicators(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compatibility wrapper used by scanner.py
    and strategy.py.
    """

    return compute_all_indicators(df)
