from __future__ import annotations

from pathlib import Path

import markdown
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from .core import list_notes, search_notes, summary_dir


def create_app(notes_dir: Path) -> FastAPI:
    app = FastAPI(title="paper-review-tool")

    @app.get("/", response_class=HTMLResponse)
    def home(q: str = Query(default="")) -> str:
        notes = search_notes(notes_dir, q) if q else list_notes(notes_dir)
        items = "".join([f'<li><a href="/note/{n.name}">{n.name}</a></li>' for n in notes])
        return f"""
        <html><body>
        <h1>paper-review-tool</h1>
        <form><input name='q' value='{q}' placeholder='search'/><button>Search</button></form>
        <ul>{items}</ul>
        </body></html>
        """

    @app.get("/note/{name}", response_class=HTMLResponse)
    def view_note(name: str) -> str:
        note = summary_dir(notes_dir) / name
        if not note.exists() or note.suffix != ".md":
            raise HTTPException(status_code=404, detail="Note not found")
        raw = note.read_text(encoding="utf-8")
        html = markdown.markdown(raw, extensions=["extra", "sane_lists"])
        slug = note.stem
        pdf_path = notes_dir / "pdfs" / f"{slug}.pdf"
        pdf_link = f"<p><a href='/file/pdfs/{slug}.pdf'>PDF</a></p>" if pdf_path.exists() else ""
        return f"<html><body><a href='/'>Back</a>{pdf_link}{html}</body></html>"

    @app.get("/file/{subpath:path}")
    def serve_file(subpath: str):
        target = (notes_dir / subpath).resolve()
        if not target.exists():
            raise HTTPException(status_code=404, detail="File not found")
        try:
            target.relative_to(notes_dir.resolve())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Unsafe path") from exc
        from fastapi.responses import FileResponse

        return FileResponse(target)

    return app
