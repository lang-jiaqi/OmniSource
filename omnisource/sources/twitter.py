"""Twitter/X source — two tiers, mirroring how mature radars do it.

  mode: apify  (default) — Apify's danek/twitter-scraper actor. Your X
                account is never used, so it's safe to run in CI. Needs APIFY_TOKEN.
  mode: opencli — shell out to OpenCLI, reusing your logged-in Chrome session.
                  Supports both keyword search and fixed-account timelines.
  mode: local  — shell out to `twitter-cli`, which uses YOUR exported x.com
                cookies. Free, but ToS-risky (use a throwaway account) and not
                for CI. Opt-in, local only.

Opt-in per track: a track uses it only if it lists `twitter` under sources AND
provides a `twitter:` config block. Without APIFY_TOKEN the source skips cleanly.
Twitter signals are type "social"; they become useful once canonicalization
folds them onto the paper/repo they link.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import shlex
import shutil
import subprocess

import requests

from ..models import Signal
from .base import Source

APIFY_BASE = "https://api.apify.com/v2"
DEFAULT_APIFY_ACTOR = "danek/twitter-scraper"
SHORT_URL_RE = re.compile(r"https?://t\.co/[A-Za-z0-9_%-]+")
REFERENCE_URL_MARKERS = (
    "arxiv.org/abs/",
    "arxiv.org/pdf/",
    "ar5iv.org/abs/",
    "huggingface.co/papers/",
    "github.com/",
    "doi.org/",
)
URL_FIELD_NAMES = {
    "expanded_url",
    "expandedUrl",
    "unwound_url",
    "unwoundUrl",
    "display_url",
    "displayUrl",
    "url",
    "href",
}


def _parse_dt(value) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        try:
            return dt.datetime.strptime(str(value), "%a %b %d %H:%M:%S %z %Y")
        except ValueError:
            return None


def _parse_count(value) -> int:
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value or "0").strip().replace(",", "")
    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*([KMB]?)", text, re.IGNORECASE)
    if not match:
        return 0
    multiplier = {"": 1, "K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
    return int(float(match.group(1)) * multiplier[match.group(2).upper()])


def _reference_urls(item: object) -> list[str]:
    """Extract expanded artifact links from Apify's varying tweet schemas."""
    urls: list[str] = []

    def walk(value: object, key: str | None = None) -> None:
        if isinstance(value, dict):
            for child_key, child in value.items():
                walk(child, str(child_key))
            return
        if isinstance(value, list):
            for child in value:
                walk(child, key)
            return
        if not isinstance(value, str) or key not in URL_FIELD_NAMES:
            return
        url = value.strip()
        if not url.startswith(("http://", "https://")):
            return
        if not any(marker in url.lower() for marker in REFERENCE_URL_MARKERS):
            return
        if url not in urls:
            urls.append(url)

    walk(item)
    return urls


def _looks_like_reference_url(url: str) -> bool:
    return any(marker in url.lower() for marker in REFERENCE_URL_MARKERS)


def _expand_short_urls(text: str, *, max_urls: int = 2) -> list[str]:
    """Resolve t.co links only when Apify did not provide expanded artifact URLs."""
    urls: list[str] = []
    for short_url in SHORT_URL_RE.findall(text)[:max_urls]:
        try:
            resp = requests.head(short_url, allow_redirects=True, timeout=2)
            expanded = resp.url
            if not _looks_like_reference_url(expanded):
                resp = requests.get(short_url, allow_redirects=True, timeout=2, stream=True)
                resp.close()
                expanded = resp.url
        except requests.RequestException:
            continue
        if _looks_like_reference_url(expanded) and expanded not in urls:
            urls.append(expanded)
    return urls


