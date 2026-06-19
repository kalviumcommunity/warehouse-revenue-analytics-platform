import csv
import json
import os
from pathlib import Path

import pandas as pd


def cast_columns_to_types(df: pd.DataFrame, type_mapping: dict[str, str]) -> tuple[pd.DataFrame, dict]:
    """Explicitly cast columns to correct dtypes."""
    df_typed = df.copy()
    conversion_log = {}

    for col, target_dtype in type_mapping.items():
        if col not in df_typed.columns:
            print(f"Warning: Column {col} not found in DataFrame")
            conversion_log[col] = {
                "from": None,
                "to": target_dtype,
                "status": "missing_column",
                "error": "Column not found",
            }
            continue

        original_dtype = df_typed[col].dtype
        try:
            df_typed[col] = df_typed[col].astype(target_dtype)
            conversion_log[col] = {
                "from": str(original_dtype),
                "to": target_dtype,
                "status": "success",
            }
            print(f"✓ {col}: {original_dtype} → {target_dtype}")
        except Exception as e:
            conversion_log[col] = {
                "from": str(original_dtype),
                "to": target_dtype,
                "status": "failed",
                "error": str(e),
            }
            print(f"✗ {col}: Conversion to {target_dtype} failed - {e}")
            raise

    return df_typed, conversion_log


