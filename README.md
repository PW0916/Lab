# Agentic AI Daily News Agent

An automated agent that collects, filters, and publishes daily news reports focused on **agentic AI** — autonomous agents, multi-agent systems, agent frameworks, and related industry developments.

## What it does

1. **Fetches** news from RSS feeds (VentureBeat, TechCrunch, The Verge, MIT Tech Review, Google News, Hacker News) and web search (DuckDuckGo News)
2. **Filters** articles using relevance scoring against agentic AI keywords (agents, LangGraph, CrewAI, MCP, etc.)
3. **Generates** a structured Markdown daily report with executive summary and categorized sections
4. **Publishes** automatically via GitHub Actions every day at 08:00 UTC

## Quick start

```bash
# Install dependencies
pip install -e .

# Generate today's report
agentic-news

# Print full report to terminal
agentic-news --print-report

# Customize lookback window and article count
agentic-news --lookback-hours 72 --max-articles 50 --verbose
```

Reports are saved to `reports/YYYY-MM-DD.md`.

## Daily automation

The GitHub Actions workflow (`.github/workflows/daily-agentic-ai-news.yml`) runs on a cron schedule and commits new reports to this repository. You can also trigger it manually from the **Actions** tab → **Daily Agentic AI News Report** → **Run workflow**.

## Configuration

Edit `src/agentic_news_agent/config.py` to customize:

- **RSS sources** — add or remove news feeds
- **Keywords** — tune relevance filtering for agentic AI topics
- **Search queries** — DuckDuckGo news search terms
- **Defaults** — max articles, lookback hours, report directory

## Project structure

```
src/agentic_news_agent/
├── agent.py       # Main orchestrator
├── config.py      # Sources, keywords, settings
├── fetcher.py     # RSS + web search collection
├── filter.py      # Relevance scoring and deduplication
├── reporter.py    # Markdown report generation
└── main.py        # CLI entry point
reports/           # Generated daily reports (auto-committed)
```

## Example report sections

- **Executive Summary** — top 5 headlines
- **Industry & Product News** — product launches, company announcements
- **Research & Analysis** — academic and analytical coverage
- **Trending Topics** — search-driven discoveries
- **Community & Developer** — Hacker News and developer community

## Requirements

- Python 3.11+
- Network access for RSS feeds and web search
