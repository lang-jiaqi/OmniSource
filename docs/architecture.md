# Architecture

OmniSource is a small, pluggable pipeline. Every stage operates on one unified
type — `Signal` — so no stage needs to know where an item came from or where it's
going.

```
Collector(fetch + dedup) → Curator(keyword + feedback filter/rank) → memory filter
                         → Quality(distill) → Analyst(LLM) → Editor(group + render)
                         → Publishers
```

## The pieces

Five agents, run in order, each in its own module under [`agents/`](../omnisource/agents):

| Agent | Where | What it does |
|---|---|---|
| Collector | [`agents/collector.py`](../omnisource/agents/collector.py) | fetch from every source the track lists, then dedup by `id` |
| Curator | [`agents/curator.py`](../omnisource/agents/curator.py) | keyword filter, rank, select top per type, score |
| Quality | [`agents/quality.py`](../omnisource/agents/quality.py) | deterministic quality distill: score matched `Signal`s and keep a per-section buffer before the LLM |
| Analyst | [`agents/analyst.py`](../omnisource/agents/analyst.py) | LLM judges relevance + novelty, explains why it matters, tags a taxonomy leaf |
| Editor | [`agents/editor.py`](../omnisource/agents/editor.py) | group by taxonomy leaf and render markdown via Jinja templates |

Supporting modules:

| Concern | Where | What it does |
|---|---|---|
| Unified item | [`models.py`](../omnisource/models.py) | `Signal` — the one shape everything speaks |
| Sources | [`sources/`](../omnisource/sources) | turn a feed into `Signal`s (`fetch(track) -> list[Signal]`) |
| Memory | [`memory/`](../omnisource/memory) | remember reported items so they don't repeat; cache HTTP fetches |
| Personalization | [`personalization.py`](../omnisource/personalization.py) | exact ignores, bounded like/similar adjustments, and followed-author boosts from owner feedback |
| Scoring | [`ranking/`](../omnisource/ranking) | weighted final score from the components |
| Config | [`config.py`](../omnisource/config.py) | central paths and tunables |
| Orchestration | [`main.py`](../omnisource/main.py) | wires the agents together; `run_pipeline()` |
| CLI | [`cli.py`](../omnisource/cli.py) | `omnisource run` / `weekly` / `tracks` |

## Signal

The contract between every stage. Sources fill in the upstream fields; the
quality distill fills `quality_score`; the analyst fills `llm_relevance` /
`novelty` / `why_it_matters`; ranking fills `final_score`. A flat dataclass —
see [`models.py`](../omnisource/models.py).

## Ranking

Relevance from the LLM saturates near 1.0 for on-topic items, so the final order
comes from a weighted blend of four components — relevance, novelty, popularity
(normalized within a section), and code availability. Tracks set the weights
under `ranking:`; defaults live in [`ranking/scoring.py`](../omnisource/ranking/scoring.py).

Tracks may also define `relevance_filter:` as a deterministic guardrail before
the LLM. It can boost preferred arXiv categories (for example `cs.DC` for AI
infrastructure) and require anchor keywords when broad categories such as
`cs.AI` / `cs.LG` would otherwise pull in adjacent but off-track papers.

## Sections And Topics

Papers have long abstracts and would crowd out repos and blogs in a single
ranked list, so selection is per type with quotas (`top_papers` / `top_repos` /
`top_blogs`) and the report is grouped into sections.

Within a track, `topics:` can be either a flat list or a 2-3 level tree. The
daily LLM classifier receives the leaf paths and writes one path back to
`Signal.topic`, for example `Systems > Inference > KV cache`. Markdown and Pages
then group cards by that full leaf path.

## Publishing

Publishers ([`publishers/`](../omnisource/publishers)) mirror sources: each takes
the finished `Report` and delivers it somewhere. A track's `publishers:` list
chooses which run; the public default is `markdown` + `github_issue`. The
official website has a separate private Pages adapter.
(`github_issue` skips off-CI). See [adding-a-publisher.md](adding-a-publisher.md).
