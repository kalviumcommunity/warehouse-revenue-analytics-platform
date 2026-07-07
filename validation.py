import json
from pathlib import Path
from typing import Any, Iterable

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
CUSTOMER_INPUTS = [
    BASE_DIR / "data" / "processed" / "customers_ingested.csv",
    BASE_DIR / "data" / "raw" / "customers.csv",
]
ORDER_INPUTS = [
    BASE_DIR / "data" / "processed" / "transactions_ingested.csv",
    BASE_DIR / "data" / "raw" / "transactions.json",
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


def resolve_existing_file(candidates: Iterable[Path], label: str) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate

    candidate_list = ", ".join(str(path) for path in candidates)
    raise FileNotFoundError(f"No {label} file found. Checked: {candidate_list}")


def load_frame(file_path: Path) -> pd.DataFrame:
    if file_path.suffix.lower() == ".json":
        return pd.read_json(file_path)
    return pd.read_csv(file_path)


def series_or_default(df, column_name, default_value: Any = True):
    if column_name in df.columns:
        return df[column_name]
    return pd.Series(default_value, index=df.index)


def normalize_join_key(df: pd.DataFrame, key: str) -> pd.DataFrame:
    normalized = df.copy()
    normalized[key] = normalized[key].astype("string").str.strip()
    return normalized


def save_dataframe(df: pd.DataFrame, file_name: str) -> Path:
    destination = OUTPUT_DIR / file_name
    df.to_csv(destination, index=False)
    return destination


def run_single_dataset_validation(input_file: Path):
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


def run_join_analysis():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    customers_file = resolve_existing_file(CUSTOMER_INPUTS, "customer")
    orders_file = resolve_existing_file(ORDER_INPUTS, "order")

    df_customers = load_frame(customers_file)
    df_orders = load_frame(orders_file)

    df_customers = normalize_join_key(df_customers, "customer_id")
    df_orders = normalize_join_key(df_orders, "customer_id")

    print("========== Join Validation ==========")
    print(f"Left: {len(df_customers)}")
    print(f"Right: {len(df_orders)}")

    if (
        "customer_id" not in df_customers.columns
        or "customer_id" not in df_orders.columns
    ):
        raise KeyError("Both datasets must contain a customer_id column for the join.")

    df_merged = pd.merge(df_customers, df_orders, on="customer_id", how="left")

    print(f"Merged: {len(df_merged)}")
    print(f"Change: {len(df_merged) - len(df_customers)}")

    unmatched_customers = df_customers[
        ~df_customers["customer_id"].isin(df_orders["customer_id"])
    ]
    unmatched_orders = df_orders[
        ~df_orders["customer_id"].isin(df_customers["customer_id"])
    ]

    print(f"Customers without orders: {len(unmatched_customers)}")
    print(f"Orphaned orders: {len(unmatched_orders)}")

    unmatched_customers_path = save_dataframe(
        unmatched_customers, "unmatched_customers.csv"
    )
    unmatched_orders_path = save_dataframe(unmatched_orders, "unmatched_orders.csv")

    inner = pd.merge(df_customers, df_orders, on="customer_id", how="inner")
    left = pd.merge(df_customers, df_orders, on="customer_id", how="left")
    right = pd.merge(df_customers, df_orders, on="customer_id", how="right")
    outer = pd.merge(df_customers, df_orders, on="customer_id", how="outer")

    print(
        f"Inner: {len(inner)}, Left: {len(left)}, Right: {len(right)}, Outer: {len(outer)}"
    )
    print(df_merged.columns)

    key_counts = df_merged["customer_id"].value_counts(dropna=False)
    max_orders_per_customer = int(key_counts.max()) if not key_counts.empty else 0
    print(f"Max orders per customer: {max_orders_per_customer}")

    duplicate_customers = df_customers[
        df_customers.duplicated(subset=["customer_id"], keep=False)
    ]
    duplicate_orders = df_orders[
        df_orders.duplicated(subset=["customer_id"], keep=False)
    ]

    join_report = {
        "join_type": "left",
        "left_table": "customers",
        "right_table": "orders",
        "join_key": "customer_id",
        "left_rows": len(df_customers),
        "right_rows": len(df_orders),
        "result_rows": len(df_merged),
        "row_change": len(df_merged) - len(df_customers),
        "inner_rows": len(inner),
        "right_join_rows": len(right),
        "outer_rows": len(outer),
        "unmatched_left": len(unmatched_customers),
        "unmatched_right": len(unmatched_orders),
        "max_orders_per_customer": max_orders_per_customer,
        "duplicate_customers": len(duplicate_customers),
        "duplicate_orders": len(duplicate_orders),
        "reasoning": (
            "Left join preserves every customer record while attaching matching orders. "
            "This is the right business choice when customers are the master table and "
            "orders are optional detail rows. Unmatched customers highlight gaps in order "
            "activity, and orphaned orders expose source-data quality issues that should be "
            "reviewed before downstream reporting."
        ),
        "source_files": {
            "customers": str(customers_file),
            "orders": str(orders_file),
        },
        "output_files": {
            "unmatched_customers": str(unmatched_customers_path),
            "unmatched_orders": str(unmatched_orders_path),
        },
    }

    report_path = OUTPUT_DIR / "join_report.json"
    report_path.write_text(json.dumps(join_report, indent=2), encoding="utf-8")

    print(json.dumps(join_report, indent=2))
    print(f"Saved join report to: {report_path}")

    return df_merged, unmatched_customers, unmatched_orders, join_report


def main():
    try:
        resolve_existing_file(CUSTOMER_INPUTS, "customer")
        resolve_existing_file(ORDER_INPUTS, "order")
    except FileNotFoundError:
        input_file = resolve_input_file()
        return run_single_dataset_validation(input_file)

    return run_join_analysis()


if __name__ == "__main__":
    main()
