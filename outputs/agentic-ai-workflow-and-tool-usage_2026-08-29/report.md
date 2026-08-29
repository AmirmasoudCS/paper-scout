# Research Report: Agentic AI workflow and tool usage

*Generated 2026-08-29 06:36 UTC · 10 papers*

## Table of Contents

- [Cross-Paper Synthesis](#cross-paper-synthesis)
- [Future Work Ideas](#future-work-ideas)
- [Future Work Ideas (Inferred)](#future-work-ideas-inferred)
- [Papers](#papers)
  - [1. To Call or Not to Call: A Framework to Assess and Optimize LLM Tool Calling](#1-to-call-or-not-to-call-a-framework-to-assess-and-optimize-llm-tool-calling)
  - [2. Lessons learned from the 2025 agentic AI for science hackathon](#2-lessons-learned-from-the-2025-agentic-ai-for-science-hackathon)
  - [3. Composing Verifiable Conceptual Models via Building Blocks: Towards Design-Time Verification of Agentic AI Workflows](#3-composing-verifiable-conceptual-models-via-building-blocks-towards-design-time-verification-of-agentic-ai-workflows)
  - [4. Progressive Crystallization: Turning Agent Exploration into Deterministic, Lower-Cost Workflows in Production](#4-progressive-crystallization-turning-agent-exploration-into-deterministic-lower-cost-workflows-in-production)
  - [5. Willful Disobedience: Automatically Detecting Failures in Agentic Traces](#5-willful-disobedience-automatically-detecting-failures-in-agentic-traces)
  - [6. Towards trustworthy agentic AI: a comprehensive survey of safety, robustness, privacy, and system security](#6-towards-trustworthy-agentic-ai-a-comprehensive-survey-of-safety-robustness-privacy-and-system-security)
  - [7. From benchmarks to deployment: a comprehensive review of agentic AI evaluation](#7-from-benchmarks-to-deployment-a-comprehensive-review-of-agentic-ai-evaluation)
  - [8. Securing the Agent: Vendor-Neutral, Multitenant Enterprise Retrieval and Tool Use](#8-securing-the-agent-vendor-neutral-multitenant-enterprise-retrieval-and-tool-use)
  - [9. From prompt to platform: an agentic AI workflow for healthcare simulation scenario design](#9-from-prompt-to-platform-an-agentic-ai-workflow-for-healthcare-simulation-scenario-design)
  - [10. Harness Engineering for Agentic AI Coding Tools: An Exploratory Study](#10-harness-engineering-for-agentic-ai-coding-tools-an-exploratory-study)

## Cross-Paper Synthesis

The dominant methods across these papers cluster around three areas: establishing rigorous evaluation frameworks, implementing architectural safeguards, and optimizing the execution lifecycle. For evaluation, several studies critique the limitations of existing metrics, noting that current benchmarks often fail to capture critical operational dimensions; for instance, [7] points out that most benchmarks neglect safety or cost-efficiency, while [1] introduces a decision-theoretic framework to assess the *necessity* and *utility* of tool calls beyond simple success metrics. Architecturally, papers focus on controlling the agent's interaction with external resources, ranging from implementing granular security controls like Attribute-Based Access Control (ABAC) at the retrieval layer to prevent cross-tenant data leakage [8]. Furthermore, several works detail complex, multi-stage workflows, such as the process for designing healthcare simulations [9] or the proposed design-time verification of building blocks for workflows [3].

There is clear agreement on the necessity of moving beyond simple outcome-based testing. Several papers emphasize the need to monitor the *process* or *trajectory* of the agent. [5] introduces AgentPex to detect procedural failures—like incorrect routing—within long agentic traces, which outcome-only scoring misses. This focus on process aligns with the comprehensive survey approach of [6], which emphasizes monitoring both outcome and process signals across the Perceive→Plan→Act→Reflect→Learn cycle. Furthermore, the concept of making agentic systems production-ready is shared between [4] and [7]; [4] addresses the cost inefficiency of perpetually running agents by proposing "progressive crystallization" to convert successful exploration into deterministic, cheaper workflows, while [7] critiques the general disconnect between benchmark success and real-world viability, specifically citing cost-efficiency as a missing metric.

Divergences appear primarily in the scope and target of the safeguards. While [8] focuses on securing data access across multiple tenants using server-side gating, [3] focuses on structural integrity by verifying the *composition* of the workflow blocks at design time, which is a static, pre-runtime check. Similarly, while [6] provides a high-level consolidation of trustworthiness dimensions (Safety, Robustness, Privacy), [1] offers a highly specific, quantitative improvement mechanism by training lightweight latent estimators (LNEs) to improve the *utility* of tool calls based on model hidden states, representing a fine-grained, internal model-state intervention rather than a broad architectural or verification layer.

Collectively, the set of papers highlights a significant gap regarding the integration of cost and resource management into core evaluation and design practices. While [4] successfully addresses cost reduction in a specific AIOps context, and [1] addresses cost via budget constraints on tool use, there is no single paper that integrates cost modeling with the architectural security concerns of [8] or the structural verification of [3]. Moreover, while [2] documents a broad, hands-on exploration of agentic capabilities in science, the set lacks a unifying, general-purpose evaluation benchmark that systematically tests the confluence of *scientific rigor* (as explored in [2]) alongside *cost-aware, verifiable, and secure* execution paths.

## Future Work Ideas

Here are 4 concrete future-work directions based *only* on the provided limitations and future work text:

1. **Comprehensive Hidden-State Probing for Utility Estimation:**
    * **Gap Addressed:** The current utility estimator (LUE) shows only small, inconsistent gains, and the existing controllers only use a single fixed representation (the final-token hidden state of each model’s last layer) without searching over layers, which limits the achievable performance.
    * **Citations:** [1]
    * **Signal Strength:** Unique to [1].

2. **Improving Robustness of Factuality Scoring via Larger/Diverse Judgments:**
    * **Gap Addressed:** The factuality scores rely on an LLM-as-judge pipeline validated against a small ($n=100$), class-imbalanced sample, limiting the precise characterization of judge reliability.
    * **Citations:** [1]
    * **Signal Strength:** Unique to [1].

3. **Evaluating Tool Use in Extended Context Windows:**
    * **Gap Addressed:** The current evaluation setup uses a 4,096-token context window and 512-token generation cap, which may underestimate the value of tool use for models capable of longer reasoning or evidence integration.
    * **Citations:** [1]
    * **Signal Strength:** Unique to [1].

4. **Investigating Utility Estimation Beyond Budgeted Tool Allocation:**
    * **Gap Addressed:** While the latent need estimator (LNE) reliably improves performance under budgeted tool allocation, the utility estimation (LUE) remains an open problem.
    * **Citations:** [1]
    * **Signal Strength:** Unique to [1].

## Future Work Ideas (Inferred)

*The directions below are inferred by the model from each paper's problem/method/key-result summary, for papers that had no extractable Limitations/Future Work section. Unlike the section above, these are not statements the authors themselves made — treat them as speculative.*

[Inferred, not author-stated] Integrating Cost Modeling with Security Gating: Extend the ABAC framework to incorporate computational cost estimations during the retrieval-time gating process to ensure both data security and operational budget adherence. (Applies to [7])
[Inferred, not author-stated] Structural Verification of Cost/Security Constraints: Adapt the design-time structural verification rules to include constraints related to mandated security policies (like ABAC rules) or predicted operational costs, moving beyond purely structural compatibility checks. (Applies to [2])
[Inferred, not author-stated] Cost-Aware Progressive Crystallization: Modify the progressive crystallization mechanism to prioritize the conversion of workflows that are both frequently executed *and* involve high-cost components (e.g., complex tool calls or external API interactions) into deterministic, cheaper forms. (Applies to [3])
[Inferred, not author-stated] Benchmarking Confluence of Rigor, Cost, and Security: Develop a unified evaluation benchmark that systematically tests agentic workflows across scientific tasks, explicitly scoring for scientific rigor (as explored in [1]), cost efficiency (as discussed in [6]), and adherence to granular security/access controls (as detailed in [7]). (Applies to [1], [6], [7])

## Papers

### 1. To Call or Not to Call: A Framework to Assess and Optimize LLM Tool Calling

Qinyuan Wu, Soumi Das, Mahsa Amani, et al. · 2026-08-06 · *HF Papers*

[View source](https://huggingface.co/papers/2605.00737)

**Problem:** Agentic AI architectures augment LLMs with external tools, but tool use is not always beneficial and can incur substantial costs or harm task performance if redundant or low-utility calls are made.

**Method:** The authors introduce a framework inspired by decision-making theory that analyzes tool-use decisions through necessity, utility, and affordability using both normative and descriptive perspectives. They train lightweight latent estimators of need (LNEs) from model hidden states to improve tool decisions.

**Key result:** Models' perceived need and utility remain misaligned with their true values, particularly under budget constraints, leading to costly overuse and performance-degrading calls. The trained LNEs generally predict true need more accurately than model self-reports and improve budgeted tool allocation across model scales and tool types.

**Stated limitations:** The utility estimator (LUE) shows only small, inconsistent gains, making utility estimation an open problem. Controllers use a single fixed representation without searching over layers, factuality scores rely on an LLM-as-judge pipeline validated against a small, class-imbalanced sample, and models were served with limited context and generation windows that may understate the value of tool use for longer reasoning tasks.

### 2. Lessons learned from the 2025 agentic AI for science hackathon

Jaehyung Lee, Harichandana Neralla, Charles Rhys Campbell, et al. · 2026-06-18 · *Semantic Scholar* · 1 citations

[View source](https://www.semanticscholar.org/paper/06a96a8297a8882c9793215d9f19294154079fb5)

**Problem:** The rapid emergence of agentic AI presents new opportunities and challenges for accelerating scientific discovery through tool-augmented reasoning, autonomous workflows, and reproducible results.

**Method:** To explore these capabilities in a hands-on, community-driven setting, the authors hosted the Agentic AI for Science Hackathon 2025, which attracted 352 registered participants. Participants engaged with a unified API ecosystem centered on the fully open-access AtomGPT.org API, implementing tool calling, asynchronous agents, and multi-model reasoning to solve problems spanning materials database retrieval, literature search, mathematical reasoning, and scientific workflow automation.

**Key result:** Outcomes included working agentic prototypes, identification of failure modes in contemporary chatbots, and actionable insights into best practices for agent design in scientific contexts. The paper documents the hackathon design, task structure, and key lessons learned, highlighting how hackathon-based evaluations can complement formal benchmarks and inform the development of robust agentic AI systems for science.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 3. Composing Verifiable Conceptual Models via Building Blocks: Towards Design-Time Verification of Agentic AI Workflows

Noe Y. Flandre, Alexander C. Nwala, Philippe J. Giabbanelli · 2026-06-19 · *HF Papers*

[View source](https://huggingface.co/papers/2606.21565)

**Problem:** Current agentic AI platforms emphasize runtime safeguards but lack support for verifying workflows during system design, creating a gap analogous to composing conceptual models without verifying building block interactions.

**Method:** The authors propose a design-time verification approach that models agentic workflows as compositions of reusable building blocks and checks their compatibility through twelve structural rules implemented in a software prototype.

**Key result:** Evaluation using two openly released datasets (48 workflows with known design flaws and 168 variants altering graph structure) shows that the verifier reliably detects violations even when flawed designs are obscured through structural transformations such as splitting tasks between agents.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 4. Progressive Crystallization: Turning Agent Exploration into Deterministic, Lower-Cost Workflows in Production

Arun Malik · 2026-07-08 · *arXiv*

[View source](http://arxiv.org/abs/2607.07052v1)

**Problem:** AI agents deployed for IT operations are typically permanent cost centers because every execution requires full LLM inference, even for previously solved problems.

**Method:** The paper introduces progressive crystallization, a lifecycle that treats agent exploration as a discovery mechanism rather than a permanent execution model. It defines a three-stage execution taxonomy and an evidence-based promotion mechanism that converts repeatedly validated agent behaviors into cheaper deterministic workflows while automatically demoting regressing ones.

**Key result:** Evaluated on a production cloud networking AIOps system, the approach increased deterministic execution from 0% to 45% over eight months, reduced per-incident agent costs by more than 70% despite doubling incident volume, and improved safety through greater reproducibility and auditability.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 5. Willful Disobedience: Automatically Detecting Failures in Agentic Traces

Reshabh K Sharma, Shraddha Barke, Ben Zorn · 2026-03-25 · *Semantic Scholar* · 2 citations

[View source](https://www.semanticscholar.org/paper/023e50da8cde8ae663283aa1aea0a05c7dfe7d91)

**Problem:** AI agents embedded in real software systems execute multi-step workflows via dialogue and tool invocations, creating long agentic traces that are difficult to validate. Outcome-only benchmarks often miss critical procedural failures such as incorrect workflow routing, unsafe tool usage, or violations of prompt-specified rules.

**Method:** The paper presents AgentPex, an AI-powered tool that extracts behavioral rules from agent prompts and system instructions to automatically evaluate agentic traces for compliance with these specifications.

**Key result:** Evaluation on 424 traces from τ2-bench across telecom, retail, and airline customer service models shows that AgentPex distinguishes agent behavior across models and surfaces specification violations not captured by outcome-only scoring. It also provides fine-grained analysis by domain and metric to help developers understand agent strengths and weaknesses at scale.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 6. Towards trustworthy agentic AI: a comprehensive survey of safety, robustness, privacy, and system security

Jinhu Qi, Muzhi Li, Jiahong Liu, et al. · 2026-05-17 · *arXiv*

[View source](http://arxiv.org/abs/2605.23989v1)

**Problem:** Agentic AI systems, which are LLMs augmented with planning, tool use, memory, and long-horizon interactions, introduce new failure modes along multi-step trajectories that challenge trustworthiness in high-risk deployments.

**Method:** The paper provides a focused examination of trustworthy agentic AI through two core dimensions (Safety and Robustness; Privacy and System Security), localizes risks within a Perceive→Plan→Act→Reflect→Learn workflow, and consolidates fragmented metrics into a unified evaluation hub emphasizing both outcome and process signals.

**Key result:** The survey summarizes stage-targeted mitigation strategies for each trustworthiness dimension and presents a case study of real-world security failures in open-source agentic systems to support consistent comparison and deployment decisions.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 7. From benchmarks to deployment: a comprehensive review of agentic AI evaluation

Tanzila Kehkashan, Muhammad Abdullah, A. S. Al-Shamayleh, et al. · 2026-04-24 · *Semantic Scholar* · 0 citations

[View source](https://www.semanticscholar.org/paper/955e63110d9a05b0676757ddc21c055ac2730105)

**Problem:** The paper addresses the critical disconnect between high benchmark performance and real-world deployment viability in agentic AI systems, where current evaluation methodologies prioritize task completion over essential dimensions like cost efficiency, safety compliance, maintainability, and workflow integration.

**Method:** The authors systematically examine and critically analyze 15 major agent benchmarks across diverse domains, using software development as a primary case study to expose inadequacies in existing metrics and propose a cross-domain taxonomy along with trajectory-level evaluation frameworks.

**Key result:** The analysis reveals that evaluation methodology, not model capability, is the primary bottleneck limiting reliable deployment, evidenced by the fact that 0/15 benchmarks integrate safety or security into scoring, 0/15 include cost-efficiency metrics, and 13/15 rely exclusively on binary success measures.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 8. Securing the Agent: Vendor-Neutral, Multitenant Enterprise Retrieval and Tool Use

Francisco Javier Arceo, Varsha Prasad Narsing · 2026-05-06 · *arXiv*

[View source](http://arxiv.org/abs/2605.05287v1)

**Problem:** Enterprise deployments of Retrieval-Augmented Generation (RAG) and agentic AI systems face challenges such as multiple tenants with heterogeneous data, strict access-control requirements, regulatory compliance, and cost pressures that existing architectures do not address. A fundamental gap exists where retrieval systems rank documents by relevance rather than authorization, allowing queries from one tenant to surface another's confidential data, alongside additional shortcomings like tool-mediated disclosure and context accumulation.

**Method:** The authors introduce a layered isolation architecture combining policy-aware ingestion, retrieval-time gating, and shared inference, enforced through server-side agentic orchestration. This approach centralizes security-critical operations like tool execution authorization and state isolation on the server while allowing client-side frameworks to retain control over agent composition.

**Key result:** Empirical evaluation of an open-source implementation in OGX shows that Attribute-Based Access Control (ABAC) gating eliminates cross-tenant leakage entirely while introducing negligible overhead (~19ms). Throughput scales linearly with no gating bottleneck, and the defense operates at the retrieval layer to remain resilient to prompt injection attacks regardless of model behavior.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 9. From prompt to platform: an agentic AI workflow for healthcare simulation scenario design

F. L. Barra, Giovanna Rodella, Alessandro Costa, et al. · 2025-05-16 · *Semantic Scholar* · 42 citations

[View source](https://www.semanticscholar.org/paper/abe45d3c3d4d05c72ef9a47ba0629fa669721a4d)

**Problem:** Healthcare simulation scenario design is a resource-intensive process that requires significant time and expertise from educators.

**Method:** The study presents an AI-driven agentic workflow evolved from a ChatGPT prototype to a platform using multiple specialized AI agents for tasks like objective formulation, patient narrative generation, diagnostic data creation, and debriefing point development, orchestrated via advanced methodologies including decomposition, prompt chaining, parallelization, retrieval-augmented generation, and iterative refinement.

**Key result:** The system ensures adherence to established simulation guidelines while reducing scenario development time by approximately 70–80%, demonstrating that healthcare professionals with modest technical skills can develop these workflows without specialized AI expertise.

**Stated limitations:** Potential pitfalls include the necessity for rigorous review of AI-generated content and awareness of bias in model outputs.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 10. Harness Engineering for Agentic AI Coding Tools: An Exploratory Study

Matthias Galster, Seyedmoein Mohsenimofidi, Jai Lal Lulla, et al. · 2026-02-16 · *arXiv*

[View source](http://arxiv.org/abs/2602.14690v5)

**Problem:** The paper addresses the need to systematically analyze configuration mechanisms for agentic AI coding tools and examine how they are adopted across software development repositories.

**Method:** The authors conduct a systematic analysis of configuration mechanisms covering five tools (Claude Code, GitHub Copilot, Cursor, Gemini, and Codex) and perform an empirical study on 2,853 GitHub repositories to analyze adoption patterns of Context Files, Skills, and Subagents.

**Key result:** Context Files dominate the configuration landscape with AGENTS.md emerging as an interoperable standard across tools, while few repositories adopt advanced mechanisms like Skills and Subagents which predominantly rely on static instructions rather than executable scripts. Distinct configuration practices are forming around different tools, with Claude Code users employing the broadest range of mechanisms.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*
