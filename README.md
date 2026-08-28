# paper-scout

<div align="center">
    <img src="banner.scg">
    <p><em>Generated using Claude.</em></p>
</div>

paper-scout is an agentic pipeline that takes a research topic as input, searches multiple paper sources, and produces a markdown report summarizing recent work in that area. The standout feature is future work ideation that is grounded in the actual Limitations and Future Work sections extracted from the papers themselves, rather than free form brainstorming from a language model.

The whole thing runs locally through Ollama, using a small model for per paper summarization and a larger model for cross paper synthesis and ideation.

## What it does

Give it a query like `"diffusion models for audio"` and it will:

1. Search arXiv, Semantic Scholar, and Hugging Face Papers
2. Deduplicate results across sources and rank them by relevance, recency, and citation count
3. Download PDFs and extract each paper's Abstract, Conclusion, Limitations, and Future Work sections
4. Summarize each paper with a small local model
5. Synthesize themes and contradictions across the whole set with a larger local model
6. Generate concrete future work directions, grounded in what the papers themselves say is unfinished
7. Write everything to a single markdown report

You run one command and get one report. No intermediate prompts, no manual steps in between.

## Requirements

- Python 3.12
- [Ollama](https://ollama.com) installed and running locally
- Two pulled models: a small one for summarization and a larger one for synthesis (configurable, see below)
- Roughly 32GB RAM recommended for comfortable CPU offload of the larger model

## Setup

```bash
git clone https://github.com/AmirmasoudCS/paper-scout.git
cd paper-scout
python -m venv .venv
.venv\Scripts\activate   # or source .venv/bin/activate on Mac/Linux
pip install -e .
pip install -r requirements.txt
```

Pull the models referenced in `config.yaml`:

```bash
ollama pull qwen3.5:9b
ollama pull gemma4:e4b
```

## Usage

```bash
python -m paper_scout "your research topic here"
```

The report is written to the `outputs/` directory as a markdown file named after your query and the date.

## Configuration

All tunable settings live in `config.yaml`: which sources are enabled, how many papers to pull, ranking weights, which Ollama models to use, and report formatting. Nothing is hardcoded, so you can adjust behavior without touching the code.

## Project structure

```
paper_scout/
├── sources/       # arXiv, Semantic Scholar, Hugging Face Papers fetchers
├── ranking/       # dedup and composite ranking
├── ingestion/      # PDF download and section extraction
├── llm/           # Ollama client and prompt templates
├── summarize/      # per paper summarization
├── synthesize/     # cross paper synthesis and grounded future work ideation
├── report/         # markdown report writer
├── pipeline.py     # LangGraph orchestration of the full pipeline
└── cli.py          # command line entry point
```

Every module is independently tested. Run the full test suite with:

```bash
pytest tests/ -m "not ollama and not network"
```

Tests marked `ollama` or `network` require a running local Ollama server or live internet access respectively, and are excluded by default so the core suite runs anywhere.

## Notes

- Every source fetcher and pipeline stage is designed to fail gracefully. One source or paper failing does not stop the whole run.
- Future work ideation will refuse to run rather than fall back to ungrounded brainstorming if none of the papers have extractable Limitations or Future Work text.
- A web interface and query history are planned as future additions but are not part of the current scope.

## License

[MIT](./LICENSE)