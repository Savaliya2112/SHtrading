"""
Market data provider.

Current provider:
Yahoo Finance via yfinance.

This is suitable for research and paper trading.
A professional real-time provider can later be plugged into
this interface without rewriting the strategy.
"""

import pandas as pd
import yfinance as yf


def get_ohlcv(
    ticker,
    period="6mo",
    interval="1d",
):
    """
    Download OHLCV market data.
    """

    df = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
        threads=False,
    )

    if df.empty:
        raise ValueError(
            f"No market data returned for {ticker}"
        )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"{ticker}: missing columns {missing}"
        )

    df = df[required_columns].copy()

    df = df.dropna()

    return df
