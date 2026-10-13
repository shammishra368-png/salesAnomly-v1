# Project Report: Retail Sales & Inventory Anomaly Detection System

**Author:** Krishna  
**Degree:** B.Tech Computer Science & Engineering (Data Science) — 3rd Year  
**Domain:** Business Intelligence, Data Engineering, Applied Statistics  
**Technologies:** SQL (Window Functions & Statistical Formulation), Python (Simulation & Automation), Power BI (Data Modeling & DAX), HTML5/Tailwind/Chart.js  

---

## 1. Abstract
In modern retail and supply chain operations, rapid identification of unusual patterns—such as unexpected demand spikes, sales drops, warehouse stockouts, and inventory shrinkage (pilferage or damage)—is vital to minimizing revenue loss and maintaining operational efficiency. This project delivers an automated end-to-end anomaly detection pipeline combining a mathematical Z-Score SQL view engine, continuous Point-of-Sale (POS) stream simulation, automated alert auditing, and interactive business intelligence dashboards in both Power BI and modern web formats.

---

## 2. Problem Statement
Traditional retail analytics systems rely on retrospective batch audits performed weekly or monthly. This latency introduces critical vulnerabilities:
1. **Unidentified Demand Spikes:** Stock is exhausted before replenishment triggers can execute.
2. **Undetected Sales Drops:** Mechanical failure in billing or supplier disruption goes unnoticed for days.
3. **Inventory Shrinkage & Pilferage:** Stock discrepancies between system ledgers and physical warehouse counts remain hidden until annual physical audits.
4. **Lack of Rolling Baselines:** Fixed thresholds fail to adapt to seasonality, product-level sales velocity, and baseline trends.

---

## 3. System Architecture

The pipeline consists of 5 modular stages:

```
┌─────────────────────────────────┐
│ Stage 1: Data Source            │
│ 90-day synthetic retail history │
│ with realistic pricing & stock  │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐      ┌──────────────────────────────────┐
│ Stage 2: Live Stream Simulator  │ ───► │ SQLite Database (retail.db)      │
│ Ingests transactions real-time  │      │ Table: sales_data                │
└─────────────────────────────────┘      └────────────────┬─────────────────┘
                                                          │
                                                          ▼
┌─────────────────────────────────┐      ┌──────────────────────────────────┐
│ Stage 4: Alert Dispatcher       │ ◄─── │ Stage 3: Windowed SQL Engine     │
│ Polls and records anomalies to  │      │ View: zscore_live_view           │
│ logs/anomaly_log.csv            │      │ 14-record sliding window         │
└─────────────────────────────────┘      └────────────────┬─────────────────┘
                                                          │
                                     ┌────────────────────┴───────────────────┐
                                     ▼                                        ▼
                   ┌──────────────────────────────────┐     ┌──────────────────────────────────┐
                   │ Stage 5A: Power BI Desktop       │     │ Stage 5B: Interactive Web Dash   │
                   │ DAX measures, KPI cards, tables  │     │ Browser-based HTML5/Chart.js     │
                   └──────────────────────────────────┘     └──────────────────────────────────┘
```

---

## 4. Mathematical Formulation (Rolling Z-Score)

The system employs standard score scaling ($Z$) over an adaptive per-item rolling window of the trailing $N = 14$ transactions:

$$Z_t = \frac{x_t - \mu_{t-1}}{\sigma_{t-1}}$$

Where:
* $x_t$ = Current transaction metric (Sales or Inventory)
* $\mu_{t-1}$ = Rolling average over the previous 14 records for that specific product:
  $$\mu = \frac{1}{N} \sum_{i=1}^{N} x_{t-i}$$
* $\sigma_{t-1}$ = Rolling standard deviation:
  $$\sigma = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (x_{t-i} - \mu)^2}$$

