# db_utils.py

import sqlite3
from typing import List, Tuple, Optional

from config import DB_FILE
from data_points import POIs, GAS_STATIONS, RESTAURANTS, HOTELS, ATMS


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            lat REAL,
            lon REAL,
            category TEXT
        )
        """
    )

    cur.execute("SELECT COUNT(*) AS c FROM locations")
    count = cur.fetchone()["c"]

    total_new_points = (
        len(POIs) + len(GAS_STATIONS) + len(RESTAURANTS) + len(ATMS) + len(HOTELS)
    )

    if count < total_new_points:
        print(
            f"♻️ Detected old or empty DB (Count: {count}). "
            f"Reseeding {total_new_points} points..."
        )
        cur.execute("DELETE FROM locations")

        def insert_dict(data_dict, category):
            for name, (lat, lon) in data_dict.items():
                cur.execute(
                    "INSERT OR IGNORE INTO locations (name, lat, lon, category) "
                    "VALUES (?, ?, ?, ?)",
                    (name, lat, lon, category),
                )

        insert_dict(POIs, "poi")
        insert_dict(GAS_STATIONS, "gas")
        insert_dict(RESTAURANTS, "restaurant")
        insert_dict(ATMS, "atm")
        insert_dict(HOTELS, "hotel")

        conn.commit()
        print("✅ Database refreshed with new coordinates.")
    else:
        print(f"✅ Database already contains {count} points.")

    conn.close()


def get_point_by_name(name: str) -> Optional[Tuple[float, float]]:
    # in-memory shortcuts
    if name in POIs:
        return POIs[name]
    if name in GAS_STATIONS:
        return GAS_STATIONS[name]
    if name in RESTAURANTS:
        return RESTAURANTS[name]
    if name in HOTELS:
        return HOTELS[name]
    if name in ATMS:
        return ATMS[name]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT lat, lon FROM locations WHERE name = ?", (name,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row["lat"], row["lon"]
    return None


def get_points_by_category(category: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT name, lat, lon FROM locations WHERE category = ?", (category,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows
