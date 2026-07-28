"""Schema and consistency checks for distiller decisions."""
from __future__ import annotations

from .models import DIMENSIONS, ReviewDecision


class AuditAgent:
    def validate_decision(self, decision: ReviewDecision) -> list[str]:
        errors: list[str] = []
        if decision.decision not in {"keep", "filter", "human_review"}:
            errors.append("decision must be keep/filter/human_review")
        if decision.review_count != 6:
            errors.append("decision must aggregate exactly 6 expert reviews")
        scores = decision.reviewer_mean_scores.to_dict()
        for name in DIMENSIONS:
            value = scores.get(name)
            if value is None or not 0.0 <= value <= 1.0:
                errors.append(f"{name} must be in [0, 1]")
        if decision.decision == "keep" and decision.decision_reason == "classic_override" and not decision.classic_evidence:
            errors.append("classic_override must include classic_evidence")
        if decision.keep_threshold <= 0:
            errors.append("keep_threshold must be positive")
        return errors
