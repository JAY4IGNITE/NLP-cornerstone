# Model Plan

## 1. MVP model stack

### Intent classifier

Base model:

`distilbert-base-uncased`

Fine-tune for the 24 canonical intents.

Why:

- lightweight
- fast CPU inference
- easy fine-tuning
- suitable for a college prototype
- deterministic evaluation is straightforward

### Dense retriever

Model:

`sentence-transformers/all-MiniLM-L6-v2`

Use 384-dimensional embeddings.

License: Apache-2.0 according to the model card.

### Generator

Provider adapter with the same application interface.

Default configuration target:

`gemini-3.8-flash`

Claude configuration target:

`claude-sonnet-4-6`

The exact model ID is configuration, not business logic.

The agent must verify the provider's current model availability when configuring a new deployment.

## 2. Training

Intent classifier:

- tokenizer from base model
- max sequence length: 128
- epochs: 3–8, selected on validation macro F1
- learning rate: start at 2e-5
- batch size: start at 16
- early stopping patience: 2
- weight decay: 0.01
- class weighting only if imbalance exists after the canonical 24x500 dataset design

Do not overfit the prototype to one validation seed.

## 3. Intent outputs

Return:

- top intent
- probability/confidence
- optional top-3 candidates

For unsupported/unknown questions, map to `unsupported_or_unknown`.

## 4. Retriever

Use two retrieval channels:

1. lexical BM25
2. dense cosine similarity

Fuse with Reciprocal Rank Fusion or an equivalent deterministic rank fusion method.

MVP top-k:

- lexical k = 10
- dense k = 10
- fused k = 5

## 5. Optional reranking

Post-MVP or only if retrieval recall is insufficient.

Do not add a reranker before measuring the baseline.

## 6. Generator behavior

The generator is not the source of truth.

Prompt structure:

```text
SYSTEM:
You answer student questions using only the supplied evidence.

RULES:
- Do not invent facts.
- Do not use unstated knowledge.
- If evidence is insufficient, abstain.
- Cite every college-specific factual claim.

QUESTION:
{question}

INTENT:
{intent}

EVIDENCE:
{top_chunks}

OUTPUT:
Return structured JSON with answer, citations, and status.
```

## 7. Metrics

### Intent

- accuracy
- macro precision
- macro recall
- macro F1
- confusion matrix
- per-intent F1

### Retrieval

- Recall@1
- Recall@3
- Recall@5
- MRR@5
- nDCG@5
- precision@5

### Generation

- answer correctness
- groundedness/faithfulness
- citation validity
- abstention correctness
- response completeness
- concise/student-friendly style

Do not use an LLM judge as the only quality gate.

## 8. Model artifact requirements

Save:

- base model ID
- tokenizer ID
- Git commit
- training seed
- data manifest hash
- config file
- metrics JSON
- confusion matrix
- environment information
- training logs

## 9. Reproducibility

Default seed: `42`.

Seed:

- Python random
- NumPy
- PyTorch
- data split
- evaluation sampling

Where full determinism is impossible on hardware, record environment and known nondeterministic operations.
