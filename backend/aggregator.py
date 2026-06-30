"""
Pulls headlines from RSS feeds defined in config.py.
No API key needed — RSS is open and free.
"""
import feedparser
import asyncio
import httpx
import time
from typing import List
from models import Article
from config import RSS_FEEDS, FEED_CACHE_SECONDS

_cache = {"timestamp": 0, "articles": []}


async def _fetch_one_feed(client: httpx.AsyncClient, feed_info: dict) -> List[Article]:
    """Fetch and parse a single RSS feed. Returns empty list on failure (don't let one bad feed kill the batch)."""
    try:
        resp = await client.get(feed_info["url"], timeout=10.0, follow_redirects=True)
        parsed = feedparser.parse(resp.content)
        articles = []
        for entry in parsed.entries[:20]:  # cap per source so one feed doesn't dominate
            articles.append(
                Article(
                    title=entry.get("title", "").strip(),
                    link=entry.get("link", ""),
                    source=feed_info["name"],
                    category=feed_info["category"],
                    published=entry.get("published", None),
                )
            )
        return articles
    except Exception as e:
        print(f"[aggregator] Failed to fetch {feed_info['name']}: {e}")
        return []


async def fetch_all_articles(force_refresh: bool = False) -> List[Article]:
    """Fetch from all configured RSS feeds concurrently, with simple time-based caching."""
    now = time.time()
    if not force_refresh and (now - _cache["timestamp"]) < FEED_CACHE_SECONDS and _cache["articles"]:
        return _cache["articles"]

    async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0 (NewsCheckBot/1.0)"}) as client:
        results = await asyncio.gather(*[_fetch_one_feed(client, feed) for feed in RSS_FEEDS])

    all_articles = [article for batch in results for article in batch if article.title]

    _cache["timestamp"] = now
    _cache["articles"] = all_articles
    return all_articles
