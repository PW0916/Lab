"""Generate a static news website from daily reports."""

from __future__ import annotations

import html
import re
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

from .config import AgentConfig, DEFAULT_CONFIG
from .models import NewsArticle
from .reporter import CATEGORY_LABELS

SITE_TITLE = "Agentic AI Daily"
SITE_TAGLINE = "Intelligence on autonomous agents & agentic AI"
GITHUB_URL = "https://github.com/PW0916/Lab"

CATEGORY_COLORS = {
    "industry": ("#1d4ed8", "#eff6ff"),
    "research": ("#6d28d9", "#f5f3ff"),
    "search":   ("#0f766e", "#f0fdfa"),
    "community":("#b45309", "#fffbeb"),
    "general":  ("#475569", "#f8fafc"),
}


# ─── Text helpers ───────────────────────────────────────────────────────────

def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def _clean_summary(text: str) -> str:
    """Remove Google News source-echo pattern and tidy whitespace."""
    if not text:
        return ""
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"\xa0", " ", text)
    # Drop trailing "· Source" or "   Source" Google News echoes
    text = re.sub(r"\s{2,}.{1,80}$", "", text.strip())
    text = re.sub(r"Article URL:.*$", "", text, flags=re.DOTALL)
    text = re.sub(r"Comments URL:.*$", "", text, flags=re.DOTALL)
    text = re.sub(r"Points:\s*\d+.*$", "", text, flags=re.DOTALL)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _time_ago(dt: datetime | None) -> str:
    if dt is None:
        return ""
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = now - dt
    if delta < timedelta(hours=1):
        m = max(1, int(delta.total_seconds() / 60))
        return f"{m}m ago"
    if delta < timedelta(hours=24):
        return f"{int(delta.total_seconds() / 3600)}h ago"
    return dt.strftime("%b %-d")


def _cat_label(category: str) -> str:
    return {
        "industry": "Industry",
        "research": "Research",
        "search":   "Trending",
        "community":"Community",
        "general":  "General",
    }.get(category, category.title())


def _cat_colors(category: str) -> tuple[str, str]:
    return CATEGORY_COLORS.get(category, ("#475569", "#f8fafc"))


def _has_real_summary(article: NewsArticle) -> bool:
    s = _clean_summary(article.summary)
    if not s or len(s) < 30:
        return False
    title_words = set(article.title.lower().split())
    summary_words = set(s.lower().split())
    overlap = len(title_words & summary_words) / max(len(title_words), 1)
    return overlap < 0.75


# ─── CSS ────────────────────────────────────────────────────────────────────

