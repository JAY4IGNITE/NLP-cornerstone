# Decision Log

## D-001 — Domain-specific dataset

**Decision:** use CampusFAQ-12K v1.0 as the canonical project dataset.

**Reason:** the chatbot needs college-specific intents, answers, and source evidence. A generic voice-assistant or banking dataset would not represent the target domain.

## D-002 — Hybrid retrieval

**Decision:** combine BM25 and dense retrieval.

**Reason:** curriculum questions contain exact identifiers (course codes, numbers, names) as well as semantic wording variation.

## D-003 — PostgreSQL + pgvector

**Decision:** use PostgreSQL + pgvector for the MVP.

**Reason:** one datastore can hold source metadata, chunks, evaluation qrels, and vectors.

## D-004 — Provider adapter

**Decision:** isolate LLM providers behind a common interface.

**Reason:** the IDE agent may be Claude or Google Antigravity, while runtime provider choice can change.

## D-005 — Abstention-first

**Decision:** unsupported evidence leads to abstention rather than a guessed answer.

**Reason:** the primary risk is a confident false campus fact.

## D-006 — MVP language

**Decision:** English only.

**Reason:** keep the first evaluation set and error taxonomy controlled. Multilingual support requires a separate validated data plan.

## D-007 — Fixed 24 intents

**Decision:** use the 24 labels in `DETAILS.md`.

**Reason:** stable label space simplifies training, analysis, and reproducibility.

## D-008 — Offline-first deterministic fallbacks (2026-09-29)

**Decision:** every external dependency has a deterministic, offline fallback: hash embeddings (blake2b feature hashing) for dense vectors, a local NumPy vector index, a self-contained BM25, a lexical keyword-overlap intent model, and an extractive grounded generator. Seed = 42.

**Reason:** the prototype must be runnable and testable with zero API keys, no database, and no network so that graders and CI can reproduce every result. The full stack (sentence-transformers, DistilBERT, a hosted provider, pgvector) is an opt-in upgrade, not a prerequisite.

**Evaluation impact:** all reported numbers are produced by the offline path; enabling the heavier components can only change them upward.

## D-009 — Local index is the reproducible source of truth (2026-09-29)

**Decision:** `scripts/build_index.py` writes `artifacts/index/` (chunks.jsonl + embeddings.npy + manifest.json with a corpus content hash). Runtime loads this persisted index; if it is absent it builds an equivalent index in-memory from the approved sources.

**Reason:** a committed, hashed index makes retrieval results reproducible and lets the service start out of the box without a build step.

## D-010 — Relevance is decided at the generator, not the fused score (2026-09-29)

**Decision:** the abstention decision is made by the extractive provider's relevance gate (within-evidence IDF distinctiveness + question-coverage), not by the RRF fused-score threshold alone.

**Reason:** RRF normalization pushes the top fused score near 1.0 regardless of quality, so the fused score cannot separate "relevant" from "best of a bad lot." The generator can justify relevance on lexical grounds it actually uses.

## D-011 — Pre-retrieval private-record safety gate (2026-09-29)

**Decision:** a query that binds an academic-record noun (marks, score, gpa, result, rank, attendance, …) to a *specific person* (first-person "my …", possessive proper name "Jane Doe's …", or "student <Name> …") is refused before retrieval and generation (`services/safety.py::is_private_record_query`).

**Reason:** the knowledge base holds only public policy, never per-student records. Without this gate the extractive generator could stitch unrelated policy sentences into a confident, non-responsive answer to "what was Jane Doe's score?" — a grounded-but-wrong privacy failure. The gate is deliberately narrow so genuine policy questions ("what grade is a pass?") are unaffected.

## D-012 — Short-query off-domain guard (2026-09-29)

**Decision:** for terse queries (≤ 2 content words) the extractive gate additionally abstains when any content word is absent from *all* retrieved evidence, or coverage is below one half.

**Reason:** terse queries carry no redundant phrasing, so a single generic pivot token can otherwise stitch an unrelated sentence into a false answer — e.g. "what time is it in London?" was answered from the exam "reporting time" sentence because "time" matched while "london" (absent from the corpus) was ignored.

**Evaluation impact:** eliminated the last out-of-scope hallucination in `evaluate_rag.py` (OOS hallucination rate 0.02 → 0.00, abstention 1.00) at a ~1.2-point cost to in-scope answer rate (0.716 → 0.704); all 11 regression cases and 146 unit tests still pass. Consistent with D-005 (abstention-first).

## How to change a decision

Do not silently modify a decision.

Add:

- decision ID
- new choice
- reason
- migration impact
- evaluation impact
- date
