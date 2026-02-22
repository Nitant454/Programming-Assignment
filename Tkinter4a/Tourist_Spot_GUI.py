"""
Question 5(a) — Tourist Spot Optimizer
GUI-based Itinerary Planner with Heuristic (Greedy) + Brute Force Comparison
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import itertools
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ─────────────────────────────────────────────
#  DATASET
# ─────────────────────────────────────────────

SPOTS = [
    {"name": "Pashupatinath Temple",   "lat": 27.7104, "lon": 85.3488, "fee": 100, "open": 6,  "close": 18, "tags": ["culture", "religious"], "duration": 1.5},
    {"name": "Swayambhunath Stupa",    "lat": 27.7149, "lon": 85.2906, "fee": 200, "open": 7,  "close": 17, "tags": ["culture", "heritage"],  "duration": 1.5},
    {"name": "Garden of Dreams",       "lat": 27.7125, "lon": 85.3170, "fee": 150, "open": 9,  "close": 21, "tags": ["nature", "relaxation"], "duration": 1.0},
    {"name": "Chandragiri Hills",      "lat": 27.6616, "lon": 85.2458, "fee": 700, "open": 9,  "close": 17, "tags": ["nature", "adventure"],  "duration": 2.0},
    {"name": "Kathmandu Durbar Square","lat": 27.7048, "lon": 85.3076, "fee": 100, "open": 10, "close": 17, "tags": ["culture", "heritage"],  "duration": 1.5},
    {"name": "Boudhanath Stupa",       "lat": 27.7215, "lon": 85.3620, "fee": 400, "open": 6,  "close": 20, "tags": ["culture", "religious"], "duration": 1.0},
    {"name": "Namobuddha",             "lat": 27.5886, "lon": 85.5472, "fee": 50,  "open": 7,  "close": 17, "tags": ["religious", "nature"],  "duration": 2.0},
    {"name": "Phewa Lake Pokhara",     "lat": 28.2096, "lon": 83.9856, "fee": 0,   "open": 6,  "close": 18, "tags": ["nature", "relaxation"], "duration": 2.0},
]

COLORS = {
    "bg":     "#1A1F2E",
    "panel":  "#242B3D",
    "card":   "#2D3548",
    "accent": "#4FC3F7",
    "green":  "#66BB6A",
    "yellow": "#F4C430",
    "red":    "#EF5350",
    "purple": "#AB47BC",
    "text":   "#E8EAF0",
    "sub":    "#8B9BB4",
    "border": "#3A4560",
}

ALL_TAGS = sorted(set(tag for s in SPOTS for tag in s["tags"]))

# ─────────────────────────────────────────────
#  ALGORITHMS
# ─────────────────────────────────────────────

def euclidean_distance(a, b):
    """Distance in km (approximate using coordinate difference)."""
    return math.sqrt((a["lat"] - b["lat"])**2 + (a["lon"] - b["lon"])**2) * 111


def score_spot(spot, current_pos, interests, budget_left, current_hour):
    """Score a spot for greedy selection."""
    interest_match = len(set(spot["tags"]) & set(interests))
    dist = euclidean_distance(current_pos, spot)
    fee_penalty = spot["fee"] / 100
    score = interest_match * 20 - dist * 3 - fee_penalty
    return score


def greedy_itinerary(budget, total_hours, interests, start_hour=9):
    """Greedy heuristic: always pick the highest-scoring unvisited affordable spot."""
    current_hour = start_hour
    remaining_budget = budget
    visited = []
    reasons = []
    current_pos = {"lat": 27.7104, "lon": 85.3488}  # Start near city centre

    while True:
        best_spot = None
        best_score = -999
        best_reason = ""

        for spot in SPOTS:
            if spot in visited:
                continue
            if spot["fee"] > remaining_budget:
                continue
            if current_hour < spot["open"] or current_hour + spot["duration"] > spot["close"]:
                continue
            if (current_hour - start_hour) + spot["duration"] > total_hours:
                continue

            s = score_spot(spot, current_pos, interests, remaining_budget, current_hour)
            tag_hits = set(spot["tags"]) & set(interests)
            dist = euclidean_distance(current_pos, spot)

            reason = f"Interest match ({', '.join(tag_hits) if tag_hits else 'none'}), " \
                    f"dist={dist:.2f}km, fee=Rs.{spot['fee']}, score={s:.1f}"

            if s > best_score:
                best_score = s
                best_spot = spot
                best_reason = reason

        if best_spot is None:
            break

        visited.append(best_spot)
        reasons.append(best_reason)
        remaining_budget -= best_spot["fee"]
        current_hour += best_spot["duration"] + 0.3   # 0.3h travel
        current_pos = best_spot

    return visited, reasons


def brute_force_itinerary(budget, total_hours, interests, start_hour=9):
    """Brute force: try all permutations of spots (small dataset only)."""
    small_spots = SPOTS[:6]   # limit to 6 for performance
    best = []
    best_score = -1

    for r in range(1, len(small_spots) + 1):
        for perm in itertools.permutations(small_spots, r):
            total_fee = sum(s["fee"] for s in perm)
            total_time = sum(s["duration"] + 0.3 for s in perm)
            if total_fee > budget or total_time > total_hours:
                continue
            # Check open hours sequentially
            valid = True
            hour = start_hour
            for spot in perm:
                if hour < spot["open"] or hour + spot["duration"] > spot["close"]:
                    valid = False
                    break
                hour += spot["duration"] + 0.3
            if not valid:
                continue

            interest_score = sum(len(set(s["tags"]) & set(interests)) for s in perm)
            if interest_score > best_score or (interest_score == best_score and len(perm) > len(best)):
                best_score = interest_score
                best = list(perm)

    return best


# ─────────────────────────────────────────────
#  GUI APPLICATION
# ─────────────────────────────────────────────

class TouristApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🗺️  Tourist Spot Optimizer — Kathmandu Itinerary Planner")
        self.root.geometry("1300x840")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(True, True)

        self._apply_styles()
        self._build_ui()

    # ── Styles ──────────────────────────────
    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TCombobox",
                        fieldbackground=COLORS["border"],
                        background=COLORS["border"],
                        foreground=COLORS["text"],
                        selectbackground=COLORS["accent"],
                        selectforeground=COLORS["bg"])

        style.configure("Tour.Treeview",
                        background=COLORS["panel"],
                        foreground=COLORS["text"],
                        fieldbackground=COLORS["panel"],
                        rowheight=24,
                        font=("Consolas", 9))
        style.configure("Tour.Treeview.Heading",
                        background=COLORS["border"],
                        foreground=COLORS["accent"],
                        font=("Consolas", 9, "bold"),
                        relief="flat")
        style.map("Tour.Treeview",
                background=[("selected", COLORS["accent"])],
                foreground=[("selected", COLORS["bg"])])

    # ── Layout ──────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg=COLORS["panel"], pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🗺️  Tourist Spot Optimizer",
                font=("Consolas", 17, "bold"),
                bg=COLORS["panel"], fg=COLORS["accent"]).pack(side="left", padx=20)
        tk.Label(hdr, text="Heuristic Itinerary Planner — Kathmandu, Nepal",
                font=("Consolas", 10),
                bg=COLORS["panel"], fg=COLORS["sub"]).pack(side="left")

        # Body
        body = tk.Frame(self.root, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=10, pady=8)

        left = tk.Frame(body, bg=COLORS["bg"], width=420)
        left.pack(side="left", fill="y", padx=(0, 8))
        left.pack_propagate(False)

        right = tk.Frame(body, bg=COLORS["bg"])
        right.pack(side="left", fill="both", expand=True)

        self._build_input_panel(left)
        self._build_kpi_row(left)
        self._build_results_panel(left)
        self._build_right_panel(right)

    # ── Input Panel ─────────────────────────
    def _build_input_panel(self, parent):
        frame = tk.Frame(parent, bg=COLORS["card"], padx=14, pady=12)
        frame.pack(fill="x", pady=(0, 8))

        tk.Label(frame, text="USER PREFERENCES",
                font=("Consolas", 8, "bold"),
                bg=COLORS["card"], fg=COLORS["sub"]).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        def label(row, text):
            tk.Label(frame, text=text, font=("Consolas", 10),
                    bg=COLORS["card"], fg=COLORS["text"]).grid(row=row, column=0, sticky="w", pady=4)

        def entry(row, default, var):
            e = tk.Entry(frame, textvariable=var, width=10,
                        bg=COLORS["border"], fg=COLORS["text"],
                        font=("Consolas", 10),
                        insertbackground=COLORS["text"],
                        relief="flat", bd=4)
            e.grid(row=row, column=1, sticky="w", padx=8, pady=4)

        self.budget_var = tk.StringVar(value="1500")
        self.hours_var  = tk.StringVar(value="8")
        self.start_var  = tk.StringVar(value="9")

        label(1, "💰 Budget (NPR):")
        entry(1, "1500", self.budget_var)

        label(2, "⏱️  Hours Available:")
        entry(2, "8", self.hours_var)

        label(3, "🕘 Start Hour (24h):")
        entry(3, "9", self.start_var)

        # Interest checkboxes
        tk.Label(frame, text="🎯 Interests:",
                font=("Consolas", 10),
                bg=COLORS["card"], fg=COLORS["text"]).grid(row=4, column=0, sticky="nw", pady=(8, 0))

        tag_frame = tk.Frame(frame, bg=COLORS["card"])
        tag_frame.grid(row=4, column=1, sticky="w", pady=(8, 0))

        self.tag_vars = {}
        for i, tag in enumerate(ALL_TAGS):
            var = tk.BooleanVar(value=tag in ["culture", "nature"])
            self.tag_vars[tag] = var
            cb = tk.Checkbutton(tag_frame, text=tag, variable=var,
                                font=("Consolas", 9),
                                bg=COLORS["card"], fg=COLORS["text"],
                                selectcolor=COLORS["border"],
                                activebackground=COLORS["card"],
                                activeforeground=COLORS["accent"])
            cb.grid(row=i // 2, column=i % 2, sticky="w")

        # Buttons
        btn_frame = tk.Frame(frame, bg=COLORS["card"])
        btn_frame.grid(row=6, column=0, columnspan=2, pady=(12, 0))

        tk.Button(btn_frame, text="🔍  Plan My Trip!",
                font=("Consolas", 11, "bold"),
                bg=COLORS["accent"], fg=COLORS["bg"],
                relief="flat", padx=16, pady=6,
                cursor="hand2",
                command=self._run).pack(side="left", padx=(0, 8))

        tk.Button(btn_frame, text="🔄 Reset",
                font=("Consolas", 10),
                bg=COLORS["border"], fg=COLORS["sub"],
                relief="flat", padx=12, pady=6,
                cursor="hand2",
                command=self._reset).pack(side="left")

    # ── KPI Row ─────────────────────────────
    def _build_kpi_row(self, parent):
        self.kpi_frame = tk.Frame(parent, bg=COLORS["bg"])
        self.kpi_frame.pack(fill="x", pady=(0, 8))

        cards = [
            ("kpi_spots",  "📍 Spots",      "—", COLORS["accent"]),
            ("kpi_cost",   "💰 Cost (NPR)", "—", COLORS["yellow"]),
            ("kpi_time",   "⏱️ Hours Used",  "—", COLORS["green"]),
            ("kpi_match",  "🎯 Interest",   "—", COLORS["purple"]),
        ]
        self.kpis = {}
        for i, (key, title, default, color) in enumerate(cards):
            card = tk.Frame(self.kpi_frame, bg=COLORS["card"], padx=8, pady=7)
            card.grid(row=0, column=i, padx=3, sticky="nsew")
            self.kpi_frame.columnconfigure(i, weight=1)
            tk.Label(card, text=title, font=("Consolas", 7),
                    bg=COLORS["card"], fg=COLORS["sub"]).pack(anchor="w")
            lbl = tk.Label(card, text=default, font=("Consolas", 14, "bold"),
                        bg=COLORS["card"], fg=color)
            lbl.pack(anchor="w")
            self.kpis[key] = lbl

    # ── Results (table + log) ────────────────
    def _build_results_panel(self, parent):
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True)

        # Tab 1 — Greedy
        tab1 = tk.Frame(nb, bg=COLORS["card"])
        nb.add(tab1, text=" 🤖 Greedy Result ")
        self._build_itinerary_tree(tab1, "greedy")

        # Tab 2 — Brute Force
        tab2 = tk.Frame(nb, bg=COLORS["card"])
        nb.add(tab2, text=" 🔢 Brute Force ")
        self._build_itinerary_tree(tab2, "brute")

        # Tab 3 — Comparison
        tab3 = tk.Frame(nb, bg=COLORS["card"])
        nb.add(tab3, text=" 📊 Comparison ")
        self._build_comparison_tab(tab3)

        # Tab 4 — Reason log
        tab4 = tk.Frame(nb, bg=COLORS["card"])
        nb.add(tab4, text=" 📝 Why Selected ")
        self.reason_text = tk.Text(tab4, bg=COLORS["panel"], fg=COLORS["text"],
                                font=("Consolas", 9), relief="flat",
                                wrap="word", state="disabled")
        self.reason_text.pack(fill="both", expand=True, padx=4, pady=4)

    def _build_itinerary_tree(self, parent, tag):
        cols = ("#", "Spot", "Fee", "Duration", "Tags", "Open")
        tree = ttk.Treeview(parent, columns=cols, show="headings",
                            style="Tour.Treeview")
        widths = [25, 160, 55, 65, 120, 70]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center")
        tree.column("Spot", anchor="w")

        tree.tag_configure("alt", background=COLORS["panel"])
        tree.tag_configure("normal", background=COLORS["card"])

        sb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True, padx=(4, 0), pady=4)
        sb.pack(side="right", fill="y", pady=4)

        if tag == "greedy":
            self.greedy_tree = tree
        else:
            self.brute_tree = tree

    def _build_comparison_tab(self, parent):
        self.cmp_text = tk.Text(parent, bg=COLORS["panel"], fg=COLORS["text"],
                                font=("Consolas", 10), relief="flat",
                                wrap="word", state="disabled")
        self.cmp_text.pack(fill="both", expand=True, padx=4, pady=4)

        self.cmp_text.tag_configure("heading", foreground=COLORS["accent"],
                                    font=("Consolas", 11, "bold"))
        self.cmp_text.tag_configure("good",    foreground=COLORS["green"])
        self.cmp_text.tag_configure("warn",    foreground=COLORS["yellow"])
        self.cmp_text.tag_configure("sub",     foreground=COLORS["sub"])

    # ── Right: Map + Chart ───────────────────
    def _build_right_panel(self, parent):
        tk.Label(parent, text="VISUAL ANALYTICS",
                font=("Consolas", 8, "bold"),
                bg=COLORS["bg"], fg=COLORS["sub"]).pack(anchor="w", padx=4)

        self.fig, self.axes = plt.subplots(1, 2, figsize=(7.5, 4.5))
        self.fig.patch.set_facecolor(COLORS["bg"])
        for ax in self.axes:
            ax.set_facecolor(COLORS["panel"])
            ax.tick_params(colors=COLORS["sub"], labelsize=7)
            for spine in ax.spines.values():
                spine.set_edgecolor(COLORS["border"])

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)

        # Bottom status bar
        self.status_var = tk.StringVar(value="Ready — set your preferences and click Plan My Trip!")
        tk.Label(parent, textvariable=self.status_var,
                font=("Consolas", 9), bg=COLORS["panel"],
                fg=COLORS["sub"], anchor="w", pady=4).pack(fill="x", padx=4)

    # ── Run Logic ───────────────────────────
    def _run(self):
        try:
            budget     = int(self.budget_var.get())
            hours      = float(self.hours_var.get())
            start_hour = int(self.start_var.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for Budget, Hours, and Start Hour.")
            return

        interests = [tag for tag, var in self.tag_vars.items() if var.get()]
        if not interests:
            messagebox.showwarning("No Interests", "Please select at least one interest tag.")
            return

        self.status_var.set("⏳ Running greedy algorithm...")
        self.root.update()

        greedy_spots, reasons = greedy_itinerary(budget, hours, interests, start_hour)

        self.status_var.set("⏳ Running brute force (first 6 spots)...")
        self.root.update()

        brute_spots = brute_force_itinerary(budget, hours, interests, start_hour)

        self._populate_tree(self.greedy_tree, greedy_spots, start_hour)
        self._populate_tree(self.brute_tree,  brute_spots,  start_hour)
        self._update_kpis(greedy_spots, interests, start_hour)
        self._update_reasons(reasons, greedy_spots)
        self._update_comparison(greedy_spots, brute_spots, interests)
        self._draw_charts(greedy_spots, brute_spots)

        self.status_var.set(
            f"✅ Done! Greedy found {len(greedy_spots)} spots | "
            f"Brute force found {len(brute_spots)} spots (from first 6)"
        )

    def _populate_tree(self, tree, spots, start_hour):
        for row in tree.get_children():
            tree.delete(row)
        hour = start_hour
        for i, s in enumerate(spots):
            tag = "alt" if i % 2 else "normal"
            tree.insert("", "end", values=(
                i + 1,
                s["name"],
                f"Rs.{s['fee']}",
                f"{s['duration']}h",
                ", ".join(s["tags"]),
                f"{int(hour):02d}:00"
            ), tags=(tag,))
            hour += s["duration"] + 0.3

    def _update_kpis(self, spots, interests, start_hour):
        total_cost  = sum(s["fee"] for s in spots)
        total_time  = sum(s["duration"] + 0.3 for s in spots)
        total_match = sum(len(set(s["tags"]) & set(interests)) for s in spots)

        self.kpis["kpi_spots"].config(text=str(len(spots)))
        self.kpis["kpi_cost"].config(text=f"{total_cost:,}")
        self.kpis["kpi_time"].config(text=f"{total_time:.1f}h")
        self.kpis["kpi_match"].config(text=f"{total_match} tags")

    def _update_reasons(self, reasons, spots):
        self.reason_text.config(state="normal")
        self.reason_text.delete(1.0, "end")
        self.reason_text.insert("end", "WHY EACH SPOT WAS SELECTED (Greedy Logic)\n\n",)
        for i, (spot, reason) in enumerate(zip(spots, reasons)):
            self.reason_text.insert("end", f"  {i+1}. {spot['name']}\n")
            self.reason_text.insert("end", f"     → {reason}\n\n")
        self.reason_text.config(state="disabled")

    def _update_comparison(self, greedy, brute, interests):
        self.cmp_text.config(state="normal")
        self.cmp_text.delete(1.0, "end")

        def write(text, tag=None):
            self.cmp_text.insert("end", text, tag)

        write("GREEDY vs BRUTE FORCE COMPARISON\n\n", "heading")

        g_cost  = sum(s["fee"] for s in greedy)
        b_cost  = sum(s["fee"] for s in brute)
        g_time  = sum(s["duration"] + 0.3 for s in greedy)
        b_time  = sum(s["duration"] + 0.3 for s in brute)
        g_match = sum(len(set(s["tags"]) & set(interests)) for s in greedy)
        b_match = sum(len(set(s["tags"]) & set(interests)) for s in brute)

        rows = [
            ("Metric",         "Greedy",           "Brute Force (6 spots)"),
            ("Spots Visited",  str(len(greedy)),    str(len(brute))),
            ("Total Cost",     f"Rs. {g_cost}",     f"Rs. {b_cost}"),
            ("Time Used",      f"{g_time:.1f} hrs", f"{b_time:.1f} hrs"),
            ("Interest Match", f"{g_match} tags",   f"{b_match} tags"),
        ]

        for i, row in enumerate(rows):
            if i == 0:
                write(f"  {'Metric':<18} {'Greedy':<20} {'Brute Force'}\n", "heading")
                write("  " + "─" * 55 + "\n", "sub")
            else:
                line = f"  {row[0]:<18} {row[1]:<20} {row[2]}\n"
                write(line, "good" if i % 2 else None)

        write("\n\n📌 ANALYSIS\n\n", "heading")
        write("  Greedy Algorithm:\n", "good")
        write("  • Fast: O(n²) — works for large datasets\n")
        write("  • Makes locally optimal choices at each step\n")
        write("  • May miss the globally optimal combination\n\n")

        write("  Brute Force:\n", "warn")
        write("  • Guaranteed optimal — checks ALL combinations\n")
        write("  • Slow: O(n!) — only feasible for ≤6 spots\n")
        write("  • For n=8 spots: 40,320 permutations checked!\n\n")

        write("  Trade-off:\n", "sub")
        write("  Greedy is ~99% as good in practice but runs\n")
        write("  in milliseconds vs seconds for brute force.\n")

        self.cmp_text.config(state="disabled")

    # ── Charts ──────────────────────────────
    def _draw_charts(self, greedy, brute):
        for ax in self.axes:
            ax.clear()
            ax.set_facecolor(COLORS["panel"])
            ax.tick_params(colors=COLORS["sub"], labelsize=8)
            for spine in ax.spines.values():
                spine.set_edgecolor(COLORS["border"])

        # Chart 1: Route map (coordinate plot)
        ax1 = self.axes[0]
        if greedy:
            lats = [s["lat"] for s in greedy]
            lons = [s["lon"] for s in greedy]
            ax1.plot(lons, lats, "-o", color=COLORS["accent"],
                    linewidth=1.5, markersize=7, zorder=3)
            for i, s in enumerate(greedy):
                ax1.annotate(f"{i+1}. {s['name'].split()[0]}",
                            (s["lon"], s["lat"]),
                            textcoords="offset points", xytext=(5, 5),
                            fontsize=6.5, color=COLORS["text"],
                            bbox=dict(boxstyle="round,pad=0.2",
                                    fc=COLORS["card"], ec=COLORS["border"], alpha=0.8))
            ax1.plot(lons[0],  lats[0],  "o", color=COLORS["green"],  markersize=10, zorder=4, label="Start")
            ax1.plot(lons[-1], lats[-1], "o", color=COLORS["red"],    markersize=10, zorder=4, label="End")

        # Also plot all available spots faintly
        for s in SPOTS:
            if s not in greedy:
                ax1.plot(s["lon"], s["lat"], "o", color=COLORS["border"],
                        markersize=5, zorder=2, alpha=0.5)

        ax1.set_title("Greedy Route Map", color=COLORS["accent"], fontsize=9, pad=6)
        ax1.set_xlabel("Longitude", color=COLORS["sub"], fontsize=7)
        ax1.set_ylabel("Latitude",  color=COLORS["sub"], fontsize=7)
        ax1.legend(fontsize=7, facecolor=COLORS["card"],
                edgecolor=COLORS["border"], labelcolor=COLORS["text"])

        # Chart 2: Greedy vs Brute comparison bars
        ax2 = self.axes[1]
        metrics      = ["Spots\nVisited", "Total\nCost (÷100)", "Time\nUsed (hrs)"]
        g_vals = [
            len(greedy),
            sum(s["fee"] for s in greedy) / 100,
            sum(s["duration"] + 0.3 for s in greedy),
        ]
        b_vals = [
            len(brute),
            sum(s["fee"] for s in brute) / 100,
            sum(s["duration"] + 0.3 for s in brute),
        ]

        x = range(len(metrics))
        w = 0.35
        bars1 = ax2.bar([i - w/2 for i in x], g_vals, w,
                        label="Greedy",      color=COLORS["accent"], alpha=0.85)
        bars2 = ax2.bar([i + w/2 for i in x], b_vals, w,
                        label="Brute Force", color=COLORS["yellow"], alpha=0.85)

        for bar in bars1:
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    f"{bar.get_height():.1f}", ha="center", va="bottom",
                    color=COLORS["text"], fontsize=7)
        for bar in bars2:
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    f"{bar.get_height():.1f}", ha="center", va="bottom",
                    color=COLORS["text"], fontsize=7)

        ax2.set_xticks(list(x))
        ax2.set_xticklabels(metrics, fontsize=8)
        ax2.set_title("Greedy vs Brute Force", color=COLORS["accent"], fontsize=9, pad=6)
        ax2.legend(fontsize=7, facecolor=COLORS["card"],
                edgecolor=COLORS["border"], labelcolor=COLORS["text"])

        self.fig.tight_layout(pad=1.5)
        self.canvas.draw()

    # ── Reset ────────────────────────────────
    def _reset(self):
        self.budget_var.set("1500")
        self.hours_var.set("8")
        self.start_var.set("9")
        for tag, var in self.tag_vars.items():
            var.set(tag in ["culture", "nature"])
        for tree in [self.greedy_tree, self.brute_tree]:
            for row in tree.get_children():
                tree.delete(row)
        for lbl in self.kpis.values():
            lbl.config(text="—")
        self.status_var.set("Ready — set your preferences and click Plan My Trip!")
        for ax in self.axes:
            ax.clear()
            ax.set_facecolor(COLORS["panel"])
        self.canvas.draw()


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = TouristApp(root)
    root.mainloop()