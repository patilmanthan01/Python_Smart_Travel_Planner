"""
GUI/budget_view.py
Visualizes trip budget allocations using Matplotlib and Seaborn embedded in Tkinter.
Aligned with Syllabus Unit 4.1 (GUI) & Unit 6.2, 6.3 (Pandas, Matplotlib: Pie Chart, Bar Graph).
"""

import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Dict, Any, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

# Resolve project root for imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.config import THEME_COLOR
from utils.helpers import format_currency_inr


class BudgetViewFrame(ttk.Frame):
    """
    Displays budget breakdowns, statistics cards, and embeds
    interactive Matplotlib Pie and Bar charts in the Tkinter UI.
    """

    def __init__(self, parent: tk.Widget):
        super().__init__(parent, padding=15)
        self.current_plan: Optional[Dict[str, Any]] = None
        self.canvas: Optional[FigureCanvasTkAgg] = None
        self._build_ui()

    def _build_ui(self):
        """Constructs layout containing summary cards and the chart canvas container."""
        # Header Label
        header_lbl = ttk.Label(
            self,
            text="Financial Breakdown & Analytics",
            font=("Helvetica", 16, "bold"),
            foreground=THEME_COLOR
        )
        header_lbl.pack(anchor="w", pady=(0, 5))

        self.sub_header_lbl = ttk.Label(
            self,
            text="Visual representation of allocated categories and planned expenses.",
            font=("Helvetica", 10, "italic"),
            foreground="#555555"
        )
        self.sub_header_lbl.pack(anchor="w", pady=(0, 15))

        # Metrics Card Frame (Horizontal stats summary)
        self.metrics_frame = ttk.LabelFrame(self, text="Budget Overview", padding=10)
        self.metrics_frame.pack(fill="x", pady=(0, 15))

        self.total_budget_var = tk.StringVar(value="₹0.00")
        self.daily_budget_var = tk.StringVar(value="₹0.00")
        self.tier_var = tk.StringVar(value="N/A")
        self.sightseeing_status_var = tk.StringVar(value="N/A")

        # Metric Columns
        self._create_stat_card(self.metrics_frame, "Total Budget", self.total_budget_var, 0)
        self._create_stat_card(self.metrics_frame, "Daily Budget", self.daily_budget_var, 1)
        self._create_stat_card(self.metrics_frame, "Tier Class", self.tier_var, 2)
        self._create_stat_card(self.metrics_frame, "Activity Buffer", self.sightseeing_status_var, 3)

        # Matplotlib Canvas Container
        self.chart_container = ttk.Frame(self)
        self.chart_container.pack(fill="both", expand=True)

    def _create_stat_card(self, parent: ttk.Widget, title: str, textvar: tk.StringVar, col: int):
        """Helper to create structured indicator cards."""
        card = ttk.Frame(parent, padding=5)
        card.grid(row=0, column=col, sticky="nsew", padx=10)
        parent.columnconfigure(col, weight=1)

        ttk.Label(card, text=title, font=("Helvetica", 9), foreground="#666666").pack(anchor="center")
        ttk.Label(card, textvariable=textvar, font=("Helvetica", 12, "bold"), foreground=THEME_COLOR).pack(anchor="center")

    def load_budget_data(self, plan_data: Dict[str, Any]):
        """
        Parses plan dictionary, updates statistic cards, and renders
        Matplotlib subplots (Pie Chart + Bar Graph).
        """
        self.current_plan = plan_data

        total_budget = plan_data.get("total_budget", 0.0)
        days = plan_data.get("days", 1)
        tier = plan_data.get("tier", "Standard")
        breakdown = plan_data.get("budget_breakdown", {})
        activity_analysis = plan_data.get("activity_expense_analysis", {})

        # Update stats text
        self.total_budget_var.set(format_currency_inr(total_budget))
        self.daily_budget_var.set(format_currency_inr(total_budget / max(days, 1)))
        self.tier_var.set(tier)

        rem_buffer = activity_analysis.get("remaining_buffer", 0.0)
        self.sightseeing_status_var.set(f"{format_currency_inr(rem_buffer)}")

        # Render Charts
        self._render_charts(breakdown)

    def _render_charts(self, breakdown: Dict[str, float]):
        """
        Builds Matplotlib subplots (Pie Chart & Bar Chart) and embeds
        them into Tkinter using FigureCanvasTkAgg (Syllabus Unit 6.3).
        """
        # Remove previously rendered canvas if present
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        if not breakdown:
            return

        # Prepare data with Pandas Series (Unit 6.2)
        df_series = pd.Series(
            data=list(breakdown.values()),
            index=[k.capitalize() for k in breakdown.keys()]
        )

        # Setup Matplotlib Figure with 2 Subplots side-by-side
        fig, (ax_pie, ax_bar) = plt.subplots(1, 2, figsize=(8, 3.6), dpi=100)
        fig.patch.set_facecolor("#f9f9f9")

        palette = ["#2b5c8f", "#3fa796", "#e07a5f", "#f4a261"]

        # Subplot 1: Pie Chart (Unit 6.3)
        wedges, texts, autotexts = ax_pie.pie(
            df_series.values,
            labels=df_series.index,
            autopct="%1.0f%%",
            startangle=140,
            colors=palette,
            wedgeprops={"edgecolor": "white", "linewidth": 1.5}
        )
        for t in texts:
            t.set_fontsize(8)
        for at in autotexts:
            at.set_fontsize(8)
            at.set_color("white")
            at.set_weight("bold")
        ax_pie.set_title("Budget Allocation Split", fontsize=10, fontweight="bold", pad=8)

        # Subplot 2: Horizontal Bar Graph (Unit 6.3)
        bars = ax_bar.barh(df_series.index, df_series.values, color=palette, height=0.55)
        ax_bar.set_title("Amount in INR (₹)", fontsize=10, fontweight="bold", pad=8)
        ax_bar.set_xlabel("INR (₹)", fontsize=8)
        ax_bar.tick_params(axis="both", labelsize=8)
        ax_bar.grid(axis="x", linestyle="--", alpha=0.6)

        # Add data values at the end of each bar
        for bar in bars:
            width = bar.get_width()
            ax_bar.text(
                width + (max(df_series.values) * 0.02),
                bar.get_y() + bar.get_height() / 2,
                f"₹{int(width):,}",
                ha="left",
                va="center",
                fontsize=7.5
            )

        # Adjust layout spacing
        plt.tight_layout()

        # Embed inside Tkinter container
        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    # Test execution
    root = tk.Tk()
    root.title("Budget View Test")
    root.geometry("850x550")

    b_view = BudgetViewFrame(root)
    b_view.pack(fill="both", expand=True)

    dummy_plan = {
        "total_budget": 8000.0,
        "days": 2,
        "tier": "Moderate",
        "budget_breakdown": {
            "stay": 3200.0,
            "food": 2000.0,
            "travel": 1600.0,
            "sightseeing": 1200.0
        },
        "activity_expense_analysis": {
            "remaining_buffer": 480.0
        }
    }

    b_view.load_budget_data(dummy_plan)
    root.mainloop()
