# IDE Project Deliverables

## 1. Recommended repository structure

```text
student-ai-chatbot/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── PRD.md
├── DETAILS.md
├── RESTRICTIONS.md
├── ARCHITECTURE.md
├── DATASET.md
├── MODEL_PLAN.md
├── RAG.md
├── EVALUATION.md
├── ROADMAP.md
├── DELIVERABLES.md
├── API.md
├── SECURITY_PRIVACY.md
├── TEST_PLAN.md
├── DECISIONS.md
├── TASKS.md
├── CONFIG_REFERENCE.md
├── pyproject.toml
├── docker-compose.yml
├── .env.example
├── backend/
├── frontend/
├── data/
│   ├── raw/              # ignored
│   ├── processed/
│   ├── manifests/
│   └── fixtures/
├── models/
├── artifacts/
├── scripts/
├── tests/
└── docs/
```

## 2. Required scripts

```text
scripts/ingest_sources.py
scripts/build_dataset.py
scripts/preprocess.py
scripts/validate_dataset.py
scripts/train_intent.py
scripts/evaluate_intent.py
scripts/build_index.py
scripts/evaluate_retrieval.py
scripts/evaluate_rag.py
scripts/run_regression.py
scripts/benchmark_latency.py
scripts/chat.py
scripts/serve.py
```

## 3. Required notebooks or equivalent reports

- `notebooks/01_data_exploration.ipynb`
- `notebooks/02_intent_training.ipynb`
- `notebooks/03_retrieval_evaluation.ipynb`
- `notebooks/04_rag_evaluation.ipynb`

A script-equivalent is acceptable when notebooks would harm reproducibility.

## 4. Required backend modules

```text
backend/app/
  main.py
  api/chat.py
  api/health.py
  schemas/chat.py
  services/orchestrator.py
  services/intent.py
  services/retrieval.py
  services/citation.py
  retrieval/bm25.py
  retrieval/vector.py
  retrieval/fusion.py
  llm/base.py
  llm/gemini.py
  llm/anthropic.py
  core/config.py
  core/logging.py
```

## 5. Required frontend modules

```text
frontend/src/
  app/
  components/Chat.tsx
  components/CitationList.tsx
  components/SourceCard.tsx
  lib/api.ts
  types/chat.ts
```

## 6. Artifacts

Every training/evaluation run should write to:

```text
artifacts/
  data/
  models/
  evaluations/
  benchmarks/
  manifests/
  logs/
```

## 7. Required test categories

- unit
- integration
- retrieval
- citation validation
- abstention
- adversarial
- API contract
- UI smoke

## 8. Example environment variables

See `CONFIG_REFERENCE.md`.

Never commit real secrets.
