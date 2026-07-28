<div align="center">

<h1>🔭 OmniSource</h1>

<p><strong>Don't read everything. Find what matters next.</strong><br>
AI-driven open research intelligence<br>
Turn papers, AI tools, startup signals, and community discussions into reports you can actually scan.</p>

[![License](https://img.shields.io/badge/license-PolyForm%20Noncommercial-8bd3a8.svg?style=for-the-badge)](LICENSE)
[![Built with uv](https://img.shields.io/badge/built%20with-uv-4B275F?style=for-the-badge&logo=uv&logoColor=white)](https://github.com/astral-sh/uv)
[![Python](https://img.shields.io/badge/python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Live demo](https://img.shields.io/badge/Live-demo-7c83ff?style=for-the-badge&logo=githubpages&logoColor=white)](https://lang-jiaqi.github.io/omnisource-site/en/)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=for-the-badge&logo=github&logoColor=white)](../../pulls)

![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white)
![Claude](https://img.shields.io/badge/Claude-D97757?style=flat-square&logo=anthropic&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-000000?style=flat-square&logo=ollama&logoColor=white)
![OpenAI-compatible](https://img.shields.io/badge/+_OpenAI--compatible-555?style=flat-square)

Self-hosted · multi-source · bilingual reports · customizable tracks

[🏠 Official site](https://lang-jiaqi.github.io/omnisource-site/en/) · [📖 Research report](https://lang-jiaqi.github.io/omnisource-site/en/report.html) · [🧰 Official tool radar](https://lang-jiaqi.github.io/omnisource-site/en/tools.html) · [📋 Sample briefing](examples/reports/en/llm-agents.md) · [📚 Docs](docs) · [中文](README.zh-CN.md)

</div>

## Why

Research updates are scattered across arXiv, Hugging Face Daily Papers, lab blogs, GitHub, X/Twitter, Reddit, Zhihu, Xiaohongshu, and more. Checking each place manually works, but it does not scale well as a daily habit.

OmniSource keeps the workflow simple: collect from configured sources, deduplicate, filter by your track, rank the candidates, and publish a Markdown report or GitHub Issue. It does not replace reading; it handles the first pass so you can decide what deserves attention.

```
collect  ->  deduplicate  ->  filter by track  ->  rank  ->  optional explanation  ->  publish
arXiv / HF / RSS / GitHub / HN / Reddit / X / Zhihu / Xiaohongshu      Markdown / GitHub Issue
```

It is designed for people who follow a field over time: graduate students, research engineers, lab teams, or anyone who wants a repeatable source-review routine.

The official website and the open-source package share the same collection,
deduplication, relevance, quality, ranking, and quota logic. An open-source fork
can add or replace sources, but every new candidate still goes through the same
curated pipeline. The website only differs in using the team's maintained
official source set. The AI-tools track additionally uses six shared scores:
relevance, practical value, freshness, usability, credibility, and differentiation.

## What It Does

- **Track-based configuration**: describe a research direction with keywords, arXiv categories, RSS feeds, GitHub queries, accounts, and negative filters. Tracks are grouped under `research/`, `venture/`, and `builder/` by audience.
- **Multi-source collection**: supports arXiv, Hugging Face Daily Papers, RSS, GitHub Trending/Search, Hacker News, Reddit, X/Twitter, Xiaohongshu, and Zhihu.
- **Deduplication with evidence**: if a paper appears on arXiv, HF, X, or a blog, OmniSource keeps it as one item and attaches the source links and signals.
- **Relevance filtering**: combines track rules, keywords, categories, source signals, quality checks, and feedback preferences.
- **Optional model-written notes**: with an API key, papers can include why to read them, the core idea, a method brief, and topic labels. Without a key, the basic report still works.
- **Structured outputs**: outputs Markdown, JSONL, and GitHub Issues. The official website is maintained separately from this DIY package.
- **Optional feedback import**: repository-owner feedback can be summarized into preferences for later runs when a fork chooses to enable that workflow.

## Demo

| | |
|---|---|
| **[Official site](https://lang-jiaqi.github.io/omnisource-site/en/)**: the project's unified information source | **[Research report](https://lang-jiaqi.github.io/omnisource-site/en/report.html)**: the official multi-track view |
| **DIY output**: your fork publishes GitHub Issues | **Sample reports**: [llm-agents](examples/reports/en/llm-agents.md) · [ai-safety](examples/reports/en/ai-safety.md) · [world-models](examples/reports/en/world-models.md) · [robotics](examples/reports/en/robotics.md) · [weekly](examples/reports/en/weekly-llm-agents.md) |

Report items keep source, date, code links, community signals, and short notes when available. The format looks like this:

```
## 1. Example Systems Paper: Reducing KV Cache Memory for Long-Context Inference ...
- priority high · relevance 1.00 · 2026-06-21 · via hf_papers · 👍 74
- Link: https://arxiv.org/abs/xxxx.xxxxx · Code: https://github.com/org/repo

Why it matters: It targets KV-cache memory pressure in long-context inference with a reproducible systems setup.
Key idea: Compress and tier older token cache entries to reduce GPU memory use while preserving generation quality.
```

## 🚀 Quickstart

Goal: see your first report in about five minutes.

There are two ways to use the repository:

| Path | Best for | What you do |
|---|---|---|
| **Fast path** | First-time users | Keep an existing track and run GitHub Actions |
| **Custom path** | Personalized reading | Copy a track, edit its YAML, then add it to `active_tracks` |

#### Step 0 · Prepare the environment

Check the terminal tools:

```bash
python3 --version   # 3.11+
uv --version
git --version
```

If `uv` is missing:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

You also need a GitHub account to fork the repository and receive Issues.

#### Step 1 · Clone

```bash
git clone https://github.com/lang-jiaqi/OmniSource && cd OmniSource
```

#### Step 2 · Preview collection, no key required

```bash
uv run omnisource run --track research/ai-algorithm --no-llm --no-memory --days 7
```

This only exercises the public collection and report pipeline. It does not build the private official website and does not need an API key.
Outputs:

- Markdown report: `reports/`
- Structured data: `reports/*.signals.jsonl`

`--no-llm` skips "why it matters / key idea"; `--no-memory` prevents local tests from marking items as already reported.

#### Step 3 · Add model-written notes

```bash
cp .env.example .env
# add the key required by your track

uv run omnisource run --track research/ai-algorithm
uv run omnisource run --track research/ai-algorithm --days 7    # temporarily widen the paper/HF window
uv run omnisource weekly --track research/ai-algorithm           # weekly digest
```

Recommended model choices:

| Use | Examples |
|---|---|
| Fast collection notes and summaries | OpenAI `gpt-4.1-mini` · Gemini `gemini-2.5-flash` · Qwen `qwen-plus` |
| Stronger reasoning and ranking | OpenAI `o3-mini` · Gemini `gemini-2.5-pro` · Qwen `qwen-max` |

OpenAI uses `OPENAI_API_KEY` and `provider: openai`. Gemini, Qwen, and gateways
use `OPENAI_COMPATIBLE_API_KEY` / `OPENAI_COMPATIBLE_BASE_URL` and
`provider: openai_compatible`; set `model` to the name supported by that service.
The secret name stays `OPENAI_COMPATIBLE_API_KEY`; its value is the Gemini, Qwen,
or gateway key.

If a track uses Anthropic, add `ANTHROPIC_API_KEY`. If it uses Reddit's OAuth
backend, also add `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`. These are
optional; unused sources need no credentials.

The main DIY research example is `research/ai-algorithm`; the public developer
example is [`builder/ai-tools.yaml`](tracks/builder/ai-tools.yaml). The official
website's AI-tool radar remains a separate, richer weekly view.

#### Step 4 · Run GitHub Issue reports automatically

After forking, configure GitHub Actions:

1. **Add secrets**: Settings → Secrets and variables → Actions
   - `OPENAI_API_KEY`, or `OPENAI_COMPATIBLE_API_KEY` + `OPENAI_COMPATIBLE_BASE_URL`
   - `ANTHROPIC_API_KEY` (only for Anthropic tracks)
   - `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET` (only for Reddit OAuth)
   - `APIFY_TOKEN` (optional; enables Twitter/X buzz)
2. **Enable Issues** under Settings → General → Features.
3. **Run once manually**: Actions → `Daily GitHub Issue Report` → **Run workflow**. Optionally set `days`.
4. **Schedule**: the public workflow opens one GitHub Issue per active track. The weekly workflow does the same on Mondays.

The official website, its AI-tool radar, email subscriptions, Settings page,
and Pages deployment are maintained separately in the private project workspace.

Each track keeps a record of published items by default. Daily runs do not repeat
items from earlier daily runs, and weekly runs do not repeat items from earlier
weekly runs. Weekly memory is separate from daily memory, so a weekly digest is
not emptied just because an item appeared in a daily report. Use `--no-memory`
only when debugging and you intentionally want to disable this protection.
GitHub Actions stores `data/memory.db` in the repository's Actions cache, so this
memory survives across scheduled runs. Daily and weekly reports share the same
database but use separate memory scopes. Clearing the Actions cache resets this
history and may allow older items to appear again.

## 📥 Sources

| Source | What | Setup |
|---|---|---|
| **arXiv** | papers | out of the box |
| **Hugging Face** | daily papers + upvotes | out of the box |
| **Lab-blog RSS** | OpenAI/Google/BAIR… | out of the box |
| **BlogrXiv** | curated AI research blogs and technical writing | public catalogue, out of the box; see [`docs/blogrxiv-setup.md`](docs/blogrxiv-setup.md) |
| **GitHub** | Trending repos + recent momentum | out of the box |
| **Hacker News** | community discussion | out of the box |
| **Reddit** | community discussion | local OpenCLI, or OAuth with `REDDIT_CLIENT_ID/SECRET` |
| **Twitter/X** | tweet buzz | configure broad queries or exact account handles; set `APIFY_TOKEN` to enable |
| **Xiaohongshu** | public posts from specified creators | install OpenCLI locally and connect a logged-in Chrome session; see [`docs/xiaohongshu-setup.md`](docs/xiaohongshu-setup.md) |
| **Zhihu** | articles and answers from specified users | install OpenCLI locally and connect a logged-in Chrome session |

> A community post (HN/Reddit/X) that links a paper folds into **that paper's buzz** — not a separate noisy entry.
> Seeded accounts are not your personal following list; they are high-signal accounts combined with keyword search.

## Quick source setup

Choose sources in the track, then add the matching config block:

```yaml
sources:
  - arxiv
  - rss
  - twitter
  - xiaohongshu
  - zhihu
```

RSS is the easiest option and works in GitHub Actions:

```yaml
rss_feeds:
  - https://huggingface.co/blog/feed.xml
  - https://openai.com/news/rss.xml
rss_days: 21
```

For GitHub Actions, Twitter/X does not need OpenCLI. Add `APIFY_TOKEN` to your
fork's Actions secrets and use the CI-safe `apify` backend:

```yaml
sources:
  - twitter
twitter:
  mode: apify
  queries: ["AI agent", "LLM tool"]
  handles: [OpenAI, AnthropicAI]
  max_results: 50
```

Apify may have a free quota and can charge after that quota is used. It does not
need Chrome, Browser Bridge, or OpenCLI.

For local-only collection, OpenCLI remains an optional backend. Install OpenCLI
and its Browser Bridge, log into x.com in Chrome, and check the connection:

```bash
opencli doctor
opencli twitter search '"LLM serving"' --product live --limit 5 -f json
opencli twitter tweets karpathy --limit 5 -f json
```

```yaml
twitter:
  mode: opencli
  search:
    enabled: true
    queries: ["LLM serving", "reasoning model"]
  accounts:
    enabled: true
    handles: [karpathy, OpenAI, HuggingFace]
```

Xiaohongshu and Zhihu use the same logged-in OpenCLI browser session:

```bash
opencli xiaohongshu user USER_ID --limit 3 -f json
opencli zhihu user-articles USER_NAME --limit 3 -f json
opencli zhihu user-answers USER_NAME --limit 3 -f json
```

On macOS, if `opencli doctor` says `Unable to find application named
'OpenCLIApp'`, the Browser Bridge login is not the problem. The managed
`opencli` launcher failed to start its daemon. Use the bundled runtime instead:

```bash
env -u OPENCLI_DAEMON_PORT \
  /Applications/OpenCLIApp.app/Contents/Resources/node_modules/node/bin/node \
  /Applications/OpenCLIApp.app/Contents/Resources/node_modules/@jackwener/opencli/dist/src/main.js \
  doctor
```

Then keep this setting in the same terminal before running the track:

```bash
export OPENCLI_COMMAND='env -u OPENCLI_DAEMON_PORT /Applications/OpenCLIApp.app/Contents/Resources/node_modules/node/bin/node /Applications/OpenCLIApp.app/Contents/Resources/node_modules/@jackwener/opencli/dist/src/main.js'
uv run omnisource run --track builder/my-social-radar
```

On Windows, use `opencli` from PowerShell if `opencli doctor` reports
`Daemon: running` and `Extension: connected`; do not copy the macOS path.

Their YAML blocks use `backend: opencli` and a list of `creators`. These browser
sources are for local runs; a standard GitHub Actions runner cannot access your
Chrome session. Use [Twitter/X setup](docs/twitter-setup.md) for the CI-safe
Apify option, and [customizing your radar](docs/customizing-your-radar.md) for
the Xiaohongshu/Zhihu fields.

Note: OpenCLI 1.8.5 may report `Navigation rejected` for a direct Zhihu
`user-articles` command even when the login is valid. OmniSource catches this
case and uses a browser-session fallback. To test OmniSource's Zhihu source,
run this in a terminal where `OPENCLI_COMMAND` is already configured:

```bash
uv run python -c 'from omnisource.sources.zhihu import ZhihuSource; rows=ZhihuSource().fetch({"days":30,"zhihu":{"creators":[{"user":"USER_NAME","articles":True,"answers":True}]}}); print(f"zhihu_signals={len(rows)}"); [print(x.title) for x in rows]'
```

## How It Works

OmniSource is a pluggable pipeline. Each source is first normalized into one `Signal` shape; deduplication, filtering, ranking, and publishing all work on that shape.

| Module | What it does |
|---|---|
| **Sources** [`sources/`](omnisource/sources) | normalize feeds into `Signal`s |
| **Dedup + memory** [`memory/`](omnisource/memory) | merge across sources; don't repeat day to day |
| **Quality filter** [`agents/quality.py`](omnisource/agents/quality.py) | drop clearly weak or off-track candidates |
| **Content notes** [`agents/analyst.py`](omnisource/agents/analyst.py) | optional model step for relevance, short notes, and topic labels |
| **Editor + Publishers** | render to Markdown, deliver to Issue / file |

## Code layout

The public package follows the execution path:

```text
omnisource/              reusable pipeline and CLI
├── sources/             source adapters
├── agents/              collection, filtering, analysis, and editing
├── ranking/             scoring and ordering
├── publishers/          Markdown and GitHub Issue output
├── llm/                 model provider adapters
└── main.py              pipeline orchestration
tracks/                  YAML track configurations grouped by audience
├── research/             research domains and reports
├── venture/              startup and market signals
└── builder/              tools, infrastructure, and engineering
examples/                copyable tracks and sample reports
.github/workflows/       daily and weekly GitHub Issue jobs
tests/                   unit tests for the public core
```

## Configure Your Track

- **Example tracks**: `research/ai-algorithm` · `builder/ai-tools` (`--track <path>`); other YAML files cover additional directions.
- **Window**: `days` in a track controls the arXiv/HF paper lookback; use `--days 7` for a temporary override.
- **Repositories**: GitHub Trending daily/weekly comes first; when it is sparse, only recently created relevant repos fill the pool, so old incumbents do not dominate.
- **Fastest custom track**: copy [`examples/tracks/custom-ai-radar.yaml`](examples/tracks/custom-ai-radar.yaml) to `tracks/research/my-ai-radar.yaml`, then edit keywords, categories, sources, and X/Twitter handles.
- **Choose scheduled tracks**: edit `active_tracks` in [`omnisource.yaml`](omnisource.yaml); GitHub Actions loops over this list for daily and weekly GitHub Issue reports.
- **Watch fixed X accounts**: use `twitter.mode: apify` for GitHub Actions, or `twitter.mode: opencli` for a local Chrome session.
- **Watch specific paper authors**: set `watchlist.authors`; it matches paper author names, not your X follow list.
- **Advanced tuning**: copy [`tracks/research/ai-algorithm.yaml`](tracks/research/ai-algorithm.yaml), edit ranking weights, `watchlist`, RSS feeds, and GitHub queries.
- **New source**: write a class in `omnisource/sources/` returning `list[Signal]`, register it — nothing else changes.

See [`docs/`](docs): [customizing your reading setup](docs/customizing-your-radar.md) · [architecture](docs/architecture.md) · [adding a source](docs/adding-a-source.md) · [adding a track](docs/adding-a-track.md).

## Status

**v0.2** — a multi-source core for DIY research reports.

- The main example track is `research/ai-algorithm`; the official developer channel is maintained as the separate AI-tool radar.
- Daily reports now target Top 15 papers + 5 repositories + 5 lab notes, with heavy author-graph enrichment for all 15 papers.
- Markdown templates and sample reports are bilingual: the Chinese README links to Chinese samples, and the English README links to English samples.
- Repository discovery is Trending-first: daily/weekly GitHub Trending comes first; sparse days are filled only by recently created relevant repos, not old incumbents.
- The paper lookback window is configurable through track `days`, CLI `--days`, and the GitHub Actions manual-run input.
- Twitter/X can be enabled with `APIFY_TOKEN`; default tracks combine keyword search with high-signal account seeds and fold tweets into paper/repo buzz.
- The public workflows open GitHub Issues only. The official website is maintained separately and is not part of this DIY package.

**v0.1** — multi-source fetch, deduplication, relevance checks, summaries, quality filtering, author graphs, daily automation, bilingual output.

Roadmap: more stable affiliation enrichment, more source connectors, team workflows.

## 🤝 Contributing

Forks, tracks, sources, and publishers welcome. A good track is often a researcher's reading list plus their filtering rules.

## 📄 License

[PolyForm Noncommercial 1.0.0](LICENSE) © 2026 lang-jiaqi

## Authors

Jiaqi Lang<sup>*</sup>, Wangbo Zhao, Pengfei Zhou, Run Liu, Bin Xv, Yixing Ma, weidong tang

*Corresponding author: Jiaqi Lang · National University of Singapore (NUS) · lang.jiaqi@u.nus.edu*

## 🌍 Independent World Model Ventures

## Interested in World Models?

The authors of this project are also independently exploring entrepreneurial opportunities in the world-model space.

**Wangbo Zhao** ([Google Scholar](https://scholar.google.com.hk/citations?user=aocj89kAAAAJ&hl=zh-CN), email) is currently building an early-stage startup focused on world models and the infrastructure required to develop and scale them. The company is currently raising a seed round. Investors and strategic partners interested in this direction are welcome to get in touch.

**Pengfei Zhou** ([lance@infrec.tech](mailto:lance@infrec.tech)) is the founder of an independent startup focused on world models and agentic game development. The company is committed to building systems with general-purpose intelligence that can understand, predict, and ultimately interact with human environments and the real world. For more information, please visit the [company website](https://www.cardinal-agi.com/).

These ventures are independent of this project and of each other.
