# OmniSource Daily — world-models

*2026-06-24 · 13 signals · sources: arxiv, hf_papers, rss, github*

# 📄 论文

### other

## 1. World Action Models: A Survey

- **Authors:** Qiuhong Shen, Shihua Zhang, Yue Liao, Qi Li, Zhenxiong Tan et al.
- **score 0.94  ·  priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-18  ·  via hf_papers  ·  👍 36**
- **Link:** https://arxiv.org/abs/2606.20781  ·  **Code:** https://github.com/world-action-models/awesome-world-action-models

**为什么值得看:** 这篇综述为研究者提供了一个关于世界模型和行动模型的统一视角，有助于理解不同方法之间的关系和设计选择。

**核心思想:** 文章通过分析现有的世界行动模型，阐明了它们在生成未来和行动推理中的不同角色和设计考量。

## 2. Attacking the Trusted Imagination: Oracle-Level Integrity Attacks on Imagine-then-Act World Models

- **Authors:** Linghan Chen, Kaiyan Ji, Minyu Guo
- **score 0.60  ·  priority high  ·  rel 0.90  ·  nov 0.80  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.22966v1

**为什么值得看:** 这篇论文揭示了想象-行动世界模型中的安全性漏洞，对研究者理解和改进世界模型的鲁棒性至关重要。

**核心思想:** 论文提出了一种攻击模型，专注于如何通过操控想象阶段的潜在轨迹来影响决策过程。

### learned simulators

## 3. IOI: Decoupling Kinematics and Physics for Interactive World Models

- **Authors:** Chengyu Bai, Peidong Jia, Tiecheng Guo, Yukai Wang, Rui Ma et al.
- **score 0.70  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23296v1

**为什么值得看:** 这项研究为构建更精确和可靠的交互式世界模型提供了新的方法，尤其是在动态模拟和策略评估方面。

**核心思想:** IOI通过将分析运动学先验与学习的物理动态相结合，提出了一种混合交互式世界模型，显著提高了模拟的准确性和鲁棒性。

## 4. Causal Reward World Models: Zero-shot Reward Design for Automated Skill Generation

- **Authors:** Yang Yang, Yuchuang Tong, Zhengtao Zhang, Xu Ding, Ning Yang et al.
- **score 0.70  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23280v1

**为什么值得看:** 这项研究为自动化奖励设计提供了一种新的因果模型框架，能够在没有反馈的情况下生成有效的奖励函数，从而加速机器人技能的生成。

**核心思想:** 提出了一种因果奖励世界模型（CRWM），通过建模奖励组件与物理变量之间的因果关系，实现零-shot奖励函数设计。

### latent dynamics

## 5. SkyJEPA: Learning Long-Horizon World Models for Zero-Shot Sim-to-Real Control of Quadrotors

- **Authors:** Pratyaksh Rao, Wancong Zhang, Randall Balestriero, Yann LeCun, Giuseppe Loianno
- **score 0.70  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23444v1

**为什么值得看:** 这项研究为无人机控制提供了一种新的长时间预测的世界模型，能够在真实环境中实现零-shot的模拟到现实转移，具有重要的应用价值。

**核心思想:** 提出了一种结合潜在动态模型和物理启发式探测器的JEPA风格模型，用于实时四旋翼控制，能够进行长时间的准确预测。

### video / generative world models

## 6. Compression and Retrieval: Implicit Memory Retrieval for Video World Models

- **Authors:** Zhan Peng, Jie Ma, Huiqiang Sun, Chong Gao, Zhijie Xue et al.
- **score 0.70  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23105v1

**为什么值得看:** 这项研究为视频世界模型提供了一种新的隐式记忆检索机制，能够在复杂环境中保持长期一致性，这对世界模型研究者至关重要。

**核心思想:** 提出了一种基于注意力的隐式记忆检索机制，通过位置编码注入视角信息，从而实现灵活的记忆检索。

### planning with world models

## 7. AdaReP:Adaptive Re-Planning under Model Mismatch for Neural World-Model Predictive Control

