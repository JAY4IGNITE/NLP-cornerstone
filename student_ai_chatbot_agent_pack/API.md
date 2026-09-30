# API Contract

## POST /api/chat

### Request

```json
{
  "message": "How many credits are in semester 4?"
}
```

### Response

```json
{
  "trace_id": "uuid",
  "status": "answered",
  "answer": "The verified curriculum source lists ...",
  "citations": [
    {
      "document_id": "DOC-0007",
      "title": "B.Tech CSE Curriculum",
      "location": "Page 12, Section 3.2"
    }
  ],
  "intent": {
    "label": "semester_credits",
    "confidence": 0.96
  }
}
```

## POST /api/feedback

```json
{
  "trace_id": "uuid",
  "rating": "helpful|not_helpful",
  "reason": "optional predefined code"
}
```

Do not accept free-form sensitive personal data in MVP feedback.

## GET /api/health

Returns:

```json
{
  "status": "ok",
  "version": "string",
  "knowledge_base_version": "string"
}
```

## POST /api/admin/reindex

Admin-only.

Request:

```json
{
  "source_version": "string"
}
```

The endpoint must require authentication in non-development environments.

## Error contract

```json
{
  "trace_id": "uuid",
  "status": "error",
  "code": "VALIDATION_ERROR|PROVIDER_ERROR|INDEX_ERROR|INTERNAL_ERROR",
  "message": "safe human-readable message"
}
```

Do not leak stack traces, API keys, internal file paths, SQL, or provider credentials.
