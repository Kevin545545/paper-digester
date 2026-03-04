from __future__ import annotations

import json
from pathlib import Path

DEFAULT_NOTES_DIR = Path("~/openclaw/projects/paper-digester/notes").expanduser()
CONFIG_PATH = Path("~/.paper-digester/config.json").expanduser()


def validate_notes_dir(path: str | Path) -> Path:
    p = Path(path).expanduser().resolve()
    allowed_roots = [Path("/mnt").resolve(), Path("~/openclaw").expanduser().resolve()]
    for root in allowed_roots:
        try:
            p.relative_to(root)
            return p
        except ValueError:
            continue
    raise ValueError(f"Invalid notes directory: {p}. Allowed roots are /mnt and ~/openclaw")


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {"notes_dir": str(DEFAULT_NOTES_DIR)}
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    notes_dir = data.get("notes_dir", str(DEFAULT_NOTES_DIR))
    validated = validate_notes_dir(notes_dir)
    return {"notes_dir": str(validated)}


def save_config(notes_dir: str | Path) -> Path:
    validated = validate_notes_dir(notes_dir)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps({"notes_dir": str(validated)}, indent=2) + "\n", encoding="utf-8"
    )
    return CONFIG_PATH


def resolve_notes_dir(override: str | None = None) -> Path:
    if override:
        return validate_notes_dir(override)
    cfg = load_config()
    return validate_notes_dir(cfg["notes_dir"])
