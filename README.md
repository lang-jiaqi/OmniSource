<div align="center">

<h1>🔭 OmniSource</h1>

<p>
  <strong>联结全域时代信号，与科研者、创变者、开发者共探 AI 世界的无限可能</strong><br>
   ☘️三重信息流通道：科研日报｜创业市场雷达｜开发者工具周刊
</p>

<p>
  <img src="https://img.shields.io/badge/license-PolyForm%20Noncommercial-8bd3a8?style=for-the-badge" alt="PolyForm Noncommercial License">
  <img src="https://img.shields.io/badge/Python-3.11%2B-8ab4f4?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/built%20with-uv-b39ddb?style=for-the-badge&logo=uv&logoColor=white" alt="Built with uv">
  <img src="https://img.shields.io/badge/GitHub%20Issues-ready-24292f?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Issues ready">
  <img src="https://img.shields.io/badge/PRs-welcome-f4c95d?style=for-the-badge&logo=github&logoColor=white" alt="PRs welcome">
</p>

<p>
  🌐 <a href="https://lang-jiaqi.github.io/omnisource-site/">访问 OmniSource 官网</a>
</p>

<p>
  <a href="https://lang-jiaqi.github.io/omnisource-site/report.html">科研报告</a> ·
  <a href="https://lang-jiaqi.github.io/omnisource-site/entrepreneur.html">创业信息流</a> ·
  <a href="https://lang-jiaqi.github.io/omnisource-site/tools.html">AI 工具雷达</a> ·
  <a href="README.en.md">English</a>
</p>

</div>

信息越来越多，真正值得关注的东西反而更难找到。OmniSource 从论文、技术博客、GitHub、行业媒体和社区中捕捉信号，去重、筛选、排序，最后交给你一份值得打开的报告。

你可以直接阅读官网的统一信息源，也可以 Fork 仓库，改写自己的关键词和来源，让专属报告自动发布到 GitHub Issues。📝

## 📬 两种使用方式

