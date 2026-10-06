# NLP Pipeline

## Architecture
1. **Preprocessing**: Domain-aware normalization (lowercase, punctuation removal).
2. **Feature Extraction**: TF-IDF (Term Frequency-Inverse Document Frequency) using unigrams and bigrams.
3. **Intent Classification**: L2-regularized Logistic Regression.
4. **Semantic Retrieval**: TF-IDF cosine similarity search over institutional documents.
5. **Evidence Grounding**: Formulation of answers explicitly citing the retrieved institutional source.
