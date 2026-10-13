# Student Project Presentation Script (Viva & Demo Guide)

> **Project:** Retail Sales & Inventory Anomaly Detection System  
> **Presenter:** Krishna — B.Tech CSE (Data Science)  

---

## 🎤 Part 1: Opening Introduction (30–45 Seconds)

**English:**
> *"Good morning/afternoon, Respected Faculty and Evaluators.  
> My name is Krishna, and today I am presenting my semester capstone project: **'Retail Sales and Inventory Anomaly Detection Engine using SQL, Python, and Power BI'**.  
> In modern retail, businesses lose millions due to three silent problems: sudden demand spikes causing stockouts, unexpected sales drops due to system billing outages, and inventory shrinkage—which is theft or damage where warehouse stock drops without any sale.  
> My objective in this project was to design a real-time, lightweight monitoring pipeline that calculates adaptive statistical baselines using SQL Window Functions, automatically flags outliers using Z-scores, and provides actionable visual intelligence to store managers."*

**Hindi / Hinglish (Alternative):**
> *"Good morning Sir/Ma'am. Mera naam Krishna hai aur mera project hai **Retail Sales & Inventory Anomaly Detection Dashboard**.  
> Retail stores me aksar 3 badi problems aati hain: demand achanak badhna (spike), sales ka achanak gir jana (drop), aur bina sale ke stock ka gayab hona (inventory shrinkage/chori).  
> Maine is project me SQL ke window functions ka use karke Z-Score calculate kiya hai, jo pichle 14 dino ka rolling average lekar abnormal transactions ko automatically flag karta hai, aur Power BI tatha ek web dashboard ke zariye management ko instant visual alerts deta hai."*

---

## 🖥️ Part 2: Screen Demonstration (1–2 Minutes)

*(Open `dashboard.html` or your Power BI report on the screen)*

1. **Point to the Top KPI Cards:**
   > *"As you can see on the screen, the dashboard tracks 5 core enterprise metrics: Total Revenue, Total Anomalies Detected, Critical 3-Sigma Outliers, and the Estimated Financial Loss Impact. This converts raw data directly into business decision metrics."*

2. **Show the Main Time Series Chart:**
   > *"In this central line chart, the purple line represents actual daily sales, while the dashed gray line is the rolling 14-record mean. Whenever sales exceed 2.5 standard deviations from the rolling mean, my system highlights the point with a prominent red dot as a statistical anomaly."*

3. **Demonstrate the "Simulate Live Stream" Button:**
   > *(Click the '▶ Simulate Live Stream' button on `dashboard.html`)*  
   > *"To test this in a production-like environment, I built a live POS stream simulation. As you can see, new transactions are processed in real-time, and whenever an outlier occurs, the anomaly counter increments dynamically."*

4. **Show the Inventory Tab:**
   > *(Switch to the 'Inventory & Shrinkage' tab)*  
   > *"This tab specifically identifies discrepancies: if inventory drops significantly while sales are normal or zero, the system flags it as 'Inventory Shrinkage (Suspected Theft)'."*

---

## ⚙️ Part 3: Explaining the SQL Code (When Examiner Asks for Code)

*(Open [`zscore_live_view.sql`](file:///c:/project/zscore_live_view.sql))*

Explain these 3 key points:

1. **Why per-item sequence (`ROW_NUMBER()`):**
   > *"Sir/Ma'am, in a POS database, transactions of 12 items are interleaved in the raw table. If I simply did `WHERE id >= current_id - 14`, it would only take 1 past record for each item. So I used `ROW_NUMBER() OVER (PARTITION BY item ORDER BY id)` to give each item its own clean sequential row number from 1 to 90."*

2. **How Standard Deviation is computed in SQLite:**
   > *"Since SQLite lacks a native `STDDEV_SAMP()` window function, I implemented the mathematical variance identity: $\text{Var}(X) = E[X^2] - (E[X])^2$. In SQL, I computed the average of sales and the average of sales squared, and took the square root of their difference: `SQRT(avg_sq - (rolling_mean * rolling_mean))`."*

3. **Classification & Financial Impact:**
   > *"Records with $|Z| \ge 3.0$ or stockouts are marked as `CRITICAL`, while $2.5 < |Z| < 3.0$ are marked as `WARNING`. The financial impact multiplies the deviation by the product's unit price to calculate exact rupee loss (₹)."*

---

## 🎯 Part 4: Examiner Rapid-Fire Defense (Top 3 Questions)

* **Q: Why didn't you use Machine Learning like Isolation Forest?**
  > **Ans:** *"Statistical Z-Score is lightweight, zero-latency, and can be computed directly inside the SQL database engine without loading large ML models into memory. However, as future scope, Isolation Forest or LSTM can be added for complex multi-variable seasonality."*

* **Q: Why a 14-record window?**
  > **Ans:** *"A 14-record window represents 2 weeks of retail history. It is long enough to avoid being skewed by daily noise, yet agile enough to adapt to seasonal demand shifts."*

* **Q: Why Power BI?**
  > **Ans:** *"Power BI enables executive self-service reporting. Store managers can filter by item, date, or severity, drill down into shrinkage events, and export audited logs."*

---

## 🏁 Part 5: Conclusion
> *"In summary, this project combines statistical modeling, SQL engineering, and modern visual analytics to convert raw POS data into real-time operational risk prevention. Thank you, and I am now ready for any questions!"*