def _to_signal(item: dict, *, resolve_short_links: bool = True) -> Signal | None:
    if item.get("demo") or item.get("noResults"):
        return None
    url = item.get("url") or item.get("twitterUrl") or item.get("tweetUrl")
    if not url and item.get("screen_name") and item.get("tweet_id"):
        url = f"https://x.com/{item['screen_name']}/status/{item['tweet_id']}"
    text = item.get("text") or item.get("full_text") or item.get("content") or ""
    if not url or not text:
        return None
    author = item.get("author") or {}
    user_info = item.get("user_info") or {}
    handle = author.get("userName") if isinstance(author, dict) else author
    handle = (
        handle
        or user_info.get("screen_name")
        or user_info.get("userName")
        or item.get("username")
        or item.get("screen_name")
        or "?"
    )
    likes = item.get("likeCount") or item.get("favorite_count") or item.get("likes") or item.get("favorites") or 0
    reference_urls = [link for link in _reference_urls(item) if link not in text]
    if resolve_short_links and not reference_urls:
        reference_urls = _expand_short_urls(text)
    summary = text
    if reference_urls:
        summary = f"{text}\n\nReferenced links:\n" + "\n".join(reference_urls)
    return Signal(
        id=url,  # canonicalization remaps to the linked arXiv/GitHub if present
        title=text.split("\n", 1)[0][:120],
        url=url,
        type="social",
        published_at=_parse_dt(item.get("createdAt") or item.get("created_at")),
        summary=summary,
        authors=[f"@{handle}"],
        sources=["twitter"],
        popularity=_parse_count(likes),
        extra={
            "reference_urls": reference_urls,
            **({"views": _parse_count(item.get("views"))} if item.get("views") is not None else {}),
            **({"retweets": _parse_count(item.get("retweets"))} if item.get("retweets") is not None else {}),
            **({"replies": _parse_count(item.get("replies"))} if item.get("replies") is not None else {}),
            **({"is_retweet": bool(item.get("is_retweet"))} if "is_retweet" in item else {}),
            **({"media_urls": item.get("media_urls")} if item.get("media_urls") else {}),
            **({"quoted_tweet": item.get("quoted_tweet")} if item.get("quoted_tweet") else {}),
        },
    )


def _actor_id(actor: str) -> str:
    return actor.replace("/", "~")


def _quoted_terms(terms: list[str]) -> str:
    return " OR ".join(f'"{term}"' if " " in term else term for term in terms)


def _query_suffix(cfg: dict) -> str:
    suffix_parts: list[str] = []
    if suffix := cfg.get("query_suffix"):
        suffix_parts.append(str(suffix))
    if language := cfg.get("tweet_language") or cfg.get("tweetLanguage"):
        suffix_parts.append(f"lang:{language}")
    return " ".join(suffix_parts)


def _with_suffix(query: str, suffix: str) -> str:
    return f"{query} {suffix}".strip()


