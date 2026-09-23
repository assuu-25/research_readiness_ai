"""
shap_explainer.py
-------------------
Computes SHAP values for a single prediction so we can tell the user WHY
their score came out the way it did, not just what the score is.
"""

from __future__ import annotations
import shap
import pandas as pd
from typing import List, Dict, Any

from app.feature_fusion import FEATURE_NAMES
from app.model import get_model

_explainer = None


def get_explainer():
    global _explainer
    if _explainer is None:
        model = get_model()
        _explainer = shap.TreeExplainer(model)
    return _explainer


def explain(feature_vector: List[float], top_k: int = 8) -> Dict[str, Any]:
    explainer = get_explainer()
    X = pd.DataFrame([feature_vector], columns=FEATURE_NAMES)
    shap_values = explainer(X)

    contributions = list(zip(FEATURE_NAMES, feature_vector, shap_values.values[0]))
    # Sort by absolute impact on the score, most influential first
    contributions.sort(key=lambda t: abs(t[2]), reverse=True)

    top_positive = [c for c in contributions if c[2] > 0][:top_k]
    top_negative = [c for c in contributions if c[2] < 0][:top_k]

    def serialize(c):
        return {
            "feature": c[0],
            "value": round(float(c[1]), 2),
            "shap_impact": round(float(c[2]), 3),
        }

    return {
        "base_value": round(float(shap_values.base_values[0]), 2),
        "top_positive_contributors": [serialize(c) for c in top_positive],
        "top_negative_contributors": [serialize(c) for c in top_negative],
    }
