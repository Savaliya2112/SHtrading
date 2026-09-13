from __future__ import annotations

import pandas as pd


def download_history(
    symbol: str,
    period: str = "1y",
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Download market data from Yahoo Finance.

    This function is used by the scanner for analysis only.
    It does not place or execute trades.
    """

    symbol = str(symbol).strip()

    if not symbol:
        return pd.DataFrame()

    try:
        import yfinance as yf

        df = yf.download(
            symbol,
            period=period,
            interval=interval,
            auto_adjust=True,
            progress=False,
            threads=False,
        )

        if df is None or df.empty:
            print(f"[DATA] No data returned for {symbol}")
            return pd.DataFrame()

        # yfinance can return MultiIndex columns even for
        # a single ticker depending on its version/settings.
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        required = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]

        missing = [
            column
            for column in required
            if column not in df.columns
        ]

        if missing:
            print(
                f"[DATA] {symbol}: missing columns "
                f"{missing}"
            )
            return pd.DataFrame()

        df = df[required].copy()

        # Remove rows without usable prices.
        df = df.dropna(
            subset=[
                "Open",
                "High",
                "Low",
                "Close",
            ]
        )

        return df

    except Exception as exc:
        print(
            f"[DATA ERROR] {symbol}: {exc}"
        )
        return pd.DataFrame()


def get_latest_price(symbol: str):
    """
    Return the latest available close price.

    Returns None if data cannot be retrieved.
    """

    df = download_history(
        symbol,
        period="5d",
        interval="1d",
    )

    if df.empty:
        return None

    try:
        return float(
            df["Close"].iloc[-1]
        )
    except (TypeError, ValueError, IndexError):
       
