# CampusNLP Presentation Content

*This document outlines the presentation for the "CampusNLP" project (NLP-cornerstone), directly mapped to the slide structure from your `review-2.pptx` template.*

---

## Slide 1: Title Page
**Title:** CampusNLP: An Intelligent NLP-Based University Student Query Understanding and Knowledge Retrieval System
**Team Members:** 
- N. Jagapathi Rama Rao (24B11CS313)
- V. Suraj Kaushik (24B11CS493)
- B.V.V. Vivek (24B11CS056)
- Ch. Sasi Kumar (24B11CS077)

---

## Slide 2: CONTENTS
- Introduction
- Problem Definition
- Proposed Solution
- Proposed Workflow
- Data Used
- Modules
  - Text Preprocessing
  - Intent Classification
  - Semantic Retrieval & Grounding
- NLP / ML Algorithm
- Output / Result
- Conclusion and Future Scope

---

## Slide 3: Introduction
**What is the project about?** 
CampusNLP is an intelligent NLP system designed to understand student queries, predict their intent, retrieve relevant academic evidence from an institutional knowledge base, and produce a grounded response with source citations.
**Application domain:** 
Natural Language Processing and Information Retrieval applied to university student services (e.g., academic regulations, curriculum, attendance rules).
**Why is this topic important?** 
Students often struggle to find accurate, institution-specific answers quickly. A grounded NLP system provides instant, reliable answers without fabricating information (hallucinations).
**What motivated the team?** 
We wanted to build a practical, hybrid NLP pipeline that goes beyond a simple LLM chatbot by combining intent classification and semantic retrieval, and crucially, knows how to abstain when reliable evidence is unavailable.

---

## Slide 4: Problem Definition
**Existing problem:** 
Institutional knowledge is scattered across various documents (regulations, curriculum, hostel rules), making manual search inefficient and time-consuming.
**Difficulties faced:** 
Students face delays in getting answers. Plain keyword searches fail on complexly worded queries, and off-the-shelf LLMs often invent incorrect, unverified answers.
**Why the problem is important:** 
Misinformation or delays can negatively affect a student's academic planning, course registration, and compliance with university rules.
**Who is affected:** 
University students, faculty, and administrative staff who handle repetitive queries.
**What needs to be improved:** 
A system that understands natural-language questions, directly extracts exact evidence from official documents, and only answers when highly confident.

---

## Slide 5: Proposed Solution
**Major functions:** 
Preprocess student queries, classify query intent (e.g., `exam_schedule`), retrieve relevant passages from the knowledge base, verify confidence, and output a grounded answer with source citations.
**Input → Processing → Output:** 
Student query → Preprocessing, Intent Classification, Semantic Retrieval, Evidence Ranking → Grounded answer with source citation (or a safe abstention).
**Expected users:** 
University students and administrative staff.
**Expected benefits:** 
Accurate, fast, and verifiable answers. Reduces manual query handling and prevents the spread of misinformation.
**Proposed methodology/workflow:** 
A hybrid approach using Intent Classification for structured lookup and Semantic Retrieval for unstructured document search, followed by a strict confidence check.

---

## Slide 6: Proposed Workflow (System Architecture)
**1. Query Preprocessing Layer:** Raw student queries undergo text normalization, whitespace correction, and tokenization before feature extraction.
**2. Intent Classification Layer:** The processed query is routed through a machine learning classifier to predict one of 24 distinct intents (e.g., `exam_schedule`, `fees`).
**3. Hybrid Information Retrieval Layer:** 
   - **Structured Lookup:** For deterministic intents, structured JSON catalogs (like course details) are queried.
   - **Semantic Retrieval:** For unstructured intents, institutional documents are chunked, embedded into dense vectors, and indexed. The system retrieves Top-K passages using cosine similarity.
**4. Evidence Ranking & Verification Check:** Retrieved passages are ranked. A configurable confidence threshold ensures only highly relevant evidence passes through.
**5. Grounded Answer Generation:** If confident, the system generates the answer and explicitly cites the source (document, page). If uncertain, it safely abstains.

---

## Slide 7: Data Used
**Source of data:** 
CampusFAQ-50K (a synthetic controlled benchmark) and an institutional knowledge base (academic calendar, regulations, curriculum).
**Type of data:** 
Unstructured text (official university documents) and structured question-answering pairs.
**Number of records:** 
50,000 records in the CampusFAQ-50K benchmark, spanning 24 intents.
**Important attributes/columns:** 
Query, intent, answerable, expected_evidence, difficulty, and source.
**Data format:** 
CSV files for datasets, JSON for structured lookups, and standard documents (PDFs/TXT) for the institutional knowledge base.

---

## Slide 8: Modules
**NLP Text Preprocessing & Feature Extraction:** 
Transforms raw natural language into machine-readable formats. Employs advanced tokenization, noise reduction, and TF-IDF (Term Frequency-Inverse Document Frequency) vectorization.
**Machine Learning Intent Classification:** 
A dedicated ML module that learns from 50,000 query examples (CampusFAQ-50K). It uses classification algorithms to categorize queries across 24 intent classes with high F1-score accuracy.
**Semantic Embedding & Document Retrieval:** 
Converts institutional text chunks into dense multidimensional vector embeddings. The retrieval module performs rapid similarity searches across this vector space to fetch exact evidence while preserving source metadata.

---

## Slide 9: Core NLP & ML Algorithms
**Intent Classification Models (TF-IDF + LR/SVM):** 
- **TF-IDF Vectorization:** Weights terms by their frequency in a query vs. their rarity across the dataset.
- **Logistic Regression & Linear SVM:** These algorithms learn the decision boundaries between 24 intents, providing highly accurate and fast structured query routing.
**Semantic Retrieval Models (Embeddings & Cosine Similarity):** 
- **Dense Vector Embeddings:** Encodes the semantic meaning of sentences into numerical vectors, allowing the system to match paraphrased questions even if exact keywords differ.
- **Cosine Similarity:** Ranks passages by measuring the cosine of the angle between the query vector and document chunk vectors: `cos(θ) = (A · B) / (||A|| ||B||)`.
**Algorithmic Thresholding (The "Abstention" Logic):** 
Applies a strict mathematical confidence threshold to the similarity scores. If the highest score falls below the threshold, the system deterministically abstains, ensuring zero hallucinations.

---

## Slide 10: Output / Result
**Main Interface:** 
Displays the student query, predicted intent, the final answer, confidence score, and the exact evidence/source document (e.g., "Academic Regulations — Page 12").
**Abstention Mechanism:** 
When evidence is below the confidence threshold, the system safely abstains instead of inventing an answer (No Info).
**Evaluation Metrics:** 
The system evaluates intent classification (Accuracy, Precision, F1-score) and retrieval (Precision@K, MRR), alongside grounding correctness.

---

## Slide 11: Conclusion and Future Scope
**Conclusion:** 
CampusNLP successfully demonstrates a hybrid NLP pipeline that understands student queries, retrieves verifiable institutional evidence, and answers with high accuracy while strictly avoiding hallucinations.
**Future Scope:** 
Expand the institutional knowledge base, improve retrieval accuracy on more complex multi-hop queries, and deploy the system across multiple university departments with a live student evaluation set.
