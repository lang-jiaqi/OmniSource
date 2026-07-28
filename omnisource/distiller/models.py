"""Data contracts for the CS Paper Distiller."""
from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DIMENSIONS = [
    "novelty",
    "workload",
    "open_source_completeness",
    "insight_contribution",
    "paper_presentation",
]


def clamp01(value: float | int | None) -> float:
    if value is None:
        return 0.0
    return max(0.0, min(1.0, float(value)))


_ARXIV_VERSION = re.compile(r"v\d+$", re.IGNORECASE)
_ARXIV_ID = re.compile(r"^(?:\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7})$", re.IGNORECASE)


def canonical_arxiv_id(value: str | None) -> str | None:
    if not value:
        return None
    clean = re.sub(r"^arxiv:", "", value.strip(), flags=re.IGNORECASE)
    clean = _ARXIV_VERSION.sub("", clean)
    return clean if _ARXIV_ID.match(clean) else None


def normalized_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


@dataclass(frozen=True)
class TaxonomyLeaf:
    leaf_id: str
    path: tuple[str, str, str]
    arxiv_categories: tuple[str, ...] = ()
    adjacent: tuple[str, ...] = ()
    venue_ids: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()

    @property
    def domain(self) -> str:
        return self.path[0]

    @property
    def area(self) -> str:
        return self.path[1]

    @property
    def name(self) -> str:
        return self.path[2]


@dataclass(frozen=True)
class Taxonomy:
    version: str
    leaves: dict[str, TaxonomyLeaf]
    max_depth: int = 3

    def leaf(self, leaf_id: str) -> TaxonomyLeaf:
        try:
            return self.leaves[leaf_id]
        except KeyError as exc:
            raise KeyError(f"Unknown taxonomy leaf: {leaf_id}") from exc

    def ids(self) -> list[str]:
        return sorted(self.leaves)


@dataclass(frozen=True)
class ExpertSkill:
    leaf_id: str
    prompt: str
    path: Path | None = None


@dataclass(frozen=True)
class ReviewerSpec:
    reviewer_id: str
    leaf_id: str
    lens: str
    relationship: str


@dataclass
class FullTextSignals:
    word_count: int = 0
    figure_count: int = 0
    table_count: int = 0
    formula_count: int = 0
    section_count: int = 0
    presentation_bonus: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "word_count": self.word_count,
            "figure_count": self.figure_count,
            "table_count": self.table_count,
            "formula_count": self.formula_count,
            "section_count": self.section_count,
            "presentation_bonus": self.presentation_bonus,
        }


@dataclass
class PaperCandidate:
    paper_id: str
    title: str
    abstract: str
    authors: list[str]
    published_at: dt.datetime
    primary_leaf: str | None = None
    secondary_leaves: list[str] = field(default_factory=list)
    arxiv_id: str | None = None
    doi: str | None = None
    venue: str | None = None
    url: str | None = None
    pdf_url: str | None = None
    github_url: str | None = None
    source_tags: list[str] = field(default_factory=list)
    full_text: str | None = None
    full_text_signals: FullTextSignals | None = None
    citation_count: int | None = None
    influential_citation_count: int | None = None
    field_year_normalized_citation: float | None = None
    hf_upvotes: int | None = None
    normalized_hf_upvote: float | None = None
    github_stars: int | None = None
    normalized_github_star: float | None = None
    self_citation_ratio: float | None = None
    is_withdrawn: bool = False
    is_retracted: bool = False
    survey_anchor_count: int = 0
    benchmark_years_active: int = 0
    contribution_type: str = "research"

    @property
    def year(self) -> int:
        return self.published_at.year

    @property
    def canonical_id(self) -> str:
        if self.doi:
            return f"doi:{self.doi.lower().strip()}"
        arxiv_id = canonical_arxiv_id(self.arxiv_id or self.paper_id)
        if arxiv_id:
            return f"arxiv:{arxiv_id}"
        return f"title:{normalized_title(self.title)}:{self.year}"

    def text_for_review(self) -> str:
        parts = [self.title, self.abstract]
        if self.full_text:
            parts.append(self.full_text[:12000])
        return "\n\n".join(p for p in parts if p)

    def supplemental_scores(self) -> "SupplementalScores":
        return SupplementalScores(
            citation=self.field_year_normalized_citation,
            hf_upvote=self.normalized_hf_upvote,
            github_star=self.normalized_github_star,
        )


@dataclass
class SupplementalScores:
    citation: float | None = None
    hf_upvote: float | None = None
    github_star: float | None = None

    def weighted(self) -> float:
        return (
            0.10 * clamp01(self.citation)
            + 0.05 * clamp01(self.hf_upvote)
            + 0.03 * clamp01(self.github_star)
        )

    def to_dict(self) -> dict[str, float | None]:
        return {
            "citation": self.citation,
            "hf_upvote": self.hf_upvote,
            "github_star": self.github_star,
        }


@dataclass
class ReviewScores:
    novelty: float
    workload: float
    open_source_completeness: float
    insight_contribution: float
    paper_presentation: float

    def __post_init__(self) -> None:
        for name in DIMENSIONS:
            setattr(self, name, clamp01(getattr(self, name)))

    def to_dict(self) -> dict[str, float]:
        return {name: getattr(self, name) for name in DIMENSIONS}

    def main_quality(self) -> float:
        return (
            0.28 * self.novelty
            + 0.18 * self.workload
            + 0.18 * self.open_source_completeness
            + 0.24 * self.insight_contribution
            + 0.12 * self.paper_presentation
        )


@dataclass
class ExpertReview:
    reviewer_id: str
    skill_leaf: str
    lens: str
    relationship: str
    scores: ReviewScores
    confidence: float
    rationale: str
    red_flags: list[str] = field(default_factory=list)
    must_keep_signal: bool = False
    must_filter_signal: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "reviewer_id": self.reviewer_id,
            "skill_leaf": self.skill_leaf,
            "lens": self.lens,
            "relationship": self.relationship,
            "scores": self.scores.to_dict(),
            "confidence": clamp01(self.confidence),
            "rationale": self.rationale,
            "red_flags": self.red_flags,
            "must_keep_signal": self.must_keep_signal,
            "must_filter_signal": self.must_filter_signal,
        }


@dataclass
class ReviewDecision:
    paper_id: str
    title: str
    primary_leaf: str
    publication_year: int
    reviewer_mean_scores: ReviewScores
    reviewer_dispersion: dict[str, float]
    supplementary_scores: SupplementalScores
    main_quality: float
    base_score: float
    age_decay: float
    age_adjusted_score: float
    keep_threshold: float
    decision: str
    decision_reason: str
    audit_trail: list[str]
    classic_evidence: list[str] = field(default_factory=list)
    review_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "primary_leaf": self.primary_leaf,
            "publication_year": self.publication_year,
            "reviewer_mean_scores": self.reviewer_mean_scores.to_dict(),
            "reviewer_dispersion": self.reviewer_dispersion,
            "supplementary_scores": self.supplementary_scores.to_dict(),
            "main_quality": self.main_quality,
            "base_score": self.base_score,
            "age_decay": self.age_decay,
            "age_adjusted_score": self.age_adjusted_score,
            "keep_threshold": self.keep_threshold,
            "decision": self.decision,
            "decision_reason": self.decision_reason,
            "audit_trail": self.audit_trail,
            "classic_evidence": self.classic_evidence,
            "review_count": self.review_count,
        }


@dataclass
class DistillerResult:
    summary_path: Path
    decisions_path: Path
    reviewer_traces_path: Path
    decisions: list[ReviewDecision]
    review_count: int
