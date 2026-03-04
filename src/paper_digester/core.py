from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

import requests

from .arxiv_fetch import PaperMeta, fetch_arxiv_metadata, parse_arxiv_id
from .pdf_extract import extract_pdf_text
from .summarizer import generate_sections
from .utils import now_iso, slugify


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
    key_contributions: list[str]
    method_overview: list[str]
    strengths: list[str]
    weaknesses: list[str]
    my_questions: list[str]


def summary_dir(notes_dir: Path) -> Path:
    return notes_dir / "summary"


def ensure_layout(notes_dir: Path) -> None:
    notes_dir.mkdir(parents=True, exist_ok=True)
    (notes_dir / "pdfs").mkdir(parents=True, exist_ok=True)
    sdir = summary_dir(notes_dir)
    sdir.mkdir(parents=True, exist_ok=True)
    index = sdir / "INDEX.md"
    if not index.exists():
        index.write_text(_index_header(), encoding="utf-8")


def migrate_legacy_markdown(notes_dir: Path) -> None:
    ensure_layout(notes_dir)
    sdir = summary_dir(notes_dir)
    skip = {"INDEX.md", "README.md", "readme.md", "CHANGELOG.md", "LICENSE.md"}
    for md in notes_dir.glob("*.md"):
        if md.name in skip:
            continue
        target = _unique_path(sdir / md.name)
        shutil.move(str(md), str(target))
    if (notes_dir / "INDEX.md").exists():
        shutil.move(str(notes_dir / "INDEX.md"), str(_unique_path(sdir / "INDEX.md")))
    rebuild_index(notes_dir)


def _index_header() -> str:
    return "# Paper Digester Index\n\n| Added At | Title | Year | Source | Tags |\n|---|---|---:|---|---|\n"


def _bullets(lines: list[str]) -> str:
    cleaned = [x.strip() for x in lines if x.strip()]
    if not cleaned:
        cleaned = ["TBD"]
    return "\n".join([f"- {x}" for x in cleaned])


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
        f"{_bullets(record.key_contributions)}\n\n"
        "## Method Overview\n\n"
        f"{_bullets(record.method_overview)}\n\n"
        "## Strengths\n\n"
        f"{_bullets(record.strengths)}\n\n"
        "## Weaknesses\n\n"
        f"{_bullets(record.weaknesses)}\n\n"
        "## My Questions\n\n"
        f"{_bullets(record.my_questions)}\n"
    )


def add_paper(
    project_root: Path,
    notes_dir: Path,
    source_input: str,
    tags: list[str] | None = None,
    download_pdf: bool = False,
) -> Path:
    del project_root
    tags = tags or []
    ensure_layout(notes_dir)

    meta = _build_metadata(source_input)
    slug = slugify(meta.title)

    pdf_excerpt = ""
    if download_pdf and meta.pdf_url:
        pdf_path = notes_dir / "pdfs" / f"{slug}.pdf"
        _download_pdf_if_needed(meta.pdf_url, pdf_path)
        try:
            pdf_excerpt = extract_pdf_text(pdf_path, max_pages=1)
        except Exception:
            pdf_excerpt = ""

    note_path = _write_summary_note(notes_dir, slug, meta, pdf_excerpt, tags)
    rebuild_index(notes_dir)
    return note_path


def _write_summary_note(notes_dir: Path, slug: str, meta: PaperMeta, pdf_excerpt: str, tags: list[str]) -> Path:
    sections = generate_sections(meta, pdf_excerpt)
    note = NoteRecord(
        title=meta.title,
        authors=", ".join(meta.authors) if meta.authors else "Unknown",
        year=meta.year or "Unknown",
        source=meta.source,
        abstract=meta.abstract.strip() if meta.abstract else pdf_excerpt[:1800],
        keywords="",
        tags=", ".join(tags),
        added_at=now_iso(),
        slug=slug,
        key_contributions=sections["key_contributions"],
        method_overview=sections["method_overview"],
        strengths=sections["strengths"],
        weaknesses=sections["weaknesses"],
        my_questions=sections["my_questions"],
    )
    note_path = _unique_path(summary_dir(notes_dir) / f"{slug}.md")
    note_path.write_text(build_note_template(note), encoding="utf-8")
    return note_path


def _download_pdf_if_needed(url: str, out_path: Path) -> None:
    if out_path.exists():
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, timeout=60, stream=True) as resp:
        resp.raise_for_status()
        with out_path.open("wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


def _build_metadata(source_input: str) -> PaperMeta:
    arxiv_id = parse_arxiv_id(source_input)
    if not arxiv_id:
        raise ValueError("Input must be an arXiv URL or arXiv id.")
    meta = fetch_arxiv_metadata(source_input)
    if not meta:
        raise ValueError(f"Could not fetch metadata for arXiv input: {source_input}")
    return meta


def list_notes(notes_dir: Path) -> list[Path]:
    ensure_layout(notes_dir)
    sdir = summary_dir(notes_dir)
    return sorted(
        [p for p in sdir.glob("*.md") if p.name != "INDEX.md"],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )


def rebuild_index(notes_dir: Path) -> Path:
    ensure_layout(notes_dir)
    rows: list[tuple[str, str]] = []
    for n in list_notes(notes_dir):
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
    index_path = summary_dir(notes_dir) / "INDEX.md"
    index_path.write_text("".join(lines), encoding="utf-8")
    return index_path


def search_notes(notes_dir: Path, keyword: str) -> list[Path]:
    k = keyword.strip().lower()
    if not k:
        return []
    matches: list[Path] = []
    for note in list_notes(notes_dir):
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


def _unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    i = 1
    while True:
        candidate = parent / f"{stem}-{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1
