import os
import sys

import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.string_cleaning_pipeline import (
    clean_text_column,
    normalize_casing,
    remove_special_characters,
    strip_all_strings,
)


def test_string_cleaning_pipeline_standardizes_text_fields():
    df = pd.DataFrame(
        {
            "product_name": [" Electronics ", "electronics", "ELECTRONICS", " electro nics "],
            "customer_name": [" John ", "JOHN", "john", "Jane "],
            "segment": ["B2B", "b2b", "B 2 B", "sme"],
            "city": ["São Paulo", "Montréal", "New York", "São Paulo"],
        }
    )

    cleaned = strip_all_strings(df.copy())
    assert cleaned.loc[0, "product_name"] == "Electronics"
    assert cleaned.loc[0, "customer_name"] == "John"

    cleaned = normalize_casing(cleaned, ["product_name", "customer_name", "segment"])
    assert cleaned.loc[0, "product_name"] == "electronics"
    assert cleaned.loc[0, "customer_name"] == "john"

    cleaned = remove_special_characters(cleaned, ["city"])
    assert cleaned.loc[0, "city"] == "So Paulo"

    result = clean_text_column(
        pd.Series(["  Product A  ", "PRODUCT B", "Product_C", None, ""]),
        lowercase=True,
        strip=True,
        remove_special=True,
    )
    assert result.iloc[0] == "product a"
    assert result.iloc[1] == "product b"
    assert result.iloc[2] == "productc"
    assert pd.isna(result.iloc[3])
