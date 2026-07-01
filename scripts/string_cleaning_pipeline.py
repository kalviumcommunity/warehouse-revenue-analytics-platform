"""
String cleaning pipeline for standardizing messy text fields.

This script demonstrates reusable text cleaning operations for:
- trimming whitespace
- normalizing casing
- removing special characters
- mapping categorical variants to canonical values
"""

from __future__ import annotations

import re

import pandas as pd


def _transform_string_values(series: pd.Series, transform) -> pd.Series:
    """Apply a text transform only to actual string values and preserve others."""
    result = series.copy()
    if result.empty:
        return result

    string_mask = result.apply(lambda value: isinstance(value, str))
    if not string_mask.any():
        return result

    result.loc[string_mask] = result.loc[string_mask].apply(transform)
    return result


def strip_all_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace from all string/object columns in a DataFrame."""
    string_cols = [
        col
        for col in df.columns
        if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col])
    ]

    for col in string_cols:
        before = df[col].nunique(dropna=True)
        df[col] = _transform_string_values(df[col], lambda value: value.strip())
        after = df[col].nunique(dropna=True)
        print(f"{col}: {before} → {after} unique values")

    return df


def normalize_casing(df: pd.DataFrame, columns_to_lower: list[str]) -> pd.DataFrame:
    """Normalize casing for the selected columns to lowercase."""
    for col in columns_to_lower:
        if col in df.columns and (
            pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col])
        ):
            df[col] = _transform_string_values(df[col], lambda value: value.lower())
            print(f"Normalized {col} to lowercase")

    return df


def remove_special_characters(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Remove special characters from selected string columns using regex."""
    pattern = r"[^a-zA-Z0-9 ]"
    for col in columns:
        if col in df.columns and (
            pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col])
        ):
            df[col] = _transform_string_values(df[col], lambda value: re.sub(pattern, "", value))
            print(f"Removed special characters from {col}")

    return df


def clean_text_column(
    series: pd.Series,
    lowercase: bool = True,
    strip: bool = True,
    remove_special: bool = False,
    mapping: dict | None = None,
) -> pd.Series:
    """Clean a text column in a reusable way with optional transformations."""
    result = series.copy()

    if result.isna().any():
        print(f"Warning: {result.isna().sum()} null values in column")

    if strip:
        result = _transform_string_values(result, lambda value: value.strip())

    if lowercase:
        result = _transform_string_values(result, lambda value: value.lower())

    if remove_special:
        result = _transform_string_values(result, lambda value: re.sub(r"[^a-zA-Z0-9 ]", "", value))

    if mapping:
        string_mask = result.apply(lambda value: isinstance(value, str))
        if string_mask.any():
            result.loc[string_mask] = result.loc[string_mask].map(mapping)

    return result


def build_sample_dataset() -> pd.DataFrame:
    """Create a sample dataset with inconsistent text values for demonstration."""
    return pd.DataFrame(
        {
            "product_name": [" Electronics ", "electronics", "ELECTRONICS", " electro nics "],
            "customer_name": [" John ", "JOHN", "john", "Jane "],
            "segment": ["B2B", "b2b", "B 2 B", "sme"],
            "city": ["São Paulo", "Montréal", "New York", "São Paulo"],
        }
    )


def standardize_segments(series: pd.Series) -> pd.Series:
    """Map common segment variants to canonical labels."""
    segment_map = {
        "b2b": "B2B",
        "b 2 b": "B2B",
        "business-to-business": "B2B",
        "sme": "SMB",
        "small medium enterprise": "SMB",
        "enterprise": "Enterprise",
    }
    return clean_text_column(series, lowercase=True, strip=True, mapping=segment_map)


def run_demo() -> None:
    """Run the cleaning pipeline and print summaries for the assignment."""
    df = build_sample_dataset()

    print("Original data:")
    print(df)

    df = strip_all_strings(df)
    df = normalize_casing(df, ["product_name", "customer_name", "segment"])
    df = remove_special_characters(df, ["city"])
    df["segment"] = standardize_segments(df["segment"])

    print("\nCleaned data:")
    print(df)

    print("\nBefore/after segment value counts:")
    print(pd.Series(["B2B", "b2b", "B 2 B", "sme"]).value_counts())
    print(pd.Series(["B2B", "B2B", "B2B", "SMB"]).value_counts())


if __name__ == "__main__":
    run_demo()
