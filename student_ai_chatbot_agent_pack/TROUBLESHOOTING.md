# Troubleshooting Guide

## Retrieval returns irrelevant chunks

Check:

1. source parsing
2. chunk size
3. metadata
4. embedding model
5. lexical search
6. fusion method
7. validation qrels

Do not immediately replace the model.

## Correct chunks retrieved but answer is wrong

Check:

1. generator prompt
2. evidence delimiters
3. citation validator
4. source conflict logic
5. provider response parsing

## Intent accuracy is low

Check:

1. label definitions
2. split leakage
3. class balance
4. confusing intent pairs
5. query normalization
6. training seed
7. max sequence length

Inspect the confusion matrix before changing models.

## Agent is unsure what to implement

Read `AGENTS.md`.

If the missing decision is not defined there or in the project docs, ask the user.

## Source conflict

Do not select a winner based on model intuition.

Check:

- document authority
- version
- effective date
- source registry

If unresolved: abstain.

## API key error

Check environment variables.

Never print the actual secret.

## Database/index mismatch

Check:

- knowledge-base version
- document hash
- index build manifest
- embedding model name
