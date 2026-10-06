# NLP-Cornerstone — Master Implementation Plan

## Purpose

Transform the existing `JAY4IGNITE/NLP-cornerstone` repository into a clean, academically defensible NLP project without rebuilding the application from scratch.

The final system must demonstrate:

**dataset → preprocessing → intent classification → semantic retrieval → evidence grounding → evaluation → application**

Do not fabricate data, metrics, sources, or claims.

---

## 1. Final Project Definition

### Title

**CampusNLP: An Intelligent NLP-Based University Student Query Understanding and Knowledge Retrieval System**

### Research Question

> Can a hybrid NLP pipeline combining intent classification, semantic retrieval, and institution-specific knowledge grounding accurately understand and answer university student queries?

### Core Objective

Build an NLP system that:
1. understands student queries,
2. predicts query intent,
3. retrieves relevant academic evidence,
4. produces a grounded response,
5. exposes the supporting source,
6. abstains when reliable evidence is unavailable.

The project is an **NLP and information-retrieval system**, not merely an LLM chatbot.

---

## 2. Non-Negotiable Data Policy

### CampusFAQ-50K

Treat `CampusFAQ-50K` as a **synthetic controlled benchmark**.

Never describe it as:
- real student conversations,
- naturally collected student data,
- authentic university queries.

Document:
- 50,000 records,
- 24 intents,
- train/validation/test split,
- synthetic/generated origin,
- intended use for controlled benchmarking.

### Institutional Knowledge Base

Use approved/public university or college information where available:
- academic calendar,
- regulations,
- attendance rules,
- examination rules,
- curriculum,
- courses,
- departments,
- student services,
- placements,
- scholarships,
- library,
- hostel,
- transport,
- official contacts.

Every document must retain source metadata.

### Student Evaluation Set

Create `data/evaluation/real_student_queries.csv` only from genuinely collected and manually labelled student queries.

Do not fabricate a "real-world" dataset.

Recommended schema:

```
query,intent,answerable,expected_evidence,difficulty,source
```

If a real evaluation set cannot be collected before review, explicitly state that limitation instead of inventing records.

---

## 3. Final Repository Structure

Target structure:

```
NLP-cornerstone/
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── .env.example
│
├── data/
│   ├── benchmark/
│   │   └── campusfaq_50k.csv
│   ├── institutional/
│   │   ├── academic_calendar/
│   │   ├── regulations/
│   │   ├── curriculum/
│   │   ├── departments/
│   │   └── student_services/
│   ├── structured/
│   │   ├── courses.json
│   │   ├── intents.json
│   │   └── resource_catalog.json
│   └── evaluation/
│       └── real_student_queries.csv
│
├── notebooks/
│   ├── 01_dataset_analysis.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_intent_classification.ipynb
│   ├── 04_semantic_retrieval.ipynb
│   └── 05_evaluation.ipynb
│
├── src/
│   ├── preprocessing/
│   │   └── text_preprocessor.py
│   ├── classification/
│   │   ├── train.py
│   │   └── predict.py
│   ├── retrieval/
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   └── retriever.py
│   ├── evaluation/
│   │   └── metrics.py
│   └── pipeline.py
│
├── models/
│   ├── intent_classifier/
│   └── embeddings/
│
├── backend/
├── frontend/
├── tests/
│   ├── test_preprocessing.py
│   ├── test_classifier.py
│   └── test_retrieval.py
│
└── docs/
    ├── DATASET_METHODOLOGY.md
    ├── NLP_PIPELINE.md
    ├── EXPERIMENTS.md
    ├── EVALUATION.md
    └── LIMITATIONS.md
```

Do not force this structure if an existing file already performs the same responsibility correctly. Prefer moving/refactoring over duplicating functionality.

---

## 4. Existing Repository: Preserve Before Refactoring

The current repository contains a working foundation including:
- `CampusFAQ-50K-v1.0/`
- `data/`
- `documents/`
- `backend/`
- `src/`
- `data_processing_and_training.ipynb`
- frontend/build configuration
- deployment configuration.

Do **not** delete these blindly.

First inspect their contents and references.

---

## 5. File Classification Rules

For every existing file, classify it as:

### KEEP
Required for:
- NLP pipeline,
- application,
- data,
- deployment,
- reproducibility,
- documentation,
- testing.

### MOVE
Useful but located in the wrong directory.

### MODIFY
Useful but inconsistent with the final architecture.

### MERGE
Duplicate functionality or duplicate datasets.

### DELETE
Only if:
- unused,
- duplicate,
- generated junk,
- obsolete debugging code,
- credentials/secrets,
- temporary build output,
- redundant experimental artifact.

