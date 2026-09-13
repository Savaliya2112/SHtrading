from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class Signal:
    symbol: str
    action: str
    score: float
    price: float
    stop: float
    target: float
    reasons: tuple[str, ...]

def generate_signal(symbol: str, df: pd.DataFrame, min_score: float = 3) -> Signal | None:
    if df is None or len(df) < 2:
        return None
    row = df.iloc[-1]
    price = float(row["Close"])
    atr = float(row.get("ATR14", 0) or 0)
    score = 0
    reasons = []
    if price > float(row["SMA20"]) > float(row["SMA50"]):
        score += 1; reasons.append("price above rising moving averages")
    if float(row["EMA20"]) > float(row["EMA50"]):
        score += 1; reasons.append("short EMA above long EMA")
    if float(row["RSI14"]) >= 52 and float(row["RSI14"]) <= 70:
        score += 1; reasons.append("RSI confirms momentum")
    if float(row["MACD_HIST"]) > 0:
        score += 1; reasons.append("MACD histogram positive")
    if float(row["VOL_RATIO"]) >= 1.2:
        score += 1; reasons.append("volume above average")

    if score < min_score:
        return None
    stop = price - max(atr * 1.5, price * 0.015)
    target = price + max(atr * 3.0, price * 0.03)
    return Signal(symbol, "BUY", float(score), price, stop, target, tuple(reasons))
