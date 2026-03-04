from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s_-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text or "untitled"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def safe_resolve_path(candidate: str | Path, project_root: Path) -> Path:
    candidate_path = Path(candidate).expanduser()
    if not candidate_path.is_absolute():
        candidate_path = (project_root / candidate_path).resolve()
    else:
        candidate_path = candidate_path.resolve()

    project_root = project_root.resolve()
    projects_root = Path("~/openclaw/projects").expanduser().resolve()

    allowed_roots = [project_root, projects_root]
    for root in allowed_roots:
        try:
            candidate_path.relative_to(root)
            return candidate_path
        except ValueError:
            continue

    raise ValueError(
        f"Unsafe path: {candidate_path}. Only files under {project_root} or {projects_root} are allowed."
    )
