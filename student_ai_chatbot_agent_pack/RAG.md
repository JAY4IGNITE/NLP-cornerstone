# RAG Integration Specification

## 1. Ingestion

Source pipeline:

```text
Approved source
  -> parser
  -> normalized document
  -> structural metadata
  -> chunker
  -> embedding
  -> PostgreSQL/pgvector
```

## 2. Document metadata

Required:

- `document_id`
- `source_url` or local source path
- `title`
- `document_type`
- `authority`
- `version`
- `published_at` when available
- `effective_from` when available
- `retrieved_at`
- `content_hash`
- `approval_status`

## 3. Chunking

Default starting point:

- target 350–600 tokens
- overlap 50–100 tokens
- preserve section headings
- preserve table context
- preserve page numbers for PDFs
- do not split course tables so that row meaning is lost

After baseline evaluation, tune chunk size based on retrieval metrics.

## 4. Embedding index

Embed:

```text
document title
section heading
chunk text
```

Store metadata with each vector.

## 5. Hybrid retrieval

For query q:

1. normalize query
2. compute dense embedding
3. retrieve dense top 10
4. retrieve lexical top 10
5. fuse rankings
6. discard unapproved/stale sources
7. rerank if enabled
8. select top 5 evidence chunks

## 6. Evidence threshold

Define configurable thresholds:

- `MIN_DENSE_SCORE`
- `MIN_LEXICAL_SCORE`
- `MIN_FUSED_SCORE`

The application must calibrate these thresholds on the validation set.

Do not hard-code a threshold merely because it “looks reasonable”.

## 7. Answer generation

Only approved evidence enters the generator context.

The generator must not receive the entire database.

Every answer citation must resolve to a real source record.

## 8. Citation validation

Before returning the response:

1. parse cited IDs
2. verify each ID exists
3. verify each cited chunk was actually provided to the model
4. reject invalid citations
5. fall back to abstention or regenerate if citation validation fails

## 9. Latency targets

- embedding/query encoding: <= 100 ms local target
- hybrid retrieval: <= 300 ms p95 local target
- total application: <= 4 s p95 target excluding provider outage/cold start

Measure actual values and report them.

## 10. Caching

MVP:

- optional in-memory cache for repeated queries
- cache key includes normalized query + knowledge-base version

Post-MVP:

- Redis

Do not cache a response without tying it to a knowledge-base version.

## 11. Knowledge updates

When a source changes:

- create a new document version
- recompute only affected chunks
- preserve prior version
- regenerate impacted evaluation records
- record index build manifest

Never silently overwrite historical versions.
