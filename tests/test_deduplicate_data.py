import os
import pandas as pd
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.deduplicate_data import (
    detect_exact_duplicates,
    detect_near_duplicates,
    remove_exact_duplicates,
    remove_near_duplicates,
    compare_before_after,
)


def test_deduplication_pipeline():
    df = pd.DataFrame(
        [
            {"customer_id": 1, "transaction_date": "2025-01-15", "amount": 100, "status": "completed"},
            {"customer_id": 1, "transaction_date": "2025-01-15", "amount": 100, "status": "completed"},
            {"customer_id": 2, "transaction_date": "2025-01-20", "amount": 250, "status": "pending"},
            {"customer_id": 2, "transaction_date": "2025-01-20", "amount": 250, "status": "pending"},
            {"customer_id": 3, "transaction_date": "2025-02-01", "amount": 150, "status": "completed"},
        ]
    )

    exact_count, exact_rows = detect_exact_duplicates(df)
    assert exact_count == 2
    assert len(exact_rows) == 4

    near_rows = detect_near_duplicates(df, key_columns=["customer_id", "transaction_date"])
    assert len(near_rows) == 4

    deduped = remove_exact_duplicates(df, keep="first")
    assert len(deduped) == 3

    deduped_near = remove_near_duplicates(deduped, key_columns=["customer_id", "transaction_date"], keep_strategy="first")
    assert len(deduped_near) == 3

    comparison = compare_before_after(df, deduped_near)
    assert comparison["rows_before"] == 5
    assert comparison["rows_after"] == 3


def test_empty_dataframe_is_handled_gracefully():
    df = pd.DataFrame(columns=["customer_id", "transaction_date", "amount"])

    exact_count, exact_rows = detect_exact_duplicates(df)
    assert exact_count == 0
    assert exact_rows.empty

    deduped = remove_exact_duplicates(df, keep="first")
    assert deduped.empty

    deduped_near = remove_near_duplicates(deduped, key_columns=["customer_id"], keep_strategy="first")
    assert deduped_near.empty
