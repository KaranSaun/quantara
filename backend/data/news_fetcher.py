"""
APEX OS — News Fetcher
RSS feeds + NewsAPI for market news pipeline.
Deduplication via fuzzy title matching.
"""

import asyncio
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Optional

import httpx
import feedparser
from config import NEWS_API_KEY, RSS_FEEDS

logger = logging.getLogger("apex.news_fetcher")


def _title_hash(title: str) -> str:
    """Create fuzzy hash for deduplication."""
    normalized = title.lower().strip()
    # Remove common filler words
    for word in ["the", "a", "an", "is", "are", "was", "were", "in", "on", "at"]:
        normalized = normalized.replace(f" {word} ", " ")
    return hashlib.md5(normalized.encode()).hexdigest()[:12]


async def fetch_rss_feeds(hours: int = 12) -> list[dict]:
    """Fetch all configured RSS feeds, deduplicate."""
    all_items = []
    seen_hashes = set()
    cutoff = datetime.now() - timedelta(hours=hours)

    for source, url in RSS_FEEDS.items():
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url)
                feed = feedparser.parse(resp.text)

            for entry in feed.entries[:20]:
                title = entry.get("title", "").strip()
                if not title:
                    continue

                h = _title_hash(title)
                if h in seen_hashes:
                    continue
                seen_hashes.add(h)

                pub_date = entry.get("published_parsed")
                if pub_date:
                    pub_dt = datetime(*pub_date[:6])
                    if pub_dt < cutoff:
                        continue
                else:
                    pub_dt = datetime.now()

                all_items.append({
                    "source": source,
                    "headline": title,
                    "url": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:500],
                    "published_at": pub_dt.isoformat(),
                    "fetched_at": datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"RSS fetch failed for {source}: {e}")
            continue

    logger.info(f"Fetched {len(all_items)} unique news items from RSS")
    return all_items


async def fetch_newsapi(query: str = "India stock market OR Nifty OR BankNifty") -> list[dict]:
    """Fetch from NewsAPI.org (free tier: 100 req/day)."""
    if not NEWS_API_KEY:
        logger.warning("NEWS_API_KEY not set, skipping NewsAPI")
        return []

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20,
        "apiKey": NEWS_API_KEY,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        items = []
        for article in data.get("articles", []):
            items.append({
                "source": f"newsapi_{article.get('source', {}).get('name', 'unknown')}",
                "headline": article.get("title", ""),
                "url": article.get("url", ""),
                "summary": article.get("description", "")[:500],
                "published_at": article.get("publishedAt", ""),
                "fetched_at": datetime.now().isoformat(),
            })
        return items
    except Exception as e:
        logger.error(f"NewsAPI fetch failed: {e}")
        return []


async def fetch_all_news(hours: int = 12) -> list[dict]:
    """Fetch from all sources and merge."""
    rss_items = await fetch_rss_feeds(hours)
    api_items = await fetch_newsapi()

    # Deduplicate across sources
    seen = set()
    merged = []
    for item in rss_items + api_items:
        h = _title_hash(item["headline"])
        if h not in seen:
            seen.add(h)
            merged.append(item)

    logger.info(f"Total unique news items: {len(merged)}")
    return merged
