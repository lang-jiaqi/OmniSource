"""End-to-end CS Paper Distiller pipeline."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

from ..config import REPORTS_DIR, ROOT
from .audit import AuditAgent
from .canonicalize import dedup_candidates
from .fulltext import PDFFullTextFetcher, attach_full_text_signals
from .hub import HubAgent
from .models import DistillerResult, ExpertReview, PaperCandidate, ReviewDecision
from .reviewer import RuleBasedReviewer
from .router import PaperRouter
from .selection import ExpertSelector
from .skills import load_skill_library
from .sources import CSLongHorizonArxivSource, CitationMetadataSource, CodeSignalSource, HFPaperSignalSource, VenueProceedingsSource
from .taxonomy import load_taxonomy
from .venue_registry import load_venue_registry

HARNESS_VERSION = "cs-distiller-mvp-v1"


def _build_reviewer(backend, taxonomy, skills, provider, model, full_text):
    """LLM reviewer if requested and available, else the rule-based one."""
    if backend == "llm":
        try:
            from ..main import load_dotenv
            from .llm_reviewer import LLMReviewer
            load_dotenv(ROOT / ".env")
            reviewer = LLMReviewer(taxonomy, skills, provider=provider, model=model, full_text=full_text)
            print(f"  reviewer: llm ({provider}/{model or 'default'}, full_text={full_text})")
            return reviewer
        except Exception as exc:
            print(f"  ! llm reviewer unavailable ({exc}); using rule-based reviewer")
    return RuleBasedReviewer(taxonomy, skills)


def run_distiller(
    taxonomy_name: str = "cs-foundation-v1",
    years: int = 15,
    dry_run: bool = False,
    max_candidates: int = 30,
    output_dir: Path | None = None,
    current_year: int | None = None,
    candidates: list[PaperCandidate] | None = None,
    include_venues: bool = True,
    fetch_pdf_text: bool = False,
    enrich_metadata: bool | None = None,
    reviewer_backend: str = "rule",
    reviewer_provider: str = "openai",
    reviewer_model: str | None = None,
    reviewer_full_text: str = "never",
) -> DistillerResult:
    taxonomy = load_taxonomy(taxonomy_name)
    skills = load_skill_library(taxonomy)
    output_dir = output_dir or REPORTS_DIR / "cs-distiller"
    output_dir.mkdir(parents=True, exist_ok=True)

    if candidates is None:
        if dry_run:
            candidates = _sample_candidates()
        else:
            leaves = list(taxonomy.leaves.values())
            per_leaf_per_year = max(1, max_candidates // max(1, len(leaves) * years))
            candidates = CSLongHorizonArxivSource().fetch(leaves, years=years, max_per_leaf_per_year=per_leaf_per_year)
            if include_venues:
                registry = load_venue_registry()
                venue_source = VenueProceedingsSource()
                per_venue = max(1, per_leaf_per_year // 2)
                for leaf in leaves:
                    venue_names = registry.names_for_leaf(leaf.leaf_id)[:3]
                    if not venue_names:
                        continue
                    try:
                        candidates.extend(venue_source.fetch(venue_names, leaf.leaf_id, years=years, per_venue=per_venue))
                    except Exception as exc:
                        print(f"  ! venue source failed for {leaf.leaf_id}: {exc}")
    candidates = dedup_candidates(candidates)[:max_candidates]
    if enrich_metadata is None:
        enrich_metadata = not dry_run
    if enrich_metadata:
        candidates = enrich_candidates(candidates)

    router = PaperRouter(taxonomy)
    selector = ExpertSelector(taxonomy)
    reviewer = _build_reviewer(reviewer_backend, taxonomy, skills, reviewer_provider, reviewer_model, reviewer_full_text)
    hub = HubAgent(current_year=current_year)
    audit = AuditAgent()
    pdf_fetcher = PDFFullTextFetcher() if fetch_pdf_text else None
    if pdf_fetcher:
        pdf_fetcher.require_pdf_parser()

    decisions: list[ReviewDecision] = []
    traces: list[dict[str, Any]] = []
    for candidate in candidates:
        router.route(candidate)
        if pdf_fetcher and candidate.pdf_url and not candidate.full_text:
            try:
                candidate.full_text = pdf_fetcher.fetch_text(candidate.pdf_url)
            except Exception as exc:
                candidate.source_tags.append(f"pdf_fetch_failed:{exc.__class__.__name__}")
        attach_full_text_signals(candidate)
        specs = selector.select(candidate.primary_leaf or "ai.ml_foundations", candidate.canonical_id, HARNESS_VERSION)
        reviews = [reviewer.review(candidate, spec) for spec in specs]
        decision = hub.decide(candidate, reviews, candidate.supplemental_scores())
        errors = audit.validate_decision(decision)
        if errors:
            decision.audit_trail.extend(f"audit_error={error}" for error in errors)
        decisions.append(decision)
        traces.extend(_trace(candidate, review) for review in reviews)

    date_str = dt.date.today().isoformat()
    stem = f"{taxonomy.version}-{date_str}"
    summary_path = output_dir / f"{stem}.summary.md"
    decisions_path = output_dir / f"{stem}.decisions.jsonl"
    traces_path = output_dir / f"{stem}.reviewer_traces.jsonl"
    summary_path.write_text(_render_summary(taxonomy.version, decisions), encoding="utf-8")
    _write_jsonl(decisions_path, [decision.to_dict() for decision in decisions])
    _write_jsonl(traces_path, traces)
    return DistillerResult(
        summary_path=summary_path,
        decisions_path=decisions_path,
        reviewer_traces_path=traces_path,
        decisions=decisions,
        review_count=len(traces),
    )


def load_candidates_jsonl(path: Path) -> list[PaperCandidate]:
    out: list[PaperCandidate] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        published = raw.get("published_at")
        published_at = dt.datetime.fromisoformat(published.replace("Z", "+00:00")) if published else dt.datetime(raw.get("year", dt.date.today().year), 1, 1, tzinfo=dt.timezone.utc)
        out.append(
            PaperCandidate(
                paper_id=raw["paper_id"],
                title=raw["title"],
                abstract=raw.get("abstract", ""),
                authors=raw.get("authors", []),
                published_at=published_at,
                primary_leaf=raw.get("primary_leaf"),
                secondary_leaves=raw.get("secondary_leaves", []),
                arxiv_id=raw.get("arxiv_id"),
                doi=raw.get("doi"),
                venue=raw.get("venue"),
                url=raw.get("url"),
                pdf_url=raw.get("pdf_url"),
                github_url=raw.get("github_url"),
                source_tags=raw.get("source_tags", []),
                full_text=raw.get("full_text"),
                citation_count=raw.get("citation_count"),
                influential_citation_count=raw.get("influential_citation_count"),
                field_year_normalized_citation=raw.get("field_year_normalized_citation"),
                hf_upvotes=raw.get("hf_upvotes"),
                normalized_hf_upvote=raw.get("normalized_hf_upvote"),
                github_stars=raw.get("github_stars"),
                normalized_github_star=raw.get("normalized_github_star"),
                self_citation_ratio=raw.get("self_citation_ratio"),
                is_withdrawn=bool(raw.get("is_withdrawn", False)),
                is_retracted=bool(raw.get("is_retracted", False)),
                survey_anchor_count=int(raw.get("survey_anchor_count", 0)),
                benchmark_years_active=int(raw.get("benchmark_years_active", 0)),
                contribution_type=raw.get("contribution_type", "research"),
            )
        )
    return out


def enrich_candidates(
    candidates: list[PaperCandidate],
    citation_source=None,
    hf_source=None,
    code_source=None,
) -> list[PaperCandidate]:
    citation_source = citation_source or CitationMetadataSource()
    hf_source = hf_source or HFPaperSignalSource()
    code_source = code_source or CodeSignalSource()

    try:
        candidates = hf_source.enrich_many(candidates)
    except Exception as exc:
        print(f"  ! hf enrichment failed: {exc}")

    enriched: list[PaperCandidate] = []
    for candidate in candidates:
        try:
            candidate = citation_source.enrich(candidate)
        except Exception as exc:
            candidate.source_tags.append(f"citation_enrich_failed:{exc.__class__.__name__}")
        try:
            candidate = code_source.enrich(candidate)
        except Exception as exc:
            candidate.source_tags.append(f"code_enrich_failed:{exc.__class__.__name__}")
        enriched.append(candidate)
    return enriched


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _trace(candidate: PaperCandidate, review: ExpertReview) -> dict[str, Any]:
    record = review.to_dict()
    record["paper_id"] = candidate.canonical_id
    record["title"] = candidate.title
    record["primary_leaf"] = candidate.primary_leaf
    return record


def _render_summary(taxonomy_version: str, decisions: list[ReviewDecision]) -> str:
    counts = {name: sum(1 for d in decisions if d.decision == name) for name in ["keep", "human_review", "filter"]}
    lines = [
        f"# CS Paper Distiller — {taxonomy_version}",
        "",
        f"*{len(decisions)} candidates · keep {counts['keep']} · human_review {counts['human_review']} · filter {counts['filter']}*",
        "",
    ]
    for decision in sorted(decisions, key=lambda d: (d.decision != "keep", -d.age_adjusted_score)):
        lines += [
            f"## {decision.title}",
            f"- **Decision:** {decision.decision} / {decision.decision_reason}",
            f"- **Leaf:** {decision.primary_leaf} · **Year:** {decision.publication_year} · **Score:** {decision.age_adjusted_score:.2f}",
            f"- **Scores:** novelty {decision.reviewer_mean_scores.novelty:.2f}, workload {decision.reviewer_mean_scores.workload:.2f}, open-source {decision.reviewer_mean_scores.open_source_completeness:.2f}, insight {decision.reviewer_mean_scores.insight_contribution:.2f}, presentation {decision.reviewer_mean_scores.paper_presentation:.2f}",
            "",
        ]
    return "\n".join(lines)


def _sample_candidates() -> list[PaperCandidate]:
    tz = dt.timezone.utc
    return [
        PaperCandidate(
            paper_id="arxiv:1706.03762",
            title="Attention Is All You Need",
            abstract="We propose the Transformer, a novel attention architecture for sequence transduction with extensive experiments and analysis.",
            authors=["Ashish Vaswani", "Noam Shazeer"],
            published_at=dt.datetime(2017, 6, 12, tzinfo=tz),
            primary_leaf="ai.nlp_speech",
            arxiv_id="1706.03762",
            github_url="https://github.com/tensorflow/tensor2tensor",
            field_year_normalized_citation=1.0,
            normalized_hf_upvote=0.0,
            normalized_github_star=0.6,
            survey_anchor_count=5,
            full_text="Abstract\nWe introduce attention. Figure 1 shows the architecture. Table 1 reports translation results. Equation: Attention(Q,K,V)=softmax(QK^T)V. Experiments include ablations and strong baselines.",
            source_tags=["dry_run"],
        ),
        PaperCandidate(
            paper_id="arxiv:1512.03385",
            title="Deep Residual Learning for Image Recognition",
            abstract="We present a residual learning framework and extensive image recognition experiments.",
            authors=["Kaiming He", "Xiangyu Zhang"],
            published_at=dt.datetime(2015, 12, 10, tzinfo=tz),
            primary_leaf="ai.cv_multimodal",
            arxiv_id="1512.03385",
            field_year_normalized_citation=1.0,
            normalized_github_star=0.5,
            survey_anchor_count=5,
            full_text="Introduction\nResidual networks make optimization easier. Figure 2 and Table 3 show ImageNet results. Equation: y = F(x) + x.",
            source_tags=["dry_run"],
        ),
        PaperCandidate(
            paper_id="arxiv:1401.00001",
            title="A Small Incremental Network Tuning Trick",
            abstract="We tune a minor parameter without strong baseline comparisons.",
            authors=["Example Author"],
            published_at=dt.datetime(2014, 1, 1, tzinfo=tz),
            primary_leaf="systems.networking",
            arxiv_id="1401.00001",
            field_year_normalized_citation=0.1,
            normalized_hf_upvote=None,
            normalized_github_star=None,
            full_text="Short note. Without strong baseline. No public code.",
            source_tags=["dry_run"],
        ),
    ]