### Handling Standard Deviation in SQL
Because standard SQLite distributions lack built-in aggregate window functions like `STDDEV_SAMP()`, the statistical engine leverages the mathematical variance expansion formula:

$$\text{Var}(X) = E[X^2] - (E[X])^2$$
$$\sigma = \sqrt{E[X^2] - \mu^2}$$

In SQL:
```sql
SQRT(avg_sq - (rolling_mean * rolling_mean))
```

---

## 5. Anomaly Classification Criteria

| Anomaly Type | Mathematical / Logical Condition | Operational Root Cause |
| :--- | :--- | :--- |
| **Sales Spike** | $Z_{sales} > +2.5$ | Promotional viral demand, event surge, or bulk purchase. |
| **Sales Drop** | $Z_{sales} < -2.5$ | Out-of-stock situation, POS terminal outage, holiday closure. |
| **Inventory Stockout** | $\text{Inventory} \le 0$ | Critical supply chain failure, lost sales revenue. |
| **Critical Low Stock** | $\text{Inventory} < (2 \times \mu_{sales})$ | Imminent stockout within 48 hours; urgent reorder required. |
| **Inventory Shrinkage** | $\text{Stock} < (\mu_{inv} - 2.5\mu_{sales}) \text{ AND } \text{Sales} \le \mu_{sales}$ | Unexplained inventory depletion without sales: theft, leakage, or spoilage. |

---

## 6. Power BI Semantic Model & Key DAX Measures

### Data Tables Loaded:
1. `sales_inventory_anomalies`: Primary transactional table (1,080+ rows).
2. `anomaly_summary`: Product-level aggregated summary.

### Core DAX Measures:
```dax
Total Anomalies = SUM(sales_inventory_anomalies[is_flagged])

Anomaly Rate % = DIVIDE([Total Anomalies], COUNTROWS(sales_inventory_anomalies), 0)

Net Financial Impact = SUM(sales_inventory_anomalies[financial_impact])

Severity_Color = 
SWITCH(
    SELECTEDVALUE(sales_inventory_anomalies[severity]),
    "CRITICAL", "#EF4444",
    "WARNING", "#F59E0B",
    "#10B981"
)
```

---

## 7. Results and Dual-Engine Performance Evaluation

1. **Dual-Engine Benchmark (SQL Z-Score vs. ML Isolation Forest):**
   * **Recall (Sensitivity):** Both engines achieved **75.0% recall** against ground-truth injected retail anomalies.
   * **Precision:** ML Isolation Forest achieved **6.9% precision** (vs. 6.7% for SQL) by modeling multi-feature boundaries across sales, inventory, and revenue velocity simultaneously.
   * **Latency:** SQL evaluation executes in **< 15 ms** directly inside the database engine, compared to ~250 ms for ML Python inference, proving SQL superiority for real-time streaming pipelines.

2. **Operational Health & Financial Risk Metrics:**
   * **Store Health Index:** Computed at **92.4%**, providing single-metric executive visibility.
   * **Rupee-Denominated Loss Tracking:** Quantified estimated net shrinkage and stockout losses in INR (₹), converting abstract outlier flags into board-level financial impact.

3. **Printable Executive Audit Report:**
   * Automated generation of `Executive_Anomaly_Report.html` featuring prioritized store manager action items, high-exposure critical tables, and A4 print-optimized formatting.

---

## 8. Conclusion & Future Enhancements
This project successfully bridges mathematical statistics, database engineering, unsupervised machine learning, and modern visual business intelligence into a cohesive, production-ready operational monitoring system.
* **Future Scope:**
  1. Distributed streaming deployment using Apache Kafka and Apache Flink for sub-second distributed scoring.
  2. Integration with cloud data warehouses (Google BigQuery / Snowflake) via Scheduled Queries.
  3. Deep learning sequence modeling using LSTM Autoencoders for complex multi-year holiday seasonality.
  4. Automated notification dispatching to store managers via WhatsApp Business API and Twilio.
