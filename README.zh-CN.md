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
  <a href="README.md">English</a>
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

### Step 0 · 🧰 准备环境

在终端确认环境：

```bash
python3 --version   # 需要 3.11+
uv --version
git --version
```

如果没有 `uv`，安装：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows PowerShell：

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

另外需要一个 GitHub 账号，用来 Fork 仓库和接收 Issues。

### Step 1 · 🍴 Fork 仓库

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

### Step 2 · 🔑 配置模型

在 **Settings → Secrets and variables → Actions** 添加密钥；模型写在 track 的 `llm` 部分：

| 用途 | 推荐模型示例 |
|---|---|
| 信息收集、摘要、日常报告 | OpenAI `gpt-4.1-mini` · Gemini `gemini-2.5-flash` · Qwen `qwen-plus` |
| 更强的推理、筛选和判断 | OpenAI `o3-mini` · Gemini `gemini-2.5-pro` · Qwen `qwen-max` |

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

密钥名称固定使用 `OPENAI_COMPATIBLE_API_KEY`；模型名和 Base URL 以服务商文档为准。GitHub Actions 会自动提供你自己的 Fork 创建 Issue 所需的 `GITHUB_TOKEN`。主仓库使用 `OMNISOURCE_ISSUE_TOKEN` 将报告发布到 `lang-jiaqi/OmniSource-workspace`。

如果 track 使用 Anthropic，添加 `ANTHROPIC_API_KEY`；如果使用 Reddit 的 OAuth 模式，再添加 `REDDIT_CLIENT_ID` 和 `REDDIT_CLIENT_SECRET`。这些都是可选项，不用的来源不需要配置。

### Step 3 · ⚡ 快速启动：使用现有 track

如果你想先看一份报告，不需要创建或修改 YAML。只要在
[omnisource.yaml](omnisource.yaml) 的 `active_tracks` 中保留已有方向：

```yaml
active_tracks:
  - research/ai-algorithm
  - venture/entrepreneur
```

保存后打开 **Actions → Daily GitHub Issue Report → Run workflow**。每个 active track
会生成一份独立的 GitHub Issue；也可以运行 **Weekly GitHub Issue Report** 生成周报。

这条路径适合第一次使用：只需要完成 Step 0–2，然后直接运行 Actions。已有示例包括 [AI 算法](tracks/research/ai-algorithm.yaml)、[创业信息](tracks/venture/entrepreneur.yaml) 和 [AI 工具](tracks/builder/ai-tools.yaml)。

### Step 4 · 🛠️ 个性化配置：创建自己的 track

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

配置完成后，把新 track 加入 `active_tracks`，再回到 Step 3 运行 Actions。它只会影响你自己的 Fork，不会改变官方网站。

### Step 5 · 📡 选择信息源

信息源统一写在 track 顶层的 `sources:` 列表里。第一次使用建议只用公开来源：
不需要额外账号、Token、Chrome 或 OpenCLI。

打开 Step 4 中复制出来的 track 文件，把原来的整个 `sources:` 块替换成：

```yaml
sources:
  - arxiv
  - hf_papers
  - rss
  - github
  - hackernews
```

保留原文件里的 `categories`、`keywords`、`llm` 和 `output`。其中 `arxiv` 需要
`categories`；已有示例都已经写好。`hf_papers` 和 `hackernews` 不需要单独的配置块。

#### RSS 信息源

RSS 配置写在同一个 track 文件的顶层，不要放在 `rss:` 下面。把已有 RSS 配置替换为：

```yaml
rss_feeds:
  - https://huggingface.co/blog/feed.xml
  - https://blog.research.google/feeds/posts/default
  - https://openai.com/news/rss.xml
rss_days: 21
```

其他公开来源也不需要 Token。需要时，把名称加入上面的 `sources:`：

```yaml
sources:
  - arxiv
  - hf_papers
  - rss
  - github
  - hackernews
  - blogrxiv
```

可选调整项：

```yaml
hf_limit: 100
hn_query: "AI agent OR foundation model"
hn_top: 50
blogrxiv_days: 1
github_query: "AI agent OR foundation model"
```

#### Twitter / X：在 GitHub Actions 中使用

在 Fork 仓库中打开 **Settings → Secrets and variables → Actions → New repository secret**，添加：

```text
Name: APIFY_TOKEN
Secret: 在这里粘贴 Apify Token
```

