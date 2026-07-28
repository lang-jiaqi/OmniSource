# Twitter / X source

Twitter has no free, clean, automatable read API, so — like other mature radars —
OmniSource offers three backends. The recommended backend for GitHub Actions is
`apify`; it only needs `APIFY_TOKEN` and does not need OpenCLI. The public
`ai-infra` track contains an Apify configuration example, but Twitter remains
opt-in: it runs only when the track lists `twitter` under `sources:` and provides
a `twitter:` block.

Twitter signals are `type: social`. On their own they don't appear in the report;
they become useful via canonicalization (`omnisource/canonical.py`), which folds a
tweet onto the arXiv paper / GitHub repo it links — turning social into **buzz** on
the real item rather than separate noise.

`queries` and `handles` work together:

- `queries` search broad topic keywords, such as "LLM serving" or "reasoning model".
- `handles` seed high-signal accounts, such as AI researchers, labs, or project teams.

This does **not** mean OmniSource only crawls accounts you personally follow. The
handles are just curated seeds to make the first results less noisy; keyword
search still brings in broader Twitter/X discussion.

If you **do** want only fixed experts' posts, leave `queries` empty and fill
`handles`:

```yaml
sources:
  - twitter
twitter:
  mode: apify
  apify_actor: "danek/twitter-scraper"
  query_suffix: "filter:links"
  queries: []
  handles: ["karpathy", "fchollet", "swyx"]
  max_results: 80
```

That becomes an X search like:

```text
(from:karpathy OR from:fchollet OR from:swyx) filter:links
```

## Mode `opencli` (recommended for local runs)

This mode reuses the X login in your Chrome profile through
[`OpenCLI`](https://github.com/jackwener/OpenCLI). It supports two independent
inputs: keyword search and the recent timelines of fixed accounts.

```yaml
sources:
  - twitter
twitter:
  mode: opencli
  profile: work
  max_results: 150
  search:
    enabled: true
    queries: ["LLM serving", "reasoning model"]
    product: live
    language: en
    has: links
    exclude_replies: true
    exclude_retweets: true
    max_results_per_query: 30
  accounts:
    enabled: true
    handles: ["karpathy", "fchollet", "OpenAI"]
    max_results_per_handle: 30
    page_delay: 2
    include_retweets: false
```

Install OpenCLI, its Browser Bridge extension, and log into x.com in Chrome.
Then verify both paths before running OmniSource:

On macOS, if the managed `opencli` launcher reports `Unable to find
application named 'OpenCLIApp'`, use the bundled-runtime fallback and
`OPENCLI_COMMAND` setting shown in the [README](../README.md). On Windows,
keep using `opencli` when `opencli doctor` reports a running daemon and a
connected extension.

```bash
opencli doctor
opencli twitter search '"LLM serving"' --product live --limit 5 -f json
opencli twitter tweets karpathy --limit 5 -f json
```

`profile` is optional and maps to `OPENCLI_PROFILE`. This mode requires a live,
logged-in browser session, so use `apify` on hosted CI. For compatibility,
top-level `queries` and `handles` are also accepted in `opencli` mode; new
configurations should prefer the explicit `search` and `accounts` blocks.

## Mode `apify` (default — safe for CI)

A paid third-party scraper. Your X account is never used, so it can run in CI.

```yaml
sources:
  - arxiv
  - twitter
twitter:
  mode: apify
  apify_actor: "danek/twitter-scraper"
  queries: ["llm agent", "tool use"]
  handles: ["AnthropicAI", "OpenAI"]
  tweet_language: en
  query_suffix: "filter:links"
  max_results: 50
```

Set `APIFY_TOKEN` (env / `.env` / GitHub secret). Without it the source skips.
OmniSource converts `queries` / `handles` into the actor's `query` input and
uses `max_results` as its tweet cap.

## Mode `local` (free — local only, NOT for CI)

Shells out to [`twitter-cli`](https://pypi.org/project/twitter-cli/), which uses
**your exported x.com cookies**. Free, but against X's ToS — **use a throwaway
account**, and never put cookies in CI.

```yaml
twitter:
  mode: local
  queries: ["llm agent benchmark"]
  max_results: 30
```

```bash
pipx install twitter-cli   # then configure cookies per twitter-cli docs
```

If `twitter-cli` isn't installed, the source skips. Keep this for local runs.

> Why two tiers: there is no free + clean + CI-safe path for Twitter. Pay a
> third-party (your account safe, CI-able) or ride your own cookie (free, risky).
