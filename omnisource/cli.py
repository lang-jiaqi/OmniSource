"""`omnisource` command-line interface."""
from __future__ import annotations

from pathlib import Path

import typer

from .config import DEFAULT_TRACK, track_references
from .main import run_pipeline

app = typer.Typer(help="OmniSource — your self-hosted AI research radar.", no_args_is_help=True)


@app.command()
def run(
    track: str = typer.Option(DEFAULT_TRACK, help="Track path under tracks/<audience>/ (bare names remain supported)."),
    no_llm: bool = typer.Option(False, "--no-llm", help="Skip the LLM analyst step."),
    no_memory: bool = typer.Option(False, "--no-memory", help="Don't filter or record already-reported signals."),
    days: int | None = typer.Option(None, "--days", min=1, help="Override the source lookback window in days."),
) -> None:
    """Generate today's briefing for a track."""
    run_pipeline(track, no_llm=no_llm, no_memory=no_memory, days=days)


@app.command()
def weekly(
    track: str = typer.Option(DEFAULT_TRACK, help="Track path under tracks/<audience>/ (bare names remain supported)."),
    no_llm: bool = typer.Option(False, "--no-llm", help="Skip the LLM analyst step."),
    days: int | None = typer.Option(None, "--days", min=1, help="Override the weekly lookback window in days."),
) -> None:
    """Generate a weekly digest with cross-week deduplication."""
    run_pipeline(track, no_llm=no_llm, weekly=True, days=days)


@app.command()
def tracks() -> None:
    """List the available tracks."""
    for reference in track_references():
        typer.echo(reference)


@app.command("active-tracks")
def active_tracks_cmd() -> None:
    """List tracks enabled in omnisource.yaml, one per line."""
    from .app_config import active_tracks

    for track in active_tracks(validate=True):
        typer.echo(track)


@app.command("summarize-feedback")
def summarize_feedback_cmd(
    events: Path | None = typer.Option(None, help="Raw feedback JSONL; defaults to data/feedback_events.jsonl."),
    output: Path | None = typer.Option(None, help="Preference summary markdown; defaults to data/preference_summary.md."),
    max_preferences: int = typer.Option(20, min=1, max=50, help="Maximum preference bullets to keep."),
) -> None:
    """Compact raw recommendation feedback into prompt-ready preferences."""
    from .prompt_feedback import (
        FEEDBACK_EVENTS_PATH,
        PREFERENCE_SUMMARY_PATH,
        write_preference_summary,
    )

    target, event_count, preference_count = write_preference_summary(
        event_path=events or FEEDBACK_EVENTS_PATH,
        output_path=output or PREFERENCE_SUMMARY_PATH,
        max_preferences=max_preferences,
    )
    typer.echo(f"events with reasons: {event_count}")
    typer.echo(f"preference bullets: {preference_count}")
    typer.echo(f"summary: {target}")


@app.command("feedback")
def feedback_cmd(
    action: str = typer.Option(..., help="like | ignore | lower-similar | follow-author"),
    track: str = typer.Option(..., help="Track reference, for example builder/ai-infra."),
    item_id: str = typer.Option("", help="Canonical report item id."),
    item_type: str = typer.Option("item", help="paper | repo | blog | social | item"),
    title: str = typer.Option("", help="Item title, used to identify similar future items."),
    url: str = typer.Option("", help="Original item URL."),
    topic: str = typer.Option("", help="Taxonomy topic from the report."),
    authors: str = typer.Option("", help="Comma-separated item authors."),
    keywords: str = typer.Option("", help="Comma-separated matching track keywords."),
    author: str = typer.Option("", help="Author to follow; required for follow-author."),
    reason: str = typer.Option("", help="Optional explanation for the learned preference."),
    events: Path | None = typer.Option(None, help="Feedback JSONL; defaults to data/feedback_events.jsonl."),
) -> None:
    """Record a local personalization action for future reports."""
    from .prompt_feedback import record_feedback_event, write_preference_summary

    target = record_feedback_event(
        action=action,
        track=track,
        item_id=item_id,
        item_type=item_type,
        title=title,
        url=url,
        topic=topic,
        authors=[item.strip() for item in authors.split(",") if item.strip()],
        keywords=[item.strip() for item in keywords.split(",") if item.strip()],
        target_author=author,
        reason=reason,
        path=events,
    )
    summary, event_count, preference_count = write_preference_summary(event_path=target)
    typer.echo(f"feedback: {target}")
    typer.echo(f"events: {event_count}; learned preferences: {preference_count}")
    typer.echo(f"summary: {summary}")


