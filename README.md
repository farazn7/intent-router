# Intent Router

Route user queries to **RAG**, **internet search**, or **a direct LLM response** using a TF-IDF + SVM intent classifier.

**Status:** Planning stage; implementation has not started.

## How it works

- **RAG:** Retrieve relevant document passages, check whether they support an answer, and retry retrieval when needed.
- **Internet:** Search and fetch public information, then answer with sources.
- **Direct LLM:** Handle self-contained writing, reasoning, and conversation without retrieval.

LangGraph coordinates the routes, corrective checks, and fallback steps. A shared model interface will support local and remote LLMs. GraphRAG is out of scope for now.

## Development plan

1. Build document retrieval and basic cited answers.
2. Collect labeled queries and train the intent classifier in parallel.
3. Connect the three routes through LangGraph.
4. Add corrective RAG and evaluate routing, answer quality, and latency.

See the [implementation plan](docs/implementation-plan.md) for the architecture, proposed repository structure, team workstreams, dataset guidance, and evaluation details.
