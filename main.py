"""
main.py
Application Entry Point for the Smart Travel Planner (MMR Edition).
Initializes database persistence, validates runtime dependencies, and launches the desktop GUI.
Aligned with Syllabus Unit 1.1 (Python Basics), Unit 2.3 (Exception Handling), & Unit 4.1 (GUI).
"""

import sys
import os
from pathlib import Path

# Resolve base project directory and register it in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.config import DATA_DIR, DATABASE_PATH, PLACES_JSON_PATH
from Database.schema import create_tables
from GUI.dashboard import TravelPlannerDashboard


def bootstrap_environment() -> bool:
    """
    Verifies project file structure, storage directories,
    and initializes SQLite database tables prior to UI startup.
    """
    print("[1/3] Checking environment & directories...")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not PLACES_JSON_PATH.exists():
        print(f"[WARNING] places.json not found at {PLACES_JSON_PATH}. "
              "Some catalog features may fall back to default placeholders.")
    else:
        print(f"[OK] Verified places dataset at: {PLACES_JSON_PATH}")

    print("[2/3] Checking & initializing database schema...")
    try:
        create_tables(DATABASE_PATH)
        print(f"[OK] Database initialized at: {DATABASE_PATH}")
    except Exception as db_err:
        print(f"[CRITICAL ERROR] Failed to initialize SQLite schema: {db_err}")
        return False

    return True


def main():
    """Main launcher routine."""
    print("=" * 60)
    print(" Smart Travel Planner — Mumbai • Navi Mumbai • Thane ")
    print("=" * 60)

    # 1. Environment bootstrap
    if not bootstrap_environment():
        print("[ABORT] Startup terminated due to initialization failures.")
        sys.exit(1)

    # 2. Launch GUI Dashboard
    print("[3/3] Launching Desktop GUI Dashboard...")
    try:
        app = TravelPlannerDashboard()
        app.mainloop()
        print("\n[INFO] Application closed successfully.")
    except KeyboardInterrupt:
        print("\n[INFO] Application interrupted by user.")
    except Exception as app_err:
        print(f"\n[FATAL ERROR] An unexpected error occurred while running the app: {app_err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
