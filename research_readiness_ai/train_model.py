"""
train_model.py
----------------
Trains the XGBoost "Research Readiness" regressor.

"""

from __future__ import annotations
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

from app.feature_fusion import FEATURE_NAMES

RNG = np.random.default_rng(42)

# Reviewer-informed importance weights (sum roughly balanced across dimensions,
# with methodology + structure weighted heaviest, matching common reviewer rubrics).
WEIGHTS = {
    "ds_completeness": 0.9, "ds_uniqueness": 0.6, "ds_balance": 0.7, "ds_validity": 0.8,
    "ds_consistency": 0.5, "ds_size_adequacy": 1.0, "ds_feature_richness": 0.6,
    "ds_outlier_control": 0.5,
    "pp_section_completeness": 1.3, "pp_citation_density": 0.9, "pp_novelty_signaling": 1.4,
    "pp_methodology_presence": 1.2, "pp_experiment_presence": 1.3, "pp_writing_quality": 0.8,
    "pp_visual_support": 0.7, "pp_abstract_quality": 0.9,
    "lit_reference_count_score": 0.6, "lit_recency_score": 0.7, "lit_coverage_breadth": 0.5,
    "lit_review_completeness": 0.8,
    "mv_baseline_comparison": 1.4, "mv_metric_selection": 1.1, "mv_statistical_rigor": 1.3,
    "mv_reproducibility": 1.0,
}


def generate_synthetic_dataset(n_samples: int = 12000) -> pd.DataFrame:
    data = {}
    for name in FEATURE_NAMES:
        # Beta distribution skewed to produce realistic 0-100 spreads (not uniform noise)
        alpha, beta = RNG.uniform(1.5, 3.5), RNG.uniform(1.5, 3.5)
        data[name] = RNG.beta(alpha, beta, n_samples) * 100

    df = pd.DataFrame(data)

    weight_vec = np.array([WEIGHTS[n] for n in FEATURE_NAMES])
    weighted_sum = df[FEATURE_NAMES].values @ weight_vec
    max_possible = 100 * weight_vec.sum()
    base_score = (weighted_sum / max_possible) * 100

    noise = RNG.normal(0, 4, n_samples)
    label = np.clip(base_score + noise, 0, 100)
    df["readiness_score"] = label
    return df


def train():
    print("Generating synthetic training data (replace with real labeled data when available)...")
    df = generate_synthetic_dataset()

    X = df[FEATURE_NAMES]
    y = df["readiness_score"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    model = xgb.XGBRegressor(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_lambda=1.0,
        random_state=42,
        objective="reg:squarederror",
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    print(f"Validation MAE: {mae:.2f} points (0-100 scale)")
    print(f"Validation R^2: {r2:.3f}")

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/rrs_xgboost.joblib")
    print("Saved model to models/rrs_xgboost.joblib")


if __name__ == "__main__":
    train()
