# Reddit source

Reddit supports two backends. `opencli` is the default for local runs and
reuses the browser session connected to OpenCLI. `oauth` uses Reddit's official
application-only API and is suitable for headless CI.

Reddit signals use `type: social`. Posts that link to an arXiv paper, GitHub
repository, Hugging Face paper, or DOI are canonicalized and folded into that
artifact as community evidence.

## Mode `opencli` (default)

OpenCLI provides two independent collection paths:

- `search.queries` calls `opencli reddit search` for keyword discovery.
- `subreddits.names` calls `opencli reddit subreddit` for fixed communities
  such as `r/Codex` and `r/ClaudeAI`.

```yaml
sources:
  - reddit

reddit:
  mode: opencli
  timeout: 180
  max_results: 150
  search:
    enabled: true
    sort: new
    time: week
    max_results_per_query: 30
    queries:
      - "Codex"
      - "Claude Code"
      - "LLM agents"
  subreddits:
    enabled: true
    sort: new
    time: week
    max_results_per_subreddit: 30
    names:
      - "Codex"
      - "ClaudeAI"
      - "MachineLearning"
      - "LocalLLaMA"
```

Subreddit names may be written as either `Codex` or `r/Codex`; OmniSource
normalizes the prefix before invoking OpenCLI. Search supports Reddit's
`relevance`, `hot`, `top`, `new`, and `comments` sort orders. Fixed subreddit
feeds support `hot`, `new`, `top`, `rising`, and `controversial`.

Verify the local setup with:

On macOS, if the managed `opencli` launcher reports `Unable to find
application named 'OpenCLIApp'`, use the bundled-runtime fallback and
`OPENCLI_COMMAND` setting shown in the [README](../README.md). On Windows,
keep using `opencli` when `opencli doctor` reports a running daemon and a
connected extension.

```bash
opencli doctor
opencli reddit search "Claude Code" --sort new --time week --limit 5 -f json
opencli reddit subreddit Codex --sort new --limit 5 -f json
```

The source preserves post score, comment count, subreddit, self-text, external
link, and media metadata. Results from search and fixed communities are
deduplicated by Reddit permalink and filtered to the track's `days` window.

## Mode `oauth` (headless CI)

Register a Reddit application and set `REDDIT_CLIENT_ID` and
`REDDIT_CLIENT_SECRET`, then configure:

```yaml
reddit:
  mode: oauth
  max_results: 50

reddit_subreddits:
  - MachineLearning
  - LocalLLaMA
```

Without credentials the OAuth backend skips cleanly. Legacy tracks containing
only `reddit_subreddits` / `reddit_top` remain compatible and now use OpenCLI by
default; set `reddit.mode: oauth` to retain the previous API behavior.
