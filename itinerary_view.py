"""
GUI/itenary_view.py
Displays day-wise activity schedules, time slots, locations, and costs in a structured tree/table.
"""

import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Dict, Any, Optional

# Resolve project root for imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.config import THEME_COLOR
from utils.helpers import format_currency_inr, group_itinerary_by_day


class ItineraryViewFrame(ttk.Frame):
    """
    Displays the generated itinerary in a tabular, day-grouped format
    with an interactive details panel.
    """

    def __init__(self, parent: tk.Widget):
        super().__init__(parent, padding=15)
        self.current_plan: Optional[Dict[str, Any]] = None
        self._build_ui()

    def _build_ui(self):
        """Constructs layout, Treeview table, scrollbars, and description cards."""
        self.header_lbl = ttk.Label(
            self,
            text="Day-Wise Travel Schedule",
            font=("Helvetica", 16, "bold"),
            foreground=THEME_COLOR
        )
        self.header_lbl.pack(anchor="w", pady=(0, 5))

        self.sub_header_lbl = ttk.Label(
            self,
            text="Select an activity below to view detailed spot information.",
            font=("Helvetica", 10, "italic"),
            foreground="#555555"
        )
        self.sub_header_lbl.pack(anchor="w", pady=(0, 15))

        content_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        content_pane.pack(fill="both", expand=True)

        # Left Table Frame
        table_frame = ttk.Frame(content_pane)
        content_pane.add(table_frame, weight=3)

        columns = ("slot", "place", "category", "cost")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="tree headings", selectmode="browse")

        self.tree.heading("#0", text="Day / Time", anchor="w")
        self.tree.heading("slot", text="Slot", anchor="center")
        self.tree.heading("place", text="Destination / Place", anchor="w")
        self.tree.heading("category", text="Category", anchor="center")
        self.tree.heading("cost", text="Estimated Cost", anchor="e")

        self.tree.column("#0", width=120, minwidth=100)
        self.tree.column("slot", width=90, anchor="center")
        self.tree.column("place", width=220, anchor="w")
        self.tree.column("category", width=110, anchor="center")
        self.tree.column("cost", width=110, anchor="e")

        table_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=table_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        table_scroll.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_item_select)

        # Right Details Panel
        details_frame = ttk.LabelFrame(content_pane, text="Spot Details", padding=15)
        content_pane.add(details_frame, weight=2)

        self.place_name_var = tk.StringVar(value="No place selected")
        self.category_var = tk.StringVar(value="-")
        self.cost_var = tk.StringVar(value="-")

        ttk.Label(details_frame, text="Place:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(5, 2))
        ttk.Label(details_frame, textvariable=self.place_name_var, font=("Helvetica", 11, "bold"), foreground=THEME_COLOR, wraplength=220).pack(anchor="w")

        ttk.Label(details_frame, text="Category:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(10, 2))
        ttk.Label(details_frame, textvariable=self.category_var, font=("Helvetica", 10), wraplength=220).pack(anchor="w")

        ttk.Label(details_frame, text="Estimated Cost:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(10, 2))
        ttk.Label(details_frame, textvariable=self.cost_var, font=("Helvetica", 10, "bold"), foreground="green").pack(anchor="w")

        ttk.Label(details_frame, text="Description:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(10, 2))
        self.desc_text = tk.Text(details_frame, wrap="word", height=8, width=28, font=("Helvetica", 9), relief="solid", bd=1)
        self.desc_text.pack(fill="both", expand=True, pady=(5, 0))
        self.desc_text.config(state="disabled")

    def load_itinerary_data(self, plan_data: Dict[str, Any]):
        self.current_plan = plan_data
        self.tree.delete(*self.tree.get_children())

        city = plan_data.get("city", "MMR")
        days = plan_data.get("days", 1)
        tier = plan_data.get("tier", "Standard")
        total_budget = format_currency_inr(plan_data.get("total_budget", 0))

        self.sub_header_lbl.config(
            text=f"Trip: {city} • {days} Day(s) • Tier: {tier} • Total Budget: {total_budget}"
        )

        raw_items = plan_data.get("itinerary", [])
        if not raw_items:
            return

        grouped = group_itinerary_by_day(raw_items)

        for day_num, items in sorted(grouped.items()):
            day_node = self.tree.insert("", "end", text=f"📅 Day {day_num}", open=True)

            for item in items:
                cost_str = format_currency_inr(item.get("estimated_cost", 0))
                self.tree.insert(
                    day_node,
                    "end",
                    text=f"  {item.get('time_slot', '')}",
                    values=(
                        item.get("time_slot", ""),
                        item.get("place_name", ""),
                        item.get("category", ""),
                        cost_str
                    ),
                    tags=(item.get("place_name", ""),)
                )

    def _on_item_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        values = self.tree.item(selected_item[0], "values")
        if not values:
            return

        slot, place_name, category, cost = values
        self.place_name_var.set(place_name)
        self.category_var.set(category)
        self.cost_var.set(cost)

        description = "No description available."
        if self.current_plan:
            for item in self.current_plan.get("itinerary", []):
                if item.get("place_name") == place_name:
                    description = item.get("description", "A key highlight on your itinerary.")
                    break

        self.desc_text.config(state="normal")
        self.desc_text.delete("1.0", tk.END)
        self.desc_text.insert(tk.END, description)
        self.desc_text.config(state="disabled")
