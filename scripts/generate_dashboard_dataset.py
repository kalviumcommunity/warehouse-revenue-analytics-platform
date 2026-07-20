"""
Generate a demo order-level dataset for the operations dashboard.

This script does NOT fabricate dashboard numbers by hand. It builds a
synthetic but internally-consistent order-level dataset calibrated against
the benchmarks documented in docs/COLUMN_TO_KPI_MAPPING.md (W1/W2/W3 speed,
accuracy, and complaint figures), extends the same warehouse-quality /
workflow-difficulty model to W4-W5, and then runs the dataset through the
project's own scripts/feature_engineering.py so every score shown on the
dashboard is produced by the same pipeline code used elsewhere in this repo.

Run:
    python scripts/generate_dashboard_dataset.py

Output:
    frontend/data.js  (window.DASHBOARD_DATA = {...})
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from feature_engineering import engineer_operational_features  # noqa: E402

RNG = np.random.default_rng(42)

WAREHOUSES = ["W1", "W2", "W3", "W4", "W5"]
# Quality/risk multiplier per warehouse. W1-W3 calibrated to the documented
# benchmarks (prep time, accuracy, complaints, efficiency score); W4/W5
# interpolated using the same model to round out the demo fleet.
WAREHOUSE_RISK = {"W1": 1.00, "W2": 1.35, "W3": 1.85, "W4": 1.15, "W5": 1.55}

WORKFLOWS = ["Picking", "Packaging", "Sorting", "Packing"]
# Difficulty multiplier per workflow stage. Sorting (order consolidation and
# routing) carries the highest inherent error/rework rate; Picking is the
# simplest single-item operation.
WORKFLOW_RISK = {"Picking": 0.85, "Packaging": 1.00, "Packing": 1.05, "Sorting": 1.30}

ORDERS_PER_CELL_RANGE = (35, 70)
N_CUSTOMERS = 300


def _risk(warehouse: str, workflow: str) -> float:
    return WAREHOUSE_RISK[warehouse] * WORKFLOW_RISK[workflow]


def generate_orders() -> pd.DataFrame:
    risk_min = min(_risk(w, k) for w in WAREHOUSES for k in WORKFLOWS)
    risk_max = max(_risk(w, k) for w in WAREHOUSES for k in WORKFLOWS)
    risk_span = risk_max - risk_min

    rows = []
    order_id = 1000
    for warehouse in WAREHOUSES:
        for workflow in WORKFLOWS:
            risk = _risk(warehouse, workflow)
            risk_norm = (risk - risk_min) / risk_span  # 0 (best) .. 1 (worst)

            n_orders = int(RNG.integers(*ORDERS_PER_CELL_RANGE))
            prep_time = RNG.normal(
                loc=12 + risk_norm * 20, scale=2.2, size=n_orders
            ).clip(min=6)
            accuracy = RNG.normal(
                loc=100 - risk_norm * 32, scale=2.5, size=n_orders
            ).clip(min=55, max=100)
            complaint_lambda = 0.05 + risk_norm * 0.9
            complaints = RNG.poisson(lam=complaint_lambda, size=n_orders)
            amount = RNG.lognormal(mean=np.log(60), sigma=0.4, size=n_orders).clip(
                10, 500
            )
            status_roll = RNG.random(n_orders)
            fail_threshold = 0.01 + risk_norm * 0.06
            cancel_threshold = fail_threshold + 0.02
            pending_threshold = cancel_threshold + 0.03
            status = np.where(
                status_roll < fail_threshold,
                "failed",
                np.where(
                    status_roll < cancel_threshold,
                    "cancelled",
                    np.where(status_roll < pending_threshold, "pending", "completed"),
                ),
            )
            customer_ids = RNG.integers(1, N_CUSTOMERS + 1, size=n_orders)
            signup_offsets = RNG.integers(0, 730, size=n_orders)
            signup_dates = pd.Timestamp("2026-07-20") - pd.to_timedelta(
                signup_offsets, unit="D"
            )

            for i in range(n_orders):
                order_id += 1
                rows.append(
                    {
                        "order_id": order_id,
                        "customer_id": int(customer_ids[i]),
                        "warehouse_id": warehouse,
                        "workflow_type": workflow,
                        "preparation_time_min": round(float(prep_time[i]), 1),
                        "packing_accuracy_pct": round(float(accuracy[i]), 1),
                        "delivery_complaints": int(complaints[i]),
                        "amount": round(float(amount[i]), 2),
                        "status": status[i],
                        "signup_date": signup_dates[i].date().isoformat(),
                    }
                )

    df = pd.DataFrame(rows)
    df["revenue"] = np.where(df["status"] == "completed", df["amount"], np.nan)
    return df


def build_dashboard_payload(df: pd.DataFrame) -> dict:
    engineered = engineer_operational_features(df)

    completed = engineered[engineered["status"] == "completed"]

    overall = {
        "totalOrders": int(len(engineered)),
        "completedOrders": int(len(completed)),
        "totalRevenue": round(float(completed["amount"].sum()), 2),
        "avgPrepTimeMin": round(float(engineered["preparation_time_min"].mean()), 1),
        "avgPackingAccuracyPct": round(
            float(engineered["packing_accuracy_pct"].mean()), 1
        ),
        "complaintRatePerOrder": round(
            float(engineered["delivery_complaints"].mean()), 3
        ),
        "avgWarehouseHealthScore": round(
            float(engineered["warehouse_health_score"].mean()), 1
        ),
        "accuracyComplaintCorrelation": round(
            float(
                engineered["packing_accuracy_pct"].corr(
                    engineered["delivery_complaints"]
                )
            ),
            3,
        ),
        "prepTimeComplaintCorrelation": round(
            float(
                engineered["preparation_time_min"].corr(
                    engineered["delivery_complaints"]
                )
            ),
            3,
        ),
    }

    def agg_group(group_cols):
        g = (
            engineered.groupby(group_cols)
            .agg(
                orders=("order_id", "count"),
                avgPrepTimeMin=("preparation_time_min", "mean"),
                avgPackingAccuracyPct=("packing_accuracy_pct", "mean"),
                complaintRatePerOrder=("delivery_complaints", "mean"),
                avgWarehouseHealthScore=("warehouse_health_score", "mean"),
            )
            .reset_index()
        )
        for col in [
            "avgPrepTimeMin",
            "avgPackingAccuracyPct",
            "complaintRatePerOrder",
            "avgWarehouseHealthScore",
        ]:
            g[col] = g[col].round(2)
        return g

    by_warehouse = agg_group(["warehouse_id"]).to_dict(orient="records")
    by_workflow = agg_group(["workflow_type"]).to_dict(orient="records")

    revenue_by_warehouse = (
        completed.groupby("warehouse_id")["amount"]
        .sum()
        .round(2)
        .reindex(WAREHOUSES)
        .fillna(0)
        .to_dict()
    )
    for row in by_warehouse:
        row["revenue"] = revenue_by_warehouse.get(row["warehouse_id"], 0)

    cell = agg_group(["warehouse_id", "workflow_type"])
    cell["failureRiskPct"] = (100 - cell["avgWarehouseHealthScore"]).round(1)
    matrix = cell.to_dict(orient="records")

    riskiest = cell.sort_values("failureRiskPct", ascending=False).iloc[0]
    safest = cell.sort_values("failureRiskPct", ascending=True).iloc[0]

    scatter = (
        engineered[
            [
                "workflow_type",
                "warehouse_id",
                "packing_accuracy_pct",
                "delivery_complaints",
            ]
        ]
        .groupby(["workflow_type", "warehouse_id"])
        .agg(
            avgAccuracy=("packing_accuracy_pct", "mean"),
            avgComplaints=("delivery_complaints", "mean"),
            orders=("packing_accuracy_pct", "count"),
        )
        .reset_index()
    )
    scatter["avgAccuracy"] = scatter["avgAccuracy"].round(2)
    scatter["avgComplaints"] = scatter["avgComplaints"].round(3)
    scatter_points = scatter.to_dict(orient="records")

    payload = {
        "generatedAt": "2026-07-20",
        "warehouses": WAREHOUSES,
        "workflows": WORKFLOWS,
        "overall": overall,
        "byWarehouse": by_warehouse,
        "byWorkflow": by_workflow,
        "matrix": matrix,
        "scatter": scatter_points,
        "insights": {
            "riskiestCombo": {
                "warehouse": riskiest["warehouse_id"],
                "workflow": riskiest["workflow_type"],
                "failureRiskPct": float(riskiest["failureRiskPct"]),
                "complaintRatePerOrder": float(riskiest["complaintRatePerOrder"]),
                "avgPackingAccuracyPct": float(riskiest["avgPackingAccuracyPct"]),
                "avgPrepTimeMin": float(riskiest["avgPrepTimeMin"]),
            },
            "safestCombo": {
                "warehouse": safest["warehouse_id"],
                "workflow": safest["workflow_type"],
                "failureRiskPct": float(safest["failureRiskPct"]),
                "complaintRatePerOrder": float(safest["complaintRatePerOrder"]),
                "avgPackingAccuracyPct": float(safest["avgPackingAccuracyPct"]),
                "avgPrepTimeMin": float(safest["avgPrepTimeMin"]),
            },
        },
    }
    return payload


def main() -> None:
    df = generate_orders()
    payload = build_dashboard_payload(df)

    repo_root = Path(__file__).resolve().parent.parent
    frontend_dir = repo_root / "frontend"
    frontend_dir.mkdir(exist_ok=True)

    data_js_path = frontend_dir / "data.js"
    data_js_path.write_text(
        "window.DASHBOARD_DATA = " + json.dumps(payload, indent=2) + ";\n",
        encoding="utf-8",
    )

    output_dir = repo_root / "output"
    output_dir.mkdir(exist_ok=True)
    order_csv_path = output_dir / "dashboard_orders.csv"
    df.to_csv(order_csv_path, index=False)

    print(f"[SUCCESS] Wrote {data_js_path} ({len(payload['matrix'])} matrix cells)")
    print(f"[SUCCESS] Wrote {order_csv_path} ({len(df)} synthetic orders)")
    print(f"[INFO] Overall KPIs: {json.dumps(payload['overall'], indent=2)}")


if __name__ == "__main__":
    main()
