# OmniSource Daily — Robotics

*2026-06-24 · 14 signals · English sample*

# 📄 Papers

### vision-language-action (VLA)

## 1. PolicyTrim: Boosting Intrinsic Policy Efficiency of Vision-Language-Action Models

- **Authors:** Xianghui Wang, Feng Chen, Wenbo Zhang, Hua Yan, Zixuan Wang et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-21  ·  via hf_papers  ·  👍 4**
- **Link:** https://arxiv.org/abs/2606.22540  ·  **Code:** https://github.com/INCEPTIONwang/PolicyTrim

**Why it matters:** While existing efforts predominantly focus on compute-centric efficiency to reduce per-step inference latency, the intrinsic policy efficiency of these models remains largely unexplored.

**Key idea:** Vision-Language-Action (VLA) models provide a unified paradigm for robotic manipulation, yet their real-world deployment is often bottlenecked by execution efficiency.

## 2. GeneralVLA-2: Geometry-Aware Reconstruction and Governed Memory for Robot Planning

- **Authors:** Haoyu Wang, Guoqing Ma, Zeyu Zhang, Yandong Guo, Boxin Shi et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-16  ·  via hf_papers  ·  👍 3**
- **Link:** https://arxiv.org/abs/2606.17480  ·  **Code:** https://github.com/AIGeeksGroup/GeneralVLA-2

**Why it matters:** GeneralVLA provides a hierarchical interface for converting language and RGB-D observations into 3D end-effector paths, but two bottlenecks remain.

**Key idea:** Generalist vision-language-action systems need object-centric 3D evidence and reusable manipulation experience to plan reliable robot trajectories.

## 3. LIBERO-Safety: A Comprehensive Benchmark for Physical and Semantic Safety in Vision-Language-Action Models

- **Authors:** Rongxu Cui, Zongzheng Zhang, Jingrui Pang, Haohan Chi, Jinbang Guo et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23686v1

**Why it matters:** To address this, we introduce a parametric safety benchmark to procedurally generate safety-critical scenarios with comprehensive stochasticity.

**Key idea:** Despite the impressive manipulation capabilities of Vision-Language-Action (VLA) models, their operational safety under strict constraints remains largely unverified.

## 4. dVLA-RL: Reinforcement Learning over Denoising Trajectories for Discrete Diffusion Vision-Language-Action Models

- **Authors:** Yuhao Wu, Yitian Liu, Weijie Shen, Mishuo Han, Wenjie Xu et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23623v1

**Why it matters:** Prevailing architectures typically model actions continuously via diffusion or flow processes, or discretely through either autoregressive generation or parallel decoding.

**Key idea:** Vision-Language-Action (VLA) models have established a powerful paradigm for generalist robotic manipulation by grounding control into the semantic reasoning of VLMs.

### manipulation

## 5. Foresight: Failure Detection for Long-Horizon Robotic Manipulation with Action-Conditioned World Model Latents

- **Authors:** Haoran Zhang, Yifu Lu, Boyang Wang, Xuhui Kang, Yen-Ling Kuo et al.
- **priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-22  ·  via arxiv, hf_papers  ·  👍 8**
- **Link:** http://arxiv.org/abs/2606.23085v1

**Why it matters:** Detecting failures in long-horizon robotic tasks is particularly challenging because failure onset is often ambiguous and dense temporal annotations are typically unavailable.

**Key idea:** Long-horizon tasks are common in real-world robotic deployments, yet failure detection for such tasks remains underexplored.

## 6. DexTeleop-0: Force-Aware Bimanual Dexterous Teleoperation with Ego-Centric Perception towards Shared Autonomy

- **Authors:** Haichao Liu, Yuyao Jiang, Hyunsun Park, Yuanjiang Xue, Ziwei Wang
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23431v1

**Why it matters:** Traditional teleoperation systems often fail in contact-rich tasks because embodiment gaps hinder accurate kinematic mapping, while tactile and force feedback remain absent.

**Key idea:** Fine-grained, bimanual dexterous manipulation remains a foundational challenge in robotics.

