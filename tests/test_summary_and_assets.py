from pathlib import Path

import paper_digester.core as core
from paper_digester.arxiv_fetch import PaperMeta
from pypdf import PdfWriter


def test_add_generates_non_empty_sections_and_diagram(tmp_path: Path, monkeypatch):
    project_root = tmp_path / "repo"
    project_root.mkdir()
    notes_dir = tmp_path / "notes"

    def fake_meta(_root: Path, _source: str):
        return (
            PaperMeta(
                title="Sample Paper",
                authors=["A", "B"],
                year="2025",
                source="arXiv:1234.5678",
                abstract="We propose a practical method for testing.",
                pdf_url=None,
            ),
            "first page excerpt",
        )

    monkeypatch.setattr(core, "_build_metadata", fake_meta)
    note_path = core.add_paper(project_root, notes_dir, "1234.5678")
    text = note_path.read_text(encoding="utf-8")

    assert note_path.parent == notes_dir / "summary"
    assert "## Key Contributions" in text and "- " in text
    assert "## Method Overview" in text and "- " in text
    assert "## Strengths" in text and "- " in text
    assert "## Weaknesses" in text and "- " in text
    assert "## My Questions" in text and "- " in text

    diagram = notes_dir / "assets" / note_path.stem / "method.png"
    assert diagram.exists()


def test_migration_moves_old_md_without_overwrite(tmp_path: Path):
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()
    (notes_dir / "legacy.md").write_text("# old", encoding="utf-8")
    (notes_dir / "summary").mkdir()
    (notes_dir / "summary" / "legacy.md").write_text("# existing", encoding="utf-8")

    core.migrate_legacy_markdown(notes_dir)

    assert not (notes_dir / "legacy.md").exists()
    assert (notes_dir / "summary" / "legacy.md").exists()
    assert (notes_dir / "summary" / "legacy-1.md").exists()


def test_add_pdf_creates_pdf_summary_and_index(tmp_path: Path):
    project_root = tmp_path / "repo"
    project_root.mkdir(parents=True)
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()

    src_pdf = project_root / "input.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    with src_pdf.open("wb") as f:
        writer.write(f)

    note_path = core.add_pdf_file(project_root, notes_dir, src_pdf, tags=["local"])

    assert note_path.exists()
    assert note_path.parent == notes_dir / "summary"
    assert (notes_dir / "summary" / "INDEX.md").exists()
    assert (notes_dir / "pdfs" / f"{note_path.stem}.pdf").exists()
    assert (notes_dir / "assets" / note_path.stem / "method.png").exists()
