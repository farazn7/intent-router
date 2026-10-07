# Implementation Plan

Intent Router is a planned application that classifies a user request and sends it to one of three paths: **RAG**, **internet search**, or **a direct LLM response**. A TF-IDF + SVM classifier chooses the initial route, while a LangGraph workflow coordinates retrieval, evidence checks, retries, and answer generation.

This document describes the proposed implementation. For a quick project overview, see the [README](../README.md). Features and directory entries below are planned unless already implemented.

## Scope

The first version will include:

- A trained intent classifier with the labels `rag`, `internet`, and `direct_llm`.
- Document retrieval with source citations.
- A corrective RAG workflow that checks retrieved evidence and retries when necessary.
- Internet search and page fetching for questions requiring public or current information.
- A shared interface for local and remote LLM providers.
- Evaluation of routing, retrieval, answer quality, latency, and model usage.

GraphRAG is out of scope for now. The RAG path will use document chunks and vector retrieval. Corrective checks are part of this single RAG path, not a separate intent or RAG implementation.

## Architecture

```text
User query
    |
TF-IDF + SVM intent router
    |
    +-- rag ---------> Retrieve document chunks
    |                         |
    |                  Evaluate evidence
    |                         |
    |                  +------+------+
    |               sufficient    insufficient
    |                  |             |
    |                  |       Rewrite and retry
    |                  |             |
    |                  |       Optional internet fallback
    |                  |             |
    |                  +------+------+
    |                         |
    |                  Answer with citations,
    |                  or report missing evidence
    |
    +-- internet ----> Search and fetch pages
    |                         |
    |                  Answer with citations,
    |                  or report missing evidence
    |
    +-- direct_llm --> Answer without retrieval
```

The classifier selects the initial route. The workflow controls what happens afterward, including any corrective fallback. Local versus remote LLM selection is a provider setting, not an intent label; either provider can support any of the three routes.

### 1. Document retrieval and corrective RAG

The ingestion pipeline loads documents, splits them into chunks, preserves source metadata, generates embeddings, and builds a searchable index.

At query time, the RAG service retrieves relevant chunks and evaluates both their relevance and whether they contain enough evidence to answer. If evidence is insufficient, the workflow can rewrite the query and retry retrieval. The initial correction budget will allow one retrieval retry, configurable later.

Internet fallback is allowed only when public information can appropriately answer the question. Missing private or internal information should lead to clarification or an explicit insufficient-evidence response. A failed evidence check must not silently turn into an unsupported answer from model memory.

This is a simplified corrective RAG design, not a claim to reproduce the full CRAG research implementation.

### 2. Workflow and model integration

LangGraph owns the shared execution state, conditional branches, retry limits, and termination rules. Individual services perform their own operations and return results; they do not start independent correction loops.

The internet service is reused by both the initial `internet` route and an eligible RAG fallback. It searches, fetches selected pages with timeouts and size limits, and returns readable content with source URLs. Retrieved content is treated as evidence, not as instructions to the application.

A shared model interface supports generation and evidence evaluation. Start with one working provider, then add the second local or remote adapter behind the same interface.

### 3. Intent classifier

Train a TF-IDF + linear SVM pipeline on labeled user requests:

| Label | Intended use | Example |
| --- | --- | --- |
| `rag` | Questions that depend on the indexed document collection | "What does our uploaded leave policy say about carryover?" |
| `internet` | Questions requiring public or current external information | "What are the latest updates to this product?" |
| `direct_llm` | Self-contained writing, reasoning, or conversation | "Rewrite this paragraph more clearly." |

Agree on the target domain and labeling rules before collecting a large dataset. Mixed requests, ambiguous references, and low-confidence predictions need a documented handling policy rather than an arbitrary default route.

Include varied wording, typos, and difficult boundary examples. Keep duplicates and closely related paraphrases in the same train, validation, or test split to reduce leakage. Fit TF-IDF only on the training split and save it together with the classifier as one fitted pipeline. SVM decision scores are not probabilities unless explicitly calibrated.

The classifier dataset and the RAG document collection are separate assets: the former teaches routing, while the latter supplies answer evidence.

## Planned repository structure

