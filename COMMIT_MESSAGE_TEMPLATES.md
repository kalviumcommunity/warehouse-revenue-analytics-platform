# Commit Message Templates - Use These for Your Commits

Copy each commit message below and use them for your 3+ commits on the feature branch.

---

## Commit #1: Documentation of Workflow

```
docs: document team github workflow and conventions

Adds WORKFLOW.md with complete documentation of:
- Branching strategy (feature branches, main protection, naming conventions)
- Commit message format and types (feat, fix, docs, refactor, chore)
- PR review process and approval requirements
- GitHub issue tracking approach
- Team responsibilities as contributors and reviewers

This document serves as the source of truth for how the team collaborates
on code and prevents merge conflicts in shared repositories.
```

---

## Commit #2: Feature - Data Validation

```
feat: add data validation function for CSV ingestion

Implements validation for incoming CSV files before pipeline processing.
Checks for schema completeness (required columns), data types, and null values.
Raises informative errors on invalid schemas.

Validation logic:
- Verify all required columns exist in incoming CSV
- Check data types match expected schema
- Count and report null values by column
- Generate validation report with pass/fail status

Used by data ingestion pipeline to ensure quality before processing.

Relates to: #1
```

---

## Commit #3: Data Quality Report Generator

```
feat: implement data quality report generator

Adds automated quality metrics reporting for incoming datasets.
Generates comprehensive quality report including:
- Schema validation results
- Missing value percentage by column
- Duplicate row detection
- Basic outlier detection for numeric columns
- Timestamp and dataset source

Reports are saved to data/processed/ with ISO timestamp for audit trail.
Enables team to track data quality metrics across ingestion events.

Relates to: #2
```

---

## Commit #4 (Optional): Requirements Update

```
chore: update requirements.txt with validation dependencies

Adds required packages for data validation and quality reporting:
- pandas (2.0+) for data manipulation
- pydantic (2.0+) for schema validation

These support the new validation and quality reporting features.
```

---

## Commit #5 (Optional): Data Dictionary

```
docs: add comprehensive data dictionary documentation

Documents all columns for datasets in warehouse:
- Column name, business definition, data type
- Valid value ranges and NULL handling
- Business rules and relationships

Updated README.md with data dictionary section for team reference.
Enables new team members to understand schema without asking questions.

Relates to: #3
```

---

## How to Use These

Each commit follows the format:
```
[type]: [description]

[optional body explaining why this matters]

[optional footer with issue references like "Relates to: #1"]
```

When you're ready to commit, use:

```bash
git add WORKFLOW.md
git commit -m "docs: document team github workflow and conventions

Adds WORKFLOW.md with complete documentation of:
- Branching strategy and naming conventions
- Commit message format and types
- PR review process
- GitHub issue tracking approach
[etc...]"
```

**Key Points:**
- First line under 72 characters ideally
- Blank line after title
- Body explains the "why"
- Reference related issues with "Relates to: #X"
- Use imperative mood: "add" not "added"

**Result:** 3-5 well-formed commits that tell the story of establishing your team workflow
