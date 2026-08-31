"""
paper_scout.llm.prompts

Centralized prompt templates. Kept separate from ollama_client.py so
prompt wording can be iterated on without touching the request/retry
logic, and so prompts are unit-testable without a live Ollama server.

Each builder returns a (system_prompt, user_prompt) tuple, ready to pass
straight into OllamaClient.generate_small()/generate_large().
"""

from __future__ import annotations

from paper_scout.utils.models import Paper

_MAX_SECTION_CHARS_IN_PROMPT = 1500


def _truncate(text: str | None, limit: int = _MAX_SECTION_CHARS_IN_PROMPT) -> str:
    if not text:
        return "(not available)"
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + " [...truncated]"


# ── Phase 5: per-paper summarization (small model) ─────────────────


SUMMARIZE_SYSTEM_PROMPT = """You are a research assistant that writes precise, factual summaries \
of academic papers. You only use information present in the provided text — never invent \
results, numbers, or claims the paper doesn't make. You always respond with a single valid \
JSON object and nothing else: no markdown fences, no preamble, no explanation."""


def build_summarize_prompt(paper: Paper) -> tuple[str, str]:
    """
    Build the (system, user) prompt for Phase 5 per-paper summarization.
    Expects paper.abstract to be populated, and paper.extracted_sections
    to be populated where available (falls back gracefully if not).
    """
    sections = paper.extracted_sections
    conclusion = _truncate(sections.conclusion if sections else None)
    limitations = _truncate(sections.limitations if sections else None)

    user_prompt = f"""Summarize the following paper into a single JSON object with exactly these keys:
- "problem": one to two sentences on the problem/question the paper addresses
- "method": one to two sentences on the approach or method used
- "key_result": one to two sentences on the main result or finding
- "stated_limitations": one to two sentences on limitations the AUTHORS themselves state \
(not your own critique) — use null if none are given below

Title: {paper.title}

Abstract:
{paper.abstract.strip()}

Conclusion (if available):
{conclusion}

Author-stated Limitations (if available):
{limitations}

Respond with ONLY the JSON object. Do not include any text, explanation, or reasoning \
before or after the JSON. Your entire response must be parseable as JSON."""

    return SUMMARIZE_SYSTEM_PROMPT, user_prompt


# ── Phase 6: cross-paper synthesis (large model) ────────────────────


CROSS_PAPER_SYSTEM_PROMPT = """You are a senior research analyst synthesizing themes across a set \
of paper summaries from the same field. You identify genuine patterns, agreements, and \
contradictions actually present in the summaries — you do not pad with generic AI-report \
boilerplate ("this is an exciting area", "further research is needed") and you do not \
introduce papers or claims that were not given to you."""


def build_cross_paper_synthesis_prompt(papers: list[Paper], query: str) -> tuple[str, str]:
    """
    Build the (system, user) prompt for Phase 6 cross-paper synthesis.
    Expects each paper.summary to already be populated (Phase 5 output).
    """
    paper_blocks = []
    for i, paper in enumerate(papers, start=1):
        if paper.summary is None:
            continue
        paper_blocks.append(
            f"""[{i}] {paper.title}
Problem: {paper.summary.problem}
Method: {paper.summary.method}
Key result: {paper.summary.key_result}"""
        )
    papers_text = "\n\n".join(paper_blocks) if paper_blocks else "(no summarized papers available)"

    user_prompt = f"""The research query was: "{query}"

Below are summaries of {len(paper_blocks)} recent papers in this area. Write a synthesis \
(3-5 paragraphs) covering:
1. The dominant methods/approaches represented across these papers
2. Where papers agree or build on each other
3. Where papers take conflicting or divergent approaches to the same problem
4. Notable gaps in what this set of papers collectively covers

Ground every claim in the specific papers below (reference them by number, e.g. "[2] and [5] \
both..."). Do not introduce outside knowledge about the field.

Papers:
{papers_text}"""

    return CROSS_PAPER_SYSTEM_PROMPT, user_prompt


# ── Phase 6: future-work ideation (large model, RAG-grounded) ──────


FUTURE_WORK_SYSTEM_PROMPT = """You are a research strategist proposing concrete future-work \
directions. Your proposals must be grounded in the Limitations and Future Work text extracted \
directly from the papers below — you are synthesizing and connecting what the authors \
themselves already identified as open problems, not brainstorming freely. Every proposed \
direction must cite which paper(s) it draws from. Do not propose directions that aren't \
traceable to the provided text."""


def build_future_work_prompt(papers: list[Paper], cross_paper_synthesis: str) -> tuple[str, str]:
    """
    Build the (system, user) prompt for Phase 6 future-work ideation.
    This is the RAG-style grounding step — critical per the design
    principles doc for keeping 7-14B output useful instead of generic.
    Expects paper.extracted_sections.limitations/future_work to be
    populated where available.
    """
    paper_blocks = []
    for i, paper in enumerate(papers, start=1):
        sections = paper.extracted_sections
        limitations = _truncate(sections.limitations if sections else None)
        future_work = _truncate(sections.future_work if sections else None)
        if limitations == "(not available)" and future_work == "(not available)":
            continue
        paper_blocks.append(
            f"""[{i}] {paper.title}
Author-stated Limitations: {limitations}
Author-stated Future Work: {future_work}"""
        )
    papers_text = "\n\n".join(paper_blocks) if paper_blocks else "(no extracted limitations/future work available)"

    user_prompt = f"""Cross-paper synthesis of this research area:
{cross_paper_synthesis.strip()}

Author-stated limitations and future work, extracted directly from each paper:
{papers_text}

Based ONLY on the limitations/future-work text above (not general knowledge of the field), \
propose 4-6 concrete future-work directions. For each direction:
- Give it a short title
- Explain the specific gap it addresses, citing the paper number(s) it's grounded in
- Note if multiple papers independently point at the same gap (that's a stronger signal)

If the provided text doesn't support a clear direction, do not invent one — fewer, \
well-grounded directions are better than padded generic ones."""

    return FUTURE_WORK_SYSTEM_PROMPT, user_prompt

