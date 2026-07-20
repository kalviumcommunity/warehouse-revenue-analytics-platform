# Product Requirements Document

**Product:** Warehouse Revenue Analytics Platform
**Repo:** github.com/kalviumcommunity/warehouse-revenue-analytics-platform
**Status:** v2 — reflects full pipeline + dashboard as built by the team
**Last updated:** 2026-07-20

---

## 1. Problem Statement

> A grocery delivery startup tracks order preparation time, packing accuracy, and
> delivery complaints, but operations leads cannot identify which warehouse
> workflows create the highest downstream failure rates.

That's the flagship question, but it sits on top of a broader problem: the
underlying data arrives messy and multi-format — CSV exports with inconsistent
encodings, nested JSON transaction logs, duplicate records, missing values,
currency strings instead of numbers, and outlier readings from WMS sync errors.
None of that can be trusted for KPI reporting or workflow-failure analysis
until it's been ingested, validated, cleaned, and structured consistently.
This project is both things: a data pipeline that makes the raw operational
data trustworthy, and a dashboard that uses the cleaned data to answer the
operations question directly.

## 2. Goals

| # | Goal | Evidence it's met |
|---|---|---|
| G1 | Turn raw, inconsistent multi-format exports into a reliable, typed dataset | Every pipeline stage writes an audit artifact to `output/` (intake report, dedup summary, dtype conversion log, imputation decisions, cleaning log, profile report) |
| G2 | Remove ambiguity from column meaning before anyone builds a KPI on top of it | `docs/DATA_DICTIONARY.md` and `docs/COLUMN_TO_KPI_MAPPING.md` define every column, valid ranges, and which KPI it feeds |
| G3 | Answer "which warehouse workflow fails most" in a way a non-technical operations lead can act on in seconds | The failure-risk dashboard (`frontend/`) surfaces one heatmap + two insight cards as the headline finding |
| G4 | Keep every pipeline decision explainable, not just automated | `handle_missing.py` and `outlier_detection.py` write out *why* each imputation/flag decision was made, not just that it happened |
| G5 | Ship something presentable to a mentor/reviewer with zero infrastructure setup | Dashboard is static HTML/CSS/JS — opens directly in a browser, no server or build step |

## 3. Users

| Persona | What they need from this project |
|---|---|
| **Operations Lead** (primary) | A single answer to which warehouse × workflow combination to fix first — the dashboard |
| **Warehouse Manager** | Their site's numbers in context against the other four warehouses |
| **Data Engineer / Contributor** (the team building this) | A modular pipeline where each stage (ingest, validate, dedupe, type, impute, profile, engineer features) can be worked on independently per `WORKFLOW.md`'s branch/PR process |
| **Mentor / Reviewer** | Confidence that every number traces back to documented logic, not guesswork |
| **Finance / Revenue stakeholder** | Revenue distribution and segment comparison view (in progress — see §6, pending merge) |

## 4. User Stories

1. As an **operations lead**, I want to see one chart that ranks every
   warehouse × workflow combination by failure risk, so I don't have to
   cross-reference three separate spreadsheets.
2. As an **operations lead**, I want the single riskiest combination called
   out explicitly, not just visible in a grid, so I know what to act on first.
3. As a **warehouse manager**, I want to see the three underlying signals
   (prep time, accuracy, complaints) broken out by workflow, so I understand
   *why* a workflow is flagged, not just that it is.
4. As a **reviewer**, I want a table view of the same data behind the
   heatmap, so I can check exact numbers instead of reading color.
5. As a **reviewer**, I want to know how the numbers were produced, so I can
   trust — or challenge — them.
6. As a **contributor**, I want each pipeline stage to write its own audit
   output (`output/*.json` / `*.csv`), so I can verify my stage worked
   correctly without re-running the whole pipeline.

## 5. Scope & Workflow

**In scope (v1)**
- The full data pipeline: ingestion → intake validation → string cleaning →
  deduplication → type enforcement → missing-value handling → outlier
  detection → profiling → feature engineering (see §6 for the stage-by-stage
  breakdown)
- The failure-risk dashboard as the pipeline's presentation layer
- Documented data dictionary and KPI mapping so no column meaning is guessed

**Out of scope (v1)**
- Real-time/live data ingestion (current data is a point-in-time snapshot)
- User authentication, roles, or multi-tenant access
- Editing or writing data back into the pipeline from the dashboard
- Customer-level LTV or churn analysis (scoped in the data dictionary, not built)
- Mobile-first layout (responsive to tablet width only)

**Team workflow** (per `WORKFLOW.md`)
- Main branch is releasable-only; all work happens on `feature/`, `fix/`,
  `docs/`, `refactor/`, or `chore/` branches
- Every change goes through a pull request with at least one approval before
  merging into `main`
- Commit messages follow `type: description` (`feat`, `fix`, `docs`,
  `refactor`, `test`, `chore`)
- Example in flight right now: `feature/revenue-distribution-analysis` is
  open, reviewed, and not yet merged — see §6, item 8b

## 6. Features

Built as a pipeline, stage by stage, each stage owned by a script with its own
audit output. This is the actual state of `main` as of this PRD, plus one
teammate contribution still on a feature branch.

