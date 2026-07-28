"""A tiny on-disk HTTP GET cache.

The radar re-fetches the same feeds on repeated and same-day runs (daily +
weekly, testing, multiple tracks). cached_get reuses a recent response instead
of hitting the network again. Keyed by URL + params, expires after CACHE_TTL.
"""
from __future__ import annotations

import hashlib
import time

import requests

from ..config import CACHE_DIR, CACHE_TTL


def cached_get(url: str, params: dict | None = None, headers: dict | None = None,
               ttl: int = CACHE_TTL, timeout: int = 30) -> str:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(f"{url}?{sorted((params or {}).items())}".encode()).hexdigest()[:16]
    path = CACHE_DIR / f"{key}.txt"
    if path.exists() and time.time() - path.stat().st_mtime < ttl:
        return path.read_text(encoding="utf-8")
    resp = requests.get(url, params=params, headers=headers, timeout=timeout)
    resp.raise_for_status()
    path.write_text(resp.text, encoding="utf-8")
    return resp.text
