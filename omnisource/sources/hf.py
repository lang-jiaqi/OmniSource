"""Hugging Face daily papers source.

These are arXiv papers the HF community surfaces and upvotes, so they overlap
with ArxivSource (which is exactly what exercises dedup) and add two things
arXiv alone can't give us: a popularity signal (upvotes) and a code link.
"""
from __future__ import annotations

import datetime as dt
import json

from ..memory.cache import cached_get
from ..models import Signal
from .base import Source

API_URL = "https://huggingface.co/api/daily_papers"


def _parse_dt(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


class HFPapersSource(Source):
    name = "hf_papers"

    def fetch(self, track: dict) -> list[Signal]:
        days = track.get("days", 3)
        limit = track.get("hf_limit", 100)

        items = json.loads(cached_get(API_URL, params={"limit": limit}))

        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
        signals: list[Signal] = []
        for item in items:
            paper = item.get("paper", {})
            paper_id = paper.get("id")
            if not paper_id:
                continue
            # Window on the HF daily date — that's when it hit the radar.
            surfaced = _parse_dt(paper.get("submittedOnDailyAt") or item.get("publishedAt"))
            if surfaced and surfaced < cutoff:
                continue
            published = _parse_dt(paper.get("publishedAt")) or surfaced
            signals.append(
                Signal(
                    id=paper_id,
                    title=paper.get("title", "").strip(),
                    url=f"https://arxiv.org/abs/{paper_id}",
                    type="paper",
                    published_at=published,
                    summary=paper.get("summary", "").strip().replace("\n", " "),
                    authors=[a.get("name", "") for a in paper.get("authors", [])],
                    sources=[self.name],
                    code_url=paper.get("githubRepo"),
                    popularity=paper.get("upvotes", 0) or 0,
                )
            )
        return signals
