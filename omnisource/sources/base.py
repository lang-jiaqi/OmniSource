"""Source base class.

The contract is deliberately tiny: given a track config, return a list of
Signals. A Source must not filter, rank, or summarize — that is the pipeline's
job. Keeping sources dumb is what makes them easy to add.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import Signal


class Source(ABC):
    name: str  # registry key, also recorded on each Signal it produces

    @abstractmethod
    def fetch(self, track: dict) -> list[Signal]:
        """Return recent Signals for this track. Raising is fine; the pipeline
        isolates one source's failure from the others."""
        raise NotImplementedError
