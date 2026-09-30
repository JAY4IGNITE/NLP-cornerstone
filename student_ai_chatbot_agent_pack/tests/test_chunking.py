"""Tests for ingestion (source registry -> chunks) and the chunker."""

from __future__ import annotations

import re

import pytest

from backend.app.ingestion.chunker import (
    OVERLAP_TOKENS,
    TARGET_TOKENS,
    chunk_document,
    chunk_section,
)
from backend.app.ingestion.metadata import DocumentMeta, chunk_id_for
from backend.app.ingestion.parser import ParsedDocument, Section
from backend.app.ingestion.source_registry import (
    SourceNotApprovedError,
    SourceRegistry,
)

CHUNK_ID_RE = re.compile(r"^DOC-DEMO-\d{4}-C\d{3}$")


def test_demo_ingestion_yields_expected_corpus(chunks, ingested):
    manifest = ingested[1]
    assert len(chunks) == 44
    assert len(manifest) == 9  # nine approved demo sources


def test_all_chunks_have_valid_ids_and_metadata(chunks):
    seen = set()
    for c in chunks:
        assert CHUNK_ID_RE.match(c.chunk_id), c.chunk_id
        assert c.chunk_id not in seen, "chunk ids must be unique"
        seen.add(c.chunk_id)
        assert c.content.strip(), "chunk content must be non-empty"
        assert c.approval_status == "approved"
        assert c.is_current is True
        # __post_init__ derives these
        assert len(c.content_hash) == 16
        assert c.token_count > 0


def test_known_fact_present_in_corpus(chunks):
    # Data Structures credits fact should be ingested verbatim.
    joined = "\n".join(c.content for c in chunks)
    assert "4 credits" in joined
    assert "75% attendance" in joined


def test_chunk_id_for_format():
    assert chunk_id_for("DOC-DEMO-0003", 3) == "DOC-DEMO-0003-C003"
    assert chunk_id_for("X", 12) == "X-C012"


def _meta() -> DocumentMeta:
    return DocumentMeta(
        document_id="DOC-DEMO-0999",
        document_version="v1",
        title="Test Doc",
        source_id="DOC-DEMO-0999",
        authority="Test Authority",
        document_type="curriculum",
    )


def test_short_section_is_single_chunk():
    section = Section(heading="Intro", text="a short section with few words", location="Section: Intro")
    out = chunk_section(section, _meta(), start_ordinal=1)
    assert len(out) == 1
    assert out[0].ordinal == 1
    assert out[0].location == "Section: Intro"
    assert out[0].heading == "Intro"


def test_long_section_splits_into_overlapping_windows():
    words = " ".join(f"w{i}" for i in range(TARGET_TOKENS * 2 + 50))
    section = Section(heading="Big", text=words, location="Section: Big")
    out = chunk_section(section, _meta(), start_ordinal=1)
    assert len(out) > 1
    # sequential ordinals + "(part N)" locations when a section is split
    assert [c.ordinal for c in out] == list(range(1, len(out) + 1))
    assert out[0].location == "Section: Big (part 1)"
    assert out[1].location == "Section: Big (part 2)"


def test_table_like_section_kept_whole():
    table = "\n".join(
        [
            "Course | Code | Credits",
            "Data Structures | CS201 | 4",
            "Algorithms | CS202 | 4",
            "Databases | CS303 | 3",
        ]
    )
    section = Section(heading="Scheme", text=table, location="Section: Scheme")
    out = chunk_section(section, _meta(), start_ordinal=5)
    assert len(out) == 1  # not fragmented
    assert "CS201" in out[0].content


def test_chunk_document_assigns_sequential_ordinals():
    doc = ParsedDocument(
        sections=[
            Section("A", "first section text", "Section: A"),
            Section("B", "second section text", "Section: B"),
        ]
    )
    out = chunk_document(doc, _meta())
    assert [c.ordinal for c in out] == [1, 2]


def test_registry_require_approved_and_rejections(settings):
    reg = SourceRegistry.load(settings.path(settings.source_registry_path))
    approved = reg.approved_sources()
    assert callable(SourceRegistry.approved_sources)  # it is a method
    assert len(approved) == 9
    # a known approved source resolves
    rec = reg.require_approved("DOC-DEMO-0003")
    assert rec.approved is True
    # unknown source is rejected (fails closed)
    with pytest.raises(SourceNotApprovedError):
        reg.require_approved("DOC-DOES-NOT-EXIST")


def test_target_and_overlap_constants_sane():
    assert TARGET_TOKENS > OVERLAP_TOKENS > 0
