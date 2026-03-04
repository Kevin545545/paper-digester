from pathlib import Path

import paper_digester.core as core
from paper_digester.arxiv_fetch import PaperMeta


def test_summaries_written_to_summary_and_index(tmp_path: Path, monkeypatch):
    notes_dir = tmp_path / "notes"

    def fake_meta(_source: str) -> PaperMeta:
        return PaperMeta(
            title="Sample Paper",
            authors=["A", "B"],
            year="2025",
            source="arXiv:1234.5678",
            abstract="We propose a practical method for testing.",
            pdf_url=None,
        )

    monkeypatch.setattr(core, "_build_metadata", fake_meta)
    note_path = core.add_paper(tmp_path, notes_dir, "1234.5678")

    assert note_path.parent == notes_dir / "summary"
    assert (notes_dir / "summary" / "INDEX.md").exists()
    text = note_path.read_text(encoding="utf-8")
    assert "## Key Contributions" in text
    assert "## Method Overview" in text
    assert "## Strengths" in text
    assert "## Weaknesses" in text
    assert "## My Questions" in text


def test_search_functionality(tmp_path: Path):
    sdir = core.summary_dir(tmp_path)
    sdir.mkdir(parents=True)
    (sdir / "a.md").write_text("# A\nTransformer model", encoding="utf-8")
    (sdir / "b.md").write_text("# B\nConvolution network", encoding="utf-8")

    matches = core.search_notes(tmp_path, "transformer")
    assert len(matches) == 1
    assert matches[0].name == "a.md"


def test_pdf_download_stored_in_pdfs(tmp_path: Path, monkeypatch):
    notes_dir = tmp_path / "notes"

    def fake_meta(_source: str) -> PaperMeta:
        return PaperMeta(
            title="Download Paper",
            authors=["A"],
            year="2025",
            source="arXiv:9999.0001",
            abstract="",
            pdf_url="https://example.com/test.pdf",
        )

    class DummyResp:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size=8192):
            del chunk_size
            yield b"%PDF-1.4\n%mock\n"

    monkeypatch.setattr(core, "_build_metadata", fake_meta)
    monkeypatch.setattr(core.requests, "get", lambda *a, **k: DummyResp())

    note_path = core.add_paper(tmp_path, notes_dir, "9999.0001", download_pdf=True)
    slug = note_path.stem
    assert (notes_dir / "pdfs" / f"{slug}.pdf").exists()
