"""
Question 4 — Smart Energy Grid Load Distribution Optimizer
Run this file in VS Code with Python 3 installed.
Required libraries: tkinter (built-in), matplotlib
Install matplotlib if needed: pip install matplotlib
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches

#  DATA

# Full 24-hour demand data (kWh) for Districts A, B, C
DEMAND_DATA = {
    "06": {"A": 20, "B": 15, "C": 25},
    "07": {"A": 22, "B": 16, "C": 28},
    "08": {"A": 25, "B": 18, "C": 30},
    "09": {"A": 28, "B": 20, "C": 32},
    "10": {"A": 30, "B": 22, "C": 35},
    "11": {"A": 32, "B": 24, "C": 36},
    "12": {"A": 35, "B": 25, "C": 38},
    "13": {"A": 33, "B": 24, "C": 36},
    "14": {"A": 30, "B": 22, "C": 34},
    "15": {"A": 28, "B": 20, "C": 32},
    "16": {"A": 26, "B": 19, "C": 30},
    "17": {"A": 24, "B": 18, "C": 28},
    "18": {"A": 22, "B": 17, "C": 26},
    "19": {"A": 30, "B": 22, "C": 35},
    "20": {"A": 35, "B": 28, "C": 40},
    "21": {"A": 32, "B": 25, "C": 38},
    "22": {"A": 28, "B": 20, "C": 33},
    "23": {"A": 20, "B": 15, "C": 25},
}

# Energy sources
SOURCES = [
    {"id": "S1", "type": "Solar",  "max_cap": 50, "start":  6, "end": 18, "cost": 1.0, "color": "#F4C430"},
    {"id": "S2", "type": "Hydro",  "max_cap": 40, "start":  0, "end": 24, "cost": 1.5, "color": "#4FC3F7"},
    {"id": "S3", "type": "Diesel", "max_cap": 60, "start": 17, "end": 23, "cost": 3.0, "color": "#EF5350"},
]

COLORS = {
    "bg":       "#1A1F2E",
    "panel":    "#242B3D",
    "card":     "#2D3548",
    "accent":   "#4FC3F7",
    "green":    "#66BB6A",
    "yellow":   "#F4C430",
    "red":      "#EF5350",
    "text":     "#E8EAF0",
    "subtext":  "#8B9BB4",
    "border":   "#3A4560",
    "solar":    "#F4C430",
    "hydro":    "#4FC3F7",
    "diesel":   "#EF5350",
}



#  ALGORITHM  (Greedy + ±10% tolerance)

def allocate_hour(hour_str, demand_override=None):
    """
    For a given hour, greedily allocate the cheapest available
    energy sources to meet district demand (with ±10% tolerance).
    Returns a dict with full breakdown.
    """
    hour = int(hour_str)
    districts = demand_override if demand_override else DEMAND_DATA[hour_str]
    total_demand = sum(districts.values())

    # Available sources sorted by cost (greedy: cheapest first)
    avail = [s for s in SOURCES if s["start"] <= hour < s["end"]]
    avail.sort(key=lambda x: x["cost"])

    remaining = total_demand
    allocations = {"Solar": 0, "Hydro": 0, "Diesel": 0}
    cost = 0.0

    for source in avail:
        if remaining <= 0:
            break
        use = min(source["max_cap"], remaining)
        allocations[source["type"]] += use
        cost += use * source["cost"]
        remaining -= use

    # ±10% tolerance check
    tolerance = total_demand * 0.10
    fulfilled = total_demand - max(remaining, 0)
    pct_met = round(fulfilled / total_demand * 100, 1) if total_demand > 0 else 0
    within_tolerance = abs(fulfilled - total_demand) <= tolerance

    renewable = allocations["Solar"] + allocations["Hydro"]
    renewable_pct = round(renewable / fulfilled * 100, 1) if fulfilled > 0 else 0

    return {
        "hour": hour_str,
        "districts": districts,
        "total_demand": total_demand,
        "allocations": allocations,
        "cost": round(cost, 2),
        "fulfilled": fulfilled,
        "pct_met": pct_met,
        "within_tolerance": within_tolerance,
        "renewable_pct": renewable_pct,
        "diesel_used": allocations["Diesel"] > 0,
    }


def run_full_day(demand_data=None):
    data = demand_data if demand_data else DEMAND_DATA
    results = []
    for hour_str in sorted(data.keys()):
        results.append(allocate_hour(hour_str, data.get(hour_str)))
    return results


#  GUI

class EnergyGridApp:
    def __init__(self, root):
        self.root = root
        self.root.title(" Smart Energy Grid — Nepal Load Distribution Optimizer")
        self.root.geometry("1280x820")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(True, True)

        self._build_ui()
        self._run_simulation()

    # Layout
    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=COLORS["panel"], pady=12)
        header.pack(fill="x")
        tk.Label(header, text="  Smart Energy Grid Load Distribution",
                font=("Consolas", 18, "bold"), bg=COLORS["panel"],
                fg=COLORS["accent"]).pack(side="left", padx=20)
        tk.Label(header, text="Nepal — Greedy + DP Optimizer",
                font=("Consolas", 11), bg=COLORS["panel"],
                fg=COLORS["subtext"]).pack(side="left")

        # Main area
        main = tk.Frame(self.root, bg=COLORS["bg"])
        main.pack(fill="both", expand=True, padx=10, pady=8)

        # Left column: controls + KPI cards + table
        left = tk.Frame(main, bg=COLORS["bg"], width=540)
        left.pack(side="left", fill="both", expand=False, padx=(0, 8))
        left.pack_propagate(False)

        # Right column: charts
        right = tk.Frame(main, bg=COLORS["bg"])
        right.pack(side="left", fill="both", expand=True)

        self._build_controls(left)
        self._build_kpi_cards(left)
        self._build_table(left)
        self._build_charts(right)

    def _build_controls(self, parent):
        frame = tk.Frame(parent, bg=COLORS["card"], pady=10, padx=12)
        frame.pack(fill="x", pady=(0, 8))

        tk.Label(frame, text="SIMULATION CONTROLS",
                font=("Consolas", 9, "bold"), bg=COLORS["card"],
                fg=COLORS["subtext"]).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

        # Hour selector
        tk.Label(frame, text="Select Hour:", font=("Consolas", 10),
                bg=COLORS["card"], fg=COLORS["text"]).grid(row=1, column=0, sticky="w")
        self.hour_var = tk.StringVar(value="06")
        hour_cb = ttk.Combobox(frame, textvariable=self.hour_var,
                            values=sorted(DEMAND_DATA.keys()), width=6, state="readonly")
        hour_cb.grid(row=1, column=1, padx=6)

        # Demand override entries
        tk.Label(frame, text="District A:", font=("Consolas", 10),
                bg=COLORS["card"], fg=COLORS["text"]).grid(row=2, column=0, sticky="w", pady=4)
        self.da_var = tk.StringVar(value="20")
        tk.Entry(frame, textvariable=self.da_var, width=6,
                bg=COLORS["border"], fg=COLORS["text"], insertbackground=COLORS["text"]).grid(row=2, column=1, padx=6)

        tk.Label(frame, text="District B:", font=("Consolas", 10),
                bg=COLORS["card"], fg=COLORS["text"]).grid(row=2, column=2, sticky="w")
        self.db_var = tk.StringVar(value="15")
        tk.Entry(frame, textvariable=self.db_var, width=6,
                bg=COLORS["border"], fg=COLORS["text"], insertbackground=COLORS["text"]).grid(row=2, column=3, padx=6)

        tk.Label(frame, text="District C:", font=("Consolas", 10),
                bg=COLORS["card"], fg=COLORS["text"]).grid(row=3, column=0, sticky="w")
        self.dc_var = tk.StringVar(value="25")
        tk.Entry(frame, textvariable=self.dc_var, width=6,
                bg=COLORS["border"], fg=COLORS["text"], insertbackground=COLORS["text"]).grid(row=3, column=1, padx=6)

        # Buttons
        btn_frame = tk.Frame(frame, bg=COLORS["card"])
        btn_frame.grid(row=4, column=0, columnspan=4, pady=(10, 0), sticky="w")

        tk.Button(btn_frame, text=" Run Hour",
                font=("Consolas", 10, "bold"),
                bg=COLORS["accent"], fg=COLORS["bg"],
                relief="flat", padx=12, pady=4,
                command=self._run_single_hour).pack(side="left", padx=(0, 8))

        tk.Button(btn_frame, text=" Full Day Sim",
                font=("Consolas", 10, "bold"),
                bg=COLORS["green"], fg=COLORS["bg"],
                relief="flat", padx=12, pady=4,
                command=self._run_simulation).pack(side="left", padx=(0, 8))

        tk.Button(btn_frame, text=" Reset",
                font=("Consolas", 10),
                bg=COLORS["card"], fg=COLORS["subtext"],
                relief="flat", padx=12, pady=4,
                command=self._reset).pack(side="left")

        # Hook hour selection to auto-fill demand
        hour_cb.bind("<<ComboboxSelected>>", self._on_hour_change)

    def _build_kpi_cards(self, parent):
        self.kpi_frame = tk.Frame(parent, bg=COLORS["bg"])
        self.kpi_frame.pack(fill="x", pady=(0, 8))

        self.kpi_labels = {}
        cards = [
            ("total_cost",    " Total Cost",   "Rs. 0",    COLORS["yellow"]),
            ("renewable_pct", " Renewable %",  "0%",       COLORS["green"]),
            ("diesel_hours",  " Diesel Hours", "0 hrs",    COLORS["red"]),
            ("avg_met",       " Avg Fulfilled", "0%",      COLORS["accent"]),
        ]
        for i, (key, label, default, color) in enumerate(cards):
            card = tk.Frame(self.kpi_frame, bg=COLORS["card"], padx=10, pady=8)
            card.grid(row=0, column=i, padx=4, sticky="nsew")
            self.kpi_frame.columnconfigure(i, weight=1)
            tk.Label(card, text=label, font=("Consolas", 8),
                    bg=COLORS["card"], fg=COLORS["subtext"]).pack(anchor="w")
            lbl = tk.Label(card, text=default, font=("Consolas", 14, "bold"),
                        bg=COLORS["card"], fg=color)
            lbl.pack(anchor="w")
            self.kpi_labels[key] = lbl

    def _build_table(self, parent):
        table_frame = tk.Frame(parent, bg=COLORS["card"], padx=4, pady=4)
        table_frame.pack(fill="both", expand=True)

        tk.Label(table_frame, text="ALLOCATION TABLE",
                font=("Consolas", 9, "bold"), bg=COLORS["card"],
                fg=COLORS["subtext"]).pack(anchor="w", padx=8, pady=(4, 2))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Grid.Treeview",
                        background=COLORS["panel"],
                        foreground=COLORS["text"],
                        fieldbackground=COLORS["panel"],
                        rowheight=22,
                        font=("Consolas", 9))
        style.configure("Grid.Treeview.Heading",
                        background=COLORS["border"],
                        foreground=COLORS["accent"],
                        font=("Consolas", 9, "bold"),
                        relief="flat")
        style.map("Grid.Treeview",
                background=[("selected", COLORS["accent"])],
                foreground=[("selected", COLORS["bg"])])

        cols = ("Hour", "Solar", "Hydro", "Diesel", "Total", "Demand", "% Met", "Cost (Rs.)")
        self.tree = ttk.Treeview(table_frame, columns=cols,
                                show="headings", style="Grid.Treeview")
        widths = [45, 55, 55, 55, 55, 60, 55, 75]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        # Tag colors
        self.tree.tag_configure("diesel",  background="#3B2020", foreground=COLORS["red"])
        self.tree.tag_configure("ok",      background=COLORS["panel"])
        self.tree.tag_configure("warn",    background="#2B3020", foreground=COLORS["yellow"])

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=4)
        scrollbar.pack(side="right", fill="y", pady=4)

    def _build_charts(self, parent):
        tk.Label(parent, text="ANALYTICS DASHBOARD",
                font=("Consolas", 9, "bold"), bg=COLORS["bg"],
                fg=COLORS["subtext"]).pack(anchor="w", padx=4)

        self.fig, self.axes = plt.subplots(2, 2, figsize=(7, 5.5))
        self.fig.patch.set_facecolor(COLORS["bg"])
        for ax in self.axes.flat:
            ax.set_facecolor(COLORS["panel"])
            ax.tick_params(colors=COLORS["subtext"], labelsize=7)
            for spine in ax.spines.values():
                spine.set_edgecolor(COLORS["border"])

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)

    # Logic 
    def _on_hour_change(self, event=None):
        h = self.hour_var.get()
        if h in DEMAND_DATA:
            d = DEMAND_DATA[h]
            self.da_var.set(str(d["A"]))
            self.db_var.set(str(d["B"]))
            self.dc_var.set(str(d["C"]))

    def _run_single_hour(self):
        hour = self.hour_var.get()
        try:
            demand = {
                "A": int(self.da_var.get()),
                "B": int(self.db_var.get()),
                "C": int(self.dc_var.get()),
            }
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid integer demand values.")
            return

        result = allocate_hour(hour, demand)
        self._show_single_result(result)

    def _show_single_result(self, r):
        # Clear table and show just this hour
        for row in self.tree.get_children():
            self.tree.delete(row)

        tag = "diesel" if r["diesel_used"] else ("warn" if not r["within_tolerance"] else "ok")
        alloc = r["allocations"]
        self.tree.insert("", "end", values=(
            r["hour"],
            alloc["Solar"], alloc["Hydro"], alloc["Diesel"],
            int(r["fulfilled"]), r["total_demand"],
            f"{r['pct_met']}%", f"{r['cost']}"
        ), tags=(tag,))

        # KPI for single hour
        self.kpi_labels["total_cost"].config(text=f"Rs. {r['cost']}")
        self.kpi_labels["renewable_pct"].config(text=f"{r['renewable_pct']}%")
        self.kpi_labels["diesel_hours"].config(text="Yes" if r["diesel_used"] else "No")
        self.kpi_labels["avg_met"].config(text=f"{r['pct_met']}%")

        self._update_single_charts(r)

    def _update_single_charts(self, r):
        for ax in self.axes.flat:
            ax.clear()
            ax.set_facecolor(COLORS["panel"])
            ax.tick_params(colors=COLORS["subtext"], labelsize=7)
            for spine in ax.spines.values():
                spine.set_edgecolor(COLORS["border"])

        alloc = r["allocations"]

        # Chart 1: Source breakdown pie
        ax = self.axes[0][0]
        vals = [alloc["Solar"], alloc["Hydro"], alloc["Diesel"]]
        labels = ["Solar", "Hydro", "Diesel"]
        colors = [COLORS["solar"], COLORS["hydro"], COLORS["diesel"]]
        non_zero = [(v, l, c) for v, l, c in zip(vals, labels, colors) if v > 0]
        if non_zero:
            ax.pie([x[0] for x in non_zero], labels=[x[1] for x in non_zero],
                colors=[x[2] for x in non_zero], autopct="%1.0f%%",
                textprops={"color": COLORS["text"], "fontsize": 8},
                startangle=90)
        ax.set_title(f"Hour {r['hour']} — Source Mix", color=COLORS["accent"], fontsize=9, pad=6)

        # Chart 2: District demand bar
        ax2 = self.axes[0][1]
        dists = list(r["districts"].keys())
        vals2 = list(r["districts"].values())
        bars = ax2.bar(dists, vals2, color=[COLORS["accent"], COLORS["green"], COLORS["yellow"]], width=0.5)
        ax2.set_title("District Demand (kWh)", color=COLORS["accent"], fontsize=9, pad=6)
        ax2.set_ylabel("kWh", color=COLORS["subtext"], fontsize=7)
        for bar, val in zip(bars, vals2):
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                    str(val), ha="center", va="bottom", color=COLORS["text"], fontsize=8)

        # Chart 3: Cost breakdown
        ax3 = self.axes[1][0]
        sources_used = [(k, v * (1.0 if k == "Solar" else 1.5 if k == "Hydro" else 3.0))
                        for k, v in alloc.items() if v > 0]
        if sources_used:
            ax3.bar([s[0] for s in sources_used], [s[1] for s in sources_used],
                    color=[COLORS["solar"] if s[0] == "Solar" else COLORS["hydro"] if s[0] == "Hydro" else COLORS["diesel"]
                        for s in sources_used], width=0.4)
        ax3.set_title("Cost per Source (Rs.)", color=COLORS["accent"], fontsize=9, pad=6)
        ax3.set_ylabel("Rs.", color=COLORS["subtext"], fontsize=7)

        # Chart 4: Fulfillment gauge
        ax4 = self.axes[1][1]
        pct = r["pct_met"]
        color = COLORS["green"] if pct >= 90 else COLORS["yellow"] if pct >= 70 else COLORS["red"]
        ax4.barh(["Fulfilled"], [pct], color=color, height=0.4)
        ax4.barh(["Fulfilled"], [100], color=COLORS["border"], height=0.4)
        ax4.barh(["Fulfilled"], [pct], color=color, height=0.4)
        ax4.set_xlim(0, 100)
        ax4.set_title(f"Demand Fulfilled: {pct}%", color=COLORS["accent"], fontsize=9, pad=6)
        ax4.text(pct / 2, 0, f"{pct}%", ha="center", va="center",
                color=COLORS["bg"], fontsize=12, fontweight="bold")

        self.fig.tight_layout(pad=1.5)
        self.canvas.draw()

    def _run_simulation(self):
        results = run_full_day()
        self._populate_table(results)
        self._update_kpis(results)
        self._update_full_day_charts(results)

    def _populate_table(self, results):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in results:
            tag = "diesel" if r["diesel_used"] else ("warn" if not r["within_tolerance"] else "ok")
            alloc = r["allocations"]
            self.tree.insert("", "end", values=(
                r["hour"],
                alloc["Solar"], alloc["Hydro"], alloc["Diesel"],
                int(r["fulfilled"]), r["total_demand"],
                f"{r['pct_met']}%", f"{r['cost']}"
            ), tags=(tag,))

    def _update_kpis(self, results):
        total_cost = sum(r["cost"] for r in results)
        avg_renewable = sum(r["renewable_pct"] for r in results) / len(results)
        diesel_hours = sum(1 for r in results if r["diesel_used"])
        avg_met = sum(r["pct_met"] for r in results) / len(results)

        self.kpi_labels["total_cost"].config(text=f"Rs. {total_cost:,.1f}")
        self.kpi_labels["renewable_pct"].config(text=f"{avg_renewable:.1f}%")
        self.kpi_labels["diesel_hours"].config(text=f"{diesel_hours} hrs")
        self.kpi_labels["avg_met"].config(text=f"{avg_met:.1f}%")

    def _update_full_day_charts(self, results):
        for ax in self.axes.flat:
            ax.clear()
            ax.set_facecolor(COLORS["panel"])
            ax.tick_params(colors=COLORS["subtext"], labelsize=7)
            for spine in ax.spines.values():
                spine.set_edgecolor(COLORS["border"])

        hours = [r["hour"] for r in results]
        solar  = [r["allocations"]["Solar"]  for r in results]
        hydro  = [r["allocations"]["Hydro"]  for r in results]
        diesel = [r["allocations"]["Diesel"] for r in results]
        demand = [r["total_demand"] for r in results]
        costs  = [r["cost"] for r in results]

        x = range(len(hours))

        # Chart 1: Stacked area — energy mix over the day
        ax1 = self.axes[0][0]
        ax1.stackplot(x, solar, hydro, diesel,
                    labels=["Solar", "Hydro", "Diesel"],
                    colors=[COLORS["solar"], COLORS["hydro"], COLORS["diesel"]],
                    alpha=0.85)
        ax1.plot(x, demand, color="white", linewidth=1.5, linestyle="--", label="Demand")
        ax1.set_xticks(x[::2])
        ax1.set_xticklabels(hours[::2], rotation=45, fontsize=6)
        ax1.set_title("Energy Mix vs Demand (24h)", color=COLORS["accent"], fontsize=9, pad=6)
        ax1.set_ylabel("kWh", color=COLORS["subtext"], fontsize=7)
        ax1.legend(loc="upper left", fontsize=6,
                facecolor=COLORS["card"], edgecolor=COLORS["border"],
                labelcolor=COLORS["text"])

        # Chart 2: Hourly cost
        ax2 = self.axes[0][1]
        bar_colors = [COLORS["red"] if r["diesel_used"] else COLORS["green"] for r in results]
        ax2.bar(x, costs, color=bar_colors, width=0.7)
        ax2.set_xticks(x[::2])
        ax2.set_xticklabels(hours[::2], rotation=45, fontsize=6)
        ax2.set_title("Hourly Cost (Rs.) — Red = Diesel Used", color=COLORS["accent"], fontsize=9, pad=6)
        ax2.set_ylabel("Rs.", color=COLORS["subtext"], fontsize=7)

        # Chart 3: Renewable % per hour
        ax3 = self.axes[1][0]
        ren_pct = [r["renewable_pct"] for r in results]
        ax3.fill_between(x, ren_pct, alpha=0.4, color=COLORS["green"])
        ax3.plot(x, ren_pct, color=COLORS["green"], linewidth=1.5)
        ax3.axhline(y=80, color=COLORS["yellow"], linestyle="--", linewidth=0.8, label="80% target")
        ax3.set_xticks(x[::2])
        ax3.set_xticklabels(hours[::2], rotation=45, fontsize=6)
        ax3.set_ylim(0, 110)
        ax3.set_title("Renewable Energy % per Hour", color=COLORS["accent"], fontsize=9, pad=6)
        ax3.set_ylabel("%", color=COLORS["subtext"], fontsize=7)
        ax3.legend(fontsize=6, facecolor=COLORS["card"],
                edgecolor=COLORS["border"], labelcolor=COLORS["text"])

        # Chart 4: Source totals pie
        ax4 = self.axes[1][1]
        total_solar  = sum(solar)
        total_hydro  = sum(hydro)
        total_diesel = sum(diesel)
        vals   = [total_solar, total_hydro, total_diesel]
        labels = [f"Solar\n{total_solar} kWh", f"Hydro\n{total_hydro} kWh", f"Diesel\n{total_diesel} kWh"]
        colors = [COLORS["solar"], COLORS["hydro"], COLORS["diesel"]]
        explode = [0.03, 0.03, 0.08]
        non_zero = [(v, l, c, e) for v, l, c, e in zip(vals, labels, colors, explode) if v > 0]
        if non_zero:
            ax4.pie([n[0] for n in non_zero], labels=[n[1] for n in non_zero],
                    colors=[n[2] for n in non_zero], explode=[n[3] for n in non_zero],
                    autopct="%1.0f%%",
                    textprops={"color": COLORS["text"], "fontsize": 7},
                    startangle=140)
        ax4.set_title("Full Day — Source Totals", color=COLORS["accent"], fontsize=9, pad=6)

        self.fig.tight_layout(pad=1.5)
        self.canvas.draw()

    def _reset(self):
        self.hour_var.set("06")
        self.da_var.set("20")
        self.db_var.set("15")
        self.dc_var.set("25")
        self._run_simulation()


#  ENTRY POINT

if __name__ == "__main__":
    root = tk.Tk()
    app = EnergyGridApp(root)
    root.mainloop()