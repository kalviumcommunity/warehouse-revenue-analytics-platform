"""
Feature engineering for warehouse operational metrics.

This module adds derived business features that help operations teams
identify warehouse workflows with the highest downstream failure risk.

Features created:
- preparation_rate_per_hour: inverse of preparation time
- packing_accuracy_tier: low / medium / high quality buckets
- delivery_complaint_quartile: complaint tier based on quantiles
- workflow_failure_score: composite score from speed, accuracy, complaints
- warehouse_health_score: normalized health score for benchmarking
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _safe_numeric(series: pd.Series) -> pd.Series:
    """Convert values to numeric, coercing invalid entries to NaN."""
    return pd.to_numeric(series, errors="coerce")


def compute_preparation_rate(df: pd.DataFrame) -> pd.DataFrame:
    """Compute orders-per-hour from preparation time."""
    result = df.copy()
    prep_time = _safe_numeric(result["preparation_time_min"])
    prep_rate = 60 / prep_time
    prep_rate = prep_rate.replace([np.inf, -np.inf], np.nan)
    result["preparation_rate_per_hour"] = prep_rate
    return result


def compute_packing_accuracy_tier(df: pd.DataFrame) -> pd.DataFrame:
    """Bin packing accuracy into business tiers."""
    result = df.copy()
    accuracy = _safe_numeric(result["packing_accuracy_pct"])
    result["packing_accuracy_tier"] = pd.cut(
        accuracy,
        bins=[-float("inf"), 90, 95, float("inf")],
        labels=["low", "medium", "high"],
        include_lowest=True,
    )
    return result


def compute_delivery_complaint_quartile(df: pd.DataFrame) -> pd.DataFrame:
    """Assign complaint tiers using quantiles."""
    result = df.copy()
    complaints = _safe_numeric(result["delivery_complaints"]).fillna(0)
    unique_values = complaints.nunique(dropna=True)

    if unique_values <= 1:
        result["delivery_complaint_quartile"] = pd.Categorical(
            ["Q1"] * len(result), categories=["Q1"], ordered=True
        )
        return result

    quantile_count = min(4, unique_values)
    discontinuous_ranks = complaints.rank(method="first", ascending=True)
    qcut_result = pd.qcut(
        discontinuous_ranks,
        q=quantile_count,
        duplicates="drop",
    )
    labels = [f"Q{i}" for i in range(1, len(qcut_result.cat.categories) + 1)]
    result["delivery_complaint_quartile"] = qcut_result.cat.rename_categories(labels)
    return result


def compute_workflow_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Create composite operational scores from derived inputs."""
    result = df.copy()

    result = compute_preparation_rate(result)

    accuracy_score = pd.cut(
        _safe_numeric(result["packing_accuracy_pct"]),
        bins=[-float("inf"), 90, 95, float("inf")],
        labels=[1, 2, 3],
        include_lowest=True,
    ).astype("Int64")

    speed_score = pd.cut(
        _safe_numeric(result["preparation_rate_per_hour"]),
        bins=[-float("inf"), 2.0, 3.0, float("inf")],
        labels=[1, 2, 3],
        include_lowest=True,
    ).astype("Int64")

    complaints = _safe_numeric(result["delivery_complaints"]).fillna(0)
    unique_values = complaints.nunique(dropna=True)

    if unique_values <= 1:
        complaint_score = pd.Series(
            [4] * len(result), index=result.index, dtype="Int64"
        )
    else:
        quantile_count = min(4, unique_values)
        complaint_rank = complaints.rank(method="first", ascending=True)
        qcut_result = pd.qcut(
            complaint_rank,
            q=quantile_count,
            duplicates="drop",
        )
        inverted_labels = list(range(len(qcut_result.cat.categories), 0, -1))
        complaint_score = qcut_result.cat.rename_categories(inverted_labels).astype("Int64")

    result["packing_accuracy_score"] = accuracy_score
    result["preparation_speed_score"] = speed_score
    result["delivery_complaint_score"] = complaint_score
    result["workflow_failure_score"] = (
        result["packing_accuracy_score"].astype("Int64")
        + result["preparation_speed_score"].astype("Int64")
        + result["delivery_complaint_score"].astype("Int64")
    )
    result["warehouse_health_score"] = (
        result["workflow_failure_score"].astype("float") / 10 * 100
    ).round(1)

    return result


def engineer_operational_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all operational feature engineering steps to the dataset."""
    result = df.copy()
    result = compute_preparation_rate(result)
    result = compute_packing_accuracy_tier(result)
    result = compute_delivery_complaint_quartile(result)
    result = compute_workflow_scores(result)
    return result


def validate_engineered_features(df: pd.DataFrame) -> dict[str, object]:
    """Return a small validation summary for engineered business features."""
    required_columns = [
        "preparation_rate_per_hour",
        "packing_accuracy_tier",
        "delivery_complaint_quartile",
        "workflow_failure_score",
        "warehouse_health_score",
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing engineered columns: {missing_columns}")

    validation = {
        "packing_accuracy_tier_distribution": df["packing_accuracy_tier"].value_counts(dropna=False).to_dict(),
        "complaint_quartile_distribution": df["delivery_complaint_quartile"].value_counts(dropna=False).to_dict(),
        "workflow_failure_score_range": (
            int(df["workflow_failure_score"].min()),
            int(df["workflow_failure_score"].max()),
        ),
        "warehouse_health_score_range": (
            float(df["warehouse_health_score"].min()),
            float(df["warehouse_health_score"].max()),
        ),
        "missing_values": df[required_columns].isna().sum().to_dict(),
    }
    return validation


def print_feature_validation(df: pd.DataFrame) -> None:
    """Print validation metrics for the engineered operational features."""
    report = validate_engineered_features(df)
    print("Engagement tier distribution:")
    print(report["packing_accuracy_tier_distribution"])
    print("Complaint quartile distribution:")
    print(report["complaint_quartile_distribution"])
    print(
        f"Workflow failure score range: {report['workflow_failure_score_range'][0]}-{report['workflow_failure_score_range'][1]}"
    )
    print(
        f"Warehouse health score range: {report['warehouse_health_score_range'][0]}-{report['warehouse_health_score_range'][1]}"
    )
    print("Missing values:")
    print(report["missing_values"])
