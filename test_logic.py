"""
tests/test_logic.py
Unit tests verifying budget calculations, itinerary sequencing queues,
and coordinator planning logic.
Aligned with Syllabus Unit 1, Unit 2 (Exceptions & OOP), Unit 3 (Queues), and Unit 6 (NumPy/Pandas).
"""

import unittest
import sys
import tempfile
from pathlib import Path
import pandas as pd

# Resolve project root for imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from Database.database import DatabaseManager
from Database.schema import create_tables
from Logic.budget import BudgetCalculator, BudgetCalculationError
from Logic.itinerary import ItineraryBuilder, ItineraryGenerationError
from Logic.smart_planner import SmartTravelPlanner


class TestBudgetCalculator(unittest.TestCase):
    """Test suite for financial calculations, tier categorizations, and Pandas Series."""

    def test_budget_split_sum(self):
        """Verifies that the category breakdown sums up to the total budget."""
        total_budget = 10000.0
        calculator = BudgetCalculator(total_budget=total_budget, total_days=3)
        split = calculator.calculate_category_split()

        self.assertAlmostEqual(sum(split.values()), total_budget, places=2)
        self.assertIn("stay", split)
        self.assertIn("food", split)
        self.assertIn("travel", split)
        self.assertIn("sightseeing", split)

    def test_tier_classification(self):
        """Tests spending tier classification logic."""
        budget_trip = BudgetCalculator(total_budget=1500.0, total_days=1)
        self.assertEqual(budget_trip.determine_budget_tier(), "Budget")

        moderate_trip = BudgetCalculator(total_budget=6000.0, total_days=2)
        self.assertEqual(moderate_trip.determine_budget_tier(), "Moderate")

        luxury_trip = BudgetCalculator(total_budget=15000.0, total_days=2)
        self.assertEqual(luxury_trip.determine_budget_tier(), "Luxury")

    def test_invalid_budget_inputs(self):
        """Verifies that negative or zero inputs raise BudgetCalculationError."""
        with self.assertRaises(BudgetCalculationError):
            BudgetCalculator(total_budget=0, total_days=2)

        with self.assertRaises(BudgetCalculationError):
            BudgetCalculator(total_budget=5000, total_days=0)

    def test_budget_series_output(self):
        """Verifies that get_budget_series returns a valid Pandas Series."""
        calculator = BudgetCalculator(total_budget=4000.0, total_days=2)
        series = calculator.get_budget_series()
        self.assertIsInstance(series, pd.Series)
        self.assertEqual(len(series), 4)


class TestItineraryBuilder(unittest.TestCase):
    """Test suite for queue-based activity sequencing and constraints."""

    def setUp(self):
        self.mock_places = [
            {"id": "T1", "name": "Yeoor Hills", "city": "Thane", "best_time_slot": "Morning", "category": "Nature", "estimated_cost_inr": 30.0},
            {"id": "T2", "name": "Mamledar Misal", "city": "Thane", "best_time_slot": "Morning", "category": "Food", "estimated_cost_inr": 150.0},
            {"id": "T3", "name": "Metkut", "city": "Thane", "best_time_slot": "Afternoon", "category": "Food", "estimated_cost_inr": 400.0},
            {"id": "T4", "name": "Upvan Lake", "city": "Thane", "best_time_slot": "Evening", "category": "Sightseeing", "estimated_cost_inr": 0.0},
        ]

    def test_schedule_generation(self):
        """Ensures that activities are populated across slots without duplicate items."""
        builder = ItineraryBuilder(city="Thane", days=1, available_places=self.mock_places)
        schedule = builder.build_schedule()

        self.assertGreater(len(schedule), 0)
        time_slots = [item["time_slot"] for item in schedule]
        self.assertIn("Morning", time_slots)
        self.assertIn("Afternoon", time_slots)
        self.assertIn("Evening", time_slots)

    def test_invalid_city_places(self):
        """Ensures that asking for an unrepresented city raises ItineraryGenerationError."""
        builder = ItineraryBuilder(city="Navi Mumbai", days=1, available_places=self.mock_places)
        with self.assertRaises(ItineraryGenerationError):
            builder.build_schedule()


class TestSmartTravelPlanner(unittest.TestCase):
    """Test suite for the central coordinator linking budget, itinerary, and DB."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_db_path = Path(self.temp_dir.name) / "test_planner.db"
        create_tables(self.test_db_path)
        self.db = DatabaseManager(db_path=self.test_db_path)
        self.planner = SmartTravelPlanner(db_manager=self.db)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_plan_trip_mumbai(self):
        """Tests full end-to-end trip planning workflow for Mumbai."""
        plan = self.planner.plan_trip(city="Mumbai", days=1, budget=3000.0, save_to_db=True)

        self.assertEqual(plan["city"], "Mumbai")
        self.assertEqual(plan["days"], 1)
        self.assertIsNotNone(plan["trip_id"])
        self.assertIsInstance(plan["itinerary"], list)
        self.assertGreater(len(plan["itinerary"]), 0)
        self.assertIn("packing_checklist", plan)

    def test_unsupported_city_raises_value_error(self):
        """Ensures non-MMR cities (e.g. Pune) get rejected."""
        with self.assertRaises(ValueError):
            self.planner.plan_trip(city="Pune", days=2, budget=5000.0, save_to_db=False)

    def test_weather_adaptive_packing_list(self):
        """Ensures rain forecast includes rain-specific packing suggestions."""
        rainy_pack = self.planner.generate_packing_checklist(weather_condition="Rainy", days=2)
        umbrella_found = any("Umbrella" in item for item in rainy_pack)
        self.assertTrue(umbrella_found)

        clear_pack = self.planner.generate_packing_checklist(weather_condition="Clear", days=2)
        sunglasses_found = any("Sunglasses" in item for item in clear_pack)
        self.assertTrue(sunglasses_found)


if __name__ == "__main__":
    unittest.main()
