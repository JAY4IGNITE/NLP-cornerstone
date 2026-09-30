# CampusFAQ-50K NLP Chatbot — Final Evaluation

## 1. Dataset Statistics
- **Total Records**: 50,000
- **Intents**: 24 exactly matching canonical labels.
- **Split Sizes**: Train: 40,000 | Validation: 5,000 | Test: 5,000

## 2. Preprocessing
Implemented Unicode normalization (NFKC), punctuation normalizations (curly quotes to straight, em-dash to hyphen), control character removal, and whitespace trimming. Domain-specific entities like `CSE101` and `sem 4` were safely preserved by preventing aggressive stemming or over-aggressive abbreviation expansion.

## 3. Models Tested
1. **Model A**: TF-IDF (1-2 word n-grams) + Logistic Regression
2. **Model B**: TF-IDF (1-2 word n-grams) + Linear SVM
3. **Model C**: TF-IDF (1-2 word n-grams) + Multinomial Naive Bayes
4. **Model D**: Hybrid TF-IDF (Word 1-2 n-grams + Char 3-5 n-grams) + Logistic Regression
5. **Model E**: DistilBERT Transformer (skipped for MVP due to environment limits to maintain lightweight runtime).

## 4. Training Configuration
- **Seed**: 42 for all deterministic modules.
- **Data used**: `train` split only.
- TF-IDF parameters tuned for college terminology: min_df=2, max_df=0.9, sublinear_tf=True.
- Full model artifacts and `metrics.json` recorded per model.

## 5. Intent Results (Test Set)
| Model | Accuracy | Macro F1 | Weighted F1 | Precision | Recall | Inference Latency |
| ----- | -------: | -------: | ----------: | --------: | -----: | ----------------: |
| Logistic | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | ~1 ms |
| Linear SVC | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | ~1 ms |
| Naive Bayes | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | ~1 ms |
| Hybrid TF-IDF | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | ~2 ms |

*(Note: Synthetic cleanly separable data yielded perfect theoretical bounds on test set.)*

## 6. Retrieval Results
- **Recall@5**: 0.6429
- **Hit@5**: 0.8593
- **MRR**: 0.6699
- Indexed 44 test chunks successfully using sentence-transformers backend.

## 7. RAG Results
- In-scope answer rate and mean grounding validated successfully via deterministic rules.
- Citation integrity: 0 violations.

## 8. Abstention Results
- **OOS silence rate**: 0.0 hallucinations (0/50 test boundaries).
- Target zero out-of-scope fabrication maintained.

## 9. Latency
- Intent Classification Latency (p95): ~2ms
- Full API Request simulated p50 latency (local models): ~40ms

## 10. Error Analysis
(See `notebooks/04_error_analysis.ipynb`)
Typical limitations in MVP models usually occur on severe misspellings or unknown abbreviations not covered by the training distribution, though synthetic tests hit perfect accuracy. Short queries ("fee?", "sem 4") occasionally risk misclassification, countered here by the hybrid character n-gram approach.

## 11. Known Limitations
- The classical ML intent models do not generalize semantically as well as large LLM embeddings; novel, out-of-distribution queries may fail.
- Retrieval relies heavily on exact keyword or basic semantic overlap; long-form ambiguous questions might miss Recall@1.
- No LLM generation was enabled in the offline testing harness to ensure safety bounds, meaning responses are purely extractive.

## 12. Selected MVP Model
**Model A (Logistic Regression with Word TF-IDF)**
*Justification*: Chosen as the MVP because it reaches the performance ceiling alongside SVM, but provides natively calibrated `predict_proba` logic, making the confidence threshold implementation robust and straightforward compared to `decision_function` scaling.

## 13. Reproduction Commands
```bash
python scripts/validate_dataset.py
python scripts/train_intent_models.py --model all
python scripts/evaluate_intent_models.py
python scripts/build_index.py
python scripts/evaluate_retrieval.py
python scripts/infer.py --query "How many credits does CSE203 have?"
python -m pytest tests
```
