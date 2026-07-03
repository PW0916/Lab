"""Data models for news articles."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NewsArticle:
    title: str
    url: str
    source: str
    published: datetime | None = None
    summary: str = ""
    category: str = "general"
    relevance_score: float = 0.0
    matched_keywords: list[str] = field(default_factory=list)

    @property
    def published_display(self) -> str:
        if self.published is None:
            return "Unknown date"
        return self.published.strftime("%Y-%m-%d %H:%M UTC")

    def dedup_key(self) -> str:
        normalized = self.title.lower().strip()
        for ch in ".,!?:;\"'":
            normalized = normalized.replace(ch, "")
        return normalized
