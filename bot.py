"""
SHtrading scanner bot.

Modes:

    python bot.py scan

    python bot.py daily

The bot sends alerts through Telegram.

It does NOT place live trades.
"""

import sys
import traceback

import requests

import config as cfg

from data_provider import get_ohlcv

from risk import build_risk_plan

from strategy import generate_signal

from news import search_news


def send_telegram_message(
    message,
):
    """
    Send message to Telegram.
    """

    if not cfg.TELEGRAM_BOT_TOKEN:
        print(
            "Telegram token not configured."
        )
        return

    if not cfg.TELEGRAM_CHAT_ID:
        print(
            "Telegram chat ID not configured."
        )
        return

    url = (
        "https://api.telegram.org/bot"
        + cfg.TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    payload = {
        "chat_id":
            cfg.TELEGRAM_CHAT_ID,

        "text":
            message,

        "disable_web_page_preview":
            True,
    }

    response = requests.post(
        url,
        data=payload,
        timeout=15,
    )

    if response.status_code != 200:

        print(
            "Telegram error:",
            response.status_code,
            response.text,
        )


def format_signal_message(
    signal,
):
    message = (
        f"🚨 {signal.direction} SIGNAL\n\n"

        f"Ticker: {signal.ticker}\n"

        f"Timeframe: {signal.timeframe}\n"

        f"Price: {signal.close:.2f}\n"

        f"Score: "
        f"{signal.score}/"
        f"{signal.max_score}\n\n"

        f"Stop Loss: "
        f"{signal.stop_loss:.2f}\n"

        f"Take Profit: "
        f"{signal.take_profit:.2f}\n\n"

        "Reasons:\n"
    )

    for reason in signal.reasons:

        message += (
            f"• {reason}\n"
        )

    plan = build_risk_plan(
        signal.close,
        signal.stop_loss,
        cfg.ACCOUNT_BALANCE_EUR,
        cfg.RISK_PER_TRADE_PCT,
        cfg.MAX_POSITION_PCT,
    )

    message += (
        "\nRisk plan:\n"
        f"Quantity: {plan.quantity}\n"
        f"Risk: €{plan.risk_eur:.2f}\n"
        f"Notional: €{plan.notional_eur:.2f}\n"
    )

    message += (
        "\n⚠️ Paper/research signal only. "
        "No live order was placed."
    )

    return message


def scan_ticker(
    ticker,
    timeframe,
):
    """
    Scan one ticker.
    """

    if timeframe == "1d":

        period = cfg.DAILY_PERIOD

    else:

        period = cfg.INTRADAY_PERIOD

    df = get_ohlcv(
        ticker,
        period=period,
        interval=timeframe,
    )

    return generate_signal(
        ticker,
        timeframe,
        df,
        cfg,
    )


def run_scan():

    print(
        f"Scanning {len(cfg.WATCHLIST)} markets..."
    )

    alerts = 0

    for ticker in cfg.WATCHLIST:

        for timeframe in (
            cfg.INTRADAY_TIMEFRAMES
            + [cfg.SWING_TIMEFRAME]
        ):

            try:

                signal = scan_ticker(
                    ticker,
                    timeframe,
                )

                if signal:

                    message = (
                        format_signal_message(
                            signal
                        )
                    )

                    send_telegram_message(
                        message
                    )

                    print(
                        message
                    )

                    alerts += 1

            except Exception:

                print(
                    f"Failed: "
                    f"{ticker} "
                    f"{timeframe}"
                )

                traceback.print_exc()

    print(
        f"Scan completed. "
        f"Signals: {alerts}"
    )


def run_news_scan():

    print(
        "News scan"
    )

    for ticker in cfg.WATCHLIST:

        try:

            items = search_news(
                ticker,
                cfg.NEWS_RESULTS,
            )

            if not items:
                continue

            message = (
                f"📰 NEWS: {ticker}\n\n"
            )

            for item in items[:5]:

                message += (
                    f"• {item.title}\n"
                    f"{item.source}\n\n"
                )

            send_telegram_message(
                message
            )

        except Exception as exc:

            print(
                f"News failed "
                f"{ticker}: {exc}"
            )


if __name__ == "__main__":

    mode = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "scan"
    )

    if mode == "news":

        run_news_scan()

    else:

        run_scan()
