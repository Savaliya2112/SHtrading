from __future__ import annotations
import urllib.parse, urllib.request, xml.etree.ElementTree as ET

def get_news(symbol,limit=5):
    q=urllib.parse.quote(f"{symbol} stock")
    url=f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
    try:
        with urllib.request.urlopen(url,timeout=10) as r: root=ET.fromstring(r.read())
        out=[]
        for i in root.findall("./channel/item")[:limit]:
            out.append({"title":i.findtext("title",""),"link":i.findtext("link",""),
                        "published":i.findtext("pubDate","")})
        return out
    except Exception: return []
