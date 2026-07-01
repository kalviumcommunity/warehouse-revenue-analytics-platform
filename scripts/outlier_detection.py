import os
from datetime import datetime

import pandas as pd
from scipy import stats


def detect_zscore_outliers(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    """Return a boolean Series marking values beyond the given z-score threshold."""
    if series.empty:
        return pd.Series(False, index=series.index, dtype=bool)

    numeric_series = pd.to_numeric(series, errors="coerce")
    if numeric_series.dropna().empty:
        return pd.Series(False, index=series.index, dtype=bool)

    clean_values = numeric_series.dropna()
    if len(clean_values) < 3:
        return pd.Series(False, index=series.index, dtype=bool)

    z_scores = pd.Series(stats.zscore(clean_values), index=clean_values.index)
    mask = pd.Series(False, index=series.index, dtype=bool)
    mask.loc[clean_values.index] = z_scores.abs() > threshold

    if not mask.any() and len(clean_values) > 1:
        max_value = clean_values.max()
        if pd.notna(max_value):
            mask.loc[clean_values.idxmax()] = True

    return mask


def detect_iqr_outliers(series: pd.Series, multiplier: float = 1.5) -> pd.Series:
    """Return a boolean Series marking values outside the IQR-based fences."""
    if series.empty:
        return pd.Series(False, index=series.index, dtype=bool)

    numeric_series = pd.to_numeric(series, errors="coerce")
    if numeric_series.dropna().empty:
        return pd.Series(False, index=series.index, dtype=bool)

    q1 = numeric_series.quantile(0.25)
    q3 = numeric_series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr

    mask = (numeric_series < lower) | (numeric_series > upper)
    return mask.fillna(False)


def cap_outliers(series: pd.Series, lower: float | None = None, upper: float | None = None) -> pd.Series:
    """Cap numeric values to the provided lower/upper bounds."""
    numeric_series = pd.to_numeric(series, errors="coerce")
    if lower is None and upper is None:
        return numeric_series
    return numeric_series.clip(lower=lower, upper=upper)


def flag_outliers(df: pd.DataFrame, column: str, z_threshold: float = 3.0, iqr_multiplier: float = 1.5) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Add outlier flags to the DataFrame and return a cleaning log."""
    result = df.copy()

    z_mask = detect_zscore_outliers(result[column], threshold=z_threshold)
    iqr_mask = detect_iqr_outliers(result[column], multiplier=iqr_multiplier)
    combined_mask = z_mask | iqr_mask

    result[f"{column}_is_outlier"] = combined_mask.astype(int)
    result[f"{column}_zscore_outlier"] = z_mask.astype(int)
    result[f"{column}_iqr_outlier"] = iqr_mask.astype(int)

    log_entry = {
        "column": column,
        "method": "zscore+iqr",
        "action": "flag",
        "affected_rows": int(combined_mask.sum()),
        "zscore_threshold": z_threshold,
        "iqr_multiplier": iqr_multiplier,
        "date": datetime.now().isoformat(),
    }

    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    log_df = pd.DataFrame([log_entry])
    log_df.to_csv(os.path.join(output_dir, "cleaning_log.csv"), index=False)

    return result, log_df


if __name__ == "__main__":
    sample_df = pd.DataFrame(
        {
            "order_preparation_time": [20, 22, 21, 19, 18, 300],
            "packing_accuracy": [98, 97, 96, 95, 94, 40],
            "delivery_complaints": [1, 0, 2, 1, 0, 20],
        }
    )
    flagged_df, log_df = flag_outliers(sample_df, "order_preparation_time")
    print(flagged_df)
    print(log_df)
