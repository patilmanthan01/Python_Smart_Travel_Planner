"""
GUI/trip_form.py
Trip configuration form enabling user input for destination, duration, and budget.
Aligned with Syllabus Unit 4.1 (Graphical User Interface) & Unit 2 (Exceptions & OOP).
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Callable, Optional, Dict, Any

# Resolve project root for imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.config import ALLOWED_CITIES, THEME_COLOR
from utils.validators import validate_all_inputs, ValidationError
from Logic.smart_planner import SmartTravelPlanner


class TripFormFrame(ttk.Frame):
    """
    Form view containing destination selectors, days spinners, budget entries,
    and triggering plan generation with callbacks to the main dashboard.
    """

    def __init__(self, parent: tk.Widget, on_trip_generated: Optional[Callable[[Dict[str, Any]], None]] = None):
        super().__init__(parent, padding=20)
        self.on_trip_generated = on_trip_generated
        self.planner = SmartTravelPlanner()

        self._build_ui()

    def _build_ui(self):
        """Constructs form layout and widgets."""
        # Header Label
        header_lbl = ttk.Label(
            self,
            text="Create New Travel Plan",
            font=("Helvetica", 16, "bold"),
            foreground=THEME_COLOR
        )
        header_lbl.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        # 1. City Dropdown
        ttk.Label(self, text="Select Destination:", font=("Helvetica", 11)).grid(
            row=1, column=0, sticky="w", pady=8
        )
        self.city_var = tk.StringVar(value=ALLOWED_CITIES[0])
        self.city_combo = ttk.Combobox(
            self,
            textvariable=self.city_var,
            values=list(ALLOWED_CITIES),
            state="readonly",
            width=28,
            font=("Helvetica", 10)
        )
        self.city_combo.grid(row=1, column=1, sticky="w", pady=8, padx=(10, 0))

        # 2. Number of Days (Spinbox)
        ttk.Label(self, text="Duration (Days, 1-7):", font=("Helvetica", 11)).grid(
            row=2, column=0, sticky="w", pady=8
        )
        self.days_var = tk.StringVar(value="2")
        self.days_spin = ttk.Spinbox(
            self,
            from_=1,
            to=7,
            textvariable=self.days_var,
            width=29,
            state="readonly",
            font=("Helvetica", 10)
        )
        self.days_spin.grid(row=2, column=1, sticky="w", pady=8, padx=(10, 0))

        # 3. Total Budget Entry
        ttk.Label(self, text="Total Budget (INR ₹):", font=("Helvetica", 11)).grid(
            row=3, column=0, sticky="w", pady=8
        )
        self.budget_var = tk.StringVar(value="5000")
        self.budget_entry = ttk.Entry(
            self,
            textvariable=self.budget_var,
            width=30,
            font=("Helvetica", 10)
        )
        self.budget_entry.grid(row=3, column=1, sticky="w", pady=8, padx=(10, 0))

        # 4. Save to Database Checkbox
        self.save_db_var = tk.BooleanVar(value=True)
        self.save_check = ttk.Checkbutton(
            self,
            text="Save to travel history database (SQLite)",
            variable=self.save_db_var
        )
        self.save_check.grid(row=4, column=0, columnspan=2, sticky="w", pady=(12, 16))

        # 5. Submit Button
        self.submit_btn = tk.Button(
            self,
            text="Generate Smart Itinerary",
            bg=THEME_COLOR,
            fg="white",
            font=("Helvetica", 11, "bold"),
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
            command=self._handle_submit
        )
        self.submit_btn.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(5, 10))

        # Status / Feedback label
        self.status_lbl = ttk.Label(self, text="", font=("Helvetica", 9, "italic"))
        self.status_lbl.grid(row=6, column=0, columnspan=2, sticky="w", pady=5)

    def _handle_submit(self):
        """Validates form fields and generates the itinerary."""
        raw_city = self.city_var.get()
        raw_days = self.days_var.get()
        raw_budget = self.budget_var.get()

        try:
            # Validate inputs using regular expressions (Unit 2.2)
            clean_city, clean_days, clean_budget = validate_all_inputs(
                city_input=raw_city,
                days_input=raw_days,
                budget_input=raw_budget
            )

            self.status_lbl.config(text="Generating smart plan...", foreground="blue")
            self.update_idletasks()

            # Execute travel planner logic
            plan = self.planner.plan_trip(
                city=clean_city,
                days=clean_days,
                budget=clean_budget,
                save_to_db=self.save_db_var.get()
            )

            self.status_lbl.config(
                text=f"Plan generated successfully! (Trip ID: {plan.get('trip_id') or 'N/A'})",
                foreground="green"
            )

            # Trigger navigation callback if registered
            if self.on_trip_generated:
                self.on_trip_generated(plan)

        except ValidationError as v_err:
            messagebox.showerror("Validation Error", str(v_err))
            self.status_lbl.config(text=f"Validation failed: {v_err}", foreground="red")
        except Exception as err:
            messagebox.showerror("Execution Error", f"Failed to generate trip: {err}")
            self.status_lbl.config(text="Error generating trip.", foreground="red")


if __name__ == "__main__":
    # Test execution
    root = tk.Tk()
    root.title("Trip Form Test")
    root.geometry("500x380")
    form = TripFormFrame(root, on_trip_generated=lambda p: print("Generated Trip:", p["city"], p["tier"]))
    form.pack(fill="both", expand=True)
    root.mainloop()
