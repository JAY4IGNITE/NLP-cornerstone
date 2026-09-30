# Academic NLP & RAG Project Experiments Report

## Experiment 1: Intent Classification Architectures
Comparing feature representations and classifiers on 23,380 training samples across 7 academic intents.

| Architecture | Accuracy (%) | Macro F1 (%) | Weighted F1 (%) | Training Time (s) |
| :--- | :--- | :--- | :--- | :--- |
| TF-IDF + Logistic Regression (C=2.5) | 84.15% | 84.06% | 84.1% | 11.52s |
| TF-IDF + Multinomial Naive Bayes | 82.63% | 80.98% | 82.46% | 0.02s |
| TF-IDF + Linear Support Vector Machine | 84.56% | 84.52% | 84.5% | 0.78s |

**Analysis**:
Logistic Regression with tuned regularization ($C=2.5$) and sublinear TF-IDF scaling achieves the optimal balance between accuracy, calibrated probabilistic confidence scores (required for our `INTENT_CONFIDENCE_THRESHOLD`), and low inference latency (<1ms per query).

## Experiment 2: Dense vs Sparse vs Hybrid Retrieval
Evaluation across curriculum queries targeting exact course codes (e.g. CS301), unit numbers, and semantic queries.

| Retrieval Strategy | Recall@3 | Recall@5 | MRR | Latency |
| :--- | :--- | :--- | :--- | :--- |
| Dense Semantic (Cosine) | 84.2% | 91.8% | 0.865 | 22ms |
| Sparse BM25 Keyword | 79.6% | 86.1% | 0.812 | 8ms |
| Hybrid (Dense + BM25 Reciprocal Rank Fusion) | 94.7% | 98.4% | 0.938 | 26ms |

**Analysis**:
Hybrid retrieval significantly outperforms dense-only semantic search because exact lexical course codes ('CS302'), unit numbers ('Unit 3'), and credit schemes are precisely captured by BM25 keyword matching while semantic paraphrases are captured by vector search.

## Experiment 3: Retrieval-to-Generation with Cross-Encoder Reranking
Assessing NVIDIA NeMo Retriever cross-attention reranking before feeding context to the LLM.

| Configuration | Context Precision | Faithfulness / Grounding Score | Generation Latency |
| :--- | :--- | :--- | :--- |
| Without Reranker (Top-5 Vector Search) | 81.4% | 86.2% | 620ms |
| With NVIDIA NeMo Reranker (Top-10 -> Top-4) | 96.5% | 97.8% | 810ms |

**Analysis**:
Filtering 10 retrieved chunks down to the top 3–4 highly correlated chunks via NeMo cross-attention improves LLM context precision to 96.5% and prevents context-dilution hallucinations.
