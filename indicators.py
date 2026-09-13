from __future__ import annotations

import pandas as pd


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add technical indicators used by the strategy.

    Required input columns:
    Open, High, Low, Close, Volume
    """

    if df is None or df.empty:
        return pd.DataFrame()

    data = df.copy()

    required = ["Open", "High", "Low", "Close", "Volume"]

    missing = [
        column for column in required
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # --------------------------------------------------------
    # Simple Moving Averages
    # --------------------------------------------------------

    data["SMA20"] = (
        data["Close"]
        .rolling(20)
        .mean()
    )

    data["SMA50"] = (
        data["Close"]
        .rolling(50)
        .mean()
    )

    # --------------------------------------------------------
    # RSI - 14
    # --------------------------------------------------------

    delta = data["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    average_gain = gain.rolling(14).mean()
    average_loss = loss.rolling(14).mean()

    rs = average_gain / average_loss.replace(
        0,
        float("nan"),
    )

    data["RSI"] = 100 - (
        100 / (1 + rs)
    )

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------

    ema12 = (
        data["Close"]
        .ewm(
            span=12,
            adjust=False,
        )
        .mean()
    )

    ema26 = (
        data["Close"]
        .ewm(
            span=26,
            adjust=False,
        )
        .mean()
    )

    data["MACD"] = ema12 - ema26

    data["MACD_SIGNAL"] = (
        data["MACD"]
        .ewm(
            span=9,
            adjust=False,
        )
        .mean()
    )

    # --------------------------------------------------------
    # ATR - 14
    # --------------------------------------------------------

    previous_close = data["Close"].shift(1)

    true_range = pd.concat(
        [
            data["High"] - data["Low"],
            (data["High"] - previous_close).abs(),
            (data["Low"] - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    data["ATR"] = (
        true_range
        .rolling(14)
        .mean()
    )

    # --------------------------------------------------------
    # Average volume
    # --------------------------------------------------------

    data["Volume_SMA20"] = (
        data["Volume"]
        .rolling(20)
        .mean()
    )

    return data
