"""
Data Profiling and Quality Assessment Script

Computes comprehensive data quality metrics including:
- Null percentages and duplicate counts
- Numerical column statistics (min, max, mean, median, std)
- Categorical column distributions
- Data quality issues and recommendations
"""

import pandas as pd
import numpy as np
import json
import os
from pathlib import Path


def profile_nulls_and_duplicates(df):
    """
    Compute null percentage and duplicate counts per column.

    Args:
        df: pandas DataFrame to profile

    Returns:
        Dictionary with null analysis by column
    """
    profile = {"null_counts": {}, "null_percentages": {}, "exact_duplicate_count": 0}

    for col in df.columns:
        null_count = df[col].isna().sum()
        null_pct = (null_count / len(df)) * 100
        profile["null_counts"][col] = int(null_count)
        profile["null_percentages"][col] = round(null_pct, 2)

    profile["exact_duplicate_count"] = int(df.duplicated().sum())
    profile["duplicate_percentage"] = round((df.duplicated().sum() / len(df)) * 100, 2)

    return profile


def profile_numerical_columns(df):
    """
    Summarise numerical columns with statistical measures.

    Args:
        df: pandas DataFrame to profile

    Returns:
        DataFrame with min, max, mean, median, std for numerical columns
    """
    numerical_cols = df.select_dtypes(include=[np.number]).columns

    stats = {}
    for col in numerical_cols:
        stats[col] = {
            "min": round(float(df[col].min()), 2),
            "max": round(float(df[col].max()), 2),
            "mean": round(float(df[col].mean()), 2),
            "median": round(float(df[col].median()), 2),
            "std": round(float(df[col].std()), 2),
            "null_count": int(df[col].isnull().sum()),
        }

    return pd.DataFrame(stats).T


def profile_categorical_columns(df, top_n=5):
    """
    Summarise categorical columns with value distributions.

    Args:
        df: pandas DataFrame to profile
        top_n: Number of top values to show for each column

    Returns:
        Dictionary with unique counts and top values per categorical column
    """
    categorical_cols = df.select_dtypes(include=["object"]).columns

    profile = {}
    for col in categorical_cols:
        profile[col] = {
            "unique_count": int(df[col].nunique()),
            "top_values": df[col].value_counts().head(top_n).to_dict(),
            "null_count": int(df[col].isnull().sum()),
        }

    return profile


def identify_quality_issues(df, null_threshold=30, duplicate_threshold=5):
    """
    Identify data quality problems based on thresholds.

    Args:
        df: pandas DataFrame to profile
        null_threshold: Percentage threshold for high nulls (default: 30%)
        duplicate_threshold: Percentage threshold for duplicates (default: 5%)

    Returns:
        List of issues found with severity and recommendations
    """
    issues = []

    # Check nulls
    null_pcts = (df.isnull().sum() / len(df)) * 100
    for col, pct in null_pcts.items():
        if pct > null_threshold:
            issues.append(
                {
                    "type": "High nulls",
                    "column": col,
                    "severity": "HIGH",
                    "value": f"{pct:.1f}% missing",
                    "recommendation": "Consider imputation or column exclusion",
                }
            )

    # Check duplicates
    dup_count = df.duplicated().sum()
    dup_pct = (dup_count / len(df)) * 100
    if dup_pct > duplicate_threshold:
        issues.append(
            {
                "type": "High duplicates",
                "column": "Full row",
                "severity": "HIGH",
                "value": f"{dup_pct:.1f}% duplicated",
                "recommendation": "Deduplication required before analysis",
            }
        )

    # Check for invalid ranges in numerical columns
    for col in df.select_dtypes(include=[np.number]).columns:
        if col in df.columns:
            # Check for negative values in columns that shouldn't have them
            if (
                "amount" in col.lower()
                or "price" in col.lower()
                or "quantity" in col.lower()
            ):
                if (df[col] < 0).any():
                    neg_count = (df[col] < 0).sum()
                    issues.append(
                        {
                            "type": "Invalid range",
                            "column": col,
                            "severity": "MEDIUM",
                            "value": f"{neg_count} negative values",
                            "recommendation": "Verify business logic - negative values may be invalid",
                        }
                    )

    return issues


def generate_quality_report(df, input_file_path):
    """
    Generate comprehensive data quality report.

    Args:
        df: pandas DataFrame to profile
        input_file_path: Path to the input data file

    Returns:
        Dictionary containing complete quality report
    """
    report = {
        "metadata": {
            "source_file": input_file_path,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "column_names": list(df.columns),
            "data_types": df.dtypes.astype(str).to_dict(),
        },
        "nulls_and_duplicates": profile_nulls_and_duplicates(df),
        "numerical_columns": profile_numerical_columns(df).to_dict(),
        "categorical_columns": profile_categorical_columns(df),
        "quality_issues": identify_quality_issues(df),
    }

    return report


def profile_ingested_data():
    """
    Main function to profile all ingested data files and generate reports.
    """
    base_path = Path(__file__).parent.parent
    data_ingested_path = base_path / "data" / "processed"
    output_path = base_path / "output"

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    # Files to profile
    ingested_files = ["customers_ingested.csv", "transactions_ingested.csv"]

    all_reports = {}

    for file_name in ingested_files:
        file_path = data_ingested_path / file_name

        if file_path.exists():
            print(f"\nProfiling: {file_name}")
            df = pd.read_csv(file_path)
            report = generate_quality_report(df, str(file_path))
            all_reports[file_name] = report

            # Print summary to console
            print(f"  Total rows: {report['metadata']['total_rows']}")
            print(f"  Total columns: {report['metadata']['total_columns']}")
            print(
                f"  Exact duplicates: {report['nulls_and_duplicates']['exact_duplicate_count']}"
            )
            print(
                f"  Duplicate percentage: {report['nulls_and_duplicates']['duplicate_percentage']}%"
            )
            print(f"  Quality issues found: {len(report['quality_issues'])}")
        else:
            print(f"Warning: {file_name} not found at {file_path}")

    # Save comprehensive report
    report_output_path = output_path / "profile_report.json"
    with open(report_output_path, "w") as f:
        json.dump(all_reports, f, indent=2)

    print(f"\n✓ Profile report saved to: {report_output_path}")

    return all_reports


if __name__ == "__main__":
    profile_ingested_data()
