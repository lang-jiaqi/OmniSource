"""Classic-paper override registry."""
from __future__ import annotations

from ..config import ROOT
from .models import PaperCandidate, canonical_arxiv_id, normalized_title
from .taxonomy import load_structured_file

CLASSICS_PATH = ROOT / "omnisource" / "taxonomies" / "classic_papers.yaml"


class ClassicRegistry:
    def __init__(self, records: list[dict] | None = None):
        self.records = records if records is not None else load_structured_file(CLASSICS_PATH).get("papers", [])

    def evidence_for(self, candidate: PaperCandidate, must_keep_count: int = 0) -> list[str]:
        evidence: list[str] = []
        candidate_arxiv = canonical_arxiv_id(candidate.arxiv_id or candidate.paper_id)
        candidate_title = normalized_title(candidate.title)
        for record in self.records:
            arxiv = canonical_arxiv_id(record.get("arxiv_id"))
            doi = (record.get("doi") or "").lower().strip()
            if arxiv and candidate_arxiv == arxiv:
                evidence.append(f"classic_registry:{record.get('key', arxiv)}")
                continue
            if doi and candidate.doi and candidate.doi.lower().strip() == doi:
                evidence.append(f"classic_registry:{record.get('key', doi)}")
                continue
            # Title-only matching is intentionally conservative. If both sides
            # have stronger identifiers and they disagree, this is not the same
            # paper even if a bad upstream record reused a famous title.
            record_has_identifier = bool(arxiv or doi)
            candidate_has_identifier = bool(candidate_arxiv or candidate.doi)
            if not (record_has_identifier and candidate_has_identifier) and normalized_title(record.get("title", "")) == candidate_title:
                evidence.append(f"classic_registry:{record.get('key', candidate_title)}")
        if candidate.field_year_normalized_citation is not None and candidate.field_year_normalized_citation >= 0.995 and must_keep_count >= 2:
            evidence.append("field_year_citation_p99.5")
        if candidate.survey_anchor_count >= 3:
            evidence.append("survey_anchor")
        if candidate.benchmark_years_active >= 5:
            evidence.append("benchmark_protocol_anchor")
        return sorted(set(evidence))