_CSS = """\
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,800;1,700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=Inter:wght@400;500;600&display=swap');

/* ─── Reset & tokens ─── */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;font-size:16px}

:root{
  --ink:       #111827;
  --ink-2:     #374151;
  --ink-3:     #6b7280;
  --rule:      #e5e7eb;
  --rule-2:    #d1d5db;
  --bg:        #fafaf9;
  --surface:   #ffffff;
  --teal:      #0f766e;
  --teal-2:    #0d9488;
  --teal-bg:   #f0fdfa;
  --gold:      #92400e;
  --gold-bg:   #fffbeb;
  --r:         10px;
  --r-sm:      6px;
  --sh:        0 1px 3px rgba(0,0,0,.06),0 4px 16px rgba(0,0,0,.04);
  --sh-hover:  0 4px 12px rgba(0,0,0,.08),0 12px 40px rgba(0,0,0,.06);
  --serif:     "Source Serif 4","Georgia",serif;
  --display:   "Playfair Display","Georgia",serif;
  --sans:      "Inter",system-ui,sans-serif;
  --wrap:      1200px;
  --col:       760px;
}

body{
  font-family:var(--sans);
  background:var(--bg);
  color:var(--ink);
  line-height:1.6;
  min-height:100vh;
  -webkit-font-smoothing:antialiased;
}

a{color:var(--teal);text-decoration:none;transition:color .15s}
a:hover{color:var(--teal-2)}

img{display:block;max-width:100%}

/* ─── Utility ─── */
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}

/* ─── Header ─── */
.site-header{
  background:rgba(255,255,255,.92);
  backdrop-filter:blur(14px);
  border-bottom:1px solid var(--rule);
  position:sticky;top:0;z-index:200;
}
.hdr-inner{
  max-width:var(--wrap);
  margin:0 auto;
  padding:.9rem 2rem;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:1.5rem;
}
.site-brand{display:flex;align-items:center;gap:.8rem;text-decoration:none}
.brand-icon{
  width:38px;height:38px;
  background:linear-gradient(135deg,#0f766e,#134e4a);
  border-radius:9px;
  display:flex;align-items:center;justify-content:center;
  font-family:var(--display);font-size:1.15rem;font-weight:700;color:#fff;
  flex-shrink:0;
}
.brand-text{line-height:1.15}
.brand-name{
  font-family:var(--display);
  font-size:1.35rem;font-weight:700;
  color:var(--ink);letter-spacing:-.01em;
}
.brand-sub{
  font-size:.68rem;font-weight:500;
  color:var(--ink-3);
  text-transform:uppercase;letter-spacing:.07em;
}
.site-nav ul{display:flex;gap:.2rem;list-style:none}
.site-nav a{
  font-size:.85rem;font-weight:500;color:var(--ink-3);
  padding:.4rem .85rem;border-radius:999px;
  transition:background .15s,color .15s;
}
.site-nav a:hover,.site-nav a.active{color:var(--ink);background:#f3f4f6}

/* ─── Main layout ─── */
main{max-width:var(--wrap);margin:0 auto;padding:2.5rem 2rem 6rem}

/* ─── Masthead (report header) ─── */
.masthead{
  text-align:center;
  max-width:680px;
  margin:0 auto 2.5rem;
  padding-bottom:2rem;
}
.masthead-eyebrow{
  display:inline-flex;align-items:center;gap:.6rem;
  font-size:.7rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;
  color:var(--teal);margin-bottom:1.1rem;
}
.masthead-eyebrow::before,.masthead-eyebrow::after{
  content:"";width:28px;height:1px;background:var(--rule-2);
}
.masthead h1{
  font-family:var(--display);
  font-size:clamp(2rem,5vw,3.2rem);
  font-weight:800;letter-spacing:-.03em;line-height:1.05;
  color:var(--ink);margin-bottom:.9rem;
}
.masthead-lede{
  font-family:var(--serif);font-size:1.05rem;
  color:var(--ink-2);line-height:1.75;margin-bottom:1.25rem;
}
.masthead-chips{
  display:flex;flex-wrap:wrap;justify-content:center;gap:.5rem .9rem;
  font-size:.78rem;color:var(--ink-3);
}
.masthead-chips strong{color:var(--ink-2);font-weight:600}
.masthead-rule{
  width:64px;height:3px;
  background:linear-gradient(90deg,var(--teal),#14b8a6);
  border-radius:2px;margin:2rem auto 0;
}

/* ─── Feature (lead) story ─── */
.feature{
  background:var(--surface);
  border:1px solid var(--rule);
  border-radius:var(--r);
  box-shadow:var(--sh);
  overflow:hidden;
  margin-bottom:3rem;
  display:grid;
  grid-template-columns:1fr 280px;
}
@media(max-width:860px){.feature{grid-template-columns:1fr}}
.feature-body{
  padding:2.25rem 2.5rem;
  border-right:1px solid var(--rule);
  display:flex;flex-direction:column;
}
@media(max-width:860px){.feature-body{border-right:none;border-bottom:1px solid var(--rule)}}
.feature-tag{
  display:inline-flex;align-items:center;gap:.4rem;
  font-size:.68rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
  color:var(--gold);margin-bottom:1.1rem;
}
.feature-tag::before{
  content:"";width:20px;height:2px;background:var(--gold);border-radius:1px;
}
.feature-body h2{
  font-family:var(--display);
  font-size:clamp(1.5rem,3vw,2rem);
  font-weight:800;letter-spacing:-.02em;line-height:1.22;
  margin-bottom:1rem;
}
.feature-body h2 a{color:var(--ink)}
.feature-body h2 a:hover{color:var(--teal)}
.feature-summary{
  font-family:var(--serif);font-size:1.02rem;color:var(--ink-2);
  line-height:1.75;flex:1;margin-bottom:1.5rem;
}
.feature-meta{
  display:flex;flex-wrap:wrap;align-items:center;gap:.65rem 1rem;
  font-size:.8rem;color:var(--ink-3);
}
.feature-source{font-weight:600;color:var(--ink-2)}
.btn-read{
  display:inline-flex;align-items:center;gap:.4rem;
  background:var(--teal);color:#fff !important;
  font-size:.82rem;font-weight:600;
  padding:.55rem 1.1rem;border-radius:999px;
  transition:background .15s,transform .15s;
  text-decoration:none !important;
}
.btn-read:hover{background:var(--teal-2);transform:translateY(-1px)}
.feature-sidebar{
  padding:1.75rem 1.5rem;
  display:flex;flex-direction:column;gap:1.25rem;
}
.sidebar-headline{
  padding-bottom:1.25rem;
  border-bottom:1px solid var(--rule);
}
.sidebar-headline:last-child{border-bottom:none;padding-bottom:0}
.sidebar-num{
  font-size:.68rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  color:var(--ink-3);margin-bottom:.35rem;
}
.sidebar-headline a{
  font-family:var(--serif);font-size:.95rem;font-weight:600;
  color:var(--ink);line-height:1.4;display:block;margin-bottom:.3rem;
}
.sidebar-headline a:hover{color:var(--teal)}
.sidebar-src{font-size:.72rem;color:var(--ink-3)}

/* ─── Headlines strip ─── */
.headlines-section{margin-bottom:3rem}
.section-head{
  display:flex;align-items:baseline;justify-content:space-between;gap:1rem;
  margin-bottom:1.25rem;padding-bottom:.75rem;
  border-bottom:2px solid var(--ink);
}
.section-head h2{
  font-family:var(--display);font-size:1.45rem;font-weight:700;letter-spacing:-.01em;
}
.section-head-count{font-size:.78rem;color:var(--ink-3);font-weight:500}
.headlines-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
  gap:.75rem;
}
.hl-card{
  display:flex;gap:.85rem;align-items:flex-start;
  background:var(--surface);
  border:1px solid var(--rule);border-radius:var(--r-sm);
  padding:1rem 1.1rem;
  transition:box-shadow .2s,border-color .2s;
}
.hl-card:hover{border-color:var(--rule-2);box-shadow:var(--sh)}
.hl-num{
  font-family:var(--display);font-size:1.5rem;font-weight:700;
  color:var(--rule-2);line-height:1;flex-shrink:0;min-width:1.8rem;
  padding-top:.05rem;
}
.hl-body a{
  font-family:var(--serif);font-size:.97rem;font-weight:600;
  color:var(--ink);line-height:1.4;display:block;margin-bottom:.3rem;
}
.hl-body a:hover{color:var(--teal)}
.hl-src{font-size:.72rem;color:var(--ink-3)}
.hl-time{font-size:.68rem;color:var(--rule-2)}

/* ─── Category sections ─── */
.cat-section{margin-bottom:3.5rem}
.cat-head{
  display:flex;align-items:center;justify-content:space-between;gap:1rem;
  margin-bottom:1.25rem;padding-bottom:.6rem;
}
.cat-head-left{display:flex;align-items:center;gap:.6rem}
.cat-stripe{width:4px;height:1.5rem;border-radius:2px}
.cat-head h2{
  font-family:var(--display);font-size:1.2rem;font-weight:700;letter-spacing:-.01em;
}
.cat-count{font-size:.75rem;color:var(--ink-3)}
.cat-rule{border:none;border-top:1px solid var(--rule);margin-bottom:1.25rem}

/* ─── Article cards ─── */
.articles-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(340px,1fr));
  gap:1rem;
}
.article-card{
  background:var(--surface);
  border:1px solid var(--rule);
  border-left-width:3px;
  border-left-style:solid;
  border-left-color:var(--rule-2);
  border-radius:0 var(--r-sm) var(--r-sm) 0;
  padding:1.25rem 1.35rem 1rem;
  display:flex;flex-direction:column;gap:.65rem;
  transition:box-shadow .2s,border-color .2s;
}
.article-card:hover{border-color:var(--rule-2);box-shadow:var(--sh-hover)}
.card-meta-top{
  display:flex;align-items:center;gap:.55rem;flex-wrap:wrap;
}
.card-cat{
  font-size:.63rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;
  padding:.18rem .5rem;border-radius:3px;
}
.card-src{font-size:.75rem;color:var(--ink-3);font-weight:500}
.card-time{font-size:.7rem;color:var(--rule-2);margin-left:auto;white-space:nowrap}
.article-card h3{
  font-family:var(--serif);font-size:1rem;font-weight:600;
  line-height:1.42;letter-spacing:-.005em;
}
.article-card h3 a{color:var(--ink)}
.article-card h3 a:hover{color:var(--teal)}
.card-summary{
  font-size:.86rem;color:var(--ink-2);line-height:1.65;flex:1;
  display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;
}
.card-footer{
  display:flex;align-items:center;justify-content:space-between;
  padding-top:.55rem;border-top:1px solid var(--rule);margin-top:auto;
}
.card-tags{display:flex;gap:.3rem;flex-wrap:wrap}
.tag{
  font-size:.62rem;font-weight:500;
  background:var(--bg);border:1px solid var(--rule);
  color:var(--ink-3);padding:.12rem .4rem;border-radius:3px;
}
.card-read{
  font-size:.76rem;font-weight:600;color:var(--teal);
  white-space:nowrap;flex-shrink:0;
}
.card-read:hover{text-decoration:underline}

/* ─── Homepage ─── */
.home-banner{
  background:var(--surface);
  border:1px solid var(--rule);border-radius:var(--r);
  box-shadow:var(--sh);
  text-align:center;
  padding:3rem 2rem 3.5rem;
  margin-bottom:3rem;
  position:relative;overflow:hidden;
}
.home-banner::after{
  content:"";
  position:absolute;bottom:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,var(--teal),#14b8a6,#6366f1);
}
.home-banner h1{
  font-family:var(--display);
  font-size:clamp(2rem,5vw,3rem);
  font-weight:800;letter-spacing:-.03em;
  margin-bottom:.85rem;color:var(--ink);
}
.home-banner p{
  font-family:var(--serif);font-size:1.05rem;color:var(--ink-2);
  max-width:500px;margin:0 auto 2rem;line-height:1.7;
}
.home-ctas{display:flex;flex-wrap:wrap;justify-content:center;gap:.75rem}
.btn-outline{
  display:inline-flex;align-items:center;gap:.4rem;
  border:1px solid var(--rule-2);color:var(--ink-2) !important;
  font-size:.85rem;font-weight:600;
  padding:.55rem 1.1rem;border-radius:999px;background:var(--surface);
  transition:border-color .15s,color .15s;text-decoration:none !important;
}
.btn-outline:hover{border-color:var(--teal);color:var(--teal) !important}

/* ─── Archive ─── */
.archive-wrap{
  border:1px solid var(--rule);border-radius:var(--r);
  background:var(--surface);overflow:hidden;
}
.archive-row{
  display:flex;align-items:center;justify-content:space-between;
  gap:1rem;padding:1.1rem 1.5rem;border-bottom:1px solid var(--rule);
  transition:background .15s;
}
.archive-row:last-child{border-bottom:none}
.archive-row:hover{background:var(--bg)}
.archive-row a{
  font-family:var(--serif);font-size:1.05rem;font-weight:600;color:var(--ink);
}
.archive-row a:hover{color:var(--teal)}
.archive-pill{
  font-size:.72rem;color:var(--ink-3);
  background:var(--bg);border:1px solid var(--rule);
  padding:.2rem .65rem;border-radius:999px;flex-shrink:0;
}

/* ─── Footer ─── */
.site-footer{
  border-top:1px solid var(--rule);
  background:var(--surface);
  padding:2rem 2rem;text-align:center;
  color:var(--ink-3);font-size:.82rem;
}
.site-footer a{color:var(--teal);font-weight:500}

/* ─── Misc ─── */
.empty{text-align:center;padding:4rem 1rem;color:var(--ink-3)}

/* ─── Responsive ─── */
@media(max-width:768px){
  main{padding:1.5rem 1rem 4rem}
  .hdr-inner{padding:.8rem 1rem}
  .site-nav a{padding:.35rem .65rem;font-size:.8rem}
  .masthead h1{letter-spacing:-.02em}
  .articles-grid{grid-template-columns:1fr}
  .headlines-grid{grid-template-columns:1fr}
}
@media(max-width:500px){
  .brand-sub{display:none}
  .masthead-lede{font-size:.95rem}
}
"""


