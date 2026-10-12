"""
GUI/weather_view.py
Weather advisory view displaying temperature, humidity, wind, and alerts.
Aligned with Syllabus Unit 4.1 (GUI, Weather API) & Unit 5.1 (Multithreading).
"""

import sys
import threading
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Dict, Any, Optional

# Resolve project root for imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.config import THEME_COLOR, ALLOWED_CITIES
from API.weather_api import WeatherService


class WeatherViewFrame(ttk.Frame):
    """
    Displays current weather conditions, advisory notes, and metrics
    with asynchronous background fetching using the threading module.
    """

    def __init__(self, parent: tk.Widget):
        super().__init__(parent, padding=20)
        self.weather_service = WeatherService()
        self.current_city = ALLOWED_CITIES[0]

        self._build_ui()
        self.fetch_weather_async(self.current_city)

    def _build_ui(self):
        """Constructs layout, header, selector, and weather metrics cards."""
        # Top Bar: Title & City Selector
        top_bar = ttk.Frame(self)
        top_bar.pack(fill="x", pady=(0, 15))

        title_lbl = ttk.Label(
            top_bar,
            text="Live Regional Weather & Forecast",
            font=("Helvetica", 16, "bold"),
            foreground=THEME_COLOR
        )
        title_lbl.pack(side="left", anchor="w")

        # City Dropdown for on-demand weather checks
        self.city_var = tk.StringVar(value=self.current_city)
        city_dropdown = ttk.Combobox(
            top_bar,
            textvariable=self.city_var,
            values=list(ALLOWED_CITIES),
            state="readonly",
            width=15,
            font=("Helvetica", 10)
        )
        city_dropdown.pack(side="right", padx=(10, 0))
        city_dropdown.bind("<<ComboboxSelected>>", self._on_city_changed)

        ttk.Label(top_bar, text="Check City:", font=("Helvetica", 10)).pack(side="right")

        # Status / Indicator Label
        self.status_var = tk.StringVar(value="Fetching latest weather data...")
        self.status_lbl = ttk.Label(
            self,
            textvariable=self.status_var,
            font=("Helvetica", 9, "italic"),
            foreground="#666666"
        )
        self.status_lbl.pack(anchor="w", pady=(0, 10))

        # Main Weather Summary Banner
        self.banner_frame = ttk.LabelFrame(self, text="Current Conditions", padding=15)
        self.banner_frame.pack(fill="x", pady=(0, 15))

        self.temp_var = tk.StringVar(value="-- °C")
        self.condition_var = tk.StringVar(value="Loading...")
        self.desc_var = tk.StringVar(value="")

        ttk.Label(self.banner_frame, textvariable=self.temp_var, font=("Helvetica", 28, "bold"), foreground=THEME_COLOR).pack(anchor="w")
        ttk.Label(self.banner_frame, textvariable=self.condition_var, font=("Helvetica", 13, "bold")).pack(anchor="w", pady=(2, 2))
        ttk.Label(self.banner_frame, textvariable=self.desc_var, font=("Helvetica", 10), foreground="#444444").pack(anchor="w")

        # Metrics Grid (Humidity, Wind, Rain alert)
        metrics_container = ttk.Frame(self)
        metrics_container.pack(fill="x", pady=(0, 15))

        self.feels_like_var = tk.StringVar(value="--")
        self.humidity_var = tk.StringVar(value="--")
        self.wind_var = tk.StringVar(value="--")
        self.rain_var = tk.StringVar(value="--")

        self._build_metric_tile(metrics_container, "Feels Like", self.feels_like_var, 0)
        self._build_metric_tile(metrics_container, "Humidity", self.humidity_var, 1)
        self._build_metric_tile(metrics_container, "Wind Speed", self.wind_var, 2)
        self._build_metric_tile(metrics_container, "Rain Chance", self.rain_var, 3)

        # Travel Advisory Box
        advisory_frame = ttk.LabelFrame(self, text="Travel Recommendations & Advisory", padding=15)
        advisory_frame.pack(fill="both", expand=True)

        self.advisory_text = tk.Text(
            advisory_frame,
            wrap="word",
            height=5,
            font=("Helvetica", 10),
            relief="flat",
            bg="#fdfdfd"
        )
        self.advisory_text.pack(fill="both", expand=True)
        self.advisory_text.config(state="disabled")

    def _build_metric_tile(self, parent: ttk.Widget, title: str, textvar: tk.StringVar, col: int):
        """Constructs a responsive metrics box."""
        card = ttk.Frame(parent, relief="groove", padding=10)
        card.grid(row=0, column=col, sticky="nsew", padx=5)
        parent.columnconfigure(col, weight=1)

        ttk.Label(card, text=title, font=("Helvetica", 9), foreground="#666666").pack(anchor="center")
        ttk.Label(card, textvariable=textvar, font=("Helvetica", 11, "bold"), foreground=THEME_COLOR).pack(anchor="center", pady=(4, 0))

    def _on_city_changed(self, event=None):
        """Callback when user selects a different city from the combobox."""
        selected_city = self.city_var.get()
        self.fetch_weather_async(selected_city)

    def fetch_weather_async(self, city: str):
        """
        Spawns a background thread to query the Weather API (Syllabus Unit 5.1).
        Prevents desktop UI freezing during network latency.
        """
        self.status_var.set(f"Connecting to weather service for {city}...")
        thread = threading.Thread(target=self._worker_fetch_weather, args=(city,), daemon=True)
        thread.start()

    def _worker_fetch_weather(self, city: str):
        """Background worker executing the network request."""
        try:
            weather_data = self.weather_service.get_current_weather(city)
            # Schedule UI update on main GUI thread
            self.after(0, self._apply_weather_data, weather_data)
        except Exception as e:
            self.after(0, self.status_var.set, f"Could not retrieve weather: {e}")

    def _apply_weather_data(self, data: Dict[str, Any]):
        """Updates UI components with fetched weather payload."""
        temp = data.get("temperature_celsius", 30.0)
        feels = data.get("feels_like_celsius", 32.0)
        humidity = data.get("humidity_percent", 70)
        wind = data.get("wind_speed_kmh", 10.0)
        is_rain = data.get("is_rainy", False)
        condition = data.get("condition", "Pleasant")
        desc = data.get("description", "")
        is_live = data.get("is_live", False)

        self.temp_var.set(f"{temp}°C")
        self.condition_var.set(f"{data.get('city')} • {condition}")
        self.desc_var.set(desc)

        self.feels_like_var.set(f"{feels}°C")
        self.humidity_var.set(f"{humidity}%")
        self.wind_var.set(f"{wind} km/h")
        self.rain_var.set("High (Rainy)" if is_rain else "Low (Dry)")

        status_text = "Live Web API Feed" if is_live else "Cached MMR Weather Feed"
        self.status_var.set(f"Status: {status_text} • Last updated just now")

        # Prepare advisory text
        advisory_msg = f"• General: {desc}.\n"
        if is_rain:
            advisory_msg += "• Precaution: Rainfall expected across MMR. Carry umbrellas and prefer indoor attractions (CSMVS, Malls, Museums).\n"
        elif temp > 33:
            advisory_msg += "• Precaution: High afternoon temperatures. Plan outdoor promenades like Marine Drive or Upvan Lake for evenings.\n"
        else:
            advisory_msg += "• Good conditions for sightseeing and local transport across Mumbai, Navi Mumbai, and Thane.\n"

        self.advisory_text.config(state="normal")
        self.advisory_text.delete("1.0", tk.END)
        self.advisory_text.insert(tk.END, advisory_msg)
        self.advisory_text.config(state="disabled")

    def load_weather_for_plan(self, city: str):
        """External call allowing dashboard to switch weather city automatically."""
        self.city_var.set(city)
        self.fetch_weather_async(city)


if __name__ == "__main__":
    # Test execution
    root = tk.Tk()
    root.title("Weather View Test")
    root.geometry("750x450")

    w_view = WeatherViewFrame(root)
    w_view.pack(fill="both", expand=True)

    root.mainloop()
