"""Source parsing → normalized sections.

Supports Markdown/plain text and HTML with the standard library. PDF is
supported when ``pypdf`` is installed (optional). Each parsed section carries a
heading and a human-readable location for citations.
"""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path


@dataclass
class Section:
    heading: str
    text: str
    location: str


@dataclass
class ParsedDocument:
    sections: list[Section]


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in ("script", "style"):
            self._skip += 1
        if tag in ("p", "br", "div", "li", "tr", "h1", "h2", "h3", "h4"):
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip and data.strip():
            self._chunks.append(data)

    def text(self) -> str:
        return "".join(self._chunks)


def _parse_markdown(text: str) -> list[Section]:
    sections: list[Section] = []
    heading = "Introduction"
    buf: list[str] = []

    def flush() -> None:
        body = "\n".join(buf).strip()
        if body:
            sections.append(Section(heading=heading, text=body, location=f"Section: {heading}"))

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            flush()
            heading = stripped.lstrip("#").strip() or heading
            buf = []
        else:
            buf.append(line)
    flush()
    return sections or [Section("Document", text.strip(), "Document")]


def _parse_pdf(path: Path) -> list[Section]:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "PDF parsing requires 'pypdf'. Install it or convert the source to text/markdown."
        ) from exc
    reader = PdfReader(str(path))
    sections: list[Section] = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            sections.append(Section(heading=f"Page {i}", text=text, location=f"Page {i}"))
    return sections


def parse_source(path: Path) -> ParsedDocument:
    suffix = path.suffix.lower()
    if suffix in (".md", ".markdown", ".txt"):
        return ParsedDocument(_parse_markdown(path.read_text(encoding="utf-8")))
    if suffix in (".html", ".htm"):
        extractor = _HTMLTextExtractor()
        extractor.feed(path.read_text(encoding="utf-8"))
        return ParsedDocument(_parse_markdown(extractor.text()))
    if suffix == ".pdf":
        return ParsedDocument(_parse_pdf(path))
    raise ValueError(f"unsupported source format: {suffix}")
