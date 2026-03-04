from pathlib import Path

from paper_digester.core import NoteRecord, build_note_template, rebuild_index, search_notes
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
        keywords="k1, k2",
        tags="t1, t2",
        added_at="2026-03-04T00:00:00+00:00",
        slug="test-paper",
    )
    text = build_note_template(note)
    required = [
        "## Abstract",
        "## Key Contributions",
        "## Method Overview",
        "## Strengths/Weaknesses",
        "## My Questions",
        "- **Added-at:**",
    ]
    for section in required:
        assert section in text


def test_index_generation_sorted_newest_first(tmp_path: Path):
    notes = tmp_path / "notes"
    notes.mkdir()

    older = notes / "older.md"
    newer = notes / "newer.md"

    older.write_text(
        "# Older\n- **Year:** 2022\n- **Source:** s\n- **Tags:** x\n- **Added-at:** 2024-01-01T00:00:00+00:00\n",
        encoding="utf-8",
    )
    newer.write_text(
        "# Newer\n- **Year:** 2025\n- **Source:** s\n- **Tags:** y\n- **Added-at:** 2025-01-01T00:00:00+00:00\n",
        encoding="utf-8",
    )

    # Force mtime order: newer newer than older
    older.touch()
    newer.touch()

    index = rebuild_index(tmp_path)
    body = index.read_text(encoding="utf-8")
    assert body.find("[Newer](newer.md)") < body.find("[Older](older.md)")


def test_search_keyword_matching(tmp_path: Path):
    notes = tmp_path / "notes"
    notes.mkdir()
    (notes / "a.md").write_text("# A\nTransformer model", encoding="utf-8")
    (notes / "b.md").write_text("# B\nConvolution network", encoding="utf-8")

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
