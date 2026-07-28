# OmniSource Weekly — llm-agents

*Week ending 2026-06-24 · 18 signals · sources: arxiv, hf_papers, rss, github*

## 本周主题分布

- **tool use / function calling** — 9
- **multi-agent systems** — 3
- **reasoning / planning** — 2
- **agent evaluation / benchmarks** — 2
- **other** — 1
- **agent safety / robustness** — 1

# 📄 论文

### tool use / function calling

## 1. S-Agent: Spatial Tool-Use Elicits Reasoning for Spatial Intelligence

- **Authors:** Yalun Dai, Hao Li, Shulin Tian, Runmao Yao, Yuhao Dong et al.
- **score 0.90  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-18  ·  via hf_papers  ·  👍 39**
- **Link:** https://arxiv.org/abs/2606.20515  ·  **Code:** https://github.com/Ropedia/S-Agent

**为什么值得看:** S-Agent introduces a novel approach to spatial reasoning and tool use in LLM agents, which is crucial for enhancing their capabilities in dynamic environments.

**核心思想:** S-Agent redefines spatial reasoning through spatio-temporal evidence accumulation and integrates a hierarchy of spatial tools for improved scene understanding.

## 2. ENPIRE: Agentic Robot Policy Self-Improvement in the Real World

- **Authors:** Wenli Xiao, Jia Xie, Tonghe Zhang, Haotian Lin, Letian "Max" Fu et al.
- **score 0.73  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-18  ·  via hf_papers  ·  👍 11**
- **Link:** https://arxiv.org/abs/2606.19980

**为什么值得看:** 这项研究展示了如何通过编码代理实现物理世界中的自主学习和工具使用，直接推动了LLM代理在现实应用中的发展。

**核心思想:** ENPIRE框架通过四个核心模块实现了物理反馈循环，从而使编码代理能够在现实世界中进行自主的策略改进。

## 3. GRADE: Graph Representation of LLM Agent Dependency and Execution

- **Authors:** Yue Zhao
- **score 0.70  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.22741v1

**为什么值得看:** 这项研究为LLM代理的执行和依赖关系提供了新的图形表示方法，有助于理解和优化其工具使用和推理能力。

**核心思想:** GRADE通过图形表示模型捕捉LLM代理的执行顺序和依赖关系，从而提高故障预测和优化能力。

### reasoning / planning

## 4. PlanBench-XL: Evaluating Long-Horizon Planning of LLM Tool-Use Agents in Large-Scale Tool Ecosystems

- **Authors:** Jiayu Liu, Qihan Lin, Cheng Qian, Rui Wang, Emre Can Acikgoz et al.
- **score 1.00  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-21  ·  via hf_papers  ·  👍 76**
- **Link:** https://arxiv.org/abs/2606.22388  ·  **Code:** https://github.com/JiayuJeff/PlanBench-XL

**为什么值得看:** 这项研究为LLM代理在复杂工具生态系统中的长远规划提供了新的评估基准，揭示了在动态环境中适应和工具使用的挑战。

**核心思想:** PlanBench-XL是一个互动基准，评估LLM工具使用代理在长时间任务中的规划能力，特别是在工具可见性受限的情况下。

## 5. Context-Aware RL for Agentic and Multimodal LLMs

- **Authors:** Peiyang Xu, Bangzheng Li, Sijia Liu, Karthik R. Narasimhan, Pramod Viswanath et al.
- **score 0.84  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-15  ·  via hf_papers  ·  👍 15**
- **Link:** https://arxiv.org/abs/2606.17053  ·  **Code:** https://github.com/xupy2003/ContextAwareRL

**为什么值得看:** 这项研究为提高LLM在复杂上下文中的推理能力提供了一种新方法，直接影响到LLM代理的表现。

**核心思想:** ContextRL通过引入上下文选择的间接辅助目标，增强了LLM在长时间推理和多模态任务中的表现。

### agent evaluation / benchmarks

