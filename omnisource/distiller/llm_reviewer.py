"""LLM-backed expert reviewer — a drop-in for RuleBasedReviewer.

Same `review(candidate, spec) -> ExpertReview` contract, so HubAgent and the rest
of the pipeline are unchanged. Each reviewer uses the leaf's expert persona plus a
critical (AI-Scientist style) rubric and emits the five ReviewScores dimensions.

Cost-aware: abstract-only by default (`full_text="always"` to include full text),
and it falls back to the rule-based reviewer on any LLM/parse error so the
six-reviewer panel always completes.
"""
from __future__ import annotations

from ..llm import get_provider
from .models import ExpertReview, ExpertSkill, PaperCandidate, ReviewScores, ReviewerSpec, Taxonomy, clamp01
from .reviewer import RuleBasedReviewer

CRITICAL_RUBRIC = (
    "You are reviewing for a prestigious venue. Be critical and cautious: if a "
    "paper is weak or you are unsure, score it low. Reward genuine novelty, rigor, "
    "reproducibility and insight; punish overclaiming, thin evaluation and missing "
    "baselines.\n"
    "Score each dimension 0..1. Respond with JSON only, keys:\n"
    "- novelty: how new the idea/result is\n"
    "- workload: technical depth, rigor, scale of the work\n"
    "- open_source: code/data/artifact availability and reproducibility\n"
    "- insight: significance and depth of the contribution\n"
    "- presentation: clarity and quality of writing/figures\n"
    "- confidence: 0..1\n"
    "- red_flags: short tags like no_strong_baseline / overclaiming / data_leakage, [] if none\n"
    "- must_keep: true only for a clear landmark / strong accept\n"
    "- must_filter: true only for a clear reject\n"
    "- rationale: one sentence"
)

LENS_HINT = {
    "evidence_reviewer": "Focus on whether the claims are supported by evidence.",
    "reproducibility_reviewer": "Focus on reproducibility and released artifacts.",
    "outside_field_reviewer": "You are from an adjacent field; weigh clarity and general significance.",
}


class LLMReviewer:
    def __init__(self, taxonomy: Taxonomy, skills: dict[str, ExpertSkill],
                 provider: str = "openai", model: str | None = None, full_text: str = "never"):
        self.taxonomy = taxonomy
        self.skills = skills
        self.full_text = full_text
        self.provider = get_provider(provider, model)  # raises if unavailable
        self._fallback = RuleBasedReviewer(taxonomy, skills)

    def review(self, candidate: PaperCandidate, spec: ReviewerSpec) -> ExpertReview:
        try:
            return self._llm_review(candidate, spec)
        except Exception as exc:  # never break the six-reviewer panel
            print(f"    ! llm reviewer fell back to rules for {candidate.canonical_id}: {exc}")
            return self._fallback.review(candidate, spec)

    def _llm_review(self, candidate: PaperCandidate, spec: ReviewerSpec) -> ExpertReview:
        persona = self.skills[spec.leaf_id].prompt.splitlines()[0]
        system = f"{persona}\n{LENS_HINT.get(spec.lens, '')}\n\n{CRITICAL_RUBRIC}"
        if self.full_text == "always" and candidate.full_text:
            body = candidate.text_for_review()
        else:
            body = f"Title: {candidate.title}\n\nAbstract: {candidate.abstract}"

        data = self.provider.complete_json(system, body)  # providers already return a dict
        scores = ReviewScores(
            novelty=clamp01(data.get("novelty")),
            workload=clamp01(data.get("workload")),
            open_source_completeness=clamp01(data.get("open_source")),
            insight_contribution=clamp01(data.get("insight")),
            paper_presentation=clamp01(data.get("presentation")),
        )
        red_flags = [str(f) for f in (data.get("red_flags") or [])]
        return ExpertReview(
            reviewer_id=spec.reviewer_id,
            skill_leaf=spec.leaf_id,
            lens=spec.lens,
            relationship=spec.relationship,
            scores=scores,
            confidence=clamp01(data.get("confidence", 0.6)),
            rationale=str(data.get("rationale", ""))[:300],
            red_flags=red_flags,
            must_keep_signal=bool(data.get("must_keep")),
            must_filter_signal=bool(data.get("must_filter") or len(red_flags) >= 2),
        )
