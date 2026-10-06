# CampusFAQ-50K v1.0

**Status: DEMO_ONLY_SYNTHETIC**

This is a real 50,000-row dataset for integrating and validating the Student AI Chatbot pipeline.

It is deliberately synthetic so the project does not invent or misrepresent information about a real college.

## Exact size

- 50,000 records
- 24 intents
- 40,000 train
- 5,000 validation
- 5,000 test

## Critical design

The queries, answers, evidence IDs and retrieval qrels all point back to the **same canonical synthetic knowledge base**.

Therefore you can use this package to test:

- intent training
- retrieval
- RAG
- citation validation
- abstention
- regression testing
- API integration
- reproducibility

## Files

- `data/campusfaq_50k_v1.0.jsonl` — canonical machine-learning dataset
- `data/campusfaq_50k_v1.0.csv` — CSV copy
- `data/demo_knowledge_chunks.jsonl` — RAG evidence chunks
- `data/retrieval_qrels_test.tsv` — retrieval test qrels
- `data/source_registry_demo.jsonl` — demo source registry
- `DATASET_MANIFEST.json` — counts and provenance
- `DATA_DICTIONARY.md` — schema

## Import

```python
import json
with open("data/campusfaq_50k_v1.0.jsonl", encoding="utf-8") as f:
    data = [json.loads(x) for x in f]
```

## Do not claim this is real college data

Before deployment or academic reporting as a real institution-specific system, regenerate the same schema from approved official college documents.
