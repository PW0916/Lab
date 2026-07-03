"""Filter and rank news articles for agentic AI relevance."""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse, urlunparse

from .config import AgentConfig, DEFAULT_CONFIG
from .models import NewsArticle


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    if "news.google.com" in parsed.netloc:
        qs = parse_qs(parsed.query)
        if "url" in qs:
            return qs["url"][0]
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", "", ""))


def _score_article(article: NewsArticle, keywords: list[str]) -> tuple[float, list[str]]:
    text = f"{article.title} {article.summary}".lower()
    matched: list[str] = []
    score = 0.0

    for keyword in keywords:
        pattern = re.escape(keyword.lower())
        if re.search(rf"\b{pattern}\b", text) or keyword.lower() in text:
            matched.append(keyword)
            weight = 2.0 if " " in keyword else 1.0
            score += weight

    agent_terms = ("agent", "agentic", "autonomous", "multi-agent", "orchestrat")
    ai_terms = ("ai", "artificial intelligence", "llm", "gpt", "claude", "gemini")

    has_agent = any(term in text for term in agent_terms)
    has_ai = any(term in text for term in ai_terms)

    if has_agent and has_ai:
        score += 3.0
    elif has_agent:
        score += 1.5

    framework_terms = ("langgraph", "crewai", "autogen", "swarm", "mcp", "cursor", "devin")
    if any(term in text for term in framework_terms):
        score += 2.0

    return score, matched


def filter_and_rank(
    articles: list[NewsArticle],
    config: AgentConfig = DEFAULT_CONFIG,
) -> list[NewsArticle]:
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    scored: list[NewsArticle] = []

    for article in articles:
        norm_url = _normalize_url(article.url)
        dedup_key = article.dedup_key()

        if norm_url in seen_urls or dedup_key in seen_titles:
            continue

        score, matched = _score_article(article, config.keywords)
        if score < 1.0:
            continue

        article.relevance_score = score
        article.matched_keywords = matched
        seen_urls.add(norm_url)
        seen_titles.add(dedup_key)
        scored.append(article)

    scored.sort(
        key=lambda a: (
            a.relevance_score,
            a.published.timestamp() if a.published else 0,
        ),
        reverse=True,
    )

    return scored[: config.max_articles]
