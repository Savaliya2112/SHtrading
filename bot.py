from __future__ import annotations

import sys
import threading
import time
import traceback

import requests

import config as cfg
from news import format_news, search_news
from scanner import scan_all_markets
from data_provider import get_ohlcv
from strategy import generate_signal


def telegram(method, payload=None, timeout=30):
    if not cfg.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
    url = f"https://api.telegram.org/bot{cfg.TELEGRAM_BOT_TOKEN}/{method}"
    response = requests.post(url, json=payload or {}, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(str(data))
    return data


def send_message(message, chat_id=None):
    target = chat_id or cfg.TELEGRAM_CHAT_ID
    if not target:
        print(message)
        return False
    telegram("sendMessage", {
        "chat_id": target,
        "text": message,
        "disable_web_page_preview": True,
    })
    return True


def format_signal(signal):
    return "\n".join([
        "🚨 SHtrading SIGNAL",
        "",
        f"Ticker: {signal.ticker}",
        f"Direction: {signal.direction}",
        f"Timeframe: {signal.timeframe}",
        f"Score: {signal.score}/{signal.max_score}",
        f"Price: {signal.close:.2f}",
        f"Stop: {signal.stop_loss:.2f}",
        f"Target: {signal.take_profit:.2f}",
        "",
        "Reasons:",
        *[f"• {r}" for r in signal.reasons],
        "",
        "⚠️ ALERT ONLY — you execute the order manually.",
    ])


def format_market_report(signals):
    if not signals:
        return "🤖 SHtrading\n\nNo new qualifying signals found."
    return "\n\n".join(format_signal(s) for s in signals[:cfg.MAX_ALERTS])


def ask_market(ticker):
    results = []
    for timeframe in ("1h", "1d"):
        try:
            period = cfg.INTRADAY_PERIOD if timeframe == "1h" else cfg.DAILY_PERIOD
            df = get_ohlcv(ticker, period=period, interval=timeframe)
            signal = generate_signal(ticker, timeframe, df, cfg)
            if signal:
                results.append(signal)
        except Exception as exc:
            print(f"ASK {ticker} {timeframe}: {exc}")

    if not results:
        return f"🔎 {ticker}\n\nNo qualifying signal on 1H or 1D."

    return "\n\n".join(
        [f"🔎 ASK — {ticker}"] +
        [format_signal(s) for s in results]
    )


def process_command(text):
    command = text.strip()
    upper = command.upper()

    if upper in ("/START", "/HELP", "HELP", "ASK HELP"):
        return (
            "🤖 SHtrading\n\n"
            "ASK NVDA — technical analysis\n"
            "ASK NEWS NVDA — recent news\n"
            "ASK MARKET — current new signals\n"
            "HELP — commands"
        )

    if upper in ("ASK MARKET", "MARKET", "/MARKET"):
        return format_market_report(scan_all_markets(only_new=False))

    if upper.startswith("ASK NEWS "):
        ticker = command[9:].strip().upper()
        return format_news(ticker, search_news(ticker, cfg.NEWS_RESULTS))

    if upper.startswith("NEWS "):
        ticker = command[5:].strip().upper()
        return format_news(ticker, search_news(ticker, cfg.NEWS_RESULTS))

    if upper.startswith("ASK "):
        ticker = command[4:].strip().upper()
        return ask_market(ticker) if ticker else "Usage: ASK NVDA"

    if len(command) <= 12 and " " not in command and not command.startswith("/"):
        return ask_market(command.upper())

    return "Usage: ASK NVDA | ASK NEWS NVDA | ASK MARKET | HELP"


def run_scan():
    signals = scan_all_markets(only_new=True)
    message = format_market_report(signals)
    send_message(message)
    return 0


def run_news():
    # News workflow can set NEWS_TICKERS; otherwise scan the broad index ETF set.
    import os
    tickers = [
        x.strip().upper()
        for x in os.getenv("NEWS_TICKERS", "QQQ,NVDA,AAPL,MSFT,TSLA").split(",")
        if x.strip()
    ]
    for ticker in tickers:
        try:
            items = search_news(ticker, cfg.NEWS_RESULTS)
            send_message(format_news(ticker, items))
        except Exception as exc:
            print(f"News {ticker}: {exc}")
    return 0


def telegram_polling():
    if not cfg.TELEGRAM_BOT_TOKEN:
        print("Telegram polling disabled: token missing.")
        return

    offset = None
    print("Telegram listener started.")

    while True:
        try:
            params = {"timeout": 30}
            if offset is not None:
                params["offset"] = offset

            data = telegram("getUpdates", params, timeout=40)

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                message = update.get("message") or {}
                text = message.get("text", "")
                chat_id = (message.get("chat") or {}).get("id")

                if not text or chat_id is None:
                    continue

                try:
                    answer = process_command(text)
                    send_message(answer, chat_id=chat_id)
                except Exception as exc:
                    traceback.print_exc()
                    send_message(f"ASK error: {exc}", chat_id=chat_id)

        except Exception as exc:
            print(f"Telegram polling error: {exc}")
            time.sleep(10)


def run_server():
    thread = threading.Thread(target=telegram_polling, daemon=True)
    thread.start()
    print("SHtrading Telegram server running.")
    while True:
        time.sleep(60)


if __name__ == "__main__":
    command = sys.argv[1].lower() if len(sys.argv) > 1 else "server"

    if command == "scan":
        raise SystemExit(run_scan())
    elif command == "news":
        raise SystemExit(run_news())
    elif command in ("server", "telegram"):
        run_server()
    else:
        print("Usage: python bot.py [scan|news|server]")
        raise SystemExit(2)
