# Viva / Interview Preparation Guide: Retail Anomaly Detection Project

> **B.Tech CSE (Data Science) — Examination & Project Evaluation Guide**

---

### Q1: What is an Anomaly in the context of retail sales?
**Answer:**
An anomaly (or outlier) is a data point that deviates significantly from the expected normal pattern or distribution. In retail:
- A sudden surge in sales (e.g., 500 units instead of the normal 80) is a **Sales Spike**.
- A sudden drop to zero sales on a working day is a **Sales Drop**.
- A sudden decrease in physical warehouse stock without a corresponding sale is **Inventory Shrinkage (Theft or Spoilage)**.

---

### Q2: Why did you choose the Z-Score method instead of a static threshold?
**Answer:**
A static threshold (e.g., "flag whenever sales > 200") fails in retail because different items have different velocities. For instance, selling 200 units of Milk is normal, but selling 200 units of Cooking Oil is extreme.
The **Z-Score** is adaptive and normalized. It measures deviation relative to each product's specific mean and standard deviation:
$$Z = \frac{x - \mu}{\sigma}$$
It automatically adapts to high-volume and low-volume products alike.

---

### Q3: Why is the rolling window set to 14 records?
**Answer:**
A 14-record trailing window represents 2 weeks of daily transactions. 
- A window that is too short (e.g., 3 days) would be overly sensitive to short-term noise.
- A window that is too long (e.g., 90 days) would lag behind seasonal trends and slow-moving changes in consumer demand.
A 14-record window strikes the ideal balance between stability and responsiveness.

---

### Q4: How did you compute Standard Deviation in SQLite when SQLite doesn't have a built-in `STDDEV()` function?
**Answer:**
We used the mathematical algebraic identity for variance:
$$\text{Var}(X) = E[X^2] - (E[X])^2$$
$$\sigma = \sqrt{\text{Var}(X)}$$
In our SQL query, we compute the rolling average of sales (`rolling_mean`) and the rolling average of the squared sales (`avg_sq`). Then standard deviation is:
`SQRT(avg_sq - (rolling_mean * rolling_mean))`.

---

### Q5: Why did you use `ROW_NUMBER() OVER (PARTITION BY item ORDER BY id)` in SQL?
**Answer:**
In a point-of-sale database, transactions for different items are interleaved (Row 1 is Milk, Row 2 is Bread, Row 3 is Rice, etc.).
If we wrote `WHERE id >= current_id - 14`, we would only get 1 or 2 past records for that specific item.
By assigning a partitioned row number (`rn`) per item, each item gets a continuous sequence: 1, 2, 3... 90. This lets us cleanly slice the trailing 14 records for each product using:
`WHERE w.rn < r.rn AND w.rn >= r.rn - 14`.

---

### Q6: What is the significance of $|Z| > 2.5$ and $|Z| \ge 3.0$?
**Answer:**
Under the Empirical Rule of a Normal Distribution:
- ~68% of data falls within $\pm 1\sigma$
- ~95% of data falls within $\pm 2\sigma$
- ~98.8% of data falls within $\pm 2.5\sigma$
- ~99.7% of data falls within $\pm 3\sigma$
An event with $|Z| > 2.5$ has less than a ~1.2% chance of occurring naturally (Warning). An event with $|Z| \ge 3.0$ has less than a 0.3% chance (Critical Anomaly).

---

### Q7: What is Inventory Shrinkage and how does your project detect it?
**Answer:**
Inventory shrinkage refers to loss of physical stock due to shoplifting, employee theft, supplier fraud, or warehouse spoilage.
Our SQL engine identifies shrinkage when:
1. Current inventory is significantly below its rolling baseline ($\text{Inventory} < \mu_{inv} - 2.5\mu_{sales}$).
2. Yet sales during that period were normal or zero ($\text{Sales} \le \mu_{sales}$).
This discrepancy immediately points to unexplained loss.

---

### Q8: What role does Power BI play in this project?
**Answer:**
Power BI serves as the Business Intelligence and executive reporting layer. It connects to the transformed SQL view/CSV export and provides:
1. **Executive KPI Cards:** Tracking total anomalies, anomaly rate %, and financial impact.
2. **Visual Outlier Detection:** Color-coded time series charts where outlier dates are highlighted in red.
3. **DAX Measures:** Dynamic aggregation of critical vs. warning anomalies and dynamic background color gradients.

---

### Q9: What is the difference between a SQL View and a Table? Why did you use a View?
**Answer:**
A physical table stores data on disk. A **VIEW** is a saved SQL query that executes dynamically when queried.
We used a View (`zscore_live_view`) because it ensures **real-time statistical computation**: whenever new sales are inserted into `sales_data`, the view recalculates rolling metrics on-the-fly without needing a batch cron job.

---

### Q10: How can this project be scaled in a real-world enterprise environment?
**Answer:**
1. **Database:** Migrate from SQLite to a distributed Cloud Data Warehouse like Google BigQuery or Snowflake.
2. **Streaming:** Use Apache Kafka or AWS Kinesis to ingest thousands of POS transactions per second.
3. **Machine Learning:** Complement the statistical Z-score with unsupervised ML models like Isolation Forest, DBSCAN, or Autoencoders for multi-variable anomaly scoring.
4. **Alerts:** Connect the alert monitor to Twilio (SMS), PagerDuty, or Slack webhooks for instant store manager alerts.

---

### Q11: Why did you implement both SQL Z-Score and Machine Learning (Isolation Forest)?
**Answer:**
We implemented a **Dual-Engine Architecture** to leverage the unique advantages of both paradigms:
1. **SQL Windowed Z-Score:** Provides **in-database, zero-latency streaming scoring (< 15ms)**. It requires no heavy dependencies and executes on pure relational databases.
2. **Machine Learning Isolation Forest:** Provides **unsupervised, multi-dimensional feature modeling** (capturing complex non-linear interactions across Sales, Inventory, Revenue, and Velocity ratios simultaneously).
In our benchmark, both engines achieved 75% recall against ground-truth anomalies, with ML providing slightly higher precision (6.9% vs 6.7%) at the expense of computational latency (~250ms).

---

### Q12: How does the Isolation Forest algorithm detect anomalies?
**Answer:**
Isolation Forest is an unsupervised tree-based ensemble method based on the principle that **anomalies are 'few and different'**.
- The algorithm randomly selects a feature and splits the data at a random value.
- Normal, dense points require many splits (deep path length) to be isolated.
- Outliers and anomalous points are isolated very quickly (short path length near the root).
Points with anomalously short average path lengths across 150 random trees are assigned an anomaly score and flagged as outliers.
