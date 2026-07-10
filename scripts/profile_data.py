"""
Data Profiling and Quality Assessment Script

Computes comprehensive data quality metrics including:
- Null percentages and duplicate counts
- Numerical column statistics (min, max, mean, median, std)
- Categorical column distributions
- Revenue distribution diagnostics and business interpretation
- Data quality issues and recommendations
"""

import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


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


def find_revenue_column(df):
    """
    Return the best available revenue-like column name.

    The workspace uses multiple aliases for the same business concept, so we
    prefer explicit revenue labels and then fall back to common transaction
    amount columns.
    """

    candidate_columns = ["revenue", "amount", "transaction_amount"]
    for column_name in candidate_columns:
        if column_name in df.columns:
            return column_name

    return None


def profile_revenue_distribution(df, output_dir):
    """
    Analyze the revenue-like column for skew, kurtosis, segment separation,
    and business interpretation.
    """

    revenue_column = find_revenue_column(df)
    if revenue_column is None:
        return None

    revenue = pd.to_numeric(df[revenue_column], errors="coerce").dropna()
    if revenue.empty:
        return None

    skewness = float(revenue.skew()) if len(revenue) > 2 else 0.0
    kurtosis = float(revenue.kurtosis()) if len(revenue) > 3 else 0.0

    percentiles = revenue.quantile([0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
    summary = {
        "column": revenue_column,
        "count": int(revenue.shape[0]),
        "mean": round(float(revenue.mean()), 2),
        "median": round(float(revenue.median()), 2),
        "max": round(float(revenue.max()), 2),
        "min": round(float(revenue.min()), 2),
        "skewness": round(skewness, 4),
        "kurtosis": round(kurtosis, 4),
        "percentiles": {
            str(index): round(float(value), 2) for index, value in percentiles.items()
        },
        "interpretation": "",
        "tail_note": "",
        "hidden_segment_note": "",
        "business_action": "",
    }

    def _plot_kde(axis, values, label):
        if len(values) < 2:
            return

        sample = np.asarray(values, dtype=float)
        standard_deviation = np.std(sample, ddof=1)
        if not np.isfinite(standard_deviation) or standard_deviation == 0:
            return

        bandwidth = 1.06 * standard_deviation * (len(sample) ** (-1 / 5))
        if not np.isfinite(bandwidth) or bandwidth <= 0:
            return

        x_values = np.linspace(sample.min(), sample.max(), 200)
        normalized_distance = (x_values[:, None] - sample[None, :]) / bandwidth
        density = np.exp(-0.5 * normalized_distance**2).sum(axis=1)
        density /= len(sample) * bandwidth * np.sqrt(2 * np.pi)
        axis.plot(x_values, density, label=label)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].hist(revenue, bins=50, edgecolor="black")
    axes[0].set_title(f"{revenue_column.title()} Distribution (Histogram)")
    axes[0].set_xlabel(revenue_column.title())

    _plot_kde(axes[1], revenue, revenue_column.title())
    axes[1].set_title(f"{revenue_column.title()} Distribution (KDE)")
    axes[1].set_xlabel(revenue_column.title())

    plt.tight_layout()
    distribution_plot = output_dir / "revenue_distribution.png"
    fig.savefig(distribution_plot)
    plt.close(fig)

    if len(revenue) > 1:
        high_value_cutoff = revenue.quantile(0.75)
        low_value_cutoff = revenue.quantile(0.25)

        high_value = revenue[revenue > high_value_cutoff]
        low_value = revenue[revenue < low_value_cutoff]

        if not high_value.empty and not low_value.empty:
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))

            axes[0].hist(high_value, bins=30, alpha=0.7, label="High-Value")
            axes[0].hist(low_value, bins=30, alpha=0.7, label="Low-Value")
            axes[0].legend()
            axes[0].set_title("Revenue: High vs Low Value Customers")
            axes[0].set_xlabel(revenue_column.title())

            axes[1].boxplot(
                [low_value, high_value], tick_labels=["Low-Value", "High-Value"]
            )
            axes[1].set_title("Revenue Segment Spread")
            axes[1].set_ylabel(revenue_column.title())

            plt.tight_layout()
            segment_plot = output_dir / "revenue_segment_comparison.png"
            fig.savefig(segment_plot)
            plt.close(fig)

    if skewness > 1:
        interpretation = (
            "Highly right-skewed: most customers are small, while a few large accounts "
            "pull the average upward."
        )
        business_action = (
            "Use median and percentile-based KPIs, and segment small versus enterprise "
            "customers into different growth strategies."
        )
    elif skewness < -1:
        interpretation = (
            "Highly left-skewed: a small set of lower-value customers is pulling the "
            "distribution down."
        )
        business_action = (
            "Investigate low-value concentration and protect higher-value segments."
        )
    else:
        interpretation = (
            "Relatively balanced distribution: the mean is more representative."
        )
        business_action = "A single revenue strategy is less risky, but monitor tails for emerging segments."

    if kurtosis > 3:
        tail_note = "Heavy tails suggest outliers or very large enterprise accounts are present."
    elif kurtosis < 0:
        tail_note = (
            "Thin tails suggest fewer extreme values than a normal distribution."
        )
    else:
        tail_note = "Tail weight is broadly close to a normal reference."

    if len(percentiles) >= 6 and (percentiles.loc[0.9] - percentiles.loc[0.75]) > (
        percentiles.loc[0.75] - percentiles.loc[0.5]
    ):
        hidden_segment_note = (
            "The jump between the 75th and 90th percentiles suggests a hidden premium "
            "segment above the core customer base."
        )
    else:
        hidden_segment_note = (
            "Percentile gaps do not strongly indicate a separate premium segment."
        )

    summary["interpretation"] = interpretation
    summary["tail_note"] = tail_note
    summary["hidden_segment_note"] = hidden_segment_note
    summary["business_action"] = business_action
    summary["distribution_plot"] = str(distribution_plot)

    print("========== Revenue Distribution Analysis ==========")
    print(f"Column: {revenue_column}")
    print(f"Mean: {revenue.mean():.2f}")
    print(f"Median: {revenue.median():.2f}")
    print(f"Skewness: {skewness:.2f}")
    print(f"Kurtosis: {kurtosis:.2f}")
    print("Percentiles:")
    print(percentiles)
    print(interpretation)
    print(tail_note)
    print(hidden_segment_note)
    print(business_action)
    print(f"Saved revenue distribution plot to: {distribution_plot}")

    return summary


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


def generate_quality_report(df, input_file_path, output_dir):
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
        "revenue_analysis": profile_revenue_distribution(df, output_dir),
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
            report = generate_quality_report(df, str(file_path), output_path)
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
            if report.get("revenue_analysis"):
                revenue_analysis = report["revenue_analysis"]
                print(
                    "  Revenue skewness: "
                    f"{revenue_analysis['skewness']}, kurtosis: {revenue_analysis['kurtosis']}"
                )
                print(f"  Revenue median: {revenue_analysis['median']}")
                print(
                    f"  Revenue business action: {revenue_analysis['business_action']}"
                )
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
