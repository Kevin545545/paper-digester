from pathlib import Path

import paper_digester.config as cfg


def test_config_loading(tmp_path: Path, monkeypatch):
    config_path = tmp_path / "config.json"
    monkeypatch.setattr(cfg, "CONFIG_PATH", config_path)

    cfg.save_config("/mnt/f/paper-notes")
    loaded = cfg.load_config()
    assert loaded["notes_dir"] == str(Path("/mnt/f/paper-notes").resolve())


def test_windows_path_handling():
    assert str(cfg.validate_notes_dir("/mnt/c/Users/test/Documents/papers")).startswith("/mnt/c")
    assert str(cfg.validate_notes_dir("/mnt/d/research-notes")).startswith("/mnt/d")
