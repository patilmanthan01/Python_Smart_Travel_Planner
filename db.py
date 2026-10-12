"""
Database/database.py
Database manager class implementing CRUD operations for trips, itineraries, and budgets.
Aligned with Syllabus Unit 2 (Classes, Custom Exceptions) & Unit 4 (Database Connectivity).
"""

import sqlite3
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Resolve project root for imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.config import DATABASE_PATH
from Database.schema import create_tables


# ==============================================================================
# CUSTOM EXCEPTIONS (Syllabus Unit 2.3)
# ==============================================================================
class DatabaseOperationError(Exception):
    """Raised when an SQLite query or transaction fails."""
    pass


class TripNotFoundError(DatabaseOperationError):
    """Raised when a query requests a trip_id that does not exist."""
    pass


# ==============================================================================
# DATABASE MANAGER CLASS (Syllabus Unit 2.1 & Unit 4.1)
# ==============================================================================
class DatabaseManager:
    """Encapsulates all database interactions for the Smart Travel Planner."""

    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = str(db_path)
        # Ensure tables exist on initialization
        create_tables(self.db_path)

    def _get_connection(self) -> sqlite3.Connection:
        """Helper method to create and configure a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name like dicts
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    # --------------------------------------------------------------------------
    # CREATE OPERATIONS
    # --------------------------------------------------------------------------
    def save_full_trip(
        self,
        city: str,
        days: int,
        total_budget: float,
        itinerary_items: List[Dict[str, Any]],
        budget_breakdown: Dict[str, float]
    ) -> int:
        """
        Saves a trip, its daily scheduled activities, and budget split atomically.
        Uses SQLite transactions (commit/rollback).
        """
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()

                # 1. Insert Trip Record
                cursor.execute(
                    """
                    INSERT INTO trips (city, days, total_budget)
                    VALUES (?, ?, ?)
                    """,
                    (city, days, total_budget)
                )
                trip_id = cursor.lastrowid

                # 2. Insert Itinerary Items
                items_to_insert = [
                    (
                        trip_id,
                        item["day_number"],
                        item["time_slot"],
                        item["place_name"],
                        item["category"],
                        item.get("estimated_cost", 0.0)
                    )
                    for item in itinerary_items
                ]
                cursor.executemany(
                    """
                    INSERT INTO itinerary_items 
                    (trip_id, day_number, time_slot, place_name, category, estimated_cost)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    items_to_insert
                )

                # 3. Insert Budget Breakdown
                cursor.execute(
                    """
                    INSERT INTO budget_breakdown 
                    (trip_id, stay_cost, food_cost, travel_cost, sightseeing_cost)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        trip_id,
                        budget_breakdown.get("stay", 0.0),
                        budget_breakdown.get("food", 0.0),
                        budget_breakdown.get("travel", 0.0),
                        budget_breakdown.get("sightseeing", 0.0)
                    )
                )

                return trip_id

        except sqlite3.Error as e:
            raise DatabaseOperationError(f"Failed to save trip transaction: {e}") from e
        finally:
            conn.close()

    # --------------------------------------------------------------------------
    # READ OPERATIONS
    # --------------------------------------------------------------------------
    def get_all_trips(self) -> List[Dict[str, Any]]:
        """Fetches all past trips ordered from newest to oldest."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trips ORDER BY trip_id DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseOperationError(f"Failed to fetch trips: {e}") from e
        finally:
            conn.close()

    def get_trip_details(self, trip_id: int) -> Dict[str, Any]:
        """
        Fetches a complete trip package: master trip details,
        itinerary items, and the budget breakdown.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Master Trip Query
            cursor.execute("SELECT * FROM trips WHERE trip_id = ?", (trip_id,))
            trip_row = cursor.fetchone()
            if not trip_row:
                raise TripNotFoundError(f"Trip with ID {trip_id} not found.")

            # Itinerary Items Query
            cursor.execute(
                """
                SELECT day_number, time_slot, place_name, category, estimated_cost
                FROM itinerary_items
                WHERE trip_id = ?
                ORDER BY day_number ASC, 
                    CASE time_slot 
                        WHEN 'Morning' THEN 1 
                        WHEN 'Afternoon' THEN 2 
                        WHEN 'Evening' THEN 3 
                    END
                """,
                (trip_id,)
            )
            items = [dict(row) for row in cursor.fetchall()]

            # Budget Breakdown Query
            cursor.execute(
                """
                SELECT stay_cost, food_cost, travel_cost, sightseeing_cost
                FROM budget_breakdown
                WHERE trip_id = ?
                """,
                (trip_id,)
            )
            budget_row = cursor.fetchone()

            return {
                "trip": dict(trip_row),
                "itinerary": items,
                "budget": dict(budget_row) if budget_row else {}
            }
        except sqlite3.Error as e:
            raise DatabaseOperationError(f"Failed to load details for trip {trip_id}: {e}") from e
        finally:
            conn.close()

    # --------------------------------------------------------------------------
    # DELETE OPERATION
    # --------------------------------------------------------------------------
    def delete_trip(self, trip_id: int) -> bool:
        """Deletes a trip by ID. Cascades to itinerary items and budget breakdown."""
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM trips WHERE trip_id = ?", (trip_id,))
                if cursor.rowcount == 0:
                    raise TripNotFoundError(f"Cannot delete: Trip ID {trip_id} does not exist.")
                return True
        except sqlite3.Error as e:
            raise DatabaseOperationError(f"Failed to delete trip {trip_id}: {e}") from e
        finally:
            conn.close()


if __name__ == "__main__":
    # Quick standalone sanity test
    db = DatabaseManager()
    print("[OK] DatabaseManager initialized and operational.") 
