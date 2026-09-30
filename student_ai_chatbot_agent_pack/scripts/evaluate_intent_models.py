import json
import os
import sys
import time
import uuid

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data.preprocessing import clean_query


def evaluate():
    test_q, test_y, test_id = [], [], []
    with open('data/campusfaq_50k_v1.0.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            if data['split'] == 'test':
                test_q.append(clean_query(data['query'], lowercase=True))
                test_y.append(data['intent'])
                test_id.append(data['id'])
                
    models_dir = 'models/intent'
    available_models = [d for d in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, d))]
    
    experiment_id = str(uuid.uuid4())
    exp_dir = f'artifacts/experiments/{experiment_id}'
    os.makedirs(exp_dir, exist_ok=True)
    
    results = []
    
    for m in available_models:
        model_path = os.path.join(models_dir, m)
        if not os.path.exists(os.path.join(model_path, 'model.joblib')):
            continue
            
        vec = joblib.load(f'{model_path}/vectorizer.joblib')
        clf = joblib.load(f'{model_path}/model.joblib')
        le = joblib.load(f'{model_path}/label_encoder.joblib')
        
        start_time = time.time()
        X_vec = vec.transform(test_q)
        y_pred = clf.predict(X_vec)
        latency = (time.time() - start_time) / len(test_q)
        
        y_true = le.transform(test_y)
        
        acc = accuracy_score(y_true, y_pred)
        mac_p = precision_score(y_true, y_pred, average='macro', zero_division=0)
        mac_r = recall_score(y_true, y_pred, average='macro', zero_division=0)
        mac_f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)
        wt_f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        # Save classification report
        report = classification_report(y_true, y_pred, target_names=le.classes_, output_dict=True)
        with open(f'artifacts/classification_report_{m}.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        # Save confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(12, 10))
        sns.heatmap(cm, annot=False, cmap='Blues', xticklabels=le.classes_, yticklabels=le.classes_)
        plt.title(f'Confusion Matrix - {m}')
        plt.ylabel('True')
        plt.xlabel('Predicted')
        plt.tight_layout()
        plt.savefig(f'artifacts/confusion_matrix_{m}.png')
        plt.close()
        
        # Save experiment prediction artifacts
        preds = []
        for i in range(len(test_q)):
            preds.append({
                'id': test_id[i],
                'query': test_q[i],
                'true_intent': test_y[i],
                'predicted_intent': le.inverse_transform([y_pred[i]])[0],
                'confidence': 1.0  # mock for SVC
            })
        with open(f'{exp_dir}/predictions_{m}.jsonl', 'w') as f:
            f.writelines(json.dumps(p) + '\\n' for p in preds)
                
        results.append({
            'Model': m,
            'Accuracy': acc,
            'Macro F1': mac_f1,
            'Weighted F1': wt_f1,
            'Precision': mac_p,
            'Recall': mac_r,
            'Inference Latency': latency * 1000
        })
        
    df = pd.DataFrame(results)
    df.to_csv('artifacts/intent_model_comparison.csv', index=False)
    df.to_json('artifacts/intent_model_comparison.json', orient='records', indent=2)
    
    with open(f'{exp_dir}/config.json', 'w') as f:
        json.dump({'evaluated_on': 'test', 'models': available_models}, f)
        
    with open(f'{exp_dir}/metrics.json', 'w') as f:
        df.to_json(f, orient='records', indent=2)

    with open(f'{exp_dir}/logs.txt', 'w') as f:
        f.write("Evaluation completed successfully.\\n")

if __name__ == '__main__':
    evaluate()
