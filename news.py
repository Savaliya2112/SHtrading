"""
News collection module.

This version uses Google News RSS.

News is contextual information and is NOT treated as a guaranteed
buy/sell signal.
"""

from dataclasses import dataclass
from urllib.parse import quote

import requests
import xml.etree.ElementTree as ET


@dataclass
class NewsItem:

    title: str

    link: str

    published: str

    source: str


def search_news(
    query,
    limit=8,
):
    """
    Search recent news through Google News RSS.
    """

    url = (
        "https://news.google.com/rss/search"
        "?q="
        + quote(query)
        + "&hl=en-US&gl=US&ceid=US:en"
    )

    response = requests.get(
        url,
        timeout=15,
        headers={
            "User-Agent":
                "SHtrading/1.0"
        },
    )

    response.raise_for_status()

    root = ET.fromstring(
        response.text
    )

    results = []

    items = root.findall(
        "./channel/item"
    )

    for item in items[:limit]:

        title = (
            item.findtext("title")
            or ""
        )

        link = (
            item.findtext("link")
            or ""
        )

        published = (
            item.findtext("pubDate")
            or ""
        )

        source_node = item.find(
            "source"
        )

        source = (
            source_node.text
            if source_node is not None
            else ""
        )

        results.append(
            NewsItem(
                title=title,
                link=link,
                published=published,
                source=source,
            )
        )

    return results
