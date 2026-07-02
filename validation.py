from pathlib import Path
from typing import Any

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
DEFAULT_INPUT = BASE_DIR / "data" / "raw_data.csv"
FALLBACK_INPUTS = [
    BASE_DIR / "data" / "raw" / "customers.csv",
    BASE_DIR / "data" / "raw" / "sample.csv",
    BASE_DIR / "data" / "raw" / "sample2.csv",
    BASE_DIR / "data" / "raw" / "quality_test.csv",
]


def resolve_input_file():
    if DEFAULT_INPUT.exists():
        return DEFAULT_INPUT

    for candidate in FALLBACK_INPUTS:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        "No input CSV found. Place your file at data/raw_data.csv or update the script."
    )


def series_or_default(df, column_name, default_value: Any = True):
    if column_name in df.columns:
        return df[column_name]
    return pd.Series(default_value, index=df.index)


def main():
    input_file = resolve_input_file()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_file)

    print("========== Dataset Inspection ==========")
    print(df.columns)
    print(df.head())
    df.info()

    date_columns = [
        "birth_date",
        "start_date",
        "end_date",
        "campaign_start_date",
        "campaign_end_date",
        "signup_date",
    ]

    for column_name in date_columns:
        if column_name in df.columns:
            df[column_name] = pd.to_datetime(df[column_name], errors="coerce")

if "age" in df.columns:
    age_num = pd.to_numeric(df["age"], errors="coerce")
    df["valid_age"] = age_num.between(0, 150, inclusive="both")
    else:
        df["valid_age"] = pd.Series(True, index=df.index)

if "price" in df.columns:
    price_num = pd.to_numeric(df["price"], errors="coerce")
    df["valid_price"] = price_num >= 0
    else:
        df["valid_price"] = pd.Series(True, index=df.index)

    if "birth_date" in df.columns:
        df["valid_date"] = (df["birth_date"] >= pd.Timestamp("1920-01-01")) & (
            df["birth_date"] <= pd.Timestamp.now()
        )
    else:
        df["valid_date"] = pd.Series(True, index=df.index)

    df["valid_customer_id"] = (
        df["customer_id"].notna()
        if "customer_id" in df.columns
        else pd.Series(True, index=df.index)
    )

    df["valid_email"] = (
        df["email"].notna()
        if "email" in df.columns
        else pd.Series(True, index=df.index)
    )

    if "email" in df.columns:
        df["valid_email_format"] = (
            df["email"].astype("string").str.contains("@", na=False)
        )
    else:
        df["valid_email_format"] = pd.Series(True, index=df.index)

    if "phone" in df.columns:
        df["valid_phone"] = (
            df["phone"].astype("string").str.match(r"^\d{10}$", na=False)
        )
    else:
        df["valid_phone"] = pd.Series(True, index=df.index)

    if {"end_date", "start_date"}.issubset(df.columns):
        df["valid_date_order"] = df["end_date"] >= df["start_date"]
    elif {"campaign_end_date", "campaign_start_date"}.issubset(df.columns):
        df["valid_date_order"] = df["campaign_end_date"] >= df["campaign_start_date"]
    else:
        df["valid_date_order"] = pd.Series(True, index=df.index)

    validation_cols = [
        "valid_age",
        "valid_price",
        "valid_date",
        "valid_customer_id",
        "valid_email",
        "valid_email_format",
        "valid_phone",
        "valid_date_order",
    ]

    df["passes_all_checks"] = df[validation_cols].all(axis=1)
    failures = df[~df["passes_all_checks"]]
    df_clean = df[df["passes_all_checks"]].copy()

    failures.to_csv(OUTPUT_DIR / "validation_failures.csv", index=False)

    print("========== Validation Report ==========")
    print(f"Source File : {input_file}")
    print(f"Total Records : {len(df)}")
    print(f"Passed : {int(df['passes_all_checks'].sum())}")
    print(f"Failed : {int((~df['passes_all_checks']).sum())}")
    print(f"Invalid Ages: {int((~df['valid_age']).sum())}")
    print(f"Invalid Prices: {int((~df['valid_price']).sum())}")
    print(f"Invalid Birth Dates: {int((~df['valid_date']).sum())}")
    print(f"Missing Customer IDs: {int((~df['valid_customer_id']).sum())}")
    print(f"Missing Emails: {int((~df['valid_email']).sum())}")
    print(f"Invalid Email Format: {int((~df['valid_email_format']).sum())}")
    print(f"Invalid Phones: {int((~df['valid_phone']).sum())}")
    print(f"Invalid Date Order: {int((~df['valid_date_order']).sum())}")
    print(f"Saved failed records to: {OUTPUT_DIR / 'validation_failures.csv'}")
    print(f"Clean records available in df_clean with {len(df_clean)} rows")

    return df_clean, failures


if __name__ == "__main__":
    main()
