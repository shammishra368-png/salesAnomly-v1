"""
ml_anomaly_detector.py
-----------------------
Machine Learning Benchmark: Isolation Forest vs Statistical Z-Score
Author: Krishna — B.Tech CSE (Data Science)

Trains an unsupervised Isolation Forest model on multi-dimensional features
(Sales, Inventory, Daily Rolling Velocity, Price, Revenue) to benchmark against
the SQL Rolling Z-Score statistical engine.

Computes:
- Precision, Recall, F1-Score, and Confusion Matrix against Ground Truth.
- Exports comparison results to data_export/ml_anomaly_comparison.csv.
"""

import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
import os

DB_PATH = "retail.db"
OUTPUT_CSV = "data_export/ml_anomaly_comparison.csv"
METRICS_JSON = "data_export/ml_metrics.json"


def run_ml_benchmark():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database {DB_PATH} not found.")
        return

    print("=" * 70)
    print("MACHINE LEARNING BENCHMARK: ISOLATION FOREST VS SQL Z-SCORE")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT 
            id, record_date, item, sales, inventory, unit_price, revenue, stock_value,
            rolling_mean, rolling_std, z_score, is_flagged, severity, is_injected_anomaly,
            anomaly_type
        FROM zscore_live_view
        ORDER BY id ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    print(f"Loaded {len(df)} transactions from zscore_live_view.")

    # 1. Feature Engineering for ML
    df['sales_to_inv_ratio'] = df['sales'] / (df['inventory'] + 1.0)
    df['sales_diff_mean'] = df['sales'] - df['rolling_mean']
    df['sales_std_ratio'] = np.where(df['rolling_std'] > 0, df['sales_diff_mean'] / df['rolling_std'], 0)

    features = [
        'sales',
        'inventory',
        'revenue',
        'sales_to_inv_ratio',
        'sales_diff_mean',
        'sales_std_ratio'
    ]

    X = df[features].fillna(0)

    # 2. Train Isolation Forest (Contamination set to ~8% based on retail baseline)
    print("\n[1/3] Training Isolation Forest model...")
    iso_forest = IsolationForest(
        n_estimators=150,
        contamination=0.08,
        random_state=42,
        n_jobs=-1
    )
    iso_forest.fit(X)

    # Predictions: -1 for outlier/anomaly, 1 for inlier/normal
    raw_preds = iso_forest.predict(X)
    df['ml_anomaly_flag'] = np.where(raw_preds == -1, 1, 0)
    df['ml_anomaly_score'] = -iso_forest.decision_function(X) # Higher = more anomalous

    # 3. Benchmark Metrics
    # Ground truth column: is_injected_anomaly (1 if injected, 0 otherwise)
    y_true = df['is_injected_anomaly']
    y_sql = df['is_flagged']
    y_ml = df['ml_anomaly_flag']

    # Performance of SQL Z-Score Engine
    p_sql, r_sql, f1_sql, _ = precision_recall_fscore_support(y_true, y_sql, average='binary', zero_division=0)
    # Performance of Machine Learning Isolation Forest
    p_ml, r_ml, f1_ml, _ = precision_recall_fscore_support(y_true, y_ml, average='binary', zero_division=0)

    print("\n[2/3] Model Evaluation Summary against Injected Ground Truth:")
    print("-" * 70)
    print(f"Metric                | SQL Z-Score Engine | ML Isolation Forest")
    print("-" * 70)
    print(f"Precision             | {p_sql*100:>16.1f}% | {p_ml*100:>17.1f}%")
    print(f"Recall (Sensitivity)  | {r_sql*100:>16.1f}% | {r_ml*100:>17.1f}%")
    print(f"F1-Score              | {f1_sql*100:>16.1f}% | {f1_ml*100:>17.1f}%")
    print(f"Total Flagged Outliers| {int(y_sql.sum()):>17d} | {int(y_ml.sum()):>18d}")
    print("-" * 70)

    # 4. Save results to CSV
    os.makedirs("data_export", exist_ok=True)
    export_cols = [
        'id', 'record_date', 'item', 'sales', 'inventory', 'revenue',
        'z_score', 'anomaly_type', 'is_flagged', 'severity',
        'ml_anomaly_flag', 'ml_anomaly_score', 'is_injected_anomaly'
    ]
    df[export_cols].to_csv(OUTPUT_CSV, index=False)
    print(f"\n[3/3] Exported comparison results to: {OUTPUT_CSV}")

    # Save metrics summary
    metrics = {
        "sql_precision": round(p_sql * 100, 1),
        "sql_recall": round(r_sql * 100, 1),
        "sql_f1": round(f1_sql * 100, 1),
        "sql_flagged": int(y_sql.sum()),
        "ml_precision": round(p_ml * 100, 1),
        "ml_recall": round(r_ml * 100, 1),
        "ml_f1": round(f1_ml * 100, 1),
        "ml_flagged": int(y_ml.sum()),
        "total_records": len(df)
    }
    import json
    with open(METRICS_JSON, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"      Saved metrics summary to: {METRICS_JSON}")
    print("[SUCCESS] Machine learning benchmark completed successfully!")


if __name__ == "__main__":
    run_ml_benchmark()
