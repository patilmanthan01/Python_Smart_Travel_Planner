"""
Logic/smart_planner.py
Central orchestrator integrating local datasets, budget calculations, 
itinerary queues, packing recommendations, and database persistence.
Aligned with Syllabus Unit 2 (OOP, File I/O, Exceptions), Unit 3 (Queues), & Unit 4 (DB).
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Resolve project root for imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.config import PLACES_JSON_PATH, ALLOWED_CITIES
from Database.database import DatabaseManager
from Logic.budget import BudgetCalculator
from Logic.itinerary import ItineraryBuilder


# ==============================================================================
# CUSTOM EXCEPTIONS (Syllabus Unit 2.3)
# ==============================================================================
class PlannerConfigurationError(Exception):
    """Raised when planner encounters corrupted files or missing datasets."""
    pass


# ==============================================================================
# SMART TRAVEL PLANNER COORDINATOR (Syllabus Unit 2.1)
# ==============================================================================
class SmartTravelPlanner:
    """
    Central controller that brings together user inputs, catalog data,
    financial allocations, scheduling algorithms, and database storage.
    """

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager if db_manager else DatabaseManager()
        self.places_catalog = self._load_places_from_json()

    def _load_places_from_json(self) -> List[Dict[str, Any]]:
        """
        Loads and parses regional destinations from places.json.
        Covers File Handling & Text Processing (Syllabus Unit 2.2).
        """
        if not PLACES_JSON_PATH.exists():
            raise PlannerConfigurationError(f"Dataset missing at {PLACES_JSON_PATH}")

        try:
            with open(PLACES_JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("destinations", [])
        except json.JSONDecodeError as err:
            raise PlannerConfigurationError(f"Error reading places.json: {err}") from err
        except OSError as err:
            raise PlannerConfigurationError(f"File system error reading places: {err}") from err

    def generate_packing_checklist(self, weather_condition: str = "Clear", days: int = 1) -> List[str]:
        """
        Generates a tailored packing checklist based on trip length
        and current weather conditions (e.g. rain, heat).
        """
        # Essential base items
        checklist = [
            "Government Photo ID & College ID",
            "Smartphone & Fast Power Bank",
            "Reusable Water Bottle",
            f"Clothing sets for {days} day(s)",
            "Basic First-Aid & Personal Medicines"
        ]

        weather_lower = weather_condition.lower()

        # Dynamic recommendations based on weather
        if "rain" in weather_lower or "drizzle" in weather_lower or "thunderstorm" in weather_lower:
            checklist.extend([
                "Compact Umbrella / Windproof Raincoat",
                "Waterproof Phone Pouch",
                "Quick-dry footwear (Floaters/Sandals)",
                "Ziploc waterproof bags for electronics"
            ])
        elif "cloud" in weather_lower:
            checklist.append("Light windbreaker jacket")
        else:
            # Sunny / Humid coastal MMR weather
            checklist.extend([
                "Sunglasses with UV protection",
                "Sunscreen (SPF 50+) & Lip balm",
                "Breathable cotton cap or hat",
                "Hand towel / Wet wipes"
            ])

        return checklist

    def plan_trip(
        self,
        city: str,
        days: int,
        budget: float,
        save_to_db: bool = True,
        weather_condition: str = "Clear"
    ) -> Dict[str, Any]:
        """
        Complete end-to-end trip generation workflow:
        1. Validates inputs against target boundaries (Mumbai, Navi Mumbai, Thane).
        2. Calculates budget split and tier.
        3. Schedules day-by-day activities using queue algorithms.
        4. Compiles weather-responsive packing suggestions.
        5. Persists the complete package to SQLite database if requested.
        """
        # 1. Validation
        city_normalized = city.strip().title()
        if city_normalized not in ALLOWED_CITIES:
            raise ValueError(f"City '{city}' is not supported. Choose from: {ALLOWED_CITIES}")

        # 2. Budget Logic (NumPy & Pandas operations)
        budget_calc = BudgetCalculator(total_budget=budget, total_days=days)
        budget_summary = budget_calc.get_summary()
        budget_split = budget_summary["category_split"]

        # 3. Scheduling Logic (Queue operations)
        builder = ItineraryBuilder(
            city=city_normalized,
            days=days,
            available_places=self.places_catalog
        )
        itinerary_schedule = builder.build_schedule()

        # 4. Activity Expense Verification
        activity_check = budget_calc.validate_activity_expenses(itinerary_schedule)

        # 5. Packing Checklist
        packing_list = self.generate_packing_checklist(weather_condition, days=days)

        # 6. Database Persistence (Atomic Transaction)
        saved_trip_id = None
        if save_to_db:
            saved_trip_id = self.db.save_full_trip(
                city=city_normalized,
                days=days,
                total_budget=budget,
                itinerary_items=itinerary_schedule,
                budget_breakdown=budget_split
            )

        # 7. Package complete response
        return {
            "trip_id": saved_trip_id,
            "city": city_normalized,
            "days": days,
            "total_budget": budget,
            "tier": budget_summary["tier"],
            "budget_breakdown": budget_split,
            "activity_expense_analysis": activity_check,
            "itinerary": itinerary_schedule,
            "packing_checklist": packing_list
        }


if __name__ == "__main__":
    # Test workflow
    planner = SmartTravelPlanner()
    plan = planner.plan_trip(city="Mumbai", days=2, budget=5000.0, save_to_db=False)
    print(f"Generated trip to {plan['city']} for {plan['days']} days (Tier: {plan['tier']})")
    print(f"Scheduled {len(plan['itinerary'])} activities across time slots.")