- **Authors:** Yutian Cheng, Xiaojian Ma, Xianhao Wang, Min Yang, Rongpeng Su et al.
- **score 0.64  ·  priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23079v1

**为什么值得看:** 世界模型研究者应该关注AdaReP，因为它提供了一种有效的自适应重规划方法，能够在模型不匹配的情况下减少计算开销，同时保持任务性能。

**核心思想:** AdaReP是一种训练无关的包装器，通过在线调整重规划容忍度来应对模型不匹配，显著减少规划器的计算需求。

### model-based reinforcement learning

## 8. Active Inference as the Test-Time Scaling Law for Physical AI Agents

- **Authors:** Omar Hashash, Christo Kurisummoottil Thomas, Walid Saad, Merouane Debbah, Karl Friston et al.
- **score 0.59  ·  priority high  ·  rel 0.80  ·  nov 0.90  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.22813v1

**为什么值得看:** 这项研究为物理AI代理提供了一种新的方法，通过动态更新其世界模型来应对未知场景，增强了模型在非平稳环境中的泛化能力。

**核心思想:** 该论文提出了一种基于主动推理的测试时间缩放法则，使物理AI代理能够在测试时通过更新策略来应对未见过的情况。

# 💻 开源项目

### other

## 1. iptv-org/iptv

- **Authors:** iptv-org
- **score 0.30  ·  priority low  ·  rel 0.00  ·  nov 0.00  ·  2026-06-23  ·  via github  ·  👍 127903**
- **Link:** https://github.com/iptv-org/iptv  ·  **Code:** https://github.com/iptv-org/iptv

**为什么值得看:** 这篇论文与世界模型的主题无关，因此对研究者没有价值。

**核心思想:** 该项目是一个公共IPTV频道的集合。

## 2. gohugoio/hugo

- **Authors:** gohugoio
- **score 0.24  ·  priority low  ·  rel 0.00  ·  nov 0.00  ·  2026-06-18  ·  via github  ·  👍 88703**
- **Link:** https://github.com/gohugoio/hugo  ·  **Code:** https://github.com/gohugoio/hugo

**为什么值得看:** 这篇论文与世界模型无关，因此对研究者没有价值。

**核心思想:** 该论文介绍了一个用于构建网站的框架。

## 3. koala73/worldmonitor

- **Authors:** koala73
- **score 0.19  ·  priority low  ·  rel 0.00  ·  nov 0.00  ·  2026-06-23  ·  via github  ·  👍 58894**
- **Link:** https://github.com/koala73/worldmonitor  ·  **Code:** https://github.com/koala73/worldmonitor

**为什么值得看:** 这篇论文与世界模型的主题无关，因此对研究者没有直接的价值。

**核心思想:** 该论文介绍了一个实时全球情报仪表板，专注于新闻聚合和地缘政治监测。

### learned simulators

## 4. NVIDIA/cosmos

- **Authors:** NVIDIA
- **score 0.62  ·  priority medium  ·  rel 0.80  ·  nov 0.60  ·  2026-06-23  ·  via github  ·  👍 10509**
- **Link:** https://github.com/NVIDIA/cosmos  ·  **Code:** https://github.com/NVIDIA/cosmos

**为什么值得看:** NVIDIA Cosmos provides a comprehensive framework for developing world models, which is essential for researchers focused on creating advanced AI systems that interact with the physical world.

**核心思想:** NVIDIA Cosmos is an open platform that integrates world models with datasets and tools for building Physical AI applications.

## 5. Genesis-Embodied-AI/genesis-world

- **Authors:** Genesis-Embodied-AI
- **score 0.47  ·  priority medium  ·  rel 0.50  ·  nov 0.40  ·  2026-06-23  ·  via github  ·  👍 29413**
- **Link:** https://github.com/Genesis-Embodied-AI/genesis-world  ·  **Code:** https://github.com/Genesis-Embodied-AI/genesis-world

**为什么值得看:** 这项研究为机器人和具身AI学习提供了一个通用的模拟平台，可能对世界模型的研究者在构建和评估模型时有帮助。

**核心思想:** 该平台旨在支持通用机器人和具身AI的学习，提供了一个灵活的模拟环境。

