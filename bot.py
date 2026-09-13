import json
import threading
import time
import traceback
from urllib.parse import quote

import requests

import config as cfg
from news import format_news, search_news
from scanner import scan_all_markets
from strategy import generate_signal
from data_provider import get_ohlcv


# ============================================================
# TELEGRAM HELPERS
# ============================================================

def telegram_url(method):
    token = getattr(
        cfg,
        "TELEGRAM_BOT_TOKEN",
        "",
    )

    return (
        f"https://api.telegram.org/"
        f"bot{token}/{method}"
    )


def send_telegram_message(
    message,
    chat_id=None,
):
    """
    Send a Telegram message.

    No trading/order API exists here.
    """

    token = getattr(
        cfg,
        "TELEGRAM_BOT_TOKEN",
        "",
    )

    default_chat_id = getattr(
        cfg,
        "TELEGRAM_CHAT_ID",
        "",
    )

    chat_id = (
        chat_id
        or default_chat_id
    )

    if not token or not chat_id:
        print(
            "Telegram credentials are not configured."
        )
        return False

    response = requests.post(
        telegram_url("sendMessage"),
        json={
            "chat_id": chat_id,
            "text": message,
        },
        timeout=20,
    )

    response.raise_for_status()

    return True


# ============================================================
# SIGNAL FORMAT
# ============================================================

def format_signal(signal):
    lines = [
        "🚨 SHtrading SIGNAL",
        "",
        f"Ticker: {signal.ticker}",
        f"Direction: {signal.direction}",
        f"Timeframe: {signal.timeframe}",
        f"Score: {signal.score}/{signal.max_score}",
        "",
        f"Price: {signal.close:.2f}",
        f"Stop: {signal.stop_loss:.2f}",
        f"Target: {signal.take_profit:.2f}",
        "",
        "Reasons:",
    ]

    for reason in signal.reasons:
        lines.append(
            f"• {reason}"
        )

    lines.extend(
        [
            "",
            "⚠️ ALERT ONLY",
            "You execute the order manually.",
        ]
    )

    return "\n".join(lines)


def format_market_report(
    signals,
):
    if not signals:
        return (
            "🤖 SHtrading\n\n"
            "No NEW qualifying signals found.\n\n"
            "No orders were placed."
        )

    messages = []

    for signal in signals[
        :cfg.MAX_ALERTS
    ]:
        messages.append(
            format_signal(signal)
        )

    return "\n\n".join(
        messages
    )


# ============================================================
# ASK COMMAND
# ============================================================

