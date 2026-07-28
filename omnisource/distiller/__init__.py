"""Long-horizon CS paper distillation.

This package implements the experimental CS Paper Distiller: stable taxonomy,
multi-reviewer paper evaluation, hub decisions, and structured report output.
It is intentionally separate from the daily radar pipeline.
"""
from __future__ import annotations

from .pipeline import run_distiller

__all__ = ["run_distiller"]
