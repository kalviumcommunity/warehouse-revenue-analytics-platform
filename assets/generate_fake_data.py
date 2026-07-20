"""
Fake data generator - warehouse-revenue-analytics-platform.

Adapted from a generator sourced outside this repo. Generation logic
(order volume, per-warehouse bias, distributions) is kept close to the
original; the payload builder was rewritten to match the schema
frontend/app.js already reads, so the dashboard needs no rework.

Outputs:
    output/dashboard_orders.csv   (order-level + generated features)
    output/dashboard_payload.json (same payload written to frontend/data.js)
    frontend/data.js              (window.DASHBOARD_DATA = {...})

Run:
    python assets/generate_fake_data.py
"""
import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

N_ORDERS = 2000
WAREHOUSES = ["W1", "W2", "W3", "W4", "W5"]
WORKFLOWS = ["Picking", "Packaging", "Sorting", "Packing"]
STATUSES = ["completed", "pending", "cancelled", "failed"]
STATUS_WEIGHTS = [0.72, 0.12, 0.09, 0.07]

# per-warehouse skew, so the dashboard has visible variance
WH_HEALTH_BIAS = {"W1": 0.05, "W2": -0.10, "W3": 0.02, "W4": 0.08, "W5": -0.15}

# per-workflow skew: Picking (single-item) is least error-prone, Sorting
# (consolidation/routing across orders) is most error-prone. Without this,
# workflow_type has no effect on any metric and the "which workflow fails
# most" question the dashboard exists to answer has no signal to show.
WORKFLOW_DIFFICULTY_BIAS = {"Picking": 0.06, "Packaging": 0.00, "Packing": -0.03, "Sorting": -0.09}

START_SIGNUP = datetime(2023, 1, 1)
END_SIGNUP = datetime(2026, 6, 30)

REPO_ROOT = Path(__file__).resolve().parent.parent


def rand_signup_date():
    delta_days = (END_SIGNUP - START_SIGNUP).days
    return START_SIGNUP + timedelta(days=random.randint(0, delta_days))


def gen_raw_orders(n):
    rows = []
    for order_id in range(1, n + 1):
        warehouse_id = random.choice(WAREHOUSES)
        workflow_type = random.choice(WORKFLOWS)
        bias = WH_HEALTH_BIAS[warehouse_id] + WORKFLOW_DIFFICULTY_BIAS[workflow_type]
        status = random.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0]

        prep_time = max(2.0, random.gauss(18 - bias * 20, 5))
        accuracy = min(100.0, max(60.0, random.gauss(94 + bias * 30, 4)))
        complaints = max(0, int(random.gauss(1.2 - bias * 4, 1.3)))
        amount = round(random.uniform(15, 850), 2)
        revenue = round(amount, 2) if status == "completed" else None

        rows.append({
            "order_id": order_id,
            "customer_id": random.randint(1000, 4500),
            "warehouse_id": warehouse_id,
            "workflow_type": workflow_type,
            "preparation_time_min": round(prep_time, 2),
            "packing_accuracy_pct": round(accuracy, 2),
            "delivery_complaints": complaints,
            "amount": amount,
            "status": status,
            "signup_date": rand_signup_date().strftime("%Y-%m-%d"),
            "revenue": revenue,
        })
    return rows


def accuracy_tier(pct):
    if pct >= 97:
        return "Excellent"
    if pct >= 92:
        return "Good"
    if pct >= 85:
        return "Fair"
    return "Poor"


def add_generated_features(rows):
    complaints_sorted = sorted(r["delivery_complaints"] for r in rows)

    def quartile(v):
        idx = 0
        for i, c in enumerate(complaints_sorted):
            if c <= v:
                idx = i
        pct = idx / max(1, len(complaints_sorted) - 1)
        if pct <= 0.25:
            return "Q1"
        if pct <= 0.5:
            return "Q2"
        if pct <= 0.75:
            return "Q3"
        return "Q4"

    for r in rows:
        prep_hr = 60.0 / r["preparation_time_min"] if r["preparation_time_min"] else 0.0
        r["preparation_rate_per_hour"] = round(prep_hr, 2)
        r["packing_accuracy_tier"] = accuracy_tier(r["packing_accuracy_pct"])
        r["delivery_complaint_quartile"] = quartile(r["delivery_complaints"])

        r["packing_accuracy_score"] = round(r["packing_accuracy_pct"] / 100 * 10, 2)
        r["preparation_speed_score"] = round(min(10, prep_hr / 4), 2)
        r["delivery_complaint_score"] = round(max(0, 10 - r["delivery_complaints"] * 2.5), 2)
        r["workflow_failure_score"] = round(
            10 if r["status"] in ("failed", "cancelled") else (5 if r["status"] == "pending" else 0), 2
        )
        # Weighted sum of four 0-10 subscores lands in 0-10; scale to 0-100
        # so it's on the same scale as every other health/efficiency score
        # documented in docs/COLUMN_TO_KPI_MAPPING.md.
        r["warehouse_health_score"] = round(
            (r["packing_accuracy_score"] * 0.35
             + r["preparation_speed_score"] * 0.25
             + r["delivery_complaint_score"] * 0.25
             + (10 - r["workflow_failure_score"]) * 0.15)
            * 10,
            1,
        )
    return rows


