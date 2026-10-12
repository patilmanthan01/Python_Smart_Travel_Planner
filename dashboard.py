"""
GUI/dashboard.py
Main desktop dashboard featuring a persistent navigation sidebar,
dynamic view switching, and integration across all sub-views.
Aligned with Syllabus Unit 2.1 (OOP & Modules) & Unit 4.1 (Graphical User Interface).
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Dict, Any, Optional

# Resolve project root for imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.config import APP_TITLE, APP_WINDOW_SIZE, THEME_COLOR
from GUI.trip_form import TripFormFrame
from GUI.itenary_view import ItineraryViewFrame
from GUI.budget_view import BudgetViewFrame
from GUI.weather_view import WeatherViewFrame
from GUI.packing_view import PackingViewFrame


class TravelPlannerDashboard(tk.Tk):
    """
    Main application window implementing a multi-view desktop dashboard.
    Manages navigation, global state, and data flow between modules.
    """

    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry(APP_WINDOW_SIZE)
        self.minsize(980, 640)

        # Active state
        self.active_plan: Optional[Dict[str, Any]] = None

        self._configure_styles()
        self._build_layout()
        self._show_view("plan")  # Default view

    def _configure_styles(self):
        """Sets up ttk styles for clean visual hierarchy."""
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Configure custom button styles
        self.style.configure(
            "Nav.TButton",
            font=("Helvetica", 10, "bold"),
            padding=10,
            background="#202b38",
            foreground="#ffffff",
            anchor="w"
        )
        self.style.map(
            "Nav.TButton",
            background=[("active", "#34495e"), ("pressed", "#1a252f")],
            foreground=[("active", "#ffffff")]
        )

    def _build_layout(self):
        """Constructs layout: Left Sidebar, Right Content Area, Bottom Status Bar."""
        # 1. Main Horizontal Container
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True)

        # ---------------- Left Sidebar ----------------
        self.sidebar = tk.Frame(main_container, bg="#1a222d", width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # App Brand Header
        brand_frame = tk.Frame(self.sidebar, bg="#1a222d", pady=20, padx=15)
        brand_frame.pack(fill="x")

        tk.Label(
            brand_frame,
            text="TRAVEL PLANNER",
            font=("Helvetica", 13, "bold"),
            bg="#1a222d",
            fg="#ffffff"
        ).pack(anchor="w")

        tk.Label(
            brand_frame,
            text="Mumbai • Navi Mumbai • Thane",
            font=("Helvetica", 8),
            bg="#1a222d",
            fg="#8892b0"
        ).pack(anchor="w", pady=(3, 0))

        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", padx=10, pady=(0, 15))

        # Navigation Buttons
        self.nav_buttons = {}
        nav_items = [
            ("plan", "📝  Plan Trip"),
            ("itinerary", "📅  Itinerary Schedule"),
            ("budget", "📊  Budget Analytics"),
            ("weather", "🌤️  Live Weather"),
            ("packing", "🧳  Packing Checklist")
        ]

        for key, label in nav_items:
            btn = tk.Button(
                self.sidebar,
                text=label,
                font=("Helvetica", 10),
                bg="#1a222d",
                fg="#ecf0f1",
                activebackground="#34495e",
                activeforeground="#ffffff",
                relief="flat",
                anchor="w",
                padx=18,
                pady=10,
                cursor="hand2",
                command=lambda k=key: self._show_view(k)
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[key] = btn

        # ---------------- Right View Container ----------------
        self.content_area = ttk.Frame(main_container)
        self.content_area.pack(side="right", fill="both", expand=True)

        # Instantiate Sub-views
        self.views = {
            "plan": TripFormFrame(self.content_area, on_trip_generated=self._on_new_plan_generated),
            "itinerary": ItineraryViewFrame(self.content_area),
            "budget": BudgetViewFrame(self.content_area),
            "weather": WeatherViewFrame(self.content_area),
            "packing": PackingViewFrame(self.content_area)
        }

        # ---------------- Bottom Status Bar ----------------
        self.status_bar = tk.Frame(self, bg="#ecf0f1", height=25, padx=15)
        self.status_bar.pack(side="bottom", fill="x")

        self.status_text = tk.Label(
            self.status_bar,
            text="System Ready. Configure a trip to get started.",
            font=("Helvetica", 8),
            bg="#ecf0f1",
            fg="#555555"
        )
        self.status_text.pack(side="left")

        self.status_plan_info = tk.Label(
            self.status_bar,
            text="No active plan loaded",
            font=("Helvetica", 8, "italic"),
            bg="#ecf0f1",
            fg="#777777"
        )
        self.status_plan_info.pack(side="right")

    def _show_view(self, view_key: str):
        """Switches active frame in the content area and highlights nav button."""
        # Hide all view frames
        for frame in self.views.values():
            frame.pack_forget()

        # Display selected frame
        selected_frame = self.views.get(view_key)
        if selected_frame:
            selected_frame.pack(fill="both", expand=True)

        # Update button sidebar highlighting
        for k, btn in self.nav_buttons.items():
            if k == view_key:
                btn.config(bg="#2c3e50", fg="#3498db", font=("Helvetica", 10, "bold"))
            else:
                btn.config(bg="#1a222d", fg="#ecf0f1", font=("Helvetica", 10))

    def _on_new_plan_generated(self, plan_data: Dict[str, Any]):
        """Callback executed when a new trip is submitted and generated."""
        self.active_plan = plan_data
        city = plan_data.get("city", "")
        days = plan_data.get("days", 1)
        tier = plan_data.get("tier", "")

        # 1. Feed generated data into Itinerary View
        self.views["itinerary"].load_itinerary_data(plan_data)

        # 2. Feed generated data into Budget View
        self.views["budget"].load_budget_data(plan_data)

        # 3. Feed weather view with target city
        self.views["weather"].load_weather_for_plan(city)

        # 4. Feed packing checklist
        self.views["packing"].load_packing_list(plan_data.get("packing_checklist", []))

        # Update status bar
        self.status_text.config(text=f"Active Plan: {city} ({days} Days, {tier} Tier)")
        self.status_plan_info.config(text=f"Trip ID: {plan_data.get('trip_id') or 'Unsaved'}")

        # Automatically navigate user to the Itinerary Schedule view
        self._show_view("itinerary")
        messagebox.showinfo(
            "Plan Generated",
            f"Successfully generated travel schedule for {city}!\nSwitched to Itinerary Schedule tab."
        )


if __name__ == "__main__":
    app = TravelPlannerDashboard()
    app.mainloop()
