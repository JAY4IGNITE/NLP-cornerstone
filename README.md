# CampusNLP: An Intelligent NLP-Based University Student Query Understanding and Knowledge Retrieval System

## 1. Project Overview
This repository contains a clean, academically defensible NLP project that transforms institutional knowledge (regulations, curriculum) into a queryable hybrid NLP pipeline. 

## 2. Problem Statement
University students frequently struggle to find precise answers in large, scattered, and often complex institutional PDFs such as academic regulations, curriculum maps, and handbooks. Existing search systems often fail to understand the specific intent behind a query.

## 3. Research Question
> Can a hybrid NLP pipeline combining intent classification, semantic retrieval, and institution-specific knowledge grounding accurately understand and answer university student queries?

## 4. Objectives
1. Understand student queries via robust text preprocessing.
2. Predict query intent accurately using a supervised classifier.
3. Retrieve relevant academic evidence via semantic vector search.
4. Produce a grounded response with source citations.
5. Explicitly abstain when reliable evidence is unavailable to prevent hallucinations.

## 5. Architecture
```
                 STUDENT QUERY
                       |
                       v
              TEXT PREPROCESSING
                       |
                       v
              INTENT CLASSIFIER
                       |
              +--------+--------+
              |                 |
              v                 v
       STRUCTURED DATA     DOCUMENT RETRIEVAL
              |                 |
              +--------+--------+
                       |
                       v
                EVIDENCE RANKING
                       |
                       v
                 CONFIDENCE CHECK
                   /          \
                  /            \
                 v              v
        GROUNDED ANSWER      ABSTAIN
                 |
                 v
             SOURCE CITATION
```

## 6. Dataset Methodology
We use the **CampusFAQ-50K** dataset, which is a **synthetic controlled benchmark**. It contains 50,000 generated records spanning 24 intents, allowing for a structured evaluation of our intent classification pipeline. We also construct a knowledge base using official university PDFs (curriculum, regulations).

## 7. NLP Pipeline
The core NLP layer involves domain-aware tokenization that preserves academic entities (e.g., `CS101`, `SGPA`), TF-IDF feature extraction, and a Calibrated Logistic Regression classifier. Semantic retrieval is powered by embedding institutional document chunks.

## 8. Experiments
We evaluate baselines (Logistic Regression vs. Linear SVM) on our intent classification benchmark.

## 9. Evaluation
Our evaluation covers intent classification accuracy, precision, and recall, alongside qualitative metrics for retrieval accuracy, source correctness, and graceful abstention on unsupported queries.

## 10. Installation
```bash
# Clone the repository
git clone <url>
cd NLP-cornerstone

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
npm install
```

## 11. API Usage
The main endpoint conceptually supports:
```http
POST /api/query
Content-Type: application/json

{
  "query": "What is the minimum attendance required?"
}
```

Example Output:
```json
{
  "query": "What is the minimum attendance required?",
  "intent": "attendance_rules",
  "overall_confidence": 0.91,
  "answer": "The minimum attendance required is 75%...",
  "sources": [
    {
      "document_id": "Academic_Regulations_2025.pdf",
      "title": "Academic Regulations",
      "location": "Page 12"
    }
  ]
}
```

## 12. Demo
Run the development server:
```bash
npm run dev
```
Navigate to `http://localhost:5173` to interact with the UI, which visibly demonstrates the query, predicted intent, answer, confidence, evidence, and safe abstention.

## 13. Limitations
The system relies on a synthetic benchmark for classification and static PDFs for retrieval. We lack a large-scale dataset of authentic, noisy student queries, meaning our high classification accuracy reflects the controlled nature of the benchmark rather than true ecological validity in the wild.

## 14. Future Work
- Collecting and incorporating genuine, human-generated query data.
- Improving robustness against typographical errors and highly ambiguous requests.
- Deploying dynamic connectors to ingest live institutional data (e.g., live course registration systems) rather than static PDFs.
