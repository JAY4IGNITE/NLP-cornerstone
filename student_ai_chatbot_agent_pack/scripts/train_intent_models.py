import argparse
import json
import os
import sys
import time

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import FeatureUnion
from sklearn.svm import LinearSVC

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data.preprocessing import LabelEncoder, clean_query

SEED = 42

def load_data(path: str):
    train_q, train_y = [], []
    val_q, val_y = [], []
    test_q, test_y = [], []
    
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            query = clean_query(data['query'], lowercase=True)
            intent = data['intent']
            split = data['split']
            
            if split == 'train':
                train_q.append(query)
                train_y.append(intent)
            elif split == 'val':
                val_q.append(query)
                val_y.append(intent)
            elif split == 'test':
                test_q.append(query)
                test_y.append(intent)
                
    return (train_q, train_y), (val_q, val_y), (test_q, test_y)

def train_logistic(X_train, y_train):
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.9, sublinear_tf=True)
    clf = LogisticRegression(C=1.0, random_state=SEED, max_iter=1000)
    return vec, clf

def train_svm(X_train, y_train):
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.9, sublinear_tf=True)
    clf = LinearSVC(C=1.0, random_state=SEED, max_iter=2000)
    return vec, clf

def train_naive_bayes(X_train, y_train):
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.9, sublinear_tf=True)
    clf = MultinomialNB()
    return vec, clf

def train_hybrid_tfidf(X_train, y_train):
    word_vec = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=2)
    char_vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=2)
    vec = FeatureUnion([("word", word_vec), ("char", char_vec)])
    clf = LogisticRegression(C=1.0, random_state=SEED, max_iter=1000)
    return vec, clf

def train_distilbert(X_train, y_train, X_val, y_val, le):
    # Optional transformer - skip if not available
    try:
        import torch
        from transformers import (
            DistilBertForSequenceClassification,
            DistilBertTokenizer,
            Trainer,
            TrainingArguments,
        )
        # Due to complexity and resource usage in MVP, we just stub or do a tiny train if requested
        print("DistilBERT training is requested but for MVP we will use a dummy or skip if resources are low.")
        return None, None
    except ImportError:
        print("Transformers library not found. Skipping DistilBERT.")
        return None, None

def evaluate(clf, vec, X, y, le, split_name):
    start_time = time.time()
    X_vec = vec.transform(X)
    y_pred = clf.predict(X_vec)
    latency = (time.time() - start_time) / len(X)
    
    y_true = le.transform(y)
    
    acc = accuracy_score(y_true, y_pred)
    mac_p = precision_score(y_true, y_pred, average='macro', zero_division=0)
    mac_r = recall_score(y_true, y_pred, average='macro', zero_division=0)
    mac_f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)
    wt_f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    
    return {
        'split': split_name,
        'accuracy': acc,
        'macro_precision': mac_p,
        'macro_recall': mac_r,
        'macro_f1': mac_f1,
        'weighted_f1': wt_f1,
        'inference_latency_ms': latency * 1000,
        'predictions': y_pred
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, required=True, 
                        choices=['logistic', 'svm', 'naive_bayes', 'hybrid_tfidf', 'distilbert', 'all'])
    args = parser.parse_args()
    
    models_to_train = [args.model] if args.model != 'all' else ['logistic', 'svm', 'naive_bayes', 'hybrid_tfidf']
    
    # Load data
    (train_q, train_y), (val_q, val_y), (_test_q, _test_y) = load_data('data/campusfaq_50k_v1.0.jsonl')
    
    le = LabelEncoder()
    train_y_enc = le.fit_transform(train_y)
    
    for m in models_to_train:
        print(f"Training {m}...")
        start_time = time.time()
        
        if m == 'logistic':
            vec, clf = train_logistic(train_q, train_y_enc)
        elif m == 'svm':
            vec, clf = train_svm(train_q, train_y_enc)
        elif m == 'naive_bayes':
            vec, clf = train_naive_bayes(train_q, train_y_enc)
        elif m == 'hybrid_tfidf':
            vec, clf = train_hybrid_tfidf(train_q, train_y_enc)
        elif m == 'distilbert':
            vec, clf = train_distilbert(train_q, train_y_enc, val_q, val_y, le)
            if clf is None:
                continue
            
        # Fit
        X_train_vec = vec.fit_transform(train_q)
        clf.fit(X_train_vec, train_y_enc)
        train_time = time.time() - start_time
        
        # Evaluate on validation
        val_metrics = evaluate(clf, vec, val_q, val_y, le, 'validation')
        
        # Save artifacts
        model_dir = f'models/intent/{m}'
        os.makedirs(model_dir, exist_ok=True)
        joblib.dump(vec, f'{model_dir}/vectorizer.joblib')
        joblib.dump(clf, f'{model_dir}/model.joblib')
        joblib.dump(le, f'{model_dir}/label_encoder.joblib')
        
        metrics = {
            'model': m,
            'train_time_s': train_time,
            'validation_metrics': {k: v for k, v in val_metrics.items() if k != 'predictions'},
            'config': {'seed': SEED, 'model_type': m}
        }
        with open(f'{model_dir}/metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)
            
        print(f"{m} trained. Val Acc: {val_metrics['accuracy']:.4f}, Val F1: {val_metrics['macro_f1']:.4f}")

if __name__ == '__main__':
    main()
