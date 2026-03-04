from pathlib import Path

import paper_digester.core as core
from paper_digester.arxiv_fetch import PaperMeta


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

    assert "## Key Contributions" in text and "- " in text
    assert "## Method Overview" in text and "- " in text
    assert "## Strengths" in text and "- " in text
    assert "## Weaknesses" in text and "- " in text
    assert "## My Questions" in text and "- " in text

    diagram = notes_dir / "assets" / "sample-paper" / "method.png"
    assert diagram.exists()
