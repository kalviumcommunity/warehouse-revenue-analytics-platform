import json
import os
from pathlib import Path

import pandas as pd


def analyze_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Compute null counts and percentages before treatment."""
    missing_analysis = pd.DataFrame(
        {
            "column": df.columns,
            "null_count": df.isnull().sum().values,
            "null_percentage": (df.isnull().sum() / len(df) * 100).round(2).values,
            "data_type": df.dtypes.values,
            "null_meaning": ["" for _ in df.columns],
        }
    )

    print("=" * 70)
    print("BEFORE IMPUTATION - Missing Value Analysis")
    print("=" * 70)
    print(missing_analysis.to_string(index=False))
    print(f"\nTotal rows: {len(df)}")
    print(f"Total cells: {len(df) * len(df.columns)}")
    print(f"Missing cells: {df.isnull().sum().sum()}")
    print("=" * 70)

    return missing_analysis


def drop_rows_with_nulls(df: pd.DataFrame, critical_cols: list[str]) -> tuple[pd.DataFrame, dict]:
    """Drop rows where critical columns are null."""
    rows_before = len(df)
    df_imputed = df.dropna(subset=critical_cols)
    rows_dropped = rows_before - len(df_imputed)

    print(f"  ✓ Dropped {rows_dropped} rows with null in: {critical_cols}")

    details = {
        "strategy": "drop_rows",
        "critical_columns": critical_cols,
        "rows_before": rows_before,
        "rows_after": len(df_imputed),
        "rows_dropped": rows_dropped,
    }
    return df_imputed, details


def impute_mean_median(df: pd.DataFrame, numerical_cols: list[str], strategy: str = "median") -> tuple[pd.DataFrame, dict]:
    """Fill numerical nulls with mean or median."""
    df_imputed = df.copy()
    summary = {"strategy": strategy, "columns": {}}

    for col in numerical_cols:
        if df[col].isnull().sum() > 0:
            fill_value = df[col].median() if strategy == "median" else df[col].mean()
            fill_value = float(fill_value)
            null_count = int(df[col].isnull().sum())
            df_imputed[col] = df[col].fillna(fill_value)
            summary["columns"][col] = {
                "null_count_before": null_count,
                "fill_value": fill_value,
            }
            print(f"  ✓ {col}: filled {null_count} nulls with {strategy} ({fill_value:.2f})")

    return df_imputed, summary


def impute_mode(df: pd.DataFrame, categorical_cols: list[str]) -> tuple[pd.DataFrame, dict]:
    """Fill categorical nulls with mode (most common value)."""
    df_imputed = df.copy()
    summary = {"strategy": "mode", "columns": {}}

    for col in categorical_cols:
        if df[col].isnull().sum() > 0:
            mode_candidates = df[col].mode(dropna=True)
            if len(mode_candidates) == 0:
                mode_value = None
            else:
                mode_value = mode_candidates.iloc[0]
            null_count = int(df[col].isnull().sum())
            df_imputed[col] = df[col].fillna(mode_value)
            summary["columns"][col] = {
                "null_count_before": null_count,
                "fill_value": mode_value,
            }
            print(f"  ✓ {col}: filled {null_count} nulls with mode '{mode_value}'")

    return df_imputed, summary


def impute_forward_fill(df: pd.DataFrame, time_series_cols: list[str]) -> tuple[pd.DataFrame, dict]:
    """Fill with previous value (for time-series data)."""
    df_imputed = df.copy()
    summary = {"strategy": "forward_fill", "columns": {}}

    for col in time_series_cols:
        if df[col].isnull().sum() > 0:
            null_count = int(df[col].isnull().sum())
            df_imputed[col] = df[col].ffill()
            summary["columns"][col] = {"null_count_before": null_count}
            print(f"  ✓ {col}: forward-filled {null_count} nulls")

    return df_imputed, summary


def document_imputation_decisions(
    df_original: pd.DataFrame,
    df_cleaned: pd.DataFrame,
    plan: dict,
    output_path: str = "output/imputation_decisions.json",
) -> dict:
    """Document all imputation decisions with business justification."""
    decisions = {}

    for col in df_original.columns:
        null_count = int(df_original[col].isnull().sum())
        if null_count == 0:
            continue

        data_type = str(df_original[col].dtype)
        decision: dict = {
            "column_type": data_type,
            "null_count_before": null_count,
            "null_percentage_before": round((null_count / len(df_original)) * 100, 2),
        }

        if col in plan["drop_rows"].get("critical_columns", []):
            decision.update(
                {
                    "strategy": "drop_rows",
                    "rows_affected": plan["drop_rows"]["rows_dropped"],
                    "business_reasoning": (
                        "This identifier column is critical for traceability and downstream joins. "
                        "Missing values indicate records cannot be reliably matched, so dropping them preserves data integrity."
                    ),
                    "risk_assessment": (
                        "Low. Only rows with missing critical identifiers are removed, preserving the remaining dataset."
                    ),
                }
            )
        elif col in plan["numerical"].get("columns", {}):
            fill_value = plan["numerical"]["columns"][col]["fill_value"]
            decision.update(
                {
                    "strategy": f"{plan['numerical']['strategy']}_imputation",
                    "value_used": fill_value,
                    "business_reasoning": (
                        "Median imputation is chosen for numerical data because it is robust to outliers and preserves the central tendency of the distribution. "
                        "It avoids inventing extreme values for revenue-like or quantity-like fields."
                    ),
                    "risk_assessment": (
                        "Medium. Imputation introduces synthetic values, but median is stable for low missingness."
                    ),
                }
            )
        elif col in plan["categorical"]["columns"]:
            fill_value = plan["categorical"]["columns"][col]["fill_value"]
            decision.update(
                {
                    "strategy": "mode_imputation",
                    "value_used": fill_value,
                    "business_reasoning": (
                        "Mode preserves the most common category and maintains category distribution without inventing a new label. "
                        "This is appropriate for segment, category, or region fields."
                    ),
                    "risk_assessment": (
                        "Medium. Preserves distribution, but may over-represent the majority class if missingness is high."
                    ),
                }
            )
        elif col in plan["time_series"]["columns"]:
            decision.update(
                {
                    "strategy": "forward_fill",
                    "business_reasoning": (
                        "Forward fill assumes that the previous observed value remains valid until the next update. "
                        "This is appropriate for time-ordered status or price fields when values usually persist between observations."
                    ),
                    "risk_assessment": (
                        "Medium. Valid only when the column is truly time-series data and values do not change frequently."
                    ),
                }
            )
        else:
            decision.update(
                {
                    "strategy": "not_imputed",
                    "business_reasoning": "Nulls were present but no automated imputation strategy was applied for this column.",
                    "risk_assessment": "Unknown.",
                }
            )

        decisions[col] = decision

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(decisions, f, indent=2, default=str)

    print(f"\n✓ Imputation decisions documented in {output_path}")
    return decisions


def validate_imputation(df_original: pd.DataFrame, df_imputed: pd.DataFrame) -> pd.DataFrame:
    """Compare metrics before and after imputation."""
    print("\n" + "=" * 70)
    print("AFTER IMPUTATION - Validation Report")
    print("=" * 70)
    print(f"Total rows before: {len(df_original)}")
    print(f"Total rows after:  {len(df_imputed)}")
    print(f"Rows removed: {len(df_original) - len(df_imputed)}")
    print(f"\nTotal nulls before: {df_original.isnull().sum().sum()}")
    print(f"Total nulls after:  {df_imputed.isnull().sum().sum()}")

    missing_after = pd.DataFrame(
        {
            "column": df_imputed.columns,
            "null_count_after": df_imputed.isnull().sum().values,
            "null_percentage_after": (df_imputed.isnull().sum() / len(df_imputed) * 100).round(2).values,
        }
    )

    print("\nNull values by column after imputation:")
    print(missing_after.to_string(index=False))
    print("=" * 70)

    return missing_after


def get_default_input_path() -> Path:
    base_path = Path(__file__).parent.parent
    candidate = base_path / "data" / "raw" / "missing_data.csv"
    if candidate.exists():
        return candidate
    fallback = base_path / "data" / "raw" / "raw_data.csv"
    return fallback


def main():
    input_path = get_default_input_path()
    if not input_path.exists():
        raise FileNotFoundError(
            f"Could not find input data. Expected '{input_path}' to exist."
        )

    df = pd.read_csv(input_path)

    print("Step 1: Analyzing missing values...")
    analyze_missing_values(df)

    critical_columns = [col for col in ["customer_id", "email"] if col in df.columns]
    df_after_drop, drop_details = drop_rows_with_nulls(df, critical_columns)

    numerical_cols = [
        col for col in df_after_drop.select_dtypes(include=["number"]).columns if col not in critical_columns
    ]
    categorical_cols = [
        col
        for col in df_after_drop.select_dtypes(include=["object", "string"]).columns
        if col not in critical_columns
    ]
    time_series_cols = [
        col
        for col in df_after_drop.columns
        if pd.api.types.is_datetime64_any_dtype(df_after_drop[col])
        and df_after_drop[col].isnull().sum() > 0
    ]

    print("\nStep 2: Applying imputation strategies...")
    df_imputed = df_after_drop.copy()

    numerical_plan = {"strategy": "median", "columns": {}}
    if numerical_cols:
        df_imputed, numerical_plan = impute_mean_median(df_imputed, numerical_cols, strategy="median")

    categorical_plan = {"strategy": "mode", "columns": {}}
    if categorical_cols:
        df_imputed, categorical_plan = impute_mode(df_imputed, categorical_cols)

    time_series_plan = {"strategy": "forward_fill", "columns": {}}
    if time_series_cols:
        df_imputed, time_series_plan = impute_forward_fill(df_imputed, time_series_cols)

    plan = {
        "drop_rows": drop_details,
        "numerical": numerical_plan,
        "categorical": categorical_plan,
        "time_series": time_series_plan,
    }

    print("\nStep 3: Documenting imputation decisions...")
    document_imputation_decisions(df, df_imputed, plan, output_path="output/imputation_decisions.json")

    print("\nStep 4: Validating imputation...")
    validate_imputation(df, df_imputed)

    output_dir = Path("data") / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    cleaned_path = output_dir / "cleaned_data.csv"
    df_imputed.to_csv(cleaned_path, index=False)
    print(f"\n✓ Cleaned data saved to {cleaned_path}")


if __name__ == "__main__":
    main()
