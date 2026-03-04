from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional
from xml.etree import ElementTree as ET

import requests


ARXIV_API = "https://export.arxiv.org/api/query"


@dataclass
class PaperMeta:
    title: str
    authors: list[str]
    year: Optional[str]
    source: str
    abstract: str
    pdf_url: Optional[str] = None


_ARXIV_ID_PATTERNS = [
    re.compile(r"(?:arxiv\.org/abs/)?([0-9]{4}\.[0-9]{4,5}(?:v\d+)?)", re.I),
    re.compile(r"(?:arxiv\.org/abs/)?([a-z\-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?)", re.I),
]


def parse_arxiv_id(value: str) -> Optional[str]:
    v = value.strip()
    for pat in _ARXIV_ID_PATTERNS:
        m = pat.search(v)
        if m:
            return m.group(1)
    return None


def fetch_arxiv_metadata(arxiv_input: str, timeout: int = 20) -> Optional[PaperMeta]:
    arxiv_id = parse_arxiv_id(arxiv_input)
    if not arxiv_id:
        return None

    params = {"search_query": f"id:{arxiv_id}", "start": 0, "max_results": 1}
    resp = requests.get(ARXIV_API, params=params, timeout=timeout)
    resp.raise_for_status()

    root = ET.fromstring(resp.text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entry = root.find("atom:entry", ns)
    if entry is None:
        return None

    title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip().replace("\n", " ")
    abstract = (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip()
    published = entry.findtext("atom:published", default="", namespaces=ns) or ""
    year = published[:4] if len(published) >= 4 else None

    authors = []
    for author in entry.findall("atom:author", ns):
        name = (author.findtext("atom:name", default="", namespaces=ns) or "").strip()
        if name:
            authors.append(name)

    pdf_url = None
    for link in entry.findall("atom:link", ns):
        if link.get("title") == "pdf" or link.get("type") == "application/pdf":
            pdf_url = link.get("href")
            break

    return PaperMeta(
        title=title or arxiv_id,
        authors=authors,
        year=year,
        source=f"arXiv:{arxiv_id}",
        abstract=abstract,
        pdf_url=pdf_url,
    )