Never delete a file solely because its name looks unnecessary. Search references first.

---

## 6. Specific Existing Root Files

### `README.md`
**MODIFY/REWRITE**

Replace generic starter/template content with:
1. Project overview
2. Problem statement
3. Research question
4. Objectives
5. Architecture
6. Dataset methodology
7. NLP pipeline
8. Experiments
9. Evaluation
10. Installation
11. API usage
12. Demo
13. Limitations
14. Future work

### `data_processing_and_training.ipynb`
**KEEP temporarily, then split useful sections**

Use it as the source for:
- dataset analysis,
- preprocessing,
- training,
- evaluation.

Create the five organized notebooks after preserving reproducible logic.

### `fix_props.cjs`
Inspect usage.

Delete only if no current build/development process requires it.

### `test_api_keys.py`
Inspect it carefully.

If it only checks local credentials or contains unsafe credential-testing logic, replace it with a safe configuration/health test. Never commit real API keys.

### `metadata.json`
Keep only if it is actually consumed by the application/tooling.

Otherwise remove after reference check.

### `presentation/`
Keep only presentation artifacts genuinely required for submission.

Do not allow presentation files to become part of the runtime pipeline.

### `student_ai_chatbot_agent_pack/`
Audit contents.

Keep only components that directly support the final NLP system or documentation. Remove duplicate prompts, generated artifacts, and unrelated agent experiments.

### `bun.lock`, `package.json`, `vite.config.ts`, `tsconfig.json`, `index.html`
Keep if the current frontend depends on them.

Do not introduce a second package manager unnecessarily.

### `render.yaml`
Keep if Render deployment is still used.

### `.env.example`
Keep.

Ensure it contains variable names only, never real secrets.

### `.gitignore`
Strengthen it to exclude:
- `.env`
- `node_modules/`
- `__pycache__/`
- `*.pyc`
- `.ipynb_checkpoints/`
- `dist/`
- `build/`
- local model/cache files that are not required
- OS/editor temporary files.

---

## 7. Dataset Organization

Move data logically:

```
data/benchmark/
    campusfaq_50k.csv

data/structured/
    intents.json
    courses.json
    resource_catalog.json

data/institutional/
    <official documents>

data/evaluation/
    real_student_queries.csv
```

Do not maintain multiple files representing the same dataset version.

Use clear naming:
- `raw`
- `processed`
- `benchmark`
- `evaluation`

only when the stages genuinely exist.

---

## 8. Intent Taxonomy

Maintain a documented intent taxonomy.

Recommended intents include:

```
attendance_rules
exam_schedule
exam_rules
course_information
course_prerequisites
curriculum
academic_calendar
faculty_information
department_information
registration
fees
scholarships
hostel
library
placements
clubs
student_services
certificates
transport
contact_information
grading
results
leave_rules
general_information
```

Do not add an intent unless examples and evaluation data support it.

Each intent should have:
- identifier,
- description,
- representative examples.

---

## 9. Preprocessing

Implement and document only preprocessing that is actually used.

Recommended pipeline:

```
Raw Query
→ text normalization
→ whitespace normalization
→ noise handling
→ tokenization
→ feature extraction
```

Avoid unnecessary preprocessing that damages semantic meaning.

Show before/after examples in the notebook.

---

## 10. Baseline Classification Experiments

Implement reproducible baselines:

### Experiment A
TF-IDF + Logistic Regression

### Experiment B
TF-IDF + Linear SVM

### Experiment C
Embedding-based semantic retrieval

### Experiment D
Hybrid intent + retrieval pipeline

For every experiment record:
- dataset split,
- preprocessing,
- model,
- hyperparameters,
- metrics,
- runtime if practical.

Never hard-code performance numbers.

---

## 11. Semantic Retrieval

Build a retrieval layer over institutional documents.

Pipeline:

```
Documents
→ text extraction
→ chunking
→ metadata attachment
→ embeddings
→ similarity index
→ Top-K retrieval
→ evidence ranking
```

Each chunk should preserve:

```
document_id
document_name
page_number
section
text
source_url
```

Use existing `documents/` content if it is suitable. Do not duplicate the same documents into multiple folders.

---

## 12. Hybrid Query Pipeline

Implement one central pipeline:

```
Student Query
      ↓
Preprocessing
      ↓
Intent Classification
      ↓
 ┌────┴─────────────┐
 ↓                  ↓
Structured Lookup   Semantic Retrieval
 ↓                  ↓
 └────────┬─────────┘
          ↓
    Evidence Ranking
          ↓
    Confidence Check
       /       \
      /         \
 confident    uncertain
    ↓             ↓
 grounded       abstain
 answer          safely
    ↓
 source citation
```

