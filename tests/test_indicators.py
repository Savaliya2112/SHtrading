import numpy as np, pandas as pd
from indicators import compute_all_indicators
def test_indicators():
    n=120; c=pd.Series(np.linspace(100,150,n))
    df=pd.DataFrame({"Open":c,"High":c+2,"Low":c-2,"Close":c,"Volume":np.full(n,100000)})
    x=compute_all_indicators(df)
    assert not x.empty
    assert {"SMA20","SMA50","RSI14","ATR14","MACD_HIST"}.issubset(x.columns)
    assert x.RSI14.between(0,100).all()
