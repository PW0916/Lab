"""Generate a static news website from daily reports."""

from __future__ import annotations

import html
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .config import AgentConfig, DEFAULT_CONFIG
from .models import NewsArticle
from .reporter import CATEGORY_LABELS

SITE_TITLE = "Agentic AI Daily"
SITE_TAGLINE = "Intelligence on autonomous agents & multi-agent systems"

CATEGORY_COLORS = {
    "industry": "#2563eb",
    "research": "#7c3aed",
    "search": "#0d9488",
    "community": "#d97706",
    "general": "#64748b",
}


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def _clean_text(text: str) -> str:
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _category_badge(category: str) -> str:
    labels = {
        "industry": "Industry",
        "research": "Research",
        "search": "Trending",
        "community": "Community",
        "general": "General",
    }
    return labels.get(category, category.title())


def _category_color(category: str) -> str:
    return CATEGORY_COLORS.get(category, "#64748b")


def _write_stylesheet(assets_dir: Path) -> None:
    assets_dir.mkdir(parents=True, exist_ok=True)
    css_path = assets_dir / "style.css"
    css_path.write_text(
        """\
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&display=swap');

:root {
  --bg: #f7f5f0;
  --bg-alt: #ffffff;
  --ink: #1c1917;
  --ink-soft: #44403c;
  --muted: #78716c;
  --line: #e7e5e4;
  --line-strong: #d6d3d1;
  --accent: #0f766e;
  --accent-soft: #ccfbf1;
  --accent-hover: #0d9488;
  --gold: #b45309;
  --shadow-sm: 0 1px 2px rgba(28, 25, 23, 0.04);
  --shadow-md: 0 8px 30px rgba(28, 25, 23, 0.06);
  --shadow-lg: 0 20px 50px rgba(28, 25, 23, 0.08);
  --radius: 16px;
  --radius-sm: 10px;
  --serif: "Cormorant Garamond", "Georgia", serif;
  --sans: "DM Sans", system-ui, sans-serif;
  --max: 1120px;
  --narrow: 720px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html { scroll-behavior: smooth; }

body {
  font-family: var(--sans);
  background: var(--bg);
  color: var(--ink);
  line-height: 1.65;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}

a { color: var(--accent); text-decoration: none; transition: color 0.15s; }
a:hover { color: var(--accent-hover); }

/* ── Header ── */
.site-header {
  background: rgba(247, 245, 240, 0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--line);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  max-width: var(--max);
  margin: 0 auto;
  padding: 1.1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
}

.logo-mark {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.logo-icon {
  width: 42px;
  height: 42px;
  background: linear-gradient(135deg, #0f766e 0%, #134e4a 100%);
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-family: var(--serif);
  font-size: 1.25rem;
  font-weight: 700;
  box-shadow: var(--shadow-sm);
}

.logo-text a {
  font-family: var(--serif);
  font-size: 1.55rem;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.02em;
  line-height: 1.1;
}

.logo-text span {
  display: block;
  font-family: var(--sans);
  font-size: 0.72rem;
  font-weight: 500;
  color: var(--muted);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-top: 0.15rem;
}

.nav-links {
  display: flex;
  gap: 0.25rem;
  list-style: none;
}

.nav-links a {
  color: var(--muted);
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.45rem 0.9rem;
  border-radius: 999px;
  transition: background 0.15s, color 0.15s;
}

.nav-links a:hover,
.nav-links a.active {
  color: var(--ink);
  background: var(--bg-alt);
  text-decoration: none;
}

/* ── Layout ── */
main {
  max-width: var(--max);
  margin: 0 auto;
  padding: 2.5rem 2rem 5rem;
}

.page-intro {
  text-align: center;
  max-width: var(--narrow);
  margin: 0 auto 3rem;
  padding-bottom: 2.5rem;
  border-bottom: 1px solid var(--line);
}

.edition-label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 1.25rem;
}

.edition-label::before,
.edition-label::after {
  content: "";
  width: 24px;
  height: 1px;
  background: var(--line-strong);
}

.page-intro h1 {
  font-family: var(--serif);
  font-size: clamp(2.4rem, 5vw, 3.5rem);
  font-weight: 600;
  line-height: 1.08;
  letter-spacing: -0.02em;
  color: var(--ink);
  margin-bottom: 1rem;
}

.page-intro .lede {
  font-size: 1.05rem;
  color: var(--ink-soft);
  line-height: 1.7;
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 1.75rem;
  font-size: 0.82rem;
  color: var(--muted);
}

.meta-row strong { color: var(--ink-soft); font-weight: 600; }

/* ── Lead story ── */
.lead-story {
  background: var(--bg-alt);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 2.25rem 2.5rem;
  margin-bottom: 3rem;
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}

.lead-story::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--accent), #14b8a6, var(--gold));
}

.lead-label {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 0.85rem;
}

.lead-story h2 {
  font-family: var(--serif);
  font-size: clamp(1.6rem, 3vw, 2.15rem);
  font-weight: 600;
  line-height: 1.25;
  margin-bottom: 1rem;
}

.lead-story h2 a {
  color: var(--ink);
  text-decoration: none;
}

.lead-story h2 a:hover { color: var(--accent); }

.lead-summary {
  font-size: 1.02rem;
  color: var(--ink-soft);
  line-height: 1.75;
  max-width: 62ch;
  margin-bottom: 1.5rem;
}

.lead-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  font-size: 0.82rem;
  color: var(--muted);
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--accent);
  color: white !important;
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.65rem 1.25rem;
  border-radius: 999px;
  transition: background 0.15s, transform 0.15s;
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
  background: var(--accent-hover);
  transform: translateY(-1px);
  text-decoration: none;
}

.btn-outline {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border: 1px solid var(--line-strong);
  color: var(--ink-soft) !important;
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.65rem 1.25rem;
  border-radius: 999px;
  background: var(--bg-alt);
  transition: border-color 0.15s, color 0.15s;
}

.btn-outline:hover {
  border-color: var(--accent);
  color: var(--accent) !important;
  text-decoration: none;
}

/* ── Section headers ── */
.section-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid var(--ink);
}

.section-header h2 {
  font-family: var(--serif);
  font-size: 1.65rem;
  font-weight: 600;
  color: var(--ink);
}

.section-header span {
  font-size: 0.78rem;
  color: var(--muted);
  font-weight: 500;
}

/* ── Headlines list ── */
.headlines-list {
  list-style: none;
  margin-bottom: 3.5rem;
}

.headlines-list li {
  display: grid;
  grid-template-columns: 2.5rem 1fr;
  gap: 1.25rem;
  padding: 1.35rem 0;
  border-bottom: 1px solid var(--line);
  align-items: start;
}

.headlines-list li:first-child { padding-top: 0; }

.headline-num {
  font-family: var(--serif);
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--line-strong);
  line-height: 1;
  padding-top: 0.1rem;
}

.headline-body a {
  font-family: var(--serif);
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--ink);
  line-height: 1.35;
  display: block;
  margin-bottom: 0.35rem;
}

.headline-body a:hover { color: var(--accent); }

.headline-source {
  font-size: 0.8rem;
  color: var(--muted);
  font-weight: 500;
}

/* ── Category sections ── */
.category-block {
  margin-bottom: 3.5rem;
}

.category-block .section-header {
  border-bottom-color: var(--line);
}

.category-block .section-header h2 {
  font-size: 1.35rem;
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.cat-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.articles-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.article-card {
  background: var(--bg-alt);
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 1.5rem 1.65rem;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 1rem 1.5rem;
  transition: box-shadow 0.2s, border-color 0.2s;
}

.article-card:hover {
  border-color: var(--line-strong);
  box-shadow: var(--shadow-md);
}

.card-main { min-width: 0; }

.card-top {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-bottom: 0.65rem;
}

.card-badge {
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
  background: var(--accent-soft);
  color: var(--accent);
}

.card-source {
  font-size: 0.78rem;
  color: var(--muted);
  font-weight: 500;
}

.article-card h3 {
  font-family: var(--serif);
  font-size: 1.15rem;
  font-weight: 600;
  line-height: 1.35;
  margin-bottom: 0.5rem;
}

.article-card h3 a {
  color: var(--ink);
  text-decoration: none;
}

.article-card h3 a:hover { color: var(--accent); }

.card-summary {
  font-size: 0.9rem;
  color: var(--ink-soft);
  line-height: 1.65;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-side {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.75rem;
  text-align: right;
}

.card-date {
  font-size: 0.75rem;
  color: var(--muted);
  white-space: nowrap;
}

.card-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  justify-content: flex-end;
}

.keyword-tag {
  font-size: 0.65rem;
  font-weight: 500;
  background: var(--bg);
  color: var(--muted);
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  border: 1px solid var(--line);
}

.read-link {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--accent);
  white-space: nowrap;
}

.read-link:hover { text-decoration: underline; }

/* ── Homepage hero ── */
.home-hero {
  text-align: center;
  padding: 3rem 1rem 3.5rem;
  margin-bottom: 3rem;
  background: var(--bg-alt);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
}

.home-hero h1 {
  font-family: var(--serif);
  font-size: clamp(2.2rem, 5vw, 3.2rem);
  font-weight: 600;
  line-height: 1.1;
  margin-bottom: 1rem;
}

.home-hero p {
  font-size: 1.05rem;
  color: var(--ink-soft);
  max-width: 520px;
  margin: 0 auto 2rem;
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.75rem;
}

/* ── Archive ── */
.archive-list {
  display: flex;
  flex-direction: column;
  gap: 0;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--bg-alt);
}

.archive-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--line);
  transition: background 0.15s;
}

.archive-item:last-child { border-bottom: none; }
.archive-item:hover { background: var(--bg); }

.archive-item a {
  font-family: var(--serif);
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--ink);
}

.archive-item a:hover { color: var(--accent); }

.archive-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-shrink: 0;
}

.archive-count {
  font-size: 0.78rem;
  color: var(--muted);
  background: var(--bg);
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  border: 1px solid var(--line);
}

.archive-arrow {
  color: var(--muted);
  font-size: 1.1rem;
}

/* ── Footer ── */
.site-footer {
  border-top: 1px solid var(--line);
  padding: 2.5rem 2rem;
  text-align: center;
  color: var(--muted);
  font-size: 0.85rem;
  background: var(--bg-alt);
}

.site-footer a { color: var(--accent); font-weight: 500; }

.empty-state {
  text-align: center;
  padding: 4rem 1.5rem;
  color: var(--muted);
  font-size: 1rem;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .header-inner { padding: 1rem 1.25rem; }
  main { padding: 1.75rem 1.25rem 3.5rem; }
  .lead-story { padding: 1.75rem 1.5rem; }
  .article-card {
    grid-template-columns: 1fr;
  }
  .card-side {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    text-align: left;
  }
  .card-keywords { justify-content: flex-start; }
  .nav-links { gap: 0; }
  .logo-text a { font-size: 1.3rem; }
}

@media (max-width: 480px) {
  .headlines-list li { grid-template-columns: 2rem 1fr; gap: 0.85rem; }
  .headline-num { font-size: 1.4rem; }
  .headline-body a { font-size: 1.05rem; }
}
""",
        encoding="utf-8",
    )


