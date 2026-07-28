# OmniSource Daily — AI Safety

*2026-06-24 · 18 signals · English sample*

# 📄 Papers

### alignment

## 1. Skin-Deep: A Geometric Diagnostic for Alignment Fragility in Large Language Model Representations

- **Authors:** Dongyub Jude Lee, Jungseob Lee, Seungyoon Lee, Seongtae Hong, Suhyune Son et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-21  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.22676v1

**Why it matters:** This is a deployment risk for open-weight models because a checkpoint can pass refusal tests at release time and later lose refusal under low-cost downstream fine-tuning.

**Key idea:** Alignment tuning is meant to make harmful-request refusal robust, yet this safety behavior can be erased by a small set of benign fine-tuning examples.

## 2. On the Limits of Prompt-Conditioned Language Models as General-Purpose Learners

- **Authors:** David Mguni, Julian Ma, Jun Wang
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23668v1

**Why it matters:** We argue that this view overlooks a fundamental constraint: language is a compressed and capacity-limited interface for conveying task information.

**Key idea:** Large Language Models (LLMs) are frequently portrayed as general-purpose solvers capable of solving arbitrary tasks.

### red-teaming / jailbreaks

## 3. The Geometry of Refusal: Linear Instability in Safety-Aligned LLMs

- **Authors:** Shivam Ratnakar, Kartikeya Vats
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-21  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.22686v1

**Why it matters:** In this work, we investigate whether safety compliance is a deep semantic decision or a manipulable linear feature.

**Key idea:** Modern Large Language Models (LLMs) rely on extensive safety alignment, yet the mechanistic basis of refusal remains opaque.

## 4. TROPT: An Open Framework for Unifying and Advancing Discrete Text Optimization

- **Authors:** Matan Ben-Tov, Mahmood Sharif
- **priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23496v1

**Why it matters:** However, the current state of discrete optimizers hinders their adoption and progress.

**Key idea:** Discrete text-trigger optimization -- searching for text sequences that, when ingested by a model, steer it toward a specified objective -- underpins model red-teaming (e.g., LLM jailbreaks), as well as auditing and interpretability.

### robustness / adversarial

## 5. SkillHarness: Harnessing Safe Skills for Computer-Use Agents

- **Authors:** Yurun Chen, Biao Yi, Keting Yin, Shengyu Zhang
- **priority high  ·  rel 0.90  ·  nov 0.80  ·  2026-06-02  ·  via hf_papers  ·  👍 14**
- **Link:** https://arxiv.org/abs/2606.20636  ·  **Code:** https://github.com/YurunChen/SkillHarness

**Why it matters:** Recent approaches address this challenge by learning reusable skills from successful trajectories.

**Key idea:** Computer-Use Agents (CUAs) are increasingly deployed in dynamic interactive environments, creating a growing need for continual skill learning during interaction.

## 6. Can LLMs Reliably Self-Report Adversarial Prefills, and How?

- **Authors:** Quang Minh Nguyen, Uzair Ahmed, Taegyoon Kim
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23671v1

**Why it matters:** We extend the question to safety contexts and examine how reliably a model can recognize that its own prior response was elicited by an adversarial prefill attack.

**Key idea:** Prior work shows that large language models (LLMs) exhibit introspective capability on benign tasks.

### interpretability

## 7. AgentLens: Interpretable Safety Steering via Mechanistic Subspaces for Multi-Turn Coding Agent

- **Authors:** Weidi Luo, Qiming Zhang, Yihao Quan, Mingyu Jin, Jie Cai et al.
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-21  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.22673v1

**Why it matters:** Existing safety mechanisms mainly rely on external guardrails, which have a limited ability to perform fine-grained behavioral control during execution.

**Key idea:** Coding agents based on large language models (LLMs) demonstrate remarkable autonomous capabilities, but they also introduce significant safety and misuse risks during multi-turn interactions with external environments.

### scalable oversight

## 8. SingGuard: A Policy-Adaptive Multimodal LLM Guardrail with Dynamic Reasoning

- **Authors:**  SingGuard Team
- **priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.22873v1

**Why it matters:** This broad deployment expands the safety surface: risks can arise from multimodal question answering, assistant responses, and cross-modal composition, while moderation policies may vary across products, regions, and deployment stages.

**Key idea:** Vision-language models (VLMs) are increasingly deployed in consumer, medical, financial, and enterprise applications.

# 💻 Repositories

## 1. obra/superpowers

