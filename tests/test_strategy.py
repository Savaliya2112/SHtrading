import numpy as np, pandas as pd
from indicators import add_indicators
from strategy import generate_signal
def test_strategy():
    n=120; c=pd.Series(np.linspace(100,150,n))
    df=pd.DataFrame({"Open":c,"High":c+2,"Low":c-2,"Close":c,"Volume":np.full(n,200000)})
    s=generate_signal("TEST",add_indicators(df),3)
    assert s is None or s.action=="BUY"