# ─── HTML shell ─────────────────────────────────────────────────────────────

def _shell(title: str, body: str, active: str = "home", base: str = "") -> str:
    home = f"{base}index.html"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="{_esc(SITE_TAGLINE)}">
  <title>{_esc(title)} — {_esc(SITE_TITLE)}</title>
  <link rel="stylesheet" href="{base}assets/style.css">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🤖</text></svg>">
</head>
<body>
<header class="site-header">
  <div class="hdr-inner">
    <a class="site-brand" href="{home}">
      <div class="brand-icon">A</div>
      <div class="brand-text">
        <div class="brand-name">{_esc(SITE_TITLE)}</div>
        <div class="brand-sub">{_esc(SITE_TAGLINE)}</div>
      </div>
    </a>
    <nav class="site-nav">
      <ul>
        <li><a href="{home}" class="{'active' if active=='home' else ''}">Home</a></li>
        <li><a href="{base}index.html#archive" class="{'active' if active=='archive' else ''}">Archive</a></li>
      </ul>
    </nav>
  </div>
</header>
<main>{body}</main>
<footer class="site-footer">
  Curated automatically by the
  <a href="{_esc(GITHUB_URL)}">Agentic AI News Agent</a>
  &nbsp;·&nbsp; Updated daily at 08:00 UTC
