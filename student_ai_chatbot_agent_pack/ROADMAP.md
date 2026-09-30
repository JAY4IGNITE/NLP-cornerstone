# MVP Roadmap

## Phase 0 — Contract and source setup

Milestone:

- repository scaffold created
- agent files installed
- source registry exists
- college source set confirmed

Exit:

- no unresolved source identity issues

## Phase 1 — Data pipeline

Build:

- source ingestion
- PDF/HTML parser
- metadata extraction
- chunking
- source registry
- dataset builder
- dataset validator

Exit:

- CampusFAQ-12K schema valid
- 12,000 records created or an explicit blocker is reported
- train/val/test manifests generated

## Phase 2 — Intent model

Build:

- tokenizer/training
- inference service
- metrics script
- confusion matrix

Exit:

- intent model passes target gates or a documented improvement loop exists

## Phase 3 — RAG

Build:

- embeddings
- PostgreSQL + pgvector index
- BM25 retrieval
- fusion
- evidence threshold
- citation validation

Exit:

- retrieval metrics reported

## Phase 4 — LLM generation

Build:

- provider interface
- Gemini adapter
- Claude adapter
- grounded prompt
- structured response parser
- abstention behavior

Exit:

- end-to-end chat works with one provider

## Phase 5 — Frontend

Build:

- chat screen
- citations
- source details
- loading/error states
- feedback button

Exit:

- usable student demo

## Phase 6 — Validation

Build:

- automated regression suite
- qualitative review tool
- latency benchmark
- reproducibility bundle

Exit:

- release gate report generated

## Phase 7 — Post-MVP enhancements

Only after MVP gates pass:

- reranker
- Redis response cache
- admin ingestion UI
- analytics dashboard
- source freshness dashboard
- explainability panel
- multilingual support
- feedback-based retraining
- background indexing
- role-based access

Each enhancement needs a new decision record and tests.
