import pandas as pd
import yfinance as yf


REQUIRED_COLUMNS = [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
]


def _flatten_columns(df):
    """Normalize yfinance MultiIndex columns."""

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            column[0]
            if isinstance(column, tuple)
            else column
            for column in df.columns
        ]

    return df


def get_ohlcv(
    ticker,
    period="1y",
    interval="1d",
):
    """
    Download OHLCV data from Yahoo Finance.

    Returns a clean DataFrame containing:
    Open, High, Low, Close and Volume.
    """

    ticker = str(ticker).strip()

    if not ticker:
        raise ValueError(
            "Ticker cannot be empty."
        )

    df = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
        threads=False,
    )

    if df is None or df.empty:
        raise ValueError(
            f"No market data returned for {ticker}."
        )

    df = _flatten_columns(df)

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"{ticker}: missing required columns: "
            f"{missing}"
        )

    df = df[
        REQUIRED_COLUMNS
    ].copy()

    for column in REQUIRED_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df = df.replace(
        [float("inf"), float("-inf")],
        pd.NA,
    )

    df = df.dropna(
        subset=REQUIRED_COLUMNS
    )

    if df.empty:
        raise ValueError(
            f"{ticker}: no valid OHLCV rows."
        )

    # Remove duplicate timestamps.
    df = df[
        ~df.index.duplicated(
            keep="last"
        )
    ]

    df = df.sort_index()

    return
