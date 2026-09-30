# Source Policy

## Purpose

Define exactly what the chatbot considers authoritative.

## Approved source categories

Only sources explicitly registered in the source registry are allowed:

- official college website
- official department website
- official syllabus/curriculum PDF
- official academic regulation PDF
- official academic calendar
- official examination circular/schedule
- official student-services documentation

## Not authoritative by default

- Wikipedia
- student blogs
- Reddit
- unofficial WhatsApp messages
- random PDFs
- third-party education sites
- model memory
- search snippets

These may help a human research the issue, but they must not be used as the factual source for an MVP answer.

## Source registry fields

```text
source_id
title
uri
authority
document_type
version
published_at
effective_from
retrieved_at
content_hash
license
approval_status
notes
```

## Freshness

Do not declare a source current merely because it is newer-looking.

A source is current only when its official version/effective metadata supports that conclusion.

## Ingestion rule

If an input source is not in the registry with `approval_status=approved`, ingestion must fail closed.
