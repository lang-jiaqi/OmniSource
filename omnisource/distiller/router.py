"""Route candidates into taxonomy leaves."""
from __future__ import annotations

from .models import PaperCandidate, Taxonomy


class PaperRouter:
    def __init__(self, taxonomy: Taxonomy):
        self.taxonomy = taxonomy

    def route(self, candidate: PaperCandidate) -> PaperCandidate:
        if candidate.primary_leaf and candidate.primary_leaf in self.taxonomy.leaves:
            return candidate
        text = f"{candidate.title} {candidate.abstract}".lower()
        best_leaf = None
        best_score = -1
        for leaf in self.taxonomy.leaves.values():
            score = 0
            if candidate.arxiv_id and any(cat.lower() in text for cat in leaf.arxiv_categories):
                score += 1
            score += sum(2 for kw in leaf.keywords if kw.lower() in text)
            if candidate.venue and candidate.venue.lower() in " ".join(leaf.venue_ids).lower():
                score += 3
            if score > best_score:
                best_leaf = leaf.leaf_id
                best_score = score
        candidate.primary_leaf = best_leaf or "ai.ml_foundations"
        return candidate
