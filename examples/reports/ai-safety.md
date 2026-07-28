# OmniSource Daily — ai-safety

*2026-06-24 · 18 signals · sources: arxiv, hf_papers, rss, github*

# 📄 论文

### robustness / adversarial

## 1. SkillHarness: Harnessing Safe Skills for Computer-Use Agents

- **Authors:** Yurun Chen, Biao Yi, Keting Yin, Shengyu Zhang
- **score 0.90  ·  priority high  ·  rel 0.90  ·  nov 0.80  ·  2026-06-02  ·  via hf_papers  ·  👍 14**
- **Link:** https://arxiv.org/abs/2606.20636  ·  **Code:** https://github.com/YurunChen/SkillHarness

**为什么值得看:** AI安全研究者应该关注SkillHarness，因为它提供了一种新的方法来确保计算机使用代理在动态环境中安全学习和使用技能，从而减少潜在的安全风险。

**核心思想:** SkillHarness通过建模技能学习和利用为一个安全约束的交互过程，引入了技能边界和选择性技能重用，以确保在动态环境中的安全性。

## 2. Can LLMs Reliably Self-Report Adversarial Prefills, and How?

- **Authors:** Quang Minh Nguyen, Uzair Ahmed, Taegyoon Kim
- **score 0.70  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23671v1

**为什么值得看:** 这项研究揭示了大型语言模型在安全上下文中自我报告的可靠性问题，直接关系到AI安全和对抗性攻击的理解。

**核心思想:** 研究表明，现有的LLM在识别自身受到对抗性预填充攻击的能力上存在显著不足，且不同的探测方法会影响模型的响应。

### red-teaming / jailbreaks

## 3. The Geometry of Refusal: Linear Instability in Safety-Aligned LLMs

- **Authors:** Shivam Ratnakar, Kartikeya Vats
- **score 0.70  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-21  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.22686v1

**为什么值得看:** 这项研究揭示了安全对齐大型语言模型的脆弱性，提供了新的方法来评估和增强模型的安全性。

**核心思想:** 引入对比逻辑引导（CLS）作为一种零优化框架，直接在输出分布上操作，以诊断安全对齐的脆弱性。

## 4. TROPT: An Open Framework for Unifying and Advancing Discrete Text Optimization

- **Authors:** Matan Ben-Tov, Mahmood Sharif
- **score 0.64  ·  priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23496v1

**为什么值得看:** AI安全研究者应该关注TROPT，因为它为模型红队和审计提供了一个统一的优化框架，促进了对模型行为的理解和控制。

**核心思想:** TROPT是一个开源框架，旨在统一和标准化离散文本优化器的开发和执行，支持多种模型和目标的定制化优化。

### alignment

## 5. Skin-Deep: A Geometric Diagnostic for Alignment Fragility in Large Language Model Representations

- **Authors:** Dongyub Jude Lee, Jungseob Lee, Seungyoon Lee, Seongtae Hong, Suhyune Son et al.
- **score 0.70  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-21  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.22676v1

**为什么值得看:** 这项研究为AI安全研究者提供了一种新的方法来检测和预防模型在对抗性微调下的对齐脆弱性。

**核心思想:** Skin-Deep是一种几何诊断工具，通过分析模型的隐藏状态激活来检测对齐脆弱性，并提供一个量化的几何脆弱性评分。

## 6. On the Limits of Prompt-Conditioned Language Models as General-Purpose Learners

- **Authors:** David Mguni, Julian Ma, Jun Wang
- **score 0.70  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.23668v1

**为什么值得看:** 这篇论文揭示了提示条件语言模型在处理复杂任务时的固有限制，对AI安全研究者理解模型的局限性至关重要。

**核心思想:** 论文提出了语言作为信息传递的容量有限通道的概念，分析了在对齐和安全约束下任务推断与执行的分离。

### interpretability

## 7. AgentLens: Interpretable Safety Steering via Mechanistic Subspaces for Multi-Turn Coding Agent

- **Authors:** Weidi Luo, Qiming Zhang, Yihao Quan, Mingyu Jin, Jie Cai et al.
- **score 0.70  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-21  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.22673v1

**为什么值得看:** 这项研究为多轮编码代理的安全性提供了新的内部视角，展示了如何通过机制解释性方法来增强AI的安全性。

**核心思想:** 提出了AgentLens框架，通过运行时安全检测和表示级干预来控制多轮编码代理的行为。

### scalable oversight

## 8. SingGuard: A Policy-Adaptive Multimodal LLM Guardrail with Dynamic Reasoning

- **Authors:**  SingGuard Team
- **score 0.70  ·  priority high  ·  rel 1.00  ·  nov 1.00  ·  2026-06-22  ·  via arxiv**
- **Link:** http://arxiv.org/abs/2606.22873v1

**为什么值得看:** AI安全研究者应关注SingGuard，因为它提供了一种动态适应的多模态安全评估方法，能够在不断变化的政策环境中有效地管理风险。

**核心思想:** SingGuard是一种政策自适应的多模态守卫模型，能够根据实时输入的自然语言规则进行安全评估。

# 💻 开源项目

### other

## 1. obra/superpowers

- **Authors:** obra
- **score 0.39  ·  priority low  ·  rel 0.20  ·  nov 0.30  ·  2026-06-23  ·  via github  ·  👍 236770**
- **Link:** https://github.com/obra/superpowers  ·  **Code:** https://github.com/obra/superpowers

