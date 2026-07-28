# Customizing your radar

OmniSource should feel like a researcher setting up their own reading desk, not
like editing a backend service. Use three layers:

1. **README**: the 30-second path.
2. **Template**: one copyable YAML file in `examples/tracks/`.
3. **Docs**: field-by-field detail for people who want precision.

The fastest path:

```bash
cp examples/tracks/custom-ai-radar.yaml tracks/builder/my-ai-radar.yaml
uv run omnisource run --track builder/my-ai-radar --no-llm --no-memory --days 7
```

Then edit `tracks/builder/my-ai-radar.yaml`.

Scheduled runs read `omnisource.yaml`:

```yaml
active_tracks:
  - builder/my-ai-radar
```

If a track name appears here, GitHub Actions will generate that track in the
daily and weekly GitHub Issue workflows.

## What users usually customize

| Goal | Field |
|---|---|
| Choose the research direction | `description`, `keywords`, `negative_keywords`, `topics` |
| Choose paper pools | `categories`, `days`, `pool_size` |
| Choose sources | `sources` |
| Follow fixed X/Twitter accounts | `twitter.handles` |
| Search broad X/Twitter topics | `twitter.queries` |
| Follow fixed Xiaohongshu creators | `xiaohongshu.creators` |
| Follow fixed Zhihu users | `zhihu.creators` |
| Watch paper authors by name | `watchlist.authors` |
| Choose blogs | `rss_feeds`, `rss_days` |
| Tune GitHub repos | `github_query`, `github_trending_periods`, `github_fallback_created_days` |
| Choose output size | `output.top_papers`, `output.top_repos`, `output.top_blogs` |
| Choose language | `output.languages` |
| Choose scheduled tracks | `omnisource.yaml` → `active_tracks` |

## Source selection

`sources` is the top-level source switchboard:

```yaml
sources:
  - arxiv
  - hf_papers
  - rss
  - github
  - twitter
  - xiaohongshu
  - zhihu
```

Remove anything the user does not want. For example:

```yaml
# Paper-only radar
sources:
  - arxiv
  - hf_papers
```

```yaml
# Experts-on-X radar
sources:
  - twitter
```

```yaml
# Topic radar with Chinese social sources
sources:
  - arxiv
  - hf_papers
  - xiaohongshu
  - zhihu
```

## Fixed X/Twitter experts

Use `twitter.handles` when the user says "I only want to watch these people":

```yaml
sources:
  - twitter

twitter:
  mode: apify
  apify_actor: danek/twitter-scraper
  tweet_language: en
  query_suffix: "filter:links"
  queries: []
  handles:
    - karpathy
    - swyx
    - ClementDelangue
  max_results: 80
```

This becomes an X search like:

```text
(from:karpathy OR from:swyx OR from:ClementDelangue) filter:links lang:en
```

If both `queries` and `handles` are set, OmniSource fetches both:

- Broad keyword search from `twitter.queries`.
- Exact account search from `twitter.handles`.

Tweets are `type: social`; they usually do not become standalone report entries.
When they link an arXiv paper or GitHub repo, canonicalization folds them into
that paper/repo as source evidence and buzz.

## Fixed Xiaohongshu and Zhihu creators

Use these when the user says "watch these exact Chinese creators". They are
source config inside a normal topic track, not separate tracks:

```yaml
sources:
  - xiaohongshu
  - zhihu

xiaohongshu:
  enabled: true
  backend: opencli
  command: opencli
  timezone: Asia/Shanghai
  days: 30
  max_notes_per_creator: 20
  creators:
    - name: "Creator name"
      profile_url: "https://www.xiaohongshu.com/user/profile/USER_ID"

zhihu:
  enabled: true
  backend: opencli
  command: opencli
  timezone: Asia/Shanghai
  days: 30
  max_items_per_creator: 20
  creators:
    - name: "Zhihu user"
      user: "USER_NAME"
      profile_url: "https://www.zhihu.com/people/USER_NAME"
      articles: true
      answers: true
```

Both sources use the track's shared `keywords` to filter posts into the same
paper/repo/blog/social report. They require a persistent OpenCLI browser session;
if OpenCLI is unavailable, the collector skips that source and continues.

## Track versus source

A **track** is the user's taste:

- topic
- keywords
- arXiv categories
- X handles
- RSS feeds
- ranking weights
- output language and size

A **source** is a connector:

- arXiv
- Hugging Face papers
- RSS
- GitHub
- Hacker News
- Reddit
- Twitter/X
- Xiaohongshu
- Zhihu

Good product wording: "Create a track" means "save my preferences". "Enable a
source" means "use this connector inside the track".

## Recommended presets

### AI infrastructure

```yaml
categories: [cs.DC, cs.OS, cs.PL, cs.AR, cs.LG, cs.AI]
keywords:
  - LLM serving
  - distributed training
  - GPU inference
  - CUDA
  - compiler
  - KV cache
twitter:
  handles: [vllm_project, lmsysorg, PyTorch, NVIDIAAI, HuggingFace]
```

### AI algorithms

```yaml
categories: [cs.AI, cs.LG, cs.CL, cs.CV]
keywords:
  - foundation model
  - reasoning
  - reinforcement learning
  - multimodal
  - post-training
twitter:
  handles: [karpathy, fchollet, ylecun, hardmaru, lilianweng]
```

### Only a few experts on X

```yaml
sources: [twitter]
twitter:
  mode: apify
  apify_actor: danek/twitter-scraper
  query_suffix: "filter:links"
  queries: []
  handles:
    - karpathy
    - fchollet
    - swyx
  max_results: 80
```

## Validation loop

1. Run without LLM first:

   ```bash
   uv run omnisource run --track builder/my-ai-radar --no-llm --no-memory --days 7
   ```

2. Check whether the raw pool is on-topic.

3. Add LLM once the pool is reasonable:

   ```bash
   uv run omnisource run --track builder/my-ai-radar --no-memory
   ```

4. Inspect the generated Markdown or GitHub Issue. If the result is too broad,
   tighten `keywords`, add `negative_keywords`, narrow `categories`, or reduce
   the source lookback window. If it is too sparse, widen the keywords or add a
   relevant RSS/GitHub source.

## Where to get help

For the public package, configuration is intentionally file-based: edit the
track YAML, run it locally, and then let GitHub Actions publish the Issue. The
official website's visual Settings and subscription features are separate and
are not required for DIY reports.