- **Authors:** obra
- **priority low  ·  rel 0.20  ·  nov 0.30  ·  2026-06-23  ·  via github  ·  👍 236770**
- **Link:** https://github.com/obra/superpowers  ·  **Code:** https://github.com/obra/superpowers

**Why it matters:** For AI Safety readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** An agentic skills framework & software development methodology that works.

## 2. NousResearch/hermes-agent

- **Authors:** NousResearch
- **priority low  ·  rel 0.20  ·  nov 0.30  ·  2026-06-23  ·  via github  ·  👍 200676**
- **Link:** https://github.com/NousResearch/hermes-agent  ·  **Code:** https://github.com/NousResearch/hermes-agent

**Why it matters:** For AI Safety readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** The agent that grows with you

## 3. Significant-Gravitas/AutoGPT

- **Authors:** Significant-Gravitas
- **priority low  ·  rel 0.20  ·  nov 0.30  ·  2026-06-23  ·  via github  ·  👍 185109**
- **Link:** https://github.com/Significant-Gravitas/AutoGPT  ·  **Code:** https://github.com/Significant-Gravitas/AutoGPT

**Why it matters:** Our mission is to provide the tools, so that you can focus on what matters.

**Key idea:** AutoGPT is the vision of accessible AI for everyone, to use and to build on.

## 4. langgenius/dify

- **Authors:** langgenius
- **priority low  ·  rel 0.20  ·  nov 0.30  ·  2026-06-23  ·  via github  ·  👍 146290**
- **Link:** https://github.com/langgenius/dify  ·  **Code:** https://github.com/langgenius/dify

**Why it matters:** For AI Safety readers, this repository is a practical artifact to inspect, compare, or reuse.

**Key idea:** Production-ready platform for agentic workflow development.

## 5. openclaw/openclaw

- **Authors:** openclaw
- **priority low  ·  rel 0.00  ·  nov 0.00  ·  2026-06-23  ·  via github  ·  👍 380113**
- **Link:** https://github.com/openclaw/openclaw  ·  **Code:** https://github.com/openclaw/openclaw

**Why it matters:** Any OS.

**Key idea:** Your own personal AI assistant.

# 📝 Lab Notes

## 1. Built to benefit everyone: our plan

- **priority low  ·  rel 0.30  ·  nov 0.20  ·  2026-06-08  ·  via rss**
- **Link:** https://openai.com/index/built-to-benefit-everyone-our-plan

**Why it matters:** For AI Safety readers, this post captures a timely lab or engineering signal worth tracking.

**Key idea:** A vision for the future of AI, focusing on access, safety, and shared prosperity as OpenAI works to ensure AGI benefits everyone.

## 2. OpenAI public policy agenda

- **priority low  ·  rel 0.30  ·  nov 0.20  ·  2026-06-03  ·  via rss**
- **Link:** https://openai.com/index/public-policy-agenda

**Why it matters:** For AI Safety readers, this post captures a timely lab or engineering signal worth tracking.

**Key idea:** OpenAI outlines its public policy agenda for AI, including safety, youth protection, workforce transition, and global standards to ensure AI benefits society.

### scalable oversight

## 3. Predicting model behavior before release by simulating deployment

- **priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-16  ·  via rss**
- **Link:** https://openai.com/index/deployment-simulation

**Why it matters:** For AI Safety readers, this post captures a timely lab or engineering signal worth tracking.

**Key idea:** OpenAI introduces Deployment Simulation, a method to predict AI model behavior before deployment using real conversation data to improve safety and evaluation accuracy.

## 4. A blueprint for democratic governance of frontier AI

- **priority medium  ·  rel 0.80  ·  nov 0.60  ·  2026-06-03  ·  via rss**
- **Link:** https://openai.com/index/frontier-safety-blueprint

**Why it matters:** governance of frontier AI, proposing a federal framework for safety, resilience, and national security.

**Key idea:** OpenAI outlines a blueprint for U.S.

### safety evaluation / benchmarks

## 5. Nemotron 3.5 Content Safety: Customizable Multimodal Safety for Global Enterprise AI

- **priority medium  ·  rel 0.80  ·  nov 0.70  ·  2026-06-04  ·  via rss**
- **Link:** https://huggingface.co/blog/nvidia/nemotron-3-5-content-safety

**Why it matters:** For AI Safety readers, this post captures a timely lab or engineering signal worth tracking.

**Key idea:** Nemotron 3.5 Content Safety: Customizable Multimodal Safety for Global Enterprise AI is surfaced as a relevant blog signal for this track.
