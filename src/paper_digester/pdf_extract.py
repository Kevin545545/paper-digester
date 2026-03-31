from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader

_STOP_HEADINGS = [
    "references",
    "bibliography",
    "acknowledgments",
    "acknowledgements",
    "appendix",
    "appendices",
]


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def find_stop_section_index(text: str) -> int | None:
    if not text:
        return None

    patterns = [
        re.compile(rf"(?:^|\n)\s*{re.escape(heading)}\s*(?:\n|$)", re.IGNORECASE)
        for heading in _STOP_HEADINGS
    ]

    first: int | None = None
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            idx = match.start()
            if first is None or idx < first:
                first = idx
    return first


def truncate_before_back_matter(text: str) -> str:
    idx = find_stop_section_index(text)
    if idx is None:
        return text.strip()
    return text[:idx].strip()


def extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    chunks: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            chunks.append(text)

    raw = "\n\n".join(chunks).strip()
    truncated = truncate_before_back_matter(raw)
    return normalize_whitespace(truncated)


def infer_title_from_pdf_path(pdf_path: Path) -> str:
    return pdf_path.stem.replace("_", " ").replace("-", " ").strip().title() or "Untitled PDF"
