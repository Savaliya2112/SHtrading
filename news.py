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
    limit=5,
):
    """
    Search Google News RSS.

    Returns a list of NewsItem objects.
    """

    query = str(query).strip()

    if not query:
        return []

    try:
        limit = max(
            1,
            int(limit),
        )
    except (TypeError, ValueError):
        limit = 5

    url = (
        "https://news.google.com/rss/search"
        f"?q={quote(query)}"
        "&hl=en-US"
        "&gl=US"
        "&ceid=US:en"
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
        response.content
    )

    results = []

    for item in root.findall(
        "./channel/item"
    )[:limit]:

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

        source = ""

        if source_node is not None:
            source = (
                source_node.text
                or ""
            )

        results.append(
            NewsItem(
                title=title.strip(),
                link=link.strip(),
                published=published.strip(),
                source=source.strip(),
            )
        )

    return results


def format_news(
    query,
    items,
):
    """Create a readable news message."""

    lines = [
        f"📰 News: {query}",
        "",
    ]

    if not items:
        lines.append(
            "No recent news found."
        )

        return "\n".join(lines)

    for number, item in enumerate(
        items,
        start=1,
    ):

        lines.append(
            f"{number}. {item.title}"
        )

        if item.source:
            lines.append(
                f"Source: {item.source}"
            )

        if item.published:
            lines.append(
                f"Published: {item.published}"
            )

        if item.link:
            lines.append(
                item.link
            )

        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":

    items = search_news(
        "NVDA",
        5,
    )

    print(
        format_news(
            "NVDA",
            items,
        )
    )
