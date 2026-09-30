# Implementation Tasks

## Milestone M0 — Repository setup

- [x] create backend/frontend/scripts/tests structure
- [x] add configuration layer
- [x] add `.env.example`
- [x] add Docker Compose for PostgreSQL + pgvector
- [x] add CI test command (`pytest`; 146 tests green)
- [x] verify agent rules

## Milestone M1 — Source pipeline

- [x] confirm approved college sources (production registry loaded)
- [x] populate source registry (`DEMO_ONLY`, 9 approved sources)
- [x] implement parser
- [x] implement metadata extraction
- [x] implement chunker
- [x] implement source hashing
- [x] write ingestion tests

## Milestone M2 — Dataset

- [x] implement 24 intent catalog
- [x] generate CampusFAQ-12K (`DEMO_ONLY`, 12,000 rows)
- [x] add evidence links
- [x] run duplicate/leakage checks
- [x] freeze train/val/test manifests
- [x] save dataset hash

## Milestone M3 — Intent model

- [x] fine-tune DistilBERT (`scripts/train_intent.py`; smoke-verified; full run is optional/online)
- [x] evaluate (`scripts/evaluate_intent.py`)
- [x] save model artifact (script saves a loadable HF dir; app defaults to the offline lexical fallback)
- [x] expose inference service
- [x] add regression tests

## Milestone M4 — Retrieval

- [x] create embeddings
- [ ] load pgvector — **optional; not implemented. The local NumPy index is the default store (D-009).**
- [x] implement lexical search
- [x] implement dense search
- [x] implement rank fusion
- [x] evaluate retrieval

## Milestone M5 — RAG

- [x] implement provider interface
- [x] implement Gemini adapter
- [x] implement Claude adapter
- [x] implement grounded prompt
- [x] implement JSON output parser
- [x] implement citation validator
- [x] implement abstention

## Milestone M6 — UI

- [x] chat page
- [x] citation component
- [x] source details
- [x] loading/error states
- [x] feedback control

## Milestone M7 — Validation

- [x] end-to-end regression (`scripts/run_regression.py`, 11/11)
- [x] adversarial suite (`tests/test_adversarial.py`, 29)
- [x] latency benchmark (`scripts/benchmark_latency.py`)
- [ ] qualitative review — (unblocked; pending review on production corpus)
- [x] reproducibility report (`artifacts/implementation_status.md` + `artifacts/eval/*`)

## Agent behavior

When a task depends on missing college-specific input, stop and ask the user.

Do not replace missing inputs with made-up examples in production code. Fixtures may be clearly labeled `DEMO_ONLY`.
