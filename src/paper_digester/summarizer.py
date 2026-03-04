from __future__ import annotations

import json
import os
from typing import Any

import requests

from .arxiv_fetch import PaperMeta


def generate_sections(meta: PaperMeta, pdf_text: str = "") -> dict[str, list[str]]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key:
        try:
            return _generate_with_openai(meta, pdf_text, api_key)
        except Exception:
            pass
    return _heuristic_sections(meta, pdf_text)


def _generate_with_openai(meta: PaperMeta, pdf_text: str, api_key: str) -> dict[str, list[str]]:
    prompt = {
        "title": meta.title,
        "authors": meta.authors,
        "year": meta.year,
        "source": meta.source,
        "abstract": meta.abstract,
        "pdf_excerpt": pdf_text[:2000],
        "task": "Return JSON with keys key_contributions, method_overview, strengths, weaknesses, my_questions. Each value must be a non-empty list of concise bullet strings.",
    }
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You produce structured paper-reading notes."},
                {"role": "user", "content": json.dumps(prompt)},
            ],
            "temperature": 0.2,
        },
        timeout=30,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    parsed = _try_parse_json(content)
    return _normalize_sections(parsed, meta)


def _try_parse_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.replace("json", "", 1).strip()
    return json.loads(text)


def _heuristic_sections(meta: PaperMeta, pdf_text: str) -> dict[str, list[str]]:
    abstract = (meta.abstract or "").strip()
    excerpt = (pdf_text or "").strip()
    key_sentence = abstract.split(".")[0].strip() if abstract else "This paper introduces a method in its domain."
    method_hint = "Model details are likely described in the methodology and experiments sections."
    if "we propose" in abstract.lower():
        method_hint = "The authors propose a new approach and validate it empirically."

    strengths = [
        "Clear problem framing and motivation.",
        "Provides an implementable method description.",
    ]
    weaknesses = [
        "May rely on specific assumptions or datasets.",
        "Generalization to other settings should be validated.",
    ]
    if excerpt:
        strengths[0] = "Includes concrete technical details in the paper text."

    return {
        "key_contributions": [key_sentence or "Introduces a meaningful contribution."],
        "method_overview": [method_hint],
        "strengths": strengths,
        "weaknesses": weaknesses,
        "my_questions": [
            "What are the most critical ablations to reproduce?",
            "How would this method perform on my target dataset?",
        ],
    }


def _normalize_sections(raw: dict[str, Any], meta: PaperMeta) -> dict[str, list[str]]:
    def as_list(value: Any, fallback: str) -> list[str]:
        if isinstance(value, list):
            cleaned = [str(x).strip() for x in value if str(x).strip()]
            return cleaned or [fallback]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return [fallback]

    return {
        "key_contributions": as_list(raw.get("key_contributions"), f"Summarizes {meta.title} contributions."),
        "method_overview": as_list(raw.get("method_overview"), "Describes the main training/inference pipeline."),
        "strengths": as_list(raw.get("strengths"), "Presents a useful and relevant method."),
        "weaknesses": as_list(raw.get("weaknesses"), "Potential limitations require further evaluation."),
        "my_questions": as_list(raw.get("my_questions"), "What are the best next experiments to run?"),
    }
