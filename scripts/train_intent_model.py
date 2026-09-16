"""Train TF-IDF + Logistic Regression intent classifier on stratified train split.
Evaluates on validation split, logs metrics, generates confusion matrix plot and classification report.
"""
import json
import sys
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

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def train_and_evaluate():
    print("Loading train, validation, and test datasets...")
    train_df = pd.read_csv(PROCESSED_DIR / "train.csv")
    val_df = pd.read_csv(PROCESSED_DIR / "val.csv")
    test_df = pd.read_csv(PROCESSED_DIR / "test.csv")

    print(f"Train size: {len(train_df)}, Val size: {len(val_df)}, Test size: {len(test_df)}")

    # Preprocessing
    print("Applying domain-aware preprocessing...")
    X_train_raw = train_df["question"].fillna("").astype(str).tolist()
    y_train_raw = train_df["intent"].astype(str).tolist()

    X_val_raw = val_df["question"].fillna("").astype(str).tolist()
    y_val_raw = val_df["intent"].astype(str).tolist()

    X_test_raw = test_df["question"].fillna("").astype(str).tolist()
    y_test_raw = test_df["intent"].astype(str).tolist()

    X_train = [preprocess_query(q) for q in X_train_raw]
    X_val = [preprocess_query(q) for q in X_val_raw]
    X_test = [preprocess_query(q) for q in X_test_raw]

    # Label Encoding
    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(y_train_raw)
    y_val = label_encoder.transform(y_val_raw)
    y_test = label_encoder.transform(y_test_raw)

    # TF-IDF Feature Extraction
    print("Fitting TfidfVectorizer with unigrams and bigrams...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.85,
        sublinear_tf=True
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_val_vec = vectorizer.transform(X_val)
    X_test_vec = vectorizer.transform(X_test)
    print(f"Vocabulary dimension: {X_train_vec.shape[1]}")

    # Logistic Regression Classifier
    print("Training Logistic Regression classifier (C=2.5, solver='lbfgs', max_iter=1000)...")
    clf = LogisticRegression(
        C=2.5,
        max_iter=1000,
        random_state=42,
        solver="lbfgs"
    )
    clf.fit(X_train_vec, y_train)

    # Save models using joblib
    joblib.dump(vectorizer, MODELS_DIR / "tfidf_vectorizer.joblib")
    joblib.dump(clf, MODELS_DIR / "intent_classifier.joblib")
    joblib.dump(label_encoder, MODELS_DIR / "label_encoder.joblib")
    print(f"Saved artifacts to {MODELS_DIR}")

    # Evaluate on Test Set
    y_pred = clf.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro")
    weighted_f1 = f1_score(y_test, y_pred, average="weighted")
    precision = precision_score(y_test, y_pred, average="weighted")
    recall = recall_score(y_test, y_pred, average="weighted")

    target_names = list(label_encoder.classes_)
    report_text = classification_report(y_test, y_pred, target_names=target_names, digits=4)

    print("=== TEST SET CLASSIFICATION REPORT ===")
    print(report_text)
    print(f"Accuracy: {accuracy:.4f} | Macro F1: {macro_f1:.4f} | Weighted F1: {weighted_f1:.4f}")

    # Save Classification Report
    report_file = REPORTS_DIR / "classification_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("ACADEMIC NLP PROJECT - INTENT CLASSIFICATION EVALUATION REPORT\n")
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
    print(f"Report saved to {report_file}")

    # Compute Confusion Matrix and find strongest / weakest / confused intents
    cm = confusion_matrix(y_test, y_pred)
    per_class_f1 = f1_score(y_test, y_pred, average=None)
    intent_f1_pairs = sorted(zip(target_names, per_class_f1), key=lambda x: x[1], reverse=True)

    strongest = intent_f1_pairs[:5]
    weakest = intent_f1_pairs[-5:]

    # Identify confused pairs (off-diagonal > 0)
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
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "macro_f1": round(float(macro_f1), 4),
        "weighted_f1": round(float(weighted_f1), 4),
        "test_samples": len(y_test),
        "num_classes": len(target_names),
        "strongest_intents": [{"intent": k, "f1": round(float(v), 4)} for k, v in strongest],
        "weakest_intents": [{"intent": k, "f1": round(float(v), 4)} for k, v in weakest],
        "top_confused_pairs": confused_pairs
    }

    with open(REPORTS_DIR / "model_evaluation.json", "w", encoding="utf-8") as f:
        json.dump(eval_summary, f, indent=2)

    # Plot and save Confusion Matrix
    plt.figure(figsize=(14, 12))
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title("Intent Classification Confusion Matrix", fontsize=14, fontweight="bold", pad=15)
    plt.colorbar(fraction=0.046, pad=0.04)
    tick_marks = np.arange(len(target_names))
    plt.xticks(tick_marks, target_names, rotation=60, ha="right", fontsize=8)
    plt.yticks(tick_marks, target_names, fontsize=8)
    plt.xlabel("Predicted Intent", fontsize=11, labelpad=10)
    plt.ylabel("Actual Intent", fontsize=11, labelpad=10)
    plt.tight_layout()

    cm_path = REPORTS_DIR / "confusion_matrix.png"
    plt.savefig(cm_path, dpi=180)
    plt.close()
    print(f"Confusion matrix plot saved to {cm_path}")

if __name__ == "__main__":
    train_and_evaluate()
