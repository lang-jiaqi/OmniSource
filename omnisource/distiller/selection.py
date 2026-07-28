"""Reviewer selection for the six-expert harness."""
from __future__ import annotations

import hashlib
import random

from .models import ReviewerSpec, Taxonomy

SMALL_PEER_LENSES = ("method_reviewer", "evidence_reviewer", "reproducibility_reviewer")


class ExpertSelector:
    def __init__(self, taxonomy: Taxonomy):
        self.taxonomy = taxonomy

    def select(self, primary_leaf: str, canonical_paper_id: str, harness_version: str) -> list[ReviewerSpec]:
        leaf = self.taxonomy.leaf(primary_leaf)
        reviewers = [
            ReviewerSpec(
                reviewer_id=f"{primary_leaf}.{lens}",
                leaf_id=primary_leaf,
                lens=lens,
                relationship="small_peer",
            )
            for lens in SMALL_PEER_LENSES
        ]

        adjacent = list(leaf.adjacent)
        if len(adjacent) < 2:
            adjacent.extend(self._nearest_by_taxonomy(primary_leaf, exclude={primary_leaf, *adjacent}))
        for i, leaf_id in enumerate(adjacent[:2], 1):
            reviewers.append(
                ReviewerSpec(
                    reviewer_id=f"{leaf_id}.adjacent_big_peer_{i}",
                    leaf_id=leaf_id,
                    lens="cross_field_reviewer",
                    relationship="adjacent_big_peer",
                )
            )

        excluded = {primary_leaf, *leaf.adjacent, *(r.leaf_id for r in reviewers)}
        far_pool = [leaf_id for leaf_id in self.taxonomy.ids() if leaf_id not in excluded]
        if not far_pool:
            far_pool = [leaf_id for leaf_id in self.taxonomy.ids() if leaf_id != primary_leaf]
        seed = int(hashlib.sha256(f"{canonical_paper_id}:{self.taxonomy.version}:{harness_version}".encode()).hexdigest()[:16], 16)
        far_leaf = random.Random(seed).choice(far_pool)
        reviewers.append(
            ReviewerSpec(
                reviewer_id=f"{far_leaf}.random_big_peer",
                leaf_id=far_leaf,
                lens="outside_field_reviewer",
                relationship="random_big_peer",
            )
        )
        return reviewers

    def _nearest_by_taxonomy(self, primary_leaf: str, exclude: set[str]) -> list[str]:
        primary = self.taxonomy.leaf(primary_leaf)
        scored: list[tuple[int, str]] = []
        for leaf_id, leaf in self.taxonomy.leaves.items():
            if leaf_id in exclude:
                continue
            score = 0
            if leaf.domain == primary.domain:
                score += 2
            if leaf.area == primary.area:
                score += 3
            scored.append((-score, leaf_id))
        return [leaf_id for _score, leaf_id in sorted(scored)]
