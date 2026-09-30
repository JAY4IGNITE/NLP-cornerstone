# Configuration Reference

All values below are examples/placeholders.

## Application

```env
APP_ENV=development
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
```

## Database

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/campusbot
```

## Intent model

```env
INTENT_MODEL_NAME=distilbert-base-uncased
INTENT_MAX_LENGTH=128
INTENT_SEED=42
```

## Embedding model

```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Retrieval

```env
LEXICAL_TOP_K=10
DENSE_TOP_K=10
FINAL_TOP_K=5
MIN_FUSED_SCORE=CALIBRATE_FROM_VALIDATION
```

Never replace calibrated thresholds with guesses.

## LLM

```env
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-3.8-flash
ANTHROPIC_MODEL=claude-sonnet-4-6
```

API keys:

```env
GEMINI_API_KEY=
ANTHROPIC_API_KEY=
```

Do not commit secrets.

## API controls

```env
MAX_QUERY_CHARS=2000
REQUEST_TIMEOUT_SECONDS=20
```

## Audit

```env
KNOWLEDGE_BASE_VERSION=campus-kb-v1
STORE_RAW_QUERY=false
```

## Configuration rules

- environment variables override local defaults
- invalid configuration should fail fast
- startup should print safe configuration summaries, never secret values
