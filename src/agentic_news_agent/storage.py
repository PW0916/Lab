"""Serialize and deserialize news articles for website rebuilds."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .config import AgentConfig, DEFAULT_CONFIG
from .models import NewsArticle


def _article_to_dict(article: NewsArticle) -> dict:
    return {
        "title": article.title,
        "url": article.url,
        "source": article.source,
        "published": article.published.isoformat() if article.published else None,
        "summary": article.summary,
        "category": article.category,
        "relevance_score": article.relevance_score,
        "matched_keywords": article.matched_keywords,
    }


def _article_from_dict(data: dict) -> NewsArticle:
    published = None
    if data.get("published"):
        published = datetime.fromisoformat(data["published"])
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
    return NewsArticle(
        title=data["title"],
        url=data["url"],
        source=data["source"],
        published=published,
        summary=data.get("summary", ""),
        category=data.get("category", "general"),
        relevance_score=data.get("relevance_score", 0.0),
        matched_keywords=data.get("matched_keywords", []),
    )


def save_articles(
    articles: list[NewsArticle],
    config: AgentConfig = DEFAULT_CONFIG,
    report_date: datetime | None = None,
) -> Path:
    now = report_date or datetime.now(timezone.utc)
    report_dir = Path(config.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    path = report_dir / f"{now.strftime('%Y-%m-%d')}.json"
    payload = {
        "date": now.strftime("%Y-%m-%d"),
        "generated_at": now.isoformat(),
        "articles": [_article_to_dict(a) for a in articles],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def load_articles(path: Path) -> tuple[datetime, list[NewsArticle]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    generated = datetime.fromisoformat(payload["generated_at"])
    if generated.tzinfo is None:
        generated = generated.replace(tzinfo=timezone.utc)
    articles = [_article_from_dict(item) for item in payload["articles"]]
    return generated, articles


def load_all_saved_reports(config: AgentConfig = DEFAULT_CONFIG) -> list[tuple[datetime, list[NewsArticle]]]:
    report_dir = Path(config.report_dir)
    results: list[tuple[datetime, list[NewsArticle]]] = []
    for json_file in sorted(report_dir.glob("*.json"), reverse=True):
        results.append(load_articles(json_file))
    return results
