"""OmniSource pipeline orchestrator.

A thin wiring layer: Collector → Curator → (memory) → Quality → Analyst → Editor → Publishers.
Each stage lives in its own module; this file only sequences them.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import time
from copy import deepcopy
from dataclasses import asdict, fields
from pathlib import Path

import yaml

from .agents import Collector, curator, editor, quality
from .config import DB_PATH, DEFAULT_TRACK, REPORTS_DIR, ROOT, track_path
from .memory import SignalStore
from .models import Signal
from .personalization import adjusted_score
from .publishers import Report, build_publishers


def load_dotenv(path: Path) -> None:
    """Minimal .env loader so secrets stay out of the shell/repo. Existing env
    vars win, which is what we want when GitHub Actions injects them."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_track(name: str) -> dict:
    with track_path(name).open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def export_jsonl(signals: list[Signal], path: Path) -> None:
    """One JSON object per line, so the day's briefing is available structured
    (for downstream analysis, datasets, or re-publishing) alongside the report."""
    with path.open("w", encoding="utf-8") as f:
        for s in signals:
            record = asdict(s)
            record["published_at"] = s.published_at.isoformat() if s.published_at else None
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def report_signals_path(track_name: str, date_str: str, *, weekly: bool = False) -> Path:
    """Return the per-track snapshot path used for an offline site rebuild."""
    prefix = "weekly-" if weekly else ""
    safe_name = track_name.replace("/", "--")
    return REPORTS_DIR / f"report-{prefix}{safe_name}-{date_str}.signals.jsonl"


def load_signal_jsonl(path: Path) -> list[Signal]:
    """Restore exported signals without collecting sources or calling an LLM."""
    signal_fields = {item.name for item in fields(Signal)}
    signals: list[Signal] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL in {path} at line {line_number}") from exc
        if not isinstance(record, dict):
            raise ValueError(f"Expected an object in {path} at line {line_number}")
        published_at = record.get("published_at")
        if isinstance(published_at, str):
            record["published_at"] = dt.datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        signals.append(Signal(**{key: value for key, value in record.items() if key in signal_fields}))
    return signals


def _expanded_collection_track(track: dict, factor: int) -> dict:
    """Widen source windows for an official retry without changing the track file."""
    expanded = deepcopy(track)
    collection = expanded.get("collection") or {}
    max_days = int(collection.get("max_days", 180) or 180)

    def widen(value: object) -> object:
        try:
            return min(max_days, max(1, int(value or 1) * factor))
        except (TypeError, ValueError):
            return value

    for key in ("days", "weekly_days", "rss_days", "github_days", "blogrxiv_days"):
        if key in expanded:
            expanded[key] = widen(expanded[key])
    for key in ("xiaohongshu", "zhihu", "twitter", "reddit"):
        config = expanded.get(key)
        if isinstance(config, dict) and "days" in config:
            config["days"] = widen(config["days"])
    return expanded


def _missing_minimums(signals: list[Signal], track: dict) -> dict[str, int]:
    """Return configured per-section deficits after deterministic quality filtering."""
    minimum = track.get("minimum_output") or {}
    if not isinstance(minimum, dict):
        return {}
    counts: dict[str, int] = {}
    for signal in signals:
        counts[signal.type] = counts.get(signal.type, 0) + 1
    missing: dict[str, int] = {}
    for signal_type, target in minimum.items():
        try:
            target_count = max(0, int(target or 0))
        except (TypeError, ValueError):
            continue
        if target_count > counts.get(signal_type, 0):
            missing[signal_type] = target_count - counts.get(signal_type, 0)
    return missing


def _collect_and_shortlist(track: dict, track_name: str, store: SignalStore | None):
    """Collect and quality-filter, widening official source windows if needed."""
    collection = track.get("collection") or {}
    factors = collection.get("retry_factors", []) if isinstance(collection, dict) else []
    try:
        retry_factors = [int(value) for value in factors if int(value) > 1]
    except (TypeError, ValueError):
        retry_factors = []

    attempts = [1, *retry_factors]
    last_result = None
    for attempt, factor in enumerate(attempts):
        attempt_track = track if factor == 1 else _expanded_collection_track(track, factor)
        if factor != 1:
            print(f"Quantity guard: retrying with source windows x{factor}")
        signals = Collector().collect(attempt_track)
        if not signals:
            if last_result is None:
                raise RuntimeError(
                    "No signals were collected. Existing reports were left untouched; "
                    "check network access and source credentials before retrying."
                )
            continue

        from .watchlist import match_watchlist
        watchlist = match_watchlist(signals, track)
        if watchlist:
            print(f"Author watchlist: {len(watchlist)} papers from named authors")

        ranked = curator.rank(signals, track)
        print(f"{len(ranked)} matched keywords")
        if store is not None:
            fresh = store.filter_unseen(ranked, track_name)
            print(f"Memory: filtered {len(ranked) - len(fresh)} already-reported, {len(fresh)} fresh")
            ranked = fresh

        distilled = quality.distill_quality(ranked, track)
        print(f"Quality distill: kept {len(distilled)}/{len(ranked)} candidates")
        missing = _missing_minimums(distilled, track)
        last_result = (signals, watchlist, ranked, distilled)
        if not missing:
            return last_result
        print("Quantity guard: missing " + ", ".join(f"{count} {typ}" for typ, count in missing.items()))

    if last_result is not None:
        missing = _missing_minimums(last_result[3], track)
        if missing:
            print(
                "::warning::High-quality source items remain below the configured minimum: "
                + ", ".join(f"{count} {typ}" for typ, count in missing.items())
            )
        return last_result
    raise RuntimeError(
        "No signals were collected. Existing reports were left untouched; "
        "check network access and source credentials before retrying."
    )


