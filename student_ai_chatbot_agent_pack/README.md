# Student AI Chatbot — IDE Agent Pack

## Purpose

This repository specification defines a production-minded college NLP cornerstone prototype that answers student questions about curricula and related college information using intent classification + retrieval-augmented generation (RAG).

The project must be **grounded in authoritative college sources**. The AI agent must never invent curriculum rules, fees, dates, contacts, eligibility, regulations, or other college-specific facts.

The repository is designed to be usable with Claude Code, Google Antigravity, or another coding agent.

## Read order for an AI coding agent

1. `AGENTS.md`
2. `PRD.md`
3. `RESTRICTIONS.md`
4. `DETAILS.md`
5. `ARCHITECTURE.md`
6. `DATASET.md`
7. `MODEL_PLAN.md`
8. `RAG.md`
9. `EVALUATION.md`
10. `DELIVERABLES.md`
11. `API.md`
12. `SECURITY_PRIVACY.md`
13. `TEST_PLAN.md`
14. `ROADMAP.md`
15. `DECISIONS.md`
16. `TASKS.md`
17. `CONFIG_REFERENCE.md`

## Canonical project decisions

- Project dataset: **CampusFAQ-12K v1.0**
- Dataset size: **12,000 evidence-grounded records**
- Intents: **24**
- Language for MVP: **English**
- Split: **80/10/10 = 9,600 / 1,200 / 1,200**
- Retriever: hybrid BM25 + dense embeddings
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2`
- Vector store: PostgreSQL + pgvector
- Generator: provider adapter; default prototype target `gemini-3.8-flash`
- Claude adapter target: `claude-sonnet-4-6`
- Backend: FastAPI
- Frontend: React + Vite + TypeScript
- Model tracking: local JSON/CSV metrics + Git commit + config snapshot
- Primary requirement: **abstain instead of hallucinate**

## Important placeholder

The college name, official domain, curriculum documents, academic regulations, and contact directory are intentionally not invented here.

Before source ingestion, the agent MUST ask the user for the authoritative source set when it is not already present in the repository.

## Running the prototype (offline, DEMO_ONLY)

The prototype runs with **no API keys, no database, and no network** — deterministic
fallbacks (hash embeddings, local vector index, self-contained BM25, lexical intent
model, extractive generator; seed = 42) stand in for the heavier components, which
are opt-in upgrades. All college content is synthetic `DEMO_ONLY` fixtures.

```bash
# 0. (optional) Postgres+pgvector — NOT required for the offline path
docker compose up -d

# Success sequence
python scripts/validate_dataset.py    # 1. dataset + registry integrity
python scripts/build_index.py         # 2. build artifacts/index/ (44 DEMO chunks)
python scripts/run_regression.py      # 3. end-to-end behaviour gate (11/11)
python -m pytest -q                   #    full test suite (146 passed)

# Evaluations (write artifacts/eval/*.{json,md})
python scripts/preprocess.py          # normalized intent-training view
python scripts/evaluate_intent.py     # intent accuracy / macro-F1
python scripts/evaluate_retrieval.py  # recall@k / MRR / nDCG
python scripts/evaluate_rag.py        # end-to-end hallucination + grounding (headline)
python scripts/benchmark_latency.py   # per-stage latency

# Optional (needs network for the base model): fine-tune DistilBERT
python scripts/train_intent.py                 # -> artifacts/models/intent (auto-loaded at runtime)
python scripts/train_intent.py --smoke         # fast wiring check into a throwaway dir

# Serve
python scripts/serve.py                         # FastAPI on http://localhost:8000
cd frontend && npm install && npm run dev       # UI on http://localhost:5173 (proxies /api)
```

Offline note: in the default `auto` embedding mode the embedder loads
`all-MiniLM-L6-v2` from a warm cache; on a truly offline machine set
`EMBEDDING_MODE=hash` to force the deterministic hash embedder.

See `artifacts/implementation_status.md` for the current verification results and
`DECISIONS.md` (D-008…D-012) for the offline-first and safety-gate rationale.
