"""Ingest approved sources into chunks and write an ingestion manifest.

Only sources marked approved in the registry are ingested (the pipeline fails
closed on anything else). Produces artifacts/ingest_manifest.json.
"""

from __future__ import annotations

import json

import _common

from backend.app.ingestion.pipeline import ingest_sources


def main() -> int:
    settings = _common.get_settings()
    _common.configure_logging(settings.log_level)
    _common.banner("Ingest approved sources")

    chunks, manifest = ingest_sources(settings)
    if not chunks:
        _common.fail("no chunks produced — check SOURCE_REGISTRY_PATH and approvals")
        return 1

    demo = sum(1 for m in manifest if m.get("demo_only"))
    _common.ok(f"ingested {len(chunks)} chunks from {len(manifest)} approved sources")
    print(f"       demo_only sources: {demo}/{len(manifest)}")
    for m in manifest:
        flag = " [DEMO_ONLY]" if m.get("demo_only") else ""
        print(f"       - {m.get('source_id')}: {m.get('chunk_count')} chunks{flag}")

    out = _common.artifacts_dir(settings) / "ingest_manifest.json"
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    _common.ok(f"wrote {out.relative_to(_common.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
