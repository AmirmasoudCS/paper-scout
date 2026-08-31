# Research Report: Agentic AI in data science tasks

*Generated 2026-08-31 18:44 UTC · 10 papers*

## Table of Contents

- [Cross-Paper Synthesis](#cross-paper-synthesis)
- [Future Work Ideas](#future-work-ideas)
- [Future Work Ideas (Inferred)](#future-work-ideas-inferred)
- [Papers](#papers)
  - [1. Autodata: An agentic data scientist to create high quality synthetic data](#1-autodata-an-agentic-data-scientist-to-create-high-quality-synthetic-data)
  - [2. AgenticDataBench: A Comprehensive Benchmark for Data Agents](#2-agenticdatabench-a-comprehensive-benchmark-for-data-agents)
  - [3. An LLM-Based Agentic AI System for Automated Construction of Knowledge Taxonomies in Data Science Problem Solving](#3-an-llm-based-agentic-ai-system-for-automated-construction-of-knowledge-taxonomies-in-data-science-problem-solving)
  - [4. A case study of evaluating AI agents on a neuroscience data-to-discovery pipeline](#4-a-case-study-of-evaluating-ai-agents-on-a-neuroscience-data-to-discovery-pipeline)
  - [5. Agentic-imodels: Evolving agentic interpretability tools via autoresearch](#5-agentic-imodels-evolving-agentic-interpretability-tools-via-autoresearch)
  - [6. Do LLM-Generated Skills Make Better AI Data Scientists? A Component Ablation Across Data-Science Workflows](#6-do-llm-generated-skills-make-better-ai-data-scientists-a-component-ablation-across-data-science-workflows)
  - [7. The dark side of autonomous intelligence: a survey on data leakage and privacy failures in agentic AI](#7-the-dark-side-of-autonomous-intelligence-a-survey-on-data-leakage-and-privacy-failures-in-agentic-ai)
  - [8. Toward AI VIS Co-Scientists: A General and End-to-End Agent Harness for Solving Complex Data Visualization Tasks](#8-toward-ai-vis-co-scientists-a-general-and-end-to-end-agent-harness-for-solving-complex-data-visualization-tasks)
  - [9. Towards trustworthy agentic AI: a comprehensive survey of safety, robustness, privacy, and system security](#9-towards-trustworthy-agentic-ai-a-comprehensive-survey-of-safety-robustness-privacy-and-system-security)
  - [10. REPRO-Bench: Can Agentic AI Systems Assess the Reproducibility of Social Science Research?](#10-repro-bench-can-agentic-ai-systems-assess-the-reproducibility-of-social-science-research)

## Cross-Paper Synthesis

The dominant approaches in agentic AI for data science tasks span the development of comprehensive evaluation frameworks, the architectural design of multi-agent systems, and the integration of specialized skills. Several papers focus on creating structured environments for testing and improving agents. For instance, [2] proposes AgenticDataBench to provide a benchmark covering diverse data science workflows across 15 domains, while [9] offers a survey framework that synthesizes risks across the Perceive→Plan→Act→Reflect→Learn cycle. In terms of system construction, there is a trend toward multi-agent architectures for complex reasoning and knowledge engineering; [3] details a system using Author, Critique, and Orchestrator agents to build knowledge taxonomies, and [8] presents an end-to-end agent harness for generating custom data visualization applications. Furthermore, some research focuses on enhancing the internal capabilities of the agents themselves, such as [5]'s development of Agentic-imodels to improve agent-facing interpretability alongside predictive performance.

Agreement is evident in the necessity of moving beyond single-task evaluation toward complex, multi-stage, and domain-specific pipelines. The need for rigorous, comprehensive testing is highlighted by [2] and [10], which both introduce specific, large-scale benchmarks (AgenticDataBench and REPRO-Bench, respectively) to measure agent performance across varied, real-world data science contexts. Similarly, the difficulty of achieving true end-to-end success is noted: [4] finds that while agents can solve individual stages of a scientific pipeline, solving the entire pipeline remains beyond their current capabilities. This suggests a consensus that capability improvement is incremental, requiring the successful chaining of multiple, individually competent modules.

Divergences appear in the focus of the required "skill." Some papers emphasize the *creation* or *refinement* of knowledge structures, such as [3] building formal taxonomies, while others focus on the *output* or *application* of skills. For example, [8] builds an agent harness specifically for the complex, multi-faceted task of visualization design, whereas [1] focuses on using agents to generate synthetic data, suggesting different target competencies for agentic intervention. A significant point of divergence is the empirical validation of generated skills: [6] reports that generated skills offered no significant performance improvement over simple task-only prompting, contrasting with the ambitious success claims made by systems like [1] which claim improved results using meta-optimization.

Collectively, the papers show a strong focus on the *process* and *robustness* of agentic systems, covering aspects like privacy ([7]), safety ([9]), and reproducibility ([10]). However, a notable gap exists in the systematic evaluation of agents when their primary function involves interpreting or acting upon non-structured or visual data formats *without* a pre-defined success criterion. While [4] notes agents struggle with interpreting visual inspection, and [8] tackles visualization, there is no single benchmark or framework dedicated to assessing agent performance on ambiguous, qualitative interpretation tasks that require expert human judgment beyond established metrics.

## Future Work Ideas

Here are 4 concrete future-work directions synthesized solely from the provided limitation/future work texts:

1. **Evaluating Agent Reproducibility with Data Masking:**
    * **Gap Addressed:** Assessing agent capability to reproduce research findings when key data points are intentionally masked, forcing the agent to rely only on raw data rather than full access to the paper and reproduction package.
    * **Citation:** [10] (Specifically suggests masking data points in experiment results).
    * **Overlap:** Single paper focus.

2. **Cross-Agent Leakage and System Orchestration in Privacy:**
    * **Gap Addressed:** Addressing the security vulnerability of information leakage that occurs *between* multiple agents working within a system, moving beyond model-level or context-level privacy concerns.
    * **Citation:** [7] (Explicitly lists "Cross-agent leakage" and "No system orchestration view" as limitations).
    * **Overlap:** Single paper focus.

3. **Expanding Reproducibility Benchmarks to Diverse Scientific Domains:**
    * **Gap Addressed:** Extending the evaluation framework for research reproducibility beyond the current focus (Social Science) to other critical fields, such as biology.
    * **Citation:** [10] (Suggests extending REPRO-BENCH to "biology (Begley and Ioannidis, 2015)").
    * **Overlap:** Single paper focus.

4. **Developing Advanced Agents for Automated Reproduction:**
    * **Gap Addressed:** Creating more powerful agent architectures specifically designed to automate and improve the overall process of scientific research reproduction.
    * **Citation:** [10] (Suggests developing "more powerful agents than REPRO-AGENT").
    * **Overlap:** Single paper focus.

## Future Work Ideas (Inferred)

*The directions below are inferred by the model from each paper's problem/method/key-result summary, for papers that had no extractable Limitations/Future Work section. Unlike the section above, these are not statements the authors themselves made — treat them as speculative.*

[Inferred, not author-stated] Evaluating Ambiguous Qualitative Interpretation: Future work should develop benchmarks specifically designed to assess agent performance on interpreting or acting upon non-structured or visual data formats when no pre-defined success criterion exists, as suggested by the limitations noted in [4].
[Inferred, not author-stated] Expanding Benchmark Scope to Qualitative Interpretation: Future work should extend the scope of comprehensive benchmarks to include systematic evaluation of agent performance on ambiguous, qualitative interpretation tasks that require expert human judgment beyond established metrics, addressing the gap identified by comparing the scope of benchmarks in [2] against the need for qualitative assessment.
[Inferred, not author-stated] Developing Self-Correcting Feedback Loops for Knowledge Engineering: Given that [3] uses an Author-Critique-Orchestrator loop, future work could focus on integrating external, domain-specific knowledge sources or expert feedback mechanisms into the Critique agent to improve the verifiability and grounding of the constructed taxonomy beyond the internal assessment criteria.
[Inferred, not author-stated] Benchmarking Agentic Performance on Unconstrained Visual Interpretation: Future research should build upon the visualization focus of [6] by creating an evaluation framework that specifically measures an agent's ability to interpret and reason about visual data when the required output is a qualitative assessment or interpretation, rather than a functional application build.

## Papers

### 1. Autodata: An agentic data scientist to create high quality synthetic data

Ilia Kulikov, Chenxi Whitehouse, Tianhao Wu, et al. · 2026-06-24 · *HF Papers*

[View source](https://huggingface.co/papers/2606.25996)

**Problem:** The paper addresses the challenge of creating high-quality training and evaluation data for AI models using traditional synthetic dataset creation methods.

**Method:** The authors introduce Autodata, a general method that trains (meta-optimizes) AI agents to act as data scientists who build stronger data through a specific implementation called Agentic Self-Instruct.

**Key result:** Experiments on computer science research tasks, legal reasoning tasks, and reasoning with mathematical objects show that Autodata achieves improved results compared to classical methods, with meta-optimizing the agent delivering an even larger performance uplift.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 2. AgenticDataBench: A Comprehensive Benchmark for Data Agents

Zhaoyan Sun, Shan Zhong, Daizhou Wen, et al. · 2026-07-02 · *HF Papers*

[View source](https://huggingface.co/papers/2607.01647)

**Problem:** The field lacks comprehensive benchmarks to rigorously evaluate LLM-based data agents across diverse scenarios with fine-grained granularity.

**Method:** The authors propose AgenticDataBench, which collects real datasets and tasks from 15 vertical domains, introduces a hierarchical skill extraction algorithm using LLM-based semantic refinement and agglomerative clustering, and employs systematic LLM-based task generation for domains lacking real data.

**Key result:** The benchmark enables evaluations to capture the diversity and complexity of data science workflows with detailed skill-level insights through an in-depth empirical study of state-of-the-art data agents.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 3. An LLM-Based Agentic AI System for Automated Construction of Knowledge Taxonomies in Data Science Problem Solving

Md Sakib Ul Rahman Sourove, Shimei Pan, L. Chen · 2026-06-28 · *Semantic Scholar* · 0 citations

[View source](https://www.semanticscholar.org/paper/6425bdda0d8b18d58f7f606e972f0a55dd7156d4)

**Problem:** The integration of artificial intelligence into data science practice shifts human contribution toward complex cognitive problem solving, challenging existing education models that focus on tools and techniques while lacking support for developing critical problem-solving competencies. A prerequisite to addressing this gap is formalizing Data Science Problem Solving (DSPS) competency as structured knowledge, but constructing a coherent and verifiable taxonomy of such knowledge remains a nontrivial task.

**Method:** The authors present a multi-agent LLM framework comprising an Author agent that proposes and revises taxonomies, a Critique agent that evaluates them based on explicit assessment criteria, and an Orchestrator agent that manages iterative refinement by routing feedback and enforcing stopping conditions. This system is grounded in established taxonomy construction and evaluation methods to support reflective, iterative knowledge construction rather than single-pass content generation.

**Key result:** The results demonstrate the potential of organizing LLMs into collaborative-adversarial architectures that support reflective, iterative knowledge construction and refinement. When further developed, these systems can function as a scalable framework for principled knowledge engineering, enabling the systematic design of DSPS curriculum, assessments, instructional scaffolds, and AI-assisted learning environments at scale.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 4. A case study of evaluating AI agents on a neuroscience data-to-discovery pipeline

Kai A. Horstmann, Ethan Lin, Alice A. Robie, et al. · 2026-06-05 · *HF Papers*

[View source](https://huggingface.co/papers/2606.07718)

**Problem:** The paper addresses the challenge of automating software development bottlenecks in scientific research pipelines, specifically focusing on a fly optogenetics data-to-discovery pipeline where scientists prioritize correctness and robustness over implementation details.

**Method:** The authors present an empirical study evaluating general-purpose coding agents on tasks substantially larger than existing benchmarks, using datasets orders of magnitude bigger and applying evaluation criteria grounded in domain expert standards.

**Key result:** Agents can solve several individual pipeline stages, suggesting stage-level automation is tractable, but solving the end-to-end pipeline correctly requires stringing together successes across all stages, which is beyond agents' current abilities. Additionally, agents struggle when lacking a pre-defined criterion to iterate on and often fail to appropriately interpret or act on visual inspection of intermediate outputs.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 5. Agentic-imodels: Evolving agentic interpretability tools via autoresearch

Chandan Singh, Yan Shuo Tan, Weijia Xu, et al. · 2026-05-05 · *HF Papers*

[View source](https://huggingface.co/papers/2605.03808)

**Problem:** Current agentic data science systems rely on statistical tools interpretable by humans rather than by agents, hindering autonomous analysis and interpretation of data.

**Method:** The authors introduce Agentic-imodels, an autoresearch loop that evolves a library of scikit-learn-compatible regressors for tabular data optimized for predictive performance and a novel LLM-based interpretability metric measuring simulatability by an LLM.

**Key result:** The evolved models jointly improve predictive performance and agent-facing interpretability while generalizing to new datasets and tests, and they increase downstream end-to-end agentic data science performance on the BLADE benchmark by up to 73%.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 6. Do LLM-Generated Skills Make Better AI Data Scientists? A Component Ablation Across Data-Science Workflows

Wei-Jung Huang · 2026-07-08 · *arXiv*

[View source](http://arxiv.org/abs/2607.07504v1)

**Problem:** The paper investigates whether LLM-generated skills provide a useful low-curation alternative to task-only prompting for product data scientists across four lifecycle stages: data preparation, extraction, statistical analysis, and reporting.

**Method:** The authors test full generated skills against No-Skill prompting across 56 tasks using nine model configurations and three providers (7,560 runs), then perform component ablations. A supplemental token-matched control adds 1,512 runs to compare full skills with task-irrelevant skill-formatted content.

**Key result:** Neither the full generated skill nor any ablated skill variant significantly improves performance over the task-only baseline; all p-values are at least 0.396, and the total spread across variants is only 1.2 percentage points. The token-matched control also performs similarly to the full skill.

**Stated limitations:** The study's scope is narrow, evaluating 56 single-turn tasks in one domain where only 17 fall within the informative 30 to 80% baseline range. Consequently, the 95% bootstrap CIs span ±4 to 6 percentage points, meaning the study can rule out moderate average effects.

### 7. The dark side of autonomous intelligence: a survey on data leakage and privacy failures in agentic AI

Rohini Bhosale, Pankaj Chandre, Sushma Mehetre, et al. · 2026-04-02 · *Semantic Scholar* · 2 citations

[View source](https://www.semanticscholar.org/paper/503f8f4d27757cdc2cb2910e17a5ef6f336219a8)

**Problem:** The paper addresses privacy risks and data leakage in autonomous agentic AI systems, which differ from traditional stateless models due to features like persistent memory, tool usage, and multi-agent collaboration.

**Method:** The study presents a comprehensive architectural analysis of the end-to-end agent workflow to model how sensitive information traverses components such as memory modules, reasoning processes, tools, and inter-agent communication channels, resulting in a structured taxonomy of leakage pathways mapped to threat models.

**Key result:** The findings reveal that data leakage mechanisms in agentic systems are more complex and pervasive than in traditional LLM settings due to the integration of memory and multi-agent interactions, and that existing LLM-centric privacy defenses are inadequate for these autonomous environments.

**Stated limitations:** The authors note limitations regarding system orchestration views, access isolation, and a limited taxonomy structure.

### 8. Toward AI VIS Co-Scientists: A General and End-to-End Agent Harness for Solving Complex Data Visualization Tasks

Haichao Miao, Zhimin Li, Kuangshi Ai, et al. · 2026-05-20 · *arXiv*

[View source](http://arxiv.org/abs/2605.21825v1)

**Problem:** The paper addresses the need for significant expertise in data management, analysis, visualization design, and implementation to inspect, interpret, and communicate complex data in scientific endeavors.

**Method:** The authors present an end-to-end agentic harness that autonomously designs custom visual analysis applications based only on data and high-level task descriptions. This system uses a collection of agents and specialized skills to coordinate exploratory analysis, planning, environment configuration, implementation, interface validation, and overall task evaluation.

**Key result:** The system autonomously produces functional single-page VIS Apps with verified linked-view behavior that are highly customized to domain experts' specified tasks and needs. The approach is validated on IEEE SciVis Contests spanning multiple science and engineering fields, demonstrating the ability to handle ambiguous requirements, diverse data modalities, design trade-offs, and task-driven validation.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 9. Towards trustworthy agentic AI: a comprehensive survey of safety, robustness, privacy, and system security

Jinhu Qi, Muzhi Li, Jiahong Liu, et al. · 2026-05-17 · *arXiv*

[View source](http://arxiv.org/abs/2605.23989v1)

**Problem:** Agentic AI systems can execute complex tasks autonomously, but their multi-step trajectories introduce new failure modes that challenge trustworthiness in high-risk deployments.

**Method:** The survey examines trustworthy agentic AI through two core dimensions—Safety and Robustness, and Privacy and System Security—by clarifying concepts, identifying risks along the agent workflow, and summarizing stage-targeted mitigation strategies within a Perceive→Plan→Act→Reflect→Learn framework.

**Key result:** The paper consolidates fragmented metrics and benchmark suites into a unified evaluation hub that emphasizes both outcome and process signals, such as constraint violations and adversarial success rates, to support consistent comparison and deployment decisions.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 10. REPRO-Bench: Can Agentic AI Systems Assess the Reproducibility of Social Science Research?

Chuxuan Hu, Liyun Zhang, Yeji Lim, et al. · 2025-07-25 · *Semantic Scholar* · 23 citations

[View source](https://www.semanticscholar.org/paper/3faf13f334e7b98f8c82cafec050a7bffc6dc003)

**Problem:** The paper addresses the challenge of assessing the reproducibility of social science research papers, noting that manual assessment is costly and existing benchmarks oversimplify real-world scenarios, lack diversity in data formats, or fail to assess consistency with the original paper.

**Method:** The authors introduce REPRO-Bench, a collection of 112 task instances representing social science papers with publicly available reproduction reports, and evaluate three representative AI agents on these end-to-end tasks. They also develop REPRO-Agent based on empirical analysis to improve upon existing agent performance.

**Key result:** Evaluation showed that the best-performing existing agent achieved only 21.4% accuracy in assessing reproducibility. The newly developed REPRO-Agent improved this accuracy by 71% relative, reaching 36.6%, though the authors conclude this remains insufficient for practical applications.

**Stated limitations:** ['The benchmark lacks alternative versions of task instances, such as multiple versions for the same paper incorporating intentionally erroneous or corrected code and data.', 'The study does not investigate more complex scenarios where agents are provided only with raw data rather than access to the entire paper and reproduction package.', 'The benchmark is currently limited to social science papers and has not been extended to other fields like biology where reproducibility is also critical.']