def _page_shell(
    title: str,
    body: str,
    active_nav: str = "home",
    base_path: str = "",
) -> str:
    home_href = f"{base_path}index.html"
    latest_href = f"{base_path}index.html#latest"
    archive_href = f"{base_path}index.html#archive"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{_esc(SITE_TAGLINE)}">
  <title>{_esc(title)} — {_esc(SITE_TITLE)}</title>
  <link rel="stylesheet" href="{base_path}assets/style.css">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🤖</text></svg>">
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <div class="logo-mark">
        <div class="logo-icon">A</div>
        <div class="logo-text">
          <a href="{home_href}">{_esc(SITE_TITLE)}</a>
          <span>{_esc(SITE_TAGLINE)}</span>
        </div>
      </div>
      <nav>
        <ul class="nav-links">
          <li><a href="{home_href}" class="{'active' if active_nav == 'home' else ''}">Home</a></li>
          <li><a href="{latest_href}" class="{'active' if active_nav == 'latest' else ''}">Latest</a></li>
          <li><a href="{archive_href}" class="{'active' if active_nav == 'archive' else ''}">Archive</a></li>
        </ul>
      </nav>
    </div>
  </header>
  <main>
    {body}
  </main>
  <footer class="site-footer">
    <p>Curated automatically by the
      <a href="https://github.com/PW0916/Lab">Agentic AI News Agent</a>
      · Updated daily at 08:00 UTC</p>
  </footer>
