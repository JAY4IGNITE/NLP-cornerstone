# Latency report (DEMO_ONLY)

- embedding_mode: sentence-transformers | intent: lexical-fallback | provider: extractive
- 10 queries x 5 reps

| stage | mean | p50 | p95 | p99 | max |
|---|---|---|---|---|---|
| intent | 0.08 | 0.09 | 0.1 | 0.15 | 0.15 |
| retrieval | 8.19 | 8.12 | 10.28 | 12.57 | 12.57 |
| end_to_end | 8.79 | 9.04 | 10.63 | 11.31 | 11.31 |
