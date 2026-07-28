# OmniSource Daily — LLM Agents

*2026-06-24 · 18 signals · English sample*

# 📄 Papers

### agent evaluation / benchmarks

## 1. DailyReport: An Open-ended Benchmark for Evaluating Search Agents on Daily Search Tasks

- **Authors:** Jingxuan Han, Wei Liu, Mingyang Zhu, Youpeng Wang, Ziwen Wang et al.
- **priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-11  ·  via hf_papers  ·  👍 8**
- **Link:** https://arxiv.org/abs/2606.12871  ·  **Code:** https://github.com/AGI-Eval-Official/DailyReport

**Why it matters:** For SAs evaluation, prior benchmarks mainly focus on specialized tasks that are unlikely to arise in real-world user scenarios.

**Key idea:** Search Agents (SAs) typically leverage large language models (LLMs) to support complex information-seeking tasks by autonomously exploring web sources and synthesizing information into comprehensive responses.

## 2. Counsel: A Meta-Evaluation Dataset for Agentic Tasks

- **Authors:** Sashank Pisupati, Henry Broomfield, Eujeong Choi, Antonia Calvi, Charlie Wang et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-19  ·  via hf_papers  ·  👍 4**
- **Link:** https://arxiv.org/abs/2606.21627

**Why it matters:** This has driven widespread reliance on automated approaches such as LLM-as-a-judge (LLMJ) to critique agents at the process and outcome-levels at scale, however, the soundness of LLMJ critiques often goes unmeasured.

**Key idea:** As agentic systems tackle increasingly complex multi-step tasks, evaluating their trajectories presents a major bottleneck - human annotation of a single trajectory on popular agentic benchmarks can take hours, making it difficult to scale evaluations for measuring performance or curating training data.

## 3. RigorBench: Benchmarking Engineering Process Discipline in Autonomous AI Coding Agents

- **Authors:** Meher Bhaskar Madiraju, Meher Sai Preetam Madiraju
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-21  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.22678v1

**Why it matters:** Existing benchmarks evaluate these agents almost exclusively on outcome correctness: whether generated code passes tests or resolves issues.

**Key idea:** Agentic coding harnesses - such as Agent-Skills, Superpowers, and Agent-Rigor - are increasingly deployed to augment underlying LLMs for real-world software engineering tasks.

### multi-agent systems

## 4. Deep Research in Physical Sciences: A Multi-Agent Framework and Comprehensive Benchmark

- **Authors:** Yigeng Jiang, Tengchao Yang, Taoyong Cui, Jiaxing Wan, Yuan Wang et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-17  ·  via hf_papers  ·  👍 12**
- **Link:** https://arxiv.org/abs/2606.18648  ·  **Code:** https://github.com/yigengjiang/physci-deepresearch

**Why it matters:** However, comprehensive and in-depth evaluations of their capabilities within this domain remain lacking.

**Key idea:** Deep research agents are Large Language Model (LLM)-based systems designed for autonomous, multi-step scientific reasoning, and they hold immense potential for accelerating research in the physical sciences.

## 5. HoloAgent-0: A Unified Embodied Agent Framework with 3D Spatial Memory

- **Authors:** Xiaolin Zhou, Liu Liu, Tingyang Xiao, Wei Feng, Fa Fu et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23565v1

**Why it matters:** Extending this loop to physical robots is difficult because physical execution is continuous, embodiment-dependent, uncertain, and constrained by safety.

**Key idea:** LLM agents follow a practical execution loop in digital environments: they reason over structured states, invoke tools, inspect feedback, and revise actions.

### reasoning / planning

## 6. CalVerT: Augmenting Agents with Calibrated Verifier Telemetry Improves Action and Learning in Knowledge-Intensive Tasks

- **Authors:** Ashwin Vinod, Ying Ding, Elias Stengel-Eskin
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-19  ·  via hf_papers  ·  👍 2**
- **Link:** https://arxiv.org/abs/2606.21777  ·  **Code:** https://github.com/ashwinn-v/CalVerT

**Why it matters:** This produces two failure modes: committing to confident but unsupported answers, which hurts accuracy, and over-retrieving when the evidence in hand already suffices, resulting in wasted compute.

**Key idea:** LLM agents in knowledge intensive question answering take retrieval and reasoning actions with incomplete knowledge about whether their current answer is uncertain, unsupported, or already complete.

## 7. GRADE: Graph Representation of LLM Agent Dependency and Execution

- **Authors:** Yue Zhao
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.22741v1

**Why it matters:** A trace records what each step did, never what it relied on, the state it read, and the results it reused.

**Key idea:** Can one graph represent every kind of LLM agent's run?

### tool use / function calling

## 8. PlanBench-XL: Evaluating Long-Horizon Planning of LLM Tool-Use Agents in Large-Scale Tool Ecosystems

- **Authors:** Jiayu Liu, Qihan Lin, Cheng Qian, Rui Wang, Emre Can Acikgoz et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-21  ·  via hf_papers  ·  👍 76**
- **Link:** https://arxiv.org/abs/2606.22388  ·  **Code:** https://github.com/JiayuJeff/PlanBench-XL