# ── Phase 6b: inferred future-work ideation (Tier 2, large model) ──


INFERRED_FUTURE_WORK_SYSTEM_PROMPT = """You are a research strategist proposing plausible next-step \
research directions for papers that did not explicitly state their own future work. You reason \
ONLY from each paper's stated problem, method, and key result — you infer directions implied by \
gaps or constraints in the method itself, you do not use outside knowledge of the field and you do \
not invent claims the paper doesn't support. Every direction you propose MUST begin with the exact \
tag "[Inferred, not author-stated]" so it is never confused with an author-stated direction, and \
must cite which paper number it applies to."""


def build_inferred_future_work_prompt(papers: list[Paper], cross_paper_synthesis: str) -> tuple[str, str]:
    """
    Build the (system, user) prompt for Tier 2 future-work ideation:
    used only for papers that have NO extracted Limitations/Future Work
    text but DO have a Phase 5 summary (problem/method/key_result).
    Explicitly marked as inferred, never blended with Tier 1 (author-
    stated) output — see synthesize/future_work.py.
    """
    paper_blocks = []
    for i, paper in enumerate(papers, start=1):
        if paper.summary is None:
            continue
        paper_blocks.append(
            f"""[{i}] {paper.title}
Problem: {paper.summary.problem}
Method: {paper.summary.method}
Key result: {paper.summary.key_result}"""
        )
    papers_text = "\n\n".join(paper_blocks) if paper_blocks else "(no summarized papers available)"

    user_prompt = f"""Cross-paper synthesis of this research area (for context only):
{cross_paper_synthesis.strip()}

The following papers did NOT have an extractable Limitations or Future Work section, so you \
must infer plausible next-step directions from their problem/method/key-result alone:
{papers_text}

Propose 2-4 concrete next-step directions total across these papers. For each direction:
- Begin the line with the exact tag "[Inferred, not author-stated]"
- Give it a short title
- Explain the specific gap or constraint in the method that motivates it, citing the paper \
number it applies to

Do not use general knowledge of the field beyond what's stated above. If a paper's summary \
doesn't clearly imply any next step, skip it rather than inventing one."""

    return INFERRED_FUTURE_WORK_SYSTEM_PROMPT, user_prompt

# ── Query refinement (small model, optional pre-pipeline step) ─────


QUERY_REFINE_SYSTEM_PROMPT = """You improve short research queries for academic paper search.

Your job is to make the user's query cleaner, clearer, and more useful for finding relevant
academic papers.

You MAY:
- fix spelling mistakes and typos
- fix grammar
- improve awkward or unnatural phrasing
- normalize capitalization
- preserve standard capitalization of technical acronyms such as LLM, RAG, CNN, NLP, ViT
- use conventional academic terminology when it is an obvious correction
- turn a conversational question into a concise academic search phrase when this preserves
  the same meaning

You MUST:
- preserve the user's original research topic and intent
- preserve important technical concepts, entities, methods, and constraints
- keep the query approximately the same scope
- remain concise
- return only the improved search query

You MUST NOT:
- add a new research topic
- invent a method, dataset, application, or constraint
- broaden the research question
- narrow the research question
- answer the question
- explain your changes

Examples:

Input:  difusion modles for audeo genration
Output: diffusion models for audio generation

Input:  rag with llm for question answering
Output: RAG with LLMs for question answering

Input:  what is the impact of federated learning on privacy in healthcare?
Output: federated learning and privacy in healthcare

Input:  DEEP LERNING FOR MEDICAL IMAGE ANALISIS
Output: deep learning for medical image analysis

Return ONLY the improved query on one line."""


def build_query_refine_prompt(raw_query: str) -> tuple[str, str]:
    user_prompt = f"""Improve this academic paper search query:

{raw_query}

Return ONLY the improved query."""
    
    return QUERY_REFINE_SYSTEM_PROMPT, user_prompt

# ── Report Q&A (large model, single-report grounded) ───────────────


QA_SYSTEM_PROMPT = """You answer questions about ONE specific research report, using ONLY the \
report text provided to you. You never use outside knowledge, and you never guess. If the \
report does not contain information to answer the question, say plainly that the report does \
not cover that, rather than speculating or answering from general knowledge. Keep answers \
concise and directly grounded in the report's own wording."""

_MAX_REPORT_CHARS_IN_QA_PROMPT = 12000


def build_qa_prompt(report_markdown: str, question: str) -> tuple[str, str]:
    """
    Build the (system, user) prompt for report Q&A. The whole report is
    passed as context — a single report is small enough that chunking/
    retrieval would be over-engineering for this use case.
    """
    report_text = report_markdown.strip()
    if len(report_text) > _MAX_REPORT_CHARS_IN_QA_PROMPT:
        report_text = report_text[:_MAX_REPORT_CHARS_IN_QA_PROMPT].rstrip() + "\n\n[...truncated]"

    user_prompt = f"""Report:
{report_text}

Question: {question}

Answer using ONLY the report above. If the answer isn't in the report, say so directly."""

    return QA_SYSTEM_PROMPT, user_prompt