| Stage | Script | What it does |
|---|---|---|
| 1. Multi-format ingestion | `scripts/ingest_data.py` | Reads CSV (with delimiter/encoding fallback) and nested JSON, flattens to tabular form, logs shape/dtypes/nulls |
| 2. Intake validation | `scripts/validate_intake.py` | Checks file existence, format, schema match against expected columns, encoding detection; writes `output/intake_report.json` |
| 3. String cleaning | `scripts/string_cleaning_pipeline.py` | Trims whitespace, normalizes casing, strips special characters, maps categorical variants (e.g. "b2b" / "B 2 B" → "B2B") |
| 4. Deduplication | `scripts/deduplicate_data.py` | Detects exact and near-duplicates (by business key), removes with a documented keep-strategy, logs every removed row to `output/removed_duplicates_audit.csv` |
| 5. Type enforcement | `scripts/enforce_types.py` | Casts dates, strips currency symbols to float, normalizes yes/no/1/0 to boolean; before/after dtype report |
| 6. Missing value handling | `scripts/handle_missing.py` | Drops rows missing critical identifiers, imputes numeric via median, categorical via mode, time-series via forward-fill — each strategy documented with business reasoning and risk level in `output/imputation_decisions.json` |
| 7. Outlier detection | `scripts/outlier_detection.py` | Flags outliers via combined z-score (±3) and IQR (1.5×) methods, never silently drops them |
| 8. Data profiling & quality scoring | `scripts/profile_data.py` | Null/duplicate rates, numerical stats, categorical distributions, severity-ranked quality issues with recommendations |
| 8b. Revenue distribution analysis *(pending merge — branch `feature/revenue-distribution-analysis`)* | `scripts/profile_data.py` (extended) | Skewness, kurtosis, percentile analysis, and segment comparison plots for revenue-like columns |
| 9. Feature engineering | `scripts/feature_engineering.py` | Computes `preparation_rate_per_hour`, `packing_accuracy_tier`, `delivery_complaint_quartile`, composite `warehouse_health_score`, and vectorized revenue normalization/z-score/rank (with a NumPy vs. loop benchmark) |
| 10. Failure-risk dashboard | `frontend/` (`index.html`, `styles.css`, `app.js`, `data.js`) | The presentation layer: failure-risk heatmap, KPI tiles, insight cards, and three evidence charts answering the flagship question |

## 7. Data Schema

Full definitions live in `docs/DATA_DICTIONARY.md`; KPI formulas in
`docs/COLUMN_TO_KPI_MAPPING.md`. Core order-level schema:

| Column | Type | Notes |
|---|---|---|
| `order_id` | int | primary key |
| `customer_id` | int | FK to customer |
| `warehouse_id` | string | `W1`–`W5` |
| `workflow_type` | string | `Picking`, `Packaging`, `Sorting`, `Packing` |
| `preparation_time_min` | float | >0, order-entry to completion |
| `packing_accuracy_pct` | float | 0–100 (values >100 are a known data-quality issue, rejected) |
| `delivery_complaints` | int | ≥0, filed within 7 days of delivery |
| `amount` | float | USD, order revenue |
| `status` | string | `completed`, `pending`, `cancelled`, `failed` — only `completed` counts as revenue |
| `signup_date` | date | ISO 8601, customer cohort |

Engineered columns added by `feature_engineering.py`:

| Column | Meaning |
|---|---|
| `preparation_rate_per_hour` | `60 / preparation_time_min` |
| `packing_accuracy_tier` | `low` / `medium` / `high` |
| `delivery_complaint_quartile` | `Q1`–`Q4` |
| `warehouse_health_score` | composite 0–100 score (accuracy + speed − complaint penalty); `100 −` this is the dashboard's "failure risk %" |

Known data quality issues (documented in the data dictionary, handled by the
pipeline stages above): `packing_accuracy_pct` values over 100, missing
`warehouse_id` on some orders, negative `preparation_time_min` from WMS clock
sync errors.

## 8. Dashboard Requirements

**Functional**
- One page, three sections: problem statement + KPIs → failure-risk heatmap +
  insight cards → three evidence charts (prep time, accuracy, complaint rate
  by workflow)
- Heatmap must have a non-color-dependent fallback (table-view toggle)
- Every chart mark has a hover tooltip with the underlying numbers
- The two extremes of the heatmap (highest-risk, safest combination) are
  called out explicitly, not left for the viewer to find

**Non-functional**
- Dark theme, committed (not toggled) — built for a presentation/projector context
- No framework, no backend — static HTML/CSS/vanilla JS, opens directly in a browser
- Zero browser console errors on load
- No dual-axis charts — different-unit measures always get separate charts
- Responsive down to tablet width
- Every number traceable to a formula in `docs/COLUMN_TO_KPI_MAPPING.md` or a
  named function in `feature_engineering.py` / the dataset generator

## 9. Success Metrics

**Pipeline (per-stage, already measured by each script's own output)**
- % of intake records passing schema validation (`output/intake_report.json`)
- Duplicate removal rate, with every removed row auditable (`output/dedup_summary.json`, `removed_duplicates_audit.csv`)
- Null resolution rate and imputation strategy coverage (`output/imputation_decisions.json`)
- Outlier flag rate by column (`output/cleaning_log.csv`)
- Data quality issues found, by severity (`output/profile_report.json`)

**Dashboard**
- A first-time viewer identifies the riskiest warehouse/workflow combination within 10 seconds, unassisted
- Zero console errors on load
- 100% of on-screen figures traceable to a documented formula or script

**Business (aspirational — once run against real, not synthetic, data)**
- Complaint rate drops for the flagged worst-performing workflow after the
  recommended intervention
- Warehouse health score trends toward the documented 85+ target across
  all five warehouses within one quarter of adopting the top performer's process
