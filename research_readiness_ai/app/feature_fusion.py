"""
Feature Fusion
---------------
Flattens the 4 dimension reports (dataset, paper, literature, methodology)
into a single ordered feature vector that the XGBoost model consumes.
Keeping the order fixed here (FEATURE_NAMES) is what lets SHAP explanations
map back to human-readable metric names later.
"""

from __future__ import annotations
from typing import Dict, Any, List

FEATURE_NAMES: List[str] = [
    # dataset_quality (8)
    "ds_completeness", "ds_uniqueness", "ds_balance", "ds_validity",
    "ds_consistency", "ds_size_adequacy", "ds_feature_richness", "ds_outlier_control",
    # paper_structure (8)
    "pp_section_completeness", "pp_citation_density", "pp_novelty_signaling",
    "pp_methodology_presence", "pp_experiment_presence", "pp_writing_quality",
    "pp_visual_support", "pp_abstract_quality",
    # literature_intelligence (4)
    "lit_reference_count_score", "lit_recency_score", "lit_coverage_breadth",
    "lit_review_completeness",
    # methodology_evaluation (4)
    "mv_baseline_comparison", "mv_metric_selection", "mv_statistical_rigor",
    "mv_reproducibility",
]


def fuse_features(dataset_report: Dict[str, Any],
                   paper_report: Dict[str, Any],
                   literature_report: Dict[str, Any],
                   methodology_report: Dict[str, Any]) -> List[float]:
    ds = dataset_report["metrics"]
    pp = paper_report["metrics"]
    lit = literature_report["metrics"]
    mv = methodology_report["metrics"]

    vector = [
        ds["completeness"], ds["uniqueness"], ds["balance"], ds["validity"],
        ds["consistency"], ds["size_adequacy"], ds["feature_richness"], ds["outlier_control"],
        pp["section_completeness"], pp["citation_density"], pp["novelty_signaling"],
        pp["methodology_presence"], pp["experiment_presence"], pp["writing_quality"],
        pp["visual_support"], pp["abstract_quality"],
        lit["reference_count_score"], lit["recency_score"], lit["coverage_breadth"],
        lit["review_completeness"],
        mv["baseline_comparison"], mv["metric_selection"], mv["statistical_rigor"],
        mv["reproducibility"],
    ]
    assert len(vector) == len(FEATURE_NAMES)
    return vector
