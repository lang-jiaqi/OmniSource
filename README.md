<div align="center">

<h1>🔭 OmniSource</h1>

<p>
  <strong>Connect signals from across the world and explore the infinite possibilities of AI with researchers, innovators, and developers</strong><br>
  ☘️ Three information channels: research daily｜startup market radar｜developer tools weekly
</p>

<p>
  <img src="https://img.shields.io/badge/license-PolyForm%20Noncommercial-8bd3a8?style=for-the-badge" alt="PolyForm Noncommercial License">
  <img src="https://img.shields.io/badge/Python-3.11%2B-8ab4f4?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/built%20with-uv-b39ddb?style=for-the-badge&logo=uv&logoColor=white" alt="Built with uv">
  <img src="https://img.shields.io/badge/GitHub%20Issues-ready-24292f?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Issues ready">
  <img src="https://img.shields.io/badge/PRs-welcome-f4c95d?style=for-the-badge&logo=github&logoColor=white" alt="PRs welcome">
</p>

<p>
  🌐 <a href="https://lang-jiaqi.github.io/omnisource-site/">Visit the OmniSource official site</a>
</p>

<p>
  <a href="https://lang-jiaqi.github.io/omnisource-site/report.html">Research reports</a> ·
  <a href="https://lang-jiaqi.github.io/omnisource-site/entrepreneur.html">Startup intelligence</a> ·
  <a href="https://lang-jiaqi.github.io/omnisource-site/tools.html">AI tool radar</a> ·
  <a href="README.zh-CN.md">中文</a>
</p>

</div>

There is more information than ever, yet it is harder to find what is truly worth paying attention to. OmniSource captures signals from papers, technical blogs, GitHub, industry media, and communities, then deduplicates, filters, and ranks them into a report worth opening.

You can read the unified information source on the official site, or fork the repository, rewrite your own keywords and sources, and have a personalized report published automatically to GitHub Issues. 📝

## 📬 Two ways to use it

