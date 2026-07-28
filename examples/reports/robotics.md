# OmniSource Daily — robotics

*2026-06-24 · 14 signals · sources: arxiv, hf_papers, rss, github*

# 📄 论文

### vision-language-action (VLA)

## 1. PolicyTrim: Boosting Intrinsic Policy Efficiency of Vision-Language-Action Models

- **Authors:** Xianghui Wang, Feng Chen, Wenbo Zhang, Hua Yan, Zixuan Wang et al.
- **score 0.90  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-21  ·  via hf_papers  ·  👍 4**
- **Link:** https://arxiv.org/abs/2606.22540  ·  **Code:** https://github.com/INCEPTIONwang/PolicyTrim

**为什么值得看:** 这项研究为机器人操作中的视觉-语言-行动模型提供了提高执行效率的新方法，直接影响到机器人在现实世界中的应用。

**核心思想:** 提出了一种名为PolicyTrim的框架，通过强化学习优化视觉-语言-行动模型的内在策略效率，减少冗余物理步骤并延长可执行动作块的长度。

## 2. GeneralVLA-2: Geometry-Aware Reconstruction and Governed Memory for Robot Planning

- **Authors:** Haoyu Wang, Guoqing Ma, Zeyu Zhang, Yandong Guo, Boxin Shi et al.
- **score 0.87  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-16  ·  via hf_papers  ·  👍 3**
- **Link:** https://arxiv.org/abs/2606.17480  ·  **Code:** https://github.com/AIGeeksGroup/GeneralVLA-2

**为什么值得看:** 这项研究为机器人规划提供了更精确的几何重建和记忆管理方法，能够提升机器人在复杂环境中的操作能力。

**核心思想:** 提出了一种几何优先的多视图3D重建方法和一个受控的长期记忆系统，以提高机器人在语言-视觉-动作任务中的表现。

## 3. LIBERO-Safety: A Comprehensive Benchmark for Physical and Semantic Safety in Vision-Language-Action Models

- **Authors:** Rongxu Cui, Zongzheng Zhang, Jingrui Pang, Haohan Chi, Jinbang Guo et al.
- **score 0.70  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23686v1

**为什么值得看:** 这项研究为机器人研究者提供了一个重要的基准，以评估视觉-语言-行动模型在安全性方面的表现，确保机器人在复杂环境中的安全操作。

**核心思想:** 该研究提出了一个参数化的安全基准，通过程序生成安全关键场景，并开发了一个新的数据生成管道，以支持视觉-语言-行动模型的安全性评估。

## 4. dVLA-RL: Reinforcement Learning over Denoising Trajectories for Discrete Diffusion Vision-Language-Action Models

- **Authors:** Yuhao Wu, Yitian Liu, Weijie Shen, Mishuo Han, Wenjie Xu et al.
- **score 0.70  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23623v1

**为什么值得看:** 机器人研究人员应该关注此研究，因为它提出了一种新颖的强化学习方法，能够有效地结合视觉、语言和动作，推动通用机器人操作的进步。

**核心思想:** 该研究提出了dVLA-RL，通过将去噪过程建模为马尔可夫决策过程，提供了一种新的轨迹级目标来优化离散扩散视觉-语言-动作模型的学习。

### manipulation

## 5. Foresight: Failure Detection for Long-Horizon Robotic Manipulation with Action-Conditioned World Model Latents

- **Authors:** Haoran Zhang, Yifu Lu, Boyang Wang, Xuhui Kang, Yen-Ling Kuo et al.
- **score 0.84  ·  priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-22  ·  via arxiv, hf_papers  ·  👍 8**
- **Link:** http://arxiv.org/abs/2606.23085v1

**为什么值得看:** 机器人研究人员应该关注这一研究，因为它提供了一种新的方法来检测长时间操作中的失败，从而提高机器人在复杂任务中的可靠性。

**核心思想:** Foresight框架利用动作条件的世界模型潜在表示来监控操作轨迹，从而实现长时间任务中的失败检测。

## 6. DexTeleop-0: Force-Aware Bimanual Dexterous Teleoperation with Ego-Centric Perception towards Shared Autonomy

- **Authors:** Haichao Liu, Yuyao Jiang, Hyunsun Park, Yuanjiang Xue, Ziwei Wang
- **score 0.70  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23431v1

**为什么值得看:** 这项研究为机器人在复杂的双手操作任务中提供了新的触觉反馈机制，能够显著提高操作精度和效率，适合关注机器人操作的研究者。

**核心思想:** 该研究提出了一种基于触觉的适应策略，通过实时优化循环将粗略的人类跟踪意图转化为精确的机器人命令，从而实现高精度的双手灵巧操作。

## 7. CoorDex: Coordinating Body and Hand Priors for Continuous Dexterous Humanoid Loco-Manipulation

