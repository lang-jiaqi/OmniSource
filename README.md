<div align="center">

<h1>🔭 OmniSource</h1>

<p>
  <strong>Connect signals from across a changing world and explore AI's limitless possibilities with researchers, innovators, and developers</strong><br>
   ☘️Three intelligence channels: Research Daily | Startup Market Radar | Developer Tools Weekly
</p>

<p>
  <img src="https://img.shields.io/badge/license-PolyForm%20Noncommercial-8bd3a8?style=for-the-badge" alt="PolyForm Noncommercial License">
  <img src="https://img.shields.io/badge/Python-3.11%2B-8ab4f4?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/built%20with-uv-b39ddb?style=for-the-badge&logo=uv&logoColor=white" alt="Built with uv">
  <img src="https://img.shields.io/badge/GitHub%20Issues-ready-24292f?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Issues ready">
  <img src="https://img.shields.io/badge/PRs-welcome-f4c95d?style=for-the-badge&logo=github&logoColor=white" alt="PRs welcome">
</p>

<p>
  🌐 <a href="https://lang-jiaqi.github.io/omnisource-site/en/">Visit the OmniSource website</a>
</p>

<p>
  <a href="https://lang-jiaqi.github.io/omnisource-site/en/report.html">Research Reports</a> ·
  <a href="https://lang-jiaqi.github.io/omnisource-site/en/entrepreneur.html">Startup Intelligence</a> ·
  <a href="https://lang-jiaqi.github.io/omnisource-site/en/tools.html">AI Tool Radar</a> ·
  <a href="README.zh-CN.md">中文</a>
</p>

</div>

As information multiplies, the things truly worth following become harder to find. OmniSource captures signals from papers, technical blogs, GitHub, industry media, and communities, then deduplicates, filters, and ranks them into a report worth opening.

You can read the unified information feed on the official website, or fork the repository, customize the keywords and sources, and automatically publish your own reports to GitHub Issues. 📝

## 📬 Two Ways to Use OmniSource

