"""Long-horizon source adapters and metadata enrichers."""
from __future__ import annotations

import datetime as dt
import os
from typing import Iterable

import requests

from .models import PaperCandidate, TaxonomyLeaf, canonical_arxiv_id


class CSLongHorizonArxivSource:
    name = "arxiv_long_horizon"

    def build_year_queries(self, leaf: TaxonomyLeaf, start_year: int, end_year: int) -> list[str]:
        categories = " OR ".join(f"cat:{category}" for category in leaf.arxiv_categories)
        return [
            f"({categories}) AND submittedDate:[{year}01010000 TO {year}12312359]"
            for year in range(start_year, end_year + 1)
        ]

    def fetch(self, leaves: Iterable[TaxonomyLeaf], years: int = 15, max_per_leaf_per_year: int = 2) -> list[PaperCandidate]:
        try:
            import arxiv  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError("Install the arxiv package to fetch live arXiv candidates") from exc
        end_year = dt.date.today().year
        start_year = end_year - years + 1
        client = arxiv.Client(page_size=100, delay_seconds=3.0, num_retries=3)
        candidates: list[PaperCandidate] = []
        for leaf in leaves:
            if not leaf.arxiv_categories:
                continue
            for query in self.build_year_queries(leaf, start_year=start_year, end_year=end_year):
                search = arxiv.Search(query=query, max_results=max_per_leaf_per_year, sort_by=arxiv.SortCriterion.SubmittedDate)
                for result in client.results(search):
                    arxiv_id = canonical_arxiv_id(result.get_short_id())
                    candidates.append(
                        PaperCandidate(
                            paper_id=f"arxiv:{arxiv_id}",
                            title=result.title.strip(),
                            abstract=result.summary.strip().replace("\n", " "),
                            authors=[author.name for author in result.authors],
                            published_at=result.published,
                            primary_leaf=leaf.leaf_id,
                            arxiv_id=arxiv_id,
                            url=result.entry_id,
                            pdf_url=getattr(result, "pdf_url", None),
                            source_tags=[self.name],
                        )
                    )
        return candidates


class VenueProceedingsSource:
    name = "venue_proceedings"
    endpoint = "https://api.openalex.org/works"

    def fetch(self, venue_names: list[str], leaf_id: str, years: int = 15, per_venue: int = 25) -> list[PaperCandidate]:
        current_year = dt.date.today().year
        from_date = f"{current_year - years}-01-01"
        candidates: list[PaperCandidate] = []
        for venue in venue_names:
            response = requests.get(
                self.endpoint,
                params={
                    "search": venue,
                    "filter": f"from_publication_date:{from_date}",
                    "per-page": per_venue,
                    "select": "id,doi,display_name,authorships,publication_year,publication_date,primary_location,cited_by_count,abstract_inverted_index",
                },
                timeout=30,
            )
            response.raise_for_status()
            for item in response.json().get("results", []):
                candidates.append(self._from_openalex(item, venue, leaf_id))
        return candidates

    def _from_openalex(self, item: dict, venue: str, leaf_id: str) -> PaperCandidate:
        year = int(item.get("publication_year") or dt.date.today().year)
        date = item.get("publication_date") or f"{year}-01-01"
        authors = [a.get("author", {}).get("display_name", "") for a in item.get("authorships", [])]
        return PaperCandidate(
            paper_id=item.get("doi") or item.get("id") or item.get("display_name"),
            title=item.get("display_name", ""),
            abstract=_invert_openalex_abstract(item.get("abstract_inverted_index")),
            authors=[a for a in authors if a],
            published_at=dt.datetime.fromisoformat(date).replace(tzinfo=dt.timezone.utc),
            primary_leaf=leaf_id,
            doi=(item.get("doi") or "").removeprefix("https://doi.org/") or None,
            venue=venue,
            url=item.get("id"),
            citation_count=item.get("cited_by_count"),
            source_tags=[self.name],
        )


class CitationMetadataSource:
    endpoint = "https://api.semanticscholar.org/graph/v1/paper"

    def enrich(self, candidate: PaperCandidate) -> PaperCandidate:
        identifier = candidate.doi or candidate.arxiv_id or candidate.title
        if not identifier:
            return candidate
        response = requests.get(
            f"{self.endpoint}/{identifier}",
            params={"fields": "citationCount,influentialCitationCount,isOpenAccess,externalIds"},
            timeout=30,
        )
        if response.status_code == 404:
            return candidate
        response.raise_for_status()
        data = response.json()
        candidate.citation_count = data.get("citationCount") or candidate.citation_count
        candidate.influential_citation_count = data.get("influentialCitationCount") or candidate.influential_citation_count
        candidate.field_year_normalized_citation = _squash_count(candidate.citation_count)
        return candidate


class HFPaperSignalSource:
    endpoint = "https://huggingface.co/api/daily_papers"

    def enrich_many(self, candidates: list[PaperCandidate], limit: int = 500) -> list[PaperCandidate]:
        response = requests.get(self.endpoint, params={"limit": limit}, timeout=30)
        response.raise_for_status()
        by_arxiv = {}
        for item in response.json():
            paper = item.get("paper", {})
            arxiv_id = canonical_arxiv_id(paper.get("id"))
            if arxiv_id:
                by_arxiv[arxiv_id] = paper
        max_upvotes = max([paper.get("upvotes", 0) or 0 for paper in by_arxiv.values()] or [1])
        for candidate in candidates:
            paper = by_arxiv.get(canonical_arxiv_id(candidate.arxiv_id))
            if not paper:
                continue
            candidate.hf_upvotes = paper.get("upvotes", 0) or 0
            candidate.normalized_hf_upvote = min(1.0, candidate.hf_upvotes / max_upvotes)
            candidate.github_url = candidate.github_url or paper.get("githubRepo")
        return candidates


class CodeSignalSource:
    endpoint = "https://api.github.com/search/repositories"

    def enrich(self, candidate: PaperCandidate) -> PaperCandidate:
        if candidate.github_url:
            return candidate
        headers = {"Accept": "application/vnd.github+json"}
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        response = requests.get(
            self.endpoint,
            params={"q": f'"{candidate.title}"', "sort": "stars", "order": "desc", "per_page": 1},
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        items = response.json().get("items", [])
        if items:
            repo = items[0]
            candidate.github_url = repo.get("html_url")
            candidate.github_stars = repo.get("stargazers_count")
            candidate.normalized_github_star = _squash_count(candidate.github_stars)
        return candidate


def _invert_openalex_abstract(index: dict | None) -> str:
    if not index:
        return ""
    positions: list[tuple[int, str]] = []
    for word, offsets in index.items():
        positions.extend((int(offset), word) for offset in offsets)
    return " ".join(word for _offset, word in sorted(positions))


def _squash_count(value: int | None) -> float | None:
    if value is None:
        return None
    return min(1.0, (value / (value + 100.0)))
