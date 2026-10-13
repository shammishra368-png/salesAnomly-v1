-- zscore_live_view.sql
-- ----------------------------------------------------------------------
-- SQL VIEW: Enterprise Sales & Inventory Anomaly Detection Engine
-- ----------------------------------------------------------------------
-- Features:
-- 1. Rolling 14-record statistical baselines per item (Mean & Standard Deviation)
-- 2. Parametric Z-Score formulation for both Sales and Inventory
-- 3. Multi-tier classification (Spikes, Drops, Stockouts, Critical Low, Shrinkage)
-- 4. Anomaly Severity tiering: CRITICAL vs WARNING vs NORMAL
-- 5. Business & Financial impact estimation (Revenue at risk / Lost sales)
-- ----------------------------------------------------------------------

DROP VIEW IF EXISTS zscore_live_view;

CREATE VIEW zscore_live_view AS
WITH ranked AS (
    SELECT
        id,
        record_date,
        item,
        sales,
        inventory,
        unit_price,
        revenue,
        stock_value,
        is_injected_anomaly,
        ROW_NUMBER() OVER (PARTITION BY item ORDER BY id) AS rn
    FROM sales_data
),
stats AS (
    SELECT
        r.id,
        r.record_date,
        r.item,
        r.sales,
        r.inventory,
        r.unit_price,
        r.revenue,
        r.stock_value,
        r.is_injected_anomaly,
        -- Rolling 14-record mean of Sales
        (
            SELECT AVG(w.sales * 1.0)
            FROM ranked w
            WHERE w.item = r.item AND w.rn < r.rn AND w.rn >= r.rn - 14
        ) AS rolling_mean,
        -- Rolling 14-record squared mean of Sales
        (
            SELECT AVG(w.sales * 1.0 * w.sales)
            FROM ranked w
            WHERE w.item = r.item AND w.rn < r.rn AND w.rn >= r.rn - 14
        ) AS avg_sq,
        -- Rolling 14-record mean of Inventory
        (
            SELECT AVG(w.inventory * 1.0)
            FROM ranked w
            WHERE w.item = r.item AND w.rn < r.rn AND w.rn >= r.rn - 14
        ) AS inv_rolling_mean,
        -- Rolling 14-record squared mean of Inventory
        (
            SELECT AVG(w.inventory * 1.0 * w.inventory)
            FROM ranked w
            WHERE w.item = r.item AND w.rn < r.rn AND w.rn >= r.rn - 14
        ) AS inv_avg_sq
    FROM ranked r
),
computed AS (
    SELECT
        id,
        record_date,
        item,
        sales,
        inventory,
        unit_price,
        revenue,
        stock_value,
        is_injected_anomaly,
        ROUND(rolling_mean, 2) AS rolling_mean,
        ROUND(CASE
            WHEN avg_sq IS NULL OR rolling_mean IS NULL THEN 0
            WHEN (avg_sq - (rolling_mean * rolling_mean)) < 0 THEN 0
            ELSE SQRT(avg_sq - (rolling_mean * rolling_mean))
        END, 2) AS rolling_std,
        ROUND(CASE
            WHEN rolling_mean IS NULL OR (avg_sq - (rolling_mean * rolling_mean)) <= 0 THEN 0
            ELSE (sales - rolling_mean) / SQRT(avg_sq - (rolling_mean * rolling_mean))
        END, 2) AS z_score,
        ROUND(inv_rolling_mean, 2) AS inv_rolling_mean,
        ROUND(CASE
            WHEN inv_avg_sq IS NULL OR inv_rolling_mean IS NULL THEN 0
            WHEN (inv_avg_sq - (inv_rolling_mean * inv_rolling_mean)) < 0 THEN 0
            ELSE SQRT(inv_avg_sq - (inv_rolling_mean * inv_rolling_mean))
        END, 2) AS inv_rolling_std,
        ROUND(CASE
            WHEN inv_rolling_mean IS NULL OR (inv_avg_sq - (inv_rolling_mean * inv_rolling_mean)) <= 0 THEN 0
            ELSE (inventory - inv_rolling_mean) / SQRT(inv_avg_sq - (inv_rolling_mean * inv_rolling_mean))
        END, 2) AS inv_z_score
    FROM stats
)
SELECT
    id,
    record_date,
    item,
    sales,
    inventory,
    unit_price,
    revenue,
    stock_value,
    is_injected_anomaly,
    rolling_mean,
    rolling_std,
    z_score,
    inv_rolling_mean,
    inv_rolling_std,
    inv_z_score,
    -- Detailed Anomaly Classification
    CASE
        WHEN z_score > 2.5 THEN 'Sales Spike'
        WHEN z_score < -2.2 OR (sales = 0 AND rolling_mean >= 15) THEN 'Sales Drop'
        WHEN (inv_z_score < -2.0 OR (inv_rolling_mean IS NOT NULL AND inventory < inv_rolling_mean * 0.50)) AND sales <= rolling_mean * 1.5 THEN 'Inventory Shrinkage (Theft)'
        WHEN inventory <= 0 THEN 'Inventory Stockout'
        WHEN inventory > 0 AND rolling_mean > 0 AND inventory < (rolling_mean * 2.0) THEN 'Critical Low Stock'
        ELSE 'Normal'
    END AS anomaly_type,
    -- Binary Anomaly Flag
    CASE
        WHEN ABS(z_score) > 2.2 THEN 1
        WHEN sales = 0 AND rolling_mean >= 15 THEN 1
        WHEN inventory <= 0 THEN 1
        WHEN inventory > 0 AND rolling_mean > 0 AND inventory < (rolling_mean * 2.0) THEN 1
        WHEN (inv_z_score < -2.0 OR (inv_rolling_mean IS NOT NULL AND inventory < inv_rolling_mean * 0.50)) AND sales <= rolling_mean * 1.5 THEN 1
        ELSE 0
    END AS is_flagged,
    -- Severity Ranking
    CASE
        WHEN ABS(z_score) >= 3.0 OR inventory <= 0 OR (sales = 0 AND rolling_mean >= 20) OR ((inv_z_score < -2.0 OR (inv_rolling_mean IS NOT NULL AND inventory < inv_rolling_mean * 0.50)) AND sales <= rolling_mean * 1.5) THEN 'CRITICAL'
        WHEN ABS(z_score) > 2.2 OR (inventory > 0 AND rolling_mean > 0 AND inventory < (rolling_mean * 2.0)) THEN 'WARNING'
        ELSE 'NORMAL'
    END AS severity,
    -- Estimated Financial Impact (₹ INR Revenue Deviation / Loss)
    ROUND(CASE
        WHEN z_score > 2.5 THEN (sales - rolling_mean) * unit_price
        WHEN z_score < -2.2 OR (sales = 0 AND rolling_mean >= 15) THEN (rolling_mean - sales) * unit_price * -1
        WHEN inventory <= 0 THEN rolling_mean * unit_price * -1
        WHEN (inv_z_score < -2.0 OR (inv_rolling_mean IS NOT NULL AND inventory < inv_rolling_mean * 0.50)) AND sales <= rolling_mean * 1.5 THEN (inv_rolling_mean - inventory) * unit_price * -1
        ELSE 0
    END, 2) AS financial_impact
FROM computed
ORDER BY id;
