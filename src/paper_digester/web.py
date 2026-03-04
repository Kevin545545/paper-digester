from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
import markdown

from .core import list_notes, search_notes


def create_app(notes_dir: Path) -> FastAPI:
    app = FastAPI(title="paper-digester")

    @app.get("/", response_class=HTMLResponse)
    def home(q: str = Query(default="")) -> str:
        notes = search_notes(notes_dir, q) if q else list_notes(notes_dir)
        items = "".join([f'<li><a href="/note/{n.name}">{n.name}</a></li>' for n in notes])
        return f"""
        <html><body>
        <h1>paper-digester</h1>
        <form><input name='q' value='{q}' placeholder='search'/><button>Search</button></form>
        <ul>{items}</ul>
        </body></html>
        """

    @app.get("/note/{name}", response_class=HTMLResponse)
    def view_note(name: str) -> str:
        note = notes_dir / name
        if not note.exists() or note.suffix != ".md":
            raise HTTPException(status_code=404, detail="Note not found")
        raw = note.read_text(encoding="utf-8")
        html = markdown.markdown(raw)
        slug = note.stem
        pdf_path = notes_dir / "pdfs" / f"{slug}.pdf"
        diagram_path = notes_dir / "assets" / slug / "method.png"
        pdf_link = f"<p><a href='/file/pdfs/{slug}.pdf'>PDF</a></p>" if pdf_path.exists() else ""
        diagram = f"<img src='/file/assets/{slug}/method.png' width='700'/>" if diagram_path.exists() else ""
        return f"<html><body><a href='/'>Back</a>{pdf_link}{diagram}{html}</body></html>"

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
