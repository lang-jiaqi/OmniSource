"""Publisher base class.

Mirrors Source: a publisher takes the finished report and sends it somewhere
(a file, a GitHub issue, a Pages site). Tracks list publishers by name, so where
the briefing goes is configuration, not code.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from ..models import Signal


@dataclass
class Report:
    track: dict
    date: str
    markdown: str
    sections: dict[str, list[Signal]]
    reports_dir: Path
    period: str = "Daily"  # "Daily" | "Weekly"
    candidate_sections: dict[str, list[Signal]] | None = None

    @property
    def slug(self) -> str:
        """Filename stem, e.g. report-2026-06-24 or report-weekly-2026-06-24."""
        prefix = "" if self.period == "Daily" else f"{self.period.lower()}-"
        return f"report-{prefix}{self.date}"


class Publisher(ABC):
    name: str

    @abstractmethod
    def publish(self, report: Report) -> None:
        """Deliver the report. Should degrade gracefully (skip with a message)
        rather than raise when its destination isn't configured."""
        raise NotImplementedError
