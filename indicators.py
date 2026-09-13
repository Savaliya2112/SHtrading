"""
Technical indicator calculations. Pure pandas/numpy, no external TA library needed
so there are fewer version-compatibility headaches.
"""

import pandas as pd
import numpy as np


def sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out = 100 - (100 / (1 + rs))
    return out.fillna(50)  # neutral when undefined


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def bollinger_bands(series: pd.Series, period: int = 20, num_std: float = 2.0):
    mid = sma(series, period)
    std = series.rolling(window=period).std()
    upper = mid + num_std * std
    lower = mid - num_std * std
    return upper, mid, lower


def volume_ratio(volume: pd.Series, lookback: int = 20) -> pd.Series:
    avg_vol = volume.rolling(window=lookback).mean()
    return volume / avg_vol.replace(0, np.nan)


def compute_all_indicators(df: pd.DataFrame, cfg) -> pd.DataFrame:
    """
    df must have columns: Open, High, Low, Close, Volume
    Returns df with indicator columns appended.
    """
    out = df.copy()
    out["sma_fast"] = sma(out["Close"], cfg.SMA_FAST)
    out["sma_slow"] = sma(out["Close"], cfg.SMA_SLOW)
    out["ema_fast"] = ema(out["Close"], cfg.EMA_FAST)
    out["ema_slow"] = ema(out["Close"], cfg.EMA_SLOW)
    out["rsi"] = rsi(out["Close"], cfg.RSI_PERIOD)
    macd_line, signal_line, hist = macd(
        out["Close"], cfg.MACD_FAST, cfg.MACD_SLOW, cfg.MACD_SIGNAL
    )
    out["macd"] = macd_line
    out["macd_signal"] = signal_line
    out["macd_hist"] = hist
    upper, mid, lower = bollinger_bands(out["Close"], cfg.BB_PERIOD, cfg.BB_STD)
    out["bb_upper"] = upper
    out["bb_mid"] = mid
    out["bb_lower"] = lower
    out["vol_ratio"] = volume_ratio(out["Volume"], cfg.VOLUME_LOOKBACK)
    return out


def score_signal(latest_row, cfg) -> dict:
    """
    Turns the latest indicator row into a buy/sell confluence score.
    This is a rule-based heuristic, NOT a statistically validated strategy,
    and it does not guarantee any win rate.
    """
    buy_points = 0
    sell_points = 0
    reasons_buy = []
    reasons_sell = []

    # Trend: fast MA above/below slow MA
    if latest_row["sma_fast"] > latest_row["sma_slow"]:
        buy_points += 1
        reasons_buy.append("SMA fast > SMA slow (uptrend)")
    else:
        sell_points += 1
        reasons_sell.append("SMA fast < SMA slow (downtrend)")

    if latest_row["ema_fast"] > latest_row["ema_slow"]:
        buy_points += 1
        reasons_buy.append("EMA fast > EMA slow")
    else:
        sell_points += 1
        reasons_sell.append("EMA fast < EMA slow")

    # RSI
    if latest_row["rsi"] < cfg.RSI_OVERSOLD:
        buy_points += 1
        reasons_buy.append(f"RSI oversold ({latest_row['rsi']:.1f})")
    elif latest_row["rsi"] > cfg.RSI_OVERBOUGHT:
        sell_points += 1
        reasons_sell.append(f"RSI overbought ({latest_row['rsi']:.1f})")

    # MACD
    if latest_row["macd"] > latest_row["macd_signal"]:
        buy_points += 1
        reasons_buy.append("MACD above signal line")
    else:
        sell_points += 1
        reasons_sell.append("MACD below signal line")

    # Bollinger Bands
    if latest_row["Close"] <= latest_row["bb_lower"]:
        buy_points += 1
        reasons_buy.append("Price at/below lower Bollinger Band")
    elif latest_row["Close"] >= latest_row["bb_upper"]:
        sell_points += 1
        reasons_sell.append("Price at/above upper Bollinger Band")

    # Volume confirmation (multiplies confidence, doesn't pick direction)
    vol_confirmed = latest_row["vol_ratio"] >= cfg.VOLUME_SPIKE_MULTIPLIER
    if vol_confirmed:
        if buy_points > sell_points:
            buy_points += 1
            reasons_buy.append(f"Volume spike ({latest_row['vol_ratio']:.1f}x avg)")
        elif sell_points > buy_points:
            sell_points += 1
            reasons_sell.append(f"Volume spike ({latest_row['vol_ratio']:.1f}x avg)")

    if buy_points >= cfg.MIN_SIGNAL_SCORE and buy_points > sell_points:
        direction = "BUY"
        score = buy_points
        reasons = reasons_buy
    elif sell_points >= cfg.MIN_SIGNAL_SCORE and sell_points > buy_points:
        direction = "SELL"
        score = sell_points
        reasons = reasons_sell
    else:
        direction = None
        score = max(buy_points, sell_points)
        reasons = []

    return {
        "direction": direction,
        "score": score,
        "max_score": 6,
        "reasons": reasons,
        "rsi": latest_row["rsi"],
        "close": latest_row["Close"],
        "vol_ratio": latest_row["vol_ratio"],
    }
