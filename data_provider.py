import pandas as pd
import yfinance as yf


def get_ohlcv(
    ticker,
    period="6mo",
    interval="1d",
):
    """
    Download OHLCV market data from Yahoo Finance.

    Returns:
        pandas.DataFrame with:
        Open, High, Low, Close, Volume
    """

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
            f"No market data returned for {ticker}"
        )

    # --------------------------------------------------------
    # yfinance may return MultiIndex columns.
    # Normalize them to simple column names.
    # --------------------------------------------------------

    if isinstance(
        df.columns,
        pd.MultiIndex
    ):
        df.columns = (
            df.columns
            .get_level_values(0)
        )

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{ticker}: missing columns "
            f"{missing_columns}"
        )

    # --------------------------------------------------------
    # Keep only required market data
    # --------------------------------------------------------

    result = df[
        required_columns
    ].copy()

    # --------------------------------------------------------
    # Convert everything to numeric
    # --------------------------------------------------------

    for column in required_columns:
        result[column] = pd.to_numeric(
            result[column],
            errors="coerce",
        )

    # Remove invalid rows
    result = result.dropna()

    # --------------------------------------------------------
    # Strategy requires enough historical data
    # --------------------------------------------------------

    if len(result) < 60:
        raise ValueError(
            f"{ticker}: insufficient OHLCV "
            f"rows ({len(result)})."
        )

    return result


def get_daily_data(
    ticker,
    period="1y",
):
    """
    Convenience function for daily data.
    """

    return get_ohlcv(
        ticker=ticker,
        period=period,
        interval="1d",
    )


def get_hourly_data(
    ticker,
    period="60d",
):
    """
    Convenience function for hourly data.
    """

    return get_ohlcv(
        ticker=ticker,
        period=period,
        interval="1h",
    )