| 入口 | 适合谁 | 内容控制权 |
|---|---|---|
| [官方网站 🌐](https://lang-jiaqi.github.io/omnisource-site/) | 想直接阅读统一信息源的人 | 项目团队维护 |
| GitHub Issue 🧩 | 想 DIY 自己的信息流的人 | Fork 后自行修改 |

这个公开仓库只负责 GitHub Issue 这一种 DIY 方式。官网的日报、周报和邮箱订阅属于官方网站。

本地的 `reports/` 目录只保存 Markdown 文件，方便查看和调试。

## 🧭 三种自定义 track

你可以根据自己的身份，选择一种报告方向，再在 Fork 中继续修改：

| 类型 | 适合关注什么 | 官网对应入口 | 开源 YAML track |
|---|---|---|---|
| **研究者** 🔬 | 论文、研究方法、实验室动态、开源实现 | [科研报告](https://lang-jiaqi.github.io/omnisource-site/report.html) | [ai-algorithm.yaml](tracks/research/ai-algorithm.yaml) |
| **企业家** 🚀 | 融资、产品、市场、创始团队和招聘 | [创业信息流](https://lang-jiaqi.github.io/omnisource-site/entrepreneur.html) | [entrepreneur.yaml](tracks/venture/entrepreneur.yaml) |
| **社区开发者** 🧑‍💻 | AI 工具 | [AI 工具雷达](https://lang-jiaqi.github.io/omnisource-site/tools.html) | [ai-tools.yaml](tracks/builder/ai-tools.yaml) |

三种类型的本质是同一个：复制一个 track，改成你自己的关键词、来源和筛选标准，然后通过 GitHub Issue 查看自己的结果。目录名分别是 `research/`、`venture/` 和 `builder/`；科研目录里的每个 YAML 就是一个具体的 research domain。

官网和 OpenSource 使用同一套抓取、去重、相关性判断、质量筛选、排序和数量控制。OpenSource 可以自由增加或替换 sources，但新增来源只会扩大候选池，仍然必须经过同样的精选机制；官网只是使用项目团队维护的官方 sources。

其中 AI 工具 track 还会统一使用六项评分：相关性、实用价值、新鲜度、可用性、可信度、差异化。

## 🚀 快速开始

先根据你的目的选择入口：

| 方式 | 适合谁 | 结果 |
|---|---|---|
| **下载 Release** | 想快速体验、直接使用内置 track | 在本地生成 Markdown 和 JSONL 报告，支持完整 LLM 分析 |
| **Fork 仓库** | 想修改关注方向、定时运行或生成 GitHub Issues | 获得自己的配置、Actions 和长期记忆 |

### 方式 A · 下载 Release，直接体验

需要 Python 3.11+ 和 `uv`。如果没有 `uv`：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows PowerShell：

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

安装 `v0.1.1` wheel（二选一）：

```bash
# 推荐：作为独立 CLI 安装
uv tool install https://github.com/lang-jiaqi/OmniSource/releases/download/v0.1.1/omnisource-0.1.1-py3-none-any.whl

# 或者：在已经激活的虚拟环境中安装
python -m pip install https://github.com/lang-jiaqi/OmniSource/releases/download/v0.1.1/omnisource-0.1.1-py3-none-any.whl
```

如果使用 `uv` 后终端提示找不到 `omnisource`，运行 `uv tool update-shell`，
然后重新打开终端。

先查看内置 track，再做一次不调用模型的预览：

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

报告会写入当前目录的 `reports/`。Release 完整支持 LLM；配置默认 OpenAI
track 所需的 Key 后，去掉 `--no-llm` 即可。在当前目录新建 `.env`：

```dotenv
OPENAI_API_KEY=你的_OpenAI_API_Key
```

然后运行：

```bash
omnisource run --track research/ai-algorithm
```

这条路径适合使用内置 track。要修改 track、接入 GitHub Actions 或定时生成
Issues，请使用下面的 Fork 路径。

### 方式 B · Fork 仓库，自定义并长期运行

需要 GitHub 账号和 Git；如需本地运行，还需要 Python 3.11+ 和 `uv`。Fork 后，
你可以修改 track，并让 Actions 自动生成日报和周报。

#### B1 · 🍴 Fork 并克隆仓库

点击 GitHub 右上角 **Fork**，然后在自己的 Fork 中打开 **Issues** 和 **Actions**。
如果要在本地修改 track，再把自己的 Fork 克隆下来：

**macOS / Linux**

```bash
git clone https://github.com/你的用户名/OmniSource.git && cd OmniSource
```

**Windows PowerShell**

```powershell
git clone https://github.com/你的用户名/OmniSource.git
Set-Location OmniSource
```

#### B2 · 🔑 配置模型

在 **Settings → Secrets and variables → Actions** 添加密钥；模型写在 track 的 `llm` 部分：

| 用途 | 推荐模型示例 |
|---|---|
| 信息收集、摘要、日常报告 | OpenAI `gpt-4.1-mini` · Gemini `gemini-2.5-flash` · Qwen `qwen-plus` |
| 更强的推理、筛选和判断 | OpenAI `o3-mini` · Gemini `gemini-2.5-pro` · Qwen `qwen-max` |

公开内置 track 默认使用 OpenAI `gpt-4.1-mini`。如果使用 Gemini、Qwen
或自建网关，请同时修改 track 中的 `provider`、`model`，并配置对应的兼容接口。

OpenAI 官方接口：

~~~
OPENAI_API_KEY=你的 OpenAI API key
~~~

Gemini、Qwen 或中转站使用 OpenAI-compatible 接口：

~~~
OPENAI_COMPATIBLE_API_KEY=你的 Gemini / Qwen / 中转站 key
OPENAI_COMPATIBLE_BASE_URL=https://对应服务的兼容接口/v1
~~~

track 中对应填写：

~~~yaml
llm:
  provider: openai                 # OpenAI 官方
  model: gpt-4.1-mini
~~~

Gemini、Qwen 和中转站：

~~~yaml
llm:
  provider: openai_compatible
  model: gemini-2.5-flash       # 或 qwen-plus、服务商支持的其他模型
~~~

密钥名称固定使用 `OPENAI_COMPATIBLE_API_KEY`；模型名和 Base URL 以服务商文档为准。GitHub Actions 创建 Issue 所需的 `GITHUB_TOKEN` 会自动提供。

如果想让所有 Actions track 统一使用中转接口，不必逐个修改 YAML；在
**Settings → Secrets and variables → Actions → Variables** 添加：

~~~
OMNISOURCE_LLM_PROVIDER=openai_compatible
OMNISOURCE_LLM_MODEL=中转站支持的模型名
~~~

如果 track 使用 Anthropic，添加 `ANTHROPIC_API_KEY`；如果使用 Reddit 的 OAuth 模式，再添加 `REDDIT_CLIENT_ID` 和 `REDDIT_CLIENT_SECRET`。这些都是可选项，不用的来源不需要配置。

#### B3 · ⚡ 快速启动：使用现有 track

如果你想先看一份报告，不需要创建或修改 YAML。只要在
[omnisource.yaml](omnisource.yaml) 的 `active_tracks` 中保留已有方向：

```yaml
active_tracks:
  - research/ai-algorithm
  - venture/entrepreneur
```

保存后打开 **Actions → Daily GitHub Issue Report → Run workflow**。每个 active track
会生成一份独立的 GitHub Issue；也可以运行 **Weekly GitHub Issue Report** 生成周报。

这条路径适合长期使用：完成 B1–B2 后即可运行 Actions。已有示例包括 [AI 算法](tracks/research/ai-algorithm.yaml)、[创业信息](tracks/venture/entrepreneur.yaml) 和 [AI 工具](tracks/builder/ai-tools.yaml)。

#### B4 · 🛠️ 个性化配置：创建自己的 track

如果你想长期跟踪自己的主题，复制一个最接近的示例。每个名称都对应 `tracks/<类型>/` 下的一个 YAML 文件：

**macOS / Linux**

```bash
cp tracks/research/ai-algorithm.yaml tracks/research/my-radar.yaml
```

**Windows PowerShell**

```powershell
Copy-Item tracks/research/ai-algorithm.yaml tracks/research/my-radar.yaml
```

然后修改名称、来源、关键词和输出数量：

```yaml
name: my-radar
display_name: 我的关注方向
description: 我想长期跟踪的内容

sources:
  - arxiv
  - rss
  - github

keywords:
  - 你的关键词
  - another keyword

output:
  top_papers: 10
  top_repos: 5
  top_blogs: 5
  language: 中文
```

最后在 [omnisource.yaml](omnisource.yaml) 中加入它：

```yaml
active_tracks:
  - research/ai-algorithm
  - venture/entrepreneur
  - research/my-radar
```

常用的可调项：关键词与排除词、arXiv 分类、RSS 地址、每类保留数量、报告语言和回看天数。可参考 [AI 算法示例](tracks/research/ai-algorithm.yaml)、[创业示例](tracks/venture/entrepreneur.yaml) 和 [AI 工具示例](tracks/builder/ai-tools.yaml)。

配置完成后，把新 track 加入 `active_tracks`，再回到 B3 运行 Actions。它只会影响你自己的 Fork，不会改变官方网站。

#### B5 · 📡 配置额外信息源

在 track 的 `sources` 中打开来源，再填写对应配置块。建议先从公开来源开始：arXiv、Hugging Face、RSS、GitHub 和 Hacker News 都不需要登录、API key、OpenCLI 或 Browser Bridge。

RSS 的配置示例：

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

**Twitter / X：用 Apify 跑 GitHub Actions**

在 Fork 仓库的 **Settings → Secrets and variables → Actions** 添加 `APIFY_TOKEN`，然后写入：

```yaml
sources:
  - twitter

twitter:
  mode: apify
  queries: ["AI agent", "LLM tool"]
  handles: [OpenAI, AnthropicAI]
  max_results: 50
```

Apify 通常有免费额度，超出后可能收费；它不需要 Chrome、Browser Bridge 或 OpenCLI。完整字段见 [Twitter/X 配置](docs/twitter-setup.md)。如果只在本地复用 Chrome 登录状态，也可以使用 OpenCLI，但这不是 GitHub Actions 的推荐路径。

**小红书 / 知乎：仅适合本地 OpenCLI**

这两个来源需要安装 [OpenCLI](https://github.com/jackwener/OpenCLI) 和 Browser Bridge，并在 Chrome 登录对应网站；普通 GitHub Actions runner 访问不到你的浏览器。先复制示例：

**macOS / Linux**

```bash
cp examples/tracks/xiaohongshu-radar.yaml tracks/builder/my-social-radar.yaml
```

先检查 OpenCLI：

```bash
opencli doctor
opencli xiaohongshu user USER_ID --limit 3 -f json
opencli zhihu user-articles USER_NAME --limit 3 -f json
opencli zhihu user-answers USER_NAME --limit 3 -f json
```

如果 macOS 出现 `Unable to find application named 'OpenCLIApp'`，不是账号没登录，而是
系统里的 `opencli` 启动器没有成功拉起后台程序。直接使用 App 内置 runtime：

```bash
env -u OPENCLI_DAEMON_PORT \
  /Applications/OpenCLIApp.app/Contents/Resources/node_modules/node/bin/node \
  /Applications/OpenCLIApp.app/Contents/Resources/node_modules/@jackwener/opencli/dist/src/main.js \
  doctor
```

验证成功后，在同一个终端告诉 OmniSource 使用这个命令：

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

Windows 不要复制上面的 macOS 路径。Windows 如果 `opencli doctor` 能显示
`Daemon: running` 和 `Extension: connected`，直接使用 `opencli` 即可。

简单来说：绿色的 Browser Bridge 只代表浏览器扩展已准备好；OmniSource 还需要
OpenCLI 的后台 daemon。macOS 的 `opencli` 启动器有时拉不起 daemon，才需要上面的
App 内置 runtime。登录小红书和知乎本身不是这次报错的原因。

把示例中的作者名称和 `USER_ID` 替换成真实信息，再按 [小红书配置](docs/xiaohongshu-setup.md) 和 [自定义配置说明](docs/customizing-your-radar.md) 补充知乎字段。公开来源和 Apify 不需要安装 OpenCLI。

提示：OpenCLI 1.8.5 直接运行知乎 `user-articles` 时，偶尔会出现
`Navigation rejected`。这不是登录失败；OmniSource 会捕获这个错误，并使用浏览器会话
fallback 读取知乎内容。要验证 OmniSource 自己的知乎 source，请在已设置
`OPENCLI_COMMAND` 的终端运行：

```bash
uv run python -c 'from omnisource.sources.zhihu import ZhihuSource; rows=ZhihuSource().fetch({"days":30,"zhihu":{"creators":[{"user":"USER_NAME","articles":True,"answers":True}]}}); print(f"zhihu_signals={len(rows)}"); [print(x.title) for x in rows]'
```

#### B6 · 🧪 可选：本地验证

如果想在运行 Actions 前检查采集、去重和筛选，可以用不调用模型的命令进行本地预览：

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

如果 `reports/` 中出现 Markdown 文件，说明基础配置已经跑通。正式生成 GitHub Issue 时，在 **Actions** 中运行对应 workflow；模型报告会使用 B2 配置的密钥，X 则额外使用 `APIFY_TOKEN`。

开源版本只负责你 Fork 后的 GitHub Issue 报告，不负责官网日报、周报或邮箱订阅。每个 track 会记录已经发布的内容：日报不会重复之前的日报，周报也不会重复之前的周报；`--no-memory` 仅用于调试，会暂时关闭这项保护。

GitHub Actions 会用仓库缓存保存 `data/memory.db`，所以跨次运行也能继续去重；日报和周报共享同一份记忆库，但使用不同的记忆范围。如果你手动清空 Actions cache，下一次运行可能重新出现较早内容。

#### B7 · 🎯 让报告学习你的偏好

在 Fork 的 GitHub Issue 报告中，每条内容都会显示四类操作：

- **喜欢**：后续提升相似主题、关键词和作者内容；
- **忽略**：即使记忆缓存丢失，也不再推送这一条；
- **降低此类**：降低同类主题和关键词的后续排名；
- **关注作者**：作者的新内容可越过普通关键词门槛，并获得排名提升。

点击后 GitHub 会打开一条预填的反馈 Issue，由你确认提交。下一次日报或周报运行时，workflow 只会导入仓库所有者创建的结构化反馈，然后同时应用于确定性筛选、排名和 LLM 推荐判断。

组织名下的 Fork 可以在 Actions Variables 中设置 `OMNISOURCE_FEEDBACK_OWNER`，指定允许学习的 GitHub 用户名。本地运行可以使用 CLI：

```bash
omnisource feedback --action like --track research/ai-algorithm \
  --item-id 2607.12345 --item-type paper --title "Example paper" \
  --keywords "reasoning,agent"

omnisource feedback --action follow-author --track research/ai-algorithm \
  --author "Example Researcher"
```

## 🧱 代码结构

开源区的目录按“抓取 → 筛选 → 发布”的流程组织：

~~~text
omnisource/              核心 pipeline 和 CLI
├── sources/             各种信息源适配器
├── agents/              抓取、筛选、分析和编辑
├── ranking/             排序和评分
├── publishers/          Markdown 与 GitHub Issue 发布
├── llm/                 各类模型接口适配
└── main.py              pipeline 总编排
tracks/                  按 audience 分类的 YAML 关注方向
├── research/             研究者的科研方向
├── venture/              企业家的创业信息
└── builder/              社区开发者的工具与工程方向
examples/                可复制的 track 和示例报告
.github/workflows/       日报与周报 GitHub Issue workflow
tests/                   开源核心测试
~~~

通常只需要改 `tracks/<audience>/` 和 `omnisource.yaml`；只有要增加新来源或新发布方式时，才需要修改 `omnisource/`。

## 🧭 常见问题

### 📨 Actions 运行成功，但没有 Issue

确认两件事：

1. 仓库的 **Issues** 已开启。
2. workflow 文件中保留了创建 Issue 所需的权限。当前配置使用 GitHub Actions 自动提供的 GITHUB_TOKEN。

### 🔐 报错 invalid_api_key

检查：

- Secret 名称是否完全正确；
- API key 是否复制完整；
- 中转站是否使用 OPENAI_COMPATIBLE_API_KEY 和 OPENAI_COMPATIBLE_BASE_URL；
- Base URL 是否是中转站要求的 API 地址，通常需要包含 /v1；
- track 中配置的模型是否是中转站支持的模型。

### 🌐 我修改了自己的报告，会影响官方网站吗？

不会。

你的 Fork 只影响你自己的 GitHub Issue 报告。官方网站使用项目团队维护的独立内容和配置，和用户 Fork 分开运行。

## License

This project is licensed under the [PolyForm Noncommercial License 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/).

## Authors

Jiaqi Lang<sup>*</sup>, Wangbo Zhao, Pengfei Zhou, Run Liu, Bin Xv, Yixing Ma, weidong tang

*Corresponding author: Jiaqi Lang · lang.jiaqi@u.nus.edu*

## 对世界模型感兴趣？

本项目的作者也在各自独立探索世界模型领域的创业机会。

**Wangbo Zhao**（[Google Scholar](https://scholar.google.com.hk/citations?user=aocj89kAAAAJ&hl=zh-CN)，[邮箱](mailto:wangbo.zhao96@gmail.com)）目前正在创办一家早期创业公司，专注于世界模型及其开发与规模化所需的基础设施。公司目前正在进行种子轮融资，欢迎对这一方向感兴趣的投资者和战略合作伙伴联系交流。

**Pengfei Zhou**（[lance@infrec.tech](mailto:lance@infrec.tech)）是一家专注通过Real-World Long-Horizon Trajectory数据来Scaling世界模型的Start-up创始人。公司致力于构建具备通用智能的系统，使其能够理解、预测并最终与人类环境及现实世界进行交互。更多信息请访问[公司官网](https://www.cardinal-agi.com/)。

上述创业项目均独立于本项目，彼此之间亦相互独立。
