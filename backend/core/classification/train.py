import os
import sys
import time
import json
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.core.preprocessing.text_preprocessor import preprocess_query

DATASET_PATH = BASE_DIR / "data/benchmark/CampusFAQ-50K-v1.0/data/campusfaq_50k_v1.0.csv"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def train_intent_model():
    print("[Trainer] Loading synthetic CampusFAQ-50K benchmark...")
    df = pd.read_csv(DATASET_PATH)
    
    # Preprocessing
    print("[Trainer] Preprocessing queries...")
    df['query'] = df['query'].fillna("").astype(str)
    
    # Verify column names
    query_col = 'query' if 'query' in df.columns else 'question'
    
    # Check for predefined splits
    if 'split' in df.columns:
        train_df = df[df['split'] == 'train']
        test_df = df[df['split'] == 'test']
    else:
        from sklearn.model_selection import train_test_split
        train_df, test_df = train_test_split(df, test_size=0.1, random_state=42, stratify=df['intent'])
        
    X_train = [preprocess_query(q) for q in train_df[query_col]]
    X_test = [preprocess_query(q) for q in test_df[query_col]]
    
    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(train_df['intent'])
    y_test = label_encoder.transform(test_df['intent'])
    
    print("[Trainer] Fitting TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=3, sublinear_tf=True)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    print("[Trainer] Training Logistic Regression...")
    clf = LogisticRegression(C=2.5, max_iter=500, random_state=42, solver='lbfgs')
    clf.fit(X_train_vec, y_train)
    
    
    print("[Trainer] Evaluating Baseline 2: Linear SVM...")
    svm = LinearSVC(random_state=42)
    svm.fit(X_train_vec, y_train)
    y_pred_svm = svm.predict(X_test_vec)
    print(f"SVM Test Accuracy: {accuracy_score(y_test, y_pred_svm):.4f}")

    print("[Trainer] Saving models...")
    joblib.dump(vectorizer, MODELS_DIR / "tfidf_vectorizer.joblib")
    joblib.dump(clf, MODELS_DIR / "intent_classifier.joblib")
    joblib.dump(label_encoder, MODELS_DIR / "label_encoder.joblib")
    
    print("[Trainer] Evaluating...")
    y_pred = clf.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=label_encoder.classes_)
    print(f"Test Accuracy: {acc:.4f}")
    print(report)
    
if __name__ == '__main__':
    train_intent_model()
