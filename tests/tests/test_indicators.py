import pandas as pd

import config
from indicators import compute_all_indicators


def test_indicators_create_expected_columns():
    close = pd.Series(range(1, 101), dtype=float)

    df = pd.DataFrame({
        "Open": close,
        "High": close + 1,
        "Low": close - 1,
        "Close": close,
        "Volume": 1000,
    })

    result = compute_all_indicators(df, config)

    expected = [
        "sma_fast",
        "sma_slow",
        "ema_fast",
        "ema_slow",
        "rsi",
        "macd",
        "macd_signal",
        "macd_hist",
        "bb_upper",
        "bb_mid",
        "bb_lower",
        "atr",
        "vol_ratio",
    ]

    for column in expected:
        assert column in result.columns
