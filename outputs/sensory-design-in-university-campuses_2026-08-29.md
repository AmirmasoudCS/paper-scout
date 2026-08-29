# Research Report: Sensory design in university campuses

*Generated 2026-08-29 04:57 UTC · 10 papers*

## Table of Contents

- [Cross-Paper Synthesis](#cross-paper-synthesis)
- [Future Work Ideas](#future-work-ideas)
- [Future Work Ideas (Inferred)](#future-work-ideas-inferred)
- [Papers](#papers)
  - [1. Cross Sensory Co-Design Tools and Interaction Qualities](#1-cross-sensory-co-design-tools-and-interaction-qualities)
  - [2. New Cross-Sensory Approach to Designing Restorative Virtual Environments](#2-new-cross-sensory-approach-to-designing-restorative-virtual-environments)
  - [3. On Hardware-Aware Design and Optimization of Edge Intelligence](#3-on-hardware-aware-design-and-optimization-of-edge-intelligence)
  - [4. Enhancing outdoor campus design by utilizing space syntax theory for social interaction locations](#4-enhancing-outdoor-campus-design-by-utilizing-space-syntax-theory-for-social-interaction-locations)
  - [5. COVID‐19 as an accelerator for digitalization at a German university: Establishing hybrid campuses in times of crisis](#5-covid19-as-an-accelerator-for-digitalization-at-a-german-university-establishing-hybrid-campuses-in-times-of-crisis)
  - [6. Multimodal Dataset Normalization and Perceptual Validation for Music-Taste Correspondences](#6-multimodal-dataset-normalization-and-perceptual-validation-for-music-taste-correspondences)
  - [7. The Observation of Sensory Design in Open Spaces of University Campus under Hot-humid Climate](#7-the-observation-of-sensory-design-in-open-spaces-of-university-campus-under-hot-humid-climate)
  - [8. Study of Quassessment Model for Campus Pedestrian Ways, Case Study: Sidewalk of the University of Lampung](#8-study-of-quassessment-model-for-campus-pedestrian-ways-case-study-sidewalk-of-the-university-of-lampung)
  - [9. Sound2Hap: Learning Audio-to-Vibrotactile Haptic Generation from Human Ratings](#9-sound2hap-learning-audio-to-vibrotactile-haptic-generation-from-human-ratings)
  - [10. DesignPref: Capturing Personal Preferences in Visual Design Generation](#10-designpref-capturing-personal-preferences-in-visual-design-generation)

## Cross-Paper Synthesis

The dominant approaches represented in these summaries are highly varied, spanning technical tool development, environmental assessment, and pedagogical adaptation. Several papers focus on developing novel technological or methodological frameworks. For instance, creating tools for multi-sensory interaction is addressed through the development of co-design tools incorporating multiple sensors and actuators for "sensory sketching" [1]. Similarly, the technical challenge of translating sensory data into physical outputs is tackled by creating models like Sound2Hap, which generates perceptually meaningful vibrations from diverse sounds using CNNs [9]. In contrast, some studies adopt empirical assessment methods, such as using space syntax theory to analyze physical campus layouts to optimize social interaction points [4], or employing mixed-methods approaches involving questionnaires and observations to evaluate pedestrian satisfaction across multiple dimensions (quality, design, sensory, safety, amenities) [8].

There is a clear agreement on the importance of moving beyond single-sense considerations when designing campus or digital environments. Papers emphasize the necessity of cross-sensory integration; [2] notes that current research on virtual nature environments often overlooks cross-sensory interactions, and [7] specifically aims to investigate the potential of "stimulated multi-senses" in open spaces. Furthermore, the concept of personalization and individual experience is recognized as crucial, as seen in [10], which argues that aggregated preferences fail to capture individual design tastes, a theme echoed in the need for student participation in identifying suitable social spaces [4].

Divergences appear in the *nature* of the sensory input and the *domain* of application. While [2] focuses on the complexity of cross-sensory combinations in virtual nature environments, suggesting that certain natural sounds can be "stress-inducing" if misplaced, [9] tackles the technical generation of haptic feedback from diverse environmental sounds, focusing on perceptual harmony rather than stress mitigation. Additionally, the application domain shifts significantly: some papers focus on the built environment's physical assessment in real-world, climatically specific settings like hot-humid campuses [7] or pedestrian ways [8], whereas others focus on the digital and computational aspects, such as developing tools for technical synesthesia [1] or creating hybrid digital learning models [5].

Collectively, the set of papers shows a notable gap in the integration of these diverse findings into a holistic framework for the physical campus. While [7] observes sensory variables in the physical campus, and [8] identifies "sensory" as one of five key evaluation dimensions, no paper appears to synthesize the findings from the advanced technical modeling (e.g., cross-sensory tools from [1], haptic generation from [9]) with the empirical, place-based assessment methodologies applied to physical campus life (e.g., space syntax from [4] or climate observation from [7]). Furthermore, the academic literature presented does not contain a direct comparative study linking the findings of technological design tools (like those in [1] or [9]) to the practical, real-world usability and satisfaction metrics derived from student surveys and site observations ([4] and [8]).

## Future Work Ideas

Here are 4 concrete future-work directions based *only* on the provided author-stated limitations and future work text:

1. **Modeling Overlapping and Blended Environmental Sounds for Haptics:**
    * **Gap Addressed:** The current system (Sound2Hap) is limited to single, salient sound sources, whereas real-world audio frequently contains overlapping or blended events.
    * **Grounding:** [9]
    * **Overlap:** No other paper addresses this specific technical limitation.

2. **Developing Multi-Source Haptic Feedback Systems:**
    * **Gap Addressed:** Extending the haptic generation model to handle multiple simultaneous sound sources by generating distinct vibrations across an array (e.g., a haptic vest), with each vibration representing a unique sound or source location.
    * **Grounding:** [9]
    * **Overlap:** No other paper addresses this specific technical limitation.

3. **Expanding Personalization Analysis Beyond Designer Feedback:**
    * **Gap Addressed:** The current dataset is limited to feedback from a small, skilled sample of designers. Future work should aim for a larger sample size to facilitate analyses identifying "clusters" of designers with similar tastes (e.g., minimalism or Bauhaus school).
    * **Grounding:** [10]
    * **Overlap:** No other paper addresses this specific limitation regarding sample size for clustering analyses.

4. **Adapting Haptic Generation to New Audio Domains:**
    * **Gap Addressed:** Extending the application of the audio-to-haptic model to other sound domains relevant to interaction design, such as earcons and voice-user-interface cues.
    * **Grounding:** [9]
    * **Overlap:** No other paper addresses this specific domain expansion.

## Future Work Ideas (Inferred)

*The directions below are inferred by the model from each paper's problem/method/key-result summary, for papers that had no extractable Limitations/Future Work section. Unlike the section above, these are not statements the authors themselves made — treat them as speculative.*

[Inferred, not author-stated] Integrating Technical Modeling with Physical Assessment: Applying the cross-sensory design principles developed using co-design tools to evaluate or guide the sensory design of real-world campus paths in hot-humid climates. This bridges the technical simulation capability of [1] with the empirical, place-based sensory evaluation framework of [7].
[Inferred, not author-stated] Developing Hardware-Aware Multisensory Feedback for Campus Simulation: Adapting the hardware-aware optimization techniques from edge intelligence to manage and render complex, cross-sensory outputs (like those generated by [1] or [9], if [9] were included) in a resource-constrained, physical simulation environment relevant to campus design. This addresses the technical implementation gap in [3].
[Inferred, not author-stated] Quantifying the Impact of Cross-Sensory Failures on Satisfaction: Extending the multi-dimensional evaluation model from [8] to specifically measure how the failure or mismatch of one sense (e.g., an unexpected sound, as discussed in [2]) impacts the overall satisfaction score across the five identified dimensions (quality, design, safety, sensory, amenities). This links the experiential failure modes of [2] to the evaluation structure of [8].
[Inferred, not author-stated] Designing Hybrid Learning Experiences for Physical Space: Using the principles of multimodal learning settings derived from the case study in [5] to inform the optimal arrangement or required technological augmentation of physical campus areas identified as critical for social interaction via space syntax analysis in [4].

## Papers

### 1. Cross Sensory Co-Design Tools and Interaction Qualities

Albrecht Kurze, Klaus Stephan · 2026-07-25 · *arXiv*

[View source](http://arxiv.org/abs/2607.23298v1)

**Problem:** The paper addresses the difficulty of designing cross-sensory and multi-modal interactions for affective and emotional purposes without appropriate co-design tools.

**Method:** The authors developed two co-design tools, Loaded Dice and Wheel of Plush, which incorporate multiple sensors and actuators to demonstrate interactions and aid in workshops based on the principle of technical synesthesia.

**Key result:** These tools allow for intuitive creation of new sensor-actuator combinations to support exploration, sensory sketching, and scenario-driven ideation.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 2. New Cross-Sensory Approach to Designing Restorative Virtual Environments

Rachel Masters, Francisco Ortega · 2026-07-08 · *arXiv*

[View source](http://arxiv.org/abs/2607.06901v1)

**Problem:** The paper addresses how virtual forests can be designed to effectively reduce stress and restore attention, noting that current research often focuses solely on visual aspects while cross-sensory interactions in VR nature environments remain underexplored.

**Method:** The authors explore the concept of cross-sensory interactions where senses are treated as additive but acknowledge that certain natural sounds can feel threatening if out of place within a virtual nature scene, challenging the current understanding of multisensory VNEs.

**Key result:** It is found that the combination of senses determines whether a virtual nature environment is stress-reducing or stress-inducing, and this complexity potentially affects the attention restoration capacity of an environment.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 3. On Hardware-Aware Design and Optimization of Edge Intelligence

Shuo Huai, Hao Kong, Xiangzhong Luo, et al. · 2026-07-13 · *arXiv*

[View source](http://arxiv.org/abs/2607.16297v1)

**Problem:** The complexity of deep learning models and the heterogeneity of edge devices make designing edge intelligence systems a challenging task, particularly for hardware-agnostic methods which face limitations when implementing such systems.

**Method:** The paper presents endeavors in hardware-aware design and optimization for edge intelligence, delving into techniques such as model compression and neural architecture search to achieve efficient and effective system designs.

**Key result:** The authors showcase three hardware-aware methods and discuss the existing challenges in the hardware-aware paradigm for edge intelligence research.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 4. Enhancing outdoor campus design by utilizing space syntax theory for social interaction locations

I. El-Darwish · 2021-07-01 · *Semantic Scholar* · 58 citations

[View source](https://www.semanticscholar.org/paper/d1cad2f2832d624f108aac6c2a2be938cd2cb625)

**Problem:** The paper addresses the need for universities to integrate outdoor spaces that encourage social interaction among students to boost their sense of belonging and enhance wellbeing.

**Method:** The study investigates social spaces at a governmental University campus in the Delta area (Egypt) by surveying students on their usage patterns, sensory evaluations, and physical feature priorities, followed by an analysis using space syntax theory to assess integration and choice.

**Key result:** The research highlights the importance of student participation in identifying suitable social interaction locations and paths, demonstrating that applying space syntax theory can optimize decision-making for creating responsive spaces in existing campuses or guiding designs for new ones.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 5. COVID‐19 as an accelerator for digitalization at a German university: Establishing hybrid campuses in times of crisis

Alexander Skulmowski, Günter Daniel Rey · 2020-05-28 · *Semantic Scholar* · 168 citations

[View source](https://www.semanticscholar.org/paper/2e0eccec7e88da6591ee93d0e0f636eefa9e095e)

**Problem:** The paper addresses the need to quickly transition university teaching from on-campus classes to technology-enhanced formats due to the COVID-19 outbreak.

**Method:** The authors present a case study of Chemnitz University of Technology, analyzing syllabus data and drawing on evidence from instructional psychology and social media research to inform teaching design.

**Key result:** Analysis revealed that video and video conferencing are important current developments, highlighting the need for multimodal learning settings. The authors propose a strategy of hybrid campuses to re-think higher education using social distancing measures and technology.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 6. Multimodal Dataset Normalization and Perceptual Validation for Music-Taste Correspondences

Matteo Spanio, Valentina Frezzato, Antonio Rodà · 2026-04-12 · *HF Papers*

[View source](https://huggingface.co/papers/2604.10632)

**Problem:** Collecting large, aligned cross-modal datasets for music-flavor research is difficult because perceptual experiments are costly and small by design.

**Method:** The authors address this bottleneck through two complementary experiments: the first tests whether audio-flavor correlations, feature-importance rankings, and latent-factor structure transfer from an experimental soundtracks collection to a large FMA-derived corpus with synthetic labels, and the second validates computational flavor targets against human perception in an online listener study.

**Key result:** Results from both experiments converge: the quantitative transfer analysis confirms that cross-modal structure is preserved across supervision regimes, and the perceptual evaluation shows significant alignment between computational targets and listener ratings (permutation p<0.0001, Mantel r=0.45, Procrustes m^2=0.51).

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 7. The Observation of Sensory Design in Open Spaces of University Campus under Hot-humid Climate

Mengjia Fan, A. Jamaludin, Hazreena Hussein · 2020-03-23 · *Semantic Scholar* · 4 citations

[View source](https://www.semanticscholar.org/paper/a101805c4baa62abfc76da58ada49de0ffbe6616)

**Problem:** This paper addresses the exploration of current sensory design in open spaces surrounding educational buildings within a hot-humid climate.

**Method:** The study conducts observation of sensory landscape variables to investigate their potential for supporting outdoor experience.

**Key result:** The expected key findings include insights into functional design and stimulated multi-senses in university campuses under a hot-humid climate.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 8. Study of Quassessment Model for Campus Pedestrian Ways, Case Study: Sidewalk of the University of Lampung

H. Murwadi, B. Dewancker · 2017-12-08 · *Semantic Scholar* · 17 citations

[View source](https://www.semanticscholar.org/paper/ca9404664ea706f6f9ca6815b67c4ea0eef0c78a)

**Problem:** The condition of pedestrian ways on campuses in Indonesia presents a serious problem due to the gap between regulations and reality, which affects students' satisfaction as they move around.

**Method:** This research uses a qualitative-quantitative mix methods approach, collecting data through literature questionnaires and observations, with quantitative content analysis and statistical analysis used to determine correlations between predominant variables and students' overall satisfaction.

**Key result:** The study identified five dimensions of an evaluation model: quality, design, safety, sensory, and amenities. It found that dominant factors causing dissatisfaction include durability of path material, aesthetics, and continuity of path without significant elevation differences, while durability, aesthetics, and availability of shelter potentially bring more satisfaction.

*This paper had no extractable Limitations/Future Work section — any future-work ideas involving it are inferred, not author-stated. See "Future Work Ideas (Inferred)" above.*

### 9. Sound2Hap: Learning Audio-to-Vibrotactile Haptic Generation from Human Ratings

Yinan Li, Hasti Seifi · 2026-01-18 · *HF Papers*

[View source](https://huggingface.co/papers/2601.12245)

**Problem:** Existing audio-to-vibration methods rely on signal-processing rules tuned for specific domains like music or games and often fail to generalize across diverse environmental sounds.

**Method:** The authors collected a dataset of human ratings for vibrations generated by four existing algorithms, then trained Sound2Hap, a CNN-based autoencoder, to generate perceptually meaningful vibrations from diverse sounds with low latency.

**Key result:** In user studies, Sound2Hap produced signals rated higher than signal-processing baselines on both audio-vibration match and Haptic Experience Index (HXI), demonstrating it is more harmonious with diverse sounds.

**Stated limitations:** The dataset represents a large collection of everyday sound events but real-world sounds span an even broader range, and Sound2Hap was only tested on clips containing a single salient sound source rather than overlapping or blended events.

### 10. DesignPref: Capturing Personal Preferences in Visual Design Generation

Yi-Hao Peng, Jeffrey P. Bigham, Jason Wu · 2025-11-25 · *HF Papers*

[View source](https://huggingface.co/papers/2511.20513)

**Problem:** Generative models for visual design generation often rely on aggregated human preferences, but individual tastes vary widely among designers, leading to significant disagreement that majority-voting methods fail to capture accurately.

**Method:** The authors introduce DesignPref, a dataset of 12k pairwise UI comparisons annotated by 20 professional designers with multi-level preference ratings and rationales, then investigate personalization strategies such as fine-tuning or incorporating designer-specific annotations into RAG pipelines.

**Key result:** Personalized models consistently outperform aggregated baseline models in predicting individual designers' preferences, even when using 20 times fewer examples, demonstrating that traditional majority-voting methods do not accurately reflect individual design taste.

**Stated limitations:** The dataset is limited to feedback from only 20 skilled designers rather than a larger crowdsourced sample, and the study focused primarily on labeling noise from inter-rater disagreement while anecdotal evidence suggests personal uncertainty also contributes to difficulty.
