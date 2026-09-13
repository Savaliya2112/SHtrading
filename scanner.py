import json
import os
from datetime import datetime, timezone

import config as cfg
from data_provider import get_ohlcv
from strategy import generate_signal


STATE_FILE = "signal_state.json"


def _load_state():
    if not os.path.exists(STATE_FILE):
        return {}

    try:
        with open(
            STATE_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return data if isinstance(data, dict) else {}

    except (OSError, json.JSONDecodeError):
        return {}


def _save_state(state):
    temporary_file = (
        f"{STATE_FILE}.tmp"
    )

    with open(
        temporary_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            state,
            file,
            indent=2,
        )

    os.replace(
        temporary_file,
        STATE_FILE,
    )


def _candle_key(df):
    """Return the timestamp of the latest candle."""

    if df is None or df.empty:
        return None

    timestamp = df.index[-1]

    try:
        return timestamp.isoformat()
    except AttributeError:
        return str(timestamp)


def scan_market(
    ticker,
    timeframe,
):
    """Scan one market."""

    try:
        if timeframe == "1d":
            period = cfg.DAILY_PERIOD
        else:
            period = cfg.INTRADAY_PERIOD

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

        return {
            "ticker": ticker,
            "timeframe": timeframe,
            "signal": signal,
            "candle": _candle_key(df),
            "error": None,
        }

    except Exception as exc:
        return {
            "ticker": ticker,
            "timeframe": timeframe,
            "signal": None,
            "candle": None,
            "error": str(exc),
        }


def _signal_key(result):
    """
    Unique identity for an alert.

    A new alert is generated when a new candle,
    direction or score appears.
    """

    signal = result["signal"]

    if signal is None:
        return None

    return "|".join(
        [
            str(result["ticker"]),
            str(result["timeframe"]),
            str(result["candle"]),
            str(signal.direction),
            str(signal.score),
        ]
    )


def scan_all_markets(
    only_new=True,
):
    """
    Scan the complete configured universe.

    When only_new=True, previously alerted setups
    are not returned again.
    """

    state = _load_state()
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

            result = scan_market(
                ticker=ticker,
                timeframe=timeframe,
            )

            if result["error"]:

                print(
                    f"{ticker} "
                    f"{timeframe}: "
                    f"ERROR — "
                    f"{result['error']}"
                )

                continue

            signal = result["signal"]

            if signal is None:
                continue

            key = _signal_key(
                result
            )

            if only_new and key in state:
                continue

            results.append(
                signal
            )

            state[key] = {
                "sent_at": datetime.now(
                    timezone.utc
                ).isoformat(),
                "ticker": ticker,
                "timeframe": timeframe,
                "candle": result["candle"],
                "direction": signal.direction,
                "score": signal.score,
            }

    _save_state(state)

    results.sort(
        key=lambda signal: (
            signal.score,
            signal.direction == "BUY",
        ),
        reverse=True,
    )

    return results


def print_market_report(
    results,
):
    """Print a readable report."""

    print("")
    print("=" * 70)
    print("SHtrading MARKET SCAN")
    print("=" * 70)

    if not results:
        print("")
        print(
            "No NEW qualifying setups found."
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

        for reason in signal.reasons:
            print(
                f"   - {reason}"
            )

    print("")
    print("=" * 70)


if __name__ == "__main__":

    signals = scan_all_markets(
        only_new=False
    )

    print_market_report(
        signals
    )
