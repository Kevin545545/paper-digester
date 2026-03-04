from pathlib import Path

from fastapi.testclient import TestClient
from pypdf import PdfWriter

from paper_digester.web import create_app


def _make_pdf_bytes() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    from io import BytesIO

    buf = BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_web_upload_creates_files(tmp_path: Path):
    notes_dir = tmp_path / "notes"
    app = create_app(notes_dir)
    client = TestClient(app)

    pdf = _make_pdf_bytes()
    resp = client.post(
        "/upload",
        files={"file": ("paper.pdf", pdf, "application/pdf")},
        data={"tags": "web,upload"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    loc = resp.headers["location"]
    assert loc.startswith("/note/")

    note_name = loc.split("/note/")[1]
    slug = Path(note_name).stem
    assert (notes_dir / "summary" / note_name).exists()
    assert (notes_dir / "summary" / "INDEX.md").exists()
    assert (notes_dir / "pdfs" / f"{slug}.pdf").exists()
