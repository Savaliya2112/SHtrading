from __future__ import annotations

import time
import pandas as pd
import yfinance as yf


def get_ohlcv(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    ticker = ticker.strip().upper()
    last_error = None

    for attempt in range(3):
        try:
            df = yf.download(
                ticker,
                period=period,
                interval=interval,
                auto_adjust=True,
                progress=False,
                threads=False,
            )

            if df is None or df.empty:
                raise ValueError(f"No market data returned for {ticker} ({interval})")

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            needed = ["Open", "High", "Low", "Close", "Volume"]
            missing = [c for c in needed if c not in df.columns]
            if missing:
                raise ValueError(f"{ticker}: missing columns {missing}")

            df = df[needed].copy()
            df = df.dropna(subset=["Open", "High", "Low", "Close"])
            if len(df) < 60:
                raise ValueError(f"{ticker}: insufficient history ({len(df)} rows)")

            return df

        except Exception as exc:
            last_error = exc
            time.sleep(1.5 * (attempt + 1))

    raise RuntimeError(str(last_error))
