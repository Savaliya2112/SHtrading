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
    Search Google News RSS for a ticker/company.

    Returns a list of NewsItem objects.
    """

    query_encoded = quote(
        str(query)
    )

    url = (
        "https://news.google.com/rss/search"
        f"?q={query_encoded}"
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
        response.text
    )

    results = []

    items = root.findall(
        "./channel/item"
    )

    for item in items[:int(limit)]:

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

        if source_node is not None:
            source = (
                source_node.text
                or ""
            )
        else:
            source = ""

        results.append(
            NewsItem(
                title=title,
                link=link,
                published=published,
                source=source,
            )
        )

    return results


if __name__ == "__main__":

    results = search_news(
        "NVIDIA",
        limit=5,
    )

    for item in results:

        print(
            item.title
        )

        print(
            item.source
        )

        print(
            item.link
        )

        print(
            item.published
        )

        print("-" * 50)
