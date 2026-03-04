from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .arxiv_fetch import PaperMeta, fetch_arxiv_metadata, parse_arxiv_id
from .pdf_extract import extract_pdf_text, infer_title_from_pdf_path
from .utils import now_iso, safe_resolve_path, slugify


@dataclass
class NoteRecord:
    title: str
    authors: str
    year: str
    source: str
    abstract: str
    keywords: str
    tags: str
    added_at: str
    slug: str


def ensure_layout(project_root: Path) -> None:
    notes_dir = project_root / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    index = notes_dir / "INDEX.md"
    if not index.exists():
        index.write_text(_index_header(), encoding="utf-8")


def _index_header() -> str:
    return "# Paper Digester Index\n\n| Added At | Title | Year | Source | Tags |\n|---|---|---:|---|---|\n"


def build_note_template(record: NoteRecord) -> str:
    return (
        f"# {record.title}\n\n"
        f"- **Authors:** {record.authors}\n"
        f"- **Year:** {record.year}\n"
        f"- **Source:** {record.source}\n"
        f"- **Added-at:** {record.added_at}\n"
        f"- **Keywords:** {record.keywords}\n"
        f"- **Tags:** {record.tags}\n\n"
        "## Abstract\n\n"
        f"{record.abstract or 'N/A'}\n\n"
        "## Key Contributions\n\n"
        "- \n\n"
        "## Method Overview\n\n"
        "- \n\n"
        "## Strengths/Weaknesses\n\n"
        "- Strengths: \n"
        "- Weaknesses: \n\n"
        "## My Questions\n\n"
        "- \n"
    )


def add_paper(project_root: Path, source_input: str, tags: list[str] | None = None) -> Path:
    tags = tags or []
    ensure_layout(project_root)

    meta = _build_metadata(project_root, source_input)
    slug = slugify(meta.title)
    added_at = now_iso()
    note = NoteRecord(
        title=meta.title,
        authors=", ".join(meta.authors) if meta.authors else "Unknown",
        year=meta.year or "Unknown",
        source=meta.source,
        abstract=meta.abstract.strip() if meta.abstract else "",
        keywords="",
        tags=", ".join(tags),
        added_at=added_at,
        slug=slug,
    )

    note_path = project_root / "notes" / f"{slug}.md"
    note_path.write_text(build_note_template(note), encoding="utf-8")
    rebuild_index(project_root)
    return note_path


def _build_metadata(project_root: Path, source_input: str) -> PaperMeta:
    arxiv_id = parse_arxiv_id(source_input)
    if arxiv_id:
        meta = fetch_arxiv_metadata(source_input)
        if not meta:
            raise ValueError(f"Could not fetch metadata for arXiv input: {source_input}")
        return meta

    candidate = safe_resolve_path(source_input, project_root)
    if candidate.suffix.lower() != ".pdf":
        raise ValueError("Input must be an arXiv URL/id or a local PDF path.")
    if not candidate.exists():
        raise FileNotFoundError(f"PDF not found: {candidate}")

    extracted = extract_pdf_text(candidate, max_pages=2)
    title = infer_title_from_pdf_path(candidate)
    return PaperMeta(
        title=title,
        authors=[],
        year=None,
        source=str(candidate),
        abstract=extracted[:2000] if extracted else "",
        pdf_url=None,
    )


def list_notes(project_root: Path) -> list[Path]:
    ensure_layout(project_root)
    notes_dir = project_root / "notes"
    return sorted(
        [p for p in notes_dir.glob("*.md") if p.name != "INDEX.md"],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )


def rebuild_index(project_root: Path) -> Path:
    ensure_layout(project_root)
    rows: list[tuple[str, str]] = []
    for n in list_notes(project_root):
        content = n.read_text(encoding="utf-8")
        title = _extract_field(content, "# ") or n.stem
        year = _extract_bullet_value(content, "Year") or "Unknown"
        source = _extract_bullet_value(content, "Source") or "Unknown"
        tags = _extract_bullet_value(content, "Tags") or ""
        added_at = _extract_bullet_value(content, "Added-at") or ""
        row = f"| {added_at} | [{title}]({n.name}) | {year} | {source} | {tags} |\n"
        rows.append((added_at, row))

    rows.sort(key=lambda x: x[0], reverse=True)
    lines = [_index_header()] + [r for _, r in rows]
    index_path = project_root / "notes" / "INDEX.md"
    index_path.write_text("".join(lines), encoding="utf-8")
    return index_path


def search_notes(project_root: Path, keyword: str) -> list[Path]:
    k = keyword.strip().lower()
    if not k:
        return []
    matches: list[Path] = []
    for note in list_notes(project_root):
        text = note.read_text(encoding="utf-8").lower()
        if k in text:
            matches.append(note)
    return matches


def _extract_field(content: str, prefix: str) -> str | None:
    for line in content.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


def _extract_bullet_value(content: str, field: str) -> str | None:
    token = f"- **{field}:**"
    for line in content.splitlines():
        if line.startswith(token):
            return line[len(token) :].strip()
    return None
