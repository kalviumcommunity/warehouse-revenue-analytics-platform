# Data Dictionary

## Dataset Overview
This dataset contains warehouse order transaction records with customer information and operational metrics for a grocery delivery platform. Data is updated daily from the warehouse management system (WMS) and CRM system.

- **Last Updated**: 2025-06-16
- **Maintained By**: Data Engineering Team
- **Update Frequency**: Daily from WMS at 00:00 UTC
- **Primary Use**: Warehouse efficiency optimization, customer lifetime value analysis, and operational KPI tracking

---

## Columns

### order_id
- **Type**: Integer
- **Business Meaning**: Unique order identifier and transaction reference key
- **Example**: 1001
- **Null Handling**: Never null (primary key enforced at database level)
- **Related KPIs**: Order volume tracking, completion rate, customer order count
- **Updates**: Auto-assigned at order creation in WMS
- **Constraints**: Must be unique, positive integer
- **Business Impact**: Used for order tracking, revenue reconciliation, and audit trails

### customer_id
- **Type**: Integer
- **Business Meaning**: Customer master data link for revenue attribution and churn analysis
- **Example**: 1
- **Null Handling**: Very rare - investigate immediately if found (indicates WMS orphaned order)
- **Related KPIs**: Customer lifetime value, revenue attribution, cohort analysis, churn rate
- **Updates**: Set at order creation from CRM system
- **Constraints**: Must reference valid customer record
- **Business Impact**: Critical for understanding revenue by customer segment, customer profitability, and retention metrics

### warehouse_id
- **Type**: String
- **Business Meaning**: Physical warehouse facility code where order was processed
- **Example**: W1, W2, W3
- **Valid Values**: W1, W2, W3, W4, W5
- **Null Handling**: If null, classify order as "SYSTEM_ERROR" and flag for investigation
- **Related KPIs**: Warehouse efficiency score, preparation velocity by facility, accuracy by warehouse
- **Updates**: Set by WMS when order assigned to warehouse queue
- **Constraints**: Must reference active warehouse in facility master
- **Business Impact**: Enables warehouse-level performance benchmarking and bottleneck identification

### amount
- **Type**: Float
- **Business Meaning**: Revenue from single order in USD currency
- **Example**: 150.50
- **Unit**: USD (always in dollars, never cents alone)
- **Null Handling**: Very rare - if null and status='completed', treat as data error and investigate
- **Related KPIs**: Monthly revenue, segment revenue, customer lifetime value, average order value
- **Updates**: Set at order checkout before warehouse processing
- **Constraints**: Must be positive, typically $10-500 range
- **Business Impact**: Foundation of revenue calculations - type errors here corrupt all financial reporting

### status
- **Type**: String
- **Business Meaning**: Current fulfillment state of order through processing pipeline
- **Example**: completed, pending, failed, cancelled
- **Valid Values**: completed, pending, failed, cancelled
- **Null Handling**: If null, treat as "unknown" and flag for WMS troubleshooting
- **Related KPIs**: Order completion rate, revenue recognition (only "completed" counts), failure analysis
- **Updates**: Updated as order moves through warehouse workflow stages
- **Constraints**: Must be one of the valid values
- **Business Impact**: Critical for revenue recognition - only "completed" orders count toward revenue KPIs

### workflow_type
- **Type**: String
- **Business Meaning**: Type of warehouse operation/process executed for this order
- **Example**: Picking, Packaging, Sorting, Packing
- **Valid Values**: Picking, Packaging, Sorting, Packing
- **Null Handling**: If null, classify as "UNKNOWN_WORKFLOW" and research which process failed
- **Related KPIs**: Workflow-specific preparation velocity, accuracy by process type, process failure rates
- **Updates**: Set when order enters that stage of warehouse workflow
- **Constraints**: Must be one of the valid process types
- **Business Impact**: Enables root-cause analysis of bottlenecks - different workflows have different performance targets

### preparation_time_min
- **Type**: Float
- **Business Meaning**: Elapsed minutes from order entry to completion at warehouse
- **Example**: 18.5, 22.0, 25.0
- **Unit**: Minutes (decimal for sub-minute precision)
- **Null Handling**: If null, order may be incomplete - flag for investigation
- **Related KPIs**: Order preparation velocity, workflow efficiency, warehouse capacity planning
- **Updates**: Auto-calculated at WMS order completion
- **Constraints**: Must be positive (>0), typically 15-45 minute range
- **Business Impact**: Directly impacts customer experience and warehouse utilization - values >45 indicate bottlenecks