def ask_market(
    ticker,
):
    """
    Analyse a ticker on demand.
    """

    ticker = ticker.upper().strip()

    if ticker not in cfg.WATCHLIST:
        # Still allow arbitrary Yahoo Finance tickers.
        pass

    results = []

    for timeframe in [
        "1h",
        "1d",
    ]:

        try:

            period = (
                cfg.INTRADAY_PERIOD
                if timeframe == "1h"
                else cfg.DAILY_PERIOD
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

            if signal:
                results.append(
                    signal
                )

        except Exception as exc:

            print(
                f"ASK {ticker} "
                f"{timeframe}: {exc}"
            )

    if not results:

        return (
            f"🔎 {ticker}\n\n"
            "No qualifying technical "
            "signal on 1H or 1D.\n\n"
            "This does NOT mean BUY or SELL."
        )

    lines = [
        f"🔎 ASK — {ticker}",
        "",
    ]

    for signal in results:

        lines.extend(
            [
                (
                    f"{signal.timeframe}: "
                    f"{signal.direction}"
                ),
                (
                    f"Score: "
                    f"{signal.score}/"
                    f"{signal.max_score}"
                ),
                (
                    f"Price: "
                    f"{signal.close:.2f}"
                ),
                (
                    f"Stop: "
                    f"{signal.stop_loss:.2f}"
                ),
                (
                    f"Target: "
                    f"{signal.take_profit:.2f}"
                ),
                "",
                "Reasons:",
            ]
        )

        for reason in signal.reasons:
            lines.append(
                f"• {reason}"
            )

        lines.append("")

    lines.extend(
        [
            "⚠️ Research signal only.",
            "You execute any order manually.",
        ]
    )

    return "\n".join(lines)


def ask_news(
    ticker,
):
    ticker = ticker.upper().strip()

    try:

        items = search_news(
            ticker,
            cfg.NEWS_RESULTS,
        )

        return format_news(
            ticker,
            items,
        )

    except Exception as exc:

        return (
            f"📰 {ticker}\n\n"
            f"News error: {exc}"
        )


def ask_help():
    return (
        "🤖 SHtrading commands\n\n"
        "ASK NVDA\n"
        "→ Technical analysis\n\n"
        "ASK NEWS NVDA\n"
        "→ Recent news\n\n"
        "ASK MARKET\n"
        "→ Current new signals\n\n"
        "ASK HELP\n"
        "→ Show this help\n\n"
        "Examples:\n"
        "ASK AAPL\n"
        "ASK QQQ\n"
        "ASK NVDA\n"
        "ASK NEWS TSLA"
    )


def process_ask(
    text,
):
    """
    Process a Telegram text message.
    """

    command = text.strip()

    if not command:
        return ask_help()

    upper = command.upper()

    if upper in [
        "/START",
        "/HELP",
        "HELP",
        "ASK HELP",
    ]:
        return ask_help()

    if upper.startswith(
        "ASK NEWS "
    ):

        ticker = command[
            len("ASK NEWS "):
        ].strip()

        if not ticker:
            return (
                "Usage:\n"
                "ASK NEWS NVDA"
            )

        return ask_news(
            ticker
        )

    if upper.startswith(
        "NEWS "
    ):

        ticker = command[
            len("NEWS "):
        ].strip()

        return ask_news(
            ticker
        )

    if upper in [
        "ASK MARKET",
        "MARKET",
        "/MARKET",
    ]:

        try:

            signals = scan_all_markets(
                only_new=False
            )

            return format_market_report(
                signals
            )

        except Exception as exc:

            return (
                "Market scan failed:\n"
                f"{exc}"
            )

    if upper.startswith(
        "ASK "
    ):

        ticker = command[
            len("ASK "):
        ].strip()

        if not ticker:
            return ask_help()

        return ask_market(
            ticker
        )

    # Simple ticker message:
    # "NVDA" -> technical analysis.
    if (
        len(command) <= 12
        and " " not in command
        and not command.startswith("/")
    ):

        return ask_market(
            command
        )

    return ask_help()


# ============================================================
# TELEGRAM POLLING
# ============================================================

def telegram_polling():
    """
    Listen for Telegram messages.

    Uses long polling.
    """

    token = getattr(
        cfg,
        "TELEGRAM_BOT_TOKEN",
        "",
    )

    if not token:
        print(
            "Telegram polling disabled: "
            "TELEGRAM_BOT_TOKEN missing."
        )
        return

    offset = None

    print(
        "Telegram ASK listener started."
    )

    while True:

        try:

            params = {
                "timeout": 30,
            }

            if offset is not None:
                params["offset"] = offset

            response = requests.get(
                telegram_url("getUpdates"),
                params=params,
                timeout=40,
            )

            response.raise_for_status()

            data = response.json()

            if not data.get("ok"):
                time.sleep(5)
                continue

            for update in data.get(
                "result",
                [],
            ):

                offset = (
                    update["update_id"]
                    + 1
                )

                message = update.get(
                    "message"
                )

                if not message:
                    continue

                text = message.get(
                    "text",
                    "",
                )

                chat = message.get(
                    "chat",
                    {},
                )

                chat_id = chat.get(
                    "id"
                )

                if not text or chat_id is None:
                    continue

                try:

                    answer = process_ask(
                        text
                    )

                    send_telegram_message(
                        answer,
                        chat_id=chat_id,
                    )

                except Exception as exc:

                    print(
                        "ASK error:"
                    )

                    traceback.print_exc()

                    send_telegram_message(
                        f"ASK error: {exc}",
                        chat_id=chat_id,
                    )

        except requests.RequestException as exc:

            print(
                f"Telegram connection error: "
                f"{exc}"
            )

            time.sleep(10)

        except Exception:

            traceback.print_exc()
            time.sleep(10)


# ============================================================
# AUTOMATIC MARKET SCAN
# ============================================================

def run_scan():
    """
    Run automatic market scanning.

    Only NEW qualifying signals are sent.
    """

    print(
        "Starting market scan..."
    )

    signals = scan_all_markets(
        only_new=True
    )

    print(
        f"New signals: {len(signals)}"
    )

    if not signals:
        return

    message = format_market_report(
        signals
    )

    send_telegram_message(
        message
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # Start Telegram ASK listener
    telegram_thread = threading.Thread(
        target=telegram_polling,
        daemon=True,
    )

    telegram_thread.start()

    # Initial scan
    run_scan()

    print("")
    print(
        "SHtrading is running."
    )
    print(
        "Telegram ASK is enabled."
    )
    print(
        "No live orders are executed."
    )
    print("")

    # Keep process alive.
    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
