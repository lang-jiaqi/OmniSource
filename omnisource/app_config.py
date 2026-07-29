"""User-facing OmniSource configuration.

Track YAML files describe one radar. The root ``omnisource.yaml`` decides which
radars scheduled workflows should run.
"""
from __future__ import annotations

import os
from pathlib import Path

import yaml

from .config import BUNDLED_CONFIG_PATH, DEFAULT_TRACK, ROOT, track_path


def _default_config_path() -> Path:
    explicit = os.environ.get("OMNISOURCE_CONFIG_PATH")
    if explicit:
        return Path(explicit)
    workspace_config = ROOT / "omnisource.yaml"
    return workspace_config if workspace_config.exists() else BUNDLED_CONFIG_PATH


APP_CONFIG_PATH = _default_config_path()
DEFAULT_ACTIVE_TRACKS = ("research/ai-algorithm", "builder/ai-infra")


def load_app_config(path: Path | None = None) -> dict:
    config_path = path or APP_CONFIG_PATH
    if not config_path.exists():
        return {"active_tracks": list(DEFAULT_ACTIVE_TRACKS)}
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {"active_tracks": list(DEFAULT_ACTIVE_TRACKS)}


def active_tracks(path: Path | None = None, *, validate: bool = False) -> list[str]:
    raw = load_app_config(path).get("active_tracks", DEFAULT_ACTIVE_TRACKS)
    if isinstance(raw, str):
        tracks = [raw]
    elif isinstance(raw, list):
        tracks = [str(item) for item in raw]
    else:
        tracks = list(DEFAULT_ACTIVE_TRACKS)

    cleaned: list[str] = []
    for track in tracks:
        name = track.strip()
        if name and name not in cleaned:
            cleaned.append(name)
    if not cleaned:
        cleaned = [DEFAULT_TRACK]

    if validate:
        missing = [name for name in cleaned if not track_path(name).exists()]
        if missing:
            joined = ", ".join(missing)
            raise ValueError(f"active_tracks references missing track files: {joined}")
    return cleaned