- **Authors:** Sikai Li, Shuning Li, Zhenyu Wei, Yunchao Yao, Chenran Li et al.
- **score 0.70  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23680v1

**为什么值得看:** 这项研究为机器人在动态环境中进行复杂的操控任务提供了新的方法，推动了人形机器人在实际应用中的能力。

**核心思想:** CoorDex通过协调身体和手的先验知识，实现了高自由度的动态操控，允许机器人在移动中进行复杂的抓取和操作。

### imitation / policy learning

## 8. Improving Robotic Imitation Learning via Trajectory Standardization

- **Authors:** Licheng Yang, Lingfeng Qian, Fei Zheng, Yonghao He, Wei Sui et al.
- **score 0.70  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.22907v1

**为什么值得看:** 这项研究为机器人模仿学习提供了一种新的数据预处理方法，能够显著提高任务成功率，值得机器人研究者关注。

**核心思想:** 提出了一种信息标准化轨迹重采样方法，通过在信息调制的黎曼流形上进行轨迹映射，改善了模仿学习的数据质量。

# 💻 开源项目

### other

## 1. huggingface/lerobot

- **Authors:** huggingface
- **score 0.71  ·  priority high  ·  rel 0.80  ·  nov 0.70  ·  2026-06-23  ·  via github  ·  👍 25218**
- **Link:** https://github.com/huggingface/lerobot  ·  **Code:** https://github.com/huggingface/lerobot

**为什么值得看:** 这项研究为机器人领域的研究人员提供了一个更易于访问的端到端学习框架，促进了机器人智能的开发。

**核心思想:** 该论文提出了一个名为LeRobot的框架，旨在通过端到端学习简化机器人AI的开发过程。

## 2. rerun-io/rerun

- **Authors:** rerun-io
- **score 0.60  ·  priority medium  ·  rel 0.70  ·  nov 0.60  ·  2026-06-23  ·  via github  ·  👍 10976**
- **Link:** https://github.com/rerun-io/rerun  ·  **Code:** https://github.com/rerun-io/rerun

**为什么值得看:** 这项研究为机器人研究人员提供了一种新的工具来可视化和查询多模态数据，从而提高训练效率。

**核心思想:** 该论文介绍了一种用于可视化和流式传输多模态机器人数据的工具，旨在改善训练过程。

## 3. earthtojake/text-to-cad

- **Authors:** earthtojake
- **score 0.58  ·  priority medium  ·  rel 0.70  ·  nov 0.60  ·  2026-06-22  ·  via github  ·  👍 6842**
- **Link:** https://github.com/earthtojake/text-to-cad  ·  **Code:** https://github.com/earthtojake/text-to-cad

**为什么值得看:** 这项研究为机器人设计提供了新的技能集合，可能会影响机器人在CAD和硬件设计中的应用。

**核心思想:** 该论文提出了一套用于CAD和机器人硬件设计的代理技能。

### embodied agents

## 4. Genesis-Embodied-AI/genesis-world

- **Authors:** Genesis-Embodied-AI
- **score 0.81  ·  priority high  ·  rel 1.00  ·  nov 0.70  ·  2026-06-23  ·  via github  ·  👍 29413**
- **Link:** https://github.com/Genesis-Embodied-AI/genesis-world  ·  **Code:** https://github.com/Genesis-Embodied-AI/genesis-world

**为什么值得看:** 这项研究为机器人和具身人工智能的学习提供了一个通用的模拟平台，能够加速相关算法的开发与测试。

**核心思想:** 该平台支持多种机器人任务的模拟，促进了机器人学习和具身智能的研究。

### manipulation

## 5. mani-skill/ManiSkill

- **Authors:** mani-skill
- **score 0.71  ·  priority high  ·  rel 0.90  ·  nov 0.80  ·  2026-06-23  ·  via github  ·  👍 3032**
- **Link:** https://github.com/mani-skill/ManiSkill  ·  **Code:** https://github.com/mani-skill/ManiSkill

**为什么值得看:** 这项研究为机器人操作提供了一个新的基准和模拟框架，有助于推动操作技能的学习和评估。

**核心思想:** 该框架利用GPU并行化技术来提高机器人操作技能的模拟效率。

# 📝 实验室动态

### vision-language-action (VLA)

## 1. From the Hugging Face Hub to robot hardware with Strands Agents and LeRobot

- **score 0.53  ·  priority high  ·  rel 0.80  ·  nov 0.70  ·  2026-06-17  ·  via rss**
- **Link:** https://huggingface.co/blog/amazon/strands-lerobot-hub-to-hardware

**为什么值得看:** 这篇论文展示了如何将先进的自然语言处理模型应用于机器人硬件，推动了机器人学习和操作的边界。

**核心思想:** 论文介绍了Strands Agents和LeRobot如何将Hugging Face Hub中的模型转化为实际的机器人应用。

