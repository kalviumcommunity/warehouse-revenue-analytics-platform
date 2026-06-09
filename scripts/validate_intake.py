import os
import json
from datetime import datetime

import pandas as pd
import chardet


def validate_file_exists(filepath):
    """
    Verify that the file exists and is not empty.

    Input:
        filepath (str)

    Returns:
        (bool, str)
        Success flag and descriptive message.
    """

    # Check whether file exists
    if not os.path.exists(filepath):
        return False, f"File does not exist: {filepath}"

    # Check if file contains data
    if os.path.getsize(filepath) == 0:
        return False, f"File is empty: {filepath}"

    return True, "PASS - File exists and has content"


def validate_file_format(filepath, allowed_formats=None):
    """
    Verify that the file extension is supported.

    Input:
        filepath (str)

    Returns:
        (bool, str)
    """

    if allowed_formats is None:
        allowed_formats = ["csv", "json", "xlsx"]

    extension = filepath.split(".")[-1].lower()

    if extension not in allowed_formats:
        return (
            False,
            f"FAIL - Unsupported format: {extension}. Allowed: {allowed_formats}",
        )

    return True, f"PASS - Format valid: {extension}"


def validate_schema(df, expected_columns):
    """
    Compare dataframe columns against expected schema.

    Input:
        df (DataFrame)
        expected_columns (list)

    Returns:
        (bool, str)
    """

    # Columns missing from incoming dataset
    missing = set(expected_columns) - set(df.columns)

    # Unexpected columns
    extra = set(df.columns) - set(expected_columns)

    issues = []

    if missing:
        issues.append(f"Missing columns: {missing}")

    if extra:
        issues.append(f"Unexpected columns: {extra}")

    if not issues:
        return True, f"PASS - Schema valid: {len(df.columns)} columns present"

    return False, "FAIL - " + " | ".join(issues)


def detect_encoding(filepath):
    """
    Detect file encoding.

    Input:
        filepath (str)

    Returns:
        tuple:
            encoding name
            descriptive message
    """

    with open(filepath, "rb") as f:
        result = chardet.detect(f.read(10000))

    encoding = result.get("encoding", "utf-8")
    confidence = result.get("confidence", 0)

    return (
        encoding,
        f"PASS - Detected: {encoding} (confidence: {confidence:.1%})",
    )


def capture_dataset_stats(filepath, df):
    """
    Capture basic dataset metrics.

    Input:
        filepath (str)
        df (DataFrame)

    Returns:
        dictionary
    """

    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "file_size_mb": round(file_size_mb, 5),
        "bytes": os.path.getsize(filepath),
    }


def generate_intake_report(filepath, expected_columns):
    """
    Execute all validation checks and create a JSON report.

    Input:
        filepath (str)
        expected_columns (list)

    Returns:
        dict containing validation results.
    """

    report = {
        "timestamp": datetime.now().isoformat(),
        "filepath": filepath,
        "validations": {},
    }

    # File existence validation

    file_exists, msg = validate_file_exists(filepath)

    report["validations"]["file_exists"] = msg

    if not file_exists:
        return report

    # File format validation

    _, msg = validate_file_format(filepath)

    report["validations"]["format"] = msg

    # Load dataset

    df = pd.read_csv(filepath)

    # Schema validation

    _, msg = validate_schema(df, expected_columns)

    report["validations"]["schema"] = msg

    # Encoding detection

    _, msg = detect_encoding(filepath)

    report["validations"]["encoding"] = msg

    # Dataset statistics

    report["statistics"] = capture_dataset_stats(filepath, df)

    # Create output directory if needed
    os.makedirs("output", exist_ok=True)

    # Save report
    with open("output/intake_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


if __name__ == "__main__":

    filepath = "data/raw/sample.csv"

    expected_columns = [
        "customer_id",
        "customer_name",
        "transaction_amount",
        "transaction_date",
    ]

    try:
        report = generate_intake_report(filepath, expected_columns)

        print("[SUCCESS] Intake validation completed.")
        print("[SUCCESS] Report saved to output/intake_report.json")

    except Exception as e:
        print(f"[ERROR] Validation failed: {e}")
