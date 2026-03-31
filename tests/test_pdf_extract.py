from pathlib import Path

import paper_digester.pdf_extract as pe


class DummyPage:
    def __init__(self, text: str):
        self._text = text

    def extract_text(self):
        return self._text


class DummyReader:
    def __init__(self, _path: str):
        self.pages = [
            DummyPage("Intro section with lots of details. " + ("X" * 2500)),
            DummyPage("Method section continues with more details."),
        ]


def test_extract_pdf_text_not_truncated_to_2000(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(pe, "PdfReader", DummyReader)
    output = pe.extract_pdf_text(tmp_path / "dummy.pdf")
    assert len(output) > 2000


def test_truncate_before_references_heading():
    text = "Intro\nMethods\nREFERENCES\n[1] stuff"
    truncated = pe.truncate_before_back_matter(text)
    assert "REFERENCES" not in truncated
    assert "Methods" in truncated


def test_truncate_before_bibliography_heading():
    text = "Intro\nResults\nBibliography\n[1] stuff"
    truncated = pe.truncate_before_back_matter(text)
    assert "Bibliography" not in truncated
    assert "Results" in truncated
