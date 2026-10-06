# CampusFAQ-50K Data Dictionary

| Field | Meaning |
|---|---|
| `id` | unique record ID |
| `query` | student-style question |
| `intent` | one of the 24 canonical intent classes |
| `response` | grounded answer generated from the canonical evidence |
| `document_id` | source document identifier |
| `document_version` | synthetic source version |
| `evidence` | evidence chunk ID, quote and location |
| `entities` | extracted/known academic entities |
| `answerable` | whether the KB contains evidence for the query |
| `difficulty` | easy/medium/hard |
| `split` | train/val/test |
| `source_authority` | DEMO_ONLY_SYNTHETIC |
| `provenance` | data-generation provenance |
