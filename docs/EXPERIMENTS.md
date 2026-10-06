# Experiments

## Baseline Models
- **TF-IDF + Logistic Regression**: Achieved 100% accuracy on the synthetic benchmark due to the highly templated nature of the generated queries.

## Experimental Setup
- **Hyperparameters**: `C=2.5`, `max_iter=500`, `solver=lbfgs`, `ngram_range=(1,2)`.

All results are derived strictly from the internal `CampusFAQ-50K` evaluation set.
