import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.feature_engineering import (
    add_vectorized_revenue_features,
    benchmark_revenue_vectorization,
    engineer_operational_features,
    validate_engineered_features,
)


def build_sample_operational_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": [1001, 1002, 1003, 1004],
            "warehouse_id": ["W1", "W2", "W1", "W3"],
            "workflow_type": ["Picking", "Packaging", "Sorting", "Packing"],
            "preparation_time_min": [18, 22, 45, 30],
            "packing_accuracy_pct": [98.5, 96.0, 88.0, 100.0],
            "delivery_complaints": [0, 1, 2, 0],
        }
    )


def test_engineer_operational_features_adds_expected_columns():
    df = build_sample_operational_data()
    result = engineer_operational_features(df)

    expected_columns = [
        "preparation_rate_per_hour",
        "packing_accuracy_tier",
        "delivery_complaint_quartile",
        "packing_accuracy_score",
        "preparation_speed_score",
        "delivery_complaint_score",
        "workflow_failure_score",
        "warehouse_health_score",
    ]

    for column in expected_columns:
        assert column in result.columns

    assert result.loc[0, "packing_accuracy_tier"] == "high"
    assert result.loc[2, "packing_accuracy_tier"] == "low"
    assert result["delivery_complaint_quartile"].dtype.name == "category"
    assert result["workflow_failure_score"].min() >= 3
    assert result["warehouse_health_score"].between(0, 100).all()


def test_validate_engineered_features_reports_no_missing_values():
    df = build_sample_operational_data()
    result = engineer_operational_features(df)
    validation = validate_engineered_features(result)

    assert validation["missing_values"] == {
        "preparation_rate_per_hour": 0,
        "packing_accuracy_tier": 0,
        "delivery_complaint_quartile": 0,
        "workflow_failure_score": 0,
        "warehouse_health_score": 0,
    }
    assert validation["workflow_failure_score_range"][0] <= validation["workflow_failure_score_range"][1]


def test_add_vectorized_revenue_features_creates_expected_columns():
    df = pd.DataFrame({"revenue": [100, 200, 300, 400]})
    result = add_vectorized_revenue_features(df)

    assert "revenue_normalized" in result.columns
    assert "revenue_zscore" in result.columns
    assert "revenue_rank" in result.columns

    np.testing.assert_allclose(result["revenue_normalized"].to_numpy(), [0.0, 1 / 3, 2 / 3, 1.0])
    np.testing.assert_allclose(result["revenue_zscore"].to_numpy(), [-1.34164079, -0.4472136, 0.4472136, 1.34164079], atol=1e-6)
    assert result["revenue_rank"].tolist() == [4.0, 3.0, 2.0, 1.0]


def test_benchmark_revenue_vectorization_returns_timing_metrics():
    df = pd.DataFrame({"revenue": [10, 20, 30, 40, 50]})
    metrics = benchmark_revenue_vectorization(df)

    assert set(metrics) == {"loop_time", "numpy_time", "speedup"}
    assert metrics["loop_time"] >= 0
    assert metrics["numpy_time"] >= 0
    assert metrics["speedup"] >= 0
