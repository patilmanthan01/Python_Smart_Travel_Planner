"""
config/config.py
Configuration settings, global constants, and file paths for Smart Travel Planner.
Aligned with Syllabus Unit 1 (Variables & Dictionaries) & Unit 2 (Modules & Directories).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve project base directory dynamically
# BASE_DIR points to the root 'TRAVEL PLANNER' directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env if present
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)

# ==============================================================================
# 1. FILE & DATABASE PATHS
# ==============================================================================
DATA_DIR = BASE_DIR / "Data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

PLACES_JSON_PATH = DATA_DIR / "places.json"
DATABASE_PATH = DATA_DIR / "travel.db"

ASSETS_DIR = BASE_DIR / "assets"

# ==============================================================================
# 2. API CONFIGURATIONS
# ==============================================================================
# OpenWeatherMap API Key (read from .env or fallback string)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "your_api_key_here")
WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Request timeout in seconds
API_TIMEOUT = 10

# ==============================================================================
# 3. REGIONAL SCOPE & COORDINATES
# ==============================================================================
# Target regions restricted to Mumbai, Navi Mumbai, and Thane
ALLOWED_CITIES = ("Mumbai", "Navi Mumbai", "Thane")

CITY_COORDINATES = {
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Navi Mumbai": {"lat": 19.0330, "lon": 73.0297},
    "Thane": {"lat": 19.2183, "lon": 72.9781},
}

# ==============================================================================
# 4. BUDGET TIER & COST WEIGHTS
# ==============================================================================
# Cost allocation percentages across travel essentials
BUDGET_SPLIT_RATIOS = {
    "stay": 0.40,        # 40% Accommodation / Base Stay
    "food": 0.25,        # 25% Dining & Local Food
    "travel": 0.20,      # 20% Local Transport (Cabs / Local Trains / Metro)
    "sightseeing": 0.15  # 15% Entry Tickets & Activities
}

# Default daily expense thresholds in INR per person
BUDGET_TIERS = {
    "Budget": {"min_daily": 800, "max_daily": 2000},
    "Moderate": {"min_daily": 2001, "max_daily": 4500},
    "Luxury": {"min_daily": 4501, "max_daily": 10000},
}

# ==============================================================================
# 5. GUI & VISUALIZATION DEFAULTS
# ==============================================================================
APP_TITLE = "Smart Travel Planner - MMR Edition"
APP_WINDOW_SIZE = "1024x720"
THEME_COLOR = "#1f538d"
