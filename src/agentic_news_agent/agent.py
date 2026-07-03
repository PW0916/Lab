"""Main news agent orchestrator."""

from __future__ import annotations

import logging
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from .config import AgentConfig, DEFAULT_CONFIG
from .fetcher import fetch_all
from .filter import filter_and_rank
from .models import NewsArticle
from .reporter import generate_report, save_report

logger = logging.getLogger(__name__)


class AgenticNewsAgent:
    """Collects, filters, and reports on agentic AI news."""

    def __init__(self, config: AgentConfig | None = None) -> None:
        self.config = config or DEFAULT_CONFIG

    def run(self, report_date: datetime | None = None) -> tuple[list[NewsArticle], Path]:
        logger.info("Starting agentic AI news collection...")
        raw = fetch_all(self.config)
        logger.info("Collected %d raw articles", len(raw))

        filtered = filter_and_rank(raw, self.config)
        logger.info("Filtered to %d relevant articles", len(filtered))

        report = generate_report(filtered, self.config, report_date)
        path = save_report(report, self.config, report_date)
        logger.info("Report saved to %s", path)

        return filtered, path

    @classmethod
    def from_cli_args(
        cls,
        max_articles: int | None = None,
        lookback_hours: int | None = None,
        report_dir: str | None = None,
    ) -> AgenticNewsAgent:
        config = DEFAULT_CONFIG
        updates = {}
        if max_articles is not None:
            updates["max_articles"] = max_articles
        if lookback_hours is not None:
            updates["lookback_hours"] = lookback_hours
        if report_dir is not None:
            updates["report_dir"] = report_dir
        if updates:
            config = replace(config, **updates)
        return cls(config)
