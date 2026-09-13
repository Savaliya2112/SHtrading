"""
SHtrading Market Scanner.

Scans the configured watchlist and ranks the strongest
technical opportunities.

No live orders are placed.
"""

import config as cfg

from strategy import generate_signal
from data_provider import get_ohlcv


def scan_market(ticker, timeframe):
    """Scan one market and return a signal if available."""

    if timeframe == "1d":
        period = cfg.DAILY_PERIOD
    else:
        period = cfg.INTRADAY_PERIOD

    try:
        df = get_ohlcv(
            ticker,
            period=period,
            interval=timeframe,
        )

        signal = generate_signal(
            ticker,
            timeframe,
            df,
            cfg,
        )

        return signal

    except Exception as exc:
        print(
            f"Scanner error - {ticker} "
            f"{timeframe}: {exc}"
        )

        return None


def scan_all_markets():
    """
    Scan all configured markets.

    Returns signals sorted by score.
    """

    results = []

    timeframes = (
        cfg.INTRADAY_TIMEFRAMES
        + [cfg.SWING_TIMEFRAME]
    )

    for ticker in cfg.WATCHLIST:

        for timeframe in timeframes:

            signal = scan_market(
                ticker,
                timeframe,
            )

            if signal is not None:

                results.append(signal)

    results.sort(
        key=lambda signal: signal.score,
        reverse=True,
    )

    return results


def print_market_report(results):
    """Print a readable ranking."""

    print()
    print("=" * 60)
    print("             SHtrading MARKET SCAN")
    print("=" * 60)

    if not results:

        print(
            "No qualifying setups found."
        )

        return

    for number, signal in enumerate(
        results,
        start=1,
    ):

        print()

        print(
            f"{number}. "
            f"{signal.ticker} "
            f"| {signal.timeframe}"
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

        print(
            "   Reasons:"
        )

        for reason in signal.reasons:

            print(
                f"      • {reason}"
            )

    print()
    print("=" * 60)


if __name__ == "__main__":

    signals = scan_all_markets()

    print_market_report(
        signals
    )
