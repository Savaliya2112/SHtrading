from __future__ import annotations

import io
import pandas as pd
import requests

import config as cfg
from data_provider import get_ohlcv
from strategy import generate_signal
from state import load_state, save_state, should_alert, mark_alerted


WIKI_URL = "https://en.wikipedia.org/wiki/Nasdaq-100"


def get_nasdaq100():
    try:
        html = requests.get(
            WIKI_URL,
            timeout=20,
            headers={"User-Agent": "SHtrading/1.0"}
        ).text
        tables = pd.read_html(io.StringIO(html))
        for table in tables:
            if "Ticker" in table.columns:
                symbols = (
                    table["Ticker"]
                    .astype(str)
                    .str.strip()
                    .str.replace(".", "-", regex=False)
                    .tolist()
                )
                if len(symbols) >= 80:
                    return sorted(set(symbols))
    except Exception as exc:
        print(f"Nasdaq-100 refresh failed: {exc}")

    return list(cfg.NASDAQ100_FALLBACK)


def universe():
    return sorted(set(get_nasdaq100() + cfg.INDEX_TICKERS))


def scan_all_markets(only_new=True):
    state = load_state(cfg.STATE_FILE)
    signals = []

    tickers = universe()
    print(f"Scanning {len(tickers)} instruments...")

    for ticker in tickers:
        for timeframe in cfg.INTERVALS:
            try:
                period = (
                    cfg.INTRADAY_PERIOD
                    if timeframe == "1h"
                    else cfg.DAILY_PERIOD
                )

                df = get_ohlcv(
                    ticker=ticker,
                    period=period,
                    interval=timeframe
                )

                signal = generate_signal(
                    ticker=ticker,
                    timeframe=timeframe,
                    df=df,
                    cfg=cfg
                )

                if not signal:
                    continue

                if only_new and not should_alert(
                    state, signal, cfg.ALERT_COOLDOWN_MINUTES
                ):
                    continue

                signals.append(signal)
                mark_alerted(state, signal)

            except Exception as exc:
                print(f"{ticker} {timeframe}: {exc}")

    save_state(cfg.STATE_FILE, state)
    return signals
