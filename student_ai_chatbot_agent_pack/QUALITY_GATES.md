# Quality Gates

## Gate G1 — Source integrity

Pass only if:

- all indexed documents are approved
- hashes are recorded
- metadata is complete

## Gate G2 — Dataset

Pass only if:

- 12,000 records
- 24 intents
- 500 per intent
- 9,600/1,200/1,200 splits
- evidence present for answerable items
- leakage checks pass

## Gate G3 — Intent

- macro F1 >= 0.90
- accuracy >= 0.90

## Gate G4 — Retrieval

- Recall@5 >= 0.90
- MRR@5 >= 0.75

## Gate G5 — Grounding

- citation validity >= 95%
- human groundedness >= 90%
- unsupported-answer rate <= 3%

## Gate G6 — Reliability

- automated tests pass
- provider failure path works
- index failure path works
- no secret leaks

## Gate G7 — Reproducibility

Every release candidate includes:

- source manifest
- dataset manifest
- model metadata
- config snapshot
- metric reports
- test report
- Git commit
