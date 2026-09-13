import numpy as np
import pandas as pd


def sma(series, period):
    return series.rolling(window=period).mean()


def ema(series, period):
    return series.ewm(
        span=period,
        adjust=False
    ).mean()


def rsi(series, period=14):
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(
        window=period
    ).mean()

    avg_loss = loss.rolling(
        window=period
    ).mean()

    rs = avg_gain / avg_loss.replace(
        0,
        np.nan
    )

    result = 100 - (
        100 / (1 + rs)
    )

    return result.fillna(50)


def macd(
    series,
    fast=12,
    slow=26,
    signal=9
):
    fast_ema = ema(
        series,
        fast
    )

    slow_ema = ema(
        series,
        slow
    )

    macd_line = (
        fast_ema - slow_ema
    )

    signal_line = ema(
        macd_line,
        signal
    )

    histogram = (
        macd_line - signal_line
    )

    return (
        macd_line,
        signal_line,
        histogram
    )


def bollinger_bands(
    series,
    period=20,
    num_std=2
):
    middle = sma(
        series,
        period
    )

    standard_deviation = (
        series
        .rolling(window=period)
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
        lower
    )


def atr(df, period=14):
    previous_close = (
        df["Close"].shift(1)
    )

    true_range = pd.concat(
        [
            df["High"] - df["Low"],
            (
                df["High"]
                - previous_close
            ).abs(),
            (
                df["Low"]
                - previous_close
            ).abs(),
        ],
        axis=1
    ).max(axis=1)

    return true_range.rolling(
        window=period
    ).mean()


def volume_ratio(
    volume,
    lookback=20
):
    average_volume = (
        volume
        .rolling(window=lookback)
        .mean()
    )

    return (
        volume
        / average_volume.replace(
            0,
            np.nan
        )
    )


def compute_all_indicators(
    df,
    cfg
):
    result = df.copy()

    result["sma_fast"] = sma(
        result["Close"],
        cfg.SMA_FAST
    )

    result["sma_slow"] = sma(
        result["Close"],
        cfg.SMA_SLOW
    )

    result["ema_fast"] = ema(
        result["Close"],
        cfg.EMA_FAST
    )

    result["ema_slow"] = ema(
        result["Close"],
        cfg.EMA_SLOW
    )

    result["rsi"] = rsi(
        result["Close"],
        cfg.RSI_PERIOD
    )

    (
        result["macd"],
        result["macd_signal"],
        result["macd_hist"],
    ) = macd(
        result["Close"],
        cfg.MACD_FAST,
        cfg.MACD_SLOW,
        cfg.MACD_SIGNAL
    )

    (
        result["bb_upper"],
        result["bb_mid"],
        result["bb_lower"],
    ) = bollinger_bands(
        result["Close"],
        cfg.BB_PERIOD,
        cfg.BB_STD
    )

    result["atr"] = atr(
        result,
        cfg.ATR_PERIOD
    )

    result["vol_ratio"] = volume_ratio(
        result["Volume"],
        cfg.VOLUME_LOOKBACK
    )

    return result