Avoid implementing separate competing pipelines that produce inconsistent answers.

---

## 13. Confidence and Abstention

If evidence similarity/confidence is below a documented threshold:

Do not invent an answer.

Return an explicit abstention response such as:

> I could not find sufficiently reliable information in the available university knowledge base.

Expose:
- confidence,
- intent,
- evidence,
- source.

Thresholds must be configurable and evaluated rather than arbitrarily hidden.

---

## 14. API Contract

The main endpoint should conceptually support:

```
POST /api/query
```

Input:

```json
{
  "query": "What is the minimum attendance required?"
}
```

Output:

```json
{
  "query": "What is the minimum attendance required?",
  "intent": "attendance_rules",
  "confidence": 0.91,
  "answer": "...",
  "sources": [
    {
      "document": "Academic Regulations",
      "page": 12
    }
  ]
}
```

The exact confidence value must come from the actual implementation.

---

## 15. Evaluation

### Intent Classification

Measure:
- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix

### Retrieval

Measure where feasible:
- Precision@K
- Recall@K
- MRR
- Top-K accuracy

### Grounding

Measure:
- source correctness,
- evidence relevance,
- answerability,
- unsupported-answer rate.

### Abstention

Measure:
- abstention accuracy,
- false-answer rate,
- low-confidence behavior.

Do not invent evaluation values.

---

## 16. Notebook Deliverables

### `01_dataset_analysis.ipynb`

Must show:
- shape,
- columns,
- missing values,
- duplicate analysis,
- intent distribution,
- class balance,
- representative samples.

### `02_preprocessing.ipynb`

Must show:
- raw examples,
- preprocessing transformations,
- resulting representation.

### `03_intent_classification.ipynb`

Must show:
- TF-IDF,
- Logistic Regression,
- Linear SVM,
- classification report,
- confusion matrix,
- comparison table.

### `04_semantic_retrieval.ipynb`

Must show:
- document chunks,
- metadata,
- embeddings,
- similarity search,
- Top-K examples.

### `05_evaluation.ipynb`

Must show:
- final metrics,
- retrieval metrics,
- groundedness/evidence evaluation,
- abstention evaluation,
- error analysis.

---

## 17. Documentation Deliverables

Create:

### `docs/DATASET_METHODOLOGY.md`

Document:
- benchmark source,
- synthetic nature,
- schema,
- collection/generation process,
- split,
- preprocessing,
- limitations.

### `docs/NLP_PIPELINE.md`

Document:
- preprocessing,
- TF-IDF,
- classifiers,
- embeddings,
- retrieval,
- evidence ranking,
- confidence.

### `docs/EXPERIMENTS.md`

Document:
- baseline models,
- experimental setup,
- hyperparameters,
- results.

### `docs/EVALUATION.md`

Document:
- metrics,
- test methodology,
- results,
- error analysis.

### `docs/LIMITATIONS.md`

State clearly:
- synthetic benchmark limitations,
- limited real student query coverage,
- institution-specific knowledge dependence,
- retrieval errors,
- possible ambiguity,
- stale documents,
- unsupported queries.

---

## 18. Frontend Requirements

Do not spend excessive time redesigning the UI.

The interface must visibly demonstrate:

1. Student query
2. Predicted intent
3. Answer
4. Confidence
5. Evidence/source
6. Abstention for unsupported queries

Example:

```
Query
"What is the minimum attendance?"

Detected Intent
attendance_rules

Answer
...

Confidence
91%

Evidence
Academic Regulations — Page 12
```

Only display confidence if it is calculated by the actual system.

---

## 19. Testing

Add tests for:

### Preprocessing
- empty input,
- normal query,
- punctuation,
- whitespace,
- mixed case.

### Classification
- known intent,
- ambiguous query,
- malformed input.

### Retrieval
- relevant document,
- no relevant document,
- metadata preservation.

### Pipeline
- complete successful query,
- low-confidence query,
- source citation.

---

## 20. Security

Never commit:
- API keys,
- passwords,
- tokens,
- private credentials.

Audit:
- `.env`,
- test scripts,
- deployment configuration,
- frontend environment variables.

Use `.env.example` for documentation.

---

## 21. Cleanup Rules

Remove after reference checking:

- duplicate datasets,
- duplicate notebooks,
- obsolete scripts,
- generated build directories,
- node_modules,
- Python caches,
- notebook checkpoints,
- temporary exports,
- unused API key testers,
- obsolete model versions,
- unrelated agent experiments,
- duplicate presentation assets.

Never delete:
- source data needed for reproducibility,
- final model required by the app,
- deployment configuration in active use,
- useful experiments required to substantiate claims.

