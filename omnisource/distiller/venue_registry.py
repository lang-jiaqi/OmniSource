"""Versioned top-conference venue registry."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..config import ROOT
from .taxonomy import load_structured_file

VENUE_REGISTRY_PATH = ROOT / "omnisource" / "taxonomies" / "venue_registry.yaml"


@dataclass(frozen=True)
class Venue:
    venue_id: str
    names: tuple[str, ...]
    leaves: tuple[str, ...]


@dataclass(frozen=True)
class VenueRegistry:
    version: str
    venues: dict[str, Venue]

    def names_for_leaf(self, leaf_id: str) -> list[str]:
        names: list[str] = []
        for venue in self.venues.values():
            if leaf_id in venue.leaves:
                names.extend(venue.names)
        return names


def load_venue_registry(path: Path | None = None) -> VenueRegistry:
    data = load_structured_file(path or VENUE_REGISTRY_PATH)
    venues = {
        raw["id"]: Venue(
            venue_id=raw["id"],
            names=tuple(raw.get("names", [])),
            leaves=tuple(raw.get("leaves", [])),
        )
        for raw in data.get("venues", [])
    }
    return VenueRegistry(version=data.get("venue_registry_version", "unknown"), venues=venues)