```text
intent-router/
|-- README.md
|-- pyproject.toml
|-- requirements.txt             # Dependency list; install inside .venv
|-- .env.example                 # Required settings; no credentials
|-- .gitignore
|-- configs/
|   |-- app.yaml                 # Providers, model settings, timeouts
|   |-- router.yaml              # Classifier artifact and routing policy
|   |-- rag.yaml                 # Chunking, retrieval, correction limits
|   `-- training.yaml            # Features, splits, classifier parameters
|-- src/intent_router/
|   |-- __init__.py
|   |-- main.py                  # Application entry point
|   |-- settings.py              # Configuration loading and validation
|   |-- schemas.py               # Shared requests, decisions, evidence, answers
|   |-- api/
|   |   |-- app.py
|   |   `-- routes.py            # Query and health endpoints
|   |-- router/
|   |   |-- predictor.py         # Load fitted pipeline and predict route
|   |   `-- policy.py            # Ambiguity and low-confidence handling
|   |-- workflow/
|   |   |-- state.py
|   |   |-- graph.py             # Assemble LangGraph nodes and edges
|   |   |-- nodes.py             # Call underlying services
|   |   `-- decisions.py         # Branching, retry, and termination rules
|   |-- rag/
|   |   |-- service.py           # Public RAG operations
|   |   |-- ingestion/
|   |   |   |-- loaders.py
|   |   |   |-- chunking.py
|   |   |   `-- pipeline.py
|   |   |-- retrieval/
|   |   |   |-- embeddings.py
|   |   |   |-- vector_store.py
|   |   |   `-- retriever.py
|   |   `-- correction/
|   |       |-- evaluator.py     # Relevance and evidence sufficiency
|   |       `-- rewriter.py
|   |-- internet/
|   |   |-- service.py
|   |   |-- search.py
|   |   |-- fetch.py
|   |   `-- extraction.py
|   |-- llm/
|   |   |-- client.py            # Shared provider interface
|   |   |-- local.py
|   |   |-- remote.py
|   |   |-- grounded.py          # Generate cited answers from evidence
|   |   `-- direct.py            # Generate answers without retrieval
|   |-- prompts/
|   |   |-- retrieval_evaluation.txt
|   |   |-- query_rewrite.txt
|   |   |-- grounded_answer.txt
|   |   `-- direct_answer.txt
|   `-- observability/
|       `-- tracing.py           # Route, steps, latency, calls, token usage
|-- training/
|   |-- prepare.py
|   |-- split.py
|   |-- train.py
|   `-- evaluate.py
|-- evaluation/
|   |-- cases/
|   |   |-- routing.jsonl
|   |   |-- retrieval.jsonl
|   |   `-- end_to_end.jsonl
|   |-- run.py
|   `-- metrics.py
|-- data/
|   |-- router/                  # Raw examples, processed data, saved splits
|   `-- documents/               # Raw and processed source documents
|-- artifacts/
|   |-- router/                  # Fitted pipeline and training metadata
|   |-- indexes/                 # Generated local indexes or manifests
|   `-- evaluation/              # Evaluation reports
|-- scripts/
|   |-- ingest_documents.py
|   `-- query.py
|-- tests/
|   |-- unit/
|   |-- integration/
|   `-- fixtures/
`-- docs/
    |-- implementation-plan.md
    |-- dataset_guidelines.md
    `-- evaluation_plan.md
```

Create modules as their functionality is implemented. Install all Python dependencies inside the project's ignored `.venv`, following the [README setup instructions](../README.md#local-setup). Maintain dependencies in `requirements.txt`; `pyproject.toml` reads that list for package installation. Keep source code and project data outside `.venv`.

Private documents, credentials, large datasets, and generated model/index artifacts should not be committed. Small sanitized examples and test fixtures can be versioned.

## Shared interfaces

Agree on these contracts before implementing the workstreams independently:

- **RouteDecision:** initial route, classifier score, and any ambiguity status.
- **Evidence:** text, source identifier, document location or URL, and retrieval metadata.
- **EvidenceAssessment:** relevance, sufficiency, and the reason for an inadequate result.
- **Answer:** response text, citations, and final status.
- **WorkflowState:** query, route decision, collected evidence, assessment, retry count, and answer.

Both retrieval services return the same evidence format. Grounded answer generation is shared between document and internet responses. Training runs offline; the application loads the saved classifier pipeline at runtime.

## Team workstreams

| Workstream | Responsibilities | Initial ownership |
| --- | --- | --- |
| Retrieval and corrective RAG | Ingestion, vector retrieval, evidence evaluation, query rewriting | Project owner |
| Workflow and integrations | LangGraph orchestration, internet fetching, model adapters, API integration | Shared; assign explicitly before integration |
| Intent classification | Dataset collection, labeling, preparation, SVM training and evaluation | Teammate collecting the dataset |

Domain selection, route-label rules, shared schemas, and evaluation cases are joint decisions. A small agreed set of sample requests and expected routes will let the team develop the classifier and application in parallel.

## Implementation milestones

1. **Define contracts and data rules:** choose the initial domain, establish labels and ambiguity policy, and prepare representative evaluation questions.
2. **Build basic document Q&A:** ingest a small collection, retrieve chunks, and generate cited answers using one model provider.
3. **Train the router in parallel:** validate the dataset, create reproducible splits, train TF-IDF + SVM, and record baseline metrics.
4. **Connect all three routes:** integrate the classifier with LangGraph, internet search, direct generation, and document Q&A.
5. **Add corrective behavior:** evaluate evidence, allow a bounded retrieval retry, and implement eligible internet fallback and insufficient-evidence responses.
6. **Evaluate and refine:** compare behavior with correction enabled and disabled, fix routing and retrieval failures, and add the second model-provider adapter.

## Validation plan

- **Routing:** macro F1, per-class precision/recall, confusion matrix, and behavior on ambiguous requests.
- **Retrieval:** whether expected supporting passages appear in retrieved results, including questions with no answer in the collection.
- **Answers:** correctness, support from cited evidence, citation validity, and handling of missing information.
- **Correction:** whether retries improve answers, how often fallback is used, and whether every path terminates within its configured limits.
- **Efficiency:** end-to-end latency, retrieval/evaluation/generation calls, token usage, and estimated remote-provider cost when available.
- **Integration:** empty search results, unavailable model/search providers, fetch failures, and malformed evaluator output.

Use the same held-out questions to compare the RAG path with correction enabled and disabled. This provides a measurable baseline without introducing multiple RAG routes.

