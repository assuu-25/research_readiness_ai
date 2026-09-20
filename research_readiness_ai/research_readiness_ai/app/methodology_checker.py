"""
Methodology Checker
--------------------
Looks for the language signals reviewers use to judge experimental rigor.

Metrics:
1. baseline_comparison  - does the paper compare against baselines/prior work
2. metric_selection     - are standard, named evaluation metrics used
3. statistical_rigor    - mentions of significance testing, confidence intervals, seeds/runs
4. reproducibility      - mentions of code/data availability, hyperparameters, environment
"""

from __future__ import annotations
from typing import Dict, Any

BASELINE_TERMS = ["baseline", "compared to", "compared with", "prior work",
                   "state-of-the-art", "state of the art", "outperform", "versus"]
METRIC_TERMS = ["accuracy", "precision", "recall", "f1", "auc", "roc", "rmse",
                "mae", "bleu", "rouge", "map", "ndcg", "perplexity"]
STAT_TERMS = ["p-value", "p <", "confidence interval", "standard deviation",
              "significance", "statistically significant", "t-test", "anova",
              "seeds", "averaged over", "5 runs", "10 runs", "multiple runs"]
REPRO_TERMS = ["github.com", "code is available", "publicly available",
               "hyperparameter", "learning rate", "batch size", "epochs",
               "open-source", "open source", "reproducib"]


def _term_score(text_lower: str, terms: list[str], cap: int) -> float:
    hits = sum(text_lower.count(t) for t in terms)
    return round(min(100, (hits / cap) * 100), 2)


def check_methodology(paper_text: str) -> Dict[str, Any]:
    text_lower = paper_text.lower()
    metrics = {
        "baseline_comparison": _term_score(text_lower, BASELINE_TERMS, cap=4),
        "metric_selection": _term_score(text_lower, METRIC_TERMS, cap=3),
        "statistical_rigor": _term_score(text_lower, STAT_TERMS, cap=3),
        "reproducibility": _term_score(text_lower, REPRO_TERMS, cap=4),
    }
    aggregate = round(sum(metrics.values()) / len(metrics), 2)
    return {
        "dimension": "methodology_evaluation",
        "aggregate_score": aggregate,
        "metrics": metrics,
    }
