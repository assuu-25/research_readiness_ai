"""
Paper Structure Analyzer
-------------------------
Extracts text from an uploaded PDF/DOCX draft and scores 8 structural
dimensions used by reviewers at top-tier (e.g. IEEE) venues.

Metrics:
1. section_completeness - presence of standard IMRaD sections
2. citation_density      - in-text citations per 1000 words (too few = weak grounding)
3. novelty_signaling     - presence of novelty/contribution language
4. methodology_presence  - presence of methodology-describing language
5. experiment_presence   - presence of experiment/results/evaluation language
6. writing_quality       - readability + sentence-length sanity (Flesch reading ease)
7. visual_support        - estimated number of figures/tables referenced
8. abstract_quality       - length & keyword coverage of the abstract
"""

from __future__ import annotations
import re
from typing import Dict, Any
import textstat

SECTION_PATTERNS = {
    "abstract": r"\babstract\b",
    "introduction": r"\bintroduction\b",
    "related_work": r"\brelated work\b|\bliterature review\b|\bbackground\b",
    "methodology": r"\bmethodology\b|\bmethods?\b|\bproposed (approach|method|system)\b",
    "experiments": r"\bexperiments?\b|\bevaluation\b|\bresults?\b",
    "discussion": r"\bdiscussion\b|\banalysis\b",
    "conclusion": r"\bconclusion\b|\bfuture work\b",
    "references": r"\breferences\b|\bbibliography\b",
}

NOVELTY_KEYWORDS = [
    "novel", "we propose", "we introduce", "for the first time", "unlike prior",
    "in contrast to previous", "our contribution", "outperforms", "state-of-the-art",
    "state of the art", "unlike existing",
]

METHOD_KEYWORDS = [
    "algorithm", "architecture", "model", "framework", "pipeline", "we design",
    "implementation", "training procedure", "dataset construction", "experimental setup",
]

EXPERIMENT_KEYWORDS = [
    "table", "figure", "accuracy", "precision", "recall", "f1", "baseline",
    "ablation", "benchmark", "p-value", "statistically significant", "evaluation metric",
]


def _extract_text_pdf(path: str) -> str:
    import pdfplumber
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            text_parts.append(t)
    return "\n".join(text_parts)


def _extract_text_docx(path: str) -> str:
    import docx
    d = docx.Document(path)
    return "\n".join(p.text for p in d.paragraphs)


def extract_text(path: str) -> str:
    lower = path.lower()
    if lower.endswith(".pdf"):
        return _extract_text_pdf(path)
    if lower.endswith(".docx"):
        return _extract_text_docx(path)
    if lower.endswith(".txt") or lower.endswith(".md"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    raise ValueError(f"Unsupported paper file type: {path}")


def _section_completeness(text_lower: str) -> float:
    found = sum(1 for pat in SECTION_PATTERNS.values() if re.search(pat, text_lower))
    return round(100 * found / len(SECTION_PATTERNS), 2)


def _citation_density(text: str) -> float:
    # Matches [1], [1,2], (Smith et al., 2020), (Smith, 2020)
    bracket_cites = re.findall(r"\[\d+(?:\s*,\s*\d+)*\]", text)
    paren_cites = re.findall(r"\([A-Z][a-zA-Z\-]+(?:\s+et al\.)?,?\s*\d{4}\)", text)
    n_cites = len(bracket_cites) + len(paren_cites)
    n_words = max(len(text.split()), 1)
    per_1000 = (n_cites / n_words) * 1000
    # Healthy density for a full paper is roughly 8-25 citations per 1000 words.
    score = min(100, (per_1000 / 15) * 100)
    return round(score, 2)


def _keyword_presence_score(text_lower: str, keywords: list[str], cap: int = 5) -> float:
    hits = sum(text_lower.count(k) for k in keywords)
    return round(min(100, (hits / cap) * 100), 2)


def _writing_quality(text: str) -> float:
    if len(text.split()) < 50:
        return 20.0
    try:
        ease = textstat.flesch_reading_ease(text)
    except Exception:
        return 50.0
    # Academic writing typically scores 20-45 on Flesch (denser than general prose).
    # We reward text in that "appropriately technical but not incomprehensible" band.
    if 10 <= ease <= 50:
        return round(90 + min(10, (ease - 10) / 4), 2)
    if ease > 50:
        return round(max(40, 90 - (ease - 50)), 2)  # too simple for an academic paper
    return round(max(20, 90 - (10 - ease) * 3), 2)  # too dense / possibly garbled


def _visual_support(text: str) -> float:
    fig_refs = len(re.findall(r"\bfig(?:ure)?\.?\s*\d+", text, re.IGNORECASE))
    table_refs = len(re.findall(r"\btable\s*\d+", text, re.IGNORECASE))
    total_refs = fig_refs + table_refs
    # 6+ distinct figure/table references is a strong signal for a full paper.
    return round(min(100, (total_refs / 6) * 100), 2)


def _abstract_quality(text: str, text_lower: str) -> float:
    m = re.search(r"abstract(.*?)(?:introduction|keywords|index terms)", text_lower, re.DOTALL)
    if not m:
        return 30.0
    abstract = m.group(1).strip()
    n_words = len(abstract.split())
    length_score = 100 if 120 <= n_words <= 300 else max(20, 100 - abs(n_words - 200) * 0.5)
    keyword_hits = sum(1 for k in ("propose", "result", "method", "show", "evaluat")
                        if k in abstract)
    keyword_score = min(100, keyword_hits * 25)
    return round((length_score + keyword_score) / 2, 2)


def analyze_paper(path: str) -> Dict[str, Any]:
    text = extract_text(path)
    text_lower = text.lower()

    metrics = {
        "section_completeness": _section_completeness(text_lower),
        "citation_density": _citation_density(text),
        "novelty_signaling": _keyword_presence_score(text_lower, NOVELTY_KEYWORDS, cap=4),
        "methodology_presence": _keyword_presence_score(text_lower, METHOD_KEYWORDS, cap=6),
        "experiment_presence": _keyword_presence_score(text_lower, EXPERIMENT_KEYWORDS, cap=8),
        "writing_quality": _writing_quality(text),
        "visual_support": _visual_support(text),
        "abstract_quality": _abstract_quality(text, text_lower),
    }
    aggregate = round(sum(metrics.values()) / len(metrics), 2)
    return {
        "dimension": "paper_structure",
        "aggregate_score": aggregate,
        "metrics": metrics,
        "meta": {
            "word_count": len(text.split()),
            "sections_found": [name for name, pat in SECTION_PATTERNS.items()
                                if re.search(pat, text_lower)],
        },
        "_raw_text": text,  # kept internally for downstream modules; stripped before API response
    }