不要把 Token 写进 YAML，也不要提交到 GitHub。然后把 track 的来源列表替换为下面这个版本，
或者只把 `twitter` 这一行加入你现有的列表：

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

Apify 不需要 Chrome、Browser Bridge 或 OpenCLI；免费额度用完后可能收费。完整字段见
[Twitter/X 配置](docs/twitter-setup.md)。

#### 小红书 / 知乎：仅在本地电脑运行

这两个来源通过 [OpenCLI](https://github.com/jackwener/OpenCLI) 使用 Chrome 中已经登录的账号，
普通 GitHub Actions runner 无法访问你的浏览器。如果只想让 GitHub Actions 自动发 Issue，跳过本节。

安装 OpenCLI 和 Browser Bridge，在 Chrome 登录对应网站，然后检查连接：

```bash
opencli doctor
opencli xiaohongshu user USER_ID --limit 3 -f json
opencli zhihu user-articles USER_NAME --limit 3 -f json
opencli zhihu user-answers USER_NAME --limit 3 -f json
```

本地 track 加入下面的来源，并把占位符替换成真实信息：

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
    - name: "博主名称"
      user_id: "USER_ID"

zhihu:
  enabled: true
  command: opencli
  timezone: Asia/Shanghai
  days: 7
  max_items_per_creator: 20
  creators:
    - name: "知乎用户"
      user: "USER_NAME"
      articles: true
      answers: true
```

然后在本地运行：

```bash
uv run omnisource run --track builder/my-social-radar
```

Windows PowerShell 也使用相同的 `opencli` 命令。如果 macOS 出现
`Unable to find application named 'OpenCLIApp'`，按 [小红书配置](docs/xiaohongshu-setup.md) 中的
内置 runtime 步骤操作；知乎字段说明见[自定义配置说明](docs/customizing-your-radar.md)。

#### Reddit

Reddit 有两种模式：本地 Chrome 使用 `mode: opencli`；GitHub Actions 使用 `mode: oauth`，
需要先创建 Reddit application，再添加 `REDDIT_CLIENT_ID` 和 `REDDIT_CLIENT_SECRET` 两个
Secret，并加入下面的配置：

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

本地 OpenCLI 配置和 Reddit application 的详细步骤见 [Reddit 配置](docs/reddit-setup.md)。

### Step 6 · 🧪 可选：本地验证

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

如果 `reports/` 中出现 Markdown 文件，说明基础配置已经跑通。正式生成 GitHub Issue 时，在 **Actions** 中运行对应 workflow；模型报告会使用 Step 2 配置的密钥，X 使用 `apify` 模式时才需要额外配置 `APIFY_TOKEN`。

开源版本只负责你 Fork 后的 GitHub Issue 报告，不负责官网日报、周报或邮箱订阅。每个 track 会记录已经发布的内容：日报不会重复之前的日报，周报也不会重复之前的周报；`--no-memory` 仅用于调试，会暂时关闭这项保护。

GitHub Actions 会用仓库缓存保存 `data/memory.db`，所以跨次运行也能继续去重；日报和周报共享同一份记忆库，但使用不同的记忆范围。如果你手动清空 Actions cache，下一次运行可能重新出现较早内容。

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
2. workflow 文件中保留了创建 Issue 所需的权限。Fork 使用 GitHub Actions 自动提供的 `GITHUB_TOKEN`；主仓库还需要配置用于独立 Issue 目标仓库的 `OMNISOURCE_ISSUE_TOKEN` Secret。

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

*Corresponding author: Jiaqi Lang · National University of Singapore (NUS) · lang.jiaqi@u.nus.edu*

## 对世界模型感兴趣？

本项目作者也在独立探索世界模型方向的创业机会。

- **Wangbo Zhao** ([Google Scholar](https://scholar.google.com.hk/citations?user=aocj89kAAAAJ&hl=zh-CN), [email](mailto:wangbo.zhao96@gmail.com))  正在筹备一个专注于世界模型及其基础设施建设的早期创业项目，目前正在进行种子轮融资。欢迎对该方向感兴趣的投资者和战略合作伙伴联系交流。

- **Pengfei Zhou** ([lance@infrec.tech](mailto:lance@infrec.tech)) 是一家独立创业公司的创始人，该公司专注于世界模型与智能体游戏开发。公司致力于构建具备通用智能能力的系统，使其能够理解、预测，并最终与人类环境和真实世界进行交互。更多信息请访问：[company website](https://www.cardinal-agi.com)。

上述创业项目均独立于本项目，且彼此之间不存在关联。
