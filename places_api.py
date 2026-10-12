"""
API/places_api.py
Fetches regional points of interest, heritage landmarks, and eateries
via REST API web services with a graceful local JSON fallback.
Aligned with Syllabus Unit 2 (Exceptions & File I/O) & Unit 4 (APIs & Web Services).
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests

# Resolve project root for imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.config import PLACES_JSON_PATH, CITY_COORDINATES, API_TIMEOUT


# ==============================================================================
# CUSTOM EXCEPTIONS (Syllabus Unit 2.3)
# ==============================================================================
class PlacesAPIError(Exception):
    """Raised when places cannot be fetched from web services or local cache."""
    pass


# ==============================================================================
# PLACES SERVICE CLASS (Syllabus Unit 2.1 & Unit 4.1)
# ==============================================================================
class PlacesService:
    """Manages place retrieval, category filtering, and external web API queries."""

    # Public OpenStreetMap Overpass API interpreter endpoint (No API key needed)
    OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"

    def __init__(self, json_path: Path = PLACES_JSON_PATH):
        self.json_path = json_path
        self._cached_local_places = self._read_local_catalog()

    def _read_local_catalog(self) -> List[Dict[str, Any]]:
        """Reads local backup catalog from places.json (Unit 2.2)."""
        if not self.json_path.exists():
            return []
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("destinations", [])
        except (json.JSONDecodeError, OSError):
            return []

    def get_places_by_city(self, city: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves places for Mumbai, Navi Mumbai, or Thane from local catalog,
        with optional category filtering (e.g., 'Sightseeing' or 'Food & Dining').
        """
        city_lower = city.strip().lower()
        matched_places = [
            place for place in self._cached_local_places
            if place.get("city", "").lower() == city_lower
        ]

        if category:
            cat_lower = category.strip().lower()
            matched_places = [
                p for p in matched_places
                if p.get("category", "").lower() == cat_lower
            ]

        return matched_places

    def fetch_live_osm_landmarks(self, city: str, radius_meters: int = 5000) -> List[Dict[str, Any]]:
        """
        Demonstrates live REST API interaction (Syllabus Unit 4.1):
        Queries Overpass API for tourism and historic nodes around city coordinates.
        Falls back to local places.json if network is unavailable or times out.
        """
        city_key = city.strip().title()
        if city_key not in CITY_COORDINATES:
            raise PlacesAPIError(f"Coordinates for city '{city}' are not configured.")

        coords = CITY_COORDINATES[city_key]
        lat, lon = coords["lat"], coords["lon"]

        # Overpass QL query searching for historic/tourism nodes around coordinates
        overpass_query = f"""
        [out:json][timeout:{API_TIMEOUT}];
        (
          node["tourism"="attraction"](around:{radius_meters},{lat},{lon});
          node["historic"](around:{radius_meters},{lat},{lon});
        );
        out 10;
        """

        try:
            response = requests.post(
                self.OVERPASS_API_URL,
                data={"data": overpass_query},
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            live_places = []
            for element in data.get("elements", []):
                tags = element.get("tags", {})
                name = tags.get("name")
                if name:
                    live_places.append({
                        "id": f"OSM_{element.get('id')}",
                        "name": name,
                        "city": city_key,
                        "category": "Sightseeing",
                        "subcategory": tags.get("historic") or tags.get("tourism") or "Landmark",
                        "estimated_cost_inr": 0,
                        "best_time_slot": "Morning",
                        "rating": 4.5
                    })

            if live_places:
                return live_places

        except (requests.RequestException, ValueError) as err:
            # Graceful fallback to local JSON database on network failure
            print(f"[PlacesService] Live API query failed ({err}). Falling back to local data.")

        fallback = self.get_places_by_city(city_key)
        if not fallback:
            raise PlacesAPIError(f"No places found for {city} in API or local dataset.")
        return fallback


if __name__ == "__main__":
    # Test local filtering and live fetch
    service = PlacesService()
    local_thane = service.get_places_by_city("Thane", category="Food & Dining")
    print(f"Found {len(local_thane)} local food places in Thane:")
    for place in local_thane:
        print(f" - {place['name']} (₹{place['estimated_cost_inr']})")
