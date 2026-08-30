# Research Report: Use of AI in electrical engineering

*Generated 2026-08-30 08:42 UTC · 10 papers*

## Table of Contents

- [Cross-Paper Synthesis](#cross-paper-synthesis)
- [Future Work Ideas](#future-work-ideas)
- [Future Work Ideas (Inferred)](#future-work-ideas-inferred)
- [Papers](#papers)
  - [1. Agentic AI systems in electrical power systems engineering: current state-of-the-art and challenges](#1-agentic-ai-systems-in-electrical-power-systems-engineering-current-state-of-the-art-and-challenges)
  - [2. THE USE OF AI TOOLS IN ESP WITH A FOCUS ON ENGINEERING COURSES](#2-the-use-of-ai-tools-in-esp-with-a-focus-on-engineering-courses)
  - [3. Power Systems Agent Benchmark: Executable Evaluation of AI Agents in Electric Power Engineering](#3-power-systems-agent-benchmark-executable-evaluation-of-ai-agents-in-electric-power-engineering)
  - [4. Faith in AI can narrow the futures individuals consider](#4-faith-in-ai-can-narrow-the-futures-individuals-consider)
  - [5. Advancements in Electrical Engineering Through AI and Digital Twinning: A Comprehensive Review](#5-advancements-in-electrical-engineering-through-ai-and-digital-twinning-a-comprehensive-review)
  - [6. Enhancing Student Understanding in Electrical Engineering: An Android-Based e-Learning Approach](#6-enhancing-student-understanding-in-electrical-engineering-an-android-based-e-learning-approach)
  - [7. Engineering AI Agents for Clinical Workflows: A Case Study in Architecture,MLOps, and Governance](#7-engineering-ai-agents-for-clinical-workflows-a-case-study-in-architecturemlops-and-governance)
  - [8. Competing Visions of Ethical AI: A Case Study of OpenAI](#8-competing-visions-of-ethical-ai-a-case-study-of-openai)
  - [9. AITEE -- Agentic Tutor for Electrical Engineering](#9-aitee----agentic-tutor-for-electrical-engineering)
  - [10. Enhancing LLMs for Power System Simulations: A Feedback-driven Multi-agent Framework](#10-enhancing-llms-for-power-system-simulations-a-feedback-driven-multi-agent-framework)

## Cross-Paper Synthesis

The dominant approaches across these papers center on three main areas: the application of AI agents in complex engineering systems, the integration of AI into electrical engineering education, and the methodological evaluation of AI capabilities. In power systems engineering, the focus is heavily on advancing agentic AI, moving beyond simple question-answering to executable, constraint-checking tasks. For instance, [3] introduces a structured, executable benchmark for agents in electric power engineering, demanding that agents check operational constraints. This theme is echoed by efforts to enhance LLMs for power system simulations using a structured, feedback-driven multi-agent framework that incorporates error-feedback mechanisms, achieving high success rates on complex tasks [10]. Furthermore, the concept of advanced, autonomous agents is explored in the context of general systems, such as the conceptual taxonomy provided for agentic AI in power systems [1] and the need for modular, autonomous MLOps lifecycles when deploying AI in critical fields like healthcare [7].

Agreement is evident in the necessity of moving AI applications beyond mere conceptual review or simple text generation. In education, the consensus is that AI tools must be highly specialized and interactive; [9] details an agent-based tutor (AITEE) that integrates circuit reconstruction and Spice simulation, significantly outperforming baselines. Similarly, [5] notes that AI enhances digital twins for *real-time monitoring and decision support*, building on the foundational modeling capability. In the context of general AI robustness, the need for structured evaluation is paramount, as demonstrated by the specialized benchmark in [3] and the development of feedback mechanisms in [10].

Divergences appear when comparing the *nature* of the AI challenge. While [1] focuses on establishing the *taxonomy* and *state-of-the-art* applications of agentic AI in power systems, [3] immediately jumps to providing a concrete, *executable benchmark* to test these agents, suggesting a gap between conceptual review and practical validation. In the educational domain, there is a clear split: [6] uses established pedagogical models (UTAUT, CB-SEM) to evaluate a mobile application's usability, whereas [9] focuses on building a novel, domain-specific agent (AITEE) with advanced retrieval and simulation capabilities. Furthermore, while [7] details best practices for building *trustworthy* AI in clinical settings through governance and auditability, [8] analyzes the *rhetoric* surrounding AI ethics from a corporate communications standpoint, addressing governance through discourse analysis rather than architectural implementation.

Collectively, the set of papers highlights a significant gap in the *direct, integrated application of these advanced agentic concepts to pedagogy*. While [9] presents an agentic tutor, it is distinct from the high-fidelity, constraint-checking benchmarks developed for power systems [3] or the comprehensive digital twin frameworks [5]. Moreover, the ethical and governance discussions are fragmented: [8] analyzes corporate *rhetoric* of safety, [7] mandates *architectural* governance for clinical use, and [2] raises concerns about academic dishonesty in student use, but no single paper synthesizes these governance requirements across the engineering design lifecycle itself.

## Future Work Ideas

Here are 4 concrete future-work directions grounded *only* in the provided author-stated limitations and future work sections:

1. **Scaling Benchmarks to Industrial Data Volumes:**
    * **Gap Addressed:** The current public benchmarks are limited to "compact" networks and short time series, failing to test agent performance when scaled to the volume of real-world industrial data.
    * **Citation:** [3]
    * **Signal Strength:** Single paper.

2. **Validating Agents Against Professional Power System Tools:**
    * **Gap Addressed:** The existing benchmark does not measure the agent's ability to operate within professional power-system software; the tasks are self-contained and do not require interaction with industry-standard tools.
    * **Citation:** [3]
    * **Signal Strength:** Single paper.

3. **Empirical Correlation of Ethical Rhetoric with Technical Compliance:**
    * **Gap Addressed:** Future research must move beyond analyzing the *dialogue* surrounding AI ethics (like corporate statements) to empirically testing how those stated ethical positions align with actual technical development practices and compliance with emerging regulations.
    * **Citation:** [8]
    * **Signal Strength:** Single paper.

4. **Comparative Industry-Wide Analysis of AI Governance Trends:**
    * **Gap Addressed:** Research needs to broaden the scope of ethical dialogue analysis beyond a single company (OpenAI) to evaluate trends across the entire industry, considering variations based on the firm, market maturity, and geopolitical location.
    * **Citation:** [8]
    * **Signal Strength:** Single paper.

## Future Work Ideas (Inferred)

*The directions below are inferred by the model from each paper's problem/method/key-result summary, for papers that had no extractable Limitations/Future Work section. Unlike the section above, these are not statements the authors themselves made — treat them as speculative.*

[Inferred, not author-stated] Integrating Pedagogical Assessment with System Architecture: The next step could involve applying the rigorous, multi-pillar architectural and governance framework developed for clinical AI systems to the development and evaluation of specialized educational agents, ensuring the tutor's MLOps lifecycle and human-in-the-loop mechanisms are formalized for pedagogical reliability. (Applies to [7] and [6])
[Inferred, not author-stated] Developing Executable Benchmarks for Educational Agents: Given the success of creating structured, executable benchmarks for power system agents, a direct extension would be to develop a similarly rigorous, executable benchmark suite specifically designed to test the complex, multi-step reasoning and simulation capabilities of educational agents like AITEE. (Applies to [3] and [7])
[Inferred, not author-stated] Modeling Ethical Failure Modes in Simulation: The success of the feedback-driven multi-agent framework in power systems could be extended to model and test the failure modes related to ethical or pedagogical constraints (e.g., academic dishonesty, bias in feedback) within a simulated learning environment. (Applies to [2], [8], and [1])

## Papers

### 1. Agentic AI systems in electrical power systems engineering: current state-of-the-art and challenges

Soham Ghosh, Gaurav Mittal · 2025-11-18 · *Semantic Scholar* · 7 citations

[View source](https://www.semanticscholar.org/paper/883e8e7f77c5172341e40ee07f557dea4b8cfce1)

**Problem:** The paper addresses the need for a clear conceptual and taxonomical understanding of agentic AI systems to differentiate this new paradigm from traditional AI agents and contemporary generative AI models, specifically within the context of electrical power systems engineering.

**Method:** The authors provide a comprehensive review that establishes a precise definition and taxonomy for agentic AI, introduce concepts through diverse applications in engineering, present four detailed state-of-the-art use-case applications in electrical power systems, and discuss challenges through detailed failure mode investigations.

**Key result:** The study demonstrates current and innovative state-of-the-art agentic AI applications ranging from advanced frameworks for streamlining complex power system studies to novel systems for survival analysis of dynamic pricing strategies in battery swapping stations, driven by global trends toward clean energy transition and grid automation.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 2. THE USE OF AI TOOLS IN ESP WITH A FOCUS ON ENGINEERING COURSES

Diana Marcu · 2026-07-22 · *Semantic Scholar* · 0 citations

[View source](https://www.semanticscholar.org/paper/063b25b488900e4fced1f0b21c762b093f7ecc73)

**Problem:** The paper addresses the use of Artificial Intelligence tools in English for Specific Purposes (ESP) instruction, specifically within engineering courses at the University of Craiova, Romania.

**Method:** It adopts an exploratory approach based on the analysis of current AI tools and combines personal teaching experience with the perspectives of Electrical Engineering students regarding AI platform usage.

**Key result:** AI-driven tools offer benefits such as personalized learning, real-time feedback, automated assessment, domain-specific instruction, and support for specialized vocabulary acquisition. However, their successful integration depends on pedagogical, ethical, and practical factors, and they present drawbacks including infrastructure inequities, concerns over accurate content, hindering of creativity, and apprehensions over academic dishonesty.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 3. Power Systems Agent Benchmark: Executable Evaluation of AI Agents in Electric Power Engineering

Sergei Trashchenkov · 2026-07-02 · *HF Papers*

[View source](https://huggingface.co/papers/2606.20950)

**Problem:** The paper addresses the lack of an executable benchmark for AI agents in electric power engineering, where current assessment relies on textual retrieval and question answering rather than checking the consequences of actions with programs.

**Method:** The authors introduce the Power Systems Agent Benchmark, which provides structured tasks grounded in citable sources or standards; a deterministic evaluator recomputes engineering quantities to check operational constraints and returns a feasibility flag, normalized score, and explicit violations. The benchmark includes 41 task families across eight power engineering areas, uses held-out cases synthesized by private seeds to resist contamination, and employs a quality-control procedure where unanimous agent failures signal potential defects.

**Key result:** In a reference evaluation with three command-line agents, the strongest agent scored near the compact tier's ceiling while a smaller open model trailed, and public and held-out performance remained consistent. The benchmark successfully identified specification defects and a latent bug in an evaluator's physics that self-consistency checks had missed.

**Stated limitations:** The public cases are compact networks rather than industrial-scale data volumes, the evaluators are deterministic surrogates without claims of industrial AC accuracy, and the ranking over 41 points is statistically fragile. Additionally, tasks are self-contained and do not require agents to operate professional power-system software, so the benchmark does not yet measure mastery of simulators used in real engineering work.

### 4. Faith in AI can narrow the futures individuals consider

Aoi Naito, Hirokazu Shirado · 2026-03-30 · *arXiv*

[View source](http://arxiv.org/abs/2603.28944v2)

**Problem:** The paper addresses how artificial intelligence predictions influence human decision-making and reasoning in a behavioral implementation of Newcomb's paradox.

**Method:** Using a behavioral implementation of Newcomb's paradox with 1,305 participants, the study examined whether perceived predictive authority of AI alters how people reason about their future actions and decide on guaranteed rewards.

**Key result:** Over 40% of participants treated AI as a predictive authority about their own behavior, which significantly increased the odds of forgoing a guaranteed reward by a factor of 3.39 and reduced earnings by 10.7-42.9%. The effect was consistent across different AI presentations and decision contexts and remained detectable even when predictions repeatedly failed.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 5. Advancements in Electrical Engineering Through AI and Digital Twinning: A Comprehensive Review

Krishna Kumar, Rajan Kumar, Deepak Kumar, et al. · 2024-06-05 · *Semantic Scholar* · 1 citations

[View source](https://www.semanticscholar.org/paper/49ec2a7e5b0833ebb6f805c4e371bfa72192e2b7)

**Problem:** The paper addresses the applications of digital twin technology and artificial intelligence in electrical power engineering.

**Method:** The authors provide an overview of digital twin technology for modelling power systems, predictive maintenance, and optimization, while highlighting the role of AI in enhancing real-time monitoring and decision support capabilities.

**Key result:** The paper discusses how AI enhances digital twins for real-time monitoring and decision support, citing a specific framework by Xu et al. for AI-driven predictive maintenance of electrical machines.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 6. Enhancing Student Understanding in Electrical Engineering: An Android-Based e-Learning Approach

Eko Supraptono · *Semantic Scholar* · 3 citations

[View source](https://www.semanticscholar.org/paper/b3682ee4df024154cc6fd984cef4068528cecebf)

**Problem:** The paper addresses the need to enhance student understanding of electronics concepts in electrical engineering education through an effective mobile learning application.

**Method:** The researchers developed and evaluated an Android-based intelligent learning application using the ADDIE framework, analyzed technology acceptance factors via the UTAUT model, and assessed implementation effects using Covariance-Based Structural Equation Modeling (CB-SEM).

**Key result:** The application achieved high suitability ratings from experts (85% for material experts and 82.22% for media experts), with CB-SEM analysis showing that Perceived Ease of Use and App Interactivity significantly influenced Perceived Usefulness, which in turn positively impacted Learning Outcomes.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 7. Engineering AI Agents for Clinical Workflows: A Case Study in Architecture,MLOps, and Governance

Cláudio Lúcio do Val Lopes, João Marcus Pitta, Fabiano Belém, et al. · 2026-01-31 · *arXiv*

[View source](http://arxiv.org/abs/2602.00751v1)

**Problem:** The integration of AI into clinical settings faces challenges from brittle, prototype-derived architectures and a lack of systemic oversight that creates a 'responsibility vacuum' compromising safety and accountability.

**Method:** The paper presents an industry case study of the 'Maria' platform using a synergistic architecture combining Clean Architecture for maintainability with Event-driven architecture for resilience and auditability, treating the Agent as the primary unit of modularity with its own autonomous MLOps lifecycle, and integrating a Human-in-the-Loop governance model as an event-driven data source.

**Key result:** The study demonstrates that trustworthy clinical AI is achieved through the holistic integration of four foundational engineering pillars: maintainability, resilience/auditability, modular agent-based MLOps, and integrated human-in-the-loop governance.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 8. Competing Visions of Ethical AI: A Case Study of OpenAI

Melissa Wilfley, Mengting Ai, Madelyn Rose Sanfilippo · 2026-01-23 · *arXiv*

[View source](http://arxiv.org/abs/2601.16513v1)

**Problem:** The paper addresses how AI ethics is framed distinctly across different actors and stakeholder groups by analyzing OpenAI's public discourse on ethical AI.

**Method:** A structured corpus of OpenAI's public documentation was assembled, differentiated between general and academic audiences, and analyzed using qualitative content analysis combined with inductively derived and deductively applied codes, as well as quantitative computational content analysis via NLP to model topics and quantify rhetorical changes over time.

**Key result:** Results indicate that safety and risk discourse dominate OpenAI's public communication and documentation without applying academic or advocacy ethics frameworks or vocabularies. The study identifies significant 'ethics-washing' practices, showing a shift toward emphasis on safety, risk, and compliance rather than nuanced ethos or meaningful social benefits.

### 9. AITEE -- Agentic Tutor for Electrical Engineering

Christopher Knievel, Alexander Bernhardt, Christian Bernhardt · 2025-05-27 · *HF Papers*

[View source](https://huggingface.co/papers/2505.21582)

**Problem:** The paper addresses the limitations of traditional educational technologies and large language models in electrical engineering education, specifically their insufficiency in addressing specific questions about electrical circuits and the teacher bandwidth problem.

**Method:** AITEE is an agent-based tutoring system that supports both hand-drawn and digital circuits through an adapted circuit reconstruction process. It employs a novel graph-based similarity measure for retrieval augmented generation from lecture materials, parallel Spice simulation for accuracy, and implements a Socratic dialogue to foster learner autonomy.

**Key result:** Experimental evaluations show that AITEE significantly outperforms baseline approaches in domain-specific knowledge application, with even medium-sized LLM models showing acceptable performance. The graph-based similarity measure effectively retrieves relevant contextual information from lecture materials.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 10. Enhancing LLMs for Power System Simulations: A Feedback-driven Multi-agent Framework

Mengshuo Jia, Zeyu Cui, Gabriela Hug · 2024-11-21 · *HF Papers*

[View source](https://huggingface.co/papers/2411.16707)

**Problem:** The paper addresses the challenge of managing power system simulations for large language models (LLMs), which is hindered by their limited domain-specific knowledge, restricted reasoning capabilities, and imprecise handling of simulation parameters.

**Method:** The authors propose a feedback-driven, multi-agent framework incorporating three modules: an enhanced retrieval-augmented generation (RAG) module, an improved reasoning module, and a dynamic environmental acting module with an error-feedback mechanism.

**Key result:** Validated on 69 diverse tasks from Daline and MATPOWER, the framework achieves success rates of 93.13% and 96.85%, respectively, significantly outperforming ChatGPT 4o, o1-preview, and fine-tuned GPT-4o which achieved success rates lower than 30% on complex tasks.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*