| Entry point | Best for | Content control |
|---|---|---|
| [Official site 🌐](https://lang-jiaqi.github.io/omnisource-site/) | People who want to read the unified information source directly | Maintained by the project team |
| GitHub Issue 🧩 | People who want to DIY their own information stream | Modify it yourself after forking |

This public repository provides only the GitHub Issue DIY workflow. The official site's daily reports, weekly reports, and email subscriptions belong to the official website.

The local `reports/` directory stores Markdown files only, making them convenient to inspect and debug.

## 🧭 Three customizable tracks

Choose a report direction based on your role, then continue customizing it in your fork:

| Type | What it follows | Official site entry | Open-source YAML track |
|---|---|---|---|
| **Researcher** 🔬 | Papers, research methods, lab updates, and open-source implementations | [Research reports](https://lang-jiaqi.github.io/omnisource-site/report.html) | [ai-algorithm.yaml](tracks/research/ai-algorithm.yaml) |
| **Entrepreneur** 🚀 | Funding, products, markets, founding teams, and hiring | [Startup intelligence](https://lang-jiaqi.github.io/omnisource-site/entrepreneur.html) | [entrepreneur.yaml](tracks/venture/entrepreneur.yaml) |
| **Community developer** 🧑‍💻 | AI tools | [AI tool radar](https://lang-jiaqi.github.io/omnisource-site/tools.html) | [ai-tools.yaml](tracks/builder/ai-tools.yaml) |

The three types are fundamentally the same: copy a track, customize its keywords, sources, and filtering rules, then view your results through GitHub Issues. The directory names are `research/`, `venture/`, and `builder/`; each YAML file in the research directory is a specific research domain.

The official site and OpenSource use the same collection, deduplication, relevance judgment, quality filtering, ranking, and quota controls. OpenSource lets you freely add or replace sources, but new sources only expand the candidate pool; every candidate still goes through the same curation pipeline. The official site simply uses the official sources maintained by the project team.

The AI-tools track also uses six shared scores: relevance, practical value, freshness, usability, credibility, and differentiation.

## 🚀 Quickstart

### Step 0 · 🧰 Prepare the environment

Check the environment in your terminal:

```bash
python3 --version   # 3.11+
uv --version
git --version
```

If `uv` is not installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

You also need a GitHub account to fork the repository and receive Issues.

### Step 1 · 🍴 Fork the repository

Click **Fork** in the upper-right corner of GitHub, then enable **Issues** and **Actions** in your fork.
If you want to modify a track locally, clone your fork:

**macOS / Linux**

```bash
git clone https://github.com/your-username/OmniSource.git && cd OmniSource
```

**Windows PowerShell**

```powershell
git clone https://github.com/your-username/OmniSource.git
Set-Location OmniSource
```

### Step 2 · 🔑 Configure a model

Add secrets under **Settings → Secrets and variables → Actions**; models are configured in the track's `llm` section:

| Use | Recommended model examples |
|---|---|
| Information collection, summaries, and daily reports | OpenAI `gpt-4.1-mini` · Gemini `gemini-2.5-flash` · Qwen `qwen-plus` |
| Stronger reasoning, filtering, and judgment | OpenAI `o3-mini` · Gemini `gemini-2.5-pro` · Qwen `qwen-max` |

OpenAI's official API:

~~~
OPENAI_API_KEY=your OpenAI API key
~~~

Gemini, Qwen, or a gateway using an OpenAI-compatible API:

~~~
OPENAI_COMPATIBLE_API_KEY=your Gemini / Qwen / gateway key
OPENAI_COMPATIBLE_BASE_URL=https://the-compatible-service-endpoint/v1
~~~

Fill in the corresponding track configuration:

~~~yaml
llm:
  provider: openai                 # Official OpenAI API
  model: gpt-4.1-mini
~~~

Gemini, Qwen, and gateways:

~~~yaml
llm:
  provider: openai_compatible
  model: gemini-2.5-flash       # Or qwen-plus or another supported model
~~~

The secret name must be `OPENAI_COMPATIBLE_API_KEY`; use the provider's documentation for the model name and Base URL. GitHub Actions automatically provides the `GITHUB_TOKEN` needed to create Issues in your own fork. The upstream repository uses `OMNISOURCE_ISSUE_TOKEN` to publish reports to `lang-jiaqi/OmniSource-workspace`.

If a track uses Anthropic, add `ANTHROPIC_API_KEY`. If it uses Reddit's OAuth mode, also add `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`. These are optional; sources you do not use need no configuration.

### Step 3 · ⚡ Quick start: use an existing track

If you want to see a report first, you do not need to create or modify YAML. Simply keep the desired directions in the `active_tracks` section of [omnisource.yaml](omnisource.yaml):

```yaml
active_tracks:
  - research/ai-algorithm
  - venture/entrepreneur
```

Save the file, then open **Actions → Daily GitHub Issue Report → Run workflow**. Each active track generates a separate GitHub Issue. You can also run **Weekly GitHub Issue Report** to generate a weekly report.

This path is suitable for first-time users: complete only Steps 0–2, then run Actions. Existing examples include [AI algorithm](tracks/research/ai-algorithm.yaml), [startup intelligence](tracks/venture/entrepreneur.yaml), and [AI tools](tracks/builder/ai-tools.yaml).

### Step 4 · 🛠️ Personalize the configuration: create your own track

If you want to follow a topic over the long term, copy the closest example. Each name corresponds to a YAML file under `tracks/<audience>/`:

**macOS / Linux**

```bash
cp tracks/research/ai-algorithm.yaml tracks/research/my-radar.yaml
```

**Windows PowerShell**

```powershell
Copy-Item tracks/research/ai-algorithm.yaml tracks/research/my-radar.yaml
```

Then edit the name, sources, keywords, and output counts:

```yaml
name: my-radar
display_name: My area of interest
description: What I want to follow over time

sources:
  - arxiv
  - rss
  - github

keywords:
  - your keyword
  - another keyword

output:
  top_papers: 10
  top_repos: 5
  top_blogs: 5
  language: English
```

Finally, add it to [omnisource.yaml](omnisource.yaml):

```yaml
active_tracks:
  - research/ai-algorithm
  - venture/entrepreneur
  - research/my-radar
```

Common options include keywords and exclusion terms, arXiv categories, RSS URLs, the number kept per category, report language, and the lookback window. See the [AI algorithm example](tracks/research/ai-algorithm.yaml), [startup example](tracks/venture/entrepreneur.yaml), and [AI tools example](tracks/builder/ai-tools.yaml).

After configuring the track, add it to `active_tracks` and return to Step 3 to run Actions. It affects only your fork and does not change the official website.

### Step 5 · 📡 Choose your sources

Sources are enabled in the track's top-level `sources:` list. The easiest first
run uses public sources only. They need no extra account, token, Chrome, or
OpenCLI.

Open the track file you copied in Step 4 and replace its entire `sources:` block
with this:

```yaml
sources:
  - arxiv
  - hf_papers
  - rss
  - github
  - hackernews
```

Keep the track's existing `categories`, `keywords`, `llm`, and `output` sections.
The `arxiv` source needs `categories`; the example tracks already contain them.
`hf_papers` and `hackernews` work without a separate configuration block.

#### RSS feeds

RSS settings go at the top level of the same track file. Do not put them under
an `rss:` heading. Replace the existing RSS block, or add this block once:

```yaml
rss_feeds:
  - https://huggingface.co/blog/feed.xml
  - https://blog.research.google/feeds/posts/default
  - https://openai.com/news/rss.xml
rss_days: 21
```

Optional public sources can be enabled by adding `blogrxiv` to the same list:

```yaml
sources:
  - arxiv
  - hf_papers
  - rss
  - github
  - hackernews
  - blogrxiv
```

Optional tuning fields:

```yaml
hf_limit: 100
hn_query: "AI agent OR foundation model"
hn_top: 50
blogrxiv_days: 1
github_query: "AI agent OR foundation model"
```

#### Twitter / X in GitHub Actions

Use Apify for X in GitHub Actions. In your fork, open **Settings → Secrets and
variables → Actions → New repository secret** and add:

```text
Name: APIFY_TOKEN
Secret: paste your Apify token here
```

Never put the token in YAML or commit it to GitHub. Then replace the track's
source list with the following version, or add only the `twitter` line to your
existing list:

```yaml
sources:
  - arxiv
  - hf_papers
  - rss
  - github
  - hackernews
  - twitter

twitter:
  mode: apify
  queries:
    - "AI agent"
    - "LLM tool"
  handles:
    - OpenAI
    - AnthropicAI
  max_results: 50
```

Apify does not require Chrome, Browser Bridge, or OpenCLI. It may charge after
its free quota is used. See [Twitter/X configuration](docs/twitter-setup.md) for
the OpenCLI and local alternatives.

#### Xiaohongshu / Zhihu: local computer only

These sources use a logged-in Chrome session through [OpenCLI](https://github.com/jackwener/OpenCLI).
They do not run on an ordinary GitHub Actions runner. Skip this section if you
only want scheduled GitHub Issues.

Install OpenCLI and Browser Bridge, log in to both sites in Chrome, and check
the connection:

```bash
opencli doctor
opencli xiaohongshu user USER_ID --limit 3 -f json
opencli zhihu user-articles USER_NAME --limit 3 -f json
opencli zhihu user-answers USER_NAME --limit 3 -f json
```

For a local track, add the source names and replace the placeholders:

```yaml
sources:
  - xiaohongshu
  - zhihu

xiaohongshu:
  enabled: true
  command: opencli
  timezone: Asia/Shanghai
  days: 1
  max_notes_per_creator: 20
  creators:
    - name: "Creator name"
      user_id: "USER_ID"

zhihu:
  enabled: true
  command: opencli
  timezone: Asia/Shanghai
  days: 7
  max_items_per_creator: 20
  creators:
    - name: "Zhihu user"
      user: "USER_NAME"
      articles: true
      answers: true
```

Then run the track locally:

```bash
uv run omnisource run --track builder/my-social-radar
```

On Windows, use the same `opencli` commands in PowerShell. If macOS says
`Unable to find application named 'OpenCLIApp'`, follow the bundled-runtime
steps in [Xiaohongshu setup](docs/xiaohongshu-setup.md). For the full Zhihu
field reference, see the [customization guide](docs/customizing-your-radar.md).

#### Reddit

Reddit has two modes. For a local Chrome session, use `mode: opencli`. For
GitHub Actions, create a Reddit application, add the `REDDIT_CLIENT_ID` and
`REDDIT_CLIENT_SECRET` repository secrets, and add this configuration:

```yaml
sources:
  - reddit

reddit:
  mode: oauth
  max_results: 50

reddit_subreddits:
  - MachineLearning
  - LocalLLaMA
```

For the local OpenCLI configuration and Reddit application details, see
[Reddit setup](docs/reddit-setup.md).

### Step 6 · 🧪 Optional: validate locally

To check collection, deduplication, and filtering before running Actions, use a local preview command that does not call a model:

**macOS / Linux**

```bash
uv sync
uv run omnisource run --track research/ai-algorithm --no-llm --no-memory
```

**Windows PowerShell**

```powershell
uv sync
uv run omnisource run --track research/ai-algorithm --no-llm --no-memory
```

If a Markdown file appears in `reports/`, the basic configuration is working. To generate official GitHub Issues, run the corresponding workflow in **Actions**; model reports use the keys configured in Step 2, while X in `apify` mode additionally uses `APIFY_TOKEN`.

The open-source version only handles GitHub Issue reports for your fork; it does not handle the official site's daily reports, weekly reports, or email subscriptions. Each track records what has already been published: daily reports do not repeat earlier daily items, and weekly reports do not repeat earlier weekly items. `--no-memory` is for debugging only and temporarily disables this protection.

GitHub Actions stores `data/memory.db` in the repository cache, so deduplication continues across runs. Daily and weekly reports share the same database but use different memory scopes. If you manually clear the Actions cache, older items may appear again on the next run.

## 🧱 Code structure

The open-source area is organized around the “collect → filter → publish” flow:

~~~text
omnisource/              core pipeline and CLI
├── sources/             source adapters
├── agents/              collection, filtering, analysis, and editing
├── ranking/             ranking and scoring
├── publishers/          Markdown and GitHub Issue publishing
├── llm/                 model interface adapters
└── main.py              overall pipeline orchestration
tracks/                  YAML tracks grouped by audience
├── research/             research directions for researchers
├── venture/              startup intelligence for entrepreneurs
└── builder/              tools and engineering directions for developers
examples/                copyable tracks and sample reports
.github/workflows/       daily and weekly GitHub Issue workflows
tests/                   open-source core tests
~~~

Usually you only need to edit `tracks/<audience>/` and `omnisource.yaml`; modify `omnisource/` only when adding a new source or publishing method.

## 🧭 FAQ

### 📨 The Actions workflow succeeds, but there is no Issue

Check two things:

1. **Issues** is enabled for the repository.
2. The workflow file retains the permissions needed to create Issues. Forks use the `GITHUB_TOKEN` automatically provided by GitHub Actions; the upstream repository also needs the `OMNISOURCE_ISSUE_TOKEN` Secret for its separate Issue destination.

### 🔐 `invalid_api_key` error

Check:

- Whether the Secret name is exactly correct;
- Whether the API key was copied completely;
- Whether the gateway uses `OPENAI_COMPATIBLE_API_KEY` and `OPENAI_COMPATIBLE_BASE_URL`;
- Whether the Base URL is the API address required by the gateway, usually including `/v1`;
- Whether the model configured in the track is supported by the gateway.

### 🌐 Will changing my report affect the official website?

No.

Your fork only affects your own GitHub Issue reports. The official website uses content and configuration maintained independently by the project team and runs separately from user forks.

## License

This project is licensed under the [PolyForm Noncommercial License 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/).

## Authors

Jiaqi Lang<sup>*</sup>, Wangbo Zhao, Pengfei Zhou, Run Liu, Bin Xv, Yixing Ma, weidong tang

*Corresponding author: Jiaqi Lang · National University of Singapore (NUS) · lang.jiaqi@u.nus.edu*

## Interested in World Models?

The authors of this project are also independently exploring startup opportunities in the world model space.

- **Wangbo Zhao** ([Google Scholar](https://scholar.google.com.hk/citations?user=aocj89kAAAAJ&hl=zh-CN), [email](mailto:wangbo.zhao96@gmail.com)) is preparing an early-stage startup focused on world models and their infrastructure. The project is currently raising a seed round. Investors and strategic partners interested in this direction are welcome to get in touch.

- **Pengfei Zhou** ([lance@infrec.tech](mailto:lance@infrec.tech)) is the founder of an independent startup focused on world models and agentic game development. The company is committed to building systems with general intelligence capabilities that can understand and predict human environments and the real world, and ultimately interact with them. For more information, please visit the [company website](https://www.cardinal-agi.com).

The ventures described above are independent of this project and are not affiliated with one another.
