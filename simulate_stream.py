"""
simulate_stream.py
-------------------
Simulates a live Point-of-Sale (POS) feed by inserting one new sales record
into retail.db every 5 seconds (or 1 second with --fast).

Supports multi-metric anomaly simulation:
- Sales Spikes (surge in customer purchases)
- Sales Drops (zero-sales events)
- Inventory Shrinkage (theft / damage where stock drops without sales)
- Inventory Stockouts (stock hitting 0)

Usage:
    python simulate_stream.py           # 5-second interval
    python simulate_stream.py --fast    # 1-second interval
"""

import sqlite3
import random
import argparse
import time
from datetime import date, timedelta

DB_PATH = "retail.db"

# 12 grocery items with baseline parameters and unit prices (INR - Indian Rupees ₹)
ITEMS = [
    {"name": "Milk (1L)",       "sales_mean": 80,  "sales_std": 8,  "inv_start": 500, "unit_price": 60.00},
    {"name": "Bread (Loaf)",    "sales_mean": 60,  "sales_std": 6,  "inv_start": 300, "unit_price": 40.00},
    {"name": "Eggs (Dozen)",    "sales_mean": 50,  "sales_std": 5,  "inv_start": 400, "unit_price": 84.00},
    {"name": "Rice (5kg)",      "sales_mean": 30,  "sales_std": 4,  "inv_start": 250, "unit_price": 320.00},
    {"name": "Chicken (1kg)",   "sales_mean": 40,  "sales_std": 5,  "inv_start": 200, "unit_price": 240.00},
    {"name": "Toilet Paper",    "sales_mean": 45,  "sales_std": 5,  "inv_start": 350, "unit_price": 120.00},
    {"name": "Cooking Oil",     "sales_mean": 35,  "sales_std": 4,  "inv_start": 220, "unit_price": 150.00},
    {"name": "Sugar (1kg)",     "sales_mean": 38,  "sales_std": 4,  "inv_start": 260, "unit_price": 45.00},
    {"name": "Tea (250g)",      "sales_mean": 42,  "sales_std": 5,  "inv_start": 280, "unit_price": 110.00},
    {"name": "Detergent",       "sales_mean": 28,  "sales_std": 3,  "inv_start": 180, "unit_price": 95.00},
    {"name": "Biscuits",        "sales_mean": 55,  "sales_std": 6,  "inv_start": 320, "unit_price": 30.00},
    {"name": "Onions (1kg)",    "sales_mean": 65,  "sales_std": 7,  "inv_start": 310, "unit_price": 35.00},
]

ANOMALY_CHANCE = 0.10  # 10% chance of injecting an operational anomaly


def get_latest_date(conn):
    cur = conn.cursor()
    cur.execute("SELECT MAX(record_date) FROM sales_data")
    row = cur.fetchone()
    if row and row[0]:
        return date.fromisoformat(row[0])
    return date.today()


def get_latest_inventory(conn, item_name):
    cur = conn.cursor()
    cur.execute(
        "SELECT inventory FROM sales_data WHERE item = ? ORDER BY id DESC LIMIT 1",
        (item_name,),
    )
    row = cur.fetchone()
    return row[0] if row else None


def generate_one_record(conn, item, current_date, day_counter):
    name = item["name"]
    unit_price = item["unit_price"]

    # Normal sales draw from Gaussian baseline
    sales = max(0, round(random.gauss(item["sales_mean"], item["sales_std"])))
    is_anomaly = 0
    anomaly_desc = ""

    last_inv = get_latest_inventory(conn, name)
    if last_inv is None:
        last_inv = item["inv_start"]
    inventory = last_inv - sales

    # Weekly restock
    if day_counter % 7 == 0:
        inventory += item["sales_mean"] * 8

    # Random anomaly injection
    if random.random() < ANOMALY_CHANCE:
        atype = random.choice(["spike", "drop", "shrinkage", "stockout"])
        if atype == "spike":
            sales = round(item["sales_mean"] * random.uniform(3.5, 4.8))
            inventory = max(0, inventory - (sales - item["sales_mean"]))
            is_anomaly = 1
            anomaly_desc = " [SALES SPIKE]"
        elif atype == "drop":
            sales = 0
            is_anomaly = 1
            anomaly_desc = " [SALES DROP]"
        elif atype == "shrinkage":
            loss = round(item["sales_mean"] * 2.0)
            inventory = max(0, inventory - loss)
            is_anomaly = 1
            anomaly_desc = f" [SHRINKAGE/THEFT -{loss} units]"
        elif atype == "stockout":
            inventory = 0
            sales = 0
            is_anomaly = 1
            anomaly_desc = " [STOCKOUT]"

    inventory = max(0, inventory)
    revenue = round(sales * unit_price, 2)
    stock_value = round(inventory * unit_price, 2)

    return (
        current_date.isoformat(),
        name,
        sales,
        inventory,
        unit_price,
        revenue,
        stock_value,
        is_anomaly,
        anomaly_desc,
    )


def main():
    parser = argparse.ArgumentParser(description="Simulate live POS retail transactions")
    parser.add_argument("--fast", action="store_true", help="1-second stream interval")
    args = parser.parse_args()
    interval = 1 if args.fast else 5

    conn = sqlite3.connect(DB_PATH)
    latest_date = get_latest_date(conn)
    current_date = latest_date + timedelta(days=1)

    item_index = 0
    day_counter = 0

    print("=" * 70)
    print("LIVE POS & INVENTORY STREAM SIMULATOR")
    print("=" * 70)
    print(f"Starting simulated stream from date: {current_date.isoformat()}")
    print(f"Interval: {interval}s per record | Anomaly probability: {ANOMALY_CHANCE*100:.0f}%")
    print("Press Ctrl+C to stop stream at any time.")
    print("-" * 70)

    try:
        while True:
            item = ITEMS[item_index]
            rec = generate_one_record(conn, item, current_date, day_counter)

            # Insert all fields matching upgraded sales_data schema
            conn.execute("""
                INSERT INTO sales_data (
                    record_date, item, sales, inventory, unit_price, revenue, stock_value, is_injected_anomaly
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, rec[:8])
            conn.commit()

            flag_str = rec[8]
            print(
                f"[STREAM] {rec[0]} | {rec[1]:<16s} | "
                f"Sales: {rec[2]:>3d} | Stock: {rec[3]:>4d} | Rev: ₹{rec[5]:>8.2f}{flag_str}"
            )

            item_index += 1
            if item_index >= len(ITEMS):
                item_index = 0
                day_counter += 1
                current_date += timedelta(days=1)

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n[STREAM] Simulator paused by user.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
