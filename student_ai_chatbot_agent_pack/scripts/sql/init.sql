-- Student AI Chatbot — PostgreSQL + pgvector schema (OPTIONAL DB path).
-- The offline prototype does not require this; it is used when DATABASE_URL is set.
-- Embedding dimension = 384 (sentence-transformers/all-MiniLM-L6-v2).

CREATE EXTENSION IF NOT EXISTS vector;

-- Registry of authoritative sources. Ingestion fails closed unless a source
-- is present here with approval_status = 'approved'.
CREATE TABLE IF NOT EXISTS source_registry (
    source_id       TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    uri             TEXT NOT NULL,
    authority       TEXT NOT NULL,
    document_type   TEXT NOT NULL,
    version         TEXT,
    published_at    DATE,
    effective_from  DATE,
    retrieved_at    TIMESTAMPTZ,
    content_hash    TEXT,
    license         TEXT,
    approval_status TEXT NOT NULL DEFAULT 'unapproved',
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS documents (
    document_id   TEXT PRIMARY KEY,
    source_id     TEXT NOT NULL REFERENCES source_registry(source_id),
    title         TEXT NOT NULL,
    document_type TEXT NOT NULL,
    authority     TEXT NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS document_versions (
    id            BIGSERIAL PRIMARY KEY,
    document_id   TEXT NOT NULL REFERENCES documents(document_id),
    version       TEXT NOT NULL,
    published_at  DATE,
    effective_from DATE,
    content_hash  TEXT NOT NULL,
    is_current    BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (document_id, version)
);

CREATE TABLE IF NOT EXISTS chunks (
    chunk_id        TEXT PRIMARY KEY,
    document_id     TEXT NOT NULL REFERENCES documents(document_id),
    document_version TEXT NOT NULL,
    ordinal         INT NOT NULL,
    heading         TEXT,
    location        TEXT,
    content         TEXT NOT NULL,
    content_hash    TEXT NOT NULL,
    token_count     INT
);

CREATE TABLE IF NOT EXISTS embeddings (
    chunk_id   TEXT PRIMARY KEY REFERENCES chunks(chunk_id),
    model      TEXT NOT NULL,
    dim        INT NOT NULL,
    embedding  vector(384)
);

CREATE INDEX IF NOT EXISTS embeddings_ann
    ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS chunks_fts
    ON chunks USING gin (to_tsvector('english', content));

-- Relevance judgements for retrieval evaluation.
CREATE TABLE IF NOT EXISTS evaluation_qrels (
    id        BIGSERIAL PRIMARY KEY,
    query_id  TEXT NOT NULL,
    query     TEXT NOT NULL,
    chunk_id  TEXT NOT NULL,
    relevance INT NOT NULL DEFAULT 1
);