---

## 22. README Claims

The README must never claim:
- "real-world dataset" for synthetic data,
- "100% accurate",
- "production-ready" without evidence,
- "hallucination-free",
- "real student conversations" unless verified.

Use academically defensible wording.

---

## 23. Review Demonstration

The main live demo must follow this sequence:

### Example

Input:

> What is the minimum attendance required?

Show:

```
Preprocessing
      ↓
Intent: attendance_rules
      ↓
Retrieve relevant evidence
      ↓
Top-K documents
      ↓
Evidence ranking
      ↓
Grounded response
      ↓
Source citation
```

Then demonstrate an unsupported question and show safe abstention.

---

## 24. Faculty Explanation

Use this concise explanation:

> Our system is an NLP-based university query understanding and knowledge retrieval system. We use CampusFAQ-50K as a synthetic controlled benchmark for intent classification, while institution-specific documents provide the factual knowledge layer. The NLP pipeline performs preprocessing and intent classification, followed by semantic retrieval and evidence ranking. The final answer is grounded in retrieved evidence, and the system can abstain when reliable evidence is unavailable. We evaluate both classification and retrieval performance instead of measuring only chatbot response quality.

---

## 25. Implementation Order

Execute in this exact order:

### Phase 1 — Audit
1. Inspect all files.
2. Find duplicate datasets.
3. Find unused scripts.
4. Identify actual application entry points.
5. Identify current NLP pipeline.
6. Identify actual model artifacts.
7. Audit `real_world_university_queries.csv`.
8. Audit `university_faq_cleaned_augmented.csv`.
9. Audit documents.

### Phase 2 — Cleanup
1. Remove only confirmed junk.
2. Move datasets.
3. Consolidate duplicates.
4. Strengthen `.gitignore`.
5. Protect secrets.

### Phase 3 — Research Pipeline
1. Formalize preprocessing.
2. Formalize intent taxonomy.
3. Train/evaluate baselines.
4. Build document chunks.
5. Build semantic retrieval.
6. Integrate hybrid pipeline.
7. Add confidence/abstention.

### Phase 4 — Evaluation
1. Generate actual metrics.
2. Create confusion matrix.
3. Evaluate retrieval.
4. Evaluate source correctness.
5. Evaluate abstention.
6. Perform error analysis.

### Phase 5 — Application
1. Connect backend to final pipeline.
2. Return intent/confidence/evidence.
3. Update frontend.
4. Verify end-to-end flow.

### Phase 6 — Documentation
1. Rewrite README.
2. Add dataset methodology.
3. Add NLP pipeline documentation.
4. Add experiment documentation.
5. Add evaluation documentation.
6. Add limitations.

### Phase 7 — Final Validation
Run:
- backend health check,
- frontend build,
- training/inference smoke test,
- test suite,
- representative query demo,
- unsupported query demo.

---

## 26. Definition of Done

The project is considered complete only when:

- [ ] Existing application still works.
- [ ] Synthetic benchmark is honestly labelled.
- [ ] Dataset sources are documented.
- [ ] Intent taxonomy is documented.
- [ ] Preprocessing is reproducible.
- [ ] At least two classification baselines are evaluated.
- [ ] Semantic retrieval works.
- [ ] Hybrid pipeline works.
- [ ] Evidence/source is returned.
- [ ] Low-confidence queries can abstain.
- [ ] Actual metrics are generated.
- [ ] Confusion matrix exists.
- [ ] Retrieval evaluation exists where ground truth permits.
- [ ] No fabricated metrics exist.
- [ ] No secrets are committed.
- [x] Duplicate/unnecessary files are removed.
- [ ] README explains the research contribution.
- [ ] The frontend demonstrates the NLP pipeline.
- [ ] The repository can be understood by a reviewer without asking the developer.

---

## 27. Critical Constraints

1. **Do not rebuild from scratch.**
2. **Do not replace the benchmark merely to obtain a larger number.**
3. **Do not fabricate real student data.**
4. **Do not fabricate metrics.**
5. **Do not add an LLM merely for marketing.**
6. **Do not claim a retrieval result is correct without evidence.**
7. **Do not delete files before checking references.**
8. **Do not duplicate existing functionality.**
9. **Prefer simple, reproducible NLP methods over unnecessary complexity.**
10. **Keep the application functional throughout the refactor.**

---

## Final Architecture

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
                 |
                 v
              EVALUATION
```

**Final principle:**

> Keep the existing working system, clean its structure, make the dataset methodology honest, strengthen the NLP pipeline, add institution-specific retrieval, evaluate it properly, and make every important claim reproducible.
