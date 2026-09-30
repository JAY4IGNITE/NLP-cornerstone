# Evaluation and Validation Plan

## 1. Evaluation layers

### Layer A — data validation

Check:

- schema
- labels
- nulls
- duplicates
- evidence links
- split leakage
- source approval

### Layer B — intent

Evaluate on frozen test set.

Gates:

- accuracy >= 0.90
- macro F1 >= 0.90

### Layer C — retrieval

Use manually/automatically mapped qrels.

Report:

- Recall@1/3/5
- MRR@5
- nDCG@5
- precision@5

Gate:

- Recall@5 >= 0.90
- MRR@5 >= 0.75

### Layer D — generation

For a stratified sample, human reviewers score:

- correctness: 0–2
- groundedness: 0–2
- citation validity: 0–2
- completeness: 0–2
- clarity: 0–2

Pass criterion:

- correctness >= 1 for >= 90%
- groundedness >= 1 for >= 90%
- citation validity >= 1 for >= 95%

## 2. Unsupported-answer test

Construct a fixed test set of questions not answerable from the KB.

Measure:

`unsupported_answer_rate = unsupported questions receiving a factual answer / unsupported questions`

Target <= 3%.

The most important failure is a confidently wrong factual answer.

## 3. Adversarial tests

Test:

- prompt injection in source documents
- prompt injection in user query
- stale document vs current document
- similar course names
- similar course codes
- nonexistent course
- missing semester
- ambiguous abbreviation
- conflicting source versions
- empty query
- very long query
- repeated query
- multilingual input, which should abstain or be clearly unsupported unless a language feature has been implemented

## 4. Qualitative review

Create a minimum 100-question review set balanced across:

- intents
- easy/medium/hard
- answerable/abstain
- course/academic/admin domains

Two reviewers should score a shared subset to measure reviewer consistency.

## 5. Reproducibility

Each evaluation run records:

- run ID
- timestamp
- Git commit
- dataset manifest hash
- source registry hash
- model IDs
- config
- seed
- environment
- metrics
- error samples

## 6. Error taxonomy

Use:

- `intent_wrong`
- `retrieval_missed`
- `retrieval_wrong`
- `stale_source`
- `citation_invalid`
- `generation_unsupported`
- `generation_incomplete`
- `abstention_wrong`
- `provider_error`
- `system_error`

## 7. Release gate

A release candidate requires:

- all automated tests passing
- dataset validation passing
- intent gates passing
- retrieval gates passing
- hallucination/unsupported gate passing
- citation validity gate passing
- manual review completed
- reproducibility artifacts stored
