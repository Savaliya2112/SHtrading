from __future__ import annotations

import sys
import urllib.parse
import urllib.request

import config
from news import get_news
from scanner import scan_symbol
from universe import all_symbols


def send_telegram(message: str) -> bool:
    """
    Send a message to Telegram.

    Returns True when Telegram accepts the request.
    Returns False when Telegram is not configured or
    the request fails.
    """

    token = config.TELEGRAM_BOT_TOKEN
    chat_id = config.TELEGRAM_CHAT_ID

    if not token or not chat_id:
        print(message)
        return False

    url = (
        f"https://api.telegram.org/"
        f"bot{token}/sendMessage"
    )

    data = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": message,
        }
    ).encode("utf-8")

    try:
        request = urllib.request.Request(
            url,
            data=data,
            method="POST",
        )

        with urllib.request.urlopen(
            request,
            timeout=config.REQUEST_TIMEOUT_SECONDS,
        ) as response:
            response.read()

        return True

    except Exception as exc:
        print(
            f"[TELEGRAM ERROR] {exc}"
        )
        return False


def format_signal(signal) -> str:
    """
    Format a trading-analysis signal for Telegram.
    """

    reasons = ", ".join(
        signal.reasons
    )

    return (
        "📈 SHtrading SIGNAL\n\n"
        f"Symbol: {signal.symbol}\n"
        f"Action: {signal.action}\n"
        f"Score: {signal.score:.0f}/5\n"
        f"Confidence: "
        f"{signal.confidence:.0f}%\n\n"
        f"Price: {signal.price:.2f}\n"
        f"Stop: {signal.stop:.2f}\n"
        f"Target: {signal.target:.2f}\n\n"
        f"Reasons: {reasons}\n\n"
        "ℹ️ Analysis/data alert only.\n"
        "No automatic trading."
    )


def ask(symbol: str) -> str:
    """
    Analyse one symbol.

    This function is retained for compatibility,
    although the background-monitor requirement
    does not depend on Telegram ASK.
    """

    symbol = (
        str(symbol)
        .strip()
        .upper()
    )

    if not symbol:
        return "Please provide a symbol."

    signal = scan_symbol(symbol)

    if signal is None:
        return (
            f"
