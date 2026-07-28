"""Central paths and tunables. One place to look for 'where do things live'."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRACKS_DIR = ROOT / "tracks"
# Keep reusable core outputs beside the public package. The private official
# site can redirect generated data through environment variables.
REPORTS_DIR = Path(os.environ.get("OMNISOURCE_REPORTS_DIR", ROOT / "reports"))
DATA_DIR = Path(os.environ.get("OMNISOURCE_DATA_DIR", ROOT / "data"))
DB_PATH = DATA_DIR / "memory.db"
CACHE_DIR = DATA_DIR / "cache"

# HTTP fetch cache lifetime (seconds). Lets repeated/same-day runs reuse fetches.
CACHE_TTL = int(os.environ.get("OMNISOURCE_CACHE_TTL", 6 * 3600))

DEFAULT_TRACK = "builder/ai-infra"


def track_path(name: str) -> Path:
    """Resolve a track reference such as ``research/ai-algorithm``.

    Bare names remain supported for existing local commands when they identify
    exactly one YAML file.
    """
    reference = str(name or "").strip().replace("\\", "/").strip("/")
    if not reference or any(part in {".", ".."} for part in reference.split("/")):
        raise ValueError(f"Invalid track reference: {name!r}")
    direct = TRACKS_DIR / f"{reference}.yaml"
    if direct.exists():
        return direct
    if "/" not in reference:
        matches = sorted(TRACKS_DIR.rglob(f"{reference}.yaml"))
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise ValueError(f"Track name is ambiguous; use a folder prefix: {name!r}")
    return direct


def track_references() -> list[str]:
    """Return track references relative to ``tracks/`` without file suffixes."""
    return sorted(path.relative_to(TRACKS_DIR).with_suffix("").as_posix() for path in TRACKS_DIR.rglob("*.yaml"))
