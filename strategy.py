from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class Signal:
    symbol: str
    action: str
    score: float
    confidence: float
    price: float
    stop: float
    target: float
    reasons: tuple[str,...]

def generate_signal(symbol: str, df: pd.DataFrame, min_score: float=3):
    if df is None or len(df)<2: return None
    r=df.iloc[-1]
    price=float(r["Close"]); atr=float(r["ATR14"])
    score=0; reasons=[]
    if price>float(r["SMA20"])>float(r["SMA50"]): score+=1; reasons.append("price above SMA20/SMA50")
    if float(r["EMA20"])>float(r["EMA50"]): score+=1; reasons.append("EMA trend positive")
    if 52<=float(r["RSI14"])<=70: score+=1; reasons.append("RSI momentum healthy")
    if float(r["MACD_HIST"])>0: score+=1; reasons.append("MACD positive")
    if float(r["VOL_RATIO"])>=1.2: score+=1; reasons.append("volume above average")
    if score<min_score: return None
    stop=price-max(1.5*atr,price*.015)
    target=price+max(3*atr,price*.03)
    confidence=min(99,50+score*9)
    return Signal(symbol,"BUY",float(score),confidence,price,stop,target,tuple(reasons))
