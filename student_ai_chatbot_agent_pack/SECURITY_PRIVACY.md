# Security, Privacy, Compliance, and Ethics

## 1. Data minimization

The MVP should not require student identity.

Do not collect:

- roll number
- phone number
- personal email
- marks
- attendance records
- disciplinary records
- private academic records

unless an explicit authenticated feature is added later.

## 2. Logging

Logs should contain:

- trace ID
- route
- latency
- status
- intent
- retrieval IDs
- provider/model
- error category

Avoid logging raw user text by default.

If raw text is required temporarily for debugging, make it opt-in and document retention/deletion.

## 3. Privacy controls

- secrets via environment variables
- least-privilege DB roles
- HTTPS in deployment
- admin/student separation
- source access control
- retention policy
- deletion mechanism for feedback or logs

## 4. Bias checks

The evaluation set should include:

- spelling variations
- informal student language
- different levels of technical vocabulary
- short and long queries
- first-year through final-year curriculum terminology

Do not intentionally infer or classify sensitive personal attributes.

## 5. Accessibility

Frontend should support:

- keyboard navigation
- readable contrast
- semantic headings
- screen-reader labels
- visible loading/error states

## 6. Auditability

Every factual answer should be traceable to:

- source document
- source version
- chunk
- model run
- configuration version

## 7. Licensing

Maintain a source-license register.

Never publish a source corpus until redistribution rights are established.

Third-party model and library licenses must be recorded in a dependency/license report.

## 8. AI safety

Prompt injection defenses:

- user input cannot change system safety rules
- retrieved text is delimited and treated as evidence
- citations are generated from IDs, not arbitrary URLs
- tools are not exposed to the generator by default

## 9. Ethical boundary

This chatbot informs students. It does not make high-impact academic decisions on behalf of the institution or students.