def run_pipeline(track_name: str = DEFAULT_TRACK, no_llm: bool = False, no_memory: bool = False,
                 weekly: bool = False, days: int | None = None) -> Path:
    """Run the radar for one track and write the report. Returns its path.

    Weekly mode widens the window and uses an independent memory scope from the
    daily report, so weekly issues do not repeat one another without suppressing
    items from the daily report."""
    load_dotenv(ROOT / ".env")
    track = {**load_track(track_name), "_reference": track_name}
    if weekly:
        track = {**track, "days": track.get("weekly_days", 7)}
    if days is not None:
        if days <= 0:
            raise ValueError("days must be a positive integer")
        track = {**track, "days": days}
    period = "Weekly" if weekly else "Daily"
    template = "weekly_report.md.j2" if weekly else "daily_report.md.j2"
    prefix = "weekly-" if weekly else ""
    memory_scope = f"{track_name}::weekly" if weekly else track_name
    store = None if no_memory else SignalStore(DB_PATH)

    print(f"Loading track: {track['name']} ({period.lower()})")
    signals, watchlist, ranked, distilled = _collect_and_shortlist(track, memory_scope, store)
    if store is not None and not distilled:
        raise RuntimeError(
            f"No new high-quality signals for {period.lower()} track {track_name}; "
            "existing reports were left untouched."
        )
    ranked = distilled

    analyst = curator.make_analyst(track, enabled=not no_llm)
    sections, candidate_sections = curator.select_sections_with_candidates(ranked, track, analyst)
    final = [s for items in sections.values() for s in items]
    print("Selected " + ", ".join(f"{len(v)} {t}" for t, v in sections.items()))

    if track.get("enrich_openalex", True):
        from .enrich import (
            enrich_arxiv_pdf_affiliations,
            enrich_author_stats,
            enrich_coauthorship,
            enrich_openalex,
            enrich_semantic_scholar,
        )
        n = enrich_openalex(final)
        print(f"OpenAlex: enriched {n} papers (citations/affiliations/author ids)")
        if track.get("graphs", True):
            pdf_affiliations = 0
            paper_quota = int(track.get("output", {}).get("top_papers", 0) or 0)
            graph_author_limit = int(track.get("graph_author_enrichment_top_papers", paper_quota) or 0)
            graph_author_cap = int(track.get("graph_max_authors_per_paper", 12) or 0)
            graph_timeout = float(track.get("graph_enrichment_timeout_seconds", 90) or 0)
            graph_deadline = time.monotonic() + graph_timeout if graph_timeout > 0 else None
            paper_index = 0
            skipped_graph_enrichment = 0
            for s in final:
                if s.type != "paper":
                    continue
                paper_index += 1
                if graph_deadline is not None and time.monotonic() >= graph_deadline:
                    skipped_graph_enrichment += 1
                    continue
                if s.author_nodes and paper_index <= graph_author_limit:
                    enrich_author_stats(s, max_authors=graph_author_cap)
                    enrich_coauthorship(s, max_authors=graph_author_cap)
                enrich_semantic_scholar(s)  # fill institution/homepage gaps or provide a fallback graph
                if not s.author_nodes or not all(node.get("institutions") for node in s.author_nodes):
                    pdf_affiliations += enrich_arxiv_pdf_affiliations(s)
            if pdf_affiliations:
                print(f"arXiv PDF: assigned {pdf_affiliations} fallback author affiliations")
            if skipped_graph_enrichment:
                print(
                    f"Graph enrichment: skipped {skipped_graph_enrichment} papers "
                    f"after {graph_timeout:.0f}s budget"
                )

    # Potential-scoring pass: rate each item by *leading* signals (so fresh,
    # not-yet-cited work can still surface) and re-order each section by it.
    # Papers use the six-expert content review; repos use star-velocity/maturity;
    # blogs use source authority + substance. Advisory — drops nothing.
    if track.get("review_distill", True):
        from .agents.review_distill import review_blogs, review_papers, review_repos
        from .enrich import enrich_blog_fulltext, enrich_code_repo
        enrich_blog_fulltext(final)
        enrich_code_repo(final)  # inspect linked repos to judge real open source
        np = review_papers(final)
        nr = review_repos(final)
        nb = review_blogs(final)
        print(f"Potential scoring: {np} papers, {nr} repos, {nb} blogs")
        for typ in ("paper", "repo", "blog"):
            items = sections.get(typ)
            if items:
                items.sort(
                    key=lambda s: (
                        adjusted_score(s.review_score or 0.0, s),
                        s.final_score or 0.0,
                    ),
                    reverse=True,
                )

    candidate_sections = curator.merge_candidate_sections(sections, candidate_sections)

    date_str = dt.date.today().isoformat()
    REPORTS_DIR.mkdir(exist_ok=True)
    markdown = editor.render(sections, track, date_str, period=period, template=template, watchlist=watchlist)

    report = Report(track=track, date=date_str, markdown=markdown, sections=sections,
                    reports_dir=REPORTS_DIR, period=period, candidate_sections=candidate_sections)
    print("Publishing:")
    for publisher in build_publishers(track):
        publisher.publish(report)

    export_jsonl(final, report_signals_path(track_name, date_str, weekly=weekly))

    if store is not None:
        store.record(final, date_str, memory_scope)
        store.close()
    return REPORTS_DIR / f"report-{prefix}{date_str}.md"
