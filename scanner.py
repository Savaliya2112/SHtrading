import config as cfg

from data_provider import get_ohlcv
from strategy import generate_signal


def _period_for_timeframe(timeframe):
    if timeframe == "1d":
        return cfg.DAILY_PERIOD

    return cfg.INTRADAY_PERIOD


def scan_market(ticker, timeframe):
    """
    Scan one ticker on one timeframe.

    Returns:
        Signal or None
    """

    period = _period_for_timeframe(
        timeframe
    )

    try:
        df = get_ohlcv(
            ticker=ticker,
            period=period,
            interval=timeframe,
        )

        return generate_signal(
            ticker=ticker,
            timeframe=timeframe,
            df=df,
            cfg=cfg,
        )

    except Exception as exc:
        print(
            f"ERROR | {ticker} | "
            f"{timeframe} | {exc}"
        )

        return None


def scan_all_markets():
    """
    Scan the complete configured universe.

    Returns a list of qualifying signals.
    """

    signals = []

    timeframes = list(
        cfg.INTRADAY_TIMEFRAMES
    )

    if cfg.SWING_TIMEFRAME not in timeframes:
        timeframes.append(
            cfg.SWING_TIMEFRAME
        )

    for ticker in cfg.WATCHLIST:

        for timeframe in timeframes:

            signal = scan_market(
                ticker=ticker,
                timeframe=timeframe,
            )

            if signal is not None:
                signals.append(
                    signal
                )

    # Strongest signals first.
    signals.sort(
        key=lambda item: (
            item.score,
            item.ticker,
            item.timeframe,
        ),
        reverse=True,
    )

    return signals


def scan_historical(
    ticker,
    timeframe,
    lookback=10,
):
    """
    Inspect previous completed candles.

    This is useful for finding setups that occurred
    recently rather than looking only at the latest candle.

    Returns:
        List of historical signals.
    """

    period = _period_for_timeframe(
        timeframe
    )

    try:
        df = get_ohlcv(
            ticker=ticker,
            period=period,
            interval=timeframe,
        )
    except Exception as exc:
        print(
            f"ERROR | historical | "
            f"{ticker} | {exc}"
        )
        return []

    if len(df) < 2:
        return []

    results = []

    # Work backwards through completed candles.
    start = max(
        1,
        len(df) - int(lookback),
    )

    for index in range(
        start,
        len(df),
    ):

        historical_df = df.iloc[
            :index + 1
        ]

        signal = generate_signal(
            ticker=ticker,
            timeframe=timeframe,
            df=historical_df,
            cfg=cfg,
        )

        if signal is not None:

            candle_time = (
                historical_df.index[-1]
            )

            results.append(
                {
                    "timestamp": str(
                        candle_time
                    ),
                    "signal": signal,
                }
            )

    return results


def scan_recent_history(
    lookback=5,
):
    """
    Scan recent historical candles for the
    complete configured universe.

    This does not place orders.
    """

    results = []

    timeframes = list(
        cfg.INTRADAY_TIMEFRAMES
    )

    if cfg.SWING_TIMEFRAME not in timeframes:
        timeframes.append(
            cfg.SWING_TIMEFRAME
        )

    for ticker in cfg.WATCHLIST:

        for timeframe in timeframes:

            history = scan_historical(
                ticker=ticker,
                timeframe=timeframe,
                lookback=lookback,
            )

            for item in history:

                results.append(
                    {
                        "ticker": ticker,
                        "timeframe": timeframe,
                        "timestamp": item[
                            "timestamp"
                        ],
                        "signal": item[
                            "signal"
                        ],
                    }
                )

    return results


def print_market_report(
    signals,
):
    """Print a readable scan report."""

    print("")
    print("=" * 70)
    print("SHtrading MARKET SCAN")
    print("=" * 70)

    if not signals:
        print("")
        print(
            "No qualifying setups found."
        )
        print("")
        return

    for number, signal in enumerate(
        signals,
        start=1,
    ):

        print("")
        print(
            f"{number}. "
            f"{signal.ticker} | "
            f"{signal.timeframe}"
        )

        print(
            f"   Direction: "
            f"{signal.direction}"
        )

        print(
            f"   Score: "
            f"{signal.score}/"
            f"{signal.max_score}"
        )

        print(
            f"   Price: "
            f"{signal.close:.2f}"
        )

        print(
            f"   Stop: "
            f"{signal.stop_loss:.2f}"
        )

        print(
            f"   Target: "
            f"{signal.take_profit:.2f}"
        )

        for reason in signal.reasons:
            print(
                f"   - {reason}"
            )

    print("")


if __name__ == "__main__":

    signals = scan_all_markets()

    print_market_report(
        signals
    )
