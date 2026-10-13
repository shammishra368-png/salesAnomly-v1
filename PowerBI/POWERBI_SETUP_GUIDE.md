# Power BI Desktop — Step-by-Step Dashboard Setup Guide

> **Project:** Retail Sales & Inventory Anomaly Detection  
> **Model:** `PowerBI/SalesAnomalyDashboard.pbip`  
> **Data Sources:** `data_export/sales_inventory_anomalies.csv` & `data_export/anomaly_summary.csv`

---

## 🚀 How to Open the Project in Power BI Desktop

1. Make sure **Power BI Desktop** is installed on your Windows PC.
2. In Power BI Desktop, enable PBIP (if not already enabled):
   * `File → Options and settings → Options → Preview features → Power BI Project (.pbip) save format` (Check the box and restart Power BI).
3. Open `PowerBI/SalesAnomalyDashboard.pbip` (or double-click the file).
4. Click **↻ Refresh** in the Home ribbon. Power BI will read the data from `C:\project\data_export\` instantly!

---

## 🎨 Recreating the Visuals in 3 Minutes

### Page 1: Executive Overview

1. **KPI Card 1 (Total Anomalies):**
   * Visual: **Card**
   * Field: Drag `[Total Anomalies]` measure into the Fields well.
   * Callout value color: `#F43F5E` (Red).

2. **KPI Card 2 (Anomaly Rate %):**
   * Visual: **Card**
   * Field: Drag `[Anomaly Rate %]` measure.

3. **KPI Card 3 (Total Revenue):**
   * Visual: **Card**
   * Field: Drag `[Total Revenue]` measure.

4. **Time Series Line Chart (Sales & Outliers):**
   * Visual: **Line Chart**
   * X-axis: `sales_inventory_anomalies[record_date]`
   * Y-axis: `sales_inventory_anomalies[sales]` and `sales_inventory_anomalies[rolling_mean]`
   * Legend: `sales_inventory_anomalies[item]`

5. **Product Breakdown (Stacked Bar Chart):**
   * Visual: **Clustered Bar Chart**
   * Y-axis: `anomaly_summary[item]`
   * X-axis: `anomaly_summary[critical_anomalies]` and `anomaly_summary[warning_anomalies]`

6. **Slicer:**
   * Visual: **Slicer**
   * Field: `sales_inventory_anomalies[item]`

---

### Page 2: Inventory & Shrinkage Analysis

1. **Donut Chart (Anomaly Severity Breakdown):**
   * Visual: **Donut Chart**
   * Legend: `sales_inventory_anomalies[severity]`
   * Values: `sales_inventory_anomalies[is_flagged]` (Count or Sum)

2. **Inventory Discrepancy Table:**
   * Visual: **Table**
   * Columns:
     * `record_date`
     * `item`
     * `sales`
     * `rolling_mean`
     * `z_score`
     * `inventory`
     * `severity`
     * `anomaly_type`
     * `financial_impact`
   * **Conditional Formatting:**
     * In Format Pane → Cell elements → Select `z_score` column.
     * Turn on **Background color** → Format by **Rules**:
       * If value >= 2.5: Red (`#EF4444`)
       * If value <= -2.5: Orange (`#F59E0B`)
       * Else: Green (`#10B981`)

---

### Page 3: Slicers & Filtering

1. **Date Range Slicer:**
   * Visual: **Slicer**
   * Field: `record_date` (Set style to *Between* slider).
2. **Anomaly Type Filter:**
   * Visual: **Slicer**
   * Field: `anomaly_type` (Checkboxes for *Sales Spike*, *Sales Drop*, *Stockout*, *Shrinkage*).
