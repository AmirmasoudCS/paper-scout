# Research Report: Cultural reasoning of LLMs for resource constrained languages

*Generated 2026-08-29 04:35 UTC · 10 papers*

## Table of Contents

- [Cross-Paper Synthesis](#cross-paper-synthesis)
- [Future Work Ideas](#future-work-ideas)
- [Future Work Ideas (Inferred)](#future-work-ideas-inferred)
- [Papers](#papers)
  - [1. A custom-configured large language model for Arabic academic feedback: a case study within the SSDEC curriculum](#1-a-custom-configured-large-language-model-for-arabic-academic-feedback-a-case-study-within-the-ssdec-curriculum)
  - [2. Automated MoCA scoring for Arabic speakers using hybrid AI of multimodal speech, vision, and LLM integration](#2-automated-moca-scoring-for-arabic-speakers-using-hybrid-ai-of-multimodal-speech-vision-and-llm-integration)
  - [3. XCR-Bench: A Multi-Task Benchmark for Evaluating Cultural Reasoning in LLMs](#3-xcr-bench-a-multi-task-benchmark-for-evaluating-cultural-reasoning-in-llms)
  - [4. AI-based experts' knowledge visualization of cultural heritage: A case study of Terracotta Warriors](#4-ai-based-experts-knowledge-visualization-of-cultural-heritage-a-case-study-of-terracotta-warriors)
  - [5. The Emotion Recognition Triathlon: DeepSeek vs. ChatGPT vs. Doubao](#5-the-emotion-recognition-triathlon-deepseek-vs-chatgpt-vs-doubao)
  - [6. Translating Across Cultures: LLMs for Intralingual Cultural Adaptation](#6-translating-across-cultures-llms-for-intralingual-cultural-adaptation)
  - [7. Extracting and Emulsifying Cultural Explanation to Improve Multilingual
  Capability of LLMs](#7-extracting-and-emulsifying-cultural-explanation-to-improve-multilingual-capability-of-llms)
  - [8. Evaluating Cultural Awareness of LLMs for Yoruba, Malayalam, and English](#8-evaluating-cultural-awareness-of-llms-for-yoruba-malayalam-and-english)
  - [9. Nunchi-Bench: Benchmarking Language Models on Cultural Reasoning with a
  Focus on Korean Superstition](#9-nunchi-bench-benchmarking-language-models-on-cultural-reasoning-with-a-focus-on-korean-superstition)
  - [10. Survey of Cultural Awareness in Language Models: Text and Beyond](#10-survey-of-cultural-awareness-in-language-models-text-and-beyond)

## Cross-Paper Synthesis

The dominant approaches across these papers for assessing LLM cultural reasoning are highly focused on developing specialized evaluation frameworks and benchmarks. Several studies introduce novel datasets or assessment tools to quantify cultural competence. For instance, [3] introduces XCR-Bench, which integrates Newmark's CSI framework with Hall's Triad of Culture to test for Culture-Specific Items (CSIs). Similarly, [9] creates Nunchi-Bench to specifically test cultural sensitivity using Korean superstitions. Other methods involve applying established cultural frameworks to assess LLMs, such as [8] using Hofstede's six cultural dimensions for Malayalam and Yoruba. Furthermore, some approaches tackle specific application domains, such as [1] using a case study to evaluate Arabic academic feedback, and [2] developing a multimodal system for clinical screening in Arabic-speaking settings.

A clear agreement among the papers is the observed weakness of LLMs in nuanced, context-dependent cultural reasoning. Multiple studies report that LLMs struggle when moving beyond factual knowledge or simple linguistic tasks. Specifically, [1] notes lower alignment in interpretive and culturally contextual domains when generating Arabic feedback. This pattern is echoed by [6], which finds that LLMs struggle with reasoning over cultural artifacts during translation adaptation, and [9] observes that models recognize facts but fail to apply them in practical scenarios. The need for specialized cultural enrichment is a recurring theme, as [7] proposes the EMCEI framework specifically to improve multilingual capability by extracting and balancing cultural context, and [8] highlights the failure to capture cultural nuances across regional languages.

Contradictions or divergent focuses appear in the scope of the cultural challenge addressed. Some papers focus narrowly on linguistic or domain-specific cultural adaptation, while others adopt a broader, multi-faceted view. For example, [3] focuses on the structural identification and adaptation of CSIs, whereas [5] takes a multimodal approach by testing cross-modal reasoning (text-image) for emotion recognition, which is a different type of cultural context. Additionally, while [7] focuses on improving multilingual capability via internal context extraction, [8] and [9] focus on direct, comparative evaluation across specific, non-English regional cultures (Malayalam, Yoruba, and Korean, respectively).

Collectively, the set of papers demonstrates a strong focus on creating structured benchmarks and demonstrating performance gaps in specific cultural contexts, but there is a notable gap in the systematic integration of these varied evaluation methods. While [10] surveys the field conceptually, the practical papers often address cultural awareness in isolation—either linguistically ([8]), contextually ([6]), or technically ([3]). There is a lack of a single, unified benchmark or framework that can simultaneously test for structural cultural adaptation (like XCR-Bench) alongside real-world, multi-modal application performance (like [5] or [2]) across diverse, low-resource languages.

## Future Work Ideas

Here are 5 concrete future-work directions derived exclusively from the authors' stated limitations and future work sections:

### 1. Expanding Cultural and Linguistic Coverage
*   **Gap Addressed:** The current benchmarks are limited to specific cultures, languages, or regional groups, preventing the identification of broader cultural patterns.
*   **Citation:**
    *   Expanding the CSI typology to cover Newmark's categories 1, 4, and 5 (ecology, material culture, gestures) beyond the current focus on social values, beliefs, and norms. [3]
    *   Incorporating additional languages and cultures beyond the current set (Western US/UK, Arabic, Bengali, Chinese). [3]
    *   Extending evaluation beyond the two regional languages (Malayalam and Yoruba) to cover a wider range of underrepresented languages worldwide. [8]
    *   Expanding the cultural scope beyond Korean superstitions to enable more generalizable findings across different traditions. [9]
*   **Signal Strength:** Multiple papers independently point to the need for broader geographical and cultural scope.

### 2. Developing Multi-Dimensional/Context-Specific Evaluation Techniques
*   **Gap Addressed:** Current evaluations often rely on oversimplified or single-aspect assessments (e.g., binary questions or specific CSI categories), failing to capture the full complexity of cultural reasoning.
*   **Citation:**
    *   Developing multi-dimensional scoring systems that capture the complexity of cultural interactions, moving beyond binary questions. [8]
    *   Incorporating context-dependent scenarios to assess cultural understanding in specific situations. [8]
    *   Utilizing natural language generation tasks to evaluate the LLM’s ability to produce culturally appropriate responses. [8]
    *   Expanding the CSI typology to include categories like ecology, material culture, and gestures, which represent different facets of culture. [3]
*   **Signal Strength:** Strong signal, with [8] providing a detailed list of desired improvements, and [3] pointing to structural gaps in the evaluation framework.

### 3. Improving Evaluation Robustness and Methodology
*   **Gap Addressed:** The current methods rely on limited data, single source-target pairs, or automated evaluators whose biases may limit the generalizability and reliability of the findings.
*   **Citation:**
    *   Addressing the limited dataset size and low statistical robustness, which can be mitigated by expanding the cultural and statistical coverage. [9]
    *   Developing more nuanced evaluation techniques that go beyond simple question formats, such as those that require deeper human judgment. [8]
    *   Assessing model performance across multiple prompt formulations or strategies to ensure findings are not sensitive to the initial prompt design. [3]
    *   Expanding evaluation beyond a single source-target culture pair. [6]
*   **Signal Strength:** Medium signal, with multiple papers noting limitations in data size, single-pair focus, and evaluation methodology.

### 4. Exploring Alternative Cultural Frameworks and Adaptation
*   **Gap Addressed:** Reliance on existing, specific cultural models (like Hofstede's) may constrain the assessment, necessitating the exploration of alternative or novel frameworks.
*   **Citation:**
    *   Exploring other cultural frameworks or developing entirely new ones specifically tailored for AI evaluation, rather than relying solely on established dimensions like Hofstede's. [8]
    *   Systematically expanding the CSI typology to cover structural gaps (ecology, material culture, gestures) that are not covered by the initial framework used. [3]
*   **Signal Strength:** Medium signal, pointing to the need to move beyond the current theoretical constraints of the evaluation tools.

### 5. Integrating Multimodal and Real-World Application Testing
*   **Gap Addressed:** A lack of unified testing that combines structural cultural knowledge with real-world, cross-modal, or complex application performance.
*   **Citation:**
    *   While not explicitly stated as a future work item, the combination of the multimodal focus in [5] and the need for real-world application testing (as noted in the synthesis summary) suggests a gap. More directly, the need to test performance in complex, real-world scenarios beyond controlled benchmarks is implied by the gaps identified in [1] (interpreting Arabic feedback) and the multimodal nature of [5]. (Note: This is the weakest link, but it synthesizes the gap mentioned in the prompt's narrative summary regarding the lack of integration between structural and multimodal testing.)

## Future Work Ideas (Inferred)

*The directions below are inferred by the model from each paper's problem/method/key-result summary, for papers that had no extractable Limitations/Future Work section. Unlike the section above, these are not statements the authors themselves made — treat them as speculative.*

[Inferred, not author-stated] Developing a unified benchmark for multimodal cultural reasoning: The current studies test cultural context across different modalities (e.g., [5] surveying multimodal efforts, [2] using multimodal speech/vision, [4] using text-image emotion), but there is no single framework that systematically tests cross-modal cultural reasoning across multiple cultural dimensions or languages.
[Inferred, not author-stated] Expanding the cultural scope of academic feedback evaluation: Since [1] found lower alignment in interpretive and culturally contextual domains when generating Arabic feedback, future work should systematically test the LLM's ability to handle culturally nuanced pedagogical disagreements beyond simple rubric matching.
[Inferred, not author-stated] Comparative analysis of cultural generalization across multiple languages: While [4] compares models on emotion recognition using a specific dataset structure, and [5] surveys cross-cultural datasets, no paper systematically compares the performance of different LLMs on a unified, multi-lingual dataset designed to test cultural understanding across several distinct, non-English language groups.
[Inferred, not author-stated] Integrating artifact analysis with structured cultural frameworks: The method in [3] analyzes attributes of physical cultural artifacts (Terracotta Warriors) using AI methods, but this process lacks explicit integration with established cultural frameworks (like those used in [3] or [8]) to assess the *meaning* or *cultural significance* of the derived feature distributions, rather than just the visualization of the features themselves.

## Papers

### 1. A custom-configured large language model for Arabic academic feedback: a case study within the SSDEC curriculum

Sadeq Telfah, S. Ahmed, D. Elsori · 2026-07-09 · *Semantic Scholar* · 0 citations

[View source](https://www.semanticscholar.org/paper/32b3370a6b08144ae3e63b5a7a01a7db6a4bb80b)

**Problem:** Despite increasing adoption of large language models (LLMs) in higher education, empirical evaluation of their suitability for Arabic academic feedback remains limited.

**Method:** The study presents a case-based feasibility evaluation of a custom-configured Arabic LLM designed to generate rubric-aligned academic feedback for the Emirates Studies course within the SSDEC curriculum. Design and AI-generated feedback were systematically compared with instructor-generated feedback across six anonymized student submissions using descriptive concordance analysis and qualitative thematic analysis.

**Key result:** Results indicated substantial rubric-level alignment, with the majority of comparisons classified as exact or close matches. The AI system demonstrated strong performance in procedural and rule-governed domains, while lower alignment was observed in interpretive and culturally contextual domains.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 2. Automated MoCA scoring for Arabic speakers using hybrid AI of multimodal speech, vision, and LLM integration

Yara Jehad Rabaya, Sherin Asad Qarariya, Tuqa Murad Abualhaija, et al. · 2026-07-08 · *Semantic Scholar* · 0 citations

[View source](https://www.semanticscholar.org/paper/7cdfb1119a1f27ed191e36e7e642deb6facf4d97)

**Problem:** Early detection of dementia and mild cognitive impairment (MCI) is a significant clinical challenge in Arabic-speaking and resource-limited settings where culturally adapted screening tools are scarce and access to specialized services is constrained.

**Method:** The study presents a preliminary feasibility study of an AI-powered hybrid multimodal cognitive screening system that digitizes the Arabic version of the MoCA, integrating speech processing, computer vision, and large language model-based reasoning within a unified platform using Qwen for structured reasoning.

**Key result:** The proposed hybrid approach achieved an overall diagnostic agreement of 83.3% with manual clinical scoring (Cohen's κ = 0.74), demonstrating complete output stability across five independent runs and no severe cross-category misclassifications.

**Stated limitations:** This pilot evaluation is intended to establish initial feasibility rather than definitive clinical equivalence, and the findings require validation through larger, adequately powered multisite investigations.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 3. XCR-Bench: A Multi-Task Benchmark for Evaluating Cultural Reasoning in LLMs

Mohsinul Kabir, Tasnim Ahmed, Md Mezbaur Rahman, et al. · 2026-01-20 · *HF Papers*

[View source](https://huggingface.co/papers/2601.14063)

**Problem:** The paper addresses the scarcity of high-quality CSI-annotated corpora needed to evaluate cross-cultural competence in large language models (LLMs), specifically focusing on the ability to identify Culture-Specific Items (CSIs) and adapt them across cultural contexts.

**Method:** The authors introduce XCR-Bench, a benchmark consisting of 4.9k parallel sentences and 1,098 unique CSIs spanning three reasoning tasks, which integrates Newmark's CSI framework with Hall's Triad of Culture to analyze cultural elements ranging from surface-level artifacts to social norms and values.

**Key result:** Evaluation findings show that state-of-the-art LLMs exhibit consistent weaknesses in identifying and adapting CSIs related to social etiquette and cultural reference, and evidence suggests that LLMs encode regional and ethno-religious biases even within a single linguistic setting during cultural adaptation.

**Stated limitations:** The benchmark has limited coverage of Newmark categories, focusing primarily on semi-visible and invisible culture elements while excluding ecology, material culture, and gestures. Additionally, the corpus includes CSI annotations for only four distinct cultures (Western US/UK, Arabic, Bengali, and Chinese), a constraint influenced by available resources for collaboration and annotation.

### 4. AI-based experts' knowledge visualization of cultural heritage: A case study of Terracotta Warriors

Siyi Li, Yue Jiang, Bowen Jing, et al. · 2026-04-24 · *arXiv*

[View source](http://arxiv.org/abs/2604.22480v1)

**Problem:** While advancements in 3D modeling and digital display have improved heritage depictions, existing studies often overlook visualizing cultural heritage figurines like the Terracotta Warriors as a unified entity that represents feature distribution and relationships.

**Method:** The research constructs a dataset of Terracotta Warriors from Pit No.1 detailing attributes for identification, employs AI methods such as generative adversarial networks and random forests to process and analyze these attributes, and visualizes the results for intuitive presentation.

**Key result:** The study introduces a novel scheme for presenting information on a collection of cultural relics by analyzing and visualizing the Terracotta Warriors' attributes as a whole entity rather than showcasing individual relics in isolation.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 5. The Emotion Recognition Triathlon: DeepSeek vs. ChatGPT vs. Doubao

Zhichang Liu · 2026-03-15 · *Semantic Scholar* · 0 citations

[View source](https://www.semanticscholar.org/paper/177e1a14db4a59f12090b3edf9c329fe1f5fd245)

**Problem:** The paper addresses a gap in the comparative evaluation of multimodal large language models by systematically comparing DeepSeek, ChatGPT (GPT-4o), and Doubao on emotion recognition tasks.

**Method:** The study uses a self-constructed dataset of 1,200 annotated text-image samples across three emotional scenarios to evaluate overall performance, fine-grained emotion recognition, and context sensitivity.

**Key result:** Results indicate that ChatGPT achieves the highest overall accuracy (89.5%) with superior cross-modal reasoning, Doubao excels in Chinese social contexts with an F1 score of 91.5% but has limited cross-lingual generalization, and DeepSeek performs stably in text-dominant tasks but lags in multimodal fusion scenarios.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 6. Translating Across Cultures: LLMs for Intralingual Cultural Adaptation

Pushpdeep Singh, Mayur Patidar, Lovekesh Vig · 2024-06-20 · *HF Papers*

[View source](https://huggingface.co/papers/2406.14504)

**Problem:** The paper addresses the overlooked aspect of cultural adaptation in translation, which involves modifying source culture references to suit the target culture, a task often requiring manual correction by specialized models that lack sensitivity to cultural differences.

**Method:** The authors define the task of cultural adaptation and create an evaluation framework to benchmark different models, curating a corpus of dialogues annotated with culture-specific elements for both edit-level and dialogue-level analysis.

**Key result:** Modern language models can localize context to a target culture to a significant extent but often struggle with reasoning over cultural artefacts, leading to a lack of coherence within the dialogue context and potential loss of the original message.

**Stated limitations:** ['The study uses English as the medium for intralingual adaptation to focus on culture-related modifications without translation complexities, which may not reflect how language strongly influences culture in other contexts.', "The selection of 'nation' as a proxy for culture emphasizes popular aspects while potentially neglecting local subcultures.", 'The analysis of prompts is not exhaustive due to evaluation limits when dealing with abstract cultural levels.', 'The study is confined to a single source-target culture pair, requiring specific annotations from people belonging to the target culture for extension.', 'State-of-the-art closed-source models like GPT-3.5 and GPT-4 were not evaluated due to budgetary limitations and a commitment to open science.', 'Human evaluation was limited despite showing a correlation between human and LLM judgements.']

### 7. Extracting and Emulsifying Cultural Explanation to Improve Multilingual
  Capability of LLMs

Hamin Koo, Jaehyung Kim · 2025-03-07 · *HF Papers*

[View source](https://huggingface.co/papers/2503.05846)

**Problem:** Large Language Models (LLMs) suffer from limited performance in non-English languages due to English-centric training data and a lack of cultural context in existing multilingual prompting methods.

**Method:** The authors propose EMCEI, a two-step framework that first extracts relevant cultural context from the LLM's parametric knowledge via prompting and then uses an LLM-as-Judge mechanism to select responses balancing cultural relevance and reasoning ability.

**Key result:** Experiments on diverse multilingual benchmarks show that EMCEI outperforms existing baselines, particularly in low-resource language settings, demonstrating that internally extracted context is more targeted and efficient than externally retrieved passages.

**Stated limitations:** The computational cost associated with multiple LLM inferences remains a concern, though the performance gains are substantial enough to justify the increased cost.

### 8. Evaluating Cultural Awareness of LLMs for Yoruba, Malayalam, and English

Fiifi Dawson, Zainab Mosunmola, Sahil Pocker, et al. · 2024-09-14 · *HF Papers*

[View source](https://huggingface.co/papers/2410.01811)

**Problem:** The paper addresses the lack of understanding and functionality of large language models (LLMs) for regional languages and cultures, specifically exploring their ability to comprehend cultural aspects of Malayalam and Yoruba.

**Method:** Using Hofstede's six cultural dimensions, the authors quantify the cultural awareness of LLM-based responses by constructing a survey of approximately 100 questions in both languages (translated via Google Translate API) and evaluating LLM performance on these binary Yes/No questions.

**Key result:** The study demonstrates that while LLMs show high cultural similarity for English, they fail to capture cultural nuances across the six metrics for Malayalam and Yoruba, highlighting the need for large-scale regional language LLM training with culturally enriched datasets.

**Stated limitations:** Limitations include the limited sample size of ground truth data for Malayalam and Yoruba due to scarce existing Hofstede survey information, potential inaccuracies from using machine translation, the oversimplification caused by binary question formats, and the focus on only two languages which may not represent global linguistic diversity.

### 9. Nunchi-Bench: Benchmarking Language Models on Cultural Reasoning with a
  Focus on Korean Superstition

Kyuhee Kim, Sangah Lee · 2025-07-05 · *HF Papers*

[View source](https://huggingface.co/papers/2507.04014)

**Problem:** The paper addresses the need to evaluate large language models' cultural sensitivity and reasoning skills, specifically focusing on Korean superstitions within multicultural environments.

**Method:** The authors introduce Nunchi-Bench, a benchmark consisting of 247 questions across 31 topics that assess factual knowledge, culturally appropriate advice, and situational interpretation. They evaluate multilingual LLMs in both Korean and English using a novel evaluation strategy with customized scoring metrics to capture cultural nuances.

**Key result:** Findings highlight significant challenges where models generally recognize factual information but struggle to apply it in practical scenarios. Additionally, explicit cultural framing enhances performance more effectively than relying solely on the language of the prompt.

**Stated limitations:** The benchmark's limited dataset size of 247 questions may reduce statistical robustness when comparing performance across models or subcategories. Furthermore, findings may not extend to future models with different training data, scale, or architectures due to the rapid pace of LLM development.

### 10. Survey of Cultural Awareness in Language Models: Text and Beyond

Siddhesh Pawar, Junyeong Park, Jiho Jin, et al. · 2024-10-30 · *HF Papers*

[View source](https://huggingface.co/papers/2411.00860)

**Problem:** The paper addresses the need for large language models (LLMs) to be culturally sensitive to ensure inclusivity in applications like chatbots and virtual assistants.

**Method:** The authors survey efforts to incorporate cultural awareness into text-based and multimodal LLMs, defining cultural awareness using definitions from anthropology and psychology while examining methodologies for cross-cultural datasets, strategies for downstream tasks, and benchmarking approaches.

**Key result:** The survey consolidates recent research on cultural inclusion under various themes, including the role of Human-Computer Interaction in driving cultural inclusion and ethical implications of cultural alignment.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*
