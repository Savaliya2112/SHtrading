from __future__ import annotations

import email.utils
import time
import urllib.parse
import xml.etree.ElementTree as ET

import requests


def search_news(ticker, limit=5):
    query = urllib.parse.quote(f"{ticker} stock")
    url = (
        "https://news.google.com/rss/search?"
        f"q={query}&hl=en-US&gl=US&ceid=US:en"
    )

    response = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "SHtrading/1.0"}
    )
    response.raise_for_status()

    root = ET.fromstring(response.text)
    items = []

    for item in root.findall("./channel/item")[:limit]:
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        pub = item.findtext("pubDate") or ""

        age_hours = None
        try:
            dt = email.utils.parsedate_to_datetime(pub)
            age_hours = max(0, (time.time() - dt.timestamp()) / 3600)
        except Exception:
            pass

        items.append({
            "title": title,
            "link": link,
            "published": pub,
            "age_hours": age_hours,
        })

    return items


def format_news(ticker, items):
    if not items:
        return f"📰 {ticker}\n\nNo recent headlines found."

    lines = [f"📰 NEWS — {ticker}", ""]

    for item in items:
        age = item["age_hours"]
        age_text = f"{age:.1f}h ago" if age is not None else item["published"]
        lines.append(f"• {item['title']}")
        lines.append(f"  {age_text}")
        lines.append(f"  {item['link']}")
        lines.append("")

    return "\n".join(lines)
