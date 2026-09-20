"""
Literature Review Intelligence
--------------------------------
Parses the References/Bibliography section of the extracted paper text and
scores how well the literature review is grounded.

Metrics:
1. reference_count_score - is there a reasonable number of references
2. recency_score         - what fraction of references are from the last ~6 years
3. coverage_breadth      - diversity of first-author surnames (proxy for not
                            over-citing a single group / self-citation heavy list)
4. review_completeness   - does a related-work/background section exist and
                            does it engage with citations (citations found inside it)
"""

from __future__ import annotations
import re
from datetime import datetime
from typing import Dict, Any


YEAR_PATTERN = re.compile(r"(19|20)\d{2}")


def _split_references(text: str) -> list[str]:
    text_lower = text.lower()
    idx = text_lower.rfind("references")
    if idx == -1:
        idx = text_lower.rfind("bibliography")
    if idx == -1:
        return []
    ref_block = text[idx:]
    # Split on patterns like "[1]", "[12]" or leading numbers "1." at line starts
    entries = re.split(r"\n\s*\[\d+\]|\n\s*\d{1,3}\.\s", ref_block)
    entries = [e.strip() for e in entries if len(e.strip()) > 15]
    return entries[:300]  # sanity cap


def _reference_count_score(n_refs: int) -> float:
    if n_refs >= 30:
        return 100.0
    if n_refs >= 20:
        return 85.0
    if n_refs >= 12:
        return 65.0
    if n_refs >= 6:
        return 40.0
    return 15.0


def _recency_score(entries: list[str]) -> float:
    if not entries:
        return 0.0
    current_year = datetime.now().year
    years = []
    for e in entries:
        matches = YEAR_PATTERN.findall(e)
        # findall with groups returns the group; re-search full match instead
        full_matches = YEAR_PATTERN.finditer(e)
        for m in full_matches:
            years.append(int(m.group(0)))
    if not years:
        return 30.0
    recent = sum(1 for y in years if current_year - y <= 6)
    return round(100 * recent / len(years), 2)


def _coverage_breadth(entries: list[str]) -> float:
    if not entries:
        return 0.0
    surnames = []
    for e in entries:
        m = re.match(r"\s*([A-Z][a-zA-Z\-]+)", e)
        if m:
            surnames.append(m.group(1).lower())
    if not surnames:
        return 40.0
    unique_ratio = len(set(surnames)) / len(surnames)
    return round(100 * unique_ratio, 2)


def _review_completeness(text_lower: str, entries: list[str]) -> float:
    has_related_work = bool(re.search(r"related work|literature review|background", text_lower))
    section_score = 60.0 if has_related_work else 20.0
    citation_bonus = min(40.0, len(entries) / 20 * 40)
    return round(section_score + citation_bonus, 2)


def analyze_literature(paper_text: str) -> Dict[str, Any]:
    text_lower = paper_text.lower()
    entries = _split_references(paper_text)

    metrics = {
        "reference_count_score": _reference_count_score(len(entries)),
        "recency_score": _recency_score(entries),
        "coverage_breadth": _coverage_breadth(entries),
        "review_completeness": _review_completeness(text_lower, entries),
    }
    aggregate = round(sum(metrics.values()) / len(metrics), 2)
    return {
        "dimension": "literature_intelligence",
        "aggregate_score": aggregate,
        "metrics": metrics,
        "meta": {"n_references_detected": len(entries)},
    }
