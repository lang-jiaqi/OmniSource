"""Reddit source with OpenCLI (default) and official OAuth backends.

OpenCLI reuses the local Chrome session and supports both keyword search and
fixed-subreddit feeds. The OAuth backend remains available for headless CI via
``mode: oauth`` and REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET.

Each post's external link is kept so canonicalization folds a Reddit post that
links an arXiv paper / GitHub repo onto that artifact as buzz.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import shlex
import shutil
import subprocess

import requests

from ..models import Signal
from .base import Source

USER_AGENT = "OmniSource/0.1 research radar"
TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API = "https://oauth.reddit.com"


class RedditSource(Source):
    name = "reddit"

    def fetch(self, track: dict) -> list[Signal]:
        cfg = track.get("reddit") or {}
        mode = cfg.get("mode", "opencli")
        if mode == "opencli":
            return self._fetch_opencli(track, cfg)
        if mode == "oauth":
            return self._fetch_oauth(track, cfg)
        print(f"    ! reddit: unknown mode '{mode}'")
        return []

    def _fetch_opencli(self, track: dict, cfg: dict) -> list[Signal]:
        command_prefix = _opencli_command_prefix()
        if not command_prefix or not _command_available(command_prefix):
            print("  reddit(opencli): skipped (opencli not installed)")
            return []

        search_cfg = cfg.get("search") or {}
        subreddits_cfg = cfg.get("subreddits") or {}
        queries = search_cfg.get("queries", cfg.get("queries", []))
        names = subreddits_cfg.get("names", track.get("reddit_subreddits", []))
        search_enabled = search_cfg.get("enabled", bool(queries))
        subreddits_enabled = subreddits_cfg.get("enabled", bool(names))
        timeout = int(cfg.get("timeout", 120))
        max_results = int(cfg.get("max_results", track.get("reddit_top", 50)))
        env = os.environ.copy()
        if profile := cfg.get("profile"):
            env["OPENCLI_PROFILE"] = str(profile)

        items: list[dict] = []
        if search_enabled:
            per_query = int(search_cfg.get("max_results_per_query", 30))
            for query in queries:
                command = [
                    *command_prefix, "reddit", "search", str(query),
                    "--sort", str(search_cfg.get("sort", "new")),
                    "--time", str(search_cfg.get("time", _time_filter(track.get("days", 3)))),
                    "--limit", str(per_query), "-f", "json",
                ]
                if subreddit := search_cfg.get("subreddit"):
                    command.extend(["--subreddit", _subreddit_name(subreddit)])
                items.extend(self._run_opencli(command, env, timeout, f"query '{query}'"))

        if subreddits_enabled:
            per_subreddit = int(subreddits_cfg.get("max_results_per_subreddit", 30))
            for name in names:
                normalized = _subreddit_name(name)
                command = [
                    *command_prefix, "reddit", "subreddit", normalized,
                    "--sort", str(subreddits_cfg.get("sort", "new")),
                    "--time", str(subreddits_cfg.get("time", _time_filter(track.get("days", 3)))),
                    "--limit", str(per_subreddit), "-f", "json",
                ]
                items.extend(self._run_opencli(command, env, timeout, f"subreddit 'r/{normalized}'"))

        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=int(track.get("days", 3)))
        signals: list[Signal] = []
        seen: set[str] = set()
        summary_max_chars = int(cfg.get("summary_max_chars", 400))
        for item in items:
            signal = _to_signal(item, summary_max_chars=summary_max_chars)
            if not signal or signal.url in seen:
                continue
            if signal.published_at and signal.published_at < cutoff:
                continue
            signal.extra["collector"] = "opencli"
            seen.add(signal.url)
            signals.append(signal)
            if len(signals) >= max_results:
                break
        return signals

    @staticmethod
    def _run_opencli(command: list[str], env: dict, timeout: int, label: str) -> list[dict]:
        try:
            out = subprocess.run(
                command, capture_output=True, text=True, timeout=timeout,
                check=True, env=env,
            ).stdout
            data = json.loads(out)
            if not isinstance(data, list):
                raise json.JSONDecodeError("expected a JSON array", out, 0)
            return [item for item in data if isinstance(item, dict)]
        except (subprocess.SubprocessError, json.JSONDecodeError) as exc:
            print(f"  reddit(opencli): {label} failed: {exc}")
            return []

    def _fetch_oauth(self, track: dict, cfg: dict) -> list[Signal]:
        client_id = os.environ.get("REDDIT_CLIENT_ID")
        secret = os.environ.get("REDDIT_CLIENT_SECRET")
        if not client_id or not secret:
            print("  reddit(oauth): skipped (no REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET)")
            return []
        try:
            token = self._token(client_id, secret)
        except Exception as exc:
            print(f"  reddit: auth failed: {exc}")
            return []

        days = track.get("days", 3)
        limit = cfg.get("max_results", track.get("reddit_top", 50))
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
        headers = {"Authorization": f"bearer {token}", "User-Agent": USER_AGENT}

        signals: list[Signal] = []
        for sub in track.get("reddit_subreddits", []):
            try:
                resp = requests.get(f"{API}/r/{sub}/new", params={"limit": limit}, headers=headers, timeout=30)
                resp.raise_for_status()
                children = resp.json().get("data", {}).get("children", [])
            except Exception as exc:  # one bad subreddit shouldn't lose the rest
                print(f"    ! reddit r/{sub} failed: {exc}")
                continue
            for child in children:
                d = child.get("data", {})
                created = dt.datetime.fromtimestamp(d.get("created_utc", 0), dt.timezone.utc)
                if created < cutoff:
                    continue
                external = d.get("url_overridden_by_dest") or d.get("url")
                permalink = "https://www.reddit.com" + d.get("permalink", "")
                signals.append(
                    Signal(
                        id=external or permalink,  # canonicalize remaps to the linked artifact
                        title=d.get("title", ""),
                        url=permalink,
                        type="social",
                        published_at=created,
                        summary=f"{d.get('title', '')} {external or ''} {d.get('selftext', '')[:500]}".strip(),
                        authors=[f"u/{d['author']}"] if d.get("author") else [],
                        sources=[self.name],
                        popularity=int(d.get("score") or 0),
                    )
                )
        return signals

    def _token(self, client_id: str, secret: str) -> str:
        resp = requests.post(
            TOKEN_URL,
            auth=(client_id, secret),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": USER_AGENT},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]


def _subreddit_name(value) -> str:
    name = str(value or "").strip()
    return name[2:] if name.lower().startswith("r/") else name


def _opencli_command_prefix() -> list[str]:
    """Reuse an explicitly configured OpenCLI bridge command when present."""
    configured = os.environ.get("OPENCLI_COMMAND", "").strip()
    return shlex.split(configured) if configured else ["opencli"]


def _command_available(command: list[str]) -> bool:
    executable = command[0] if command else ""
    return bool(executable and (os.path.isabs(executable) or shutil.which(executable)))


def _time_filter(days: int) -> str:
    days = int(days or 0)
    if days <= 1:
        return "day"
    if days <= 7:
        return "week"
    if days <= 31:
        return "month"
    if days <= 366:
        return "year"
    return "all"


def _int_value(value) -> int:
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return 0


def _created_at(value) -> dt.datetime | None:
    try:
        return dt.datetime.fromtimestamp(float(value), dt.timezone.utc)
    except (TypeError, ValueError, OSError):
        return None


def _to_signal(item: dict, *, summary_max_chars: int = 400) -> Signal | None:
    title = str(item.get("title") or "").strip()
    permalink = str(item.get("url") or "").strip()
    if not title or not permalink:
        return None
    external = str(item.get("url_overridden_by_dest") or "").strip()
    author = str(item.get("author") or "").strip()
    subreddit = str(item.get("subreddit") or "").strip()
    popularity = _int_value(item.get("score", item.get("upvotes", 0)))
    selftext = " ".join(str(item.get("selftext") or "").split())
    if summary_max_chars > 0 and len(selftext) > summary_max_chars:
        selftext = selftext[:summary_max_chars].rstrip() + "…"
    return Signal(
        id=external or permalink,
        title=title,
        url=permalink,
        type="social",
        published_at=_created_at(item.get("created_utc")),
        summary=f"{title} {external} {selftext}".strip(),
        authors=[f"u/{author}"] if author else [],
        sources=["reddit"],
        popularity=popularity,
        extra={
            "subreddit": subreddit,
            "comments": _int_value(item.get("comments")),
            **({"external_url": external} if external else {}),
            **({"post_hint": item.get("post_hint")} if item.get("post_hint") else {}),
            **({"preview_image_url": item.get("preview_image_url")} if item.get("preview_image_url") else {}),
            **({"gallery_urls": item.get("gallery_urls")} if item.get("gallery_urls") else {}),
        },
    )