### packing_accuracy_pct
- **Type**: Float
- **Business Meaning**: Percentage of items in order packed correctly without errors
- **Example**: 98.5, 96.0, 92.0
- **Unit**: Percentage (0-100, ideally 95%+ for customer satisfaction)
- **Null Handling**: If null, flag as incomplete packing verification - investigate
- **Related KPIs**: Packing accuracy rate, defect rate, customer complaint correlation
- **Updates**: Set by quality assurance checklist during packing completion
- **Constraints**: Should be 0-100%, values >100% indicate data quality errors (reject these)
- **Data Quality Issues**: Values >100 found in raw data - indicates QA process error, must be cleaned
- **Business Impact**: Strong predictor of customer satisfaction and delivery complaints

### delivery_complaints
- **Type**: Integer
- **Business Meaning**: Count of customer complaints received for this order
- **Example**: 0, 1, 2, 3+
- **Null Handling**: If null, treat as 0 (no complaint filed)
- **Related KPIs**: Complaint rate, customer satisfaction, order quality score
- **Updates**: Incremented when customer files complaint within 7 days of delivery
- **Constraints**: Must be non-negative integer (0, 1, 2, 3...)
- **Business Impact**: Lagging indicator of quality - higher values trigger warehouse process review

### signup_date
- **Type**: Datetime (ISO 8601 format YYYY-MM-DD)
- **Business Meaning**: Date customer account was created in CRM system
- **Example**: 2025-01-15
- **Format**: YYYY-MM-DD (always UTC, never localized)
- **Null Handling**: Never null - required at account creation
- **Related KPIs**: Customer acquisition rate, customer tenure, cohort analysis
- **Updates**: Set once at customer creation, never changes
- **Constraints**: Cannot be future date, typically within last 2 years
- **Business Impact**: Foundation for customer cohort analysis and tenure-based segmentation

### name
- **Type**: String
- **Business Meaning**: Customer full name for business communication
- **Example**: Alice Johnson, Bob Smith
- **Null Handling**: Can be null for anonymized/test accounts
- **Related KPIs**: Customer segmentation, communication targeting
- **Updates**: Set at signup, can be updated by customer
- **Constraints**: Maximum 100 characters, alphanumeric + spaces
- **Business Impact**: Used for personalization in customer communications

---

## Column to KPI Mapping

### Monthly Revenue
- **Formula**: `SUM(amount)` WHERE status='completed' AND DATE_TRUNC(signup_date, MONTH) = current_month
- **Related Columns**: amount, status, signup_date, order_id
- **Why It Matters**: Primary revenue KPI - tracks total company revenue and forecasting baseline
- **Update Frequency**: Daily (cumulative through month)
- **Target**: Revenue trending upward month-over-month
- **Data Dependencies**: amount must never be null, status must be 'completed'

### Order Preparation Velocity
- **Formula**: `AVG(preparation_time_min)` grouped by warehouse_id, workflow_type
- **Related Columns**: preparation_time_min, warehouse_id, workflow_type
- **Why It Matters**: Identifies which warehouses/workflows are efficient vs. bottlenecked
- **Update Frequency**: Daily (recalculate for last 30 days)
- **Target**: Target <20 minutes for Picking, <15 minutes for Packaging
- **Data Dependencies**: preparation_time_min must be positive
- **Benchmark**: Warehouses >25 min average trigger operational review

### Packing Accuracy Rate
- **Formula**: `AVG(packing_accuracy_pct)` grouped by warehouse_id, workflow_type
- **Related Columns**: packing_accuracy_pct, warehouse_id, workflow_type
- **Why It Matters**: Quality metric - directly impacts customer satisfaction and complaint rate
- **Update Frequency**: Daily (recalculate for last 30 days)
- **Target**: 98%+ accuracy across all warehouses
- **Data Dependencies**: packing_accuracy_pct must be 0-100%, reject values >100%
- **Action Threshold**: <95% triggers warehouse quality investigation

### Complaint Rate by Order
- **Formula**: `AVG(delivery_complaints)` grouped by warehouse_id, workflow_type
- **Related Columns**: delivery_complaints, warehouse_id, workflow_type
- **Why It Matters**: Customer satisfaction indicator - predicts churn and retention risk
- **Update Frequency**: Weekly (7-day rolling window)
- **Target**: <0.5 complaints per order average
- **Data Dependencies**: delivery_complaints must be non-negative
- **Correlation**: Strong negative correlation with packing_accuracy_pct

