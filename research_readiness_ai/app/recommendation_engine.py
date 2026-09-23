"""
recommendation_engine.py
--------------------------
Rule-based engine: for every feature that scores below its threshold, emit
a specific, actionable recommendation instead of a generic "improve your
paper" message. This is what makes the tool "actionable over generic"
(see deck's differentiation slide).
"""

from __future__ import annotations
from typing import List, Dict, Any

# threshold, message
RULES: Dict[str, tuple] = {
    "ds_completeness": (70, "Your dataset has significant missing values. Impute or document "
                             "missing-data handling before submission — reviewers flag unexplained gaps."),
    "ds_uniqueness": (80, "Your dataset contains many duplicate rows. De-duplicate and re-verify "
                           "your reported sample size."),
    "ds_balance": (60, "Your target classes are imbalanced. Consider resampling, class weighting, "
                        "or report metrics (F1, AUC) robust to imbalance instead of raw accuracy."),
    "ds_validity": (85, "Some numeric fields contain invalid values (inf/out-of-range). Clean these "
                         "before running experiments — they can silently corrupt results."),
    "ds_size_adequacy": (60, "Your dataset may be too small to support the claimed conclusions. "
                              "Either justify the sample size statistically or collect more data."),
    "ds_feature_richness": (50, "Many columns are near-constant or pure identifiers and add no "
                                  "signal. Drop or engineer them into more informative features."),

    "pp_section_completeness": (70, "Your draft is missing standard IMRaD sections (e.g. Related "
                                      "Work, Discussion). Reviewers expect the full structure even "
                                      "in a short paper."),
    "pp_citation_density": (50, "Your citation density is low for a paper of this length. Ground "
                                  "more claims in prior work, especially in the Introduction and "
                                  "Related Work sections."),
    "pp_novelty_signaling": (40, "The novelty of your contribution isn't clearly signaled. Add an "
                                   "explicit 'our contribution is...' statement in the Introduction."),
    "pp_methodology_presence": (60, "Your methodology description is thin. Add architecture/"
                                      "algorithm details sufficient for another researcher to "
                                      "reproduce your approach."),
    "pp_experiment_presence": (60, "Experimental evidence is sparse. Add quantitative results with "
                                     "named metrics and comparisons, not just qualitative claims."),
    "pp_writing_quality": (60, "Readability metrics suggest the writing is either too dense or too "
                                 "informal for an academic venue. Have a peer review for clarity."),
    "pp_visual_support": (40, "Few figures/tables are referenced. Add at least one architecture "
                                "diagram and one results table — reviewers scan these first."),
    "pp_abstract_quality": (60, "Your abstract is too short/long or missing key elements (problem, "
                                  "method, result). Aim for 150-250 words covering all four."),

    "lit_reference_count_score": (55, "Your reference list is thin for a competitive venue. Aim for "
                                        "20-40+ references covering foundational and recent work."),
    "lit_recency_score": (50, "Most of your citations are dated. Add recent (last 3-5 years) papers "
                                "to show awareness of current state-of-the-art."),
    "lit_coverage_breadth": (50, "Your references cluster around a few authors/groups. Broaden "
                                    "coverage to avoid appearing to ignore competing work."),
    "lit_review_completeness": (55, "Your related-work discussion doesn't engage deeply enough with "
                                      "cited papers. Explicitly contrast your approach against each "
                                      "major cited method."),

    "mv_baseline_comparison": (55, "You don't clearly compare against baselines or prior "
                                     "state-of-the-art. Add at least one strong baseline comparison — "
                                     "this is one of the most common rejection reasons."),
    "mv_metric_selection": (55, "Consider reporting standard, named metrics for your task (e.g. F1, "
                                  "AUC, RMSE) so reviewers can benchmark your results directly."),
    "mv_statistical_rigor": (40, "Results lack statistical grounding (significance tests, multiple "
                                    "runs, confidence intervals). Add these to strengthen your claims."),
    "mv_reproducibility": (45, "Add reproducibility details: hyperparameters, code/data availability, "
                                 "and environment specs. Many top venues now require this."),
}


def generate_recommendations(feature_dict: Dict[str, float], max_items: int = 8) -> List[Dict[str, Any]]:
    """feature_dict: mapping of feature_name -> value (0-100)."""
    issues = []
    for feature, value in feature_dict.items():
        rule = RULES.get(feature)
        if rule is None:
            continue
        threshold, message = rule
        if value < threshold:
            severity = round((threshold - value) / threshold, 2)  # 0-1, higher = more urgent
            issues.append({
                "feature": feature,
                "score": round(value, 1),
                "threshold": threshold,
                "severity": severity,
                "recommendation": message,
            })
    issues.sort(key=lambda x: x["severity"], reverse=True)
    return issues[:max_items]
