# CS Paper Distiller

The CS Paper Distiller is an experimental long-horizon feature for building a
curated CS paper canon. It follows the review architecture in
`omnisource_humanreview/cs_multi_agent_paper_distiller_architecture.md`, while
keeping the implementation isolated from the daily radar pipeline.

## What It Adds

- Fixed taxonomy: `omnisource/taxonomies/cs_foundation_v1.yaml` defines 30 CS
  leaves, each with a three-level path, arXiv categories, adjacent fields,
  venue IDs, and routing keywords.
- Expert skills: `omnisource/expert_skills/cs_foundation_v1/*.md` provides one
  concise domain-expert prompt per taxonomy leaf.
- Multi-agent harness: each paper gets six deterministic reviewer subagents:
  three small peers, two adjacent big peers, and one reproducible random big
  peer.
- Hub decision: `HubAgent` combines five primary dimensions with citation,
  Hugging Face upvote, and GitHub star supplements, then applies age decay,
  classic-paper override, red-flag consensus, dispersion, and young-breakthrough
  rescue rules.
- Full-text signals: the MVP extracts figure/table/formula/section counts from
  available full text and uses them in presentation and workload scoring.

## Commands

Offline calibration run:

```bash
uv run omnisource distill-cs --dry-run --max-candidates 3
```

Live arXiv-backed run:

```bash
uv run omnisource distill-cs --years 15 --max-candidates 60
```

Offline candidate JSONL run:

```bash
uv run omnisource distill-cs --input-jsonl candidates.jsonl --max-candidates 100
```

Candidate JSONL records should contain at least:

```json
{"paper_id":"arxiv:1706.03762","title":"Attention Is All You Need","abstract":"...","authors":["..."],"published_at":"2017-06-12T00:00:00+00:00","primary_leaf":"ai.nlp_speech","arxiv_id":"1706.03762","full_text":"optional extracted text"}
```

## Outputs

The default output directory is `reports/cs-distiller/`:

- `cs-foundation-v1-YYYY-MM-DD.summary.md`
- `cs-foundation-v1-YYYY-MM-DD.decisions.jsonl`
- `cs-foundation-v1-YYYY-MM-DD.reviewer_traces.jsonl`

Each decision records the canonical paper ID, primary leaf, reviewer mean scores,
supplemental scores, age-adjusted score, decision, reason, and audit trail.

## Current MVP Boundaries

- The default reviewer is deterministic and rule-based so the harness can run
  without an LLM key. The `ReviewerSpec` and `ExpertReview` contracts are ready
  for a future LLM-backed reviewer.
- PDF parsing is best-effort. The core MVP uses available full text; live PDF
  extraction requires an optional PDF parser such as `pypdf`.
- Venue proceedings and metadata enrichers are implemented as adapters, but
  broad live 15-year crawls should be run with conservative limits and cached
  before CI use.
- README keeps this feature under TODO because taxonomy coverage, venue mapping,
  calibration sets, human-review UI, and long-run cost controls need contributor
  iteration.
