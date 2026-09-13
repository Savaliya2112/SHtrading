from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request

from bot import ask, news


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"

OFFSET_FILE = "telegram_offset.txt"


def telegram_request(method: str, data: dict | None = None):
    url = f"{API}/{method}"

    if data:
        body = urllib.parse.urlencode(data).encode("utf-8")
        request = urllib.request.Request(url, data=body)
    else:
        request = urllib.request.Request(url)

    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def send_message(chat_id: int, text: str):
    telegram_request(
        "sendMessage",
        {
            "chat_id": str(chat_id),
            "text": text[:4096],
        },
    )


def load_offset() -> int:
    try:
        with open(OFFSET_FILE, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_offset(offset: int):
    with open(OFFSET_FILE, "w", encoding="utf-8") as f:
        f.write(str(offset))


def handle_message(chat_id: int, text: str):
    text = text.strip()

    if not text:
        return

    lower = text.lower()

    if lower in ("/start", "/help", "help"):
        send_message(
            chat_id,
            "🤖 SHtrading Bot\n\n"
            "Commands:\n"
            "ASK NVDA\n"
            "ASK AAPL\n"
            "ASK NEWS NVDA\n"
            "HELP\n\n"
            "The bot provides market data and analysis only.",
        )
        return

    if lower.startswith("ask news "):
        symbol = text[9:].strip().upper()

        if not symbol:
            send_message(chat_id, "Example: ASK NEWS NVDA")
            return

        result = news(symbol)
        send_message(chat_id, result)
        return

    if lower.startswith("ask "):
        symbol = text[4:].strip().upper()

        if not symbol:
            send_message(chat_id, "Example: ASK NVDA")
            return

        send_message(chat_id, "🔎 Analysing " + symbol + "...")

        try:
            result = ask(symbol)
            send_message(chat_id, result)
        except Exception as exc:
            send_message(
                chat_id,
                f"⚠️ Could not analyse {symbol}.\nError: {exc}",
            )

        return

    send_message(
        chat_id,
        "I didn't understand that.\n\n"
        "Try:\n"
        "ASK NVDA\n"
        "ASK NEWS NVDA\n"
        "HELP",
    )


def poll():
    if not TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is not configured."
        )

    offset = load_offset()

    print("SHtrading Telegram bot started.")

    while True:
        try:
            result = telegram_request(
                "getUpdates",
                {
                    "timeout": "50",
                    "offset": str(offset),
                    "allowed_updates": json.dumps(["message"]),
                },
            )

            if not result.get("ok"):
                print("Telegram API error:", result)
                time.sleep(5)
                continue

            for update in result.get("result", []):
                offset = update["update_id"] + 1
                save_offset(offset)

                message = update.get("message")

                if not message:
                    continue

                chat = message.get("chat", {})
                chat_id = chat.get("id")
                text = message.get("text", "")

                if chat_id is None:
                    continue

                handle_message(chat_id, text)

        except Exception as exc:
            print("Polling error:", exc)
            time.sleep(5)


if __name__ == "__main__":
    poll()
