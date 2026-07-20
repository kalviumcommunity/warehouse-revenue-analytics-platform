window.DASHBOARD_DATA = {
  "generatedAt": "2026-07-20",
  "warehouses": [
    "W1",
    "W2",
    "W3",
    "W4",
    "W5"
  ],
  "workflows": [
    "Picking",
    "Packaging",
    "Sorting",
    "Packing"
  ],
  "overall": {
    "totalOrders": 2000,
    "completedOrders": 1466,
    "totalRevenue": 648562.19,
    "avgPrepTimeMin": 18.39,
    "avgPackingAccuracyPct": 92.75,
    "complaintRatePerOrder": 1.094,
    "avgWarehouseHealthScore": 64.76
  },
  "byWarehouse": [
    {
      "warehouse_id": "W1",
      "orders": 370,
      "revenue": 119075.27,
      "avgPrepTimeMin": 16.92,
      "avgPackingAccuracyPct": 94.82,
      "complaintRatePerOrder": 0.876,
      "avgWarehouseHealthScore": 67.19
    },
    {
      "warehouse_id": "W2",
      "orders": 399,
      "revenue": 133343.25,
      "avgPrepTimeMin": 20.07,
      "avgPackingAccuracyPct": 90.33,
      "complaintRatePerOrder": 1.404,
      "avgWarehouseHealthScore": 61.87
    },
    {
      "warehouse_id": "W3",
      "orders": 441,
      "revenue": 148879.25,
      "avgPrepTimeMin": 17.78,
      "avgPackingAccuracyPct": 93.71,
      "complaintRatePerOrder": 0.977,
      "avgWarehouseHealthScore": 66.0
    },
    {
      "warehouse_id": "W4",
      "orders": 402,
      "revenue": 127470.21,
      "avgPrepTimeMin": 16.48,
      "avgPackingAccuracyPct": 95.55,
      "complaintRatePerOrder": 0.749,
      "avgWarehouseHealthScore": 68.24
    },
    {
      "warehouse_id": "W5",
      "orders": 388,
      "revenue": 119794.21,
      "avgPrepTimeMin": 20.76,
      "avgPackingAccuracyPct": 89.26,
      "complaintRatePerOrder": 1.474,
      "avgWarehouseHealthScore": 60.42
    }
  ],
  "byWorkflow": [
    {
      "workflow_type": "Picking",
      "orders": 454,
      "avgPrepTimeMin": 16.83,
      "avgPackingAccuracyPct": 94.95,
      "complaintRatePerOrder": 0.921,
      "avgWarehouseHealthScore": 66.93
    },
    {
      "workflow_type": "Packaging",
      "orders": 519,
      "avgPrepTimeMin": 17.92,
      "avgPackingAccuracyPct": 93.18,
      "complaintRatePerOrder": 1.042,
      "avgWarehouseHealthScore": 65.85
    },
    {
      "workflow_type": "Sorting",
      "orders": 464,
      "avgPrepTimeMin": 19.74,
      "avgPackingAccuracyPct": 90.37,
      "complaintRatePerOrder": 1.291,
      "avgWarehouseHealthScore": 62.62
    },
    {
      "workflow_type": "Packing",
      "orders": 563,
      "avgPrepTimeMin": 18.98,
      "avgPackingAccuracyPct": 92.53,
      "complaintRatePerOrder": 1.119,
      "avgWarehouseHealthScore": 63.79
    }
  ],
  "matrix": [
    {
      "warehouse_id": "W1",
      "workflow_type": "Picking",
      "orders": 83,
      "avgPrepTimeMin": 15.67,
      "avgPackingAccuracyPct": 97.06,
      "complaintRatePerOrder": 0.735,
      "avgWarehouseHealthScore": 68.83,
      "failureRiskPct": 31.2
    },
    {
      "warehouse_id": "W1",
      "workflow_type": "Packaging",
      "orders": 103,
      "avgPrepTimeMin": 16.11,
      "avgPackingAccuracyPct": 94.82,
      "complaintRatePerOrder": 0.728,
      "avgWarehouseHealthScore": 68.19,
      "failureRiskPct": 31.8
    },
    {
      "warehouse_id": "W1",
      "workflow_type": "Sorting",
      "orders": 88,
      "avgPrepTimeMin": 18.2,
      "avgPackingAccuracyPct": 92.36,
      "complaintRatePerOrder": 1.205,
      "avgWarehouseHealthScore": 64.66,
      "failureRiskPct": 35.3
    },
    {
      "warehouse_id": "W1",
      "workflow_type": "Packing",
      "orders": 96,
      "avgPrepTimeMin": 17.69,
      "avgPackingAccuracyPct": 95.15,
      "complaintRatePerOrder": 0.854,
      "avgWarehouseHealthScore": 67.01,
      "failureRiskPct": 33.0
    },
    {
      "warehouse_id": "W2",
      "workflow_type": "Picking",
      "orders": 94,
      "avgPrepTimeMin": 18.94,
      "avgPackingAccuracyPct": 92.36,
      "complaintRatePerOrder": 1.138,
      "avgWarehouseHealthScore": 65.26,
      "failureRiskPct": 34.7
    },
    {
      "warehouse_id": "W2",
      "workflow_type": "Packaging",
      "orders": 105,
      "avgPrepTimeMin": 19.43,
      "avgPackingAccuracyPct": 90.97,
      "complaintRatePerOrder": 1.324,
      "avgWarehouseHealthScore": 63.14,
      "failureRiskPct": 36.9
    },
    {
      "warehouse_id": "W2",
      "workflow_type": "Sorting",
      "orders": 80,
      "avgPrepTimeMin": 21.61,
      "avgPackingAccuracyPct": 87.5,
      "complaintRatePerOrder": 1.7,
      "avgWarehouseHealthScore": 57.99,
      "failureRiskPct": 42.0
    },
    {
      "warehouse_id": "W2",
      "workflow_type": "Packing",
      "orders": 120,
      "avgPrepTimeMin": 20.48,
      "avgPackingAccuracyPct": 90.06,
      "complaintRatePerOrder": 1.483,
      "avgWarehouseHealthScore": 60.69,
      "failureRiskPct": 39.3
    },
    {
      "warehouse_id": "W3",
      "workflow_type": "Picking",
      "orders": 94,
      "avgPrepTimeMin": 15.98,
      "avgPackingAccuracyPct": 95.97,
      "complaintRatePerOrder": 0.83,
      "avgWarehouseHealthScore": 67.17,
      "failureRiskPct": 32.8
    },
    {
      "warehouse_id": "W3",
      "workflow_type": "Packaging",
      "orders": 97,
      "avgPrepTimeMin": 17.04,
      "avgPackingAccuracyPct": 94.49,
      "complaintRatePerOrder": 0.938,
      "avgWarehouseHealthScore": 67.7,
      "failureRiskPct": 32.3
    },
    {
      "warehouse_id": "W3",
      "workflow_type": "Sorting",
      "orders": 115,
      "avgPrepTimeMin": 19.04,
      "avgPackingAccuracyPct": 91.36,
      "complaintRatePerOrder": 1.148,
      "avgWarehouseHealthScore": 64.55,
      "failureRiskPct": 35.5
    },
    {
      "warehouse_id": "W3",
      "workflow_type": "Packing",
      "orders": 135,
      "avgPrepTimeMin": 18.49,
      "avgPackingAccuracyPct": 93.58,
      "complaintRatePerOrder": 0.963,
      "avgWarehouseHealthScore": 65.19,
      "failureRiskPct": 34.8
    },
    {
      "warehouse_id": "W4",
      "workflow_type": "Picking",
      "orders": 94,
      "avgPrepTimeMin": 13.99,
      "avgPackingAccuracyPct": 97.58,
      "complaintRatePerOrder": 0.628,
      "avgWarehouseHealthScore": 71.04,
      "failureRiskPct": 29.0
    },
    {
      "warehouse_id": "W4",
      "workflow_type": "Packaging",
      "orders": 112,
      "avgPrepTimeMin": 16.56,
      "avgPackingAccuracyPct": 96.24,
      "complaintRatePerOrder": 0.741,
      "avgWarehouseHealthScore": 68.46,
      "failureRiskPct": 31.5
    },
    {
      "warehouse_id": "W4",
      "workflow_type": "Sorting",
      "orders": 91,
      "avgPrepTimeMin": 18.43,
      "avgPackingAccuracyPct": 92.98,
      "complaintRatePerOrder": 0.835,
      "avgWarehouseHealthScore": 66.55,
      "failureRiskPct": 33.5
    },
    {
      "warehouse_id": "W4",
      "workflow_type": "Packing",
      "orders": 105,
      "avgPrepTimeMin": 16.92,
      "avgPackingAccuracyPct": 95.23,
      "complaintRatePerOrder": 0.79,
      "avgWarehouseHealthScore": 66.96,
      "failureRiskPct": 33.0
    },
    {
      "warehouse_id": "W5",
      "workflow_type": "Picking",
      "orders": 89,
      "avgPrepTimeMin": 19.56,
      "avgPackingAccuracyPct": 91.88,
      "complaintRatePerOrder": 1.27,
      "avgWarehouseHealthScore": 62.31,
      "failureRiskPct": 37.7
    },
    {
      "warehouse_id": "W5",
      "workflow_type": "Packaging",
      "orders": 102,
      "avgPrepTimeMin": 20.56,
      "avgPackingAccuracyPct": 89.18,
      "complaintRatePerOrder": 1.5,
      "avgWarehouseHealthScore": 61.64,
      "failureRiskPct": 38.4
    },
    {
      "warehouse_id": "W5",
      "workflow_type": "Sorting",
      "orders": 90,
      "avgPrepTimeMin": 21.78,
      "avgPackingAccuracyPct": 87.08,
      "complaintRatePerOrder": 1.656,
      "avgWarehouseHealthScore": 58.28,
      "failureRiskPct": 41.7
    },
    {
      "warehouse_id": "W5",
      "workflow_type": "Packing",
      "orders": 107,
      "avgPrepTimeMin": 21.11,
      "avgPackingAccuracyPct": 88.98,
      "complaintRatePerOrder": 1.467,
      "avgWarehouseHealthScore": 59.49,
      "failureRiskPct": 40.5
    }
  ],
  "insights": {
    "riskiestCombo": {
      "warehouse": "W2",
      "workflow": "Sorting",
      "failureRiskPct": 42.0,
      "complaintRatePerOrder": 1.7,
      "avgPackingAccuracyPct": 87.5,
      "avgPrepTimeMin": 21.61
    },
    "safestCombo": {
      "warehouse": "W4",
      "workflow": "Picking",
      "failureRiskPct": 29.0,
      "complaintRatePerOrder": 0.628,
      "avgPackingAccuracyPct": 97.58,
      "avgPrepTimeMin": 13.99
    }
  }
};
