import config as cfg

from data_provider import get_ohlcv
from strategy import generate_signal


def scan_market(ticker, timeframe):
    """
    Scan one ticker on one timeframe.

    Returns:
        Signal object or None
    """

    if timeframe == "1d":
        period = cfg.DAILY_PERIOD
    else:
        period = cfg.INTRADAY_PERIOD

    try:
        print(
            f"Scanning {ticker} "
            f"({timeframe})..."
        )

        df = get_ohlcv(
            ticker=ticker,
            period=period,
            interval=timeframe,
        )

        signal = generate_signal(
            ticker=ticker,
            timeframe=timeframe,
            df=df,
            cfg=cfg,
        )

        if signal is None:
            print(
                f"  {ticker} "
                f"({timeframe}): no signal"
            )
        else:
            print(
                f"  {ticker} "
                f"({timeframe}): "
                f"{signal.direction} "
                f"score={signal.score}/"
                f"{signal.max_score}"
            )

        return signal

    except Exception as exc:
        print(
            f"  ERROR {ticker} "
            f"({timeframe}): {exc}"
        )
        return None


def scan_all_markets():
    """
    Scan every ticker in the configured
    watchlist on every configured timeframe.

    Returns:
        List of valid trading signals.
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

            signal = scan_market(
                ticker=ticker,
                timeframe=timeframe,
            )

            if signal is not None:
                results.append(signal)

    # Strongest signals first
    results.sort(
        key=lambda signal: (
            signal.score,
            signal.direction == "BUY",
        ),
        reverse=True,
    )

    return results


def print_market_report(results):
    """
    Print a readable market-scan report.
    """

    print("")
    print("=" * 60)
    print("SHtrading MARKET SCAN")
    print("=" * 60)

    if not results:
        print("")
        print(
            "No qualifying setups found."
        )
        print("")
        return

    for number, signal in enumerate(
        results,
        start=1,
    ):

        print("")
        print(
            f"{number}. "
            f"{signal.ticker} | "
            f"{signal.timeframe}"
        )

        print(
            f"   Signal: "
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

        print("   Reasons:")

        for reason in signal.reasons:
            print(
                f"      - {reason}"
            )

    print("")
    print("=" * 60)


if __name__ == "__main__":

    print(
        f"Scanning "
        f"{len(cfg.WATCHLIST)} markets..."
    )

    signals = scan_all_markets()

    print_market_report(
        signals
    )

    print(
        f"Qualified signals: "
        f"{len(signals)}"
    )
