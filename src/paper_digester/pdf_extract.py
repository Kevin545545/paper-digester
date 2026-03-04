from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


def extract_pdf_text(pdf_path: Path, max_pages: int = 2) -> str:
    reader = PdfReader(str(pdf_path))
    chunks: list[str] = []
    for page in reader.pages[:max_pages]:
        text = page.extract_text() or ""
        if text.strip():
            chunks.append(text.strip())
    return "\n\n".join(chunks).strip()


def infer_title_from_pdf_path(pdf_path: Path) -> str:
    return pdf_path.stem.replace("_", " ").replace("-", " ").strip().title() or "Untitled PDF"
