"""Fetch news from RSS feeds and web search."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

import feedparser
import requests
from dateutil import parser as date_parser
from ddgs import DDGS

from .config import AgentConfig, DEFAULT_CONFIG
from .models import NewsArticle

logger = logging.getLogger(__name__)

USER_AGENT = (
    "AgenticNewsAgent/1.0 (+https://github.com/PW0916/Lab; daily agentic AI news bot)"
)


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except (TypeError, ValueError, OverflowError):
        pass
    try:
        dt = date_parser.parse(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        return None


def _clean_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _within_lookback(published: datetime | None, lookback_hours: int) -> bool:
    if published is None:
        return True
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    return published >= cutoff


def fetch_rss(config: AgentConfig = DEFAULT_CONFIG) -> list[NewsArticle]:
    articles: list[NewsArticle] = []
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    for source in config.rss_sources:
        try:
            response = session.get(source.url, timeout=20)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
        except requests.RequestException as exc:
            logger.warning("Failed to fetch RSS from %s: %s", source.name, exc)
            continue

        for entry in feed.entries:
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()
            if not title or not link:
                continue

            published = _parse_date(getattr(entry, "published", None) or getattr(entry, "updated", None))
            if not _within_lookback(published, config.lookback_hours):
                continue

            summary = _clean_html(getattr(entry, "summary", "") or getattr(entry, "description", ""))
            articles.append(
                NewsArticle(
                    title=title,
                    url=link,
                    source=source.name,
                    published=published,
                    summary=summary[:500],
                    category=source.category,
                )
            )

    logger.info("Fetched %d articles from RSS feeds", len(articles))
    return articles


def fetch_web_search(config: AgentConfig = DEFAULT_CONFIG) -> list[NewsArticle]:
    articles: list[NewsArticle] = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=config.lookback_hours)

    try:
        with DDGS() as ddgs:
            for query in config.search_queries:
                try:
                    results = ddgs.news(query, max_results=8)
                except Exception as exc:
                    logger.warning("Web search failed for query '%s': %s", query, exc)
                    continue

                for item in results:
                    title = (item.get("title") or "").strip()
                    url = (item.get("url") or item.get("href") or "").strip()
                    if not title or not url:
                        continue

                    published = _parse_date(item.get("date"))
                    if published and published < cutoff:
                        continue

                    source_name = item.get("source") or urlparse(url).netloc or "Web Search"
                    body = (item.get("body") or "").strip()

                    articles.append(
                        NewsArticle(
                            title=title,
                            url=url,
                            source=f"Search: {source_name}",
                            published=published,
                            summary=body[:500],
                            category="search",
                        )
                    )
    except Exception as exc:
        logger.warning("DuckDuckGo search unavailable: %s", exc)

    logger.info("Fetched %d articles from web search", len(articles))
    return articles


def fetch_all(config: AgentConfig = DEFAULT_CONFIG) -> list[NewsArticle]:
    rss_articles = fetch_rss(config)
    search_articles = fetch_web_search(config)
    return rss_articles + search_articles