## 6. DailyReport: An Open-ended Benchmark for Evaluating Search Agents on Daily Search Tasks

- **Authors:** Jingxuan Han, Wei Liu, Mingyang Zhu, Youpeng Wang, Ziwen Wang et al.
- **score 0.76  ·  priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-11  ·  via hf_papers  ·  👍 8**
- **Link:** https://arxiv.org/abs/2606.12871  ·  **Code:** https://github.com/AGI-Eval-Official/DailyReport

**为什么值得看:** 这项研究为评估搜索代理的能力提供了一个新的基准，强调了在真实用户场景中使用LLM代理的重要性。

**核心思想:** DailyReport基准通过开放式任务和细化的评估标准，提供了对搜索代理在日常搜索任务中表现的深入分析。

## 7. Beyond Static Leaderboards: Predictive Validity for the Evaluation of LLM Agents

- **Authors:** Dhaval C. Patel, Kaoutar El Maghraoui, Shuxin Lin, Yusheng Li, Tianjun Feng et al.
- **score 0.74  ·  priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-18  ·  via hf_papers  ·  👍 39**
- **Link:** https://arxiv.org/abs/2606.19704

**为什么值得看:** 这篇论文为评估LLM代理提供了新的视角，强调了预测有效性的重要性，帮助研究人员理解如何更好地评估和比较代理的性能。

**核心思想:** 论文提出了一种基于预测有效性的排名配置，旨在改进LLM代理的评估方法。

### multi-agent systems

## 8. Deep Research in Physical Sciences: A Multi-Agent Framework and Comprehensive Benchmark

- **Authors:** Yigeng Jiang, Tengchao Yang, Taoyong Cui, Jiaxing Wan, Yuan Wang et al.
- **score 0.83  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-17  ·  via hf_papers  ·  👍 12**
- **Link:** https://arxiv.org/abs/2606.18648  ·  **Code:** https://github.com/yigengjiang/physci-deepresearch

**为什么值得看:** 这项研究为 LLM 代理在科学研究中的应用提供了重要的基准和框架，展示了多代理系统在复杂推理任务中的潜力。

**核心思想:** 研究提出了 PhySciBench 基准和 DelveAgent 多代理框架，旨在提升 LLM 在物理科学领域的推理能力和可靠性。

# 💻 开源项目

### tool use / function calling

## 1. anthropics/claude-code

- **Authors:** anthropics
- **score 0.85  ·  priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-22  ·  via github  ·  👍 133949**
- **Link:** https://github.com/anthropics/claude-code  ·  **Code:** https://github.com/anthropics/claude-code

**为什么值得看:** 这项研究展示了如何通过自然语言命令增强代码编写效率，这对LLM代理的工具使用和功能调用具有重要意义。

**核心思想:** Claude Code是一个能够理解代码库并通过自然语言执行例行任务的代理工具。

## 2. langflow-ai/langflow

- **Authors:** langflow-ai
- **score 0.73  ·  priority medium  ·  rel 0.80  ·  nov 0.60  ·  2026-06-23  ·  via github  ·  👍 149978**
- **Link:** https://github.com/langflow-ai/langflow  ·  **Code:** https://github.com/langflow-ai/langflow

**为什么值得看:** 研究人员应该关注Langflow，因为它提供了构建和部署AI代理及工作流的工具，这对LLM代理的开发至关重要。

**核心思想:** Langflow是一个用于构建和部署AI代理和工作流的强大工具。

## 3. langgenius/dify

- **Authors:** langgenius
- **score 0.72  ·  priority medium  ·  rel 0.80  ·  nov 0.60  ·  2026-06-23  ·  via github  ·  👍 146290**
- **Link:** https://github.com/langgenius/dify  ·  **Code:** https://github.com/langgenius/dify

**为什么值得看:** 这项研究为开发智能代理工作流提供了一个生产就绪的平台，可能会对 LLM 代理的应用和工具使用产生影响。

**核心思想:** 该平台旨在简化和优化智能代理的工作流开发过程。

### multi-agent systems