@app.command("import-feedback-issues")
def import_feedback_issues_cmd(
    issues: Path = typer.Option(..., exists=True, dir_okay=False, help="JSON produced by gh issue list."),
    owner: str = typer.Option(..., envvar="GITHUB_REPOSITORY_OWNER", help="Only import feedback authored by this owner."),
    output: Path | None = typer.Option(None, help="Feedback JSONL; defaults to data/feedback_events.jsonl."),
) -> None:
    """Import structured owner feedback from GitHub Issues."""
    from .prompt_feedback import FEEDBACK_EVENTS_PATH
    from .repository_feedback import import_feedback_issues

    target, issue_count, event_count = import_feedback_issues(
        issue_path=issues,
        owner=owner,
        output_path=output or FEEDBACK_EVENTS_PATH,
    )
    typer.echo(f"issues scanned: {issue_count}")
    typer.echo(f"owner feedback events: {event_count}")
    typer.echo(f"events: {target}")


@app.command("distill-cs")
def distill_cs(
    taxonomy: str = typer.Option("cs-foundation-v1", help="Fixed CS taxonomy name."),
    years: int = typer.Option(15, help="How many publication years to consider."),
    max_candidates: int = typer.Option(30, help="Maximum candidates to review in this run."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Use built-in calibration candidates without network calls."),
    input_jsonl: Path | None = typer.Option(None, help="Optional candidate JSONL file for offline distillation."),
    output_dir: Path | None = typer.Option(None, help="Output directory; defaults to reports/cs-distiller."),
    include_venues: bool = typer.Option(True, "--include-venues/--no-include-venues", help="Include top-conference source adapters during live runs."),
    fetch_pdf_text: bool = typer.Option(False, "--fetch-pdf-text/--no-fetch-pdf-text", help="Best-effort PDF/full-text extraction for presentation review."),
    enrich_metadata: bool | None = typer.Option(None, "--enrich-metadata/--no-enrich-metadata", help="Enable citation/HF/GitHub enrichment; defaults on for live runs and off for dry-run."),
    reviewer: str = typer.Option("rule", help="Reviewer backend: rule | llm."),
    reviewer_provider: str = typer.Option("openai", help="LLM provider for reviewer (openai | anthropic | local)."),
    reviewer_model: str | None = typer.Option(None, help="LLM model for the reviewer."),
    reviewer_full_text: str = typer.Option("never", help="Send full text to the reviewer: never | always."),
) -> None:
    """Run the experimental CS Paper Distiller."""
    from .distiller.pipeline import load_candidates_jsonl, run_distiller

    candidates = load_candidates_jsonl(input_jsonl) if input_jsonl else None
    result = run_distiller(
        taxonomy_name=taxonomy,
        years=years,
        dry_run=dry_run,
        max_candidates=max_candidates,
        output_dir=output_dir,
        candidates=candidates,
        include_venues=include_venues,
        fetch_pdf_text=fetch_pdf_text,
        enrich_metadata=enrich_metadata,
        reviewer_backend=reviewer,
        reviewer_provider=reviewer_provider,
        reviewer_model=reviewer_model,
        reviewer_full_text=reviewer_full_text,
    )
    typer.echo(f"summary: {result.summary_path}")
    typer.echo(f"decisions: {result.decisions_path}")
    typer.echo(f"reviewer traces: {result.reviewer_traces_path}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
