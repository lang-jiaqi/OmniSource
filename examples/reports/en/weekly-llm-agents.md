# OmniSource Weekly — LLM Agents

*2026-06-24 · 18 signals · English sample*

# 📄 Papers

### tool use / function calling

## 1. S-Agent: Spatial Tool-Use Elicits Reasoning for Spatial Intelligence

- **Authors:** Yalun Dai, Hao Li, Shulin Tian, Runmao Yao, Yuhao Dong et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-18  ·  via hf_papers  ·  👍 39**
- **Link:** https://arxiv.org/abs/2606.20515  ·  **Code:** https://github.com/Ropedia/S-Agent

**Why it matters:** We introduce \textsc{S-Agent}, a spatial tool-use agentic paradigm for understanding and reasoning over continuous multi-view images and videos.

**Key idea:** Real-world spatial intelligence requires reasoning over a continuous and evolving 3D world, yet existing VLMs and tool-augmented agents largely remain tied to static, stateless inference from isolated visual observations.

## 2. ENPIRE: Agentic Robot Policy Self-Improvement in the Real World

- **Authors:** Wenli Xiao, Jia Xie, Tonghe Zhang, Haotian Lin, Letian "Max" Fu et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-18  ·  via hf_papers  ·  👍 11**
- **Link:** https://arxiv.org/abs/2606.19980

**Why it matters:** Although emerging coding agents can generate code to automate algorithm search, their successes remain largely confined in digital environments.

**Key idea:** Achieving dexterous robotic manipulation in the real world heavily relies on human supervision and algorithm engineering, which becomes a central bottleneck in the pursuit of general physical intelligence.

## 3. GRADE: Graph Representation of LLM Agent Dependency and Execution

- **Authors:** Yue Zhao
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.22741v1

**Why it matters:** A trace records what each step did, never what it relied on, the state it read, and the results it reused.

**Key idea:** Can one graph represent every kind of LLM agent's run?

### agent evaluation / benchmarks

## 4. DailyReport: An Open-ended Benchmark for Evaluating Search Agents on Daily Search Tasks

- **Authors:** Jingxuan Han, Wei Liu, Mingyang Zhu, Youpeng Wang, Ziwen Wang et al.
- **priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-11  ·  via hf_papers  ·  👍 8**
- **Link:** https://arxiv.org/abs/2606.12871  ·  **Code:** https://github.com/AGI-Eval-Official/DailyReport

**Why it matters:** For SAs evaluation, prior benchmarks mainly focus on specialized tasks that are unlikely to arise in real-world user scenarios.

**Key idea:** Search Agents (SAs) typically leverage large language models (LLMs) to support complex information-seeking tasks by autonomously exploring web sources and synthesizing information into comprehensive responses.

## 5. Beyond Static Leaderboards: Predictive Validity for the Evaluation of LLM Agents

- **Authors:** Dhaval C. Patel, Kaoutar El Maghraoui, Shuxin Lin, Yusheng Li, Tianjun Feng et al.
- **priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-18  ·  via hf_papers  ·  👍 39**
- **Link:** https://arxiv.org/abs/2606.19704

**Why it matters:** This paper aggregates the largest coordinated deep-dive of one MCP-based industrial-agent benchmark to date: fourteen parallel implementation studies covering new asset classes (including a multi-modal visual extension), alternative orchestrations, retrieval strategies, reasoning modes, infrastructure optimizations, and evaluation-methodology probes.

**Key idea:** Agent benchmarks are growing fast, but no single benchmark touches more than four or five of the dimensions that deployment exposes.

### reasoning / planning

## 6. PlanBench-XL: Evaluating Long-Horizon Planning of LLM Tool-Use Agents in Large-Scale Tool Ecosystems

- **Authors:** Jiayu Liu, Qihan Lin, Cheng Qian, Rui Wang, Emre Can Acikgoz et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-21  ·  via hf_papers  ·  👍 76**
- **Link:** https://arxiv.org/abs/2606.22388  ·  **Code:** https://github.com/JiayuJeff/PlanBench-XL

**Why it matters:** However, existing benchmarks rarely evaluate planning under retrieval-limited tool visibility.

**Key idea:** LLM agents increasingly operate in large tool ecosystems, where real-world tasks require discovering relevant tools, inferring implicit sub-goals, and adapting to dynamic environments over long horizons.

## 7. Context-Aware RL for Agentic and Multimodal LLMs

- **Authors:** Peiyang Xu, Bangzheng Li, Sijia Liu, Karthik R. Narasimhan, Pramod Viswanath et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-15  ·  via hf_papers  ·  👍 15**
- **Link:** https://arxiv.org/abs/2606.17053  ·  **Code:** https://github.com/xupy2003/ContextAwareRL

**Why it matters:** We propose ContextRL, a context-aware reinforcement learning (RL) method that improves long-horizon reasoning and multimodal performance through an indirect auxiliary objective.

**Key idea:** Large language models (LLMs) often fail when answering requires identifying a small but decisive piece of evidence within a long or complex context, such as a single line in a tool trace or a subtle detail in an image.

### multi-agent systems

## 8. Deep Research in Physical Sciences: A Multi-Agent Framework and Comprehensive Benchmark

