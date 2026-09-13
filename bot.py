from __future__ import annotations
import sys, urllib.parse, urllib.request
import config
from scanner import scan_symbol
from universe import all_symbols
from news import get_news

def send_telegram(message):
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        print(message); return False
    data=urllib.parse.urlencode({"chat_id":config.TELEGRAM_CHAT_ID,"text":message}).encode()
    url=f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        urllib.request.urlopen(urllib.request.Request(url,data=data),timeout=15).read()
        return True
    except Exception as e:
        print("Telegram error:",e); return False

def format_signal(s):
    return (f"📈 {s.symbol} BUY\nScore {s.score:.0f}/5 | Confidence {s.confidence:.0f}%\n"
            f"Price {s.price:.2f}\nStop {s.stop:.2f}\nTarget {s.target:.2f}\n"
            f"Reasons: {', '.join(s.reasons)}")

def ask(symbol):
    s=scan_symbol(symbol.upper())
    return format_signal(s) if s else f"WAIT — no qualifying BUY signal for {symbol.upper()}."

def scan():
    hits=[]
    for symbol in all_symbols():
        s=scan_symbol(symbol)
        if s: hits.append(format_signal(s))
    message="\n\n".join(hits) if hits else "🔎 Scan complete: no qualifying signals."
    send_telegram(message)
    return hits

def news(symbol):
    items=get_news(symbol.upper())
    message="\n".join("📰 "+x["title"] for x in items) or "No news found."
    send_telegram(message); return message

def main():
    args=[a for a in sys.argv[1:]]
    if not args: scan(); return
    cmd=args[0].lower()
    if cmd=="scan": scan()
    elif cmd=="ask" and len(args)>=2 and args[1].lower()=="news":
        news(args[2] if len(args)>2 else "NVDA")
    elif cmd=="ask" and len(args)>=2:
        msg=ask(args[1]); send_telegram(msg); print(msg)
    elif cmd=="news":
        news(args[1] if len(args)>1 else "NVDA")
    else:
        print("Usage: python bot.py [scan|news SYMBOL|ask SYMBOL|ask news SYMBOL]")

if __name__=="__main__": main()
