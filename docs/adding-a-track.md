# Adding a track

A track is a YAML file describing one research direction. A good track is one
researcher's reading taste.

For most users, start from the copyable template:

```bash
cp examples/tracks/custom-ai-radar.yaml tracks/builder/my-ai-radar.yaml
uv run omnisource run --track builder/my-ai-radar --no-llm --no-memory --days 7
```

Then edit `tracks/builder/my-ai-radar.yaml`. You can also copy an existing production
track in [`tracks/`](../tracks) if your field is close to one of them.

```yaml
name: my-track
display_name: My Track        # optional UI/report title; name stays the stable id
description: One line — also shown on the site and given to the LLM as context.

sources:            # which sources to pull from (names from SOURCE_REGISTRY)
  - arxiv
  - hf_papers
  - rss
  - github

categories:         # arXiv categories
  - cs.LG
  - cs.AI
days: 3             # arXiv/HF paper lookback window; users can choose 3/5/7...
pool_size: 400      # max arXiv papers to pull before filtering

keywords:           # an item scores 1 per distinct keyword it matches
  - your topic
  - another phrase
negative_keywords:  # any match drops the item
  - off topic

relevance_filter:   # optional deterministic guardrails before the LLM
  paper:
    preferred_arxiv_categories:
      - cs.DC
      - cs.OS
    broad_arxiv_categories:
      - cs.AI
      - cs.LG
    min_anchor_hits: 1
    broad_category_min_anchor_hits: 1
    anchor_keywords:
      - serving
      - distributed training
      - GPU
      - compiler
  blog:
    allow_keyword_fallback: true  # useful for curated feeds with sparse wording

topics:             # 2-3 level taxonomy; reports group by leaf paths
  - name: broad area
    children:
      - name: middle area
        children:
          - narrow leaf one
          - narrow leaf two
  - name: another broad area
    children:
      - another leaf

rss_feeds:          # blogs for the rss source (sparse, so wider window)
  - https://huggingface.co/blog/feed.xml
rss_days: 21

twitter:            # optional; requires APIFY_TOKEN in env / .env / Actions
  mode: apify
  apify_actor: danek/twitter-scraper
  query_suffix: "filter:links"
  queries:
    - "your broad topic"
  handles:
    - karpathy
    - swyx
  max_results: 80

github_query: "your topic OR related"   # Search fallback query (keep operators ≤ 5)
github_trending_periods: ["daily", "weekly"]
github_fallback_created_days: 120       # fallback excludes older known repos
github_days: 14
github_top: 30

llm:
  provider: openai          # openai | anthropic | local | openai_compatible
  model: gpt-4o-mini        # e.g. claude-haiku-4-5, llama3.1, or a gateway model

ranking:            # weights for the final score (optional; these are defaults)
  relevance: 0.4
  novelty: 0.3
  popularity: 0.2
  code_available: 0.1

personalization:    # optional; bounded additions to the normal 0..1 score
  enabled: true
  like_boost: 0.12
  lower_similar_penalty: 0.18
  follow_author_boost: 0.24
  similarity_threshold: 0.25

quality_distill:    # optional cheap pre-LLM shortlist controls
  min_score: 0.18
  buffer: 8
  fill_quota_types:
    - blog

output:
  top_papers: 15
  top_repos: 5
  top_blogs: 5
  language: 中文      # language for the LLM's why_it_matters / key_idea
  languages:          # optional; enables bilingual Pages/Markdown content
    - 中文
    - English
```

Run it: `uv run omnisource run --track builder/my-track`.
Temporarily override the window: `uv run omnisource run --track builder/my-track --days 7`.

Tips:
- `keywords` only pre-filter; the LLM does the real relevance judgment, so a
  generous keyword list is fine.
- Tune `days` per track. Fast-moving or sparse directions can use `5` or `7`;
  manual GitHub Actions runs also expose a `days` input.
- Use `relevance_filter` when a broad source category admits adjacent-but-wrong
  work. `preferred_arxiv_categories` get a ranking boost, while
  `broad_arxiv_categories` can require concrete `anchor_keywords`.
- Use `fill_quota_types` for sparse sections such as curated blogs; it lets the
  quality distill backfill from lower-score candidates instead of returning a
  half-empty section.
- GitHub repos are Trending-first. Trending candidates are filtered against the
  track before enrichment; `github_query` only fills from recently created repos,
  so reports surface new tools instead of familiar incumbents.
- To watch only fixed X/Twitter accounts, set `twitter.queries: []` and fill
  `twitter.handles`. If both `queries` and `handles` are set, OmniSource fetches
  both broad topic search and exact accounts.
- Do not use `--no-llm` when you need complete paper explanations, recommendation reasons,
  and method summaries; it is only useful for inspecting keyword-filter candidates.
- Keep topic leaves specific enough to separate reading queues, but not so fine
  that each leaf gets only one paper. The LLM returns one full leaf path such as
  `broad area > middle area > narrow leaf one`.
- Use `provider: openai_compatible` for a hosted gateway or self-managed API
  that speaks the OpenAI chat completions protocol. Configure
  `OPENAI_COMPATIBLE_API_KEY` and `OPENAI_COMPATIBLE_BASE_URL` in `.env`.
- Set `output.analysis_buffer` to control how many extra candidates are sent to
  the LLM analyst beyond the initial visible quota. GitHub Pages retains this
  buffer for per-browser personalization; use `0` to disable the extra pool or
  `3` to `5` for a modest personalized candidate set.
- Repository-synced feedback is scoped by `track`, so owner feedback from one
  track remains distinguishable when Actions builds the next preference summary.
- Likes and "show fewer" actions generalize through shared track keywords,
  title terms, topic, and authors. Ignore remains exact-item only. Follow-author
  can pass the keyword gate but still respects negative keywords and explicit
  track relevance guardrails.
