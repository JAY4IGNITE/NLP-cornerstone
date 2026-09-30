import json
import os

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook


def create_notebook():
    nb = new_notebook()
    nb.cells.extend([
        new_markdown_cell("# Dataset Exploration: CampusFAQ-50K"),
        new_code_cell("""import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# Load dataset
data = []
with open('../data/campusfaq_50k_v1.0.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))
df = pd.DataFrame(data)
"""),
        new_markdown_cell("## Intent Distribution"),
        new_code_cell("""plt.figure(figsize=(12, 6))
sns.countplot(y='intent', data=df, order=df['intent'].value_counts().index)
plt.title('Intent Distribution')
plt.show()"""),
        new_markdown_cell("## Query and Response Lengths"),
        new_code_cell("""df['query_len'] = df['query'].apply(lambda x: len(x.split()))
df['resp_len'] = df['response'].apply(lambda x: len(str(x).split()))
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
sns.histplot(df['query_len'], ax=axes[0], bins=30).set_title('Query Length (words)')
sns.histplot(df['resp_len'], ax=axes[1], bins=30).set_title('Response Length (words)')
plt.show()"""),
        new_markdown_cell("## Train/Validation/Test Split"),
        new_code_cell("""plt.figure(figsize=(6, 4))
sns.countplot(x='split', data=df)
plt.title('Split Distribution')
plt.show()"""),
        new_markdown_cell("## Answerable vs Unsupported"),
        new_code_cell("""plt.figure(figsize=(6, 4))
sns.countplot(x='answerable', data=df)
plt.title('Answerable Distribution')
plt.show()"""),
        new_markdown_cell("## Difficulty Distribution"),
        new_code_cell("""plt.figure(figsize=(6, 4))
sns.countplot(x='difficulty', data=df)
plt.title('Difficulty Distribution')
plt.show()"""),
        new_markdown_cell("## Generate Statistics JSON"),
        new_code_cell("""import os
os.makedirs('../artifacts', exist_ok=True)
stats = {
    'total_records': len(df),
    'intents': df['intent'].value_counts().to_dict(),
    'splits': df['split'].value_counts().to_dict(),
    'answerable': df['answerable'].value_counts().to_dict(),
    'difficulty': df['difficulty'].value_counts().to_dict(),
    'avg_query_len': df['query_len'].mean(),
    'avg_resp_len': df['resp_len'].mean()
}
with open('../artifacts/dataset_statistics.json', 'w') as f:
    json.dump(stats, f, indent=2)
print("Saved artifacts/dataset_statistics.json")""")
    ])
    os.makedirs("notebooks", exist_ok=True)
    with open("notebooks/01_dataset_exploration.ipynb", "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

def generate_stats_json():
    data = []
    with open('data/campusfaq_50k_v1.0.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    import pandas as pd
    df = pd.DataFrame(data)
    df['query_len'] = df['query'].apply(lambda x: len(x.split()))
    df['resp_len'] = df['response'].apply(lambda x: len(str(x).split()))
    stats = {
        'total_records': len(df),
        'intents': df['intent'].value_counts().to_dict(),
        'splits': df['split'].value_counts().to_dict(),
        'answerable': {str(k): v for k, v in df['answerable'].value_counts().to_dict().items()},
        'difficulty': df['difficulty'].value_counts().to_dict(),
        'avg_query_len': df['query_len'].mean(),
        'avg_resp_len': df['resp_len'].mean()
    }
    os.makedirs("artifacts", exist_ok=True)
    with open('artifacts/dataset_statistics.json', 'w') as f:
        json.dump(stats, f, indent=2)

if __name__ == "__main__":
    create_notebook()
    generate_stats_json()
