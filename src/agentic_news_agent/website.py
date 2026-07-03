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
SITE_TAGLINE = "Your daily briefing on autonomous agents, multi-agent systems, and agentic AI"


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def _category_badge(category: str) -> str:
    labels = {
        "industry": "Industry",
        "research": "Research",
        "search": "Trending",
        "community": "Community",
        "general": "General",
    }
    return labels.get(category, category.title())


def _write_stylesheet(assets_dir: Path) -> None:
    assets_dir.mkdir(parents=True, exist_ok=True)
    css_path = assets_dir / "style.css"
    if css_path.exists():
        return

    css_path.write_text(
        """\
:root {
  --bg: #0b0f17;
  --surface: #121826;
  --surface-2: #1a2233;
  --border: #2a3447;
  --text: #e8edf5;
  --muted: #94a3b8;
  --accent: #6366f1;
  --accent-2: #818cf8;
  --hero: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e293b 100%);
  --card-shadow: 0 4px 24px rgba(0, 0, 0, 0.35);
  --radius: 12px;
  --font: "Segoe UI", system-ui, -apple-system, sans-serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  min-height: 100vh;
}

a { color: var(--accent-2); text-decoration: none; }
a:hover { text-decoration: underline; }

.site-header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.logo {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.logo a {
  color: var(--text);
  text-decoration: none;
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.logo span {
  color: var(--muted);
  font-size: 0.78rem;
  font-weight: 400;
}

.nav-links {
  display: flex;
  gap: 1.25rem;
  list-style: none;
}

.nav-links a {
  color: var(--muted);
  font-size: 0.9rem;
  font-weight: 500;
}

.nav-links a:hover,
.nav-links a.active {
  color: var(--text);
  text-decoration: none;
}

main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem 1.5rem 4rem;
}

.hero {
  background: var(--hero);
  border-radius: var(--radius);
  padding: 2.5rem 2rem;
  margin-bottom: 2.5rem;
  border: 1px solid rgba(99, 102, 241, 0.25);
}

.hero-label {
  display: inline-block;
  background: rgba(99, 102, 241, 0.2);
  color: var(--accent-2);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  margin-bottom: 1rem;
}

.hero h1 {
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1.2;
  margin-bottom: 0.75rem;
}

.hero p {
  color: rgba(232, 237, 245, 0.75);
  font-size: 1.05rem;
  max-width: 620px;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
  margin-top: 1.5rem;
  color: var(--muted);
  font-size: 0.875rem;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted);
  margin-bottom: 1.25rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border);
}

.summary-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 2.5rem;
}

.summary-list li {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
}

.summary-rank {
  flex-shrink: 0;
  width: 1.75rem;
  height: 1.75rem;
  background: var(--accent);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
}

.summary-list a {
  color: var(--text);
  font-weight: 600;
  font-size: 1rem;
}

.summary-list .source {
  display: block;
  color: var(--muted);
  font-size: 0.82rem;
  margin-top: 0.2rem;
  font-weight: 400;
}

.articles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.25rem;
  margin-bottom: 2.5rem;
}

.article-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: border-color 0.2s, transform 0.2s;
}

.article-card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
}

.card-badge {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
  background: var(--surface-2);
  color: var(--accent-2);
  width: fit-content;
}

.article-card h3 {
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.4;
}

.article-card h3 a {
  color: var(--text);
  text-decoration: none;
}

.article-card h3 a:hover {
  color: var(--accent-2);
}

.card-summary {
  color: var(--muted);
  font-size: 0.875rem;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
  font-size: 0.78rem;
  color: var(--muted);
}

.card-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.keyword-tag {
  font-size: 0.68rem;
  background: rgba(99, 102, 241, 0.15);
  color: var(--accent-2);
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.read-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--accent-2);
  margin-top: auto;
}

.archive-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
}

.archive-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem;
  transition: border-color 0.2s;
}

.archive-card:hover {
  border-color: var(--accent);
}

.archive-card a {
  color: var(--text);
  font-weight: 700;
  font-size: 1.05rem;
}

.archive-card .date-label {
  color: var(--muted);
  font-size: 0.82rem;
  margin-top: 0.35rem;
}

.site-footer {
  border-top: 1px solid var(--border);
  padding: 2rem 1.5rem;
  text-align: center;
  color: var(--muted);
  font-size: 0.85rem;
}

.site-footer a { color: var(--accent-2); }

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--muted);
}

@media (max-width: 640px) {
  .header-inner { flex-direction: column; align-items: flex-start; }
  .articles-grid { grid-template-columns: 1fr; }
  .hero { padding: 1.75rem 1.25rem; }
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
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <div class="logo">
        <a href="{home_href}">{_esc(SITE_TITLE)}</a>
        <span>{_esc(SITE_TAGLINE)}</span>
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
    <p>Automated daily briefing powered by the
      <a href="https://github.com/PW0916/Lab">Agentic AI News Agent</a>.
      Updated daily at 08:00 UTC.</p>
  </footer>
</body>
</html>"""


def _render_article_card(article: NewsArticle) -> str:
    keywords_html = ""
    if article.matched_keywords:
        tags = "".join(
            f'<span class="keyword-tag">{_esc(k)}</span>'
            for k in article.matched_keywords[:4]
        )
        keywords_html = f'<div class="card-keywords">{tags}</div>'

    summary = _esc(article.summary) if article.summary else ""

    return f"""
    <article class="article-card">
      <span class="card-badge">{_esc(_category_badge(article.category))}</span>
      <h3><a href="{_esc(article.url)}" target="_blank" rel="noopener">{_esc(article.title)}</a></h3>
      {f'<p class="card-summary">{summary}</p>' if summary else ''}
      <div class="card-meta">
        <span>{_esc(article.source)}</span>
        <span>{_esc(article.published_display)}</span>
      </div>
      {keywords_html}
      <a class="read-btn" href="{_esc(article.url)}" target="_blank" rel="noopener">Read full article →</a>
    </article>"""


def _render_report_page(
    articles: list[NewsArticle],
    report_date: datetime,
) -> str:
    date_str = report_date.strftime("%Y-%m-%d")
    display_date = report_date.strftime("%A, %B %d, %Y")
    time_str = report_date.strftime("%H:%M UTC")

    top = articles[:5]
    summary_items = ""
    for i, article in enumerate(top, start=1):
        summary_items += f"""
        <li>
          <span class="summary-rank">{i}</span>
          <div>
            <a href="{_esc(article.url)}" target="_blank" rel="noopener">{_esc(article.title)}</a>
            <span class="source">{_esc(article.source)}</span>
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
        cards = "".join(_render_article_card(a) for a in cat_articles)
        sections += f"""
        <h2 class="section-title">{_esc(label)}</h2>
        <div class="articles-grid">{cards}</div>"""

    if not articles:
        sections = """
        <div class="empty-state">
          <p>No agentic AI news matched today. Check back tomorrow.</p>
        </div>"""

    body = f"""
    <section class="hero">
      <span class="hero-label">Daily Report</span>
      <h1>{_esc(display_date)}</h1>
      <p>Today's curated briefing on agentic AI — covering autonomous agents, multi-agent frameworks, and industry developments.</p>
      <div class="hero-meta">
        <span>{len(articles)} articles</span>
        <span>Generated {time_str}</span>
      </div>
    </section>

    <h2 class="section-title" id="latest">Executive Summary</h2>
    <ol class="summary-list">{summary_items if summary_items else '<li><p class="empty-state">No headlines today.</p></li>'}</ol>

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
        hero = f"""
        <section class="hero">
          <span class="hero-label">Latest Edition</span>
          <h1>Agentic AI News — {_esc(latest_date)}</h1>
          <p>{_esc(SITE_TAGLINE)}. Your automated daily digest of the most important developments in autonomous AI agents.</p>
          <div class="hero-meta">
            <span><a href="reports/{_esc(latest_date)}.html">Read today's full report →</a></span>
          </div>
        </section>"""
    else:
        hero = f"""
        <section class="hero">
          <span class="hero-label">Welcome</span>
          <h1>{_esc(SITE_TITLE)}</h1>
          <p>{_esc(SITE_TAGLINE)}. Reports will appear here once the agent runs.</p>
        </section>"""

    archive_cards = ""
    for date_str, display, count in archive:
        archive_cards += f"""
        <div class="archive-card">
          <a href="reports/{_esc(date_str)}.html">{_esc(display)}</a>
          <p class="date-label">{count} articles</p>
        </div>"""

    if not archive_cards:
        archive_cards = '<p class="empty-state">No archived reports yet.</p>'

    body = f"""
    {hero}

    <h2 class="section-title" id="archive">Report Archive</h2>
    <div class="archive-grid">{archive_cards}</div>
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

        html_file = reports_html_dir / f"{ds}.html"
        if not html_file.exists() and ds != date_str:
            continue

    latest = archive[0][0] if archive else None
    index_path = site_dir / "index.html"
    index_path.write_text(_render_index_page(latest, archive), encoding="utf-8")

    return site_dir


def rebuild_index_only(config: AgentConfig = DEFAULT_CONFIG) -> Path:
    """Rebuild the homepage from existing report files without fetching news."""
    site_dir = Path(config.website_dir)
    reports_html_dir = site_dir / "reports"
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
