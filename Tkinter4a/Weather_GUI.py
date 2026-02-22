"""
Question 5(b) - Multi-threaded Weather Data Collector
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#  CITIES

CITIES = [
    {"name": "Kathmandu",  "lat": 27.7172, "lon": 85.3240},
    {"name": "Biratnagar", "lat": 26.4525, "lon": 87.2718},
    {"name": "Pokhara",    "lat": 28.2096, "lon": 83.9856},
    {"name": "Nepalgunj",  "lat": 28.0500, "lon": 81.6167},
    {"name": "Dhangadhi",  "lat": 28.6833, "lon": 80.5833},
]

WMO_CODES = {
    0: "Clear sky",      1: "Mainly clear",  2: "Partly cloudy",  3: "Overcast",
    45: "Foggy",         48: "Icy fog",       51: "Light drizzle", 53: "Drizzle",
    55: "Heavy drizzle", 61: "Slight rain",   63: "Rain",          65: "Heavy rain",
    71: "Slight snow",   73: "Snow",          75: "Heavy snow",
    80: "Showers",       81: "Showers",       82: "Heavy showers",
    95: "Thunderstorm",  96: "T-storm+hail",  99: "Heavy t-storm",
}

#  FETCH FUNCTIONS

def fetch_one(city, results, lock, index):
    """Fetch one city from Open-Meteo (free, no API key)."""
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={city['lat']}&longitude={city['lon']}"
        "&current=temperature_2m,relative_humidity_2m,"
        "weather_code,wind_speed_10m,surface_pressure"
        "&wind_speed_unit=ms"
    )
    start = time.time()
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        d    = resp.json()["current"]
        code = d.get("weather_code", 0)
        row  = {
            "city":     city["name"],
            "temp":     f"{d['temperature_2m']:.1f}",
            "humidity": str(d["relative_humidity_2m"]),
            "pressure": f"{d['surface_pressure']:.0f}",
            "weather":  WMO_CODES.get(code, f"Code {code}"),
            "wind":     str(d["wind_speed_10m"]),
            "time":     time.strftime("%H:%M:%S"),
            "ok":       True,
            "latency":  round(time.time() - start, 3),
        }
    except Exception:
        row = {
            "city":     city["name"],
            "temp":     "N/A", "humidity": "N/A",
            "pressure": "N/A", "weather":  "Error",
            "wind":     "N/A", "time":     time.strftime("%H:%M:%S"),
            "ok":       False, "latency":  round(time.time() - start, 3),
        }
    with lock:
        results[index] = row


#  GUI APPLICATION

class WeatherApp:
    def __init__(self, root):
        self.root      = root
        self.root.title("Multi-threaded Weather Data Collector")
        self.root.geometry("1100x680")
        self.root.configure(bg="#B0B0B0")
        self.root.resizable(True, True)

        self._par_time        = None
        self._seq_time        = None
        self._fetching        = False
        self._chart_widget    = None
        self._chart_fig       = None

        self._setup_styles()
        self._build_ui()

    # ── Styles ──────────────────────────────
    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("W.Treeview",
                    background="#D3D3D3",
                    foreground="#212121",
                    fieldbackground="#D3D3D3",
                    rowheight=26,
                    font=("Arial", 10))
        s.configure("W.Treeview.Heading",
                    background="#A0A0A0",
                    foreground="#111111",
                    font=("Arial", 10, "bold"),
                    relief="flat")
        s.map("W.Treeview",
              background=[("selected", "#888888")],
              foreground=[("selected", "white")])

    # ── Build UI ────────────────────────────
    def _build_ui(self):
        self._build_titlebar()
        self._build_control_panel()
        self._build_status_bar()
        self._build_main_area()
        self._build_footer()

    def _build_titlebar(self):
        bar = tk.Frame(self.root, bg="#1565C0", pady=12)
        bar.pack(fill="x")

        tk.Label(bar, text="  ☁",
                 font=("Arial", 20), bg="#1565C0",
                 fg="white").pack(side="left", padx=(12, 4))
        tk.Label(bar,
                 text="Multi-threaded Weather Data Collector",
                 font=("Arial", 16, "bold"),
                 bg="#1565C0", fg="white").pack(side="left")
        tk.Label(bar,
                 text="   Real-time weather data from 5 Nepalese cities using parallel processing",
                 font=("Arial", 9), bg="#1565C0",
                 fg="#90CAF9").pack(side="left")

    def _build_control_panel(self):
        outer = tk.LabelFrame(self.root, text=" Control Panel",
                               font=("Arial", 9, "bold"),
                               bg="#B0B0B0", fg="#222",
                               padx=10, pady=8)
        outer.pack(fill="x", padx=10, pady=(8, 4))

        row = tk.Frame(outer, bg="#B0B0B0")
        row.pack(anchor="w")

        self._make_btn(row, " Fetch Weather (Parallel/Multithreaded)",
                       "#4CAF50", self._on_parallel).pack(side="left", padx=(0, 8))
        self._make_btn(row, "  Fetch Weather (Sequential/Single-threaded)",
                       "#FF9800", self._on_sequential).pack(side="left", padx=(0, 8))
        self._make_btn(row, "  Show Performance Comparison",
                       "#9C27B0", self._on_show_chart).pack(side="left", padx=(0, 8))
        self._make_btn(row, "  Clear",
                       "#F44336", self._on_clear).pack(side="left")

    def _make_btn(self, parent, text, bg, cmd):
        return tk.Button(parent, text=text,
                         font=("Arial", 10, "bold"),
                         bg=bg, fg="white",
                         relief="flat", padx=14, pady=7,
                         cursor="hand2", command=cmd,
                         activebackground=bg,
                         activeforeground="white")

    def _build_status_bar(self):
        self._status_frame = tk.Frame(self.root, bg="#C8E6C9",
                                      relief="solid", bd=1)
        self._status_frame.pack(fill="x", padx=10, pady=(0, 6))
        self._status_var = tk.StringVar(value="")
        self._status_lbl = tk.Label(self._status_frame,
                                    textvariable=self._status_var,
                                    font=("Arial", 9, "bold"),
                                    bg="#C8E6C9", fg="#1B5E20",
                                    anchor="w", pady=5, padx=10)
        self._status_lbl.pack(fill="x")

    def _set_status(self, msg, bg="#C8E6C9", fg="#1B5E20"):
        self._status_var.set(f"  ✔  {msg}")
        self._status_frame.config(bg=bg)
        self._status_lbl.config(bg=bg, fg=fg)

    def _build_main_area(self):
        main = tk.Frame(self.root, bg="#B0B0B0")
        main.pack(fill="both", expand=True, padx=10, pady=4)

        # ── Left: weather table ──
        tbl_lf = tk.LabelFrame(main, text=" Weather Data Table",
                                font=("Arial", 9, "bold"),
                                bg="#B0B0B0", fg="#222")
        tbl_lf.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self._build_table(tbl_lf)

        # ── Right: chart + stats ──
        right = tk.Frame(main, bg="#B0B0B0", width=390)
        right.pack(side="left", fill="y")
        right.pack_propagate(False)

        self._chart_lf = tk.LabelFrame(right, text=" Performance Comparison",
                                        font=("Arial", 9, "bold"),
                                        bg="#B0B0B0", fg="#222")
        self._chart_lf.pack(fill="both", expand=True, pady=(0, 6))

        self._chart_ph = tk.Label(self._chart_lf,
                                   text="Click 'Show Performance Comparison'\nafter fetching data",
                                   font=("Arial", 9), bg="#B0B0B0",
                                   fg="#555555", justify="center")
        self._chart_ph.pack(expand=True)

        # Stats box
        stats_lf = tk.LabelFrame(right, text=" Statistics",
                                   font=("Arial", 9, "bold"),
                                   bg="#B0B0B0", fg="#222")
        stats_lf.pack(fill="x")

        self._stats = tk.Text(stats_lf, height=7,
                               bg="#0D1117", fg="#39FF14",
                               font=("Consolas", 9),
                               relief="flat", state="disabled",
                               padx=6, pady=4)
        self._stats.pack(fill="x", padx=6, pady=6)
        self._stats.tag_configure("head",  foreground="#00BCD4", font=("Consolas", 9, "bold"))
        self._stats.tag_configure("key",   foreground="#FFD54F")
        self._stats.tag_configure("val",   foreground="#69F0AE")
        self._stats.tag_configure("speed", foreground="#FF6E40")
        self._write_stats_placeholder()

    def _build_table(self, parent):
        cols = ("City", "Temperature (C)", "Humidity (%)",
                "Pressure (hPa)", "Weather", "Wind (m/s)", "Fetch Time")
        self._tree = ttk.Treeview(parent, columns=cols,
                                   show="headings", style="W.Treeview",
                                   height=11)
        widths = [110, 120, 95, 105, 140, 80, 80]
        for col, w in zip(cols, widths):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, anchor="center", minwidth=50)
        self._tree.column("City",    anchor="w")
        self._tree.column("Weather", anchor="w")

        self._tree.tag_configure("odd",  background="#C8C8C8")
        self._tree.tag_configure("even", background="#D3D3D3")
        self._tree.tag_configure("err",  background="#FFEBEE", foreground="#C62828")

        vsb = ttk.Scrollbar(parent, orient="vertical",   command=self._tree.yview)
        hsb = ttk.Scrollbar(parent, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self._tree.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        vsb.pack(side="right",  fill="y",  pady=6)
        hsb.pack(side="bottom", fill="x",  padx=6)

    def _build_footer(self):
        ft = tk.Frame(self.root, bg="#999999", pady=5)
        ft.pack(fill="x", side="bottom")
        tk.Label(ft,
                 text=" Parallel fetching uses 5 threads to fetch all cities simultaneously  "
                      "|  Sequential fetching processes one city at a time",
                 font=("Arial", 8), bg="#999999", fg="#222222").pack()

    # ── Populate table ───────────────────────
    def _fill_table(self, results):
        for r in self._tree.get_children():
            self._tree.delete(r)
        for i, row in enumerate(results):
            if row is None:
                continue
            tag = "err" if not row["ok"] else ("odd" if i % 2 else "even")
            self._tree.insert("", "end", values=(
                row["city"], row["temp"], row["humidity"],
                row["pressure"], row["weather"],
                row["wind"], row["time"]
            ), tags=(tag,))

    # ── Stats box ───────────────────────────
    def _write_stats_placeholder(self):
        self._stats.config(state="normal")
        self._stats.delete(1.0, "end")
        self._stats.insert("end", "==== PERFORMANCE ====\n\n", "head")
        self._stats.insert("end", "  Fetch data first to see results\n", "key")
        self._stats.config(state="disabled")

    def _write_stats(self):
        self._stats.config(state="normal")
        self._stats.delete(1.0, "end")
        self._stats.insert("end", "==== PERFORMANCE ====\n\n", "head")
        if self._par_time is not None:
            self._stats.insert("end", "   Parallel:    ", "key")
            self._stats.insert("end", f"{self._par_time}s\n", "val")
        if self._seq_time is not None:
            self._stats.insert("end", "  ➡ Sequential:  ", "key")
            self._stats.insert("end", f"{self._seq_time}s\n", "val")
        if self._par_time and self._seq_time and self._par_time > 0:
            speedup = round(self._seq_time / self._par_time, 1)
            saved   = round(self._seq_time - self._par_time, 2)
            pct     = round((1 - self._par_time / self._seq_time) * 100, 1)
            self._stats.insert("end", f"\n   Speedup:     ", "key")
            self._stats.insert("end", f"{speedup}x\n", "speed")
            self._stats.insert("end", f"   Improvement: ", "key")
            self._stats.insert("end", f"{pct}%\n", "speed")
            self._stats.insert("end", f"  Time Saved:  ", "key")
            self._stats.insert("end", f"{saved}s\n", "speed")
        self._stats.config(state="disabled")

    # ── Chart ───────────────────────────────
    def _draw_chart(self):
        if self._par_time is None and self._seq_time is None:
            return

        # Remove old chart
        if self._chart_ph:
            self._chart_ph.pack_forget()
            self._chart_ph = None
        if self._chart_widget:
            self._chart_widget.get_tk_widget().destroy()
            self._chart_widget = None
        if self._chart_fig:
            plt.close(self._chart_fig)

        fig, ax = plt.subplots(figsize=(3.5, 3.0))
        fig.patch.set_facecolor("#B0B0B0")
        ax.set_facecolor("#D3D3D3")

        labels, values, bar_colors = [], [], []
        if self._par_time is not None:
            labels.append("Parallel\n(Multithreaded)")
            values.append(self._par_time)
            bar_colors.append("#4CAF50")
        if self._seq_time is not None:
            labels.append("Sequential\n(Single-threaded)")
            values.append(self._seq_time)
            bar_colors.append("#FF9800")

        bars = ax.bar(labels, values, color=bar_colors,
                      width=0.45, edgecolor="#E0E0E0", linewidth=0.8)

        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(values) * 0.02,
                    f"{val}s",
                    ha="center", va="bottom",
                    fontsize=11, fontweight="bold", color="#333")

        if self._par_time and self._seq_time and self._par_time > 0:
            speedup = round(self._seq_time / self._par_time, 1)
            ax.annotate(f"★ Speedup: {speedup}x faster",
                        xy=(0.5, max(values) * 0.82),
                        xycoords=("axes fraction", "data"),
                        ha="center", fontsize=9, fontweight="bold",
                        color="#D32F2F",
                        bbox=dict(boxstyle="round,pad=0.35",
                                  fc="#FFF9C4", ec="#F44336", alpha=0.95))

        ax.set_title("Fetch Time Comparison",
                     fontsize=11, fontweight="bold",
                     color="#1565C0", pad=8)
        ax.set_ylabel("Time (seconds)", fontsize=9, color="#555")
        ax.tick_params(colors="#555", labelsize=9)
        for sp in ["top", "right"]:
            ax.spines[sp].set_visible(False)
        for sp in ["left", "bottom"]:
            ax.spines[sp].set_edgecolor("#CCCCCC")
        ax.set_ylim(0, max(values) * 1.35)
        fig.tight_layout(pad=1.2)

        self._chart_fig    = fig
        self._chart_widget = FigureCanvasTkAgg(fig, master=self._chart_lf)
        self._chart_widget.draw()
        self._chart_widget.get_tk_widget().pack(fill="both", expand=True,
                                                 padx=4, pady=4)

    # ── Button handlers ──────────────────────
    def _on_parallel(self):
        if self._fetching:
            return
        self._fetching = True
        self._set_status("Fetching in parallel... please wait",
                         bg="#E3F2FD", fg="#1565C0")
        threading.Thread(target=self._run_parallel, daemon=True).start()

    def _run_parallel(self):
        results = [None] * len(CITIES)
        lock    = threading.Lock()
        threads = []
        t0 = time.time()
        for i, city in enumerate(CITIES):
            t = threading.Thread(target=fetch_one,
                                  args=(city, results, lock, i))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        elapsed = round(time.time() - t0, 2)
        self._par_time = elapsed
        self.root.after(0, self._done_parallel, results, elapsed)

    def _done_parallel(self, results, elapsed):
        self._fill_table(results)
        self._set_status(f"PARALLEL fetch completed in {elapsed} seconds",
                         bg="#C8E6C9", fg="#1B5E20")
        self._write_stats()
        self._fetching = False

    def _on_sequential(self):
        if self._fetching:
            return
        self._fetching = True
        self._set_status("Fetching sequentially... please wait",
                         bg="#FFF3E0", fg="#E65100")
        threading.Thread(target=self._run_sequential, daemon=True).start()

    def _run_sequential(self):
        results = [None] * len(CITIES)
        lock    = threading.Lock()
        t0 = time.time()
        for i, city in enumerate(CITIES):
            fetch_one(city, results, lock, i)
        elapsed = round(time.time() - t0, 2)
        self._seq_time = elapsed
        self.root.after(0, self._done_sequential, results, elapsed)

    def _done_sequential(self, results, elapsed):
        self._fill_table(results)
        self._set_status(f"SEQUENTIAL fetch completed in {elapsed} seconds",
                         bg="#FFF3E0", fg="#E65100")
        self._write_stats()
        self._fetching = False

    def _on_show_chart(self):
        self._draw_chart()

    def _on_clear(self):
        for r in self._tree.get_children():
            self._tree.delete(r)
        self._par_time = None
        self._seq_time = None
        self._status_var.set("")
        self._status_frame.config(bg="#B0B0B0")
        self._status_lbl.config(bg="#B0B0B0")
        self._write_stats_placeholder()
        if self._chart_widget:
            self._chart_widget.get_tk_widget().destroy()
            self._chart_widget = None
        if self._chart_fig:
            plt.close(self._chart_fig)
            self._chart_fig = None
        self._chart_ph = tk.Label(self._chart_lf,
                                   text="Click 'Show Performance Comparison'\nafter fetching data",
                                   font=("Arial", 9), bg="#B0B0B0",
                                   fg="#555555", justify="center")
        self._chart_ph.pack(expand=True)


#  ENTRY POINT

if __name__ == "__main__":
    root = tk.Tk()
    app  = WeatherApp(root)
    root.mainloop()