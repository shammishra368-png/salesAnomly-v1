"""
generate_data.py
-----------------
Generates 90 days of realistic daily sales, inventory levels, and financial records
for an Indian Metro Superstore across 12 high-velocity FMCG items.
Stores data in retail.db (sales_data table).

Real-World Domain Properties:
- Weekly supplier replenishment cycles with realistic lead times
- Gaussian demand distributions reflecting typical supermarket POS velocity
- Ground-truth operational anomalies:
  * Festival / Flash demand surges (Spikes)
  * System outage / POS billing dropouts (Drops)
  * Stockout / Out-of-stock depletion
  * Pilferage, transit damage, leakage (Inventory Shrinkage)
"""

import sqlite3
import random
from datetime import date, timedelta

DB_PATH = "retail.db"
NUM_DAYS = 90
START_DATE = date.today() - timedelta(days=NUM_DAYS)

# 12 authentic supermarket FMCG staples with retail parameters in Indian Rupees (₹)
ITEMS = [
    {"name": "Amul Taaza Milk (1L)",        "sales_mean": 85,  "sales_std": 8,  "inv_start": 550, "unit_price": 66.00},
    {"name": "Aashirvaad Atta (10kg)",      "sales_mean": 38,  "sales_std": 4,  "inv_start": 280, "unit_price": 420.00},
    {"name": "Fortune Sunflower Oil (1L)",  "sales_mean": 44,  "sales_std": 5,  "inv_start": 320, "unit_price": 145.00},
    {"name": "India Gate Rice (5kg)",       "sales_mean": 30,  "sales_std": 4,  "inv_start": 240, "unit_price": 380.00},
    {"name": "Tata Tea Gold (500g)",        "sales_mean": 40,  "sales_std": 4,  "inv_start": 260, "unit_price": 260.00},
    {"name": "Madhur Pure Sugar (1kg)",     "sales_mean": 55,  "sales_std": 6,  "inv_start": 360, "unit_price": 46.00},
    {"name": "Tata Toor Dal (1kg)",         "sales_mean": 32,  "sales_std": 4,  "inv_start": 230, "unit_price": 175.00},
    {"name": "Amul Butter (500g)",          "sales_mean": 48,  "sales_std": 5,  "inv_start": 310, "unit_price": 285.00},
    {"name": "Surf Excel Detergent (1kg)",  "sales_mean": 34,  "sales_std": 4,  "inv_start": 250, "unit_price": 140.00},
    {"name": "Fresh Farm Eggs (Tray 30)",   "sales_mean": 42,  "sales_std": 4,  "inv_start": 280, "unit_price": 210.00},
    {"name": "Britannia Good Day Cookies",  "sales_mean": 65,  "sales_std": 6,  "inv_start": 420, "unit_price": 40.00},
    {"name": "Maggi Noodles (Pack of 8)",   "sales_mean": 58,  "sales_std": 6,  "inv_start": 380, "unit_price": 112.00},
]

# Real-world benchmark anomaly scenarios (Festivals, System Glitches, Transit Loss, Stockout)
INJECTED_ANOMALIES = [
    ("Amul Taaza Milk (1L)",        22, "spike",      4.2),  # Festive bulk morning demand surge
    ("Aashirvaad Atta (10kg)",      35, "drop",       0.0),  # POS barcode scanner unmapped glitch
    ("Fortune Sunflower Oil (1L)",  44, "shrinkage",  110),  # Warehouse canister puncture / leakage
    ("India Gate Rice (5kg)",       53, "spike",      4.5),  # Wedding catering bulk purchase
    ("Tata Toor Dal (1kg)",         62, "stockout",   0),    # Distributor shipment delay
    ("Maggi Noodles (Pack of 8)",   71, "spike",      4.3),  # Flash weekend discount surge
    ("Amul Butter (500g)",          79, "shrinkage",  85),   # Cold-storage transit pilferage
    ("Tata Tea Gold (500g)",        85, "drop",       0.0),  # Network billing downtime
]


def build_dataset():
    random.seed(42)  # Deterministic seed for reproducible evaluation
    rows = []
    inventory = {item["name"]: item["inv_start"] for item in ITEMS}
    injected_lookup = {(a[0], a[1]): a for a in INJECTED_ANOMALIES}

    for day_offset in range(NUM_DAYS):
        current_date = START_DATE + timedelta(days=day_offset)
        for item in ITEMS:
            name = item["name"]
            unit_price = item["unit_price"]
            base_sales = max(0, round(random.gauss(item["sales_mean"], item["sales_std"])))

            key = (name, day_offset)
            is_anomaly = 0
            if key in injected_lookup:
                _, _, atype, factor = injected_lookup[key]
                if atype == "spike":
                    base_sales = round(item["sales_mean"] * factor)
                    is_anomaly = 1
                elif atype == "drop":
                    base_sales = 0
                    is_anomaly = 1
                elif atype == "shrinkage":
                    inventory[name] = max(0, inventory[name] - int(factor))
                    is_anomaly = 1
                elif atype == "stockout":
                    inventory[name] = 0
                    base_sales = 0
                    is_anomaly = 1

            # Standard inventory decrement
            inventory[name] -= base_sales

            # Scheduled weekly store restocking (Every Monday equivalent)
            if day_offset % 7 == 0:
                inventory[name] += item["sales_mean"] * 8

            inventory[name] = max(0, inventory[name])
            revenue = round(base_sales * unit_price, 2)
            stock_value = round(inventory[name] * unit_price, 2)

            rows.append((
                current_date.isoformat(),
                name,
                base_sales,
                inventory[name],
                unit_price,
                revenue,
                stock_value,
                is_anomaly,
            ))
    return rows


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS sales_data")
    cur.execute("""
        CREATE TABLE sales_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_date TEXT NOT NULL,
            item TEXT NOT NULL,
            sales INTEGER NOT NULL,
            inventory INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            revenue REAL NOT NULL,
            stock_value REAL NOT NULL,
            is_injected_anomaly INTEGER NOT NULL DEFAULT 0
        )
    """)
    rows = build_dataset()
    cur.executemany("""
        INSERT INTO sales_data (
            record_date, item, sales, inventory, unit_price, revenue, stock_value, is_injected_anomaly
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    conn.close()
    print(f"[SUCCESS] Real-world retail dataset generated: {len(rows)} transactions.")
    print(f"          Date range: {rows[0][0]} to {rows[-1][0]} (Leading directly to today)")
    print(f"          Database saved: {DB_PATH}")


if __name__ == "__main__":
    main()