def avg(vals):
    vals = list(vals)
    return round(sum(vals) / len(vals), 2) if vals else 0.0


def build_dashboard_payload(rows):
    completed = [r for r in rows if r["status"] == "completed"]
    total_orders = len(rows)
    total_complaints = sum(r["delivery_complaints"] for r in rows)

    by_warehouse = []
    for wid in WAREHOUSES:
        g = [r for r in rows if r["warehouse_id"] == wid]
        g_completed = [r for r in g if r["status"] == "completed"]
        g_complaints = sum(r["delivery_complaints"] for r in g)
        by_warehouse.append({
            "warehouse_id": wid,
            "orders": len(g),
            "revenue": round(sum(r["revenue"] or 0 for r in g_completed), 2),
            "avgPrepTimeMin": avg(r["preparation_time_min"] for r in g),
            "avgPackingAccuracyPct": avg(r["packing_accuracy_pct"] for r in g),
            "complaintRatePerOrder": round(g_complaints / len(g), 3) if g else 0.0,
            "avgWarehouseHealthScore": avg(r["warehouse_health_score"] for r in g),
        })

    by_workflow = []
    for wf in WORKFLOWS:
        g = [r for r in rows if r["workflow_type"] == wf]
        g_complaints = sum(r["delivery_complaints"] for r in g)
        by_workflow.append({
            "workflow_type": wf,
            "orders": len(g),
            "avgPrepTimeMin": avg(r["preparation_time_min"] for r in g),
            "avgPackingAccuracyPct": avg(r["packing_accuracy_pct"] for r in g),
            "complaintRatePerOrder": round(g_complaints / len(g), 3) if g else 0.0,
            "avgWarehouseHealthScore": avg(r["warehouse_health_score"] for r in g),
        })

    matrix = []
    for wid in WAREHOUSES:
        for wf in WORKFLOWS:
            cell = [r for r in rows if r["warehouse_id"] == wid and r["workflow_type"] == wf]
            cell_complaints = sum(r["delivery_complaints"] for r in cell)
            health = avg(r["warehouse_health_score"] for r in cell)
            matrix.append({
                "warehouse_id": wid,
                "workflow_type": wf,
                "orders": len(cell),
                "avgPrepTimeMin": avg(r["preparation_time_min"] for r in cell),
                "avgPackingAccuracyPct": avg(r["packing_accuracy_pct"] for r in cell),
                "complaintRatePerOrder": round(cell_complaints / len(cell), 3) if cell else 0.0,
                "avgWarehouseHealthScore": health,
                "failureRiskPct": round(100 - health, 1),
            })

    riskiest = max(matrix, key=lambda m: m["failureRiskPct"])
    safest = min(matrix, key=lambda m: m["failureRiskPct"])

    def combo_summary(m):
        return {
            "warehouse": m["warehouse_id"],
            "workflow": m["workflow_type"],
            "failureRiskPct": m["failureRiskPct"],
            "complaintRatePerOrder": m["complaintRatePerOrder"],
            "avgPackingAccuracyPct": m["avgPackingAccuracyPct"],
            "avgPrepTimeMin": m["avgPrepTimeMin"],
        }

    overall = {
        "totalOrders": total_orders,
        "completedOrders": len(completed),
        "totalRevenue": round(sum(r["revenue"] or 0 for r in completed), 2),
        "avgPrepTimeMin": avg(r["preparation_time_min"] for r in rows),
        "avgPackingAccuracyPct": avg(r["packing_accuracy_pct"] for r in rows),
        "complaintRatePerOrder": round(total_complaints / total_orders, 3) if total_orders else 0.0,
        "avgWarehouseHealthScore": avg(r["warehouse_health_score"] for r in rows),
    }

    return {
        "generatedAt": datetime.now().date().isoformat(),
        "warehouses": WAREHOUSES,
        "workflows": WORKFLOWS,
        "overall": overall,
        "byWarehouse": by_warehouse,
        "byWorkflow": by_workflow,
        "matrix": matrix,
        "insights": {
            "riskiestCombo": combo_summary(riskiest),
            "safestCombo": combo_summary(safest),
        },
    }


if __name__ == "__main__":
    rows = gen_raw_orders(N_ORDERS)
    rows = add_generated_features(rows)

    output_dir = REPO_ROOT / "output"
    output_dir.mkdir(exist_ok=True)
    frontend_dir = REPO_ROOT / "frontend"
    frontend_dir.mkdir(exist_ok=True)

    csv_path = output_dir / "dashboard_orders.csv"
    fieldnames = list(rows[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    payload = build_dashboard_payload(rows)

    json_path = output_dir / "dashboard_payload.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    data_js_path = frontend_dir / "data.js"
    with open(data_js_path, "w", encoding="utf-8") as f:
        f.write("window.DASHBOARD_DATA = " + json.dumps(payload, indent=2) + ";\n")

    print(f"[SUCCESS] Wrote {csv_path} ({len(rows)} rows)")
    print(f"[SUCCESS] Wrote {json_path}")
    print(f"[SUCCESS] Wrote {data_js_path}")
    print(
        f"orders={payload['overall']['totalOrders']} "
        f"completed={payload['overall']['completedOrders']} "
        f"revenue={payload['overall']['totalRevenue']}"
    )
