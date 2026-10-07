# Intent Router

Route user queries to **RAG**, **internet search**, or **a direct LLM response** using a TF-IDF + SVM intent classifier.

**Status:** Starter skeleton in place; retrieval and workflow implementation are next.

## How it works

- **RAG:** Retrieve relevant document passages, check whether they support an answer, and retry retrieval when needed.
- **Internet:** Search and fetch public information, then answer with sources.
- **Direct LLM:** Handle self-contained writing, reasoning, and conversation without retrieval.

LangGraph coordinates the routes, corrective checks, and fallback steps. A shared model interface will support local and remote LLMs. GraphRAG is out of scope for now.

## Local setup

Use Python 3.11 or newer. Install all project dependencies in the local `.venv`, not globally. From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -e .
```

This installs the dependencies and the project in editable mode using the virtual environment's Python. Use that interpreter to run project commands, and select it in your editor. You can optionally activate the environment with `.\.venv\Scripts\Activate.ps1`.

Add dependencies to `requirements.txt`; `pyproject.toml` reads that same list. Source code, documents, and `.env` stay in the project folders; `.venv` contains the Python environment and installed packages and is ignored by Git.

Copy `.env.example` to `.env` if it does not already exist. Put local source documents in `data/documents/`; generated indexes belong in `artifacts/`. These contents and `.env` are ignored by Git.

Start in `src/intent_router/rag/` for ingestion and retrieval, and `src/intent_router/workflow/graph.py` for LangGraph orchestration. These are placeholders; there is no runnable query pipeline yet.

## Development plan

1. Build document retrieval and basic cited answers.
2. Collect labeled queries and train the intent classifier in parallel.
3. Connect the three routes through LangGraph.
4. Add corrective RAG and evaluate routing, answer quality, and latency.

See the [implementation plan](docs/implementation-plan.md) for the architecture, proposed repository structure, team workstreams, dataset guidance, and evaluation details.
