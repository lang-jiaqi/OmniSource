"""arXiv source: recent papers in the track's categories."""
from __future__ import annotations

import datetime as dt
import re
import time

import requests

from ..models import Signal
from .base import Source

_VERSION_SUFFIX = re.compile(r"v\d+$")


def canonical_arxiv_id(short_id: str) -> str:
    """'2606.21638v2' -> '2606.21638' so the same paper from any source matches."""
    return _VERSION_SUFFIX.sub("", short_id)


class ArxivSource(Source):
    name = "arxiv"

    def fetch(self, track: dict) -> list[Signal]:
        try:
            import arxiv
        except ModuleNotFoundError as exc:
            raise RuntimeError("Install the arxiv package to use the arxiv source") from exc

        categories = track["categories"]
        days = track.get("days", 3)
        pool_size = track.get("pool_size", 400)

        query = " OR ".join(f"cat:{c}" for c in categories)
        search = arxiv.Search(
            query=query,
            max_results=pool_size,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
        attempts = min(5, max(1, int(track.get("arxiv_retry_attempts", 3) or 3)))
        base_delay = min(60.0, max(1.0, float(track.get("arxiv_delay_seconds", 5.0) or 5.0)))
        client_retries = min(5, max(0, int(track.get("arxiv_client_retries", 2) or 0)))
        retryable = (arxiv.HTTPError, arxiv.UnexpectedEmptyPageError, requests.RequestException)

        for attempt in range(attempts):
            delay = min(60.0, base_delay * (2**attempt))
            client = arxiv.Client(page_size=100, delay_seconds=delay, num_retries=client_retries)
            signals: list[Signal] = []
            try:
                for r in client.results(search):  # newest-first, so we can stop early
                    if r.published < cutoff:
                        break
                    categories = list(getattr(r, "categories", []) or [])
                    signals.append(
                        Signal(
                            id=canonical_arxiv_id(r.get_short_id()),
                            title=r.title.strip(),
                            url=r.entry_id,
                            type="paper",
                            published_at=r.published,
                            summary=r.summary.strip().replace("\n", " "),
                            authors=[a.name for a in r.authors],
                            sources=[self.name],
                            extra={
                                "arxiv_categories": categories,
                                "primary_arxiv_category": getattr(r, "primary_category", None),
                            },
                        )
                    )
                return signals
            except retryable as exc:
                if attempt + 1 >= attempts:
                    raise
                print(
                    f"    ! arxiv attempt {attempt + 1}/{attempts} failed: {exc}; "
                    f"retrying in {delay:g}s"
                )
                time.sleep(delay)

        return []
