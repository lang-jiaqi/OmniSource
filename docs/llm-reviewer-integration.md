# Swapping the rule-based reviewer for an LLM reviewer

The CS Paper Distiller's decision architecture (6-reviewer panel → HubAgent with
age decay, classic override, dispersion → human review, young-breakthrough
rescue, red-flag consensus) is solid. The weak part is the *signal* it runs on:
`RuleBasedReviewer` just counts keywords/terms in the abstract. This note shows
how to drop in an LLM reviewer **without touching that architecture**, and how to
keep token cost low from day one.

## The swap point (one contract, one line)

A reviewer is anything with:

```python
def review(self, candidate: PaperCandidate, spec: ReviewerSpec) -> ExpertReview: ...
```

In [`pipeline.py`](../omnisource/distiller/pipeline.py):

```python
reviewer = RuleBasedReviewer(taxonomy, skills)   # line 70 today
reviews  = [reviewer.review(candidate, spec) for spec in specs]   # line 88
```

Make line 70 pick by config:

```python
backend = (track_cfg or {}).get("reviewer", {}).get("backend", "rule")
reviewer = (LLMReviewer(taxonomy, skills, cfg) if backend == "llm"
            else RuleBasedReviewer(taxonomy, skills))
```

Everything downstream (`HubAgent.decide`, audit traces, outputs) is unchanged.

## What the LLM reviewer must produce

`ExpertReview` fields the hub consumes:

| field | meaning |
|---|---|
| `scores: ReviewScores` | the 5 dims, each 0..1 |
| `confidence` | 0..1 |
| `red_flags: list[str]` | e.g. `no_strong_baseline`, `overclaiming`, `data_leakage` |
| `must_keep_signal` | strong-accept hint |
| `must_filter_signal` | strong-reject hint |
| `rationale` | one line (audit) |

The 5 `ReviewScores` dims (and `main_quality` weights): `novelty` (.28),
`insight_contribution` (.24), `workload` (.18), `open_source_completeness` (.18),
`paper_presentation` (.12).

## Mapping the AI-Scientist rubric onto these dims

Use the AI-Scientist reviewer prompt (critical/cautious persona + NeurIPS form)
but ask it to emit the distiller's fields:

| AI-Scientist field | → distiller |
|---|---|
| Originality | `novelty` |
| Soundness + Quality | `workload` (technical depth/rigor) |
| Significance + Contribution | `insight_contribution` |
| Clarity + Presentation | `paper_presentation` |
| (reproducibility / artifacts) | `open_source_completeness` (LLM judgment + has-code metadata) |
| Weaknesses → tagged | `red_flags` |
| Overall ≥ 8 | `must_keep_signal = true` |
| Decision == Reject & Overall ≤ 4 | `must_filter_signal = true` |
| Confidence (1–5) | `confidence` (÷5) |

The per-leaf expert persona (`skills[spec.leaf_id].prompt`) becomes the system
prompt prefix, plus the `spec.lens` / `spec.relationship` framing the rule
reviewer already encodes (evidence / reproducibility / outside-field reviewer).

## Cost-aware design (build it cheap from the start)

The naive cost is `6 reviewers × full-text × #papers × model price`. Keep all
four multipliers small:

1. **Funnel first.** Keep the free rule-based prefilter (`agents/quality.py` +
   `RuleBasedReviewer` as a stage-0 screen). Only candidates that pass reach the
   LLM panel. The LLM never sees the long tail.
2. **Abstract by default, full-text only for finalists.** Most reviews run on
   title+abstract (~1k tokens). Send full text only for borderline papers near
   the keep threshold, or to 1–2 reviewers, not all 6.
3. **Cheap / local model.** The rubric is structured — a small model (gpt-4o-mini
   / Haiku / DeepSeek) is enough. The distiller is **offline**, so a **local
   model (Ollama) costs $0** and latency doesn't matter. Reuse `omnisource/llm/`.
4. **Batch + cache.** Offline → use the provider Batch API (~50% off). Cache each
   `ExpertReview` by `(paper_id, leaf_id, lens, model, harness_version)` so
   re-runs and overlapping panels never re-pay.

Rough cost with mini + full-text on every review: ~$0.01/paper (60 papers ≈
$0.7). With abstract-screen-then-finalists-only, or a local model: near zero.
The daily radar is unaffected — `agents/quality.py` stays rule-based and free.

## Suggested config

```yaml
# distiller reviewer config
reviewer:
  backend: llm            # rule | llm
  provider: local         # openai | anthropic | local | openai_compatible
  model: llama3.1
  full_text: finalists    # never | finalists | always
  batch: true
  cache: true
```

## LLMReviewer skeleton

```python
# omnisource/distiller/llm_reviewer.py
from ..llm import get_provider
from ..llm.base import parse_json
from .models import ExpertReview, ReviewScores, clamp01

class LLMReviewer:
    def __init__(self, taxonomy, skills, cfg):
        self.taxonomy, self.skills = taxonomy, skills
        self.provider = get_provider(cfg.get("provider", "local"), cfg.get("model"))
        self.full_text_mode = cfg.get("full_text", "finalists")

    def review(self, candidate, spec):
        persona = self.skills[spec.leaf_id].prompt
        system = persona + "\n" + AISCIENTIST_CRITICAL_PROMPT + DISTILLER_JSON_SPEC
        body = candidate.text_for_review()  # gate full text by self.full_text_mode
        data = parse_json(self.provider.complete_json(system, body))
        return ExpertReview(
            reviewer_id=spec.reviewer_id, skill_leaf=spec.leaf_id,
            lens=spec.lens, relationship=spec.relationship,
            scores=ReviewScores(
                novelty=clamp01(data["novelty"]),
                workload=clamp01(data["workload"]),
                open_source_completeness=clamp01(data["open_source"]),
                insight_contribution=clamp01(data["insight"]),
                paper_presentation=clamp01(data["presentation"]),
            ),
            confidence=clamp01(data.get("confidence", 0.6)),
            rationale=data.get("rationale", ""),
            red_flags=data.get("red_flags", []),
            must_keep_signal=bool(data.get("must_keep")),
            must_filter_signal=bool(data.get("must_filter")),
        )
```

## Division of labor

- **Distiller owner**: wire the `backend` switch in `pipeline.py`; add the cache
  keyed by `(paper_id, leaf_id, lens, model, harness_version)`; the finalists
  full-text gate.
- **Reviewer prompt**: port the AI-Scientist critical rubric + per-leaf persona
  into `AISCIENTIST_CRITICAL_PROMPT` / `DISTILLER_JSON_SPEC`, and calibrate
  stinginess against a small labeled set (reuse `taxonomies/classic_papers.yaml`
  as positive anchors).
