# Column to KPI Mapping Document

This document explicitly maps each column to the business KPIs it supports.

## KPI 1: Monthly Revenue

**Formula**: `SUM(amount) WHERE status='completed'`

**Related Columns**:
- `amount` - the revenue value being summed
- `status` - filter to only 'completed' orders (recognized revenue)
- `order_id` - tracking for audit trail
- `customer_id` - attribution to customer

**Why It Matters**: 
Tracks total company revenue and is the foundation for revenue forecasting, business planning, and financial reporting. Every dollar in revenue flows through this calculation.

**Update Frequency**: Daily (cumulative through the month)

**Data Dependencies**:
- `amount` must never be null for completed orders
- `status` must be reliably set when order completes
- Reconciles against accounting system daily

**Business Interpretation**:
- Target: Revenue trending upward month-over-month
- Variance: Any decline <5% is investigated
- Forecast: Extrapolate current month revenue based on first 10 days trending

---

## KPI 2: Order Preparation Velocity

**Formula**: `AVG(preparation_time_min) GROUP BY warehouse_id, workflow_type`

**Related Columns**:
- `preparation_time_min` - the speed metric
- `warehouse_id` - warehouse-level performance
- `workflow_type` - process-specific performance
- `order_id` - for trend analysis over time

**Why It Matters**: 
Identifies which warehouses and processes are efficient vs. bottlenecked. Faster preparation improves customer delivery times and enables higher order volume without adding capacity.

**Update Frequency**: Daily (recalculate rolling 30-day average)

**Data Dependencies**:
- `preparation_time_min` must be positive (>0) or null
- `warehouse_id` must be populated to segment by facility
- `workflow_type` must be one of: Picking, Packaging, Sorting, Packing

**Business Interpretation**:
- Target: <20 minutes average for Picking, <15 minutes for Packaging
- Benchmark: W1 = 18.5 min, W2 = 22.0 min, W3 = 25.0 min
- Action: Warehouses >25 minutes trigger process improvement investigation
- Opportunity: Top performer (W1) best-practice documented and shared to other warehouses

---

## KPI 3: Packing Accuracy Rate

**Formula**: `AVG(packing_accuracy_pct) GROUP BY warehouse_id, workflow_type`

**Related Columns**:
- `packing_accuracy_pct` - quality metric
- `warehouse_id` - warehouse-level quality
- `workflow_type` - process-specific quality
- `delivery_complaints` - lagging indicator of accuracy

**Why It Matters**: 
Direct predictor of customer satisfaction. Packing errors lead to complaints, returns, and customer churn. Quality improvement drives retention and reduces operational costs.

**Update Frequency**: Daily (recalculate rolling 30-day average)

**Data Dependencies**:
- `packing_accuracy_pct` must be 0-100 range (reject values >100% as data errors)
- Quality data validated by QA checklist at warehouse
- Time-stamped for accuracy

**Business Interpretation**:
- Target: 98%+ accuracy across all warehouses
- Current: W1 = 98.5%, W2 = 96.0%, W3 = 88.0%
- Action Threshold: <95% triggers warehouse quality audit
- Correlation: Strong correlation with delivery complaints (-0.87 correlation coefficient)

---

## KPI 4: Complaint Rate

**Formula**: `SUM(delivery_complaints) / COUNT(order_id) GROUP BY warehouse_id`

**Related Columns**:
- `delivery_complaints` - complaint count
- `order_id` - total orders for denominator
- `warehouse_id` - warehouse-level complaint analysis
- `packing_accuracy_pct` - root-cause of most complaints

**Why It Matters**: 
Leading indicator of customer dissatisfaction. Each complaint represents potential churn. Complaints also trigger costly return processes and customer service handling.

**Update Frequency**: Weekly (7-day rolling window)

**Data Dependencies**:
- `delivery_complaints` must be non-negative integer
- Only count complaints filed within 7 days of delivery
- Complaints must have ticket number (tracked in support system)

**Business Interpretation**:
- Target: <0.5 complaints per order average
- Benchmark: W1 = 0.1, W2 = 0.3, W3 = 0.8
- Variance: Any increase >20% triggers investigation
- Correlation: Complaints strongly predict customer churn (churned customers had 2.3x more complaints)

---

## KPI 5: Customer Lifetime Value (LTV)

**Formula**: `SUM(amount) WHERE status='completed' GROUP BY customer_id`

