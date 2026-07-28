# BlogrXiv source

OmniSource can read BlogrXiv's curated AI research-writing index through its
public published-blog catalogue. It does not require a login or a local
browser session.

The source discovers BlogrXiv's public frontend data configuration at runtime,
requests only rows marked `published`, and applies the track's
`blogrxiv_days` lookback window. The default tracks use a one-day
Asia/Shanghai calendar window so each daily report sees that day's updates
only. The article's category and tags are retained in
the signal summary so ranking and the LLM analyst can use the editorial
context.

The default `research/ai-algorithm` and `builder/ai-infra` tracks include `blogrxiv` alongside
RSS. To disable it for a custom track, omit `blogrxiv` from `sources`.

The source uses the original article URL as its signal id, so an article that
links to an arXiv paper or GitHub repository can still fold into that artifact
through OmniSource's normal canonicalization and deduplication.
