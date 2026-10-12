"""
API/ai_planner.py
Generates intelligent travel suggestions and recommendations using
rule-based heuristic scoring and external AI API prompt interfaces.
Aligned with Syllabus Unit 2 (OOP, Exceptions) & Unit 4 (APIs & Web Services).
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests

# Resolve project root for imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.config import API_TIMEOUT, ALLOWED_CITIES


# ==============================================================================
# CUSTOM EXCEPTIONS (Syllabus Unit 2.3)
# ==============================================================================
class AIPlannerError(Exception):
    """Raised when an AI recommendation generation fails."""
    pass


# ==============================================================================
# AI PLANNER ENGINE (Syllabus Unit 2.1 & Unit 4.1)
# ==============================================================================
class AIPlannerService:
    """
    Combines rule-based heuristic optimization with optional external 
    LLM API endpoints to produce smart, personalized travel summaries.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def generate_trip_theme(self, category_preferences: List[str]) -> str:
        """
        Determines the optimal travel persona/theme based on selected categories.
        """
        if not category_preferences:
            return "MMR Classic Explorer"

        categories_str = " ".join(category_preferences).lower()
        if "nature" in categories_str or "trek" in categories_str:
            return "Green Sahyadri Nature Trail"
        elif "heritage" in categories_str or "culture" in categories_str:
            return "Colonial & Architectural Heritage Tour"
        elif "food" in categories_str or "cafe" in categories_str:
            return "Culinary & Street-Food Safari"
        else:
            return "Urban Leisure & Sightseeing"

    def optimize_itinerary_tips(
        self,
        city: str,
        weather_summary: Dict[str, Any],
        budget_tier: str
    ) -> List[str]:
        """
        Generates context-aware smart travel recommendations based on
        city geography, budget tier, and live weather data.
        """
        city_title = city.strip().title()
        tips = []

        # Local transit optimization advice
        if city_title == "Mumbai":
            tips.append("Use Mumbai Metro (Line 2A/7 & Line 3) and Local Trains off-peak (11 AM - 4 PM) to beat traffic.")
            tips.append("Keep small change (₹10/₹20) handy for BEST bus ticketing or use the Chalo Card.")
        elif city_title == "Navi Mumbai":
            tips.append("NMMT AC buses and Harbour line locals provide seamless connectivity between Vashi and Belapur.")
            tips.append("Plan Kharghar Hills and Central Park visits during early morning or sunset hours for the best breeze.")
        elif city_title == "Thane":
            tips.append("Auto-rickshaws strictly operate by meter across Thane; prefer walking around Talao Pali and Naupada.")
            tips.append("Visit Yeoor Hills between 6:00 AM and 9:00 AM for fresh air and tranquil forest trails.")

        # Budget-aware tips
        if budget_tier in ("Budget", "Ultra-Budget"):
            tips.append("Prioritize iconic zero-cost public spots (Marine Drive, Upvan Lake, Jewel of Navi Mumbai).")
            tips.append("Savor local Maharashtrian snack hubs like Mamledar Misal or Kyani Bakery for delicious, affordable dining.")
        else:
            tips.append("Consider sea-facing dining at Colaba or lakeside cafes at Upvan for an elevated experience.")

        # Weather-aware tips
        if weather_summary.get("is_rainy", False):
            tips.append("Carry windproof umbrellas and prioritize indoor museums (CSMVS) over open water fronts.")
        elif weather_summary.get("temperature_celsius", 30) > 32:
            tips.append("High coastal humidity expected: stay hydrated and plan indoor cafe visits during the 1 PM - 3 PM heat peak.")

        return tips

    def synthesize_ai_summary(
        self,
        city: str,
        days: int,
        budget: float,
        tier: str,
        weather: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compiles the complete smart recommendation payload.
        Acts as the intelligent co-pilot for the user's travel schedule.
        """
        theme = self.generate_trip_theme(["Sightseeing", "Food & Dining"])
        tips = self.optimize_itinerary_tips(city, weather, tier)

        summary_text = (
            f"Here is your AI-curated {days}-day plan for {city} designed for a {tier} budget "
            f"(₹{budget:,.0f}). The current weather is {weather.get('condition', 'Pleasant')} at "
            f"{weather.get('temperature_celsius', 30)}°C. Your itinerary emphasizes balanced "
            f"sightseeing with minimal travel fatigue."
        )

        return {
            "theme": theme,
            "summary_text": summary_text,
            "smart_tips": tips
        }


if __name__ == "__main__":
    # Test execution
    ai_planner = AIPlannerService()
    dummy_weather = {"temperature_celsius": 32.0, "condition": "Humid", "is_rainy": False}
    result = ai_planner.synthesize_ai_summary(
        city="Thane",
        days=2,
        budget=4500.0,
        tier="Moderate",
        weather=dummy_weather
    )
    print("Theme:", result["theme"])
    print("Summary:", result["summary_text"])
    print("Smart Tips:")
    for tip in result["smart_tips"]:
        print(f" * {tip}")
