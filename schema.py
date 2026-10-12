"""
Database/schema.py
Defines the SQLite database schema and table initialization for Smart Travel Planner.
Aligned with Syllabus Unit 2 (Exception Handling) & Unit 4 (Database Connectivity).
"""

import sqlite3
import sys
from pathlib import Path

# Resolve base directory to ensure config can be imported from any working directory
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.config import DATABASE_PATH


# ==============================================================================
# SQL TABLE DEFINITIONS
# ==============================================================================

# 1. Trips master table: stores user travel request summaries
CREATE_TRIPS_TABLE = """
CREATE TABLE IF NOT EXISTS trips (
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL CHECK(city IN ('Mumbai', 'Navi Mumbai', 'Thane')),
    days INTEGER NOT NULL CHECK(days > 0),
    total_budget REAL NOT NULL CHECK(total_budget > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# 2. Itinerary items table: stores sequential day-wise activities
CREATE_ITINERARY_ITEMS_TABLE = """
CREATE TABLE IF NOT EXISTS itinerary_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER NOT NULL,
    day_number INTEGER NOT NULL CHECK(day_number > 0),
    time_slot TEXT NOT NULL CHECK(time_slot IN ('Morning', 'Afternoon', 'Evening')),
    place_name TEXT NOT NULL,
    category TEXT NOT NULL,
    estimated_cost REAL DEFAULT 0 CHECK(estimated_cost >= 0),
    FOREIGN KEY (trip_id) REFERENCES trips (trip_id) ON DELETE CASCADE
);
"""

# 3. Budget breakdown table: stores categorized costs for Matplotlib chart rendering
CREATE_BUDGET_BREAKDOWN_TABLE = """
CREATE TABLE IF NOT EXISTS budget_breakdown (
    budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER NOT NULL UNIQUE,
    stay_cost REAL NOT NULL CHECK(stay_cost >= 0),
    food_cost REAL NOT NULL CHECK(food_cost >= 0),
    travel_cost REAL NOT NULL CHECK(travel_cost >= 0),
    sightseeing_cost REAL NOT NULL CHECK(sightseeing_cost >= 0),
    FOREIGN KEY (trip_id) REFERENCES trips (trip_id) ON DELETE CASCADE
);
"""

# Index creation for optimizing queries filtering by trip_id
CREATE_INDEX_TRIP_ITEMS = """
CREATE INDEX IF NOT EXISTS idx_itinerary_trip_id ON itinerary_items (trip_id);
"""

CREATE_INDEX_BUDGET_TRIP = """
CREATE INDEX IF NOT EXISTS idx_budget_trip_id ON budget_breakdown (trip_id);
"""


# ==============================================================================
# SCHEMA INITIALIZATION FUNCTIONS
# ==============================================================================

def create_tables(db_path=DATABASE_PATH):
    """
    Connects to SQLite database and creates the required tables and indexes.
    Enforces foreign keys via PRAGMA command.
    """
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Enforce foreign key constraints in SQLite
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Execute table generation statements
        cursor.execute(CREATE_TRIPS_TABLE)
        cursor.execute(CREATE_ITINERARY_ITEMS_TABLE)
        cursor.execute(CREATE_BUDGET_BREAKDOWN_TABLE)

        # Execute index statements
        cursor.execute(CREATE_INDEX_TRIP_ITEMS)
        cursor.execute(CREATE_INDEX_BUDGET_TRIP)

        connection.commit()
        print(f"[SUCCESS] Database schema created successfully at: {db_path}")

    except sqlite3.DatabaseError as db_err:
        print(f"[DATABASE ERROR] Failed to initialize schema: {db_err}")
        if connection:
            connection.rollback()
        raise db_err

    except Exception as exc:
        print(f"[UNEXPECTED ERROR] An error occurred while creating tables: {exc}")
        if connection:
            connection.rollback()
        raise exc

    finally:
        if connection:
            connection.close()


def drop_tables(db_path=DATABASE_PATH):
    """
    Drops all project tables. Useful for reset or unit testing.
    """
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        cursor.execute("PRAGMA foreign_keys = OFF;")
        cursor.execute("DROP TABLE IF EXISTS budget_breakdown;")
        cursor.execute("DROP TABLE IF EXISTS itinerary_items;")
        cursor.execute("DROP TABLE IF EXISTS trips;")
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        connection.commit()
        print(f"[INFO] Existing tables dropped cleanly from: {db_path}")
    except sqlite3.Error as e:
        print(f"[ERROR] Could not drop tables: {e}")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    create_tables()
