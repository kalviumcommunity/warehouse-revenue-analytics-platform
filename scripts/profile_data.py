import json
import os
from pathlib import Path

import numpy as np
import pandas as pd


def profile_nulls_and_duplicates(df):
    """
    Compute null percentages and duplicate counts for each column.

    Returns:
        dict: Null counts, null percentages, exact duplicate count, and duplicate percentage.
    """
    profile = {
        "null_counts": {},
        "null_percentages": {},
        "exact_duplicate_count": 0,
        "duplicate_percentage": 0.0,
    }

    for col in df.columns:
        null_count = int(df[col].isna().sum())
        null_pct = round((null_count / len(df)) * 100, 2) if len(df) else 0.0
        profile["null_counts"][col] = null_count
        profile["null_percentages"][col] = null_pct

    duplicate_count = int(df.duplicated().sum())
    profile["exact_duplicate_count"] = duplicate_count
    profile["duplicate_percentage"] = round((duplicate_count / len(df)) * 100, 2) if len(df) else 0.0

    return profile


def profile_numerical_columns(df):
    """
    Summarize numerical columns with key statistics.

    Returns:
        pandas.DataFrame: Summary table for each numeric column.
    """
    numerical_cols = df.select_dtypes(include=[np.number]).columns

    stats = {}
    for col in numerical_cols:
        stats[col] = {
            "min": round(float(df[col].min()), 2) if not df[col].empty else None,
            "max": round(float(df[col].max()), 2) if not df[col].empty else None,
            "mean": round(float(df[col].mean()), 2) if not df[col].empty else None,
            "median": round(float(df[col].median()), 2) if not df[col].empty else None,
            "std": round(float(df[col].std()), 2) if not df[col].empty else None,
            "null_count": int(df[col].isnull().sum()),
        }

    return pd.DataFrame(stats).T


def profile_categorical_columns(df, top_n=5):
    """
    Summarize categorical columns with value distributions.

    Returns:
        dict: Unique counts, top values, and null counts for each categorical column.
    """
    categorical_cols = df.select_dtypes(include=['object', 'string']).columns

    profile = {}
    for col in categorical_cols:
        value_counts = df[col].fillna("<NA>").value_counts().head(top_n)
        profile[col] = {
            "unique_count": int(df[col].nunique()),
            "top_values": value_counts.to_dict(),
            "null_count": int(df[col].isnull().sum()),
        }

    return profile


def identify_quality_issues(df, null_threshold=30, duplicate_threshold=5):
    """
    Identify common data quality issues and recommend remediation.

    Returns:
        list: Issue records with severity and recommendation.
    """
    issues = []

    null_pcts = (df.isnull().sum() / len(df)) * 100
    for col, pct in null_pcts.items():
        if pct >= null_threshold:
            issues.append({
                "type": "High nulls",
                "column": col,
                "severity": "HIGH",
                "value": f"{pct:.1f}% missing",
                "recommendation": "Consider imputation or column exclusion before analysis",
            })

    duplicate_pct = (df.duplicated().sum() / len(df)) * 100 if len(df) else 0.0
    if duplicate_pct >= duplicate_threshold:
        issues.append({
            "type": "High duplicates",
            "column": "Full row",
            "severity": "HIGH",
            "value": f"{duplicate_pct:.1f}% duplicated",
            "recommendation": "Deduplicate records before downstream analysis",
        })

    for col in df.select_dtypes(include=[np.number]).columns:
        series = df[col]
        if col in {"preparation_time_min", "delivery_complaints"}:
            invalid = series[series < 0]
            if not invalid.empty:
                issues.append({
                    "type": "Invalid range",
                    "column": col,
                    "severity": "HIGH",
                    "value": f"{int(invalid.count())} negative value(s)",
                    "recommendation": "Review and correct invalid negative business values",
                })

        if col == "packing_accuracy_pct":
            invalid = series[(series < 0) | (series > 100)]
            if not invalid.empty:
                issues.append({
                    "type": "Invalid range",
                    "column": col,
                    "severity": "HIGH",
                    "value": f"{int(invalid.count())} out-of-range value(s)",
                    "recommendation": "Verify packing accuracy values against the allowed 0-100% scale",
                })

    return issues


def build_report(df):
    """Build a structured profiling report for JSON output."""
    null_profile = profile_nulls_and_duplicates(df)
    numerical_profile = profile_numerical_columns(df)
    categorical_profile = profile_categorical_columns(df)
    quality_issues = identify_quality_issues(df)

    report = {
        "dataset_shape": {
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
        },
        "null_profile": null_profile,
        "numerical_profile": numerical_profile.to_dict(orient="index"),
        "categorical_profile": categorical_profile,
        "quality_issues": quality_issues,
    }

    return report


def save_report(report, output_path):
    """Save the profiling report to disk."""
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)


def main():
    base_dir = Path(__file__).resolve().parents[1]
    input_path = base_dir / "data" / "raw" / "quality_test.csv"
    output_path = base_dir / "output" / "profile_report.json"

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(input_path)
    report = build_report(df)
    save_report(report, output_path)

    print(f"Loaded {len(df)} rows from {input_path}")
    print(f"Saved profiling report to {output_path}")
    print("Quality issues:")
    for issue in report["quality_issues"]:
        print(f" - {issue['type']} | {issue['column']} | {issue['value']}")


if __name__ == "__main__":
    main()