**为什么值得看:** 这篇论文可能提供了一种新的方法论，但与AI安全的核心问题关系不大。

**核心思想:** 论文提出了一种代理技能框架和软件开发方法论。

## 2. NousResearch/hermes-agent

- **Authors:** NousResearch
- **score 0.38  ·  priority low  ·  rel 0.20  ·  nov 0.30  ·  2026-06-23  ·  via github  ·  👍 200676**
- **Link:** https://github.com/NousResearch/hermes-agent  ·  **Code:** https://github.com/NousResearch/hermes-agent

**为什么值得看:** 这篇论文可能涉及到与AI代理的成长和适应性相关的主题，但与AI安全的核心问题关系不大。

**核心思想:** 论文讨论了一种能够随着用户需求变化而成长的AI代理。

## 3. Significant-Gravitas/AutoGPT

- **Authors:** Significant-Gravitas
- **score 0.37  ·  priority low  ·  rel 0.20  ·  nov 0.30  ·  2026-06-23  ·  via github  ·  👍 185109**
- **Link:** https://github.com/Significant-Gravitas/AutoGPT  ·  **Code:** https://github.com/Significant-Gravitas/AutoGPT

**为什么值得看:** AI安全研究者应该关注如何确保可访问AI的安全性和对齐性。

**核心思想:** AutoGPT旨在提供可访问的AI工具，以便用户能够专注于重要事务。

## 4. langgenius/dify

- **Authors:** langgenius
- **score 0.35  ·  priority low  ·  rel 0.20  ·  nov 0.30  ·  2026-06-23  ·  via github  ·  👍 146290**
- **Link:** https://github.com/langgenius/dify  ·  **Code:** https://github.com/langgenius/dify

**为什么值得看:** 这项研究可能涉及到代理系统的开发，但与AI安全的核心问题关系不大。

**核心思想:** 该平台旨在为代理工作流开发提供生产就绪的解决方案。

## 5. openclaw/openclaw

- **Authors:** openclaw
- **score 0.30  ·  priority low  ·  rel 0.00  ·  nov 0.00  ·  2026-06-23  ·  via github  ·  👍 380113**
- **Link:** https://github.com/openclaw/openclaw  ·  **Code:** https://github.com/openclaw/openclaw

**为什么值得看:** 这篇论文与AI安全领域没有直接关系，因此对研究者没有实际价值。

**核心思想:** 该论文似乎关注于个人AI助手的开发，而不是AI安全或对齐问题。

# 📝 实验室动态

### scalable oversight

## 1. Predicting model behavior before release by simulating deployment

- **score 0.64  ·  priority high  ·  rel 1.00  ·  nov 0.80  ·  2026-06-16  ·  via rss**
- **Link:** https://openai.com/index/deployment-simulation

**为什么值得看:** 这项研究为AI安全提供了一种新的方法，通过模拟部署来预测模型行为，从而在发布前识别潜在风险。

**核心思想:** 该方法利用真实对话数据进行部署模拟，以提高AI模型的安全性和评估准确性。

## 2. A blueprint for democratic governance of frontier AI

- **score 0.50  ·  priority medium  ·  rel 0.80  ·  nov 0.60  ·  2026-06-03  ·  via rss**
- **Link:** https://openai.com/index/frontier-safety-blueprint

**为什么值得看:** 这篇论文为AI安全研究者提供了关于如何通过民主治理来确保前沿AI的安全性和韧性的框架。

**核心思想:** 论文提出了一种联邦框架，以促进前沿AI的安全、韧性和国家安全。

### other

## 3. Built to benefit everyone: our plan

- **score 0.18  ·  priority low  ·  rel 0.30  ·  nov 0.20  ·  2026-06-08  ·  via rss**
- **Link:** https://openai.com/index/built-to-benefit-everyone-our-plan

**为什么值得看:** AI-safety researchers should care about the broader vision of AI development to understand the societal implications and ethical considerations of AGI.

**核心思想:** 该论文提出了一个关于AI未来的愿景，强调了安全性和共享繁荣的重要性。

## 4. OpenAI public policy agenda

- **score 0.18  ·  priority low  ·  rel 0.30  ·  nov 0.20  ·  2026-06-03  ·  via rss**
- **Link:** https://openai.com/index/public-policy-agenda

**为什么值得看:** AI安全研究者应该关注政策议程，因为它可能影响AI安全的实施和监管。

**核心思想:** OpenAI提出了一个公共政策议程，旨在确保AI技术的安全性和社会利益。

### safety evaluation / benchmarks

## 5. Nemotron 3.5 Content Safety: Customizable Multimodal Safety for Global Enterprise AI

- **score 0.53  ·  priority medium  ·  rel 0.80  ·  nov 0.70  ·  2026-06-04  ·  via rss**
- **Link:** https://huggingface.co/blog/nvidia/nemotron-3-5-content-safety

**为什么值得看:** 这篇论文探讨了多模态安全性，提供了企业AI的定制化安全解决方案，这对AI安全研究者在设计安全系统时具有重要参考价值。

**核心思想:** 论文提出了一种可定制的多模态安全框架，旨在增强全球企业AI的内容安全性。

