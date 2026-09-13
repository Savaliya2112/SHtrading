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


def _value(
    row,
    name: str,
    default=None,
):
    value = row.get(
        name,
        default,
    )

    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def generate_signal(
    symbol: str,
    data: pd.DataFrame,
    min_score: float = 3,
) -> Optional[Signal]:
    """
    Analyse the latest available candle.

    This function generates analysis only.
    It does NOT place or execute orders.
    """

    if data is None or data.empty:
        return None

    row = data.iloc[-1]

    price = _value(
        row,
        "Close",
    )

    if price is None or price <= 0:
        return None

    score = 0.0
    reasons: list[str] = []

    # ========================================================
    # TREND
    # ========================================================

    sma20 = _value(
        row,
        "SMA20",
    )

    sma50 = _value(
        row,
        "SMA50",
    )

    if (
        sma20 is not None
        and price > sma20
    ):
        score += 1
        reasons.append(
            "price above SMA20"
        )

    if (
        sma20 is not None
        and sma50 is not None
        and sma20 > sma50
    ):
        score += 1
        reasons.append(
            "SMA20 above SMA50"
        )

    # ========================================================
    # RSI
    # ========================================================

    rsi = _value(
        row,
        "RSI14",
    )

    if rsi is None:
        rsi = _value(
            row,
            "RSI",
        )

    if rsi is not None:

        if 50 <= rsi <= 70:
            score += 1
            reasons.append(
                "RSI bullish"
            )

        elif rsi < 30:
            score += 0.5
            reasons.append(
                "RSI oversold"
            )

    # ========================================================
    # MACD
    # ========================================================

    macd = _value(
        row,
        "MACD",
    )

    macd_signal = _value(
        row,
        "MACD_SIGNAL",
    )

    if (
        macd is not None
        and macd_signal is not None
        and macd > macd_signal
    ):
        score += 1
        reasons.append(
            "MACD bullish"
        )

    # ========================================================
    # VOLUME
    # ========================================================

    volume = _value(
        row,
        "Volume",
    )

    volume_average = _value(
        row,
        "Volume_SMA20",
    )

    if (
        volume is not None
        and volume_average is not None
        and volume > volume_average
    ):
        score += 1
        reasons.append(
            "volume above average"
        )

    # ========================================================
    # ATR / RISK LEVELS
    # ========================================================

    atr = _value(
        row,
        "ATR14",
    )

    if atr is None:
        atr = _value(
            row,
            "ATR",
        )

    if atr is None or atr <= 0:
        atr = price * 0.02

    stop = price - (
        1.5 * atr
    )

    target = price + (
        3.0 * atr
    )

    # ========================================================
    # SIGNAL THRESHOLD
    # ========================================================

    if score < float(min_score):
        return None

    confidence = min(
        99.0,
        max(
            0.0,
            50.0
            + (
                score - 3.0
            ) * 12.5,
        ),
    )

    return Signal(
        symbol=symbol,
        action="BUY",
        score=score,
        confidence=confidence,
        price=price,
        stop=max(
            0.0,
            stop,
        ),
        target=target,
        reasons=reasons,
    )
