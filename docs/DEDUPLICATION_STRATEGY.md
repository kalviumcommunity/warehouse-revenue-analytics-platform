# Duplicate Detection and Deduplication Strategy

## Overview
This workflow detects two duplicate patterns:

1. Exact duplicates: rows where every column value is identical.
2. Near-duplicates: rows that share the same business key but differ in other fields.

## Strategy
- Exact duplicates are removed with `keep='first'` so the earliest valid record is preserved.
- Near-duplicates are evaluated by the business key `customer_id` and `transaction_date`.
- When multiple rows share the same key, the most complete row is kept by selecting the record with the fewest null values.
- All removed rows are exported to `output/removed_duplicates_audit.csv` for audit and compliance purposes.

## Why this approach
- It prevents inflated customer and transaction counts.
- It keeps a deterministic and explainable record-selection rule.
- It leaves a traceable audit trail for downstream analysis and investigations.
