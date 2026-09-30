# Implementation Status — Student AI Chatbot (DEMO_ONLY prototype)

_Generated 2026-09-29. All facts below are reproduced from the offline pipeline;
college-specific content is synthetic `DEMO_ONLY` fixtures, not a real college._

## 1. What this is

A runnable, tested prototype of a grounded college-information assistant:
**intent classification → hybrid retrieval (BM25 + dense → RRF) → grounded
generation → citation validation → abstention.** The core mandate is *never
fabricate a college-specific fact*; abstention is a first-class outcome.

The whole system runs **offline, deterministic, zero-key, zero-DB** via built-in
fallbacks (hash embeddings, local NumPy vector index, self-contained BM25,
lexical intent model, extractive generator; seed = 42). Heavier components
(sentence-transformers, fine-tuned DistilBERT, a hosted LLM provider) are opt-in
upgrades — see §5.

## 2. Success sequence (reproduce)

```
docker compose up -d                 # optional: Postgres+pgvector (not required offline)
python scripts/validate_dataset.py   # 1. dataset/registry integrity  -> exit 0
python scripts/build_index.py        # 2. build artifacts/index/       -> 44 chunks
python scripts/run_regression.py     # 3. end-to-end behaviour gate    -> 11/11
python -m pytest -q                  #    unit/integration/adversarial -> 146 passed
# API + UI:
python scripts/serve.py              # FastAPI on :8000
cd frontend && npm install && npm run dev   # Vite UI on :5173 (proxies /api)
```

## 3. Verification results (this run)

| Check | Command | Result |
|---|---|---|
| Dataset/registry integrity | `validate_dataset.py` | pass (exit 0) |
| Index build | `build_index.py` | 44 chunks, 9 approved sources |
| Behavioural regression | `run_regression.py` | **11/11 passed** |
| Unit/integration/adversarial | `pytest` | **146 passed, 0 failed, 0 skipped** |
| Intent (lexical fallback) | `evaluate_intent.py` | acc 0.6725, macro-F1 0.6616 |
| Retrieval | `evaluate_retrieval.py` | recall@5 0.643, MRR 0.670, nDCG@5 0.577 |
| **RAG safety (headline)** | `evaluate_rag.py` | **OOS hallucination 0.00, abstention 1.00** |
| RAG grounding / integrity | `evaluate_rag.py` | grounding 1.00, citation violations 0 |
| RAG in-scope coverage | `evaluate_rag.py` | answer rate 0.704 |
| Latency (offline) | `benchmark_latency.py` | end-to-end p95 ≈ 11 ms |

Machine-readable copies of every eval are under `artifacts/eval/*.json`.

## 4. Anti-hallucination layers (defense in depth)

1. **Approval/currency/score filter** — only approved, current chunks above the
   fused/dense/lexical thresholds become evidence (`services/retrieval.py`).
2. **Pre-retrieval private-record gate** — a record noun bound to a specific
   person is refused up front (`services/safety.py`, D-011).
3. **Extractive relevance gate** — the offline generator abstains unless the
   evidence's distinctive tokens actually cover the question; terse off-domain
   queries are caught by the short-query guard (`llm/extractive.py`, D-010/D-012).
4. **Citation validation** — every returned citation must be a chunk that was
   actually retrieved; unsupported claims are dropped or abstained
   (`services/citation.py`).

A notable bug this caught and fixed: *"what time is it in London?"* was answered
from the unrelated exam "reporting time" sentence (a grounded-but-wrong pivot on
the token "time"). The short-query guard (D-012) closed it — OOS hallucination
rate went 0.02 → 0.00 with all gates and tests still green.

## 5. Known limitations & optional upgrades

- **Real sources pending.** All college content is `DEMO_ONLY`. Real ingestion
  is blocked on the official, approved source set (see the single open question
  in the project status).
- **Intent model.** The default is the deterministic lexical fallback
  (acc ≈ 0.67). `scripts/train_intent.py` fine-tunes DistilBERT and the runtime
  auto-loads it if present; the first run needs network for the base model.
- **pgvector store not implemented.** The local NumPy index is the source of
  truth (D-009); `docker-compose.yml` provisions Postgres+pgvector for a future
  adapter but the app does not require it.
- **Retrieval qrels are linker-derived** (`DEMO_ONLY`), so retrieval metrics
  measure recovery of linked chunks, not human relevance. Replace with human
  judgements on real data.
- **Offline embedding guard.** In `auto` mode the embedder loads
  sentence-transformers from a warm cache; on a truly offline machine set
  `EMBEDDING_MODE=hash` (or `HF_HUB_OFFLINE=1` before import) to force the
  deterministic hash embedder.

## 6. Reproducibility

- Seed = 42 across dataset generation, training, and fallbacks.
- Index manifest records embedding model/mode/dim, chunk count, and a corpus
  content hash (`artifacts/index/manifest.json`).
- Dataset split sizes are frozen (`train 9600 / val 1200 / test 1200`,
  500/intent) and checked by `validate_dataset.py`.

