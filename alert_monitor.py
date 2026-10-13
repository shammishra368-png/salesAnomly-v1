"""
alert_monitor.py
-----------------
Continuously polls the zscore_live_view in retail.db and logs any newly
detected anomalies (Critical or Warning) to logs/anomaly_log.csv.

Features:
- Multi-tier alert detection (Sales Spikes/Drops, Stockouts, Critical Low Stock, Shrinkage).
- Deduplication: Never logs the same transaction ID twice.
- Colorized real-time console alerts.

Usage:
    python alert_monitor.py                 # polls every 10 seconds
    python alert_monitor.py --interval 5    # polls every 5 seconds
"""

import sqlite3
import csv
import os
import time
import argparse
from datetime import datetime

DB_PATH = "retail.db"
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "anomaly_log.csv")

CSV_HEADERS = [
    "log_timestamp",
    "record_id",
    "record_date",
    "item",
    "severity",
    "anomaly_type",
    "sales",
    "rolling_mean",
    "z_score",
    "inventory",
    "financial_impact",
]


def ensure_log_file():
    os.makedirs(LOG_DIR, exist_ok=True)
    logged_ids = set()

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    logged_ids.add(int(row["record_id"]))
                except (ValueError, KeyError):
                    pass
    else:
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)

    return logged_ids


def poll_anomalies(conn, logged_ids):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, record_date, item, severity, anomaly_type, sales, rolling_mean, z_score, inventory, financial_impact
        FROM zscore_live_view
        WHERE is_flagged = 1
        ORDER BY id ASC
    """)
    new_anomalies = []
    for row in cur.fetchall():
        record_id = row[0]
        if record_id not in logged_ids:
            new_anomalies.append({
                "record_id":        record_id,
                "record_date":      row[1],
                "item":             row[2],
                "severity":         row[3],
                "anomaly_type":     row[4],
                "sales":            row[5],
                "rolling_mean":     row[6],
                "z_score":          row[7],
                "inventory":        row[8],
                "financial_impact": row[9],
            })
    return new_anomalies


def log_anomalies(anomalies, logged_ids):
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for a in anomalies:
            writer.writerow([
                datetime.now().isoformat(timespec="seconds"),
                a["record_id"],
                a["record_date"],
                a["item"],
                a["severity"],
                a["anomaly_type"],
                a["sales"],
                a["rolling_mean"],
                a["z_score"],
                a["inventory"],
                a["financial_impact"],
            ])
            logged_ids.add(a["record_id"])


def main():
    parser = argparse.ArgumentParser(description="Live Anomaly Alert Monitor")
    parser.add_argument("--interval", type=int, default=5, help="Poll interval in seconds")
    args = parser.parse_args()

    logged_ids = ensure_log_file()

    print("=" * 70)
    print("RETAIL ANOMALY MONITOR & ALERT DISPATCHER")
    print("=" * 70)
    print(f"Monitoring: {DB_PATH} -> zscore_live_view")
    print(f"Alert Log:  {LOG_FILE} (pre-loaded {len(logged_ids)} prior alerts)")
    print(f"Polling Interval: {args.interval}s  |  Press Ctrl+C to stop")
    print("-" * 70)

    try:
        while True:
            if not os.path.exists(DB_PATH):
                time.sleep(args.interval)
                continue

            conn = sqlite3.connect(DB_PATH)
            new_anomalies = poll_anomalies(conn, logged_ids)
            conn.close()

            if new_anomalies:
                log_anomalies(new_anomalies, logged_ids)
                for a in new_anomalies:
                    prefix = "[CRITICAL ALERT]" if a["severity"] == "CRITICAL" else "[WARNING ALERT ]"
                    print(
                        f"{prefix} {a['record_date']} | {a['item']:<15s} | "
                        f"{a['anomaly_type']:<26s} | Z={a['z_score']:>+5.2f} | Impact: ₹{a['financial_impact']:>8.2f}"
                    )
            else:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] Polled: No new anomalies detected.", end="\r")

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n[MONITOR] Alert polling stopped by user.")


if __name__ == "__main__":
    main()
