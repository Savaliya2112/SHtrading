from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import pandas as pd


@dataclass
class Signal:
    symbol: str
    action: str
    score: float
    confidence: float
    price: float
    stop: float
    target: float
    reasons: List[str]


def _value(row, name: str, default=None):
    value = row.get(name, default)

    if pd.isna(value):
        return default

    return float(value)


def generate_signal(
    symbol: str,
    data: pd.DataFrame,
    min_score: float = 3,
) -> Optional[Signal]:
    """
    Generate an analysis signal from the latest candle.

    This function ONLY analyses market data.
    It does not place orders.
    """

    if data is None or data.empty:
        return None

    row = data.iloc[-1]

    price = _value(row, "Close")

    if price is None or price <= 0:
        return None

    score = 0.0
    reasons: list[str] = []

    # --------------------------------------------------------
    # Trend
    # --------------------------------------------------------

    sma20 = _value(row, "SMA20")
    sma50 = _value(row, "SMA50")

    if sma20 is not None and price > sma20:
        score += 1
        reasons.append("price above SMA20")

    if (
        sma20 is not None
        and sma50 is not None
        and sma20 > sma50
    ):
        score += 1
        reasons.append("SMA20 above SMA50")

    # --------------------------------------------------------
    # RSI
    # --------------------------------------------------------

    rsi = _value(row, "RSI")

    if rsi is not None:
        if 50 <= rsi <= 70:
            score += 1
            reasons.append("RSI bullish")

        elif rsi < 30:
            score += 0.5
            reasons.append("RSI oversold")

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------

    macd = _value(row, "MACD")
    macd_signal = _value(
        row,
        "MACD_SIGNAL",
    )

    if (
        macd is
