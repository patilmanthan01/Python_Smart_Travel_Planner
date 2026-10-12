"""
tests/test_api.py
Unit tests verifying WeatherService, PlacesService, and AIPlannerService.
Aligned with Syllabus Unit 2 (Exceptions, OOP) & Unit 4 (APIs & Web Services).
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Resolve project root for imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from API.weather_api import WeatherService, WeatherAPIError
from API.places_api import PlacesService, PlacesAPIError
from API.ai_planner import AIPlannerService


class TestWeatherService(unittest.TestCase):
    """Test suite verifying Weather API requests, fallback, and error checking."""

    def setUp(self):
        self.weather_service = WeatherService(api_key="mock_api_key")

    @patch("API.weather_api.requests.get")
    def test_get_current_weather_live_success(self, mock_get):
        """Tests successful parsing of simulated OpenWeatherMap response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "weather": [{"main": "Clouds", "description": "few clouds"}],
            "main": {"temp": 29.4, "feels_like": 32.1, "humidity": 70},
            "wind": {"speed": 4.0}
        }
        mock_get.return_value = mock_response

        data = self.weather_service.get_current_weather("Mumbai")
        self.assertEqual(data["city"], "Mumbai")
        self.assertEqual(data["temperature_celsius"], 29.4)
        self.assertEqual(data["condition"], "Clouds")
        self.assertFalse(data["is_rainy"])
        self.assertTrue(data["is_live"])

    def test_unsupported_city_raises_weather_error(self):
        """Verifies that queries outside Mumbai/Navi Mumbai/Thane are rejected."""
        with self.assertRaises(WeatherAPIError):
            self.weather_service.get_current_weather("Pune")

    def test_offline_fallback(self):
        """Ensures service falls back to default cache if API key is unconfigured."""
        service_unconfigured = WeatherService(api_key="your_api_key_here")
        data = service_unconfigured.get_current_weather("Thane")
        self.assertEqual(data["city"], "Thane")
        self.assertFalse(data["is_live"])
        self.assertIn("temperature_celsius", data)


class TestPlacesService(unittest.TestCase):
    """Test suite for local place retrieval and external place fallbacks."""

    def setUp(self):
        self.places_service = PlacesService()

    def test_get_places_by_city(self):
        """Verifies that local places are filtered accurately by city."""
        thane_places = self.places_service.get_places_by_city("Thane")
        self.assertIsInstance(thane_places, list)
        self.assertGreater(len(thane_places), 0)
        for place in thane_places:
            self.assertEqual(place["city"], "Thane")

    def test_get_places_with_category_filter(self):
        """Verifies category filtering (Sightseeing vs Food & Dining)."""
        mumbai_food = self.places_service.get_places_by_city("Mumbai", category="Food & Dining")
        self.assertIsInstance(mumbai_food, list)
        for place in mumbai_food:
            self.assertEqual(place["category"], "Food & Dining")

    @patch("API.places_api.requests.post")
    def test_live_osm_fetch_graceful_fallback(self, mock_post):
        """Tests that a network failure triggers local JSON fallback gracefully."""
        # Simulate network error
        mock_post.side_effect = Exception("Connection Timeout")

        places = self.places_service.fetch_live_osm_landmarks("Navi Mumbai")
        self.assertIsInstance(places, list)
        self.assertGreater(len(places), 0)
        self.assertEqual(places[0]["city"], "Navi Mumbai")


class TestAIPlannerService(unittest.TestCase):
    """Test suite for smart recommendations and itinerary tips synthesis."""

    def setUp(self):
        self.ai_planner = AIPlannerService()

    def test_trip_theme_generation(self):
        """Tests heuristic determination of trip theme."""
        theme = self.ai_planner.generate_trip_theme(["Food & Dining"])
        self.assertIn("Culinary", theme)

        heritage_theme = self.ai_planner.generate_trip_theme(["Heritage"])
        self.assertIn("Heritage", heritage_theme)

    def test_synthesize_ai_summary(self):
        """Tests generation of complete AI advice payload."""
        dummy_weather = {
            "temperature_celsius": 33.0,
            "condition": "Rain",
            "is_rainy": True
        }
        summary = self.ai_planner.synthesize_ai_summary(
            city="Mumbai",
            days=2,
            budget=5000.0,
            tier="Moderate",
            weather=dummy_weather
        )

        self.assertIn("theme", summary)
        self.assertIn("summary_text", summary)
        self.assertIsInstance(summary["smart_tips"], list)
        self.assertGreater(len(summary["smart_tips"]), 0)


if __name__ == "__main__":
    unittest.main()