## 7. CoorDex: Coordinating Body and Hand Priors for Continuous Dexterous Humanoid Loco-Manipulation

- **Authors:** Sikai Li, Shuning Li, Zhenyu Wei, Yunchao Yao, Chenran Li et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23680v1

**Why it matters:** It also commonly relies on low degree-of-freedom (DoF) end effectors that behave like an open-close grasp primitive.

**Key idea:** Humanoid loco-manipulation is often simplified into a stop-and-go process: walking to an object, stopping to manipulate it, and then resuming locomotion.

### imitation / policy learning

## 8. Improving Robotic Imitation Learning via Trajectory Standardization

- **Authors:** Licheng Yang, Lingfeng Qian, Fei Zheng, Yonghao He, Wei Sui et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.22907v1

**Why it matters:** A common preprocessing strategy is time-uniform downsampling to shorten sequences, but it cannot effectively remove speed-induced non-uniformity or redundant pauses.

**Key idea:** Imitation learning for robotic manipulation relies on large sets of human demonstration trajectories, which are often noisy and temporally irregular due to variable operator speed, intermittent pauses, and inconsistent action density.

# 💻 Repositories

## 1. huggingface/lerobot

- **Authors:** huggingface
- **priority high  ·  rel 0.80  ·  nov 0.70  ·  2026-06-23  ·  via github  ·  👍 25218**
- **Link:** https://github.com/huggingface/lerobot  ·  **Code:** https://github.com/huggingface/lerobot

**Why it matters:** For Robotics readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** 🤗 LeRobot: Making AI for Robotics more accessible with end-to-end learning

## 2. rerun-io/rerun

- **Authors:** rerun-io
- **priority medium  ·  rel 0.70  ·  nov 0.60  ·  2026-06-23  ·  via github  ·  👍 10976**
- **Link:** https://github.com/rerun-io/rerun  ·  **Code:** https://github.com/rerun-io/rerun

**Why it matters:** For Robotics readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** Visualize, query, and stream to train on multimodal robotics data.

## 3. earthtojake/text-to-cad

- **Authors:** earthtojake
- **priority medium  ·  rel 0.70  ·  nov 0.60  ·  2026-06-22  ·  via github  ·  👍 6842**
- **Link:** https://github.com/earthtojake/text-to-cad  ·  **Code:** https://github.com/earthtojake/text-to-cad

**Why it matters:** For Robotics readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** A collection of agent skills for CAD, robotics and hardware design

### embodied agents

## 4. Genesis-Embodied-AI/genesis-world

- **Authors:** Genesis-Embodied-AI
- **priority high  ·  rel 1.00  ·  nov 0.70  ·  2026-06-23  ·  via github  ·  👍 29413**
- **Link:** https://github.com/Genesis-Embodied-AI/genesis-world  ·  **Code:** https://github.com/Genesis-Embodied-AI/genesis-world

**Why it matters:** For Robotics readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** Simulation platform for general-purpose robotics & embodied AI learning.

### manipulation

## 5. mani-skill/ManiSkill

- **Authors:** mani-skill
- **priority high  ·  rel 0.90  ·  nov 0.80  ·  2026-06-23  ·  via github  ·  👍 3032**
- **Link:** https://github.com/mani-skill/ManiSkill  ·  **Code:** https://github.com/mani-skill/ManiSkill

**Why it matters:** For Robotics readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** SAPIEN Manipulation Skill Framework, an open source GPU parallelized robotics simulator and benchmark

# 📝 Lab Notes

### vision-language-action (VLA)

## 1. From the Hugging Face Hub to robot hardware with Strands Agents and LeRobot

- **priority high  ·  rel 0.80  ·  nov 0.70  ·  2026-06-17  ·  via rss**
- **Link:** https://huggingface.co/blog/amazon/strands-lerobot-hub-to-hardware

**Why it matters:** For Robotics readers, this post captures a timely lab or engineering signal worth tracking.

**Key idea:** From the Hugging Face Hub to robot hardware with Strands Agents and LeRobot is surfaced as a relevant blog signal for this track.
