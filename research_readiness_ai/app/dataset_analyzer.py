"""
Dataset Quality Analyzer
------------------------
Computes 8 quality dimensions for a tabular dataset (CSV) attached to a
research paper. Each metric is scaled to 0-100 so it can be fused later.

Metrics implemented:
1. completeness   - % of non-missing cells
2. uniqueness     - % of rows that are not exact duplicates
3. balance        - class balance of the (guessed) target column
4. validity       - % of numeric columns free of impossible values (e.g. inf, out-of-range)
5. consistency    - % of columns with a single consistent dtype after coercion
6. size_adequacy  - is the dataset large enough to support the claimed analysis
7. feature_richness - ratio of usable (non-constant, non-id) columns to total columns
8. outlier_control  - % of numeric cells within 3 standard deviations (proxy for cleaning)
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, Any


def _completeness(df: pd.DataFrame) -> float:
    total = df.size
    if total == 0:
        return 0.0
    missing = df.isna().sum().sum()
    return round(100 * (1 - missing / total), 2)


def _uniqueness(df: pd.DataFrame) -> float:
    if len(df) == 0:
        return 0.0
    dup_ratio = df.duplicated().sum() / len(df)
    return round(100 * (1 - dup_ratio), 2)


def _guess_target_column(df: pd.DataFrame) -> str | None:
    """Heuristic: prefer a low-cardinality categorical/int column near the end,
    named like a typical label column, otherwise fall back to the last
    categorical column with <= 20 unique values."""
    candidates = [c for c in df.columns if c.lower() in
                  ("label", "target", "class", "y", "outcome")]
    if candidates:
        return candidates[0]
    for col in reversed(df.columns):
        nunique = df[col].nunique(dropna=True)
        if 2 <= nunique <= 20 and (df[col].dtype == object or
                                     pd.api.types.is_integer_dtype(df[col])):
            return col
    return None


def _balance(df: pd.DataFrame) -> float:
    target = _guess_target_column(df)
    if target is None:
        return 70.0  # neutral score when no obvious target exists (e.g. unsupervised data)
    counts = df[target].value_counts(normalize=True)
    if len(counts) < 2:
        return 40.0
    # Balance score: 100 when perfectly uniform, drops as the top class dominates.
    ideal = 1.0 / len(counts)
    imbalance = (counts.max() - ideal) / (1 - ideal) if len(counts) > 1 else 0
    return round(100 * (1 - imbalance), 2)


def _validity(df: pd.DataFrame) -> float:
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0:
        return 80.0
    bad = 0
    total = 0
    for col in numeric_cols:
        series = df[col]
        total += len(series)
        bad += series.isin([np.inf, -np.inf]).sum()
    if total == 0:
        return 80.0
    return round(100 * (1 - bad / total), 2)


def _consistency(df: pd.DataFrame) -> float:
    if len(df.columns) == 0:
        return 0.0
    consistent = 0
    for col in df.columns:
        series = df[col].dropna()
        if len(series) == 0:
            consistent += 1
            continue
        coerced_numeric = pd.to_numeric(series, errors="coerce")
        numeric_ratio = coerced_numeric.notna().mean()
        # a column is "consistent" if it's almost entirely numeric or almost entirely not
        if numeric_ratio > 0.95 or numeric_ratio < 0.05:
            consistent += 1
    return round(100 * consistent / len(df.columns), 2)


def _size_adequacy(df: pd.DataFrame) -> float:
    n = len(df)
    # Heuristic thresholds inspired by common ML rule-of-thumb minimums.
    if n >= 5000:
        return 100.0
    if n >= 1000:
        return 85.0
    if n >= 300:
        return 65.0
    if n >= 50:
        return 40.0
    return 15.0


def _feature_richness(df: pd.DataFrame) -> float:
    if len(df.columns) == 0:
        return 0.0
    usable = 0
    for col in df.columns:
        nunique = df[col].nunique(dropna=True)
        is_id_like = nunique == len(df) and len(df) > 1
        is_constant = nunique <= 1
        if not is_id_like and not is_constant:
            usable += 1
    return round(100 * usable / len(df.columns), 2)


def _outlier_control(df: pd.DataFrame) -> float:
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0:
        return 85.0
    total, within = 0, 0
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) < 5 or series.std() == 0:
            within += len(series)
            total += len(series)
            continue
        z = (series - series.mean()) / series.std()
        within += (z.abs() <= 3).sum()
        total += len(series)
    if total == 0:
        return 85.0
    return round(100 * within / total, 2)


def analyze_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """Run all 8 dataset-quality metrics and return a breakdown + aggregate score."""
    metrics = {
        "completeness": _completeness(df),
        "uniqueness": _uniqueness(df),
        "balance": _balance(df),
        "validity": _validity(df),
        "consistency": _consistency(df),
        "size_adequacy": _size_adequacy(df),
        "feature_richness": _feature_richness(df),
        "outlier_control": _outlier_control(df),
    }
    aggregate = round(sum(metrics.values()) / len(metrics), 2)
    return {
        "dimension": "dataset_quality",
        "aggregate_score": aggregate,
        "metrics": metrics,
        "meta": {
            "n_rows": int(len(df)),
            "n_cols": int(len(df.columns)),
            "guessed_target_column": _guess_target_column(df),
        },
    }
