# Product Requirements Document

## 1. Product

**Name:** Student AI Chatbot

**Type:** NLP cornerstone project / college information assistant

**Primary users:** college students

**Primary job:** answer questions about curriculum and related college information using verified institutional sources.

## 2. Problem

Students repeatedly search syllabi, curriculum PDFs, academic calendars, examination regulations, department pages, and administrative information. Information is fragmented, terminology varies, and students may not know which document contains the answer.

The system provides a conversational interface over this information while preserving source traceability.

## 3. Scope

### In scope

- curriculum and syllabus questions
- subject/course details
- semester structure
- credits and prerequisites when present in official sources
- academic calendar information
- examination rules when present in approved sources
- general administrative FAQs from approved documents
- source citations
- confidence / evidence indicators
- abstention when evidence is insufficient
- English-language student queries
- intent classification
- RAG retrieval
- evaluation harness

### Out of scope for MVP

- personalized academic advising
- diagnosis of student performance
- automatic enrollment
- grading
- admissions decisions
- scholarship eligibility decisions
- legal/medical advice
- unrestricted internet search
- access to private student records

## 4. Functional requirements

### FR-01: Query intake

The system accepts a free-text student question.

### FR-02: Intent detection

The system predicts one of 24 supported campus intents and a confidence value.

### FR-03: Retrieval

The system retrieves relevant passages from the approved knowledge base.

### FR-04: Answer generation

The generator produces a concise answer grounded only in retrieved evidence.

### FR-05: Citation

Each factual answer must expose source title plus page/section/chunk reference where available.

### FR-06: Abstention

The system must abstain when:

- retrieval score is below the configured threshold
- no approved source supports the claim
- conflicting sources exist and precedence is unresolved
- the question is outside the supported scope
- the user requests private information not accessible to the chatbot

### FR-07: Audit trace

Each request gets a trace ID and records:

- timestamp
- normalized query
- predicted intent
- intent confidence
- retrieved document IDs
- retrieval scores
- selected evidence IDs
- model/provider identifier
- latency
- answer status: answered / abstained / error

Do not log raw personally identifying user information.

## 5. Non-functional requirements

### Performance targets

- intent classification p95: <= 100 ms locally
- retrieval p95: <= 300 ms locally for MVP corpus
- API end-to-end p50: <= 2.0 s excluding provider cold starts
- API end-to-end p95: <= 4.0 s excluding external-provider outages
- index build: deterministic and rerunnable
- application should remain usable on ordinary student hardware

### Quality targets

Release candidate gates:

- intent macro F1 >= 0.90
- intent accuracy >= 0.90
- retrieval recall@5 >= 0.90 on held-out qrels
- retrieval MRR@5 >= 0.75
- unsupported-answer rate <= 3%
- citation validity >= 95%
- human groundedness pass rate >= 90%
- human correctness pass rate >= 90%

These are target gates, not claims about achieved performance.

## 6. Validation approach

Validation is performed in five layers:

1. schema/data validation
2. intent classification evaluation
3. retrieval evaluation
4. grounded response evaluation
5. end-to-end human acceptance testing

A feature cannot be called validated because a single model metric passed.

## 7. Primary user experience

Example:

Student:
> How many credits are required in semester 4 for CSE?

System:
- predicts `curriculum_credits`
- retrieves the official semester/course source
- answers using the source
- cites the source section/page

If no authoritative evidence exists:

> I don't have enough verified information in the college knowledge base to answer that accurately.

## 8. Acceptance criteria

The MVP is accepted when:

- the application starts locally with documented commands
- a seeded/fixture knowledge base can be indexed
- a query can be classified
- relevant passages can be retrieved
- grounded answer generation works through at least one configured LLM provider
- citations are visible
- abstention works
- automated evaluation scripts run end-to-end
- reproducibility artifacts are saved
- tests pass
- the agent has not invented missing college facts