## 4. TauricResearch/TradingAgents

- **Authors:** TauricResearch
- **score 0.77  ·  priority high  ·  rel 0.90  ·  nov 0.80  ·  2026-06-22  ·  via github  ·  👍 88154**
- **Link:** https://github.com/TauricResearch/TradingAgents  ·  **Code:** https://github.com/TauricResearch/TradingAgents

**为什么值得看:** 这项研究为多智能体系统在金融交易中的应用提供了新的框架，可能会推动LLM代理在复杂决策环境中的表现。

**核心思想:** 该框架利用多智能体LLM进行金融交易，展示了智能体之间的协作与竞争。

### other

## 5. obra/superpowers

- **Authors:** obra
- **score 0.69  ·  priority medium  ·  rel 0.60  ·  nov 0.50  ·  2026-06-23  ·  via github  ·  👍 236770**
- **Link:** https://github.com/obra/superpowers  ·  **Code:** https://github.com/obra/superpowers

**为什么值得看:** 这项研究提供了一种新的代理技能框架，可能对开发更有效的LLM代理有启发。

**核心思想:** 该论文提出了一种有效的代理技能框架和软件开发方法论。

# 📝 实验室动态

### tool use / function calling

## 1. Agentic Resource Discovery: Let agents search

- **score 0.64  ·  priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-17  ·  via rss**
- **Link:** https://huggingface.co/blog/agentic-resource-discovery-launch

**为什么值得看:** 这项研究为LLM代理提供了一种新的资源发现机制，增强了它们的搜索能力和工具使用效率。

**核心思想:** 提出了一种新方法，使代理能够自主搜索和发现资源，从而提高其在复杂任务中的表现。

## 2. Is it agentic enough? Benchmarking open models on your own tooling

- **score 0.61  ·  priority high  ·  rel 1.00  ·  nov 0.70  ·  2026-06-18  ·  via rss**
- **Link:** https://huggingface.co/blog/is-it-agentic-enough

**为什么值得看:** 这篇论文为研究人员提供了一个基准框架，以评估开放模型在工具使用方面的能力，帮助推动LLM代理的实用性和有效性。

**核心思想:** 论文提出了一种新的基准方法，用于评估开放模型在自主工具使用中的表现。

## 3. Build real agentic apps using CUGA: two dozen working examples on a lightweight harness

- **score 0.60  ·  priority high  ·  rel 0.90  ·  nov 0.80  ·  2026-06-23  ·  via rss**
- **Link:** https://huggingface.co/blog/ibm-research/cuga-apps

**为什么值得看:** 这篇论文提供了一个轻量级的框架和多个实例，展示了如何构建具有代理能力的应用程序，适合希望在LLM代理领域进行实际开发的研究人员。

**核心思想:** 论文介绍了CUGA框架，通过二十多个示例展示了如何创建具有代理功能的应用程序。

### multi-agent systems

## 4. The Open Source Community is backing OpenEnv for Agentic RL

- **score 0.53  ·  priority medium  ·  rel 0.80  ·  nov 0.70  ·  2026-06-08  ·  via rss**
- **Link:** https://huggingface.co/blog/openenv-agentic-rl

**为什么值得看:** 这篇论文探讨了开放源代码社区如何支持Agentic RL，这对研究LLM代理的工具使用和规划能力至关重要。

**核心思想:** 论文提出了一个开放环境，旨在促进代理强化学习的发展，强调社区的作用。

### agent safety / robustness

## 5. MosaicLeaks: Can your research agent keep a secret?

- **score 0.53  ·  priority medium  ·  rel 0.80  ·  nov 0.70  ·  2026-06-18  ·  via rss**
- **Link:** https://huggingface.co/blog/ServiceNow/mosaicleaks

**为什么值得看:** 研究人员应该关注这项研究，因为它探讨了LLM代理在处理敏感信息时的安全性和隐私问题。

**核心思想:** 该论文提出了一种新的方法来评估研究代理在保密性方面的能力。

