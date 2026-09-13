"""
Technical indicators used by the SHtrading strategy.

Pure pandas/numpy implementation.
No TA-Lib dependency is required.
"""

import numpy as np
import pandas as pd


def sma(series, period):
    return series.rolling(window=period).mean()


def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


def rsi(series, period=14):
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    result = 100 - (100 / (1 + rs))

    return result.fillna(50)


def macd(series, fast=12, slow=26, signal=9):
    fast_ema = ema(series, fast)
    slow_ema = ema(series, slow)

    macd_line = fast_ema - slow_ema
    signal_line = ema(macd_line, signal)

    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def bollinger_bands(series, period=20, num_std=2):
    middle = sma(series, period)

    std = series.rolling(period).std()

    upper = middle + num_std * std
    lower = middle - num_std * std

    return upper, middle, lower


def atr(df, period=14):
    previous_close = df["Close"].shift(1)

    tr1 = df["High"] - df["Low"]

    tr2 = (df["High"] - previous_close).abs()

    tr3 = (df["Low"] - previous_close).abs()

    true_range = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    return true_range.rolling(period).mean()


def volume_ratio(volume, lookback=20):
    average_volume = volume.rolling(lookback).mean()

    return volume / average_volume.replace(0, np.nan)


def compute_all_indicators(df, cfg):
    """
    Add all strategy indicators to OHLCV dataframe.
    """

    out = df.copy()

    out["sma_fast"] = sma(
        out["Close"],
        cfg.SMA_FAST
    )

    out["sma_slow"] = sma(
        out["Close"],
        cfg.SMA_SLOW
    )

    out["ema_fast"] = ema(
        out["Close"],
        cfg.EMA_FAST
    )

    out["ema_slow"] = ema(
        out["Close"],
        cfg.EMA_SLOW
    )

    out["rsi"] = rsi(
        out["Close"],
        cfg.RSI_PERIOD
    )

    (
        out["macd"],
        out["macd_signal"],
        out["macd_hist"],
    ) = macd(
        out["Close"],
        cfg.MACD_FAST,
        cfg.MACD_SLOW,
        cfg.MACD_SIGNAL,
    )

    (
        out["bb_upper"],
        out["bb_mid"],
        out["bb_lower"],
    ) = bollinger_bands(
        out["Close"],
        cfg.BB_PERIOD,
        cfg.BB_STD,
    )

    out["atr"] = atr(
        out,
        cfg.ATR_PERIOD
    )

    out["vol_ratio"] = volume_ratio(
        out["Volume"],
        cfg.VOLUME_LOOKBACK
    )

    return out
