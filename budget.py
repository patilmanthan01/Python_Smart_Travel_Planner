"""
Logic/budget.py
Calculates budget splits, tier classifications, and expense analyses.
Aligned with Syllabus Unit 2 (OOP, Exceptions) & Unit 6 (NumPy arrays, Pandas Series).
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd

# Resolve project root for imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.config import BUDGET_SPLIT_RATIOS, BUDGET_TIERS


# ==============================================================================
# CUSTOM EXCEPTIONS (Syllabus Unit 2.3)
# ==============================================================================
class BudgetCalculationError(Exception):
    """Raised when budget inputs fail business logic or calculation steps."""
    pass


# ==============================================================================
# BUDGET CALCULATOR CLASS (Syllabus Unit 2.1 & Unit 6.1, 6.2)
# ==============================================================================
class BudgetCalculator:
    """Handles financial allocation and expense validation for trips."""

    def __init__(self, total_budget: float, total_days: int):
        if total_days <= 0:
            raise BudgetCalculationError("Total trip duration must be at least 1 day.")
        if total_budget <= 0:
            raise BudgetCalculationError("Total budget must be greater than 0 INR.")

        self.total_budget = float(total_budget)
        self.total_days = int(total_days)
        self.daily_budget = self.total_budget / self.total_days

    def determine_budget_tier(self) -> str:
        """
        Classifies trip spending style (Budget, Moderate, Luxury) 
        based on daily spending power per person.
        """
        for tier_name, limits in BUDGET_TIERS.items():
            if limits["min_daily"] <= self.daily_budget <= limits["max_daily"]:
                return tier_name
        
        if self.daily_budget < BUDGET_TIERS["Budget"]["min_daily"]:
            return "Ultra-Budget"
        return "Luxury"

    def calculate_category_split(self) -> Dict[str, float]:
        """
        Splits total budget into Stay, Food, Travel, and Sightseeing
        using NumPy vector operations (Syllabus Unit 6.1).
        """
        categories = list(BUDGET_SPLIT_RATIOS.keys())
        # Convert weight dictionary values into a 1D NumPy array
        ratios_array = np.array(list(BUDGET_SPLIT_RATIOS.values()), dtype=np.float64)

        # Mathematical vector multiplication using NumPy
        allocated_amounts = np.round(self.total_budget * ratios_array, 2)

        # Build dictionary mapping categories to allocated funds
        return dict(zip(categories, allocated_amounts.tolist()))

    def get_budget_series(self) -> pd.Series:
        """
        Converts allocated budget distribution into a Pandas Series (Syllabus Unit 6.2)
        for easy downstream plotting in GUI via Matplotlib.
        """
        split_dict = self.calculate_category_split()
        series = pd.Series(
            data=list(split_dict.values()),
            index=[cat.capitalize() for cat in split_dict.keys()],
            name="Allocated_INR"
        )
        return series

    def validate_activity_expenses(self, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compares the planned activity costs against the allocated sightseeing budget.
        Uses Pandas DataFrame operations to aggregate expenses.
        """
        if not activities:
            return {
                "total_estimated_activities": 0.0,
                "sightseeing_budget": self.calculate_category_split()["sightseeing"],
                "is_within_budget": True,
                "remaining_buffer": self.calculate_category_split()["sightseeing"]
            }

        # Convert activities list to Pandas DataFrame (Syllabus Unit 6.2)
        df = pd.DataFrame(activities)
        
        if "estimated_cost" not in df.columns:
            total_activity_cost = 0.0
        else:
            # Pandas column summation
            total_activity_cost = float(df["estimated_cost"].sum())

        sightseeing_allowance = self.calculate_category_split()["sightseeing"]
        difference = sightseeing_allowance - total_activity_cost

        return {
            "total_estimated_activities": round(total_activity_cost, 2),
            "sightseeing_budget": round(sightseeing_allowance, 2),
            "is_within_budget": difference >= 0,
            "remaining_buffer": round(difference, 2)
        }

    def get_summary(self) -> Dict[str, Any]:
        """Returns a comprehensive dictionary summary of the budget."""
        return {
            "total_budget": self.total_budget,
            "total_days": self.total_days,
            "daily_budget": round(self.daily_budget, 2),
            "tier": self.determine_budget_tier(),
            "category_split": self.calculate_category_split()
        }


if __name__ == "__main__":
    # Test execution
    calc = BudgetCalculator(total_budget=6000, total_days=3)
    print("Summary:", calc.get_summary())
    print("\nPandas Series for Visualization:")
    print(calc.get_budget_series())
