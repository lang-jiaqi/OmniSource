"""Scoring: combine component signals into one final score per item."""
from __future__ import annotations

from .scoring import DEFAULT_WEIGHTS, score_final

__all__ = ["DEFAULT_WEIGHTS", "score_final"]
