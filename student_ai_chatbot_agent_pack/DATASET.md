# Dataset Specification — CampusFAQ-12K v1.0

## 1. Dataset decision

The sole canonical project dataset is:

**CampusFAQ-12K v1.0**

It is a **project-owned, evidence-grounded dataset** built specifically for this college chatbot.

It is not a generic chatbot dataset. This is intentional: the target task is campus-specific intent detection and grounded answering.

## 2. Dataset construction source

The dataset must be constructed from an approved corpus of authoritative college materials, for example:

- official curriculum/syllabus documents
- official academic regulations
- official academic calendar
- official examination rules/schedules
- official department pages
- official student-services pages
- official administrative circulars

The exact college and source list are project inputs and MUST NOT be invented.

If those source files/URLs are missing, the agent must ask the user for them.

## 3. Dataset size

Exactly 12,000 records for v1.

Class design:

- 24 intents
- 500 records per intent
- total = 12,000

Split:

- train: 9,600
- validation: 1,200
- test: 1,200

Each split must preserve intent distribution as 400/50/50 examples per intent.

## 4. Record schema

JSONL record:

```json
{
  "id": "campusfaq_000001",
  "query": "How many credits are in semester 4?",
  "intent": "semester_credits",
  "response": "string",
  "document_id": "DOC-0007",
  "document_version": "2026-01",
  "evidence": [
    {
      "chunk_id": "DOC-0007-C012",
      "quote": "short exact supporting span",
      "location": "page 12, section 3.2"
    }
  ],
  "entities": {
    "program": "CSE",
    "semester": 4
  },
  "answerable": true,
  "difficulty": "easy|medium|hard|adversarial",
  "split": "train|val|test"
}
```

## 5. Data creation rules

Every answerable record must include evidence.

The `response` must be derivable from the evidence without adding unsupported facts.

Queries should include natural student language:

- abbreviations defined by project glossary
- spelling variation
- short queries
- full questions
- informal phrasing
- multi-step questions
- entity-heavy queries

Do not add facts not contained in the source corpus.

## 6. Response categories

Target composition:

- 40% direct fact
- 20% short list
- 15% procedure
- 10% comparison
- 5% source-location
- 10% abstention/unknown/adversarial

The exact per-intent distribution can vary when the source material makes a category impossible; record the reason in the data-generation log.

## 7. Hard-negative and adversarial records

At least 10% of the dataset should contain:

- wrong semester
- similar course name
- close course code
- stale document version
- unsupported campus question
- incomplete question
- conflicting wording
- prompt-injection-like document text

These records are for robustness, not for teaching the model to invent answers.

## 8. Leakage prevention

Do not create train/test records by simple random duplication of paraphrases.

Perform:

- near-duplicate detection
- question similarity clustering
- document-version grouping

Keep semantically near-identical families in one split whenever feasible.

## 9. Provenance

Each answer must store source document ID/version and evidence chunk IDs.

The repository should store only metadata and approved derived artifacts in Git.

Raw copyrighted source documents should not be committed unless licensing/permission explicitly allows redistribution.

## 10. Licensing

CampusFAQ-12K is not automatically an open-source dataset.

For MVP, use this policy:

- raw college documents: **restricted/internal educational use unless their license explicitly permits redistribution**
- project-authored annotations and synthetic/paraphrased queries: owned by the project team, but distribution rights remain subject to the rights of the underlying sources
- do not publish the raw corpus or verbatim source passages without permission
- keep a `SOURCE_LICENSE_REGISTER` recording the license/permission for every source

Before public release, obtain explicit permission for any source that does not grant redistribution rights.

## 11. Quality gates for the dataset

Block model training if any of these occur:

- missing intent labels
- invalid intent label
- answerable record without evidence
- citation refers to missing chunk
- malformed JSONL
- duplicate IDs
- cross-split leakage
- unsupported claims detected during QA
- source registry says `unapproved`

## 12. Dataset commands

Planned:

```bash
python scripts/ingest_sources.py
python scripts/build_dataset.py
python scripts/preprocess.py
python scripts/validate_dataset.py
```

All commands must save a versioned manifest under `artifacts/data/`.