**Why it matters:** However, existing benchmarks rarely evaluate planning under retrieval-limited tool visibility.

**Key idea:** LLM agents increasingly operate in large tool ecosystems, where real-world tasks require discovering relevant tools, inferring implicit sub-goals, and adapting to dynamic environments over long horizons.

# 💻 Repositories

### tool use / function calling

## 1. anthropics/claude-code

- **Authors:** anthropics
- **priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-22  ·  via github  ·  👍 133949**
- **Link:** https://github.com/anthropics/claude-code  ·  **Code:** https://github.com/anthropics/claude-code

**Why it matters:** For LLM Agents readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** Claude Code is an agentic coding tool that lives in your terminal, understands your codebase, and helps you code faster by executing routine tasks, explaining complex code, and handling git workflows - all through natural language commands.

## 2. langgenius/dify

- **Authors:** langgenius
- **priority medium  ·  rel 0.80  ·  nov 0.70  ·  2026-06-23  ·  via github  ·  👍 146290**
- **Link:** https://github.com/langgenius/dify  ·  **Code:** https://github.com/langgenius/dify

**Why it matters:** For LLM Agents readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** Production-ready platform for agentic workflow development.

## 3. langflow-ai/langflow

- **Authors:** langflow-ai
- **priority medium  ·  rel 0.80  ·  nov 0.60  ·  2026-06-23  ·  via github  ·  👍 149978**
- **Link:** https://github.com/langflow-ai/langflow  ·  **Code:** https://github.com/langflow-ai/langflow

**Why it matters:** For LLM Agents readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** Langflow is a powerful tool for building and deploying AI-powered agents and workflows.

### multi-agent systems

## 4. TauricResearch/TradingAgents

- **Authors:** TauricResearch
- **priority high  ·  rel 0.90  ·  nov 0.70  ·  2026-06-22  ·  via github  ·  👍 88153**
- **Link:** https://github.com/TauricResearch/TradingAgents  ·  **Code:** https://github.com/TauricResearch/TradingAgents

**Why it matters:** For LLM Agents readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** TradingAgents: Multi-Agents LLM Financial Trading Framework

## 5. NousResearch/hermes-agent

- **Authors:** NousResearch
- **priority medium  ·  rel 0.70  ·  nov 0.60  ·  2026-06-23  ·  via github  ·  👍 200675**
- **Link:** https://github.com/NousResearch/hermes-agent  ·  **Code:** https://github.com/NousResearch/hermes-agent

**Why it matters:** For LLM Agents readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** The agent that grows with you

# 📝 Lab Notes

### tool use / function calling

## 1. Build real agentic apps using CUGA: two dozen working examples on a lightweight harness

- **priority high  ·  rel 0.90  ·  nov 0.80  ·  2026-06-23  ·  via rss**
- **Link:** https://huggingface.co/blog/ibm-research/cuga-apps

**Why it matters:** For LLM Agents readers, this post captures a timely lab or engineering signal worth tracking.

**Key idea:** Build real agentic apps using CUGA: two dozen working examples on a lightweight harness is surfaced as a relevant blog signal for this track.

## 2. Is it agentic enough? Benchmarking open models on your own tooling

- **priority high  ·  rel 0.90  ·  nov 0.80  ·  2026-06-18  ·  via rss**
- **Link:** https://huggingface.co/blog/is-it-agentic-enough

**Why it matters:** For LLM Agents readers, this post captures a timely lab or engineering signal worth tracking.

**Key idea:** Is it agentic enough? Benchmarking open models on your own tooling is surfaced as a relevant blog signal for this track.

## 3. Agentic Resource Discovery: Let agents search

- **priority high  ·  rel 0.90  ·  nov 0.80  ·  2026-06-17  ·  via rss**
- **Link:** https://huggingface.co/blog/agentic-resource-discovery-launch

**Why it matters:** For LLM Agents readers, this post captures a timely lab or engineering signal worth tracking.

**Key idea:** Agentic Resource Discovery: Let agents search is surfaced as a relevant blog signal for this track.

### agent safety / robustness

## 4. MosaicLeaks: Can your research agent keep a secret?

- **priority high  ·  rel 0.80  ·  nov 0.70  ·  2026-06-18  ·  via rss**
- **Link:** https://huggingface.co/blog/ServiceNow/mosaicleaks

**Why it matters:** For LLM Agents readers, this post captures a timely lab or engineering signal worth tracking.

**Key idea:** MosaicLeaks: Can your research agent keep a secret? is surfaced as a relevant blog signal for this track.

### multi-agent systems

## 5. The Open Source Community is backing OpenEnv for Agentic RL

- **priority medium  ·  rel 0.80  ·  nov 0.70  ·  2026-06-08  ·  via rss**
- **Link:** https://huggingface.co/blog/openenv-agentic-rl

**Why it matters:** For LLM Agents readers, this post captures a timely lab or engineering signal worth tracking.

**Key idea:** The Open Source Community is backing OpenEnv for Agentic RL is surfaced as a relevant blog signal for this track.