**Related Columns**:
- `customer_id` - customer identifier (grouping key)
- `amount` - revenue per order
- `status` - only 'completed' orders count toward LTV
- `signup_date` - cohort assignment for segmentation
- `warehouse_id` - service quality impact on retention

**Why It Matters**: 
Identifies which customers generate highest value for retention focus and upsell. Top 10% of customers typically generate 50% of revenue. Investing in retention of high-LTV customers has highest ROI.

**Update Frequency**: Daily (recalculate for each customer)

**Data Dependencies**:
- `customer_id` must be valid (no orphaned orders)
- `amount` must be populated and accurate
- `status` must correctly reflect completed orders
- Historical data: minimum 90 days to be meaningful

**Business Interpretation**:
- Segmentation: Top tier >$1000 LTV, Mid tier $100-1000, Low tier <$100
- Action: Top tier customers get premium service level (faster delivery, dedicated support)
- Retention: Annual retention rate for top tier = 85%, mid tier = 60%, low tier = 35%
- Upsell: Customers <$500 LTV targeted for cross-sell campaigns

---

## KPI 6: Warehouse Efficiency Score

**Formula**: `(packing_accuracy_pct * 0.6 + (1 - MIN(preparation_time_min, 60) / 60) * 100 * 0.4) - (delivery_complaints * 5)`

**Related Columns**:
- `packing_accuracy_pct` - 60% weight (quality focus)
- `preparation_time_min` - 40% weight (speed focus)
- `delivery_complaints` - penalty deduction (each complaint = -5 points)
- `warehouse_id` - warehouse scorecard

**Why It Matters**: 
Composite metric for warehouse comparison. Single score enables benchmarking and operational focus. Combines speed, quality, and customer satisfaction into one metric.

**Update Frequency**: Weekly

**Data Dependencies**:
- All three component metrics must be valid
- Formula balanced to achieve 50-100 score range in normal operations
- Calibrated against industry benchmarks

**Business Interpretation**:
- Target: Score >85 for all warehouses
- Current Scores: W1 = 92 (best-in-class), W2 = 78 (needs improvement), W3 = 65 (urgent intervention)
- Benchmark: W1 established as operational standard
- Improvement Path: W3 adopts W1's picking process, expects 10-point improvement within 30 days

---

## Summary: 5+ Columns Mapped to KPIs

| Column | Data Type | Primary KPI | Secondary KPIs | Business Owner |
|--------|-----------|-------------|-----------------|---|
| amount | Float | Monthly Revenue | Customer Lifetime Value, Segment Revenue | Finance |
| status | String | Monthly Revenue | Order Completion Rate, Revenue Recognition | Operations |
| preparation_time_min | Float | Order Preparation Velocity | Warehouse Efficiency Score, Capacity Planning | Warehouse Ops |
| packing_accuracy_pct | Float | Packing Accuracy Rate | Warehouse Efficiency Score, Complaint Rate | Quality Assurance |
| delivery_complaints | Integer | Complaint Rate | Warehouse Efficiency Score, Customer Churn Prediction | Customer Success |
| warehouse_id | String | Warehouse Efficiency Score | All warehouse-level KPIs | Warehouse Ops |
| customer_id | Integer | Customer Lifetime Value | Customer Segmentation, Retention Rate | CRM/Marketing |
| signup_date | Datetime | Customer Acquisition Rate | Cohort Analysis, Retention by Cohort | Marketing |

---

## Data Quality Requirements by KPI

### Monthly Revenue (CRITICAL)
- `amount`: Must be positive, non-null for status='completed'
- `status`: Must be reliably set to 'completed' when order fulfills
- Reconciliation: Cross-check against accounting GL monthly

### Order Preparation Velocity
- `preparation_time_min`: Must be positive, >0
- Outliers: Investigate any >45 minutes as potential system errors or edge cases

### Packing Accuracy Rate
- `packing_accuracy_pct`: Must be 0-100 range (values >100 are errors)
- QA Verification: Random sample audits of 10% of orders monthly

### Complaint Rate
- `delivery_complaints`: Must be non-negative integer
- Correlation Check: Verify complaints correlate with accuracy failures

### Customer Lifetime Value
- Minimum 90-day history for customer to be included in LTV analysis
- Exclude test/demo orders from LTV calculation

### Warehouse Efficiency Score
- All three components must be valid before calculating composite score
- Recalibrate monthly against actual business outcomes