</footer>
</body>
</html>"""


# ─── Feature (lead) card ────────────────────────────────────────────────────

def _pick_lead(articles: list[NewsArticle]) -> int:
    for i, a in enumerate(articles):
        if _has_real_summary(a):
            return i
    return 0


def _render_feature(lead: NewsArticle, sidebar_articles: list[NewsArticle]) -> str:
    summary = _clean_summary(lead.summary)
    summary_html = f'<p class="feature-summary">{_esc(summary)}</p>' if summary else ""

    sidebar_items = ""
    for i, a in enumerate(sidebar_articles[:4], start=2):
        sidebar_items += f"""
      <div class="sidebar-headline">
        <div class="sidebar-num">#{i:02d}</div>
        <a href="{_esc(a.url)}" target="_blank" rel="noopener">{_esc(a.title)}</a>
        <div class="sidebar-src">{_esc(a.source)} &nbsp;·&nbsp; {_time_ago(a.published)}</div>
      </div>"""

    return f"""
<section class="feature">
  <div class="feature-body">
    <p class="feature-tag">Top Story</p>
    <h2><a href="{_esc(lead.url)}" target="_blank" rel="noopener">{_esc(lead.title)}</a></h2>
    {summary_html}
    <div class="feature-meta">
      <span class="feature-source">{_esc(lead.source)}</span>
      <span>{_esc(lead.published_display)}</span>
      <a class="btn-read" href="{_esc(lead.url)}" target="_blank" rel="noopener">Read article →</a>
    </div>
  </div>
  <div class="feature-sidebar">
    {sidebar_items}
  </div>
