"""GitHub source: track-relevant repos with recent momentum.

GitHub has no official Trending API. We therefore scrape GitHub Trending first
and use Search only as a fresh-repo fallback pool. For repo ranking,
``popularity`` means recent momentum (stars today/week, or an estimated
stars-per-day rate), while ``extra.total_stars`` keeps the lifetime star count
for display and maturity checks.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re

from ..memory.cache import cached_get
from ..models import Signal
from .base import Source

API_URL = "https://api.github.com/search/repositories"
REPO_API_URL = "https://api.github.com/repos/{full_name}"
TRENDING_URL = "https://github.com/trending"

_ARTICLE_RE = re.compile(r"<article\b[^>]*>(.*?)</article>", re.S | re.I)
_REPO_LINK_RE = re.compile(r'href="/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)"')
_DESC_RE = re.compile(r"<p\b[^>]*>(.*?)</p>", re.S | re.I)
_LANG_RE = re.compile(r'itemprop="programmingLanguage"[^>]*>(.*?)</span>', re.S | re.I)
_TREND_RE = re.compile(r"([\d,]+)\s+stars?\s+(today|this week|this month)", re.I)
_TAG_RE = re.compile(r"<[^>]+>")
_OR_RE = re.compile(r"\s+OR\s+", re.I)


def _parse_dt(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def _strip_tags(value: str | None) -> str:
    return html.unescape(_TAG_RE.sub(" ", value or "")).replace("\n", " ").strip()


def _count(value: str | None) -> int:
    try:
        return int(str(value or "0").replace(",", "").strip())
    except ValueError:
        return 0


def _age_days(value: str | None, today: dt.date | None = None) -> float | None:
    parsed = _parse_dt(value)
    if not parsed:
        return None
    today = today or dt.datetime.now(dt.timezone.utc).date()
    return max(1.0, (today - parsed.date()).days)


def _star_velocity(total_stars: int, created_at: str | None) -> float:
    age = _age_days(created_at)
    if age is None:
        return float(total_stars)
    return total_stars / age


def _period_days(period: str | None) -> int:
    return {"daily": 1, "weekly": 7, "monthly": 30}.get(str(period or "").lower(), 1)


def _as_list(value, default: list[str]) -> list[str]:
    if value is None:
        return default
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value]


def _split_or_terms(value: str, limit: int) -> list[str]:
    terms: list[str] = []
    for term in _OR_RE.split(str(value)):
        cleaned = term.strip().strip('"').strip("'")
        if cleaned and cleaned not in terms:
            terms.append(cleaned)
        if len(terms) >= limit:
            break
    return terms


def _or_query(terms: list[str]) -> str:
    return " OR ".join(f'"{term}"' if " " in term else term for term in terms)


def _terms(track: dict) -> list[str]:
    raw_terms: list[str] = []
    query = track.get("github_query")
    if query:
        raw_terms.extend(_OR_RE.split(str(query)))
    raw_terms.extend(str(keyword) for keyword in track.get("keywords", []))
    cleaned = []
    for term in raw_terms:
        term = term.strip().strip('"').strip("'").lower()
        if term and term not in cleaned:
            cleaned.append(term)
    return cleaned


def _matches_track(blob: str, track: dict) -> bool:
    text = blob.lower()
    for term in _terms(track):
        if term in text:
            return True
        words = [word for word in re.split(r"[^a-z0-9.+-]+", term) if len(word) >= 3]
        if len(words) > 1 and all(word in text for word in words):
            return True
    return False


def _parse_trending(html_body: str) -> list[dict]:
    entries = []
    for block in _ARTICLE_RE.findall(html_body):
        link = _REPO_LINK_RE.search(block)
        if not link:
            continue
        full_name = link.group(1)
        desc_match = _DESC_RE.search(block)
        lang_match = _LANG_RE.search(block)
        trend_match = _TREND_RE.search(_strip_tags(block))
        entries.append({
            "full_name": full_name,
            "description": _strip_tags(desc_match.group(1) if desc_match else ""),
            "language": _strip_tags(lang_match.group(1) if lang_match else ""),
            "trending_stars": _count(trend_match.group(1) if trend_match else "0"),
            "trending_window": trend_match.group(2).lower() if trend_match else "",
        })
    return entries


class GitHubSource(Source):
    name = "github"

    def _api_headers(self) -> dict:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "OmniSource research radar",
        }
        token = os.environ.get("GITHUB_TOKEN")
        if token:  # raises the rate limit; present in GitHub Actions
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _query(self, track: dict) -> str:
        # GitHub caps boolean operators at five, so keep the API query short.
        if track.get("github_query"):
            terms = _or_query(_split_or_terms(str(track["github_query"]), 5))
        else:
            terms = _or_query([str(k) for k in track.get("keywords", [])[:4]])
        now = dt.datetime.now(dt.timezone.utc)
        pushed_cutoff = (now - dt.timedelta(days=track.get("github_days", 14))).date()
        created_days = int(track.get("github_fallback_created_days", 120))
        created_cutoff = (now - dt.timedelta(days=created_days)).date()
        return f"{terms} created:>={created_cutoff.isoformat()} pushed:>={pushed_cutoff.isoformat()}"

    def _repo_details(self, full_name: str, headers: dict) -> dict:
        try:
            body = cached_get(REPO_API_URL.format(full_name=full_name), headers=headers)
            data = json.loads(body)
            return data if data.get("full_name") else {}
        except Exception:
            return {}

    def _signal_from_repo(
        self,
        full_name: str,
        repo: dict,
        *,
        fallback_description: str = "",
        trending_period: str | None = None,
        trending_stars: int = 0,
        discovery: str,
    ) -> Signal:
        owner = (repo.get("owner") or {}).get("login") or full_name.split("/")[0]
        total_stars = int(repo.get("stargazers_count") or 0)
        velocity = _star_velocity(total_stars, repo.get("created_at"))
        momentum = trending_stars / _period_days(trending_period) if trending_stars else velocity
        extra = {
            "created_at": repo.get("created_at"),
            "pushed_at": repo.get("pushed_at"),
            "forks": repo.get("forks_count", 0),
            "open_issues": repo.get("open_issues_count", 0),
            "topics": repo.get("topics") or [],
            "license": (repo.get("license") or {}).get("spdx_id"),
            "homepage": repo.get("homepage") or "",
            "language": repo.get("language") or "",
            "total_stars": total_stars,
            "star_velocity": round(velocity, 2),
            "repo_discovery": discovery,
        }
        if trending_stars:
            extra.update({
                "trending_period": trending_period,
                "trending_stars": trending_stars,
            })
        return Signal(
            id=f"github:{full_name}",
            title=repo.get("full_name") or full_name,
            url=repo.get("html_url") or f"https://github.com/{full_name}",
            type="repo",
            published_at=_parse_dt(repo.get("pushed_at")),
            summary=repo.get("description") or fallback_description,
            authors=[owner] if owner else [],
            sources=[self.name],
            code_url=repo.get("html_url") or f"https://github.com/{full_name}",
            popularity=max(0, int(round(momentum))),
            extra=extra,
        )

    def _fetch_trending(self, track: dict, headers: dict) -> list[Signal]:
        periods = _as_list(track.get("github_trending_periods"), ["daily", "weekly"])
        languages = _as_list(track.get("github_trending_languages"), [""])
        limit = int(track.get("github_trending_top", 25))
        html_headers = {"Accept": "text/html", "User-Agent": "OmniSource research radar"}
        signals: list[Signal] = []
        seen: set[str] = set()
        for period in periods:
            for language in languages:
                url = f"{TRENDING_URL}/{language}" if language else TRENDING_URL
                try:
                    body = cached_get(url, params={"since": period}, headers=html_headers)
                except Exception:
                    continue
                for entry in _parse_trending(body):
                    full_name = entry["full_name"]
                    if full_name in seen:
                        continue
                    entry_blob = f"{full_name} {entry['description']} {entry['language']}"
                    if not _matches_track(entry_blob, track):
                        continue
                    repo = self._repo_details(full_name, headers)
                    repo_blob = " ".join([
                        full_name,
                        repo.get("description") or entry["description"],
                        repo.get("language") or entry["language"],
                        " ".join(repo.get("topics") or []),
                    ])
                    if repo and not _matches_track(repo_blob, track):
                        continue
                    signals.append(self._signal_from_repo(
                        full_name,
                        repo,
                        fallback_description=entry["description"],
                        trending_period=period,
                        trending_stars=entry["trending_stars"],
                        discovery="trending",
                    ))
                    seen.add(full_name)
                    if len(signals) >= limit:
                        return signals
        return signals

    def _is_fresh_fallback(self, signal: Signal, track: dict) -> bool:
        created_days = int(track.get("github_fallback_created_days", 120))
        age = _age_days((signal.extra or {}).get("created_at"))
        if age is None:
            return False
        return age <= created_days

    def _fetch_search(self, track: dict, headers: dict, limit: int) -> list[Signal]:
        body = cached_get(
            API_URL,
            params={
                "q": self._query(track),
                "sort": track.get("github_search_sort", "stars"),
                "order": "desc",
                "per_page": limit,
            },
            headers=headers,
        )

        signals: list[Signal] = []
        for r in json.loads(body).get("items", []):
            signal = self._signal_from_repo(r["full_name"], r, discovery="fresh_search")
            if self._is_fresh_fallback(signal, track):
                signals.append(signal)
        return signals

    def fetch(self, track: dict) -> list[Signal]:
        headers = self._api_headers()
        limit = int(track.get("github_top", 30))
        signals: list[Signal] = []
        seen: set[str] = set()

        if track.get("github_trending", True):
            for signal in self._fetch_trending(track, headers):
                signals.append(signal)
                seen.add(signal.id)

        if track.get("github_fallback_search", True) and len(signals) < limit:
            for signal in self._fetch_search(track, headers, limit - len(signals)):
                if signal.id in seen:
                    continue
                signals.append(signal)
                seen.add(signal.id)

        return signals
