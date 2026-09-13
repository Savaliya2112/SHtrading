import numpy as np
import pandas as pd


def sma(series, period):
    """Simple Moving Average."""
    return series.rolling(
        window=period,
        min_periods=period,
    ).mean()


def ema(series, period):
    """Exponential Moving Average."""
    return series.ewm(
        span=period,
        adjust=False,
        min_periods=period,
    ).mean()


def rsi(series, period=14):
    """Relative Strength Index."""

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    average_gain = gain.rolling(
        window=period,
        min_periods=period,
    ).mean()

    average_loss = loss.rolling(
        window=period,
        min_periods=period,
    ).mean()

    # Avoid division by zero.
    rs = average_gain / average_loss.replace(
        0,
        np.nan,
    )

    result = 100 - (
        100 / (1 + rs)
    )

    # If there is no loss, RSI is 100.
    result = result.where(
        average_loss != 0,
        100,
    )

    return result


def macd(
    series,
    fast=12,
    slow=26,
    signal=9,
):
    """MACD line, signal line and histogram."""

    fast_ema = ema(
        series,
        fast,
    )

    slow_ema = ema(
        series,
        slow,
    )

    macd_line = (
        fast_ema - slow_ema
    )

    signal_line = ema(
        macd_line,
        signal,
    )

    histogram = (
        macd_line - signal_line
    )

    return (
        macd_line,
        signal_line,
        histogram,
    )


def bollinger_bands(
    series,
    period=20,
    num_std=2,
):
    """Bollinger upper, middle and lower bands."""

    middle = sma(
        series,
        period,
    )

    standard_deviation = (
        series
        .rolling(
            window=period,
            min_periods=period,
        )
        .std()
    )

    upper = (
        middle
        + num_std * standard_deviation
    )

    lower = (
        middle
        - num_std * standard_deviation
    )

    return (
        upper,
        middle,
        lower,
    )


def atr(
    df,
    period=14,
):
    """Average True Range."""

    previous_close = (
        df["Close"].shift(1)
    )

    high_low = (
        df["High"] - df["Low"]
    )

    high_previous_close = (
        df["High"]
        - previous_close
    ).abs()

    low_previous_close = (
        df["Low"]
        - previous_close
    ).abs()

    true_range = pd.concat(
        [
            high_low,
            high_previous_close,
            low_previous_close,
        ],
        axis=1,
    ).max(axis=1)

    return true_range.rolling(
        window=period,
        min_periods=period,
    ).mean()


def volume_ratio(
    volume,
    lookback=20,
):
    """Current volume divided by average volume."""

    average_volume = (
        volume
        .rolling(
            window=lookback,
            min_periods=lookback,
        )
        .mean()
    )

    return (
        volume
        / average_volume.replace(
            0,
            np.nan,
        )
    )


def compute_all_indicators(
    df,
    cfg,
):
    """
    Add all indicators required by the strategy.

    The original OHLCV dataframe is not modified.
    """

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
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    result = df.copy()

    # Ensure numeric calculations.
    for column in required:
        result[column] = pd.to_numeric(
            result[column],
            errors="coerce",
        )

    result["sma_fast"] = sma(
        result["Close"],
        cfg.SMA_FAST,
    )

    result["sma_slow"] = sma(
        result["Close"],
        cfg.SMA_SLOW,
    )

    result["ema_fast"] = ema(
        result["Close"],
        cfg.EMA_FAST,
    )

    result["ema_slow"] = ema(
        result["Close"],
        cfg.EMA_SLOW,
    )

    result["rsi"] = rsi(
        result["Close"],
        cfg.RSI_PERIOD,
    )

    (
        result["macd"],
        result["macd_signal"],
        result["macd_hist"],
    ) = macd(
        result["Close"],
        cfg.MACD_FAST,
        cfg.MACD_SLOW,
        cfg.MACD_SIGNAL,
    )

    (
        result["bb_upper"],
        result["bb_mid"],
        result["bb_lower"],
    ) = bollinger_bands(
        result["Close"],
        cfg.BB_PERIOD,
        cfg.BB_STD,
    )

    result["atr"] = atr(
        result,
        cfg.ATR_PERIOD,
    )

    result["vol_ratio"] = volume_ratio(
        result["Volume"],
        cfg.VOLUME_LOOKBACK,
    )

    return result
