import os
import sys

import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.outlier_detection import detect_iqr_outliers, detect_zscore_outliers, flag_outliers


def test_zscore_and_iqr_detect_outliers():
    series = pd.Series([10, 11, 12, 10, 11, 100])

    z_mask = detect_zscore_outliers(series)
    iqr_mask = detect_iqr_outliers(series)

    assert bool(z_mask.iloc[-1])
    assert bool(iqr_mask.iloc[-1])
    assert z_mask.sum() >= 1
    assert iqr_mask.sum() >= 1


def test_flag_outliers_creates_binary_columns_and_log():
    df = pd.DataFrame({"revenue": [100, 110, 105, 102, 500]})
    flagged_df, log_df = flag_outliers(df, "revenue")

    assert "revenue_is_outlier" in flagged_df.columns
    assert "revenue_zscore_outlier" in flagged_df.columns
    assert "revenue_iqr_outlier" in flagged_df.columns
    assert log_df.iloc[0]["column"] == "revenue"
    assert log_df.iloc[0]["action"] == "flag"
    assert os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "cleaning_log.csv"))
