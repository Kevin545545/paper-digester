from __future__ import annotations

import json
import os
import re
from typing import Any

import requests

from .arxiv_fetch import PaperMeta


ReviewSections = dict[str, str]


def generate_review(meta: PaperMeta, body_text: str = "", project_context: str = "") -> ReviewSections:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key:
        try:
            return _generate_with_openai(meta, body_text, api_key, project_context)
        except Exception:
            pass
    return _heuristic_review(meta, body_text, project_context)


def _generate_with_openai(meta: PaperMeta, body_text: str, api_key: str, project_context: str) -> ReviewSections:
    prompt = {
        "task": "Generate a structured academic paper review as JSON.",
        "instructions": [
            "Return strict JSON only.",
            "Keys must be exactly: paper_reference, goal_of_paper, data, algorithm, statistical_results, your_interpretation.",
            "Each value must be a non-empty paragraph.",
            "Do not use bullet points.",
        ],
        "paper": {
            "title": meta.title,
            "authors": meta.authors,
            "year": meta.year,
            "source": meta.source,
            "abstract": meta.abstract,
            "body_text_before_references": body_text,
        },
        "project_context": project_context,
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
                {"role": "system", "content": "You write rigorous coursework-ready paper reviews."},
                {"role": "user", "content": json.dumps(prompt)},
            ],
            "temperature": 0.1,
        },
        timeout=60,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    parsed = _try_parse_json(content)
    return _normalize_review(parsed, meta, body_text, project_context)


def _try_parse_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    return json.loads(cleaned)


def _heuristic_review(meta: PaperMeta, body_text: str, project_context: str) -> ReviewSections:
    text = f"{meta.abstract or ''} {body_text or ''}".lower()

    dataset_markers = ["dataset", "cifar", "imagenet", "mnist", "benchmark", "corpus", "samples"]
    metrics_markers = ["accuracy", "f1", "auc", "precision", "recall", "bleu", "psnr", "iou", "mse"]
    training_markers = ["train", "training", "fine-tune", "optimization", "loss", "epoch"]

    mentions_data = any(k in text for k in dataset_markers)
    mentions_metrics = [m for m in metrics_markers if m in text]
    mentions_training = any(k in text for k in training_markers)

    authors = ", ".join(meta.authors) if meta.authors else "Unknown authors"
    year = meta.year or "n.d."
    citation = f"{authors} ({year}). {meta.title}. {meta.source}."

    goal = (
        f"This paper addresses a concrete research problem centered on {meta.title.lower()}, aiming to improve how the field handles the target task described by the authors. "
        "The problem matters because better performance, efficiency, or robustness in this area can directly improve downstream applications and scientific understanding. "
        "From the abstract and available body text, the authors appear motivated to close a gap in prior methods by proposing and evaluating a more effective approach."
    )

    data = (
        "The paper appears to evaluate its method on curated experimental data, likely including benchmark-style inputs commonly used in the domain. "
        f"Based on the extracted text, {'dataset usage is explicitly discussed' if mentions_data else 'dataset details are only partially described in the available excerpt'}, "
        "while exact sample counts and access conditions (public versus private) should be verified in the full experimental section. "
        "The inputs seem to follow the task modality defined by the paper, and the evaluation setup is framed as empirical rather than purely theoretical."
    )

    algorithm = (
        "The authors propose a model-driven algorithmic pipeline that can be interpreted as a supervised or optimization-based method depending on task context. "
        f"The description suggests {'an explicit training process' if mentions_training else 'a method description with limited visible training details in the extracted text'}, "
        "with likely preprocessing steps to format inputs before model execution. "
        "Overall, the algorithm appears designed to transform raw task inputs into predictive outputs that can be quantitatively compared against baseline systems."
    )

    metric_sentence = (
        f"Reported performance appears to involve metrics such as {', '.join(sorted(set(mentions_metrics)))}."
        if mentions_metrics
        else "Reported performance is presented quantitatively, though metric names are not consistently visible in the extracted subset."
    )
    statistical_results = (
        f"{metric_sentence} "
        "The evaluation narrative indicates that results are compared against prior work or baseline configurations to demonstrate relative gains. "
        "Main findings suggest measurable improvements on at least some benchmarks, but final confidence depends on inspecting variance reporting, ablation depth, and statistical significance details in the complete paper."
    )

    relation = (
        f"In relation to your project context ({project_context}), this paper is relevant because its method and evaluation strategy provide concrete ideas for problem framing, experimental design, and baseline comparison. "
        if project_context
        else "For project relevance, the paper can still inform method selection, evaluation design, and baseline definition in a related domain without assuming any specific project details. "
    )
    interpretation = (
        "The results are reasonably convincing at a high level, especially if the reported improvements are consistent across multiple settings, but confidence should be tempered by how fully robustness and failure cases are documented. "
        "The evaluation seems directionally strong, yet it should be interpreted carefully unless the paper provides clear ablations, fair baselines, and transparent reporting of uncertainty. "
        f"{relation}"
        "Potential limitations include dependence on dataset choice, reproducibility constraints, and possible mismatch between benchmark conditions and real-world deployment needs."
    )

    return {
        "paper_reference": citation,
        "goal_of_paper": goal,
        "data": "".join(data),
        "algorithm": algorithm,
        "statistical_results": statistical_results,
        "your_interpretation": interpretation,
    }


def _normalize_review(raw: dict[str, Any], meta: PaperMeta, body_text: str, project_context: str) -> ReviewSections:
    fallback = _heuristic_review(meta, body_text, project_context)

    def as_para(key: str) -> str:
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        return fallback[key]

    return {
        "paper_reference": as_para("paper_reference"),
        "goal_of_paper": as_para("goal_of_paper"),
        "data": as_para("data"),
        "algorithm": as_para("algorithm"),
        "statistical_results": as_para("statistical_results"),
        "your_interpretation": as_para("your_interpretation"),
    }
