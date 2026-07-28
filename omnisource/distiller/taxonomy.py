"""Load and validate the fixed CS taxonomy."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..config import ROOT
from .models import Taxonomy, TaxonomyLeaf

TAXONOMY_DIR = ROOT / "omnisource" / "taxonomies"


def _file_stem(name: str) -> str:
    return name.replace("-", "_")


def load_structured_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError(f"{path} is not JSON and PyYAML is not installed") from exc
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise ValueError(f"{path} must contain a mapping")
        return data


def load_taxonomy(name: str = "cs-foundation-v1", path: Path | None = None) -> Taxonomy:
    path = path or TAXONOMY_DIR / f"{_file_stem(name)}.yaml"
    data = load_structured_file(path)
    version = data.get("taxonomy_version")
    if not version:
        raise ValueError("taxonomy_version is required")
    max_depth = int(data.get("max_depth", 3))
    if max_depth > 3:
        raise ValueError("CS taxonomy depth must not exceed 3")

    leaves: dict[str, TaxonomyLeaf] = {}
    for raw in data.get("leaves", []):
        leaf_id = raw["id"]
        path_parts = tuple(raw["path"])
        if len(path_parts) != 3:
            raise ValueError(f"{leaf_id} must have exactly three path components")
        leaves[leaf_id] = TaxonomyLeaf(
            leaf_id=leaf_id,
            path=path_parts,  # type: ignore[arg-type]
            arxiv_categories=tuple(raw.get("arxiv", [])),
            adjacent=tuple(raw.get("adjacent", [])),
            venue_ids=tuple(raw.get("venues", [])),
            keywords=tuple(raw.get("keywords", [])),
        )

    taxonomy = Taxonomy(version=version, max_depth=max_depth, leaves=leaves)
    for leaf in taxonomy.leaves.values():
        missing = [adj for adj in leaf.adjacent if adj not in taxonomy.leaves]
        if missing:
            raise ValueError(f"{leaf.leaf_id} references missing adjacent leaves: {missing}")
    return taxonomy
