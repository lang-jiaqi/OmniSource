"""Write the report to a local markdown file."""
from __future__ import annotations

from .base import Publisher, Report


class MarkdownPublisher(Publisher):
    name = "markdown"

    def publish(self, report: Report) -> None:
        report.reports_dir.mkdir(parents=True, exist_ok=True)
        path = report.reports_dir / f"{report.slug}.md"
        path.write_text(report.markdown, encoding="utf-8")
        print(f"  markdown: {path}")
