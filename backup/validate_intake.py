import json
import os
from datetime import datetime

import chardet
import pandas as pd


DEFAULT_INPUT = "data/raw/sample.csv"
DEFAULT_OUTPUT = "output/intake_report.json"
DEFAULT_ALLOWED_FORMATS = ["csv", "json", "xlsx"]
DEFAULT_EXPECTED_COLUMNS = [
    "customer_id",
    "customer_name",
    "transaction_amount",
    "transaction_date",
]


def validate_file_exists(filepath):
    """Check if file exists and is non-empty."""
    if not os.path.exists(filepath):
        return False, f"File does not exist: {filepath}"

    if os.path.getsize(filepath) == 0:
        return False, f"File is empty: {filepath}"

    return True, "File exists and has content"


def validate_file_format(filepath, allowed_formats=None):
    """Check if file extension is supported."""
    if allowed_formats is None:
        allowed_formats = DEFAULT_ALLOWED_FORMATS

    extension = os.path.splitext(filepath)[1].lower().replace('.', '')

    if extension not in allowed_formats:
        return False, f"Unsupported format: {extension}. Allowed: {allowed_formats}"

    return True, f"Format valid: {extension}"


def validate_schema(df, expected_columns):
    """Validate that DataFrame has all expected columns."""
    missing = set(expected_columns) - set(df.columns)
    extra = set(df.columns) - set(expected_columns)

    issues = []
    if missing:
        issues.append(f"Missing columns: {sorted(missing)}")
    if extra:
        issues.append(f"Unexpected columns: {sorted(extra)}")

    if not issues:
        return True, f"Schema valid: {len(df.columns)} columns present"

    return False, " | ".join(issues)


def detect_encoding(filepath):
    """Detect file encoding with confidence."""
    with open(filepath, 'rb') as file:
        result = chardet.detect(file.read(10000))

    encoding = result.get('encoding', 'utf-8')
    confidence = result.get('confidence', 0)

    return encoding, f"Detected: {encoding} (confidence: {confidence:.1%})"


def capture_dataset_stats(filepath, df):
    """Log row count and file size."""
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)

    return {
        'rows': len(df),
        'columns': len(df.columns),
        'file_size_mb': round(file_size_mb, 2),
        'bytes': os.path.getsize(filepath),
    }


def generate_intake_report(filepath, expected_columns, output_path=DEFAULT_OUTPUT):
    """Generate a complete intake validation report."""
    report = {
        'timestamp': datetime.now().isoformat(),
        'filepath': filepath,
        'validations': {},
        'overall_status': 'passed',
    }

    file_exists, file_msg = validate_file_exists(filepath)
    report['validations']['file_exists'] = {
        'status': 'passed' if file_exists else 'failed',
        'message': file_msg,
    }
    if not file_exists:
        report['overall_status'] = 'failed'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as handle:
            json.dump(report, handle, indent=2, default=str)
        return report

    format_valid, format_msg = validate_file_format(filepath)
    report['validations']['format'] = {
        'status': 'passed' if format_valid else 'failed',
        'message': format_msg,
    }
    if not format_valid:
        report['overall_status'] = 'failed'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as handle:
            json.dump(report, handle, indent=2, default=str)
        return report

    try:
        df = pd.read_csv(filepath, encoding='utf-8')
    except UnicodeDecodeError:
        report['validations']['schema'] = {
            'status': 'failed',
            'message': 'Unable to decode file with utf-8 encoding',
        }
        report['overall_status'] = 'failed'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as handle:
            json.dump(report, handle, indent=2, default=str)
        return report

    schema_valid, schema_msg = validate_schema(df, expected_columns)
    report['validations']['schema'] = {
        'status': 'passed' if schema_valid else 'failed',
        'message': schema_msg,
    }

    encoding, encoding_msg = detect_encoding(filepath)
    report['validations']['encoding'] = {
        'status': 'passed' if encoding else 'failed',
        'message': encoding_msg,
    }

    report['statistics'] = capture_dataset_stats(filepath, df)

    if not all(item['status'] == 'passed' for item in report['validations'].values()):
        report['overall_status'] = 'failed'

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as handle:
        json.dump(report, handle, indent=2, default=str)

    return report


def main():
    report = generate_intake_report(DEFAULT_INPUT, DEFAULT_EXPECTED_COLUMNS)
    print(json.dumps(report, indent=2, default=str))


if __name__ == '__main__':
    main()
