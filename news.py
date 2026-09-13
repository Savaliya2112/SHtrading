from __future__ import annotations
import urllib.parse
import xml.etree.ElementTree as ET
import urllib.request

def get_news(symbol: str, limit: int = 5):
    q = urllib.parse.quote(f"{symbol} stock")
    url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            root = ET.fromstring(r.read())
        out = []
        for item in root.findall("./channel/item")[:limit]:
            out.append({
                "title": item.findtext("title", ""),
                "link": item.findtext("link", ""),
                "published": item.findtext("pubDate", ""),
            })
        return out
    except Exception:
        return []
