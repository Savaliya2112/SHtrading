from __future__ import annotations

from dataclasses import dataclass
from typing import List

from indicators import add_indicators


@dataclass
class Signal:
    ticker: str
    timeframe: str
    direction: str
    score: int
    max_score: int
    close: float
    stop_loss: float
    take_profit: float
    reasons: List[str]


def generate_signal(ticker, timeframe, df, cfg):
    x = add_indicators(df)
    if x.empty:
        return None

    r = x.iloc[-1]
    close = float(r["Close"])
    atr = float(r["ATR14"])

    if atr <= 0:
        return None

    bullish = 0
    bearish = 0
    bull_reasons = []
    bear_reasons = []

    if r["Close"] > r["SMA20"]:
        bullish += 1
        bull_reasons.append("Price above SMA20")
    else:
        bearish += 1
        bear_reasons.append("Price below SMA20")

    if r["SMA20"] > r["SMA50"]:
        bullish += 1
        bull_reasons.append("SMA20 above SMA50")
    else:
        bearish += 1
        bear_reasons.append("SMA20 below SMA50")

    if r["RSI14"] >= 55:
        bullish += 1
        bull_reasons.append(f"RSI bullish ({r['RSI14']:.1f})")
    elif r["RSI14"] <= 45:
        bearish += 1
        bear_reasons.append(f"RSI bearish ({r['RSI14']:.1f})")

    if r["MACD"] > r["MACD_SIGNAL"]:
        bullish += 1
        bull_reasons.append("MACD bullish")
    elif r["MACD"] < r["MACD_SIGNAL"]:
        bearish += 1
        bear_reasons.append("MACD bearish")

    if r["VOL_RATIO"] >= 1.2:
        if r["Close"] > r["Open"]:
            bullish += 1
            bull_reasons.append("Above-average volume on up candle")
        elif r["Close"] < r["Open"]:
            bearish += 1
            bear_reasons.append("Above-average volume on down candle")

    max_score = 5

    if bullish >= bearish and bullish >= cfg.MIN_SCORE:
        stop = close - 1.5 * atr
        target = close + 3.0 * atr
        return Signal(
            ticker, timeframe, "BUY", bullish, max_score,
            close, stop, target, bull_reasons
        )

    if bearish > bullish and bearish >= cfg.MIN_SCORE:
        stop = close + 1.5 * atr
        target = close - 3.0 * atr
        return Signal(
            ticker, timeframe, "SELL", bearish, max_score,
            close, stop, target, bear_reasons
        )

    return None
