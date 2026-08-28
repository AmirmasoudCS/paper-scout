# Research Report: AI in Architecture

*Generated 2026-08-28 14:43 UTC · 10 papers*

## Table of Contents

- [Cross-Paper Synthesis](#cross-paper-synthesis)
- [Future Work Ideas](#future-work-ideas)
- [Papers](#papers)
  - [1. AI art in architecture](#1-ai-art-in-architecture)
  - [2. The role of artificial intelligence (AI) in architectural design: a systematic review of emerging technologies and applications](#2-the-role-of-artificial-intelligence-ai-in-architectural-design-a-systematic-review-of-emerging-technologies-and-applications)
  - [3. The New Shape of Search: How Conversational AI Recomposes Information Seeking](#3-the-new-shape-of-search-how-conversational-ai-recomposes-information-seeking)
  - [4. Generative AI Applications in Architecture, Engineering, and Construction: Trends, Implications for Practice, Education & Imperatives for Upskilling—A Review](#4-generative-ai-applications-in-architecture-engineering-and-construction-trends-implications-for-practice-education-imperatives-for-upskillinga-review)
  - [5. AI-Generated Smells: An Analysis of Code and Architecture in LLM and Agent-Driven Development](#5-ai-generated-smells-an-analysis-of-code-and-architecture-in-llm-and-agent-driven-development)
  - [6. Quo vadis AI in Architecture? Survey of the current possibilities of AI in the architectural practice](#6-quo-vadis-ai-in-architecture-survey-of-the-current-possibilities-of-ai-in-the-architectural-practice)
  - [7. Perceptions of generative AI in the architectural profession in Egypt: opportunities, threats, concerns for the future, and steps to improve](#7-perceptions-of-generative-ai-in-the-architectural-profession-in-egypt-opportunities-threats-concerns-for-the-future-and-steps-to-improve)
  - [8. Faith in AI can narrow the futures individuals consider](#8-faith-in-ai-can-narrow-the-futures-individuals-consider)
  - [9. Explainable AI in 6G O-RAN: A Tutorial and Survey on Architecture, Use Cases, Challenges, and Future Research](#9-explainable-ai-in-6g-o-ran-a-tutorial-and-survey-on-architecture-use-cases-challenges-and-future-research)
  - [10. Engineering AI Agents for Clinical Workflows: A Case Study in Architecture,MLOps, and Governance](#10-engineering-ai-agents-for-clinical-workflows-a-case-study-in-architecturemlops-and-governance)

## Cross-Paper Synthesis

The dominant approaches in the literature center on the practical application of generative AI and large language models (LLMs) across various stages of the architectural process. Several papers focus on the *output* capabilities of these tools, specifically analyzing diffusion-based platforms for concept design, ideation, and visualization in early-stage work, as shown in [1]. Complementing this, other works systematically survey the broader impact of AI, noting its enhancement of generative design, spatial planning, and performance analysis across the entire field [2]. A more comprehensive trend analysis identifies the transformative impact of generative AI and LLMs across the entire Architecture, Engineering, and Construction (AEC) sector, emphasizing the necessary corresponding shifts in education and professional upskilling [4].

Agreement is evident in the recognition of AI's potential to enhance creativity and efficiency. Specifically, industry professionals perceive generative AI as having promise in conceptualization and visualization, suggesting it acts as an enhancer rather than a replacement for architects [7]. Furthermore, the need for robust, reliable systems is a shared concern, though applied to different domains: [10] details the necessity of systemic oversight and modularity for trustworthy AI integration in high-stakes environments, while [4] emphasizes the need for rigorous practical training to manage the technology's implications in the AEC industry.

Divergences appear when considering the scope and nature of the AI implementation. While some papers focus on the *user experience* and *output* (e.g., [1] analyzing Midjourney queries for design workflows), others address deeper, non-design-specific technical challenges. For instance, [5] focuses on the structural degradation and technical debt inherent in *AI-generated code* itself, a concern distinct from aesthetic or functional design output. Similarly, [9] deals with the interpretability and trust mechanisms (XAI) required for autonomous systems in specialized networking infrastructure (O-RAN), while [10] mandates specific architectural patterns (Clean/Event-driven) to ensure accountability in clinical workflows.

Collectively, the set of papers exhibits notable gaps regarding the integration of design workflows with underlying engineering principles of trust and maintainability. While [1] and [7] focus on the *concept* and *visualization* phase using generative tools, there is a lack of synthesis connecting these creative outputs to the rigorous, systemic engineering requirements detailed in [10] (e.g., governance, modularity) or the code quality issues highlighted in [5]. Furthermore, the papers touch upon human decision-making under AI influence ([8]) and the evolution of information seeking ([3]), but these behavioral and information-architecture aspects are not directly mapped onto the physical or procedural design challenges of architecture itself.

## Future Work Ideas

Based *only* on the provided "Author-stated limitations and future work" text, there are no explicit future work directions available to synthesize.

The text for paper [2] only states:
*Author-stated Future Work: (not available)*

Therefore, I cannot propose any concrete future-work directions as they must be grounded in the authors' stated limitations or future work, and this information is absent for all cited papers.

## Papers

### 1. AI art in architecture

J. Ploennigs, Markus Berger · 2022-12-19 · *Semantic Scholar* · 112 citations

[View source](https://www.semanticscholar.org/paper/951016af892f5ecde12b2acd9374b92b66afb796)

**Problem:** The paper investigates how applicable diffusion-based AI art platforms are to tasks in early-stage architectural design, including ideation, sketching, and modelling.

**Method:** The authors compare the capabilities of public platforms (Midjourney, DALL·E 2, and Stable Diffusion), specify requirements for supporting common civil engineering and architecture use cases, analyze 85 million Midjourney queries using NLP to extract usage patterns, and derive workflows for interior design images and exterior design views.

**Key result:** The study establishes that diffusion-based models are powerful tools for concept design in architecture and identifies which tasks are already solvable or might soon be by combining the strengths of individual platforms into specific workflows.

### 2. The role of artificial intelligence (AI) in architectural design: a systematic review of emerging technologies and applications

I. Albukhari · 2025-07-28 · *Semantic Scholar* · 35 citations

[View source](https://www.semanticscholar.org/paper/cbd874a75e6c7402e2c97713ad5ff0ee3d20ef79)

**Problem:** The paper addresses how artificial intelligence reshapes architectural design by enhancing techniques such as spatial planning, parametric modeling, generative design, and performance-based analysis.

**Method:** A structured literature review was conducted using the PRISMA framework to analyze peer-reviewed studies on AI applications in architectural design, urban planning, and smart cities published between 2003 and 2025.

**Key result:** The reviewed studies demonstrate that AI enhances generative design, streamlines spatial organization, supports sustainable architecture, improves efficiency, and empowers architects to explore innovative solutions responsive to user needs and environmental factors.

**Stated limitations:** This study is subject to the limitation of excluding non-English literature.

### 3. The New Shape of Search: How Conversational AI Recomposes Information Seeking

Michael Iannelli, Alan Ai · 2026-07-05 · *arXiv*

[View source](http://arxiv.org/abs/2607.04282v3)

**Problem:** The paper addresses how conversational AI changes the traditional search journey, challenging the assumption that users ask a question first and then click through to documents.

**Method:** The authors link captured prompts and responses to panelists' observed searches and pageviews, reconstructing inactivity-defined cross-surface temporal sessions that include standalone assistant surfaces and search-embedded AI.

**Key result:** Content usually follows search but more often precedes assistant use, with assistant-containing sessions showing no observed external web step for 34.1% of user-weighted sessions compared to 19.5% for search-centered sessions.

### 4. Generative AI Applications in Architecture, Engineering, and Construction: Trends, Implications for Practice, Education & Imperatives for Upskilling—A Review

D. Onatayo, A. Onososen, A. Oyediran, et al. · 2024-10-18 · *Semantic Scholar* · 91 citations

[View source](https://www.semanticscholar.org/paper/ff5ab2f1ebe460ca1a04abb8c04344a9d1cc55b2)

**Problem:** The paper addresses the current landscape of generative AI and large language model (LLM) applications in the architecture, engineering, and construction (AEC) industry, focusing on trends, practical implications, educational strategies, and imperatives for upskilling.

**Method:** The study employs a six-stage systematic review methodology to analyze 120 papers sourced from Google Scholar, Scopus, and Web of Science.

**Key result:** The research identifies the transformative impact of AI on the AEC sector and education, highlighting the need for continuous professional development, formal education, and practical training to effectively leverage these technologies for sustainable infrastructure and efficient project management.

### 5. AI-Generated Smells: An Analysis of Code and Architecture in LLM and Agent-Driven Development

Yuecai Zhu, Nikolaos Tsantalis, Peter C. Rigby · 2026-05-04 · *HF Papers*

[View source](https://huggingface.co/papers/2605.02741)

**Problem:** The paper addresses the issue of long-term maintainability in AI-generated software, noting that current evaluations focus on functional correctness while overlooking technical debt.

**Method:** The authors conduct a systematic audit spanning single-file algorithmic tasks and complex agent-generated systems to identify patterns in AI-generated defects and architectural decay.

**Key result:** The study establishes a Volume-Quality Inverse Law where code volume is a near perfect predictor of structural degradation, revealing that increased model capability leads to more bloated and coupled code that neither functional correctness nor detailed prompting can mitigate.

### 6. Quo vadis AI in Architecture? Survey of the current possibilities of AI in the architectural practice

Laura Mrosla, P. Both · 2019-12-01 · *Semantic Scholar* · 19 citations

[View source](https://www.semanticscholar.org/paper/03972760e61f8550338bd1f730efb0fc59137110)

**Problem:** The paper addresses the extent to which contemporary artificial intelligence implementations and their underlying algorithms can conquer the architectural profession across all steps of architectural conception and fabrication.

**Method:** The authors discuss various concepts and examples to illustrate current AI research results in architecture and present a summary of an automation concept for the whole profession.

**Key result:** The paper illustrates that AI applications are increasingly present in the physical world and affect even human features like motivation and creativity within every step of architectural conception and fabrication approaches.

### 7. Perceptions of generative AI in the architectural profession in Egypt: opportunities, threats, concerns for the future, and steps to improve

Sara Elrawy, Bahaa Wagdy · 2025-03-04 · *Semantic Scholar* · 15 citations

[View source](https://www.semanticscholar.org/paper/bfed09bfb19289442216dbccc7e1f4fc9e5a50dd)

**Problem:** The paper addresses whether prompt-based generative AI enhances efficiency, creativity, and sustainability in architecture or threatens to replace architects, specifically examining perceptions among industry professionals in Egypt.

**Method:** The authors conducted a survey and interviews with industry experts to assess the transformative impacts of AI on architecture and explore concerns regarding its role in the profession.

**Key result:** Findings reveal strong awareness of AI's potential to enhance design quality and project outcomes, with small firms viewing AI as vital for optimizing operations and attracting clients. Overall, AI shows promise in conceptualization and visualization, enhancing creativity and efficiency, suggesting architects need to adapt to AI as a tool for innovation rather than a competitor.

### 8. Faith in AI can narrow the futures individuals consider

Aoi Naito, Hirokazu Shirado · 2026-03-30 · *arXiv*

[View source](http://arxiv.org/abs/2603.28944v2)

**Problem:** The paper addresses how artificial intelligence predictions influence human decision-making and the futures individuals consider when making choices.

**Method:** Using a behavioral implementation of Newcomb's paradox with 1,305 participants, the study examined whether perceived predictive authority of AI alters reasoning about future actions and leads people to forgo guaranteed rewards.

**Key result:** Over 40% of participants treated AI as a predictive authority about their own behavior, which significantly increased the odds of forgoing a guaranteed reward by a factor of 3.39 and reduced earnings by 10.7-42.9%. The effect persisted across different AI presentations and decision contexts even when predictions repeatedly failed.

### 9. Explainable AI in 6G O-RAN: A Tutorial and Survey on Architecture, Use Cases, Challenges, and Future Research

Bouziane Brik, Hatim Chergui, Lanfranco Zanzi, et al. · 2023-07-01 · *Semantic Scholar* · 78 citations

[View source](https://www.semanticscholar.org/paper/cbdc44a849d67912cc8349b773e09178e9e454f4)

**Problem:** The adoption of AI/ML-based smart and autonomous systems in Open Radio Access Network (O-RAN) architectures is limited by the inability of human operators to understand the decision processes of these solutions, which affects trust.

**Method:** This survey summarizes XAI methods and metrics, studies their deployment over the O-RAN Alliance RAN architecture, presents various use-cases, discusses automation of XAI pipelines, reviews security aspects, and examines relevant projects/standards.

**Key result:** The paper identifies challenges and research directions arising from the heavy adoption of AI/ML decision entities in O-RAN, focusing on how XAI can help interpret, understand, and improve trust in O-RAN operational networks.

### 10. Engineering AI Agents for Clinical Workflows: A Case Study in Architecture,MLOps, and Governance

Cláudio Lúcio do Val Lopes, João Marcus Pitta, Fabiano Belém, et al. · 2026-01-31 · *HF Papers*

[View source](https://huggingface.co/papers/2602.00751)

**Problem:** The integration of AI into clinical settings faces challenges from brittle, prototype-derived architectures and a lack of systemic oversight that creates a 'responsibility vacuum' compromising safety and accountability.

**Method:** The paper presents the 'Maria' platform, which employs a synergistic architecture combining Clean Architecture for maintainability with Event-driven architecture for resilience and auditability. It treats the Agent as the primary unit of modularity with its own autonomous MLOps lifecycle and integrates a Human-in-the-Loop governance model as an event-driven data source for continuous improvement.

**Key result:** The study demonstrates that trustworthy clinical AI is achieved through the holistic integration of four foundational engineering pillars, offering the 'Maria' platform as a reference architecture for building maintainable, scalable, and accountable AI-enabled systems in high-stakes domains.
