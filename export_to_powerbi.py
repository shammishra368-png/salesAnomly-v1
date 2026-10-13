"""
export_to_powerbi.py
--------------------
Exports clean, enriched datasets from zscore_live_view in retail.db into
ready-to-use CSV files for Power BI Desktop.
Also generates a DAX measures reference cheat-sheet for rapid dashboard authoring.
"""

import sqlite3
import csv
import os

DB_PATH = "retail.db"
EXPORT_DIR = "data_export"
POWERBI_DIR = "PowerBI"
MAIN_EXPORT = os.path.join(EXPORT_DIR, "sales_inventory_anomalies.csv")
SUMMARY_EXPORT = os.path.join(EXPORT_DIR, "anomaly_summary.csv")
DAX_FILE = os.path.join(POWERBI_DIR, "DAX_MEASURES.txt")


def generate_dax_file():
    dax_content = """================================================================================
POWER BI DAX MEASURES CHEAT SHEET
Sales & Inventory Anomaly Detection Dashboard
================================================================================

1. Total Records:
   Total Records = COUNTROWS(sales_inventory_anomalies)

2. Total Anomalies Detected:
   Total Anomalies = SUM(sales_inventory_anomalies[is_flagged])

3. Anomaly Rate (%):
   Anomaly Rate % = 
   DIVIDE([Total Anomalies], [Total Records], 0)
   (Format as Percentage: 0.00%)

4. Total Revenue:
   Total Revenue = SUM(sales_inventory_anomalies[revenue])
   (Format as Currency: ₹#,##0.00)

5. Net Financial Anomaly Impact:
   Net Financial Impact = SUM(sales_inventory_anomalies[financial_impact])
   (Format as Currency: ₹#,##0.00)

6. Critical Anomalies Count:
   Critical Anomalies = 
   CALCULATE(
       COUNTROWS(sales_inventory_anomalies),
       sales_inventory_anomalies[severity] = "CRITICAL"
   )

7. Warning Anomalies Count:
   Warning Anomalies = 
   CALCULATE(
       COUNTROWS(sales_inventory_anomalies),
       sales_inventory_anomalies[severity] = "WARNING"
   )

8. Inventory Stockout Alerts:
   Stockout Events = 
   CALCULATE(
       COUNTROWS(sales_inventory_anomalies),
       sales_inventory_anomalies[anomaly_type] = "Inventory Stockout"
   )

9. Dynamic Color Formatting for Table & Matrix:
   Severity_Color = 
   SWITCH(
       SELECTEDVALUE(sales_inventory_anomalies[severity]),
       "CRITICAL", "#EF4444", -- Vivid Red
       "WARNING", "#F59E0B",  -- Amber / Orange
       "#10B981"              -- Emerald Green
   )

10. Average |Z-Score| of Flagged Anomalies:
    Avg Anomaly Z-Score = 
    CALCULATE(
        AVERAGE(sales_inventory_anomalies[z_score]),
        sales_inventory_anomalies[is_flagged] = 1
    )
================================================================================
"""
    os.makedirs(POWERBI_DIR, exist_ok=True)
    with open(DAX_FILE, "w", encoding="utf-8") as f:
        f.write(dax_content)
    print(f"      Created DAX Measures Cheat Sheet: {DAX_FILE}")


def main():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] '{DB_PATH}' not found. Run generate_data.py first.")
        return

    os.makedirs(EXPORT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("[1/3] Exporting full zscore_live_view to CSV...")
    cur.execute("SELECT * FROM zscore_live_view")
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    with open(MAIN_EXPORT, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
    print(f"      Saved {len(rows)} rows to '{MAIN_EXPORT}'")

    print("[2/3] Exporting product-level anomaly summary...")
    cur.execute("""
        SELECT 
            item,
            COUNT(*) AS total_records,
            ROUND(SUM(revenue), 2) AS total_revenue,
            ROUND(AVG(sales), 2) AS avg_daily_sales,
            ROUND(AVG(inventory), 2) AS avg_inventory,
            SUM(CASE WHEN is_flagged = 1 THEN 1 ELSE 0 END) AS total_anomalies,
            SUM(CASE WHEN severity = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_anomalies,
            SUM(CASE WHEN severity = 'WARNING' THEN 1 ELSE 0 END) AS warning_anomalies,
            SUM(CASE WHEN anomaly_type = 'Sales Spike' THEN 1 ELSE 0 END) AS sales_spikes,
            SUM(CASE WHEN anomaly_type = 'Sales Drop' THEN 1 ELSE 0 END) AS sales_drops,
            SUM(CASE WHEN anomaly_type = 'Inventory Stockout' THEN 1 ELSE 0 END) AS stockouts,
            SUM(CASE WHEN anomaly_type = 'Inventory Shrinkage (Theft)' THEN 1 ELSE 0 END) AS shrinkages,
            ROUND(SUM(financial_impact), 2) AS total_financial_impact,
            ROUND(
                (SUM(CASE WHEN is_flagged = 1 THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100, 
                2
            ) AS anomaly_rate_pct
        FROM zscore_live_view
        GROUP BY item
        ORDER BY total_anomalies DESC
    """)
    summary_cols = [desc[0] for desc in cur.description]
    summary_rows = cur.fetchall()

    with open(SUMMARY_EXPORT, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(summary_cols)
        writer.writerows(summary_rows)
    print(f"      Saved {len(summary_rows)} item summaries to '{SUMMARY_EXPORT}'")

    print("[3/3] Generating DAX measures guide...")
    generate_dax_file()

    conn.close()
    print("\n[SUCCESS] Power BI Assets Exported Successfully!")
    print(f"  - {os.path.abspath(MAIN_EXPORT)}")
    print(f"  - {os.path.abspath(SUMMARY_EXPORT)}")
    print(f"  - {os.path.abspath(DAX_FILE)}")


if __name__ == "__main__":
    main()
