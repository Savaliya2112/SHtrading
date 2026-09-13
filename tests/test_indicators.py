import numpy as np
import pandas as pd
from indicators import add_indicators, compute_all_indicators

def sample():
    n = 120
    close = pd.Series(np.linspace(100, 150, n))
    return pd.DataFrame({
        "Open": close,
        "High": close + 2,
        "Low": close - 2,
        "Close": close,
        "Volume": pd.Series(np.full(n, 100000.0))
    })

def test_indicator_api_and_columns():
    out = compute_all_indicators(sample())
    assert not out.empty
    for c in ["SMA20","SMA50","EMA20","EMA50","RSI14","ATR14","MACD","MACD_SIGNAL",
              "MACD_HIST","VOL_RATIO","sma_fast","sma_slow","rsi","macd_hist","atr"]:
        assert c in out.columns
    assert out["RSI14"].between(0, 100).all()
