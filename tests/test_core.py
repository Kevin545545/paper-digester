from pathlib import Path

from paper_digester.core import NoteRecord, build_note_template, rebuild_index, search_notes, summary_dir
from paper_digester.utils import safe_resolve_path, slugify


def test_slugify_behavior():
    assert slugify("Attention Is All You Need!") == "attention-is-all-you-need"
    assert slugify("  hello___world  ") == "hello-world"


def test_note_template_contains_required_sections():
    note = NoteRecord(
        title="Test Paper",
        authors="A, B",
        year="2026",
        source="arXiv:1234.5678",
        abstract="A summary",
        tags="t1, t2",
        added_at="2026-03-04T00:00:00+00:00",
        slug="test-paper",
        paper_reference="A, B (2026). Test Paper. arXiv:1234.5678.",
        goal_of_paper="Goal paragraph.",
        data="Data paragraph.",
        algorithm="Algorithm paragraph.",
        statistical_results="Results paragraph.",
        your_interpretation="Interpretation paragraph.",
    )
    text = build_note_template(note)
    required = [
        "# Paper Review",
        "## Paper Reference",
        "## Goal of the Paper",
        "## Data",
        "## Algorithm",
        "## Statistical Results",
        "## Your Interpretation",
        "- **Added-at:**",
    ]
    for section in required:
        assert section in text


def test_index_generation_sorted_newest_first(tmp_path: Path):
    sdir = summary_dir(tmp_path)
    sdir.mkdir(parents=True)

    older = sdir / "older.md"
    newer = sdir / "newer.md"

    older.write_text(
        "# Paper Review\n\n## Metadata\n- **Title:** Older\n- **Year:** 2022\n- **Source:** s\n- **Tags:** x\n- **Added-at:** 2024-01-01T00:00:00+00:00\n",
        encoding="utf-8",
    )
    newer.write_text(
        "# Paper Review\n\n## Metadata\n- **Title:** Newer\n- **Year:** 2025\n- **Source:** s\n- **Tags:** y\n- **Added-at:** 2025-01-01T00:00:00+00:00\n",
        encoding="utf-8",
    )

    index = rebuild_index(tmp_path)
    body = index.read_text(encoding="utf-8")
    assert body.find("[Newer](newer.md)") < body.find("[Older](older.md)")


def test_search_keyword_matching(tmp_path: Path):
    sdir = summary_dir(tmp_path)
    sdir.mkdir(parents=True)
    (sdir / "a.md").write_text("# A\nTransformer model", encoding="utf-8")
    (sdir / "b.md").write_text("# B\nConvolution network", encoding="utf-8")

    matches = search_notes(tmp_path, "transformer")
    assert len(matches) == 1
    assert matches[0].name == "a.md"


def test_safe_path_enforcement(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir(parents=True)
    good = project / "inside.pdf"
    good.write_text("x", encoding="utf-8")

    resolved = safe_resolve_path(good, project)
    assert resolved == good.resolve()

    bad = Path("/etc/passwd")
    try:
        safe_resolve_path(bad, project)
        assert False, "Expected ValueError for unsafe path"
    except ValueError:
        assert True
