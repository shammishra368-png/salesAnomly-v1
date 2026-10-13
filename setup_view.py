"""
setup_view.py
--------------
Reads zscore_live_view.sql and executes it against retail.db to create
(or recreate) the zscore_live_view SQL VIEW.

Run this once after generate_data.py, before starting the monitor or
refreshing Power BI.

Usage:
    python setup_view.py
"""

import sqlite3
import os

DB_PATH = "retail.db"
SQL_FILE = "zscore_live_view.sql"


def main():
    # Verify the database exists
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database '{DB_PATH}' not found.")
        print("        Run 'python generate_data.py' first to create it.")
        return

    # Read the SQL file
    if not os.path.exists(SQL_FILE):
        print(f"[ERROR] SQL file '{SQL_FILE}' not found.")
        return

    with open(SQL_FILE, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # Execute the SQL statements (DROP VIEW + CREATE VIEW)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(sql_script)
    conn.close()

    print(f"[OK] View 'zscore_live_view' created/recreated in {DB_PATH}")
    print("     You can now run alert_monitor.py or refresh Power BI.")


if __name__ == "__main__":
    main()
