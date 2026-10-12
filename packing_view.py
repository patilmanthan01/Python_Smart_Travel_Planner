"""
GUI/packing_view.py
Interactive checklist view for trip packing essentials based on duration and weather.
Aligned with Syllabus Unit 1.3 (Lists & Dicts), Unit 2.1 (OOP), & Unit 4.1 (GUI).
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Dict, Any, List, Optional

# Resolve project root for imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.config import THEME_COLOR


class PackingViewFrame(ttk.Frame):
    """
    Displays an interactive, weather-aware packing checklist with 
    progress tracking and custom item addition.
    """

    def __init__(self, parent: tk.Widget):
        super().__init__(parent, padding=20)
        self.check_vars: Dict[str, tk.BooleanVar] = {}
        self.items_list: List[str] = []
        self._build_ui()

    def _build_ui(self):
        """Constructs layout, header, checklist container, and controls."""
        # Header Label
        header_lbl = ttk.Label(
            self,
            text="Smart Packing Checklist",
            font=("Helvetica", 16, "bold"),
            foreground=THEME_COLOR
        )
        header_lbl.pack(anchor="w", pady=(0, 5))

        self.subtitle_lbl = ttk.Label(
            self,
            text="Check off items as you pack. Tailored to your trip duration and weather forecast.",
            font=("Helvetica", 10, "italic"),
            foreground="#555555"
        )
        self.subtitle_lbl.pack(anchor="w", pady=(0, 15))

        # Progress Bar & Counter Card
        progress_card = ttk.LabelFrame(self, text="Packing Progress", padding=10)
        progress_card.pack(fill="x", pady=(0, 15))

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(
            progress_card,
            variable=self.progress_var,
            maximum=100.0,
            mode="determinate"
        )
        self.progress_bar.pack(fill="x", pady=(0, 5))

        self.progress_lbl = ttk.Label(
            progress_card,
            text="0 of 0 items packed (0%)",
            font=("Helvetica", 9, "bold"),
            foreground=THEME_COLOR
        )
        self.progress_lbl.pack(anchor="e")

        # Scrollable Canvas Container for Checkboxes
        list_container = ttk.Frame(self)
        list_container.pack(fill="both", expand=True, pady=(0, 15))

        self.canvas = tk.Canvas(list_container, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Controls & Custom Add Item Bar
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill="x")

        self.new_item_var = tk.StringVar()
        self.new_item_entry = ttk.Entry(
            controls_frame,
            textvariable=self.new_item_var,
            font=("Helvetica", 10),
            width=30
        )
        self.new_item_entry.pack(side="left", padx=(0, 8))

        add_btn = ttk.Button(controls_frame, text="Add Item", command=self._add_custom_item)
        add_btn.pack(side="left", padx=(0, 8))

        reset_btn = ttk.Button(controls_frame, text="Reset Checks", command=self._reset_all_checks)
        reset_btn.pack(side="right")

    def load_packing_list(self, packing_items: List[str]):
        """Populates checklist items dynamically from smart planner response."""
        self.items_list = list(packing_items)
        self._render_checkboxes()

    def _render_checkboxes(self):
        """Clears and re-renders checkbox rows inside the scrollable container."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.check_vars.clear()

        for item in self.items_list:
            var = tk.BooleanVar(value=False)
            self.check_vars[item] = var

            chk = ttk.Checkbutton(
                self.scrollable_frame,
                text=f"  {item}",
                variable=var,
                command=self._update_progress
            )
            chk.pack(anchor="w", pady=4, padx=5)

        self._update_progress()

    def _update_progress(self):
        """Calculates current check progress and updates progress bar."""
        total = len(self.check_vars)
        if total == 0:
            self.progress_var.set(0.0)
            self.progress_lbl.config(text="0 of 0 items packed (0%)")
            return

        packed = sum(1 for var in self.check_vars.values() if var.get())
        pct = (packed / total) * 100.0

        self.progress_var.set(pct)
        self.progress_lbl.config(text=f"{packed} of {total} items packed ({int(pct)}%)")

    def _add_custom_item(self):
        """Appends a user-defined packing item to the checklist."""
        item_text = self.new_item_var.get().strip()
        if not item_text:
            return

        if item_text in self.items_list:
            messagebox.showinfo("Duplicate", "This item is already on your packing list.")
            return

        self.items_list.append(item_text)
        self.new_item_var.set("")
        self._render_checkboxes()

    def _reset_all_checks(self):
        """Unchecks all items in the list."""
        for var in self.check_vars.values():
            var.set(False)
        self._update_progress()


if __name__ == "__main__":
    # Test execution
    root = tk.Tk()
    root.title("Packing View Test")
    root.geometry("600x500")

    p_view = PackingViewFrame(root)
    p_view.pack(fill="both", expand=True)

    dummy_checklist = [
        "Government Photo ID & College ID",
        "Smartphone & Fast Power Bank",
        "Reusable Water Bottle",
        "Clothing sets for 2 day(s)",
        "Compact Umbrella / Windproof Raincoat",
        "Waterproof Phone Pouch",
        "Quick-dry footwear (Floaters/Sandals)"
    ]
    p_view.load_packing_list(dummy_checklist)

    root.mainloop()
