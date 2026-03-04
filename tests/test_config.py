from pathlib import Path

import paper_digester.config as cfg
import paper_digester.core as core
from paper_digester.arxiv_fetch import PaperMeta


def test_config_loading(tmp_path: Path, monkeypatch):
    config_path = tmp_path / "config.json"
    monkeypatch.setattr(cfg, "CONFIG_PATH", config_path)

    cfg.save_config("/mnt/f/paper-notes")
    loaded = cfg.load_config()
    assert loaded["notes_dir"] == str(Path("/mnt/f/paper-notes").resolve())


def test_windows_path_handling():
    assert str(cfg.validate_notes_dir("/mnt/c/Users/test/Documents/papers")).startswith("/mnt/c")
    assert str(cfg.validate_notes_dir("/mnt/d/research-notes")).startswith("/mnt/d")


def test_custom_notes_directory(tmp_path: Path, monkeypatch):
    project_root = tmp_path / "repo"
    project_root.mkdir()

    notes_dir = tmp_path / "my-notes"
    notes_dir.mkdir()

    def fake_meta(_root: Path, _source: str) -> PaperMeta:
        return PaperMeta(
            title="Test Paper",
            authors=["A"],
            year="2026",
            source="arXiv:test",
            abstract="abstract",
            pdf_url=None,
        )

    monkeypatch.setattr(core, "_build_metadata", fake_meta)
    note_path = core.add_paper(project_root, notes_dir, "anything")
    assert note_path.parent == notes_dir
    assert (notes_dir / "INDEX.md").exists()
