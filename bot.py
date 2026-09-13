import sys
import traceback

import requests

import config as cfg

from news import search_news
from scanner import scan_all_markets


# ============================================================
# TELEGRAM
# ============================================================

def send_telegram_message(message):
    """
    Send a message to Telegram.

    If Telegram credentials are not configured,
    the message is printed locally instead.

    This function does NOT place trades.
    """

    token = getattr(
        cfg,
        "TELEGRAM_BOT_TOKEN",
        "",
    )

    chat_id = getattr(
        cfg,
        "TELEGRAM_CHAT_ID",
        "",
    )

    if not token or not chat_id:
        print(
            "Telegram is not configured."
        )
        print(
            "Report was generated locally."
        )
        return False

    url = (
        "https://api.telegram.org/"
        f"bot{token}/sendMessage"
    )

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": True,
        },
        timeout=15,
    )

    response.raise_for_status()

    return True


# ============================================================
# MARKET REPORT
# ============================================================

def format_market_report(
    signals,
):
    """
    Convert market signals into
    a Telegram-friendly report.
    """

    max_alerts = int(
        getattr(
            cfg,
            "MAX_ALERTS",
            10,
        )
    )

    lines = [
        "🤖 SHtrading MARKET SCAN",
        "",
    ]

    if not signals:

        lines.extend(
            [
                "No qualifying setups found.",
                "",
                "Market scan completed successfully.",
                "",
                "⚠️ Research/paper signal only.",
                "No live order was placed.",
            ]
        )

        return "\n".join(lines)

    for number, signal in enumerate(
        signals[:max_alerts],
        start=1,
    ):

        lines.extend(
            [
                (
                    f"{number}. "
                    f"{signal.ticker} — "
                    f"{signal.direction}"
                ),

                (
                    f"Timeframe: "
                    f"{signal.timeframe}"
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

                (
                    "Reasons: "
                    + "; ".join(
                        signal.reasons
                    )
                ),

                "",
            ]
        )

    lines.extend(
        [
            "⚠️ Research/paper signal only.",
            "No live order was placed.",
        ]
    )

    return "\n".join(lines)


# ============================================================
# MARKET SCAN
# ============================================================

def run_scan():
    """
    Run the complete market scanner.
    """

    watchlist = getattr(
        cfg,
        "WATCHLIST",
        [],
    )

    print("")
    print("=" * 60)
    print("SHtrading BOT")
    print("MARKET SCAN")
    print("=" * 60)
    print("")

    print(
        f"Markets configured: "
        f"{len(watchlist)}"
    )

    print("")

    signals = scan_all_markets()

    message = format_market_report(
        signals
    )

    print("")
    print(message)
    print("")

    telegram_sent = (
        send_telegram_message(
            message
        )
    )

    print(
        f"Qualified signals: "
        f"{len(signals)}"
    )

    print(
        "Telegram sent: "
        f"{telegram_sent}"
    )

    print("")
    print(
        "SCAN COMPLETED"
    )
    print(
        "No live trades were placed."
    )
    print("")


# ============================================================
# NEWS SCAN
# ============================================================

def run_news_scan():
    """
    Run a basic news scan for the
    configured watchlist.
    """

    watchlist = getattr(
        cfg,
        "WATCHLIST",
        [],
    )

    news_results = int(
        getattr(
            cfg,
            "NEWS_RESULTS",
            5,
        )
    )

    news_per_ticker = int(
        getattr(
            cfg,
            "NEWS_PER_TICKER",
            2,
        )
    )

    lines = [
        "📰 SHtrading NEWS",
        "",
    ]

    found = 0

    for ticker in watchlist:

        try:

            items = search_news(
                ticker,
                news_results,
            )

            for item in items[
                :news_per_ticker
            ]:

                lines.extend(
                    [
                        (
                            f"{ticker}: "
                            f"{item.title}"
                        ),
                        (
                            f"Source: "
                            f"{item.source}"
                        ),
                        (
                            f"{item.link}"
                        ),
                        "",
                    ]
                )

                found += 1

        except Exception as exc:

            print(
                f"News failed for "
                f"{ticker}: {exc}"
            )

    if found == 0:

       
