"""
utils/validators.py
Input validation routines using Regular Expressions and type checking.
Aligned with Syllabus Unit 2.2 (Regular Expressions) & Unit 2.3 (User-Defined Exceptions).
"""

import re
import sys
from pathlib import Path
from typing import Tuple, Optional, Any  # Added 'Any' here

# Resolve project root for imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.config import ALLOWED_CITIES


# ==============================================================================
# CUSTOM EXCEPTIONS (Syllabus Unit 2.3)
# ==============================================================================
class ValidationError(Exception):
    """Base exception for user input validation errors."""
    pass


class InvalidCityError(ValidationError):
    """Raised when destination city is invalid or outside the MMR scope."""
    pass


class InvalidBudgetError(ValidationError):
    """Raised when budget is not a positive numeric value."""
    pass


class InvalidDaysError(ValidationError):
    """Raised when trip duration is outside acceptable bounds."""
    pass


# ==============================================================================
# REGULAR EXPRESSIONS PATTERNS (Syllabus Unit 2.2)
# ==============================================================================
# Matches positive floating-point numbers or integers (e.g., "500", "2500.50")
BUDGET_REGEX = re.compile(r"^\d+(\.\d{1,2})?$")

# Matches integer string with 1 to 2 digits (e.g., "1" to "30")
DAYS_REGEX = re.compile(r"^[1-9]\d{0,1}$")

# Matches alphabetic names with optional single spaces/hyphens
CITY_NAME_REGEX = re.compile(r"^[A-Za-z]+(\s[A-Za-z]+)*$")


# ==============================================================================
# VALIDATION FUNCTIONS
# ==============================================================================
def validate_city(city_input: str) -> str:
    """
    Validates the destination city using regex and allowed MMR boundaries.
    """
    if not city_input or not isinstance(city_input, str):
        raise InvalidCityError("City name cannot be empty.")

    clean_city = city_input.strip()

    # Regex syntax check (Syllabus Unit 2.2)
    if not CITY_NAME_REGEX.match(clean_city):
        raise InvalidCityError(f"'{city_input}' contains invalid characters. Use letters only.")

    normalized_city = clean_city.title()
    if normalized_city not in ALLOWED_CITIES:
        raise InvalidCityError(
            f"City '{normalized_city}' is outside the project scope. "
            f"Allowed destinations are: {', '.join(ALLOWED_CITIES)}."
        )

    return normalized_city


def validate_budget(budget_input: Any) -> float:
    """
    Validates whether the budget is a valid positive number using regex.
    """
    raw_str = str(budget_input).strip()

    # Regex verification
    if not BUDGET_REGEX.match(raw_str):
        raise InvalidBudgetError(f"Invalid budget amount: '{budget_input}'. Must be a positive number.")

    try:
        budget_val = float(raw_str)
    except ValueError:
        raise InvalidBudgetError("Budget could not be parsed as a valid number.")

    if budget_val <= 0:
        raise InvalidBudgetError("Budget must be greater than ₹0.")

    if budget_val > 1000000:
        raise InvalidBudgetError("Budget exceeds the maximum supported threshold (₹10,00,000).")

    return round(budget_val, 2)


def validate_days(days_input: Any, min_days: int = 1, max_days: int = 7) -> int:
    """
    Validates trip duration using regex and bounds checking.
    """
    raw_str = str(days_input).strip()

    # Regex verification
    if not DAYS_REGEX.match(raw_str):
        raise InvalidDaysError(f"Days must be a positive integer between {min_days} and {max_days}.")

    try:
        days_val = int(raw_str)
    except ValueError:
        raise InvalidDaysError("Duration must be a valid integer.")

    if not (min_days <= days_val <= max_days):
        raise InvalidDaysError(f"Trip duration must be between {min_days} and {max_days} days for a mini-project plan.")

    return days_val


def validate_all_inputs(city_input: str, days_input: Any, budget_input: Any) -> Tuple[str, int, float]:
    """
    Convenience orchestrator that validates all form fields at once.
    Returns cleaned (city, days, budget) tuple.
    """
    valid_city = validate_city(city_input)
    valid_days = validate_days(days_input)
    valid_budget = validate_budget(budget_input)
    return valid_city, valid_days, valid_budget


if __name__ == "__main__":
    try:
        c, d, b = validate_all_inputs("mumbai", "3", "4500.50")
        print(f"[OK] Validated: City={c}, Days={d}, Budget=₹{b}")
    except ValidationError as err:
        print(f"[ERROR] {err}")
