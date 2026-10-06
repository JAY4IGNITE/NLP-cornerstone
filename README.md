# CampusNLP: An Intelligent NLP-Based University Student Query Understanding and Knowledge Retrieval System

## Overview
This repository contains a clean, academically defensible hybrid NLP pipeline designed to understand student queries, predict their intent, and retrieve highly relevant academic evidence from a controlled institutional knowledge base. 

## Research Question
> Can a hybrid NLP pipeline combining intent classification, semantic retrieval, and institution-specific knowledge grounding accurately understand and answer university student queries?

## Architecture
The system implements a rigorous pipeline without relying on black-box LLM hallucinations:
1. **Dataset**: Synthetic benchmarking on `CampusFAQ-50K`.
2. **Preprocessing**: Deterministic, domain-aware text normalization.
3. **Intent Classification**: L2-regularized Logistic Regression over TF-IDF n-gram vectors.
4. **Semantic Retrieval**: Cosine similarity matching over an institutional document index.
5. **Evidence Grounding**: Confidence thresholding to guarantee answers are grounded in retrieved texts.

## Documentation
Please see the `docs/` directory for detailed methodologies:
- [Dataset Methodology](docs/DATASET_METHODOLOGY.md)
- [NLP Pipeline](docs/NLP_PIPELINE.md)
- [Experiments](docs/EXPERIMENTS.md)
- [Evaluation](docs/EVALUATION.md)
- [Limitations](docs/LIMITATIONS.md)

## Installation & Usage
1. Activate your python environment.
2. Install requirements: `pip install -r requirements.txt`
3. The entire pipeline is demonstrated interactively in `notebooks/data_processing_and_training.ipynb`.
4. To run the API backend: `uvicorn backend.main:app`
