# OmniSource Daily — World Models

*2026-06-24 · 13 signals · English sample*

# 📄 Papers

### learned simulators

## 1. IOI: Decoupling Kinematics and Physics for Interactive World Models

- **Authors:** Chengyu Bai, Peidong Jia, Tiecheng Guo, Yukai Wang, Rui Ma et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23296v1

**Why it matters:** Interactive world models address this by simulating such complex dynamics.

**Key idea:** Developing generalist embodied agents requires interactive environments providing visually realistic feedback and accurate action-conditioned dynamics.

## 2. Causal Reward World Models: Zero-shot Reward Design for Automated Skill Generation

- **Authors:** Yang Yang, Yuchuang Tong, Zhengtao Zhang, Xu Ding, Ning Yang et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23280v1

**Why it matters:** However, existing approaches based on large language models (LLMs) remain inherently correlation-driven, relying on iterative environmental feedback to refine reward hypotheses for each specific task.

**Key idea:** Automated Reward Design (ARD) aims to replace manual reward engineering in reinforcement learning with language-driven reward function synthesis.

## 3. World Action Models: A Survey

- **Authors:** Qiuhong Shen, Shihua Zhang, Yue Liao, Qi Li, Zhenxiong Tan et al.
- **priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-18  ·  via hf_papers  ·  👍 36**
- **Link:** https://arxiv.org/abs/2606.20781  ·  **Code:** https://github.com/world-action-models/awesome-world-action-models

**Why it matters:** Recent WAMs repurpose large video generation models, and a parallel line relies on language or vision-language backbones without a video-generation core.

**Key idea:** World Action Models (WAMs) are embodied predictive-action models that make a forecast of the future available to action.

## 4. Attacking the Trusted Imagination: Oracle-Level Integrity Attacks on Imagine-then-Act World Models

- **Authors:** Linghan Chen, Kaiyan Ji, Minyu Guo
- **priority high  ·  rel 0.90  ·  nov 0.80  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.22966v1

**Why it matters:** A world-action model (WAM) first imagines a short future as a latent trajectory z~, on which the action is then conditioned.

**Key idea:** Many recent vision-language-action (VLA) policies adopt an imagine-then-act design.

### latent dynamics

## 5. SkyJEPA: Learning Long-Horizon World Models for Zero-Shot Sim-to-Real Control of Quadrotors

- **Authors:** Pratyaksh Rao, Wancong Zhang, Randall Balestriero, Yann LeCun, Giuseppe Loianno
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23444v1

**Why it matters:** Neural network dynamics models are attractive for capturing complex nonlinear effects, but existing predictive approaches struggle with long-horizon forecasting because their autoregressive rollout mechanism amplifies errors over time.

**Key idea:** Accurate dynamics models are critical for informed decision-making in robotic systems, particularly for agile aerial vehicles operating under uncertainty.

### model-based reinforcement learning

## 6. Active Inference as the Test-Time Scaling Law for Physical AI Agents

- **Authors:** Omar Hashash, Christo Kurisummoottil Thomas, Walid Saad, Merouane Debbah, Karl Friston et al.
- **priority high  ·  rel 0.80  ·  nov 0.90  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.22813v1

**Why it matters:** This scaling law enables physical AI agents to reason with their world models to generalize in unforeseen scenarios at test time.

**Key idea:** In this paper, a novel test-time scaling law for physical artificial intelligence (AI) agents is introduced.

### planning with world models

## 7. AdaReP:Adaptive Re-Planning under Model Mismatch for Neural World-Model Predictive Control

- **Authors:** Yutian Cheng, Xiaojian Ma, Xianhao Wang, Min Yang, Rongpeng Su et al.
- **priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23079v1

**Why it matters:** Reusing a cached plan reduces this overhead, yet its effectiveness depends on how prediction mismatch propagates through the local dynamics.

**Key idea:** Neural world models coupled with model predictive control (MPC) replan at every environment step to bound accumulated prediction error, but this incurs substantial computational overhead.

### video / generative world models

## 8. Compression and Retrieval: Implicit Memory Retrieval for Video World Models

- **Authors:** Zhan Peng, Jie Ma, Huiqiang Sun, Chong Gao, Zhijie Xue et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23105v1

**Why it matters:** Existing methods typically rely on computationally expensive context scaling or rigid heuristic retrieval mechanisms, which lacks generalization to varying camera trajectories and environments.

**Key idea:** Video world models hold promise for simulating interactive environments, yet maintaining consistent long-term memory across complex camera trajectories remains a critical challenge.

# 💻 Repositories

## 1. iptv-org/iptv

- **Authors:** iptv-org
- **priority low  ·  rel 0.00  ·  nov 0.00  ·  2026-06-23  ·  via github  ·  👍 127903**
- **Link:** https://github.com/iptv-org/iptv  ·  **Code:** https://github.com/iptv-org/iptv

**Why it matters:** For World Models readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** Collection of publicly available IPTV channels from all over the world

## 2. gohugoio/hugo

- **Authors:** gohugoio
- **priority low  ·  rel 0.00  ·  nov 0.00  ·  2026-06-18  ·  via github  ·  👍 88703**
- **Link:** https://github.com/gohugoio/hugo  ·  **Code:** https://github.com/gohugoio/hugo

**Why it matters:** For World Models readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** The world’s fastest framework for building websites.

## 3. koala73/worldmonitor

- **Authors:** koala73
- **priority low  ·  rel 0.00  ·  nov 0.00  ·  2026-06-23  ·  via github  ·  👍 58894**
- **Link:** https://github.com/koala73/worldmonitor  ·  **Code:** https://github.com/koala73/worldmonitor

**Why it matters:** AI-powered news aggregation, geopolitical monitoring, and infrastructure tracking in a unified situational awareness interface

**Key idea:** Real-time global intelligence dashboard.

### learned simulators

## 4. NVIDIA/cosmos

- **Authors:** NVIDIA
- **priority medium  ·  rel 0.80  ·  nov 0.60  ·  2026-06-23  ·  via github  ·  👍 10509**
- **Link:** https://github.com/NVIDIA/cosmos  ·  **Code:** https://github.com/NVIDIA/cosmos

**Why it matters:** For World Models readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** NVIDIA Cosmos is an open platform of world models, datasets, and tools that enables developers to build Physical AI for robots, autonomous vehicles, smart infrastructure, and more.

## 5. Genesis-Embodied-AI/genesis-world

- **Authors:** Genesis-Embodied-AI
- **priority medium  ·  rel 0.50  ·  nov 0.40  ·  2026-06-23  ·  via github  ·  👍 29413**
- **Link:** https://github.com/Genesis-Embodied-AI/genesis-world  ·  **Code:** https://github.com/Genesis-Embodied-AI/genesis-world

**Why it matters:** For World Models readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** Simulation platform for general-purpose robotics & embodied AI learning.
