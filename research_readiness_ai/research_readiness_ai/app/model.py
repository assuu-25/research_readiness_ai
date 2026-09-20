"""
model.py
---------
Loads the trained XGBoost model once and exposes a predict() helper that
takes a fused feature vector and returns the Research Readiness Score (RRS).
"""

from __future__ import annotations
import os
import joblib
import numpy as np
import pandas as pd
from typing import List

from app.feature_fusion import FEATURE_NAMES

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "rrs_xgboost.joblib")
_model = None


def get_model():
    global _model
    if _model is None:
        if not os.path.exists(_MODEL_PATH):
            raise FileNotFoundError(
                "Model not found. Run `python train_model.py` first to train and save it."
            )
        _model = joblib.load(_MODEL_PATH)
    return _model


def predict_rrs(feature_vector: List[float]) -> float:
    model = get_model()
    X = pd.DataFrame([feature_vector], columns=FEATURE_NAMES)
    score = model.predict(X)[0]
    return float(np.clip(score, 0, 100))
