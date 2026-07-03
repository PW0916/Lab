"""CLI entry point for the agentic AI news agent."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone

from .agent import AgenticNewsAgent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentic-news",
        description="Daily news agent for agentic AI — fetches, filters, and reports the latest developments.",
    )
    parser.add_argument(
        "--max-articles",
        type=int,
        default=30,
        help="Maximum number of articles in the report (default: 30)",
    )
    parser.add_argument(
        "--lookback-hours",
        type=int,
        default=48,
        help="How many hours back to search for news (default: 48)",
    )
    parser.add_argument(
        "--report-dir",
        default="reports",
        help="Directory to save generated reports (default: reports/)",
    )
    parser.add_argument(
        "--website-dir",
        default="docs",
        help="Directory for the generated news website (default: docs/)",
    )
    parser.add_argument(
        "--rebuild-website",
        action="store_true",
        help="Rebuild the news website from saved report data (no fetching)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--print-report",
        action="store_true",
        help="Print the full report to stdout",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    agent = AgenticNewsAgent.from_cli_args(
        max_articles=args.max_articles,
        lookback_hours=args.lookback_hours,
        report_dir=args.report_dir,
        website_dir=args.website_dir,
    )

    if args.rebuild_website:
        site_path = agent.rebuild_website()
        print(f"\n✓ News website rebuilt")
        print(f"  Website:  {site_path}/index.html")
        return 0

    articles, report_path, site_path = agent.run(datetime.now(timezone.utc))

    print(f"\n✓ Agentic AI Daily News Report generated")
    print(f"  Articles: {len(articles)}")
    print(f"  Report:   {report_path}")
    print(f"  Website:  {site_path}/index.html")

    if args.print_report:
        print("\n" + "=" * 60 + "\n")
        print(report_path.read_text(encoding="utf-8"))

    return 0


if __name__ == "__main__":
    sys.exit(main())
