# Research Report: Cultural reasoning of LLMs for resource constrained languages.

*Generated 2026-08-28 11:00 UTC · 10 papers*

## Table of Contents

- [Cross-Paper Synthesis](#cross-paper-synthesis)
- [Future Work Ideas](#future-work-ideas)
- [Papers](#papers)
  - [1. LLMs Are Not Good Strategists, Yet Memory-Enhanced Agency Boosts Reasoning](#1-llms-are-not-good-strategists-yet-memory-enhanced-agency-boosts-reasoning)
  - [2. CultureForest: Understanding and Evaluating Cultural Norm Grounded Reasoning in LLMs](#2-cultureforest-understanding-and-evaluating-cultural-norm-grounded-reasoning-in-llms)
  - [3. A custom-configured large language model for Arabic academic feedback: a case study within the SSDEC curriculum](#3-a-custom-configured-large-language-model-for-arabic-academic-feedback-a-case-study-within-the-ssdec-curriculum)
  - [4. Cultural Benchmarking of LLMs in Standard and Dialectal Arabic Dialogues](#4-cultural-benchmarking-of-llms-in-standard-and-dialectal-arabic-dialogues)
  - [5. CulturALL: Benchmarking Multilingual and Multicultural Competence of LLMs on Grounded Tasks](#5-culturall-benchmarking-multilingual-and-multicultural-competence-of-llms-on-grounded-tasks)
  - [6. Automated MoCA scoring for Arabic speakers using hybrid AI of multimodal speech, vision, and LLM integration](#6-automated-moca-scoring-for-arabic-speakers-using-hybrid-ai-of-multimodal-speech-vision-and-llm-integration)
  - [7. Toward Culturally Grounded Natural Language Processing](#7-toward-culturally-grounded-natural-language-processing)
  - [8. Building a Strong Instruction Language Model for a Less-Resourced Language](#8-building-a-strong-instruction-language-model-for-a-less-resourced-language)
  - [9. XCR-Bench: A Multi-Task Benchmark for Evaluating Cultural Reasoning in LLMs](#9-xcr-bench-a-multi-task-benchmark-for-evaluating-cultural-reasoning-in-llms)
  - [10. AI-based experts' knowledge visualization of cultural heritage: A case study of Terracotta Warriors](#10-ai-based-experts-knowledge-visualization-of-cultural-heritage-a-case-study-of-terracotta-warriors)

## Cross-Paper Synthesis

The research approaches for assessing cultural reasoning in LLMs are broadly categorized into the development of specialized, grounded benchmarks, the application of LLMs to specific cultural domains, and the engineering of advanced architectural components for reasoning. A major theme is the shift from general language understanding to assessing competence within specific, context-rich scenarios. Several papers focus on creating comprehensive evaluation sets, such as CultureForest [2] and CulturALL [5], which aim to move beyond superficial knowledge recall by incorporating diverse geographical and cross-cultural dimensions. Furthermore, the development of specialized datasets is crucial, exemplified by ArabCulture-Dialogue [4], which specifically targets the nuances of dialectal conversation in Arabic, contrasting with the more general, multi-lingual scope of CulturALL [5].

There is notable agreement regarding the limitations of current LLMs when cultural reasoning requires deep, contextual utilization rather than mere knowledge retrieval. Papers consistently point out that performance degrades when tasks move into open-ended or highly specific domains [2] and [5]. Specific cultural reasoning is often framed around identifying underlying norms or values, as seen with XCR-Bench [9], which integrates established frameworks like Newmark's CSI, and the analysis of academic feedback in culturally sensitive areas, such as interpretive domains in Arabic [3]. Moreover, the necessity of addressing linguistic variation is a shared concern, evidenced by the comparison between MSA and dialects in [4], and the focus on adapting models for less-resourced languages like Slovene [8].

Divergences appear primarily in the *type* of reasoning or resource constrained. Some studies focus on the *mechanics* of reasoning in complex environments, such as the strategic, multi-step planning framework proposed by EpicStar for game environments [1], which is distinct from the cultural reasoning benchmarks. Another divergence is between purely cultural/linguistic evaluation and functional application: [3] examines the practical utility of LLMs for academic feedback in a specific curriculum, whereas [6] applies LLM integration to a distinct, clinical domain (MoCA scoring) using multimodal inputs, suggesting that the *application* context dictates the necessary architectural enhancement.

Collectively, the set of papers reveals a gap in addressing the intersection of resource constraints, cultural reasoning, and complex, non-linguistic modalities. While [6] successfully integrates multimodal inputs (speech, vision) for a clinical task, there is no parallel work demonstrating how cultural reasoning benchmarks (like those in [2] or [9]) could be adapted to test these multimodal cultural competencies. Furthermore, while [8] addresses low-resource language adaptation, the integration of cultural grounding into the *training* process for such models, beyond simple pre-training on local texts, is not explicitly detailed across the board.

## Future Work Ideas

*No grounded future-work ideas were generated for this run — this can happen if no paper had extractable Limitations/Future Work sections.*

## Papers

### 1. LLMs Are Not Good Strategists, Yet Memory-Enhanced Agency Boosts Reasoning

Yi Wu, Zhimin Hu · 2026-08-12 · *arXiv*

[View source](http://arxiv.org/abs/2608.12626v1)

**Problem:** Strategic reasoning in Large Language Models within long-horizon environments is often limited by inconsistent subgoals and strategic drift caused by finite attention resources preventing coherence over thousands of steps.

**Method:** The authors introduce EpicStar, a framework where agents learn memory as policy by maintaining a bank of successful past episodes alongside working memory for short-term changes, using a dynamic gating mechanism to decide between executing retrieved actions or performing new reasoning via contextual fusion.

**Key result:** EpicStar significantly outperforms baseline methods in StarCraft II by achieving higher win rates and consuming an order of magnitude fewer tokens while maintaining advantages across difficulty levels and opponent strategies.

### 2. CultureForest: Understanding and Evaluating Cultural Norm Grounded Reasoning in LLMs

Yangfan Ye, Xiaocheng Feng, Jialong Tang, et al. · 2026-06-01 · *HF Papers*

[View source](https://huggingface.co/papers/2606.01879)

**Problem:** Existing research largely reduces cultural intelligence in LLMs to a knowledge-level problem, overlooking whether models can effectively utilize their acquired knowledge in realistic scenarios.

**Method:** The authors introduce CultureForest, a benchmark for Cultural Norm Grounded Reasoning comprising 5,378 examples across 8 domains and 53 countries/regions, which supports progressive evaluation from multiple-choice to open-ended generation with questions grounded in small sets of atomic norms.

**Key result:** Extensive experiments reveal that even top-tier models degrade substantially in open-ended settings accompanied by pronounced cross-region disparities. Targeted analysis uncovers patterns including limited gains from test-time reasoning, highly shared regional preference structures, markedly conservative model responses under stricter constraints, and a bottleneck where effective use of substantial cultural knowledge is hindered.

### 3. A custom-configured large language model for Arabic academic feedback: a case study within the SSDEC curriculum

Sadeq Telfah, S. Ahmed, D. Elsori · 2026-07-09 · *Semantic Scholar* · 0 citations

[View source](https://www.semanticscholar.org/paper/32b3370a6b08144ae3e63b5a7a01a7db6a4bb80b)

**Problem:** Despite increasing adoption of large language models (LLMs) in higher education, empirical evaluation of their suitability for Arabic academic feedback remains limited.

**Method:** The study conducted a case-based feasibility evaluation comparing AI-generated feedback with instructor-generated feedback across six anonymized student submissions within the SSDEC curriculum's Emirates Studies course. Descriptive concordance analysis examined rubric-level alignment, supported by qualitative thematic analysis of feedback content to identify patterns of alignment and divergence.

**Key result:** Results indicated substantial rubric-level alignment, with the AI system demonstrating strong performance in procedural domains like APA compliance and citation accuracy, while lower alignment was observed in interpretive and culturally contextual domains. Instructors engaged with AI-generated feedback as an assistive resource, selectively refining outputs rather than adopting them uncritically.

### 4. Cultural Benchmarking of LLMs in Standard and Dialectal Arabic Dialogues

Muhammad Dehan Al Kautsar, Saeed Almheiri, Momina Ahsan, et al. · 2026-04-30 · *HF Papers*

[View source](https://huggingface.co/papers/2605.00119)

**Problem:** There is a significant gap in evaluating cultural reasoning in LLMs using conversational datasets that capture culturally rich and dialectal contexts, as most Arabic benchmarks focus on short text snippets in Modern Standard Arabic (MSA) while overlooking cultural nuances in dialogues.

**Method:** The authors introduce ArabCulture-Dialogue, a culturally grounded conversational dataset covering 13 Arabic-speaking countries in both MSA and respective dialects across 12 daily-life topics and 54 fine-grained subtopics, which is used to form three benchmarking tasks: multiple-choice cultural reasoning, machine translation between MSA and dialects, and dialect-steering generation.

**Key result:** Experiments indicate that the performance gap between MSA and Arabic dialects still exists, with models performing worse on all three tasks in the dialectal setup compared to the MSA one.

### 5. CulturALL: Benchmarking Multilingual and Multicultural Competence of LLMs on Grounded Tasks

Peiqin Lin, Chenyang Lyu, Wenjiang Luo, et al. · 2026-04-21 · *HF Papers*

[View source](https://huggingface.co/papers/2604.19262)

**Problem:** Existing benchmarks for large language models prioritize generic language understanding or superficial cultural trivia, leaving the evaluation of grounded tasks where models must reason within real-world, context-rich scenarios largely unaddressed.

**Method:** The authors present CulturALL, a comprehensive benchmark built via a human-AI collaborative framework involving expert annotators and LLMs, containing 2,610 samples in 14 languages from 51 regions distributed across 16 topics to assess multilingual and multicultural competence on grounded tasks.

**Key result:** Experiments show that the best large language model achieves 44.48% accuracy on CulturALL, underscoring substantial room for improvement.

### 6. Automated MoCA scoring for Arabic speakers using hybrid AI of multimodal speech, vision, and LLM integration

Yara Jehad Rabaya, Sherin Asad Qarariya, Tuqa Murad Abualhaija, et al. · 2026-07-08 · *Semantic Scholar* · 0 citations

[View source](https://www.semanticscholar.org/paper/7cdfb1119a1f27ed191e36e7e642deb6facf4d97)

**Problem:** Early detection of dementia and mild cognitive impairment (MCI) is a significant clinical challenge in Arabic-speaking and resource-limited settings where culturally adapted screening tools are scarce and access to specialized neuropsychological services is constrained.

**Method:** The study presents a preliminary feasibility study of an AI-powered hybrid multimodal cognitive screening system that digitizes the Arabic version of the MoCA, integrating speech processing, computer vision, and large language model-based reasoning within a unified platform using a Qwen-based structured reasoning framework.

**Key result:** The proposed hybrid approach achieved an overall diagnostic agreement of 83.3% with manual clinical scoring and a Cohen's kappa of 0.74, demonstrating complete output stability across five independent runs and no severe cross-category misclassifications from Dementia to Normal.

### 7. Toward Culturally Grounded Natural Language Processing

Sina Bagheri Nezhad · 2026-03-27 · *arXiv*

[View source](http://arxiv.org/abs/2603.26013v2)

**Problem:** Multilingual NLP often fails to achieve global inclusion because linguistic coverage and cultural competence frequently diverge, treating languages as isolated rows rather than considering their communicative ecologies.

**Method:** The paper synthesizes over 50 papers covering multilingual performance inequality, cross-lingual transfer, culture-aware evaluation, and community-grounded data practices to propose a layered evaluation and reporting agenda centered on representation audits, mixed elicitation, ecological validity, community validation, adaptation provenance, within-language variation, and maintenance of living cultural resources.

**Key result:** Outcomes in multilingual NLP are shaped by factors beyond training data coverage, including tokenization, prompt language, translated benchmark design, culturally grounded supervision, modality, and the identity of authors or validators of evaluation data.

### 8. Building a Strong Instruction Language Model for a Less-Resourced Language

Domen Vreš, Tjaša Arčon, Timotej Petrič, et al. · 2026-03-02 · *arXiv*

[View source](http://arxiv.org/abs/2603.01691v1)

**Problem:** Current open-source large language models are primarily trained on English texts, leading to poorer performance on less-resourced languages and cultures.

**Method:** The authors present GaMS3-12B, a generative model for Slovene with 12 billion parameters, adapted using three-stage continual pre-training of the Gemma 3 model followed by two-stage supervised fine-tuning (SFT) on a combination of 140B tokens from multiple languages and over 200 thousand SFT examples.

**Key result:** GaMS3-12B outperforms the 12B Gemma 3 across all evaluated scenarios and performs comparably to much larger commercial GPT-4o in the Slovene LLM arena, achieving a win rate of over 60%.

### 9. XCR-Bench: A Multi-Task Benchmark for Evaluating Cultural Reasoning in LLMs

Mohsinul Kabir, Tasnim Ahmed, Md Mezbaur Rahman, et al. · 2026-01-20 · *HF Papers*

[View source](https://huggingface.co/papers/2601.14063)

**Problem:** Cross-cultural competence in large language models (LLMs) is constrained by a scarcity of high-quality Culture-Specific Item (CSI)-annotated corpora with parallel cross-cultural sentence pairs.

**Method:** The authors introduce XCR-Bench, a benchmark consisting of 4.9k parallel sentences and 1,098 unique CSIs spanning three reasoning tasks, which integrates Newmark's CSI framework with Hall's Triad of Culture to analyze cultural reasoning across surface-level artifacts and deeper elements like social norms, beliefs, and values.

**Key result:** State-of-the-art LLMs exhibit consistent weaknesses in identifying and adapting CSIs related to social etiquette and cultural reference, and evidence suggests that LLMs encode regional and ethno-religious biases even within a single linguistic setting during cultural adaptation.

### 10. AI-based experts' knowledge visualization of cultural heritage: A case study of Terracotta Warriors

Siyi Li, Yue Jiang, Bowen Jing, et al. · 2026-04-24 · *arXiv*

[View source](http://arxiv.org/abs/2604.22480v1)

**Problem:** While advancements in 3D modeling and digital display technologies have improved heritage depictions, many studies focus on individual figurines rather than visualizing cultural heritage collections like the Terracotta Warriors as a unified entity to represent feature distribution and relationships.

**Method:** The researchers constructed a dataset of Terracotta Warriors from Pit No.1 detailing attributes for identification, then employed AI methods such as generative adversarial networks and random forests to process and analyze these attributes before visualizing the results.

**Key result:** The study introduces a novel scheme for presenting information on a collection of cultural relics by analyzing and visualizing the Terracotta Warriors' attributes as a whole entity rather than showcasing individual relics in isolation.
