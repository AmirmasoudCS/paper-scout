# Research Report: How to detect AI-written academic papers

*Generated 2026-08-31 16:02 UTC · 10 papers*

## Table of Contents

- [Cross-Paper Synthesis](#cross-paper-synthesis)
- [Future Work Ideas](#future-work-ideas)
- [Future Work Ideas (Inferred)](#future-work-ideas-inferred)
- [Papers](#papers)
  - [1. Sem-Detect: Semantic Level Detection of AI Generated Peer-Reviews](#1-sem-detect-semantic-level-detection-of-ai-generated-peer-reviews)
  - [2. Psychological Determinants of Academic Integrity in the Use of Generative AI in Higher Education](#2-psychological-determinants-of-academic-integrity-in-the-use-of-generative-ai-in-higher-education)
  - [3. Paper Reconstruction Evaluation: Evaluating Presentation and Hallucination in AI-written Papers](#3-paper-reconstruction-evaluation-evaluating-presentation-and-hallucination-in-ai-written-papers)
  - [4. Tensor Manifold-Based Graph-Vector Fusion for AI-Native Academic Literature Retrieval](#4-tensor-manifold-based-graph-vector-fusion-for-ai-native-academic-literature-retrieval)
  - [5. EditLens: Quantifying the Extent of AI Editing in Text](#5-editlens-quantifying-the-extent-of-ai-editing-in-text)
  - [6. Fine-Grained Detection of AI-Generated Text Using Sentence-Level
  Segmentation](#6-fine-grained-detection-of-ai-generated-text-using-sentence-level-segmentation)
  - [7. Is Your Paper Being Reviewed by an LLM? Benchmarking AI Text Detection in Peer Review](#7-is-your-paper-being-reviewed-by-an-llm-benchmarking-ai-text-detection-in-peer-review)
  - [8. Ghostbuster: Detecting Text Ghostwritten by Large Language Models](#8-ghostbuster-detecting-text-ghostwritten-by-large-language-models)
  - [9. DeTeCtive: Detecting AI-generated Text via Multi-Level Contrastive
  Learning](#9-detective-detecting-ai-generated-text-via-multi-level-contrastive-learning)
  - [10. GenAI Content Detection Task 2: AI vs. Human -- Academic Essay Authenticity Challenge](#10-genai-content-detection-task-2-ai-vs-human----academic-essay-authenticity-challenge)

## Cross-Paper Synthesis

The dominant approaches for detecting AI-written academic papers fall into three primary methodological categories: feature-level analysis, contextual/semantic analysis, and model generalization. Several papers focus on improving the technical robustness of detection. For instance, [6] and [9] address the limitation of document-level detection by proposing more granular methods; [6] uses a sentence-level sequence labeling model to pinpoint transitions between text types, while [9] employs a multi-level contrastive learning framework to learn distinct writing styles, moving beyond simple binary classification. Furthermore, several papers tackle the limitations of existing detectors by focusing on robustness. [8] introduces Ghostbuster, which circumvents the need for access to target model token probabilities by passing documents through multiple weaker language models. Similarly, [9] aims for better generalizability by designing a method that is compatible with various text encoders and excels in Out-of-Distribution (OOD) zero-shot evaluation.

Agreement among the research centers on the limitations of simple, document-level classifiers and the need for context-aware, specialized detection. In the domain of peer review, both [1] and [7] focus specifically on this niche. [1] proposes Sem-Detect, which combines textual features with claim-level semantic analysis by comparing a target review against multiple AI-generated reviews to leverage convergence patterns. [7] also addresses peer review detection, introducing a context-aware method called Anchor that leverages the manuscript content for detection, finding that AI-generated reviews are less specific and less grounded in the manuscript compared to human ones. This shows a collective agreement that the *context* of the academic writing, particularly in structured formats like reviews, is a critical factor for improving detection accuracy beyond general language patterns.

Divergences appear in the scope of the text being analyzed and the nature of the AI intervention. Some papers focus on quantifying the *degree* of AI influence, while others focus on outright classification. [5] proposes EditLens, a regression model that quantifies the *extent* of AI editing, allowing it to detect the specific degree of change made by AI to human writing, which is a more nuanced output than simple binary classification. In contrast, [1] and [7] are primarily concerned with the binary detection of whether a review is AI-written versus human-written. Another divergence is seen in the application domain: while [1] and [7] focus on peer reviews, [3] focuses on evaluating the *output* of code-generating agents by comparing generated papers against original resources to disentangle presentation quality from hallucination, representing a different evaluation goal than mere authorship detection.

Collectively, the set of papers exhibits notable gaps. While several papers address the *detection* aspect using advanced models, there is a clear gap in addressing the *pedagogical* or *institutional* response to the problem. [2] is the only paper that moves beyond the technical detection mechanism to analyze how psychological factors and institutional guidance influence academic integrity, suggesting that detection alone is insufficient. Furthermore, while [4] and [10] deal with the *utility* or *generation* of AI-related academic content—[4] for literature retrieval and [10] for essay authenticity challenges—these papers do not contribute detection methodologies; they address the problem space surrounding AI-generated academic artifacts without providing a corresponding detection framework for them.

## Future Work Ideas

Here are 4 concrete future-work directions synthesized from the authors' stated limitations and future work:

1. **Developing Robustness Against Adversarial Attacks:**
    * **Gap Addressed:** The current models lack explicit training or testing on adversarial samples, leaving them vulnerable to manipulation of linguistic structures or semantics designed to mislead detection.
    * **Citation:** [6]
    * **Overlap:** Single citation.

2. **Expanding Dataset Scope and Domain Coverage:**
    * **Gap Addressed:** Several papers note limitations regarding the scope of their training data. This includes needing to incorporate additional conferences from diverse research areas beyond the initial focus (e.g., CS domain) [7], or developing models on a larger corpus generally [9]. Furthermore, for essay authenticity, the small dataset size is a limitation [10].
    * **Citation:** [7], [9], [10]
    * **Overlap:** Multiple papers point to the need for larger/more diverse datasets.

3. **Modeling Complex Revision Scenarios and Contextual Edits:**
    * **Gap Addressed:** The current detection methods do not fully simulate the bidirectional nature of human-AI interaction. Specifically, detection scenarios need to cover the case where a *human revises an AI-generated draft*, as current work only includes AI-edits-on-human-text [7]. Additionally, evaluation should consider settings where models rely on external systems (like retrieval/references) rather than just structured inputs [3].
    * **Citation:** [7], [3]
    * **Overlap:** The need to model complex interaction/revision patterns is highlighted by [7] and [3].

4. **Improving Interpretability and Generalizability of Detection Features:**
    * **Gap Addressed:** There is a need for deeper analysis of *why* the model makes a decision. This involves exploring the interpretability of the detection mechanism, analyzing the differences and similarities between human and AI text at the token level, and conducting token-level interpretability research [9].
    * **Citation:** [9]
    * **Overlap:** Single citation.

## Future Work Ideas (Inferred)

*The directions below are inferred by the model from each paper's problem/method/key-result summary, for papers that had no extractable Limitations/Future Work section. Unlike the section above, these are not statements the authors themselves made — treat them as speculative.*

[Inferred, not author-stated] Developing graded detection for peer reviews: Since Sem-Detect focuses on a binary classification (AI vs. Human) for peer reviews, a next step could involve adapting its framework to quantify the *degree* of AI influence within a review, similar to the methodology of EditLens, to provide a more nuanced assessment of academic integrity in this specific context. (Applies to [1])
[Inferred, not author-stated] Incorporating Psychological Metrics into Detection: Given that the study on psychological determinants highlights that institutional guidance and perceived legitimacy affect integrity risk, future work could integrate quantifiable metrics derived from institutional policies or perceived academic pressure into a detection model, moving detection beyond purely linguistic features. (Applies to [2])
[Inferred, not author-stated] Integrating Temporal/Manifold Structure into Detection: Since the proposed framework for literature retrieval relies on complex temporal and manifold structures to model academic graphs, a future direction could involve applying these graph-theoretic principles to model the *structural* evolution or context dependency of text, potentially enhancing detection beyond simple local feature analysis. (Applies to [3])
[Inferred, not author-stated] Analyzing the Interaction between Editing Degree and Authorship: As EditLens quantifies the *extent* of AI editing, a plausible next step would be to use this quantification as an input feature to a detection system, allowing the model to differentiate between text that is merely *edited* by AI versus text that is *entirely generated* by AI. (Applies to [4])

## Papers

### 1. Sem-Detect: Semantic Level Detection of AI Generated Peer-Reviews

André V. Duarte, Brian Tufts, Aditya Oke, et al. · 2026-05-20 · *HF Papers*

[View source](https://huggingface.co/papers/2605.21713)

**Problem:** The paper addresses how to distinguish whether a peer review was written by a human or generated by an AI model.

**Method:** The authors propose Sem-Detect, a method that combines textual features with claim-level semantic analysis, comparing a target review against multiple AI-generated reviews of the same paper to leverage convergence patterns in AI models versus unique judgments from humans.

**Key result:** Sem-Detect improves over the strongest baseline by 25.5% in TPR@0.1% FPR in the binary setting and shows that fewer than 3.5% of LLM-refined human reviews are misclassified as AI-generated.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 2. Psychological Determinants of Academic Integrity in the Use of Generative AI in Higher Education

Ezgi Dagtekin, Ercan Erkalkan · 2026-07-06 · *arXiv*

[View source](http://arxiv.org/abs/2608.14605v1)

**Problem:** The paper addresses how psychological factors influence academically honest and dishonest uses of generative artificial intelligence (GenAI) in higher education, moving beyond viewing academic misconduct solely as a technological issue.

**Method:** The study employs a focused narrative review and conceptual synthesis design, assembling a purposive corpus of 16 core publications including peer-reviewed studies and policy-oriented texts published between 2022 and March 2026.

**Key result:** Integrity risk increases when institutional guidance is vague, peer use is normalized, academic pressure is high, and AI tools are perceived as legitimate substitutes for cognitive labor, whereas assignment-level guidance, explicit disclosure norms, ethics-oriented instruction, and authentic assessment design reduce integrity risk more effectively than detection-centered responses.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 3. Paper Reconstruction Evaluation: Evaluating Presentation and Hallucination in AI-written Papers

Atsuyuki Miyai, Mashiro Toyooka, Zaiying Zhao, et al. · 2026-04-01 · *arXiv*

[View source](http://arxiv.org/abs/2604.01128v1)

**Problem:** The paper addresses the lack of rigorous evaluation frameworks for quantifying the quality and potential risks of papers written by modern coding agents.

**Method:** The authors introduce Paper Reconstruction Evaluation (PaperRecon), a framework where an agent generates a full paper based on an overview and minimal resources, which is then compared against the original to disentangle presentation quality from hallucination. They also introduce PaperWrite-Bench, a benchmark of 51 papers from top-tier venues published after 2025.

**Key result:** Experiments reveal a clear trade-off where ClaudeCode achieves higher presentation quality at the cost of more than 10 hallucinations per paper on average, whereas Codex produces fewer hallucinations but lower presentation quality.

### 4. Tensor Manifold-Based Graph-Vector Fusion for AI-Native Academic Literature Retrieval

Xing Wei, Yang Yu · 2026-04-02 · *arXiv*

[View source](http://arxiv.org/abs/2604.16416v1)

**Problem:** Existing graph-vector fusion methods for academic literature retrieval face bottlenecks including matrix dependence, storage explosion, semantic dilution, and a lack of AI-native support.

**Method:** The paper proposes a geometry-unified graph-vector fusion framework based on tensor manifold theory that formally proves an academic literature graph is a discrete projection of a tensor manifold. Based on this conclusion, the authors design four core modules: matrix-independent temporal diffusion signature update, hierarchical temporal manifold encoding, temporal Riemannian manifold indexing, and AI-agent programmable retrieval.

**Key result:** Theoretical analysis and complexity proofs demonstrate that all core algorithms have linear time and space complexity, enabling adaptation to large-scale dynamic academic literature graphs. This provides a new theoretical framework and engineering solution for AI-native academic literature retrieval.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 5. EditLens: Quantifying the Extent of AI Editing in Text

Katherine Thai, Bradley Emi, Elyas Masrour, et al. · 2025-10-03 · *HF Papers*

[View source](https://huggingface.co/papers/2510.03154)

**Problem:** The paper addresses the detection and quantification of AI-edited text, distinguishing it from both fully human-written and fully AI-generated text.

**Method:** The authors propose using lightweight similarity metrics to quantify AI editing magnitude validated by human annotators, which serve as intermediate supervision for training EditLens, a regression model that predicts the degree of AI editing within a text.

**Key result:** EditLens achieves state-of-the-art performance on binary (F1=94.7%) and ternary (F1=90.4%) classification tasks and successfully detects both the presence of AI-edited text and the specific degree of change made by AI to human writing.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 6. Fine-Grained Detection of AI-Generated Text Using Sentence-Level
  Segmentation

Lekkala Sai Teja, Annepaka Yadagiri, Partha Pakray, et al. · 2025-09-22 · *HF Papers*

[View source](https://huggingface.co/papers/2509.17830)

**Problem:** Traditional AI detectors relying on document-level classification struggle to identify AI content in hybrid or slightly edited texts, making it difficult to distinguish between human-written and AI-generated texts.

**Method:** The authors propose a sentence-level sequence labeling model that combines state-of-the-art pre-trained Transformer models with Neural Networks and Conditional Random Fields to detect transitions between human- and AI-generated text at token-level granularity.

**Key result:** Evaluation on two publicly available benchmark datasets shows the approach can accurately detect spans of AI texts within completely collaborative texts, outperforming zero-shot detectors and existing state-of-the-art models.

**Stated limitations:** A key limitation is the lack of robustness against both syntactic and semantic adversarial attacks, as the model has not been explicitly trained or tested on adversarial samples that could manipulate linguistic structures or semantics to mislead sequence labeling.

### 7. Is Your Paper Being Reviewed by an LLM? Benchmarking AI Text Detection in Peer Review

Sungduk Yu, Man Luo, Avinash Madasu, et al. · 2025-02-26 · *arXiv*

[View source](http://arxiv.org/abs/2502.19614v3)

**Problem:** The paper addresses the risk that negligent peer reviewers rely on large language models (LLMs) to write reviews, creating a need for resources to benchmark the detectability of AI-generated text in the peer review domain.

**Method:** The authors introduce a comprehensive dataset of 788,984 AI-written peer reviews paired with human reviews from ICLR and NeurIPS spanning eight years. They evaluate 18 existing AI text detection algorithms and explore a context-aware method called Anchor that leverages manuscript content for detection.

**Key result:** Existing open-source detection methods struggle in the peer review setting, often achieving high detection rates only by falsely flagging human-written reviews. The study demonstrates that leveraging manuscript context improves accuracy while maintaining low false positive rates, and finds that AI-generated reviews are less specific, less grounded in the manuscript, and consistently assign higher scores.

**Stated limitations:** The dataset focuses primarily on two computer science conferences rather than diverse research areas. Prompt choice influences generation, and real-world use cases may involve a wider range of prompting styles than tested. The study does not simulate the reverse case where a human revises an AI-generated draft due to difficulty sourcing experts at scale. Main results are based on evaluations of three commercial LLMs, making comprehensive experiments across all available models infeasible.

### 8. Ghostbuster: Detecting Text Ghostwritten by Large Language Models

Vivek Verma, Eve Fleisig, Nicholas Tomlin, et al. · 2023-05-24 · *HF Papers*

[View source](https://huggingface.co/papers/2305.15047)

**Problem:** The paper addresses the challenge of detecting AI-generated text, particularly from black-box models or unknown model versions where access to token probabilities is unavailable.

**Method:** Ghostbuster passes documents through a series of weaker language models, performs a structured search over combinations of their features, and trains a classifier on selected features to predict whether documents are AI-generated without requiring access to the target model's token probabilities.

**Key result:** Ghostbuster achieves an F1 score of 99.0 across domains, which is 5.9 higher than the best preexisting model, and outperforms all previous approaches in generalization across writing domains, prompting strategies, and language models.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 9. DeTeCtive: Detecting AI-generated Text via Multi-Level Contrastive
  Learning

Xun Guo, Shan Zhang, Yongxin He, et al. · 2024-10-28 · *HF Papers*

[View source](https://huggingface.co/papers/2410.20964)

**Problem:** Current AI-generated text detection techniques rely on manual feature crafting and supervised binary classification, leading to performance bottlenecks, poor generalizability, and inapplicability for out-of-distribution data and newly emerged large language models.

**Method:** The authors propose DeTeCtive, a multi-task auxiliary, multi-level contrastive learning framework designed to learn distinct writing styles of different authors rather than simply classifying text as human-written or AI-generated. This approach combines style learning with a dense information retrieval pipeline and is compatible with various text encoders.

**Key result:** Extensive experiments show that DeTeCtive enhances the ability of various text encoders to detect AI-generated text across multiple benchmarks, achieving state-of-the-art results. Notably, the method outperforms existing approaches by a large margin in OOD zero-shot evaluation and possesses a Training-Free Incremental Adaptation capability for OOD data.

**Stated limitations:** The authors note that they have not thoroughly explored the method's interpretability and did not carry out training on a larger corpus.

### 10. GenAI Content Detection Task 2: AI vs. Human -- Academic Essay Authenticity Challenge

Shammur Absar Chowdhury, Hind Almerekhi, Mucahid Kutlu, et al. · 2024-12-24 · *arXiv*

[View source](http://arxiv.org/abs/2412.18274v1)

**Problem:** The paper addresses the challenge of detecting whether academic essays are generated by machines or authored by humans, specifically for English and Arabic languages.

**Method:** The study presents a shared task where teams submitted systems based on fine-tuned transformer-based models, with one team utilizing Large Language Models like Llama 2 and Llama 3, evaluated using an established framework.

**Key result:** Nearly all submitted systems outperformed the n-gram-based baseline, with top-performing systems achieving F1 scores exceeding 0.98 for both languages, indicating significant progress in detection capabilities.

**Stated limitations:** A major limitation of the dataset is its small size, particularly for Arabic, which restricts the development of more robust models due to the challenging nature of academic essay collection.
