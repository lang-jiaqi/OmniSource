"""Rule-based expert reviewer subagents."""
from __future__ import annotations

import re

from .models import ExpertReview, ExpertSkill, PaperCandidate, ReviewScores, ReviewerSpec, Taxonomy, clamp01


class RuleBasedReviewer:
    """A deterministic reviewer that applies the leaf skill and shared rubric.

    This gives the harness testable behavior and a no-key MVP. A later LLM-backed
    reviewer can use the same ReviewerSpec/ExpertReview contracts.
    """

    def __init__(self, taxonomy: Taxonomy, skills: dict[str, ExpertSkill]):
        self.taxonomy = taxonomy
        self.skills = skills

    def review(self, candidate: PaperCandidate, spec: ReviewerSpec) -> ExpertReview:
        leaf = self.taxonomy.leaf(spec.leaf_id)
        skill = self.skills[spec.leaf_id]
        text = candidate.text_for_review().lower()
        keyword_hits = sum(1 for keyword in leaf.keywords if keyword.lower() in text)
        primary_bonus = 0.06 if candidate.primary_leaf == spec.leaf_id else 0.0
        adjacent_penalty = -0.03 if spec.relationship != "small_peer" else 0.0
        full = candidate.full_text_signals

        novelty = 0.42 + 0.045 * min(keyword_hits, 6) + primary_bonus + self._term_bonus(text, ["novel", "new", "first", "state-of-the-art", "breakthrough"])
        workload = 0.42 + self._term_bonus(text, ["large-scale", "extensive", "theorem", "proof", "system", "dataset", "benchmark"], weight=0.035)
        if full:
            workload += min(0.14, 0.02 * full.figure_count + 0.02 * full.table_count + 0.03 * full.formula_count)
        # A public repo is the only real evidence of open source — a paper merely
        # *claiming* it released code shouldn't get credit. So this is binary:
        # repo present → 1.0, otherwise 0.0.
        open_source = 1.0 if candidate.github_url else 0.0
        insight = 0.43 + 0.04 * min(keyword_hits, 5) + self._term_bonus(text, ["insight", "analysis", "ablation", "mechanism", "principle"], weight=0.03)
        presentation = 0.46 + (full.presentation_bonus if full else 0.0) + self._term_bonus(text, ["figure", "table", "equation", "clear", "analysis"], weight=0.02)

        if spec.lens == "evidence_reviewer":
            workload += 0.03
            presentation += 0.02
        elif spec.lens == "outside_field_reviewer":
            presentation += 0.04
            novelty += adjacent_penalty

        red_flags = self._red_flags(text, candidate)
        if red_flags:
            novelty -= 0.08
            workload -= 0.06
            insight -= 0.07
        if "no_strong_baseline" in red_flags:
            workload -= 0.08
        if "unclear_presentation" in red_flags:
            presentation -= 0.18

        scores = ReviewScores(
            novelty=novelty,
            workload=workload,
            open_source_completeness=open_source,
            insight_contribution=insight,
            paper_presentation=presentation,
        )
        must_keep = bool(candidate.field_year_normalized_citation and candidate.field_year_normalized_citation >= 0.995 and scores.novelty >= 0.7)
        rationale = f"{skill.prompt.splitlines()[0]} 依据 {spec.lens} 视角给出评分；关键词命中 {keyword_hits} 个，red_flags={red_flags or 'none'}。"
        return ExpertReview(
            reviewer_id=spec.reviewer_id,
            skill_leaf=spec.leaf_id,
            lens=spec.lens,
            relationship=spec.relationship,
            scores=scores,
            confidence=clamp01(0.62 + 0.04 * min(keyword_hits, 5) + (0.08 if candidate.full_text else 0.0)),
            rationale=rationale,
            red_flags=red_flags,
            must_keep_signal=must_keep,
            must_filter_signal=len(red_flags) >= 2,
        )

    def _term_bonus(self, text: str, terms: list[str], weight: float = 0.025) -> float:
        return min(0.12, weight * sum(1 for term in terms if term in text))

    def _red_flags(self, text: str, candidate: PaperCandidate) -> list[str]:
        flags: list[str] = []
        if candidate.is_withdrawn or "withdrawn" in text:
            flags.append("withdrawn")
        if candidate.is_retracted or "retracted" in text:
            flags.append("retracted")
        if re.search(r"\b(no|without)\s+(strong\s+)?baseline", text):
            flags.append("no_strong_baseline")
        if "data leakage" in text or "leaked" in text:
            flags.append("data_leakage")
        if candidate.full_text_signals and candidate.full_text_signals.word_count < 120 and len(candidate.abstract) < 400:
            flags.append("unclear_presentation")
        return sorted(set(flags))
