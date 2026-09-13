"""
SHtrading Telegram scanner.

Scans the configured watchlist, ranks qualifying technical
signals, and sends one consolidated report.

It does NOT place live trades.
"""

import sys
import traceback

import requests

import config as cfg

from news import search_news
from scanner import scan_all_markets


def send_telegram_message(message):
    """Send a message through Telegram."""

    if not cfg.TELEGRAM_BOT_TOKEN:
        print("Telegram token not configured.")
        return False

    if not cfg.TELEGRAM_CHAT_ID:
        print("Telegram chat ID not configured.")
        return False

    url = (
        "https://api.telegram.org/bot"
        + cfg.TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    response = requests.post(
        url,
        data={
            "chat_id": cfg.TELEGRAM_CHAT_ID,
            "text": message,
            "disable_web_page_preview": True,
        },
        timeout=15,
    )

    if response.status_code != 200:
        print(
            "Telegram error:",
            response.status_code,
            response.text,
        )
        return False

    return True


def format_market_report(signals):
    """Format ranked scanner results for Telegram."""

    if not signals:
        return (
            "🤖 SHtrading MARKET SCAN\n\n"
            "No qualifying setups found.\n\n"
            "⚠️ Research/paper signal only."
        )

    lines = [
        "🤖 SHtrading MARKET SCAN",
        "",
    ]

    for number, signal in enumerate(
        signals[:cfg.MAX_ALERTS],
        start=1,
    ):
        lines.extend(
            [
                f"{number}. {signal.ticker} — "
                f"{signal.direction}",
                f"Timeframe: {signal.timeframe}",
                f"Score: {signal.score}/{signal.max_score}",
                f"Price: {signal.close:.2f}",
                f"Stop: {signal.stop_loss:.2f}",
                f"Target: {signal.take_profit:.2f}",
                "Reasons: "
                + "; ".join(signal.reasons),
                "",
            ]
        )

    lines.append(
        "⚠️ Research/paper signal only. "
        "No live order was placed."
    )

    return "\n".join(lines)


def run_scan():
    """Run the ranked market scanner."""

    print(
        f"Scanning {len(cfg.WATCHLIST)} markets..."
    )

    signals = scan_all_markets()

    message = format_market_report(
        signals
    )

    print(message)

    send_telegram_message(
        message
    )

    print(
        f"Scan completed. "
        f"Qualified signals: {len(signals)}"
    )


def run_news_scan():
    """Send a consolidated recent-news report."""

    print("News scan")

    lines = [
        "📰 SHtrading NEWS",
        "",
    ]

    found = 0

    for ticker in cfg.WATCHLIST:

        try:

            items = search_news(
                ticker,
                cfg.NEWS_RESULTS,
            )

            for item in items[
                :cfg.NEWS_PER_TICKER
            ]:

                lines.extend(
                    [
                        f"{ticker}: "
                        f"{item.title}",
                        f"{item.source}",
                        "",
                    ]
                )

                found += 1

        except Exception as exc:

            print(
                f"News failed "
                f"{ticker}: {exc}"
            )

    if found == 0:

        lines.append(
            "No news items found."
        )

    lines.append(
        "⚠️ News is contextual information, "
        "not a guaranteed trading signal."
    )

    send_telegram_message(
        "\n".join(lines)
    )


if __name__ == "__main__":

    mode = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "scan"
    )

    try:

        if mode == "news":

            run_news_scan()

        else:

            run_scan()

    except Exception:

        traceback.print_exc()

        raise
