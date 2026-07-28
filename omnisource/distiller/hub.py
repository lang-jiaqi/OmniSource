"""Hub-agent scoring and keep/filter decisions."""
from __future__ import annotations

import math
from collections import Counter
from statistics import mean, pstdev

from .classics import ClassicRegistry
from .models import DIMENSIONS, ExpertReview, PaperCandidate, ReviewDecision, ReviewScores, SupplementalScores, clamp01


class HubAgent:
    def __init__(self, current_year: int | None = None, classic_registry: ClassicRegistry | None = None):
        self.current_year = current_year
        self.classic_registry = classic_registry or ClassicRegistry()

    def decide(
        self,
        candidate: PaperCandidate,
        reviews: list[ExpertReview],
        supplemental: SupplementalScores | None = None,
    ) -> ReviewDecision:
        if len(reviews) != 6:
            raise ValueError(f"Expected exactly 6 expert reviews, got {len(reviews)}")
        supplemental = supplemental or candidate.supplemental_scores()
        means = self._mean_scores(reviews)
        dispersion = self._dispersion(reviews)
        main_quality = means.main_quality()
        adjusted_supplemental = self._adjust_supplemental(candidate, supplemental)
        base_score = clamp01(0.82 * main_quality + adjusted_supplemental.weighted())
        current_year = self.current_year or max(candidate.year, 2026)
        age_decay = self.age_decay(candidate.year, current_year)
        age_adjusted = clamp01(base_score * age_decay)
        threshold = self.keep_threshold(candidate.year, current_year)
        audit = [
            f"main_quality={main_quality:.3f}",
            f"supplementary={adjusted_supplemental.weighted():.3f}",
            f"age_decay={age_decay:.3f}",
            f"threshold={threshold:.3f}",
        ]

        if candidate.is_withdrawn or candidate.is_retracted:
            return self._decision(candidate, reviews, means, dispersion, adjusted_supplemental, main_quality, base_score, age_decay, age_adjusted, threshold, "filter", "withdrawn_or_retracted", audit)

        classic_evidence = self.classic_registry.evidence_for(candidate, must_keep_count=sum(1 for r in reviews if r.must_keep_signal))
        if classic_evidence:
            audit.append("classic")
            audit.append("classic_override")
            return self._decision(candidate, reviews, means, dispersion, adjusted_supplemental, main_quality, base_score, age_decay, max(age_adjusted, 0.85), threshold, "keep", "classic_override", audit, classic_evidence)

        severe_reason = self._severe_consensus_red_flag(reviews)
        if severe_reason:
            audit.append(f"red_flag={severe_reason}")
            return self._decision(candidate, reviews, means, dispersion, adjusted_supplemental, main_quality, base_score, age_decay, age_adjusted, threshold, "filter", "severe_consensus_red_flags", audit)

        if max(dispersion.values()) > 0.25:
            audit.append("reviewer_dispersion")
            return self._decision(candidate, reviews, means, dispersion, adjusted_supplemental, main_quality, base_score, age_decay, age_adjusted, threshold, "human_review", "reviewer_dispersion", audit)

        if self._young_breakthrough(candidate, means, adjusted_supplemental, current_year):
            reason = "young_breakthrough_rescue"
            decision = "keep" if main_quality >= 0.78 else "human_review"
            audit.append(reason)
            return self._decision(candidate, reviews, means, dispersion, adjusted_supplemental, main_quality, base_score, age_decay, max(age_adjusted, threshold), threshold, decision, reason, audit)

        if age_adjusted >= threshold:
            return self._decision(candidate, reviews, means, dispersion, adjusted_supplemental, main_quality, base_score, age_decay, age_adjusted, threshold, "keep", "score_above_threshold", audit)
        if age_adjusted >= threshold - 0.05:
            return self._decision(candidate, reviews, means, dispersion, adjusted_supplemental, main_quality, base_score, age_decay, age_adjusted, threshold, "human_review", "near_threshold", audit)
        return self._decision(candidate, reviews, means, dispersion, adjusted_supplemental, main_quality, base_score, age_decay, age_adjusted, threshold, "filter", "below_threshold", audit)

    @staticmethod
    def age_decay(publication_year: int, current_year: int) -> float:
        age_years = max(0, current_year - publication_year)
        return max(0.55, math.exp(-age_years / 8.0))

    @staticmethod
    def keep_threshold(publication_year: int, current_year: int) -> float:
        age_years = max(0, current_year - publication_year)
        if age_years <= 3:
            return 0.72
        if age_years <= 8:
            return 0.76
        return 0.82

    def _mean_scores(self, reviews: list[ExpertReview]) -> ReviewScores:
        values = {name: mean(getattr(r.scores, name) for r in reviews) for name in DIMENSIONS}
        return ReviewScores(**values)

    def _dispersion(self, reviews: list[ExpertReview]) -> dict[str, float]:
        return {name: pstdev(getattr(r.scores, name) for r in reviews) for name in DIMENSIONS}

    def _adjust_supplemental(self, candidate: PaperCandidate, supplemental: SupplementalScores) -> SupplementalScores:
        citation = supplemental.citation
        if citation is not None and candidate.self_citation_ratio is not None and candidate.self_citation_ratio >= 0.5:
            citation *= 0.5
        return SupplementalScores(citation=citation, hf_upvote=supplemental.hf_upvote, github_star=supplemental.github_star)

    def _severe_consensus_red_flag(self, reviews: list[ExpertReview]) -> str | None:
        flags = Counter(flag for review in reviews for flag in review.red_flags)
        for flag, count in flags.items():
            if count >= 3:
                return flag
        if sum(1 for review in reviews if review.must_filter_signal) >= 3:
            return "must_filter_consensus"
        return None

    def _young_breakthrough(self, candidate: PaperCandidate, means: ReviewScores, supplemental: SupplementalScores, current_year: int) -> bool:
        age_years = max(0, current_year - candidate.year)
        if age_years > 1:
            return False
        return (
            means.main_quality() >= 0.78
            or (means.novelty >= 0.85 and means.insight_contribution >= 0.80)
            or clamp01(supplemental.hf_upvote) >= 0.95
            or clamp01(supplemental.github_star) >= 0.95
        )

    def _decision(
        self,
        candidate: PaperCandidate,
        reviews: list[ExpertReview],
        means: ReviewScores,
        dispersion: dict[str, float],
        supplemental: SupplementalScores,
        main_quality: float,
        base_score: float,
        age_decay: float,
        age_adjusted: float,
        threshold: float,
        decision: str,
        reason: str,
        audit: list[str],
        classic_evidence: list[str] | None = None,
    ) -> ReviewDecision:
        return ReviewDecision(
            paper_id=candidate.canonical_id,
            title=candidate.title,
            primary_leaf=candidate.primary_leaf or "unknown",
            publication_year=candidate.year,
            reviewer_mean_scores=means,
            reviewer_dispersion=dispersion,
            supplementary_scores=supplemental,
            main_quality=round(main_quality, 6),
            base_score=round(base_score, 6),
            age_decay=round(age_decay, 6),
            age_adjusted_score=round(age_adjusted, 6),
            keep_threshold=threshold,
            decision=decision,
            decision_reason=reason,
            audit_trail=audit,
            classic_evidence=classic_evidence or [],
            review_count=len(reviews),
        )