</section>"""


# ─── Headlines strip ────────────────────────────────────────────────────────

def _render_headlines(articles: list[NewsArticle], start_n: int = 6) -> str:
    items = ""
    for i, a in enumerate(articles, start=start_n):
        items += f"""
    <div class="hl-card">
      <div class="hl-num">{i:02d}</div>
      <div class="hl-body">
        <a href="{_esc(a.url)}" target="_blank" rel="noopener">{_esc(a.title)}</a>
        <div class="hl-src">{_esc(a.source)} &nbsp;·&nbsp; <span class="hl-time">{_time_ago(a.published)}</span></div>
      </div>
    </div>"""

    return f"""
<section class="headlines-section">
  <div class="section-head">
    <h2>More Headlines</h2>
    <span class="section-head-count">{len(articles)} stories</span>
  </div>
  <div class="headlines-grid">{items}</div>
</section>"""


# ─── Article card ───────────────────────────────────────────────────────────

def _render_card(article: NewsArticle) -> str:
    fg, bg = _cat_colors(article.category)
    label = _cat_label(article.category)
    summary = _clean_summary(article.summary)
    summary_html = f'<p class="card-summary">{_esc(summary)}</p>' if summary else ""

    tags_html = ""
    if article.matched_keywords:
        tags_html = "".join(
            f'<span class="tag">{_esc(k)}</span>'
            for k in article.matched_keywords[:3]
        )
        tags_html = f'<div class="card-tags">{tags_html}</div>'

    return f"""