- **Authors:** Yigeng Jiang, Tengchao Yang, Taoyong Cui, Jiaxing Wan, Yuan Wang et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-17  ·  via hf_papers  ·  👍 12**
- **Link:** https://arxiv.org/abs/2606.18648  ·  **Code:** https://github.com/yigengjiang/physci-deepresearch

**Why it matters:** However, comprehensive and in-depth evaluations of their capabilities within this domain remain lacking.

**Key idea:** Deep research agents are Large Language Model (LLM)-based systems designed for autonomous, multi-step scientific reasoning, and they hold immense potential for accelerating research in the physical sciences.

# 💻 Repositories

### tool use / function calling

## 1. anthropics/claude-code

- **Authors:** anthropics
- **priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-22  ·  via github  ·  👍 133949**
- **Link:** https://github.com/anthropics/claude-code  ·  **Code:** https://github.com/anthropics/claude-code

**Why it matters:** For LLM Agents readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** Claude Code is an agentic coding tool that lives in your terminal, understands your codebase, and helps you code faster by executing routine tasks, explaining complex code, and handling git workflows - all through natural language commands.

## 2. langflow-ai/langflow

- **Authors:** langflow-ai
- **priority medium  ·  rel 0.80  ·  nov 0.60  ·  2026-06-23  ·  via github  ·  👍 149978**
- **Link:** https://github.com/langflow-ai/langflow  ·  **Code:** https://github.com/langflow-ai/langflow

**Why it matters:** For LLM Agents readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** Langflow is a powerful tool for building and deploying AI-powered agents and workflows.

## 3. langgenius/dify

- **Authors:** langgenius
- **priority medium  ·  rel 0.80  ·  nov 0.60  ·  2026-06-23  ·  via github  ·  👍 146290**
- **Link:** https://github.com/langgenius/dify  ·  **Code:** https://github.com/langgenius/dify

**Why it matters:** For LLM Agents readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** Production-ready platform for agentic workflow development.

### multi-agent systems

## 4. TauricResearch/TradingAgents

- **Authors:** TauricResearch
- **priority high  ·  rel 0.90  ·  nov 0.80  ·  2026-06-22  ·  via github  ·  👍 88154**
- **Link:** https://github.com/TauricResearch/TradingAgents  ·  **Code:** https://github.com/TauricResearch/TradingAgents

**Why it matters:** For LLM Agents readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** TradingAgents: Multi-Agents LLM Financial Trading Framework

## 5. obra/superpowers

- **Authors:** obra
- **priority medium  ·  rel 0.60  ·  nov 0.50  ·  2026-06-23  ·  via github  ·  👍 236770**
- **Link:** https://github.com/obra/superpowers  ·  **Code:** https://github.com/obra/superpowers

**Why it matters:** For LLM Agents readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** An agentic skills framework & software development methodology that works.

# 📝 Lab Notes

### tool use / function calling

## 1. Agentic Resource Discovery: Let agents search

- **priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-17  ·  via rss**
- **Link:** https://huggingface.co/blog/agentic-resource-discovery-launch

**Why it matters:** For LLM Agents readers, this post captures a timely lab or engineering signal worth tracking.

**Key idea:** Agentic Resource Discovery: Let agents search is surfaced as a relevant blog signal for this track.

## 2. Is it agentic enough? Benchmarking open models on your own tooling

- **priority high  ·  rel 1.00  ·  nov 0.70  ·  2026-06-18  ·  via rss**
- **Link:** https://huggingface.co/blog/is-it-agentic-enough

**Why it matters:** For LLM Agents readers, this post captures a timely lab or engineering signal worth tracking.

**Key idea:** Is it agentic enough? Benchmarking open models on your own tooling is surfaced as a relevant blog signal for this track.

## 3. Build real agentic apps using CUGA: two dozen working examples on a lightweight harness

- **priority high  ·  rel 0.90  ·  nov 0.80  ·  2026-06-23  ·  via rss**
- **Link:** https://huggingface.co/blog/ibm-research/cuga-apps

**Why it matters:** For LLM Agents readers, this post captures a timely lab or engineering signal worth tracking.

**Key idea:** Build real agentic apps using CUGA: two dozen working examples on a lightweight harness is surfaced as a relevant blog signal for this track.

### agent safety / robustness

## 4. MosaicLeaks: Can your research agent keep a secret?

- **priority medium  ·  rel 0.80  ·  nov 0.70  ·  2026-06-18  ·  via rss**
- **Link:** https://huggingface.co/blog/ServiceNow/mosaicleaks

**Why it matters:** For LLM Agents readers, this post captures a timely lab or engineering signal worth tracking.

**Key idea:** MosaicLeaks: Can your research agent keep a secret? is surfaced as a relevant blog signal for this track.

### multi-agent systems

## 5. The Open Source Community is backing OpenEnv for Agentic RL

- **priority medium  ·  rel 0.80  ·  nov 0.70  ·  2026-06-08  ·  via rss**
- **Link:** https://huggingface.co/blog/openenv-agentic-rl

**Why it matters:** For LLM Agents readers, this post captures a timely lab or engineering signal worth tracking.

**Key idea:** The Open Source Community is backing OpenEnv for Agentic RL is surfaced as a relevant blog signal for this track.
