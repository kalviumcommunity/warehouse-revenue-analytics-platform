# GitHub Issue Templates - Copy & Paste Into GitHub

---

## Issue #1: Data Ingestion Task

**Title:**
```
Ingest customer transaction data into pipeline
```

**Description:**
```
## Context
The analytics team needs reliable ingestion of customer transaction data from raw sources into the processed data layer. Currently, no validation or schema checking exists for incoming data.

## What Needs to Happen
- Create Python script to read transaction CSV files from data/raw/
- Validate incoming data schema (columns, data types, row counts)
- Log validation errors and skip invalid records
- Save validated data to data/processed/transactions.csv

## Success Criteria
✅ Script reads CSV files without errors
✅ Validates all required columns exist
✅ Handles missing/invalid values gracefully
✅ Generates validation report
✅ Processes sample data successfully

## Requirements
- Use pandas for data handling
- Add validation function to scripts/
- Update requirements.txt with dependencies
```

**Labels:** `feature`, `data-pipeline`
**Assignee:** (yourself)

---

## Issue #2: Data Quality Documentation

**Title:**
```
Create data quality report template for incoming datasets
```

**Description:**
```
## Context
As datasets flow through our pipeline, the team needs visibility into data quality metrics. Currently, no standardized way to report quality issues across datasets.

## What Needs to Happen
- Design data quality report structure (schema completeness, null %, outliers, duplicates)
- Create Python function to generate quality metrics
- Save reports to data/processed/ with timestamp
- Document report format in README

## Success Criteria
✅ Report captures key quality metrics
✅ Function runs on any dataset
✅ Report is human-readable
✅ Documentation updated
✅ Sample report generated

## Requirements
- Function should be reusable across datasets
- Add to scripts/ folder
- Include null value analysis, outlier detection
```

**Labels:** `feature`, `analysis`, `documentation`
**Assignee:** (yourself)

---

## Issue #3: Data Dictionary Documentation

**Title:**
```
Document data dictionary for team reference
```

**Description:**
```
## Context
Team members are unclear about what columns mean, what data types they should be, and what valid values are. This causes confusion during analysis and integration.

## What Needs to Happening
- Document all datasets (customers, transactions, products if applicable)
- For each column: name, description, data type, valid range/values
- Include business rules and definitions
- Save to docs/ or README.md

## Success Criteria
✅ All datasets documented
✅ Every column has description and data type
✅ Business context is clear
✅ Team can reference it without asking
✅ Format is easy to update

## Requirements
- Add to README.md or create separate DATADICTIONARY.md
- Include examples of valid values
- Document any NULL/missing value handling
```

**Labels:** `documentation`, `data-pipeline`
**Assignee:** (yourself)

---

## How to Create These on GitHub

1. Go to your repository → **Issues** tab
2. Click **New Issue**
3. Copy the Title into the Title field
4. Copy the Description (without the "Description:" label)
5. Add Labels from the list
6. Set Assignee to yourself
7. Click **Submit new issue**
8. Repeat for all 3 issues

**Result:** You'll have 3 trackable issues your team can reference
