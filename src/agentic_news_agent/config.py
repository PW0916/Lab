"""Configuration for the agentic AI news agent."""

from dataclasses import dataclass, field


@dataclass
class RSSSource:
    name: str
    url: str
    category: str = "general"


@dataclass
class AgentConfig:
    """Runtime configuration for news collection and reporting."""

    max_articles: int = 30
    lookback_hours: int = 48
    report_dir: str = "reports"
    website_dir: str = "docs"

    keywords: list[str] = field(default_factory=lambda: [
        "agentic ai",
        "agentic artificial intelligence",
        "ai agent",
        "ai agents",
        "autonomous agent",
        "autonomous agents",
        "multi-agent",
        "multi agent",
        "agent framework",
        "agent orchestration",
        "agentic workflow",
        "tool-use agent",
        "tool use agent",
        "llm agent",
        "coding agent",
        "computer-use agent",
        "langgraph",
        "crewai",
        "autogen",
        "swarm agents",
        "agent protocol",
        "mcp server",
        "model context protocol",
        "openai agents",
        "anthropic agents",
        "claude agent",
        "cursor agent",
        "devin",
        "manus ai",
        "agent marketplace",
    ])

    rss_sources: list[RSSSource] = field(default_factory=lambda: [
        RSSSource("VentureBeat AI", "https://venturebeat.com/category/ai/feed/", "industry"),
        RSSSource("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/", "industry"),
        RSSSource("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "industry"),
        RSSSource("MIT Technology Review AI", "https://www.technologyreview.com/topic/artificial-intelligence/feed", "research"),
        RSSSource("Ars Technica AI", "https://feeds.arstechnica.com/arstechnica/technology-lab", "industry"),
        RSSSource("Google News — Agentic AI", "https://news.google.com/rss/search?q=agentic+AI+OR+AI+agents+when:2d&hl=en-US&gl=US&ceid=US:en", "search"),
        RSSSource("Google News — AI Agents", "https://news.google.com/rss/search?q=%22AI+agents%22+OR+%22autonomous+agents%22+when:2d&hl=en-US&gl=US&ceid=US:en", "search"),
        RSSSource("Hacker News — AI Agents", "https://hnrss.org/newest?q=agent+AI+OR+agentic+OR+LangGraph+OR+CrewAI", "community"),
    ])

    search_queries: list[str] = field(default_factory=lambda: [
        "agentic AI news",
        "AI agents latest developments",
        "autonomous AI agents framework",
        "multi-agent AI systems",
        "LangGraph CrewAI AutoGen news",
    ])


DEFAULT_CONFIG = AgentConfig()
