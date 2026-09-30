"""Approved-source registry (SOURCE_POLICY.md).

Ingestion fails closed: a source is usable only if it is present in the registry
with ``approval_status == "approved"``. Unknown sources are rejected.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

REQUIRED_FIELDS = ("source_id", "title", "uri", "authority", "document_type", "approval_status")


class SourceNotApprovedError(RuntimeError):
    """Raised when ingestion is attempted on a non-approved / unknown source."""


@dataclass
class SourceRecord:
    source_id: str
    title: str
    uri: str
    authority: str
    document_type: str
    approval_status: str = "unapproved"
    version: str | None = None
    published_at: str | None = None
    effective_from: str | None = None
    retrieved_at: str | None = None
    content_hash: str | None = None
    license: str | None = None
    notes: str = ""
    local_path: str | None = None
    demo_only: bool = False

    @property
    def approved(self) -> bool:
        return self.approval_status.strip().lower() == "approved"


@dataclass
class SourceRegistry:
    records: dict[str, SourceRecord] = field(default_factory=dict)

    @staticmethod
    def load(path: Path) -> SourceRegistry:
        if not path.exists():
            return SourceRegistry()
        raw = json.loads(path.read_text(encoding="utf-8"))
        entries = raw["sources"] if isinstance(raw, dict) and "sources" in raw else raw
        records: dict[str, SourceRecord] = {}
        for e in entries:
            missing = [f for f in REQUIRED_FIELDS if f not in e]
            if missing:
                raise ValueError(f"source registry entry missing fields {missing}: {e}")
            rec = SourceRecord(**{k: e.get(k) for k in SourceRecord.__dataclass_fields__ if k in e})
            records[rec.source_id] = rec
        return SourceRegistry(records)

    def get(self, source_id: str) -> SourceRecord | None:
        return self.records.get(source_id)

    def is_approved(self, source_id: str) -> bool:
        rec = self.records.get(source_id)
        return bool(rec and rec.approved)

    def require_approved(self, source_id: str) -> SourceRecord:
        rec = self.records.get(source_id)
        if rec is None:
            raise SourceNotApprovedError(f"source {source_id!r} is not in the registry (rejected)")
        if not rec.approved:
            raise SourceNotApprovedError(
                f"source {source_id!r} has approval_status={rec.approval_status!r} (rejected)"
            )
        return rec

    def approved_sources(self) -> list[SourceRecord]:
        return [r for r in self.records.values() if r.approved]