def _danek_payloads(cfg: dict) -> list[dict]:
    suffix = _query_suffix(cfg)
    queries: list[str] = []
    if query := cfg.get("query"):
        queries.append(_with_suffix(str(query), suffix))
    elif cfg.get("queries"):
        queries.append(_with_suffix(f"({_quoted_terms(list(cfg['queries']))})", suffix))

    handles = [str(handle).lstrip("@") for handle in cfg.get("handles", [])]
    if handles:
        from_terms = " OR ".join(f"from:{handle}" for handle in handles)
        queries.append(_with_suffix(f"({from_terms})", suffix))

    max_results = int(cfg.get("max_results", 50))
    max_per_query = max(5, max_results // max(1, len(queries)))
    return [{"query": query, "max_posts": max_per_query} for query in queries if query]


def _apify_payloads(actor: str, cfg: dict) -> list[dict]:
    if actor == "danek~twitter-scraper":
        return _danek_payloads(cfg)
    payload = {
        "searchTerms": cfg.get("queries", []),
        "twitterHandles": cfg.get("handles", []),
        "maxItems": cfg.get("max_results", 50),
        "onlyVerifiedUsers": cfg.get("only_verified", False),
    }
    if tweet_language := cfg.get("tweet_language") or cfg.get("tweetLanguage"):
        payload["tweetLanguage"] = tweet_language
    if sort := cfg.get("sort"):
        payload["sort"] = sort
    return [payload]


def _opencli_command_prefix() -> list[str]:
    """Use an explicitly configured OpenCLI runtime, if one is provided."""
    configured = os.environ.get("OPENCLI_COMMAND", "").strip()
    return shlex.split(configured) if configured else ["opencli"]


def _command_available(command: list[str]) -> bool:
    executable = command[0] if command else ""
    return bool(executable and (os.path.isabs(executable) or shutil.which(executable)))


class TwitterSource(Source):
    name = "twitter"

    def fetch(self, track: dict) -> list[Signal]:
        cfg = track.get("twitter")
        if not cfg:
            return []
        mode = cfg.get("mode", "apify")
        if mode == "apify":
            return self._fetch_apify(track, cfg)
        if mode == "opencli":
            return self._fetch_opencli(track, cfg)
        if mode == "local":
            return self._fetch_local(track, cfg)
        print(f"    ! twitter: unknown mode '{mode}'")
        return []

    def _fetch_apify(self, track: dict, cfg: dict) -> list[Signal]:
        token = os.environ.get("APIFY_TOKEN")
        if not token:
            print("  twitter(apify): skipped (no APIFY_TOKEN)")
            return []
        actor = _actor_id(cfg.get("apify_actor", DEFAULT_APIFY_ACTOR))
        signals: list[Signal] = []
        for payload in _apify_payloads(actor, cfg):
            resp = requests.post(
                f"{APIFY_BASE}/acts/{actor}/run-sync-get-dataset-items",
                params={"token": token},
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            items = resp.json()
            resolve_short_links = bool(cfg.get("resolve_short_links", True))
            short_link_budget = int(cfg.get("resolve_short_links_max", 12) or 0)
            for item in items:
                text = item.get("text") or item.get("full_text") or item.get("content") or ""
                should_resolve = bool(resolve_short_links and short_link_budget > 0 and SHORT_URL_RE.search(text))
                if should_resolve:
                    short_link_budget -= 1
                if signal := _to_signal(item, resolve_short_links=should_resolve):
                    signals.append(signal)
            if not signals and any(isinstance(it, dict) and it.get("demo") for it in items):
                print("  twitter(apify): actor returned demo rows; check actor access/billing in Apify")
            elif not signals and any(isinstance(it, dict) and it.get("noResults") for it in items):
                print("  twitter(apify): no results for configured queries/handles")
        return signals

    def _fetch_opencli(self, track: dict, cfg: dict) -> list[Signal]:
        command_prefix = _opencli_command_prefix()
        if not command_prefix or not _command_available(command_prefix):
            print("  twitter(opencli): skipped (opencli not installed)")
            return []

        search_cfg = cfg.get("search") or {}
        accounts_cfg = cfg.get("accounts") or {}
        queries = search_cfg.get("queries", cfg.get("queries", []))
        handles = accounts_cfg.get("handles", cfg.get("handles", []))
        search_enabled = search_cfg.get("enabled", bool(queries))
        accounts_enabled = accounts_cfg.get("enabled", bool(handles))
        timeout = int(cfg.get("timeout", 120))
        max_results = int(cfg.get("max_results", 150))
        env = os.environ.copy()
        if profile := cfg.get("profile"):
            env["OPENCLI_PROFILE"] = str(profile)

        items: list[dict] = []
        if search_enabled:
            per_query = int(search_cfg.get("max_results_per_query", cfg.get("max_results", 30)))
            for query in queries:
                final_query = str(query).strip()
                if language := search_cfg.get("language", cfg.get("tweet_language")):
                    final_query = f"{final_query} lang:{language}"
                days = int(track.get("days", 0) or 0)
                if days:
                    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).date()
                    final_query = f"{final_query} since:{since.isoformat()}"
                if search_cfg.get("exclude_replies", False):
                    final_query += " -filter:replies"
                if search_cfg.get("exclude_retweets", False):
                    final_query += " -filter:nativeretweets"
                command = [
                    *command_prefix, "twitter", "search", final_query,
                    "--product", str(search_cfg.get("product", "live")),
                    "--limit", str(per_query), "-f", "json",
                ]
                if has := search_cfg.get("has"):
                    command.extend(["--has", str(has)])
                items.extend(self._run_opencli(command, env, timeout, f"query '{query}'"))

        if accounts_enabled:
            per_handle = int(accounts_cfg.get("max_results_per_handle", 30))
            page_delay = int(accounts_cfg.get("page_delay", 2))
            include_retweets = bool(accounts_cfg.get("include_retweets", False))
            for handle in handles:
                command = [
                    *command_prefix, "twitter", "tweets", str(handle).lstrip("@"),
                    "--limit", str(per_handle), "--page-delay", str(page_delay),
                    "-f", "json",
                ]
                account_items = self._run_opencli(command, env, timeout, f"account '@{str(handle).lstrip('@')}'")
                if not include_retweets:
                    account_items = [item for item in account_items if not item.get("is_retweet")]
                items.extend(account_items)

        signals: list[Signal] = []
        seen: set[str] = set()
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=int(track.get("days", 0) or 0))
        for item in items:
            signal = _to_signal(item)
            if not signal or signal.id in seen:
                continue
            if track.get("days") and signal.published_at:
                published = signal.published_at
                if published.tzinfo is None:
                    published = published.replace(tzinfo=dt.timezone.utc)
                if published < cutoff:
                    continue
            signal.extra["collector"] = "opencli"
            seen.add(signal.id)
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
            print(f"  twitter(opencli): {label} failed: {exc}")
            return []

    def _fetch_local(self, track: dict, cfg: dict) -> list[Signal]:
        if not shutil.which("twitter"):
            print("  twitter(local): skipped (twitter-cli not installed)")
            return []
        n = str(cfg.get("max_results", 30))
        signals: list[Signal] = []
        for query in cfg.get("queries", []):
            try:
                out = subprocess.run(
                    ["twitter", "search", query, "-n", n, "--json"],
                    capture_output=True, text=True, timeout=120, check=True,
                ).stdout
                items = json.loads(out)
                signals += [s for it in (items if isinstance(items, list) else []) if (s := _to_signal(it))]
            except (subprocess.SubprocessError, json.JSONDecodeError) as exc:
                print(f"  twitter(local): query '{query}' failed: {exc}")
        return signals