</body>
</html>"""


def _render_lead_story(article: NewsArticle) -> str:
    summary = f'<p class="lead-summary">{_esc(_clean_text(article.summary))}</p>' if article.summary else ""
    return f"""
    <section class="lead-story">
      <p class="lead-label">Lead Story</p>
      <h2><a href="{_esc(article.url)}" target="_blank" rel="noopener">{_esc(article.title)}</a></h2>
      {summary}
      <div class="lead-meta">
        <span>{_esc(article.source)}</span>
        <span>·</span>
        <span>{_esc(article.published_display)}</span>
        <a class="btn-primary" href="{_esc(article.url)}" target="_blank" rel="noopener">Read article →</a>
      </div>
    </section>"""


def _render_article_card(article: NewsArticle) -> str:
    keywords_html = ""
    if article.matched_keywords:
        tags = "".join(
            f'<span class="keyword-tag">{_esc(k)}</span>'
            for k in article.matched_keywords[:3]
        )
        keywords_html = f'<div class="card-keywords">{tags}</div>'

    summary = f'<p class="card-summary">{_esc(_clean_text(article.summary))}</p>' if article.summary else ""
    color = _category_color(article.category)

    return f"""
    <article class="article-card">
      <div class="card-main">
        <div class="card-top">
          <span class="card-badge" style="background:{color}18;color:{color}">{_esc(_category_badge(article.category))}</span>
          <span class="card-source">{_esc(article.source)}</span>
        </div>
        <h3><a href="{_esc(article.url)}" target="_blank" rel="noopener">{_esc(article.title)}</a></h3>
        {summary}
      </div>
      <div class="card-side">
        <span class="card-date">{_esc(article.published_display)}</span>
        {keywords_html}
        <a class="read-link" href="{_esc(article.url)}" target="_blank" rel="noopener">Read →</a>
      </div>
    </article>"""


def _render_report_page(
    articles: list[NewsArticle],
    report_date: datetime,
) -> str:
    display_date = report_date.strftime("%A, %B %d, %Y")
    time_str = report_date.strftime("%H:%M UTC")
    date_str = report_date.strftime("%Y-%m-%d")

    lead_html = ""
    headline_articles = articles
    if articles:
        lead_html = _render_lead_story(articles[0])
        headline_articles = articles[1:6]

    summary_items = ""
    for i, article in enumerate(headline_articles[:5], start=2 if articles else 1):
        summary_items += f"""
        <li>
          <span class="headline-num">{i:02d}</span>
          <div class="headline-body">
            <a href="{_esc(article.url)}" target="_blank" rel="noopener">{_esc(article.title)}</a>
            <span class="headline-source">{_esc(article.source)}</span>
          </div>
        </li>"""

    grouped: dict[str, list[NewsArticle]] = defaultdict(list)
    for article in articles:
        grouped[article.category].append(article)

    category_order = ["industry", "research", "search", "community", "general"]
    sections = ""

    for category in category_order:
        cat_articles = grouped.get(category, [])
        if not cat_articles:
            continue
        label = CATEGORY_LABELS.get(category, category.title())
        color = _category_color(category)
        cards = "".join(_render_article_card(a) for a in cat_articles)
        sections += f"""
        <section class="category-block">
          <div class="section-header">
            <h2><span class="cat-dot" style="background:{color}"></span>{_esc(label)}</h2>
            <span>{len(cat_articles)} stories</span>
          </div>
          <div class="articles-list">{cards}</div>
        </section>"""

    if not articles:
        sections = '<div class="empty-state"><p>No agentic AI news matched today. Check back tomorrow.</p></div>'

    headlines_section = ""
    if summary_items:
        headlines_section = f"""
    <div class="section-header" id="latest">
      <h2>Top Headlines</h2>
      <span>Editor's picks</span>
    </div>
    <ol class="headlines-list">{summary_items}</ol>"""

    body = f"""
    <header class="page-intro">
      <p class="edition-label">Daily Briefing</p>
      <h1>{_esc(display_date)}</h1>
      <p class="lede">A curated selection of the day's most important developments in agentic AI — from product launches and research breakthroughs to community discussions.</p>
      <div class="meta-row">
        <span><strong>{len(articles)}</strong> articles</span>
        <span>Generated <strong>{time_str}</strong></span>
        <span>Edition <strong>{_esc(date_str)}</strong></span>
      </div>
    </header>

    {lead_html}
    {headlines_section}
    {sections}
    """

    return _page_shell(
        f"Report — {date_str}",
        body,
        active_nav="latest",
        base_path="../",
    )


def _render_index_page(
    latest_date: str | None,
    archive: list[tuple[str, str, int]],
) -> str:
    if latest_date:
        display = _format_display_date(latest_date)
        hero = f"""
        <section class="home-hero">
          <p class="edition-label">Latest Edition</p>
          <h1>{_esc(display)}</h1>
          <p>Your daily intelligence briefing on autonomous agents, multi-agent orchestration, and the rapidly evolving agentic AI landscape.</p>
          <div class="hero-actions">
            <a class="btn-primary" href="reports/{_esc(latest_date)}.html">Read today's report →</a>
            <a class="btn-outline" href="#archive">Browse archive</a>
          </div>
        </section>"""
    else:
        hero = f"""
        <section class="home-hero">
          <p class="edition-label">Welcome</p>
          <h1>{_esc(SITE_TITLE)}</h1>
          <p>{_esc(SITE_TAGLINE)}. Daily reports will appear here once the agent runs.</p>
        </section>"""

    archive_items = ""
    for date_str, display, count in archive:
        archive_items += f"""
        <div class="archive-item">
          <a href="reports/{_esc(date_str)}.html">{_esc(display)}</a>
          <div class="archive-meta">
            <span class="archive-count">{count} articles</span>
            <span class="archive-arrow">→</span>
          </div>
        </div>"""

    if not archive_items:
        archive_items = '<div class="empty-state"><p>No archived reports yet.</p></div>'
    else:
        archive_items = f'<div class="archive-list">{archive_items}</div>'

    body = f"""
    {hero}

    <div class="section-header" id="archive">
      <h2>Report Archive</h2>
      <span>All editions</span>
    </div>
    {archive_items}
    """

    return _page_shell(SITE_TITLE, body, active_nav="home", base_path="")


def _count_articles_in_report(report_path: Path) -> int:
    if not report_path.exists():
        return 0
    text = report_path.read_text(encoding="utf-8")
    match = re.search(r"\*\*Articles found:\*\*\s*(\d+)", text)
    return int(match.group(1)) if match else 0


def _format_display_date(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%A, %B %d, %Y")


def build_website(
    articles: list[NewsArticle],
    config: AgentConfig = DEFAULT_CONFIG,
    report_date: datetime | None = None,
) -> Path:
    now = report_date or datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")

    site_dir = Path(config.website_dir)
    reports_html_dir = site_dir / "reports"
    assets_dir = site_dir / "assets"

    site_dir.mkdir(parents=True, exist_ok=True)
    reports_html_dir.mkdir(parents=True, exist_ok=True)
    _write_stylesheet(assets_dir)

    report_html = reports_html_dir / f"{date_str}.html"
    report_html.write_text(_render_report_page(articles, now), encoding="utf-8")

    archive: list[tuple[str, str, int]] = []
    report_md_dir = Path(config.report_dir)

    for md_file in sorted(report_md_dir.glob("*.md"), reverse=True):
        ds = md_file.stem
        count = _count_articles_in_report(md_file)
        archive.append((ds, _format_display_date(ds), count))

    latest = archive[0][0] if archive else None
    index_path = site_dir / "index.html"
    index_path.write_text(_render_index_page(latest, archive), encoding="utf-8")

    return site_dir


def rebuild_index_only(config: AgentConfig = DEFAULT_CONFIG) -> Path:
    """Rebuild the homepage from existing report files without fetching news."""
    site_dir = Path(config.website_dir)
    report_md_dir = Path(config.report_dir)

    archive: list[tuple[str, str, int]] = []
    for md_file in sorted(report_md_dir.glob("*.md"), reverse=True):
        ds = md_file.stem
        count = _count_articles_in_report(md_file)
        archive.append((ds, _format_display_date(ds), count))

    latest = archive[0][0] if archive else None
    (site_dir / "index.html").write_text(_render_index_page(latest, archive), encoding="utf-8")
    _write_stylesheet(site_dir / "assets")
    return site_dir


def rebuild_website_from_storage(config: AgentConfig = DEFAULT_CONFIG) -> Path:
    """Rebuild the full website from saved JSON report files."""
    from .storage import load_all_saved_reports

    site_dir = Path(config.website_dir)
    reports_html_dir = site_dir / "reports"
    assets_dir = site_dir / "assets"

    site_dir.mkdir(parents=True, exist_ok=True)
    reports_html_dir.mkdir(parents=True, exist_ok=True)
    _write_stylesheet(assets_dir)

    archive: list[tuple[str, str, int]] = []
    saved = load_all_saved_reports(config)

    for report_date, articles in saved:
        date_str = report_date.strftime("%Y-%m-%d")
        html_path = reports_html_dir / f"{date_str}.html"
        html_path.write_text(_render_report_page(articles, report_date), encoding="utf-8")
        archive.append((date_str, _format_display_date(date_str), len(articles)))

    latest = archive[0][0] if archive else None
    (site_dir / "index.html").write_text(_render_index_page(latest, archive), encoding="utf-8")
    return site_dir