### Customer Lifetime Value
- **Formula**: `SUM(amount)` WHERE status='completed' grouped by customer_id
- **Related Columns**: customer_id, amount, status, signup_date
- **Why It Matters**: Identifies high-value customers for retention investment and upsell
- **Update Frequency**: Daily (cumulative for each customer)
- **Target**: Track top 10% customers (generate 50%+ of revenue)
- **Segmentation**: Top tier >$1000 LTV, Mid tier $100-1000, Low tier <$100
- **Business Action**: Top tier customers get premium service, retention focus

### Warehouse Efficiency Score
- **Formula**: `(packing_accuracy_pct * 0.6 + (60 - MIN(preparation_time_min, 60)) / 60 * 100 * 0.4) - (delivery_complaints * 5)`
- **Related Columns**: packing_accuracy_pct, preparation_time_min, delivery_complaints, warehouse_id
- **Why It Matters**: Composite warehouse performance metric for comparison and benchmarking
- **Update Frequency**: Weekly
- **Target**: Score >85 for all warehouses
- **Benchmark**: Highest score warehouse = best-in-class operations model

---

## Ambiguous Columns & Resolutions

### Column: workflow_type
- **Original Ambiguity**: Is this the type of work OR the current workflow step? Does "Packing" mean the packing stage or type of work? How does it differ from "Packaging"?
- **Resolved Meaning**: Specific warehouse process stage/type where order is currently being processed. "Picking" = item selection from inventory. "Packaging" = boxing and wrap. "Packing" = additional protective packing (synonym for Packaging). "Sorting" = order consolidation and routing.
- **Business Interpretation**: Enables performance targeting by process - each workflow has different efficiency targets, SLA, and quality metrics
- **Proposed Rename**: `order_processing_stage` (more explicit that this is current stage, not order type)
- **Risk If Misunderstood**: Could mix up order type (e.g., "bulk_order", "fragile_order") with process stage, leading to wrong performance metrics applied

