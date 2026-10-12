"""
utils/helpers.py
General utility functions for text formatting, currency styling, 
date manipulation, and data transformations across the application.
Aligned with Syllabus Unit 1.4 (Functions, Arguments, Scope) & Unit 2.2 (Text Processing).
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


def format_currency_inr(amount: float) -> str:
    """
    Formats a numeric value into standard Indian Rupee notation (e.g., ₹2,500.00).
    Demonstrates string manipulation and number formatting.
    """
    try:
        val = float(amount)
        # Indian number formatting logic for thousands and lakhs
        parts = f"{val:.2f}".split(".")
        integer_part = parts[0]
        decimal_part = parts[1]

        if len(integer_part) > 3:
            last_three = integer_part[-3:]
            remaining = integer_part[:-3]
            # Group into twos for lakhs/crores
            groups = []
            while len(remaining) > 2:
                groups.insert(0, remaining[-2:])
                remaining = remaining[:-2]
            if remaining:
                groups.insert(0, remaining)
            formatted_int = ",".join(groups) + "," + last_three
        else:
            formatted_int = integer_part

        return f"₹{formatted_int}.{decimal_part}"
    except (ValueError, TypeError):
        return "₹0.00"


def calculate_trip_dates(start_date_str: Optional[str] = None, total_days: int = 1) -> List[str]:
    """
    Generates a list of formatted calendar dates corresponding to each trip day.
    Defaults to starting tomorrow if no start date is supplied.
    """
    if start_date_str:
        try:
            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
        except ValueError:
            start_dt = datetime.now() + timedelta(days=1)
    else:
        start_dt = datetime.now() + timedelta(days=1)

    dates = []
    for day_offset in range(total_days):
        current_date = start_dt + timedelta(days=day_offset)
        dates.append(current_date.strftime("%d %b %Y (%A)"))
    return dates


def clean_text_display(text: str, max_chars: int = 80) -> str:
    """
    Truncates and adds an ellipsis to lengthy descriptions for clean UI display.
    """
    if not text:
        return ""
    stripped = text.strip()
    if len(stripped) <= max_chars:
        return stripped
    return stripped[: max_chars - 3] + "..."


def group_itinerary_by_day(itinerary_items: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
    """
    Groups raw itinerary dictionaries by their day_number for structured UI rendering.
    Demonstrates dictionary aggregation and sorting.
    """
    grouped: Dict[int, List[Dict[str, Any]]] = {}
    for item in itinerary_items:
        day_num = item.get("day_number", 1)
        if day_num not in grouped:
            grouped[day_num] = []
        grouped[day_num].append(item)

    # Sort each day's items chronologically by time slot
    slot_order = {"Morning": 1, "Afternoon": 2, "Evening": 3}
    for day_num in grouped:
        grouped[day_num].sort(key=lambda x: slot_order.get(x.get("time_slot", ""), 99))

    return grouped


if __name__ == "__main__":
    # Test executions
    print("Currency Format:", format_currency_inr(154500.5))
    print("Trip Dates (3 days):", calculate_trip_dates(total_days=3))
    print("Text Truncate:", clean_text_display("A stunning panoramic view of Sanjay Gandhi National Park in Borivali.", 30))
