from __future__ import annotations
import os
import sys
from indicators import add_indicators
from data_provider import download_history
from strategy import generate_signal
from universe import all_symbols, get_nasdaq100
from news import get_news
import config

def scan_symbol(symbol):
    try:
        df = download_history(symbol, config.HISTORY_PERIOD, "1d")
        if df.empty:
            return None
        return generate_signal(symbol, add_indicators(df), config.MIN_SCORE)
    except Exception as exc:
        return {"error": f"{symbol}: {exc}"}

def format_signal(s):
    if isinstance(s, dict):
        return f"⚠️ {s['error']}"
    return (
        f"📈 {s.symbol} BUY signal\n"
        f"Score: {s.score:.0f}\nPrice: {s.price:.2f}\n"
        f"Stop: {s.stop:.2f}\nTarget: {s.target:.2f}\n"
        f"Reasons: {', '.join(s.reasons)}"
    )

def ask(symbol):
    symbol = symbol.upper().strip()
    s = scan_symbol(symbol)
    if s is None:
        return f"No qualifying BUY signal for {symbol} right now."
    return format_signal(s)

def send_telegram(text):
    token, chat_id = config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID
    if not token or not chat_id:
        print(text)
        return False
    import urllib.parse, urllib.request
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=15).read()
        return True
    except Exception as exc:
        print(f"Telegram error: {exc}")
        return False

def run_scan():
    hits = []
    for symbol in all_symbols():
        s = scan_symbol(symbol)
        if hasattr(s, "action"):
            hits.append(format_signal(s))
    message = "\n\n".join(hits) if hits else "🔎 Scan complete: no qualifying signals."
    send_telegram(message)
    return hits

def main():
    if len(sys.argv) >= 3 and sys.argv[1].lower() == "ask":
        if sys.argv[2].lower() == "news":
            symbol = sys.argv[3] if len(sys.argv) > 3 else "NVDA"
            items = get_news(symbol)
            text = "\n".join(f"• {x['title']}" for x in items) or "No news found."
            send_telegram(text)
            print(text)
        else:
            text = ask(sys.argv[2])
            send_telegram(text)
            print(text)
    else:
        run_scan()

if __name__ == "__main__":
    main()
