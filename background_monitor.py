from __future__ import annotations

import time
import traceback

import config
from bot import send_telegram
from scanner import scan_symbol
from universe import all_symbols


# Keep track of the last alert for each symbol.
# This prevents the same signal from being sent every 2 minutes.
last_alerts: dict[str, str] = {}


def signal_key(signal) -> str:
    """
    Create a simple fingerprint for a signal.

    A new Telegram alert is sent when the important
    parts of the signal change.
    """
    return (
        f"{signal.action}|"
        f"{round(signal.price, 2)}|"
        f"{round(signal.stop, 2)}|"
        f"{round(signal.target, 2)}"
    )


def format_alert(signal) -> str:
    reasons = ", ".join(signal.reasons)

    return (
        "🚨 SHtrading SIGNAL\n\n"
        f"Symbol: {signal.symbol}\n"
        f"Action: {signal.action}\n"
        f"Score: {signal.score:.0f}/5\n"
        f"Confidence: {signal.confidence:.0f}%\n\n"
        f"Price: {signal.price:.2f}\n"
        f"Stop: {signal.stop:.2f}\n"
        f"Target: {signal.target:.2f}\n\n"
        f"Reasons: {reasons}\n\n"
        "ℹ️ Data/analysis alert only."
    )


def check_symbol(symbol: str) -> bool:
    """
    Check one symbol.

    Returns True if a new Telegram alert was sent.
    """
    try:
        signal = scan_symbol(symbol)

        # No qualifying signal.
        if signal is None:
            return False

        key = signal_key(signal)

        # Same signal as previous check.
        if last_alerts.get(symbol) == key:
            return False

        # New or changed signal.
        message = format_alert(signal)

        sent = send_telegram(message)

        if sent:
            last_alerts[symbol] = key
            print(f"[ALERT] {symbol}")
            return True

        print(f"[TELEGRAM FAILED] {symbol}")
        return False

    except Exception as exc:
        print(f"[ERROR] {symbol}: {exc}")
        return False


def run_scan() -> int:
    """
    Scan the complete configured universe.
    """
    symbols = all_symbols()

    print(
        f"Starting scan of {len(symbols)} symbols..."
    )

    alerts = 0

    for symbol in symbols:
        if check_symbol(symbol):
            alerts += 1

    print(
        f"Scan complete. "
        f"Checked={len(symbols)}, Alerts={alerts}"
    )

    return alerts


def main():
    print("======================================")
    print(" SHtrading Background Monitor")
    print("======================================")
    print(
        f"Check interval: "
        f"{config.SCAN_INTERVAL_MINUTES} minutes"
    )
    print("Mode: ALERT ONLY")
    print("Automatic trading: DISABLED")
    print("--------------------------------------")

    while True:
        started = time.time()

        try:
            run_scan()

        except KeyboardInterrupt:
            print("Monitor stopped.")
            break

        except Exception:
            print("Unexpected monitor error:")
            traceback.print_exc()

        elapsed = time.time() - started

        interval_seconds = (
            config.SCAN_INTERVAL_MINUTES * 60
        )

        # Don't start another scan immediately if
        # the previous scan took some time.
        sleep_seconds = max(
            1,
            interval_seconds - elapsed
        )

        print(
            f"Next scan in "
            f"{sleep_seconds:.0f} seconds..."
        )

        try:
            time.sleep(sleep_seconds)
        except KeyboardInterrupt:
            print("Monitor stopped.")
            break


if __name__ == "__main__":
    main()
