"""
data_workflow.py

A modular data processing workflow that demonstrates
data ingestion, transformation, and output generation.

Run:
    python scripts/data_workflow.py
"""

import os
import pandas as pd


def ingest_data(filepath):
    """
    Load data from a CSV file.

    Input:
        filepath (str): Path to the source CSV file.

    Returns:
        pandas.DataFrame:
            Raw dataset loaded from disk.

    Assumptions:
        - File exists.
        - File is a valid CSV.
        - User has read permissions.
    """
    try:
        # Read CSV data into a DataFrame
        df = pd.read_csv(filepath)

        print(f"[INFO] Loaded {len(df)} rows from {filepath}")

        return df

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Input file not found: {filepath}"
        )

    except Exception as error:
        raise Exception(
            f"Failed to ingest data: {error}"
        )


def process_data(df):
    """
    Transform raw data into analysis-ready format.

    Input:
        df (pandas.DataFrame):
            Raw dataset.

    Returns:
        pandas.DataFrame:
            Cleaned and processed dataset.

    Processing Steps:
        - Remove duplicate rows.
        - Fill missing numeric values with median.
        - Add a processing timestamp column.

    Assumptions:
        - DataFrame is not empty.
    """

    # Remove exact duplicate records
    df = df.drop_duplicates()

    # Fill missing values in numeric columns with their respective medians
    numeric_columns = df.select_dtypes(include=["number"]).columns
    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())

    # Add metadata column indicating processing occurred
    df["processed_flag"] = True

    return df


def output_results(df, output_path):
    """
    Save processed data to disk.

    Input:
        df (pandas.DataFrame):
            Processed dataset.

        output_path (str):
            Destination CSV file path.

    Returns:
        None

    Assumptions:
        - Output directory is writable.
    """

    # Create output directory if it does not exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write processed data to CSV
    df.to_csv(output_path, index=False)

    # Print execution summary
    print("[SUCCESS] Data successfully processed")
    print(f"[SUCCESS] Rows processed: {len(df)}")
    print(f"[SUCCESS] Output saved to {output_path}")


if __name__ == "__main__":
    try:
        # Define input and output paths
        input_file = "data/raw/sample.csv"
        output_file = "output/processed.csv"

        # Pipeline execution
        raw_data = ingest_data(input_file)
        processed_data = process_data(raw_data)
        output_results(processed_data, output_file)

    except Exception as error:
        print(f"[ERROR] Workflow failed: {error}")