<article class="article-card" style="border-left-color:{fg}">
  <div class="card-meta-top">
    <span class="card-cat" style="background:{bg};color:{fg}">{_esc(label)}</span>
    <span class="card-src">{_esc(article.source)}</span>
    <span class="card-time">{_time_ago(article.published)}</span>
  </div>
  <h3><a href="{_esc(article.url)}" target="_blank" rel="noopener">{_esc(article.title)}</a></h3>
  {summary_html}
  <div class="card-footer">
    {tags_html}
    <a class="card-read" href="{_esc(article.url)}" target="_blank" rel="noopener">Read →</a>
  </div>
</article>"""


# ─── Report page ────────────────────────────────────────────────────────────

def _render_report_page(articles: list[NewsArticle], report_date: datetime) -> str:
    display_date = report_date.strftime("%A, %B %-d, %Y")
    date_str = report_date.strftime("%Y-%m-%d")
    gen_time = report_date.strftime("%H:%M UTC")

    # Lead story + sidebar
    feature_html = ""
    next_idx = 0
    if articles:
        lead_idx = _pick_lead(articles)
        lead = articles[lead_idx]
        rest = [a for i, a in enumerate(articles) if i != lead_idx]
        feature_html = _render_feature(lead, rest[:4])
        next_idx = 5

    # More headlines (non-lead, non-category-section items, next ~8)
    headlines_pool = [a for a in articles[next_idx:next_idx + 8]]
    headlines_html = _render_headlines(headlines_pool, start_n=6) if headlines_pool else ""

    # Category sections — exclude already-shown articles
    shown_urls = {articles[0].url} if articles else set()
    shown_urls.update(a.url for a in (rest[:4] if articles else []))
    shown_urls.update(a.url for a in headlines_pool)

    grouped: dict[str, list[NewsArticle]] = defaultdict(list)
    for a in articles:
        if a.url not in shown_urls:
            grouped[a.category].append(a)

    cat_sections = ""
    cat_order = ["industry", "research", "search", "community", "general"]
    for cat in cat_order:
        arts = grouped.get(cat, [])
        if not arts:
            continue
        fg, _ = _cat_colors(cat)
        label = CATEGORY_LABELS.get(cat, cat.title())
        cards = "".join(_render_card(a) for a in arts)
        cat_sections += f"""
<section class="cat-section">
  <div class="cat-head">
    <div class="cat-head-left">
      <div class="cat-stripe" style="background:{fg}"></div>
      <h2>{_esc(label)}</h2>
    </div>
    <span class="cat-count">{len(arts)} stories</span>
  </div>
  <hr class="cat-rule">
  <div class="articles-grid">{cards}</div>
</section>"""

    if not articles:
        cat_sections = '<div class="empty"><p>No agentic AI news matched today. Check back tomorrow.</p></div>'

    body = f"""
<header class="masthead">
  <p class="masthead-eyebrow">Daily Briefing</p>
  <h1>{_esc(display_date)}</h1>
  <p class="masthead-lede">A curated selection of the day's most important developments in agentic AI — autonomous agents, multi-agent systems, and the tools shaping them.</p>
  <div class="masthead-chips">
    <span><strong>{len(articles)}</strong> articles</span>
    <span>Generated <strong>{gen_time}</strong></span>
    <span>Edition <strong>{_esc(date_str)}</strong></span>
  </div>
  <div class="masthead-rule"></div>
</header>

{feature_html}
{headlines_html}
{cat_sections}"""

    return _shell(f"Report — {date_str}", body, active="home", base="../")


# ─── Index page ─────────────────────────────────────────────────────────────

def _render_index_page(
    latest_date: str | None,
    archive: list[tuple[str, str, int]],
) -> str:
    if latest_date:
        display = _format_display_date(latest_date)
        banner = f"""