### Column: packing_accuracy_pct
- **Original Ambiguity**: Does this measure accuracy of packing only, or the entire order fulfillment accuracy? Are missing items vs. wrong items both captured? Does it measure what was packed vs. what customer received?
- **Resolved Meaning**: Percentage of items that were correctly packed in the warehouse (pre-delivery). Measures: correct item included, correct quantity, correct positioning. Does NOT measure delivery damage (that's post-delivery). Calculated as (items_correct / items_ordered * 100).
- **Business Interpretation**: Warehouse quality metric - identifies packing process failures before delivery. Strong predictor of customer complaints.
- **Proposed Rename**: `warehouse_packing_accuracy_pct` (clarifies it's warehouse accuracy, not delivery accuracy)
- **Risk If Misunderstood**: If confused with post-delivery accuracy, teams could blame delivery/logistics for warehouse failures, leading to misallocated improvement efforts

### Column: delivery_complaints
- **Original Ambiguity**: What types of complaints does this count? Does it include only packing complaints or also delivery timing, driver behavior, package damage? Is this complaints filed OR complaints acknowledged?
- **Resolved Meaning**: Count of customer-filed complaints within 7 days of order delivery. Includes: items missing/wrong, damaged items, quality issues. Excludes: delivery timing, driver behavior (those are separate channels). Only counts complaints that received ticket number (filed, not just mentions).
- **Business Interpretation**: Quality complaint metric - correlates heavily with packing accuracy. Used for root-cause analysis of warehouse process failures.
- **Proposed Rename**: `packing_related_complaints_7d` (clarifies scope: packing-related only, 7-day window, filed)
- **Risk If Misunderstood**: Could include non-warehouse complaints (e.g., "driver was rude") and bias warehouse improvement efforts toward wrong problems

### Column: status
- **Original Ambiguity**: Does "completed" mean order was delivered to customer OR just finished warehouse processing? Are cancelled and failed different or synonymous?
- **Resolved Meaning**: "completed" = entire order-to-delivery workflow finished successfully. "pending" = still in warehouse or in transit. "failed" = warehouse process error (items misplaced, couldn't fulfill). "cancelled" = customer cancelled before fulfillment or order rejected.
- **Business Interpretation**: Revenue recognition status - only "completed" counts toward revenue. "pending" are at-risk. "failed"/"cancelled" are lost revenue and require investigation.
- **Proposed Rename**: `order_fulfillment_status` (more explicit than generic "status")
- **Risk If Misunderstood**: Revenue could be overstated if "pending" is counted as revenue, or understated if "completed" interpreted as just warehouse completion

---

## Column Relationships

### Revenue per Customer by Cohort
- **Definition**: `SUM(amount)` WHERE status='completed' grouped by customer_id AND DATE_TRUNC(signup_date, MONTH)
- **Columns Involved**: customer_id, amount, status, signup_date
- **How It Matters**: Identifies which customer acquisition cohorts generate highest lifetime value and retention patterns. January cohort vs February cohort may have different behavior patterns.
- **Example**: "Customers acquired in January 2025 show 15% higher lifetime value than February cohort"
- **Business Action**: If cohort LTV correlates with acquisition channel, optimize marketing budget toward better-performing channels
- **Calculation Frequency**: Monthly

### Warehouse Quality Impact on Customer Lifetime Value
- **Definition**: Correlation between `AVG(packing_accuracy_pct)` by warehouse_id and `AVG(SUM(amount))` by customer_id when customer's order is processed at that warehouse
- **Columns Involved**: packing_accuracy_pct, warehouse_id, customer_id, amount, delivery_complaints
- **How It Matters**: Demonstrates whether warehouse quality directly impacts customer repeat purchases and spending. High-accuracy warehouse customers spend more (higher retention).
- **Example**: "Customers served by W1 (98.5% accuracy) spend 30% more on average than customers served by W3 (85% accuracy)"
- **Business Action**: If correlation is strong, quality improvement at low-accuracy warehouses becomes revenue priority, not just operational metric
- **Hidden Risk**: If warehouse assignments are correlated with customer segment (premium customers go to better warehouse), this correlation is confounded

### Order Velocity vs. Complaint Rate
- **Definition**: Correlation between `preparation_time_min` and `delivery_complaints` by workflow_type
- **Columns Involved**: preparation_time_min, delivery_complaints, workflow_type
- **How It Matters**: Identifies whether rushing orders (faster prep time) increases quality failures. Trade-off between speed and accuracy.
- **Example**: "Picking workflow: orders <15 min avg 0.2 complaints vs orders >25 min avg 0.8 complaints" - suggests rushing causes mistakes
- **Business Action**: If positive correlation, establishes SLA speed targets based on quality constraints, not arbitrary targets
- **Optimization Trade-off**: Cannot minimize preparation_time without quality impact - need to find optimal balance

### Warehouse Efficiency Score Trending
- **Definition**: Time-series of warehouse_efficiency_score by warehouse_id over 90-day rolling window
- **Columns Involved**: packing_accuracy_pct, preparation_time_min, delivery_complaints, warehouse_id
- **How It Matters**: Identifies which warehouses are improving vs. degrading. Declining efficiency may indicate staffing issues, process drift, or system problems.
- **Example**: "W2 efficiency declining 2 points/week over last month - investigation revealed new staff onboarding in progress"
- **Business Action**: Early warning system for operational problems before they become critical
- **Benchmark Comparison**: Compare each warehouse to best-performing warehouse to identify process improvement opportunities

---

## Data Quality Standards

### Critical Columns (never null)
- order_id: Primary key
- customer_id: Revenue attribution
- amount: Revenue calculation
- status: Revenue recognition
- signup_date: Cohort analysis

### Validation Rules
- preparation_time_min must be positive (>0) or null
- packing_accuracy_pct must be 0-100 range (reject >100)
- delivery_complaints must be non-negative integer
- amount must be positive
- status must be one of: completed, pending, failed, cancelled

### Known Data Quality Issues
- Some orders have packing_accuracy_pct >100 (data error from QA system)
- Some orders missing warehouse_id (system failures)
- Some orders have negative preparation_time_min (time sync errors in WMS)

### Data Governance
- All data retained for 24 months minimum (regulatory requirement)
- Customer PII (name, email) governed by privacy policy
- Order data belongs to customer - must honor deletion requests
- Aggregated data (KPIs) retained indefinitely

---

## Related Documentation
- See `data_workflow.py` for data ingestion logic
- See `validate_intake.py` for validation rules
- See `profile_data.py` for profiling output
- See `WORKFLOW.md` for data pipeline stages
