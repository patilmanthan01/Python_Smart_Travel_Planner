"""
API/weather_api.py
Fetches live weather reports and forecasts for Mumbai, Navi Mumbai, and Thane.
Aligned with Syllabus Unit 2 (OOP, Custom Exceptions) & Unit 4 (APIs: Fetch Weather Data).
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import requests

# Resolve project root for imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.config import WEATHER_API_KEY, WEATHER_BASE_URL, API_TIMEOUT, ALLOWED_CITIES


# ==============================================================================
# CUSTOM EXCEPTIONS (Syllabus Unit 2.3)
# ==============================================================================
class WeatherAPIError(Exception):
    """Raised when an external weather API request fails or is malformed."""
    pass


# ==============================================================================
# WEATHER SERVICE CLASS (Syllabus Unit 2.1 & Unit 4.1)
# ==============================================================================
class WeatherService:
    """Handles real-time weather inquiries for the Mumbai Metropolitan Region."""

    def __init__(self, api_key: str = WEATHER_API_KEY):
        self.api_key = api_key
        self.base_url = WEATHER_BASE_URL

    def _get_offline_fallback(self, city: str) -> Dict[str, Any]:
        """
        Provides realistic seasonal coastal weather data if offline 
        or if an invalid/empty API key is provided.
        """
        return {
            "city": city.title(),
            "temperature_celsius": 30.5,
            "feels_like_celsius": 34.0,
            "humidity_percent": 75,
            "condition": "Partly Cloudy",
            "description": "Scattered clouds with coastal humidity",
            "wind_speed_kmh": 14.5,
            "is_rainy": False,
            "is_live": False
        }

    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """
        Fetches live current weather from OpenWeatherMap REST API (Unit 4.1).
        Parses JSON response and extracts essential weather metrics.
        """
        city_title = city.strip().title()
        if city_title not in ALLOWED_CITIES:
            raise WeatherAPIError(f"City '{city}' not supported. Allowed: {ALLOWED_CITIES}")

        # If user hasn't configured a valid API key yet, return offline fallback gracefully
        if not self.api_key or self.api_key == "your_api_key_here":
            return self._get_offline_fallback(city_title)

        # For OpenWeatherMap search, qualify city with state/country
        query_location = f"{city_title},MH,IN"
        params = {
            "q": query_location,
            "appid": self.api_key,
            "units": "metric"  # Return Celsius
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=API_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            weather_data = data.get("weather", [{}])[0]
            main_data = data.get("main", {})
            wind_data = data.get("wind", {})

            condition_main = weather_data.get("main", "Clear")
            is_rain = condition_main.lower() in ("rain", "drizzle", "thunderstorm")

            return {
                "city": city_title,
                "temperature_celsius": round(main_data.get("temp", 30.0), 1),
                "feels_like_celsius": round(main_data.get("feels_like", 33.0), 1),
                "humidity_percent": main_data.get("humidity", 70),
                "condition": condition_main,
                "description": weather_data.get("description", "Clear sky").capitalize(),
                "wind_speed_kmh": round(wind_data.get("speed", 3.0) * 3.6, 1),  # m/s to km/h
                "is_rainy": is_rain,
                "is_live": True
            }

        except requests.exceptions.RequestException as req_err:
            print(f"[WeatherService] Network/API Error ({req_err}). Using fallback data.")
            return self._get_offline_fallback(city_title)
        except (KeyError, ValueError) as parse_err:
            raise WeatherAPIError(f"Error parsing weather API data: {parse_err}") from parse_err


if __name__ == "__main__":
    # Test execution
    service = WeatherService()
    for city_name in ["Mumbai", "Navi Mumbai", "Thane"]:
        report = service.get_current_weather(city_name)
        status = "Live" if report["is_live"] else "Offline/Cached"
        print(f"[{status}] {report['city']}: {report['temperature_celsius']}°C, {report['condition']} ({report['description']})")