| Entry point | Best for | Who controls the content |
|---|---|---|
| [Official website 🌐](https://lang-jiaqi.github.io/omnisource-site/en/) | People who want to read the unified information feed directly | Maintained by the project team |
| GitHub Issues 🧩 | People who want to build their own information feed | You customize it after forking |

This public repository supports the DIY GitHub Issues workflow only. The daily reports, weekly reports, and email subscriptions on the website belong to the official website.

The local `reports/` directory stores Markdown files only, making them easy to inspect and debug.

## 🧭 Three Customizable Track Types

Choose a report direction based on your role, then continue customizing it in your fork:

| Type | What to follow | Official website | Open-source YAML track |
|---|---|---|---|
| **Researchers** 🔬 | Papers, research methods, lab updates, and open-source implementations | [Research Reports](https://lang-jiaqi.github.io/omnisource-site/en/report.html) | [ai-algorithm.yaml](tracks/research/ai-algorithm.yaml) |
| **Entrepreneurs** 🚀 | Funding, products, markets, founding teams, and hiring | [Startup Intelligence](https://lang-jiaqi.github.io/omnisource-site/en/entrepreneur.html) | [entrepreneur.yaml](tracks/venture/entrepreneur.yaml) |
| **Community Developers** 🧑‍💻 | AI tools | [AI Tool Radar](https://lang-jiaqi.github.io/omnisource-site/en/tools.html) | [ai-tools.yaml](tracks/builder/ai-tools.yaml) |

All three types work the same way: copy a track, replace its keywords, sources, and filtering rules with your own, then view the results in GitHub Issues. Their directories are `research/`, `venture/`, and `builder/`; each YAML file in the research directory represents a specific research domain.

The official website and the open-source package use the same collection, deduplication, relevance assessment, quality filtering, ranking, and result-limit logic. The open-source package lets you freely add or replace sources, but new sources only expand the candidate pool: every candidate still passes through the same curation pipeline. The website simply uses the official sources maintained by the project team.

The AI tools track also applies the same six scores everywhere: relevance, practical value, freshness, usability, credibility, and differentiation.

## 🚀 Quickstart

First, choose the path that matches your goal:

| Path | Best for | Result |
|---|---|---|
| **Download a Release** | Quickly trying OmniSource or using a built-in track | Generate Markdown and JSONL reports locally, with full LLM analysis support |
| **Fork the repository** | Changing what you follow, scheduling runs, or creating GitHub Issues | Own your configuration, Actions workflows, and long-term memory |

### Path A · Download a Release and Try It

You need Python 3.11+ and `uv`. If you do not have `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

Install the `v0.1.1` wheel using either option:

```bash
# Recommended: install it as an isolated CLI
uv tool install https://github.com/lang-jiaqi/OmniSource/releases/download/v0.1.1/omnisource-0.1.1-py3-none-any.whl

# Or install it in an already activated virtual environment
python -m pip install https://github.com/lang-jiaqi/OmniSource/releases/download/v0.1.1/omnisource-0.1.1-py3-none-any.whl
```

If your terminal cannot find `omnisource` after using `uv`, run `uv tool update-shell`, then reopen the terminal.

List the built-in tracks, then run a preview without calling a model:

**macOS / Linux**

```bash
mkdir omnisource-run && cd omnisource-run
omnisource active-tracks
omnisource run --track research/ai-algorithm --no-llm --no-memory --days 7
```

**Windows PowerShell**

```powershell
New-Item -ItemType Directory -Force omnisource-run
Set-Location omnisource-run
omnisource active-tracks
omnisource run --track research/ai-algorithm --no-llm --no-memory --days 7
```

Reports are written to `reports/` in the current directory. The Release fully supports LLM analysis. Configure the API key required by the default OpenAI track, remove `--no-llm`, and create a `.env` file in the current directory:

```dotenv
OPENAI_API_KEY=your_OpenAI_API_key
```

Then run:

```bash
omnisource run --track research/ai-algorithm
```

This path is best for using the built-in tracks. To modify tracks, use GitHub Actions, or schedule Issue reports, follow the Fork path below.

### Path B · Fork, Customize, and Run Long-Term

You need a GitHub account and Git. Local runs also require Python 3.11+ and `uv`. After forking, you can customize tracks and let Actions automatically generate daily and weekly reports.

#### B1 · 🍴 Fork and Clone the Repository

Click **Fork** in the upper-right corner of GitHub, then enable **Issues** and **Actions** in your fork. To edit a track locally, clone your fork:

**macOS / Linux**

```bash
git clone https://github.com/YOUR_USERNAME/OmniSource.git && cd OmniSource
```

**Windows PowerShell**

```powershell
git clone https://github.com/YOUR_USERNAME/OmniSource.git
Set-Location OmniSource
```

#### B2 · 🔑 Configure a Model

Add secrets under **Settings → Secrets and variables → Actions**. The model is configured in the track's `llm` section:

| Use case | Recommended model examples |
|---|---|
| Collection, summarization, and daily reports | OpenAI `gpt-4.1-mini` · Gemini `gemini-2.5-flash` · Qwen `qwen-plus` |
| Stronger reasoning, filtering, and judgment | OpenAI `o3-mini` · Gemini `gemini-2.5-pro` · Qwen `qwen-max` |

The built-in public tracks use OpenAI `gpt-4.1-mini` by default. To use Gemini, Qwen, or a self-hosted gateway, update both `provider` and `model` in the track and configure the matching compatible endpoint.

For the official OpenAI API:

~~~
OPENAI_API_KEY=your OpenAI API key
~~~

For Gemini, Qwen, or a gateway using an OpenAI-compatible endpoint:

~~~
OPENAI_COMPATIBLE_API_KEY=your Gemini / Qwen / gateway key
OPENAI_COMPATIBLE_BASE_URL=https://your-provider-compatible-endpoint/v1
~~~

Configure the track like this:

~~~yaml
llm:
  provider: openai                 # Official OpenAI API
  model: gpt-4.1-mini
~~~

For Gemini, Qwen, and gateways:

~~~yaml
llm:
  provider: openai_compatible
  model: gemini-2.5-flash          # Or qwen-plus / another model supported by your provider
~~~

The secret name remains `OPENAI_COMPATIBLE_API_KEY`; use the model name and Base URL documented by your provider. GitHub Actions automatically provides the `GITHUB_TOKEN` required to create Issues.

To use one gateway for every Actions track without editing each YAML file, add these values under **Settings → Secrets and variables → Actions → Variables**:

~~~
OMNISOURCE_LLM_PROVIDER=openai_compatible
OMNISOURCE_LLM_MODEL=model-supported-by-your-gateway
~~~

If a track uses Anthropic, add `ANTHROPIC_API_KEY`. If it uses Reddit's OAuth mode, also add `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`. These are optional; sources you do not use need no credentials.

#### B3 · ⚡ Quick Start with an Existing Track

You do not need to create or edit YAML just to see your first report. Keep the desired built-in tracks under `active_tracks` in [omnisource.yaml](omnisource.yaml):

```yaml
active_tracks:
  - research/ai-algorithm
  - venture/entrepreneur
```

Save the file, then open **Actions → Daily GitHub Issue Report → Run workflow**. Each active track creates its own GitHub Issue. You can also run **Weekly GitHub Issue Report** to generate weekly reports.

This path is designed for long-term use: after completing B1–B2, you can run Actions. Existing examples include [AI Algorithms](tracks/research/ai-algorithm.yaml), [Startup Intelligence](tracks/venture/entrepreneur.yaml), and [AI Tools](tracks/builder/ai-tools.yaml).

#### B4 · 🛠️ Personalize Your Setup: Create a Track

To follow your own topic over time, copy the closest example. Each name maps to a YAML file under `tracks/<type>/`:

**macOS / Linux**

```bash
cp tracks/research/ai-algorithm.yaml tracks/research/my-radar.yaml
```

**Windows PowerShell**

```powershell
Copy-Item tracks/research/ai-algorithm.yaml tracks/research/my-radar.yaml
```

Then change its name, sources, keywords, and output limits:

```yaml
name: my-radar
display_name: My Focus Area
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

Common settings include keywords and exclusions, arXiv categories, RSS URLs, per-category result limits, report language, and lookback days. See the [AI Algorithms example](tracks/research/ai-algorithm.yaml), [Startup example](tracks/venture/entrepreneur.yaml), and [AI Tools example](tracks/builder/ai-tools.yaml).

After configuring the track, add it to `active_tracks`, then return to B3 and run Actions. It affects only your own fork and does not change the official website.

#### B5 · 📡 Configure Additional Sources

Enable a source under the track's `sources`, then add its matching configuration block. Start with public sources when possible: arXiv, Hugging Face, RSS, GitHub, and Hacker News require no login, API key, OpenCLI, or Browser Bridge.

Example RSS configuration:

```yaml
sources:
  - arxiv
  - rss
  - github

rss_feeds:
  - https://huggingface.co/blog/feed.xml
  - https://blog.research.google/feeds/posts/default
  - https://openai.com/news/rss.xml
rss_days: 21
```

**Twitter / X: Run GitHub Actions with Apify**

Add `APIFY_TOKEN` under **Settings → Secrets and variables → Actions** in your fork, then configure:

```yaml
sources:
  - twitter

twitter:
  mode: apify
  queries: ["AI agent", "LLM tool"]
  handles: [OpenAI, AnthropicAI]
  max_results: 50
```

Apify usually offers a free quota and may charge for usage beyond it. It does not require Chrome, Browser Bridge, or OpenCLI. See [Twitter/X setup](docs/twitter-setup.md) for every field. You can also use OpenCLI to reuse a local Chrome login, but that is not the recommended path for GitHub Actions.

**Xiaohongshu / Zhihu: Local OpenCLI Only**

These sources require [OpenCLI](https://github.com/jackwener/OpenCLI), Browser Bridge, and a Chrome session logged into the corresponding websites. A standard GitHub Actions runner cannot access your browser. First, copy the example:

**macOS / Linux**

```bash
cp examples/tracks/xiaohongshu-radar.yaml tracks/builder/my-social-radar.yaml
```

Check OpenCLI first:

```bash
opencli doctor
opencli xiaohongshu user USER_ID --limit 3 -f json
opencli zhihu user-articles USER_NAME --limit 3 -f json
opencli zhihu user-answers USER_NAME --limit 3 -f json
```

If macOS reports `Unable to find application named 'OpenCLIApp'`, the problem is not your login. The system `opencli` launcher failed to start the background process. Use the runtime bundled with the app directly:

```bash
env -u OPENCLI_DAEMON_PORT \
  /Applications/OpenCLIApp.app/Contents/Resources/node_modules/node/bin/node \
  /Applications/OpenCLIApp.app/Contents/Resources/node_modules/@jackwener/opencli/dist/src/main.js \
  doctor
```

After that succeeds, tell OmniSource to use this command in the same terminal:

```bash
export OPENCLI_COMMAND='env -u OPENCLI_DAEMON_PORT /Applications/OpenCLIApp.app/Contents/Resources/node_modules/node/bin/node /Applications/OpenCLIApp.app/Contents/Resources/node_modules/@jackwener/opencli/dist/src/main.js'
uv run omnisource run --track builder/my-social-radar
```

**Windows PowerShell**

```powershell
Copy-Item examples/tracks/xiaohongshu-radar.yaml tracks/builder/my-social-radar.yaml
opencli doctor
opencli xiaohongshu user USER_ID --limit 3 -f json
opencli zhihu user-articles USER_NAME --limit 3 -f json
opencli zhihu user-answers USER_NAME --limit 3 -f json
```

Do not copy the macOS path on Windows. If `opencli doctor` reports `Daemon: running` and `Extension: connected`, use `opencli` directly.

In short, a green Browser Bridge only means the browser extension is ready; OmniSource also needs the OpenCLI background daemon. The macOS `opencli` launcher sometimes fails to start that daemon, which is when the bundled app runtime above is needed. Logging into Xiaohongshu and Zhihu is not the cause of this error.

Replace the example author names and `USER_ID` with real values, then follow [Xiaohongshu setup](docs/xiaohongshu-setup.md) and [customization instructions](docs/customizing-your-radar.md) to add the Zhihu fields. Public sources and Apify do not require OpenCLI.

Note: OpenCLI 1.8.5 may occasionally return `Navigation rejected` when running Zhihu `user-articles` directly. This does not mean the login failed. OmniSource catches the error and falls back to reading Zhihu through the browser session. To test OmniSource's own Zhihu source, run this in a terminal where `OPENCLI_COMMAND` is already set:

```bash
uv run python -c 'from omnisource.sources.zhihu import ZhihuSource; rows=ZhihuSource().fetch({"days":30,"zhihu":{"creators":[{"user":"USER_NAME","articles":True,"answers":True}]}}); print(f"zhihu_signals={len(rows)}"); [print(x.title) for x in rows]'
```

#### B6 · 🧪 Optional: Validate Locally

To inspect collection, deduplication, and filtering before running Actions, use a local preview that does not call a model:

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

If a Markdown file appears under `reports/`, the basic configuration works. To create a GitHub Issue, run the corresponding workflow under **Actions**. Model-written reports use the keys configured in B2; X additionally uses `APIFY_TOKEN`.

The open-source package is responsible only for GitHub Issue reports in your fork, not the daily reports, weekly reports, or email subscriptions on the official website. Each track records what it has already published: daily reports do not repeat previous daily items, and weekly reports do not repeat previous weekly items. Use `--no-memory` only for debugging when you intentionally want to disable this protection.

GitHub Actions stores `data/memory.db` in the repository's Actions cache, so deduplication continues across runs. Daily and weekly reports share the same database but use separate memory scopes. If you manually clear the Actions cache, older items may appear again in the next run.

#### B7 · 🎯 Teach Reports Your Preferences

Every item in a GitHub Issue report generated by your fork provides four feedback actions:

- **Like**: boost similar topics, keywords, and authors in later reports;
- **Ignore**: never recommend this item again, even if the memory cache is lost;
- **Less like this**: lower the future ranking of similar topics and keywords;
- **Follow author**: let new work by this author pass the normal keyword threshold and receive a ranking boost.

Clicking an action opens a prefilled feedback Issue for you to confirm and submit. During the next daily or weekly run, the workflow imports structured feedback created only by the repository owner, then applies it to deterministic filtering, ranking, and LLM recommendation decisions.

For a fork owned by an organization, set `OMNISOURCE_FEEDBACK_OWNER` in Actions Variables to the GitHub username whose feedback may be learned. For local runs, use the CLI:

```bash
omnisource feedback --action like --track research/ai-algorithm \
  --item-id 2607.12345 --item-type paper --title "Example paper" \
  --keywords "reasoning,agent"

omnisource feedback --action follow-author --track research/ai-algorithm \
  --author "Example Researcher"
```

## 🧱 Code Structure

The open-source directory follows the collection → filtering → publishing flow:

~~~text
omnisource/              core pipeline and CLI
├── sources/             source adapters
├── agents/              collection, filtering, analysis, and editing
├── ranking/             ranking and scoring
├── publishers/          Markdown and GitHub Issue publishing
├── llm/                 model provider adapters
└── main.py              pipeline orchestration
tracks/                  YAML topics grouped by audience
├── research/            research topics for researchers
├── venture/             startup intelligence for entrepreneurs
└── builder/             tools and engineering topics for community developers
examples/                copyable tracks and sample reports
.github/workflows/       daily and weekly GitHub Issue workflows
tests/                   public-core tests
~~~

In most cases, you only need to edit `tracks/<audience>/` and `omnisource.yaml`. Modify `omnisource/` only when adding a new source or publishing method.

## 🧭 FAQ

### 📨 Actions Succeeds but No Issue Appears

Check two things:

1. **Issues** is enabled for the repository.
2. The workflow file still grants the permissions required to create Issues. The current configuration uses the GITHUB_TOKEN automatically provided by GitHub Actions.

### 🔐 `invalid_api_key` Error

Check that:

- The secret name is exactly correct;
- The API key was copied in full;
- A gateway uses `OPENAI_COMPATIBLE_API_KEY` and `OPENAI_COMPATIBLE_BASE_URL`;
- The Base URL matches the endpoint required by the gateway and usually includes `/v1`;
- The model configured in the track is supported by the gateway.

### 🌐 Will Customizing My Report Affect the Official Website?

No.

Your fork affects only your own GitHub Issue reports. The official website uses content and configuration maintained separately by the project team and runs independently from user forks.

## License

This project is licensed under the [PolyForm Noncommercial License 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/).

## Authors

Jiaqi Lang<sup>*</sup>, Wangbo Zhao, Pengfei Zhou, Run Liu, Bin Xv, Yixing Ma, Weidong Tang

*Corresponding author: Jiaqi Lang · lang.jiaqi@u.nus.edu*

## Interested in World Models?

Some of this project's authors are also independently exploring startup opportunities in world models.

**Wangbo Zhao** ([Google Scholar](https://scholar.google.com.hk/citations?user=aocj89kAAAAJ&hl=en), [email](mailto:wangbo.zhao96@gmail.com)) is building an early-stage company focused on world models and the infrastructure needed to develop and scale them. The company is currently raising a seed round and welcomes conversations with investors and strategic partners interested in this direction.

**Pengfei Zhou** ([lance@infrec.tech](mailto:lance@infrec.tech)) is the founder of a startup focused on scaling world models with real-world, long-horizon trajectory data. The company is building generally intelligent systems that can understand, predict, and ultimately interact with human environments and the real world. Visit the [company website](https://www.cardinal-agi.com/) for more information.

These startup projects are independent of this project and of one another.