<section class="home-banner">
  <p class="masthead-eyebrow">Latest Edition</p>
  <h1>{_esc(display)}</h1>
  <p>Your automated daily intelligence briefing on autonomous agents, multi-agent orchestration, and the rapidly evolving agentic AI landscape.</p>
  <div class="home-ctas">
    <a class="btn-read" href="reports/{_esc(latest_date)}.html">Read today's report →</a>
    <a class="btn-outline" href="#archive">Browse archive</a>
  </div>
</section>"""
    else:
        banner = f"""
<section class="home-banner">
  <p class="masthead-eyebrow">Welcome</p>
  <h1>{_esc(SITE_TITLE)}</h1>
  <p>{_esc(SITE_TAGLINE)}. Daily reports appear here once the agent runs.</p>
</section>"""

    rows = ""
    for ds, display, count in archive:
        rows += f"""
    <div class="archive-row">
      <a href="reports/{_esc(ds)}.html">{_esc(display)}</a>
      <span class="archive-pill">{count} articles</span>
    </div>"""

    archive_html = f'<div class="archive-wrap">{rows}</div>' if rows else '<div class="empty"><p>No reports yet.</p></div>'

    body = f"""
{banner}
<div class="section-head" id="archive">
  <h2>Report Archive</h2>
  <span class="section-head-count">{len(archive)} editions</span>
</div>
{archive_html}"""

    return _shell(SITE_TITLE, body, active="home", base="")


# ─── Helpers ────────────────────────────────────────────────────────────────

def _count_articles_in_report(path: Path) -> int:
    if not path.exists():
        return 0
    m = re.search(r"\*\*Articles found:\*\*\s*(\d+)", path.read_text(encoding="utf-8"))
    return int(m.group(1)) if m else 0


def _format_display_date(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%A, %B %-d, %Y")


def _write_css(assets_dir: Path) -> None:
    assets_dir.mkdir(parents=True, exist_ok=True)
    (assets_dir / "style.css").write_text(_CSS, encoding="utf-8")


# ─── Public builders ────────────────────────────────────────────────────────

def build_website(
    articles: list[NewsArticle],
    config: AgentConfig = DEFAULT_CONFIG,
    report_date: datetime | None = None,
) -> Path:
    now = report_date or datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")

    site_dir = Path(config.website_dir)
    reports_dir = site_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    _write_css(site_dir / "assets")

    (reports_dir / f"{date_str}.html").write_text(
        _render_report_page(articles, now), encoding="utf-8"
    )

    archive: list[tuple[str, str, int]] = []
    for md in sorted(Path(config.report_dir).glob("*.md"), reverse=True):
        archive.append((md.stem, _format_display_date(md.stem), _count_articles_in_report(md)))

    (site_dir / "index.html").write_text(
        _render_index_page(archive[0][0] if archive else None, archive),
        encoding="utf-8",
    )
    return site_dir


def rebuild_index_only(config: AgentConfig = DEFAULT_CONFIG) -> Path:
    site_dir = Path(config.website_dir)
    archive: list[tuple[str, str, int]] = []
    for md in sorted(Path(config.report_dir).glob("*.md"), reverse=True):
        archive.append((md.stem, _format_display_date(md.stem), _count_articles_in_report(md)))
    _write_css(site_dir / "assets")
    (site_dir / "index.html").write_text(
        _render_index_page(archive[0][0] if archive else None, archive),
        encoding="utf-8",
    )
    return site_dir


def rebuild_website_from_storage(config: AgentConfig = DEFAULT_CONFIG) -> Path:
    from .storage import load_all_saved_reports

    site_dir = Path(config.website_dir)
    reports_dir = site_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    _write_css(site_dir / "assets")

    archive: list[tuple[str, str, int]] = []
    for report_date, articles in load_all_saved_reports(config):
        date_str = report_date.strftime("%Y-%m-%d")
        (reports_dir / f"{date_str}.html").write_text(
            _render_report_page(articles, report_date), encoding="utf-8"
        )
        archive.append((date_str, _format_display_date(date_str), len(articles)))

    (site_dir / "index.html").write_text(
        _render_index_page(archive[0][0] if archive else None, archive),
        encoding="utf-8",
    )
    return site_dir
