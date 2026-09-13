from __future__ import annotations

from typing import Any

import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


def get_news(
    symbol: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Retrieve recent news headlines using Google News RSS.

    This is informational only. No trading orders are placed.
    """

    symbol = str(symbol).strip().upper()

    if not symbol:
        return []

    query = urllib.parse.quote(
        f"{symbol} stock"
    )

    url = (
        "https://news.google.com/rss/search?"
        f"q={query}&"
        "hl=en-US&"
        "gl=US&"
        "ceid=US:en"
    )

    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "SHtrading/1.0"
                )
            },
        )

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:
            content = response.read()

        root = ET.fromstring(content)

        results: list[dict[str, Any]] = []

        for item in root.findall(
            "./channel/item"
        ):

            title = item.findtext(
                "title",
                default="",
            ).strip()

            link = item.findtext(
                "link",
                default="",
            ).strip()

            published = item.findtext(
                "pubDate",
                default="",
            ).strip()

            source_element = item.find(
                "source"
            )

            source = ""

            if source_element is not None:
                source = (
                    source_element.text or ""
                ).strip()

            if not title:
                continue

            results.append(
                {
                    "title": title,
                    "link": link,
                    "published": published,
                    "source": source,
                }
            )

            if len(results) >= int(limit):
                break

        return results

    except Exception as exc:
        print(
            f"[NEWS ERROR] {symbol}: {exc}"
        )
        return []


def get_latest_news(
    symbol: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Compatibility alias for callers that use
    get_latest_news
