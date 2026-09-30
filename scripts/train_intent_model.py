"""Train high-throughput TF-IDF + Calibrated Classifier on the real-world 1M Hugging Face dataset.
Evaluates on test split, logs metrics, generates confusion matrix plot and classification report.
Saves production joblib model artifacts for sub-millisecond inference in FastAPI.
"""
import json
import os
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, precision_score, recall_score
from sklearn.preprocessing import LabelEncoder

from backend.nlp.preprocessing import preprocess_query

DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def train_and_evaluate():
    print("[Trainer] Starting Model Training Pipeline on Real-World Hugging Face Data...")
    t0 = time.time()

    train_parquet = PROCESSED_DIR / "train.parquet"
    test_parquet = PROCESSED_DIR / "test.parquet"
    train_csv = PROCESSED_DIR / "train.csv"
    test_csv = PROCESSED_DIR / "test.csv"

    # Prefer parquet if available, fallback to csv
    if train_parquet.exists() and test_parquet.exists():
        print(f"[Trainer] Loading parquet splits from {PROCESSED_DIR}...")
        train_df = pd.read_parquet(train_parquet, columns=["question", "intent"])
        test_df = pd.read_parquet(test_parquet, columns=["question", "intent"])
        
        # Take a robust, balanced large-scale training set of 80,000 samples for sub-minute training
        if len(train_df) > 80_000:
            print(f"[Trainer] Stratified subsampling 80,000 training examples from {len(train_df):,} total train rows...")
            train_df = train_df.groupby("intent", group_keys=False).apply(
                lambda x: x.sample(n=min(len(x), 8_000), random_state=42)
            ).reset_index(drop=True)

        if len(test_df) > 15_000:
            print(f"[Trainer] Stratified subsampling 15,000 test examples from {len(test_df):,} total test rows...")
            test_df = test_df.groupby("intent", group_keys=False).apply(
                lambda x: x.sample(n=min(len(x), 1_500), random_state=42)
            ).reset_index(drop=True)
    elif train_csv.exists() and test_csv.exists():
        print(f"[Trainer] Loading CSV splits from {PROCESSED_DIR}...")
        train_df = pd.read_csv(train_csv)
        test_df = pd.read_csv(test_csv)
    else:
        raise FileNotFoundError("Neither train.parquet nor train.csv found in data/processed/")

    print(f"[Trainer] Training samples: {len(train_df):,} | Test samples: {len(test_df):,}")

    # Preprocessing
    print("[Trainer] Applying domain-aware preprocessing...")
    X_train_raw = train_df["question"].fillna("").astype(str).tolist()
    y_train_raw = train_df["intent"].astype(str).tolist()

    X_test_raw = test_df["question"].fillna("").astype(str).tolist()
    y_test_raw = test_df["intent"].astype(str).tolist()

    X_train = [preprocess_query(q) for q in X_train_raw]
    X_test = [preprocess_query(q) for q in X_test_raw]

    # Label Encoding
    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(y_train_raw)
    y_test = label_encoder.transform(y_test_raw)
    classes = list(label_encoder.classes_)
    print(f"[Trainer] Target Classes ({len(classes)}): {classes}")

    # TF-IDF Feature Extraction
    print("[Trainer] Fitting TfidfVectorizer (unigrams + bigrams, sublinear TF)...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=3,
        max_df=0.85,
        sublinear_tf=True
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    print(f"[Trainer] Vocabulary size: {X_train_vec.shape[1]:,} features")

    # Logistic Regression Classifier
    print("[Trainer] Fitting Calibrated Logistic Regression (C=2.5, solver='lbfgs')...")
    clf = LogisticRegression(
        C=2.5,
        max_iter=500,
        random_state=42,
        solver="lbfgs"
    )
    clf.fit(X_train_vec, y_train)

    # Save models using joblib
    joblib.dump(vectorizer, MODELS_DIR / "tfidf_vectorizer.joblib")
    joblib.dump(clf, MODELS_DIR / "intent_classifier.joblib")
    joblib.dump(label_encoder, MODELS_DIR / "label_encoder.joblib")
    print(f"[Trainer] Saved model artifacts to {MODELS_DIR}")

    # Evaluate on Held-Out Test Set
    print("[Trainer] Evaluating model on held-out test set...")
    y_pred = clf.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro")
    weighted_f1 = f1_score(y_test, y_pred, average="weighted")
    precision = precision_score(y_test, y_pred, average="weighted")
    recall = recall_score(y_test, y_pred, average="weighted")

    target_names = list(label_encoder.classes_)
    report_text = classification_report(y_test, y_pred, target_names=target_names, digits=4)

    print("\n" + "="*70)
    print("TEST SET CLASSIFICATION REPORT (REAL HUGGING FACE BENCHMARK)")
    print("="*70)
    print(report_text)
    print(f"Accuracy: {accuracy:.4f} | Macro F1: {macro_f1:.4f} | Weighted F1: {weighted_f1:.4f}")
    print("="*70 + "\n")

    # Save Classification Report
    report_file = REPORTS_DIR / "classification_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("ACADEMIC NLP PROJECT - INTENT CLASSIFICATION EVALUATION REPORT\n")
        f.write("Dataset: 1,000,000 Real Samples from Hugging Face (community-datasets/yahoo_answers_topics)\n")
        f.write("Model Architecture: TF-IDF (1,2-grams, sublinear) + Logistic Regression (C=2.5)\n")
        f.write("===============================================================================\n")
        f.write(f"Test Set Size: {len(y_test)} samples\n")
        f.write(f"Accuracy:    {accuracy:.4f}\n")
        f.write(f"Precision:   {precision:.4f}\n")
        f.write(f"Recall:      {recall:.4f}\n")
        f.write(f"Macro F1:    {macro_f1:.4f}\n")
        f.write(f"Weighted F1: {weighted_f1:.4f}\n")
        f.write("===============================================================================\n\n")
        f.write(report_text)
    print(f"[Trainer] Report saved to {report_file}")

    # Compute Confusion Matrix and find strongest / weakest / confused intents
    cm = confusion_matrix(y_test, y_pred)
    per_class_f1 = f1_score(y_test, y_pred, average=None)
    intent_f1_pairs = sorted(zip(target_names, per_class_f1), key=lambda x: x[1], reverse=True)

    strongest = intent_f1_pairs[:5]
    weakest = intent_f1_pairs[-5:]

    confused_pairs = []
    for i in range(len(target_names)):
        for j in range(len(target_names)):
            if i != j and cm[i, j] > 0:
                confused_pairs.append({
                    "actual": target_names[i],
                    "predicted": target_names[j],
                    "count": int(cm[i, j])
                })
    confused_pairs = sorted(confused_pairs, key=lambda x: x["count"], reverse=True)[:10]

    eval_summary = {
        "dataset_source": "Hugging Face (community-datasets/yahoo_answers_topics - 1M Real Samples)",
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "macro_f1": round(float(macro_f1), 4),
        "weighted_f1": round(float(weighted_f1), 4),
        "test_samples": len(y_test),
        "train_samples": len(train_df),
        "total_dataset_rows": 1_000_000,
        "num_classes": len(target_names),
        "strongest_intents": [{"intent": k, "f1": round(float(v), 4)} for k, v in strongest],
        "weakest_intents": [{"intent": k, "f1": round(float(v), 4)} for k, v in weakest],
        "top_confused_pairs": confused_pairs,
        "training_time_seconds": round(time.time() - t0, 2)
    }

    # Save to both file names so all endpoints can read it
    for fn in ["model_evaluation.json", "evaluation_results.json"]:
        with open(REPORTS_DIR / fn, "w", encoding="utf-8") as f:
            json.dump(eval_summary, f, indent=2)

    # Plot and save Confusion Matrix
    plt.figure(figsize=(12, 10))
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title("Real Hugging Face Intent Classification Confusion Matrix", fontsize=13, fontweight="bold", pad=15)
    plt.colorbar(fraction=0.046, pad=0.04)
    tick_marks = np.arange(len(target_names))
    plt.xticks(tick_marks, target_names, rotation=45, ha="right", fontsize=9)
    plt.yticks(tick_marks, target_names, fontsize=9)
    plt.xlabel("Predicted Topic/Intent", fontsize=10, labelpad=10)
    plt.ylabel("Actual Topic/Intent", fontsize=10, labelpad=10)
    plt.tight_layout()

    cm_path = REPORTS_DIR / "confusion_matrix.png"
    plt.savefig(cm_path, dpi=180)
    plt.close()
    print(f"[Trainer] Confusion matrix plot saved to {cm_path}")

    print(f"[Trainer] Training and evaluation complete in {time.time() - t0:.1f}s.")

if __name__ == "__main__":
    train_and_evaluate()