def convert_string_dates_to_datetime(
    df: pd.DataFrame,
    date_columns: list[str],
    date_format: str | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Convert string columns to datetime with explicit format."""
    df_typed = df.copy()
    conversion_log = {}

    for col in date_columns:
        if col not in df_typed.columns:
            print(f"Warning: Column {col} not found")
            conversion_log[col] = {
                "status": "missing_column",
                "error": "Column not found",
            }
            continue

        try:
            if date_format:
                df_typed[col] = pd.to_datetime(df_typed[col], format=date_format)
            else:
                df_typed[col] = pd.to_datetime(df_typed[col])
            conversion_log[col] = {
                "status": "success",
                "from": str(df[col].dtype),
                "to": "datetime64[ns]",
                "format": date_format,
            }
            print(f"✓ {col}: Converted to datetime using format '{date_format}'")
        except Exception as e:
            sample_values = df_typed[col].head(5).tolist()
            conversion_log[col] = {
                "status": "failed",
                "error": str(e),
                "sample_values": sample_values,
                "format": date_format,
            }
            print(f"✗ {col}: Conversion failed - {e}")
            print(f"  Sample values: {sample_values}")
            print(f"  Expected format: {date_format}")
            raise

    return df_typed, conversion_log


def convert_currency_to_float(
    df: pd.DataFrame,
    currency_columns: list[str],
) -> tuple[pd.DataFrame, dict]:
    """Strip currency symbols and convert to float."""
    df_typed = df.copy()
    conversion_log = {}

    for col in currency_columns:
        if col not in df_typed.columns:
            print(f"Warning: Column {col} not found")
            conversion_log[col] = {
                "status": "missing_column",
                "error": "Column not found",
            }
            continue

        try:
            cleaned = (
                df_typed[col]
                .astype(str)
                .str.replace(r"[\$€,£,\s]", "", regex=True)
                .str.replace(
                    r"[^0-9\.\-]",
                    "",
                    regex=True,
                )
                .replace("", pd.NA)
            )
            numeric = pd.to_numeric(cleaned, errors="coerce")
            missing_before = int(df_typed[col].isna().sum())
            failed_conversions = int(numeric.isna().sum()) - missing_before
            df_typed[col] = numeric

            conversion_log[col] = {
                "status": "success",
                "from": str(df[col].dtype),
                "to": "float64",
                "failed_conversions": failed_conversions,
            }
            if failed_conversions > 0:
                print(
                    f"⚠ {col}: {failed_conversions} values could not be converted to float"
                )
            print(f"✓ {col}: Stripped currency symbols and converted to float")
        except Exception as e:
            conversion_log[col] = {
                "status": "failed",
                "error": str(e),
            }
            print(f"✗ {col}: Conversion failed - {e}")
            raise

    return df_typed, conversion_log


def convert_integers_to_boolean(
    df: pd.DataFrame,
    boolean_columns: list[str],
) -> tuple[pd.DataFrame, dict]:
    """Convert 0/1 or yes/no columns to proper boolean type."""
    df_typed = df.copy()
    conversion_log = {}

    for col in boolean_columns:
        if col not in df_typed.columns:
            print(f"Warning: Column {col} not found")
            conversion_log[col] = {
                "status": "missing_column",
                "error": "Column not found",
            }
            continue

        try:
            unique_vals = df_typed[col].dropna().unique().tolist()
            print(f"  {col} unique values: {unique_vals}")

            if df_typed[col].dtype == "object":
                mapping = {
                    "yes": True,
                    "no": False,
                    "y": True,
                    "n": False,
                    "true": True,
                    "false": False,
                    "1": True,
                    "0": False,
                    1: True,
                    0: False,
                    True: True,
                    False: False,
                }
                normalized = df_typed[col].astype(str).str.strip().str.lower()
                df_typed[col] = normalized.map(mapping)
            else:
                df_typed[col] = df_typed[col].astype(bool)

            conversion_log[col] = {
                "status": "success",
                "from": str(df[col].dtype),
                "to": "bool",
                "unique_values": unique_vals,
            }
            print(f"✓ {col}: Converted to boolean")
        except Exception as e:
            conversion_log[col] = {
                "status": "failed",
                "error": str(e),
            }
            print(f"✗ {col}: Conversion failed - {e}")
            raise

    return df_typed, conversion_log


def compare_dtypes(df_original: pd.DataFrame, df_typed: pd.DataFrame) -> pd.DataFrame:
    """Compare dtypes before and after conversion."""
    comparison = pd.DataFrame(
        {
            "column": df_original.columns,
            "dtype_before": df_original.dtypes.astype(str).values,
            "dtype_after": df_typed.dtypes.astype(str).values,
            "changed": (df_original.dtypes != df_typed.dtypes).values,
        }
    )

    print("\n" + "=" * 70)
    print("DTYPE CONVERSION SUMMARY")
    print("=" * 70)
    print(comparison.to_string(index=False))

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "dtype_conversion_report.csv"
    comparison.to_csv(report_path, index=False)
    print(f"\nReport saved to {report_path}")
    print("=" * 70)

    return comparison


def get_default_input_path() -> Path:
    base_path = Path(__file__).parent.parent
    candidate = base_path / "data" / "raw" / "untyped_data.csv"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(
        f"Could not find input data. Expected '{candidate}' to exist."
    )


def main() -> None:
    input_path = get_default_input_path()
    df = pd.read_csv(input_path)

    print("=" * 70)
    print("BEFORE TYPE CONVERSION")
    print("=" * 70)
    print(df.dtypes)
    print("\nSample data:")
    print(df.head(3).to_string(index=False))

    df_typed = df.copy()
    conversion_artifacts: dict[str, dict] = {}

    print("\n1. Converting date columns...")
    date_cols = ["transaction_date", "signup_date"]
    df_typed, date_log = convert_string_dates_to_datetime(
        df_typed,
        date_cols,
        date_format="%Y-%m-%d",
    )
    conversion_artifacts["date_conversion"] = date_log

    print("\n2. Converting currency columns...")
    currency_cols = ["amount", "revenue"]
    df_typed, currency_log = convert_currency_to_float(df_typed, currency_cols)
    conversion_artifacts["currency_conversion"] = currency_log

    print("\n3. Converting boolean columns...")
    boolean_cols = ["is_active", "is_premium"]
    df_typed, boolean_log = convert_integers_to_boolean(df_typed, boolean_cols)
    conversion_artifacts["boolean_conversion"] = boolean_log

    print("\n4. Comparing before/after types...")
    comparison = compare_dtypes(df, df_typed)

    output_dir = Path("data") / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    typed_path = output_dir / "typed_data.csv"
    df_typed.to_csv(typed_path, index=False)
    print(f"\n✓ Typed data saved to {typed_path}")

    json_path = Path("output") / "dtype_conversion_log.json"
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(conversion_artifacts, handle, indent=2, default=str)
    print(f"✓ Conversion log saved to {json_path}")


if __name__ == "__main__":
    main()
