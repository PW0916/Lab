# Agentic AI Daily News Agent

An automated agent that collects, filters, and publishes daily news reports focused on **agentic AI** — autonomous agents, multi-agent systems, agent frameworks, and related industry developments.

## What it does

1. **Fetches** news from RSS feeds (VentureBeat, TechCrunch, The Verge, MIT Tech Review, Google News, Hacker News) and web search
2. **Filters** articles using relevance scoring against agentic AI keywords (agents, LangGraph, CrewAI, MCP, etc.)
3. **Generates** a structured Markdown daily report with executive summary and categorized sections
4. **Publishes** a **news website** in `docs/` with homepage, daily report pages, and archive
5. **Deploys** automatically to GitHub Pages every day at 08:00 UTC

## News website

After each run, the agent builds a static news site in `docs/`:

| Page | URL |
|------|-----|
| Homepage | `docs/index.html` |
| Daily report | `docs/reports/YYYY-MM-DD.html` |

Once merged and GitHub Pages is enabled, the site will be live at:

**https://pw0916.github.io/Lab/**

To enable GitHub Pages: go to **Settings → Pages → Build and deployment → Source: GitHub Actions**.

## Quick start

```bash
# Install dependencies
pip install -e .

# Generate today's report and website
agentic-news

# Print full report to terminal
agentic-news --print-report

# Rebuild website from saved data (no network fetch)
agentic-news --rebuild-website

# Customize lookback window and article count
agentic-news --lookback-hours 72 --max-articles 50 --verbose
```

Reports are saved to `reports/YYYY-MM-DD.md` and `reports/YYYY-MM-DD.json`.

## Daily automation

Two GitHub Actions workflows run automatically:

- **Daily Agentic AI News Report** — fetches news, generates report + website, commits to repo
- **Deploy News Website** — publishes `docs/` to GitHub Pages on every push to `main`

You can also trigger them manually from the **Actions** tab.

## Configuration

Edit `src/agentic_news_agent/config.py` to customize:

- **RSS sources** — add or remove news feeds
- **Keywords** — tune relevance filtering for agentic AI topics
- **Search queries** — web search terms
- **Defaults** — max articles, lookback hours, report/website directories

## Project structure

```
src/agentic_news_agent/
├── agent.py       # Main orchestrator
├── config.py      # Sources, keywords, settings
├── fetcher.py     # RSS + web search collection
├── filter.py      # Relevance scoring and deduplication
├── reporter.py    # Markdown report generation
├── website.py     # HTML news website generator
├── storage.py     # JSON persistence for rebuilds
└── main.py        # CLI entry point
docs/              # Generated news website (deployed to GitHub Pages)
reports/           # Generated daily reports (Markdown + JSON)
```

## Requirements

- Python 3.11+
- Network access for RSS feeds and web search
