# Reference Architecture

## 1. Logical architecture

```text
Student
  |
  v
React Web UI
  |
  v
FastAPI /api/chat
  |
  +--> Input Validation / Rate Limit
  |
  +--> Intent Classifier
  |       |
  |       +--> intent + confidence
  |
  +--> Hybrid Retriever
  |       |
  |       +--> BM25 / PostgreSQL text search
  |       +--> pgvector dense search
  |       |
  |       v
  |    candidate chunks
  |
  +--> Evidence Filter / Reranker
  |
  +--> LLM Provider Adapter
  |       |
  |       +--> Gemini
  |       +--> Claude
  |
  +--> Citation Validator
  |
  +--> Safe Response
  |
  +--> Audit Logger
```

## 2. Services

### Frontend

React + Vite + TypeScript.

Responsibilities:

- chat UI
- loading/error states
- citations
- source expansion
- basic feedback controls

### API

FastAPI.

Responsibilities:

- request/response schemas
- orchestration
- auth hooks
- rate limiting
- observability
- model adapter invocation

### NLP service

Python module within the backend for MVP.

Responsibilities:

- normalization
- intent inference
- optional entity extraction

### Retrieval service

MVP may run in-process.

Responsibilities:

- lexical retrieval
- dense retrieval
- fusion
- reranking
- evidence filtering

### Knowledge store

PostgreSQL + pgvector.

Tables:

- documents
- document_versions
- chunks
- embeddings
- source_registry
- evaluation_qrels

### LLM provider adapter

Common interface:

```python
class LLMProvider(Protocol):
    def generate(self, prompt: str, *, model: str) -> str: ...
```

Providers:

- Gemini
- Anthropic

Only one provider is required for MVP runtime.

## 3. Data flow

### Ingestion

Official source -> parser -> cleaner -> document metadata -> chunker -> embeddings -> PostgreSQL/pgvector.

### Inference

Question -> normalize -> classify intent -> retrieve -> filter -> generate -> validate citations -> return.

## 4. Deployment model

Prototype:

- frontend: Vite dev server
- backend: Uvicorn/FastAPI
- database: local PostgreSQL with pgvector
- optional Docker Compose

The architecture should keep provider and database interfaces replaceable.

## 5. Suggested modules

```text
backend/app/
  api/
  core/
  models/
  schemas/
  services/
  retrieval/
  llm/
  evaluation/
  ingestion/
frontend/src/
  components/
  pages/
  lib/
  types/
scripts/
tests/
data/
docs/
```

## 6. Failure isolation

External LLM failure must not corrupt retrieval state.

Indexing failure must not destroy an existing valid index.

A failed provider request returns a controlled error/abstention path.

## 7. Scalability path

Post-MVP:

- asynchronous ingestion workers
- background embedding jobs
- Redis cache
- reranker service
- centralized metrics
- document change detection
- multi-tenant source registries

Do not implement these before MVP unless required.
