# Retail Sales & Inventory Anomaly Detection System

> **B.Tech CSE (Data Science) — 3rd Year Semester Project**  
> **Student Author:** Krishna  
> **Domain:** Business Intelligence, Applied Statistics & Data Engineering  

---

## 📌 Project Overview

This project implements an end-to-end automated monitoring pipeline designed to detect unusual operational patterns (anomalies) in retail sales and warehouse inventory. Using the **rolling Z-Score statistical method** in SQL and a dynamic **Power BI & Web Dashboard**, the system identifies:

1. **Sales Spikes:** Sudden, abnormal demand surges (bulk purchasing, viral promotions).
2. **Sales Drops:** Unexplained zero or near-zero sales days (billing outage, supplier delay).
3. **Inventory Stockouts:** Products completely depleted from warehouse shelves.
4. **Critical Low Stock:** Inventory projected to deplete within 48 hours based on rolling velocity.
5. **Inventory Shrinkage (Theft/Damage):** Unexplained physical stock depletion without corresponding sales.

---

## 🏗️ Architecture & Pipeline

```
[POS Simulator / Sales Feed] 
          │ (real-time stream simulation)
          ▼
   [retail.db (SQLite)] ──► [sales_data table]
          │
          ▼
   [zscore_live_view.sql] (SQL Window Functions & Statistics)
   • 14-record rolling mean & standard deviation per item
   • Dynamic Z-Score: (x - μ) / σ
   • Severity classification: CRITICAL vs WARNING vs NORMAL
   • Estimated revenue loss / financial impact calculation
          │
          ├──────────────────────────┐
          ▼                          ▼
[Live Alert Monitor]       [Data Export & BI Layer]
• Polls zscore_live_view   • PowerBI/SalesAnomalyDashboard.pbip
• Logs to anomaly_log.csv  • data_export/*.csv (1-click load)
• Instant console alerts   • dashboard.html (Interactive Browser UI)
```

---

## 📁 Repository Structure

```
KRISHNA-RETAIL-ANOMALY-ENGINE/
│
├── generate_data.py          # Generates 90 days of synthetic sales, inventory & pricing
├── setup_view.py             # Executes SQL view creation in retail.db
├── zscore_live_view.sql      # Core SQL VIEW calculating rolling Z-Score & anomalies
├── simulate_stream.py        # Live POS simulation feed (inserts transactions in real-time)
├── alert_monitor.py          # Background polling service logging anomalies
├── export_to_powerbi.py      # Exports enriched datasets to CSV for Power BI Desktop
├── build_html_dashboard.py   # Generates presentation-grade standalone dashboard
├── run_project.bat           # 1-Click launcher to build & open the dashboard
│
├── retail.db                 # SQLite database storing sales_data and view
├── dashboard.html            # Interactive Web Dashboard (Chart.js + Tailwind)
│
├── data_export/              # Power BI ready datasets
│   ├── sales_inventory_anomalies.csv
│   └── anomaly_summary.csv
│
├── logs/
│   └── anomaly_log.csv       # Logged anomalies from alert_monitor.py
│
├── PowerBI/                  # Power BI Desktop Assets
│   ├── SalesAnomalyDashboard.pbip
│   ├── DAX_MEASURES.txt      # Copy-paste DAX measures
│   └── POWERBI_SETUP_GUIDE.md # Visual setup guide
│
├── PROJECT_REPORT.md         # Full Academic Project Report
├── VIVA_QUESTIONS_AND_ANSWERS.md # Top 10 Viva Questions with model answers
└── STUDENT_PRESENTATION_SCRIPT.md # Word-for-word presentation script
```

---

## 🚀 How to Run the Project

### Option A: The 1-Click Method (Recommended)
Simply double-click **`run_project.bat`**.  
This executes the full pipeline and launches the interactive dashboard directly in your browser.

### Option B: Step-by-Step Execution

1. **Generate Base Dataset:**
   ```powershell
   python generate_data.py
   ```
2. **Compile SQL Z-Score View:**
   ```powershell
   python setup_view.py
   ```
3. **Export Clean CSVs for Power BI:**
   ```powershell
   python export_to_powerbi.py
   ```
4. **Build & Open Dashboard:**
   ```powershell
   python build_html_dashboard.py
   start dashboard.html
   ```

### Option C: Run Real-Time POS Feed & Alerts
* **Terminal 1 (POS Simulator):**
  ```powershell
  python simulate_stream.py --fast
  ```
* **Terminal 2 (Alert Monitor):**
  ```powershell
  python alert_monitor.py
  ```

---

## 📊 Power BI Dashboard Setup

1. Open **Power BI Desktop**.
2. Open `PowerBI/SalesAnomalyDashboard.pbip` (or import `data_export/sales_inventory_anomalies.csv`).
3. Click **↻ Refresh** to populate all visuals.
4. Use the pre-configured DAX measures in [`PowerBI/DAX_MEASURES.txt`](file:///c:/project/PowerBI/DAX_MEASURES.txt).

---

## 👤 Author & Academic Details

* **Student Name:** Krishna
* **Course:** B.Tech Computer Science & Engineering (Data Science)
* **Semester:** 3rd Year (6th Semester) Capstone Project
