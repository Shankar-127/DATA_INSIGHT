"""
DATA INSIGHT — Interactive Data Analysis & Visualization System
A local, offline-capable Tkinter application for exploring tabular datasets.
"""
from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, colorchooser

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

APP_NAME = "DATA INSIGHT"
BASE_DIR = Path(__file__).resolve().parent
EXPORT_DIR = BASE_DIR / "exports"
EXPORT_DIR.mkdir(exist_ok=True)

BG = "#F3F6FB"
PANEL = "#FFFFFF"
SIDEBAR = "#17243A"
ACCENT = "#356AE6"
TEXT = "#17243A"
MUTED = "#68758A"
SUCCESS = "#16845B"
DANGER = "#C43D4B"
FONT = ("Segoe UI", 10)
TITLE_FONT = ("Segoe UI", 20, "bold")


def make_sample_dataset(rows: int = 350, seed: int = 42) -> pd.DataFrame:
    """Create deterministic synthetic sales records with intentional missing values."""
    rng = np.random.default_rng(seed)
    products = np.array(["Laptop", "Phone", "Tablet", "Monitor", "Headphones", "Keyboard"])
    categories = {"Laptop": "Computers", "Phone": "Mobiles", "Tablet": "Mobiles",
                  "Monitor": "Accessories", "Headphones": "Accessories", "Keyboard": "Accessories"}
    regions = np.array(["North", "South", "East", "West", "Central"])
    prices = {"Laptop": 720, "Phone": 430, "Tablet": 310, "Monitor": 210,
              "Headphones": 85, "Keyboard": 45}
    product = rng.choice(products, rows)
    quantity = rng.integers(1, 9, rows).astype(float)
    discount = rng.choice([0, .05, .10, .15, .20], rows, p=[.25, .2, .25, .2, .1])
    gross = np.array([prices[p] for p in product]) * quantity
    sales = gross * (1 - discount) * rng.uniform(.94, 1.06, rows)
    cost_ratio = rng.uniform(.58, .83, rows)
    profit = sales * (1 - cost_ratio) - gross * .025
    dates = pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, rows), unit="D")
    df = pd.DataFrame({
        "Order_ID": [f"ORD-{i+1:04d}" for i in range(rows)],
        "Date": dates.strftime("%Y-%m-%d"),
        "Product": product,
        "Category": [categories[p] for p in product],
        "Region": rng.choice(regions, rows),
        "Quantity": quantity.astype(int),
        "Discount": discount,
        "Sales": np.round(sales, 2),
        "Profit": np.round(profit, 2),
        "Customer_Age": rng.integers(18, 71, rows).astype(float),
    })
    for col, count in [("Discount", 8), ("Customer_Age", 10), ("Region", 5), ("Profit", 4)]:
        indices = rng.choice(rows, count, replace=False)
        df.loc[indices, col] = np.nan
    return df


class DataInsightApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DATA INSIGHT — Interactive Data Analysis & Visualization System")
        self.geometry("1440x900")
        self.minsize(1080, 700)
        self.configure(bg=BG)
        self.original_df: Optional[pd.DataFrame] = None
        self.df: Optional[pd.DataFrame] = None
        self.dataset_name = "No dataset loaded"
        self.current_figure = None
        self.canvas = None
        self.toolbar = None
        self.chart_color = "#356AE6"
        self._configure_style()
        self._build_shell()
        self.show_page("Home")

    def _configure_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", font=FONT)
        style.configure("Treeview", rowheight=27, background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#E8EEF8")
        style.configure("TButton", padding=(10, 7))
        style.configure("Accent.TButton", background=ACCENT, foreground="white", padding=(12, 8))
        style.map("Accent.TButton", background=[("active", "#2455C7")])
        style.configure("TNotebook.Tab", padding=(12, 7))

    def _build_shell(self):
        self.sidebar = tk.Frame(self, bg=SIDEBAR, width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text="DATA\nINSIGHT", bg=SIDEBAR, fg="white",
                 font=("Segoe UI", 21, "bold"), justify="left").pack(anchor="w", padx=24, pady=(28, 4))
        tk.Label(self.sidebar, text="DATA ANALYSIS STUDIO", bg=SIDEBAR, fg="#AAB9D2",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=25, pady=(0, 24))
        self.nav_buttons = {}
        nav = ["Home", "Upload Dataset", "Data Overview", "Data Cleaning", "Data Analysis",
               "Visualization Studio", "Insights", "Export Results", "About Project"]
        for item in nav:
            b = tk.Button(self.sidebar, text="  " + item, anchor="w", relief="flat",
                          bg=SIDEBAR, fg="#D9E2F1", activebackground="#263B5B",
                          activeforeground="white", font=("Segoe UI", 10),
                          padx=18, pady=10, command=lambda p=item: self.show_page(p))
            b.pack(fill="x", padx=9, pady=1)
            self.nav_buttons[item] = b
        tk.Button(self.sidebar, text="  Exit Application", anchor="w", relief="flat",
                  bg=SIDEBAR, fg="#F2A7AC", activebackground="#263B5B",
                  font=("Segoe UI", 10), padx=18, pady=10,
                  command=self.on_exit).pack(side="bottom", fill="x", padx=9, pady=18)

        self.main = tk.Frame(self, bg=BG)
        self.main.pack(side="right", fill="both", expand=True)
        header = tk.Frame(self.main, bg="white", height=66)
        header.pack(fill="x")
        header.pack_propagate(False)
        self.header_title = tk.Label(header, text="Home", bg="white", fg=TEXT,
                                     font=("Segoe UI", 15, "bold"))
        self.header_title.pack(side="left", padx=28)
        self.status_label = tk.Label(header, text="●  No dataset loaded", bg="white",
                                     fg=MUTED, font=("Segoe UI", 9))
        self.status_label.pack(side="right", padx=25)
        self.content = tk.Frame(self.main, bg=BG)
        self.content.pack(fill="both", expand=True, padx=24, pady=20)

    def show_page(self, page):
        self.page_name = page
        self.header_title.config(text=page)
        for name, button in self.nav_buttons.items():
            button.config(bg="#263B5B" if name == page else SIDEBAR,
                          fg="white" if name == page else "#D9E2F1")
        for child in self.content.winfo_children():
            child.destroy()
        if page == "Home": self.page_home()
        elif page == "Upload Dataset": self.page_upload()
        elif page == "Data Overview": self.page_overview()
        elif page == "Data Cleaning": self.page_cleaning()
        elif page == "Data Analysis": self.page_analysis()
        elif page == "Visualization Studio": self.page_visualization()
        elif page == "Insights": self.page_insights()
        elif page == "Export Results": self.page_export()
        elif page == "About Project": self.page_about()

    def update_status(self):
        if self.df is None:
            self.status_label.config(text="●  No dataset loaded", fg=MUTED)
        else:
            self.status_label.config(text=f"●  {self.dataset_name}  |  {len(self.df):,} rows × {len(self.df.columns)} columns",
                                     fg=SUCCESS)

    def heading(self, parent, title, subtitle=None):
        tk.Label(parent, text=title, bg=BG, fg=TEXT, font=TITLE_FONT).pack(anchor="w")
        if subtitle:
            tk.Label(parent, text=subtitle, bg=BG, fg=MUTED, font=FONT).pack(anchor="w", pady=(4, 14))

    def card(self, parent, title, value, note=""):
        frame = tk.Frame(parent, bg=PANEL, highlightbackground="#E3E9F2", highlightthickness=1)
        tk.Label(frame, text=title.upper(), bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=16, pady=(13, 4))
        tk.Label(frame, text=str(value), bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 21, "bold")).pack(anchor="w", padx=16)
        if note:
            tk.Label(frame, text=note, bg=PANEL, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", padx=16, pady=(2, 12))
        else:
            tk.Frame(frame, bg=PANEL, height=12).pack()
        return frame

    def require_data(self):
        if self.df is None or self.df.empty:
            messagebox.showwarning("Dataset required", "Please upload a dataset or load the sample dataset first.")
            return False
        return True

    def page_home(self):
        self.heading(self.content, "Welcome to DATA INSIGHT",
                     "Explore, clean, analyze and visualize your data — all locally on your computer.")
        hero = tk.Frame(self.content, bg="#E9F0FF", padx=24, pady=22)
        hero.pack(fill="x", pady=(4, 18))
        tk.Label(hero, text="Turn raw data into clear insights.", bg="#E9F0FF", fg="#17366F",
                 font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(hero, text="Import CSV or Excel files, inspect quality, run descriptive statistics, build charts and export your work.",
                 bg="#E9F0FF", fg="#3F557A", font=FONT, wraplength=900).pack(anchor="w", pady=(7, 15))
        actions = tk.Frame(hero, bg="#E9F0FF")
        actions.pack(anchor="w")
        ttk.Button(actions, text="Upload dataset", style="Accent.TButton",
                   command=self.upload_dataset).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Try sample dataset", command=self.load_sample).pack(side="left")
        stats = tk.Frame(self.content, bg=BG)
        stats.pack(fill="x", pady=6)
        rows = len(self.df) if self.df is not None else "—"
        cols = len(self.df.columns) if self.df is not None else "—"
        missing = int(self.df.isna().sum().sum()) if self.df is not None else "—"
        for i, c in enumerate([self.card(stats, "Dataset", self.dataset_name if self.df is not None else "Not loaded"),
                               self.card(stats, "Rows", rows), self.card(stats, "Columns", cols),
                               self.card(stats, "Missing cells", missing)]):
            c.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 10, 0))
            stats.grid_columnconfigure(i, weight=1)
        tk.Label(self.content, text="WORKFLOW", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(22, 9))
        features = [
            ("01  Upload", "Load CSV, XLSX or XLS files and choose an Excel worksheet."),
            ("02  Understand", "Review data types, missing values, duplicates and a record preview."),
            ("03  Prepare", "Clean a working copy while keeping the original dataset safe."),
            ("04  Explore", "Calculate descriptive statistics, correlations and automatic insights."),
            ("05  Present", "Create charts and export datasets, summaries and visualizations.")
        ]
        for title, desc in features:
            line = tk.Frame(self.content, bg="white", padx=16, pady=11)
            line.pack(fill="x", pady=4)
            tk.Label(line, text=title, bg="white", fg=ACCENT, font=("Segoe UI", 10, "bold"), width=15, anchor="w").pack(side="left")
            tk.Label(line, text=desc, bg="white", fg=TEXT, font=FONT).pack(side="left")

    def page_upload(self):
        self.heading(self.content, "Upload a dataset", "Files are processed locally. Your uploaded source file is never edited.")
        panel = tk.Frame(self.content, bg="white", padx=24, pady=22)
        panel.pack(fill="x")
        tk.Label(panel, text="Supported formats", bg="white", fg=TEXT,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(panel, text="CSV (.csv)  •  Excel (.xlsx, .xls)", bg="white", fg=MUTED).pack(anchor="w", pady=(4, 15))
        ttk.Button(panel, text="Choose file…", style="Accent.TButton",
                   command=self.upload_dataset).pack(anchor="w")
        ttk.Button(panel, text="Load built-in sample sales dataset",
                   command=self.load_sample).pack(anchor="w", pady=9)
        self.upload_info = tk.Label(self.content, text=self._dataset_description(),
                                    bg=BG, fg=MUTED, justify="left", font=FONT)
        self.upload_info.pack(anchor="w", pady=20)

    def _dataset_description(self):
        if self.df is None: return "No dataset is currently loaded."
        return f"Loaded: {self.dataset_name}\nWorking dataset: {len(self.df):,} rows × {len(self.df.columns)} columns\nOriginal upload is preserved separately."

    def upload_dataset(self):
        path = filedialog.askopenfilename(title="Select dataset",
            filetypes=[("Supported datasets", "*.csv *.xlsx *.xls"), ("CSV files", "*.csv"),
                       ("Excel workbooks", "*.xlsx *.xls"), ("All files", "*.*")])
        if not path: return
        try:
            suffix = Path(path).suffix.lower()
            if suffix == ".csv":
                errors = []
                data = None
                for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
                    try:
                        data = pd.read_csv(path, encoding=encoding)
                        break
                    except UnicodeDecodeError as exc:
                        errors.append(str(exc))
                if data is None: raise ValueError("Could not decode this CSV file.")
            elif suffix in (".xlsx", ".xls"):
                sheets = pd.ExcelFile(path).sheet_names
                sheet = sheets[0]
                if len(sheets) > 1:
                    chosen = simpledialog.askstring("Select worksheet",
                        "Available worksheets:\n" + "\n".join(f"• {s}" for s in sheets) +
                        "\n\nEnter worksheet name:", initialvalue=sheets[0], parent=self)
                    if chosen is None: return
                    if chosen not in sheets: raise ValueError("The worksheet name was not found.")
                    sheet = chosen
                data = pd.read_excel(path, sheet_name=sheet)
            else:
                raise ValueError("Unsupported format. Choose CSV, XLSX or XLS.")
            if data.empty or len(data.columns) == 0:
                raise ValueError("The selected file contains no data.")
            self._set_dataset(data, Path(path).name)
            messagebox.showinfo("Upload complete", f"Loaded {len(data):,} rows and {len(data.columns)} columns.")
            self.show_page("Home")
        except ImportError as exc:
            messagebox.showerror("Missing dependency", f"{exc}\nInstall the dependencies in requirements.txt.")
        except Exception as exc:
            messagebox.showerror("Upload failed", str(exc))

    def _set_dataset(self, data, name):
        self.original_df = data.copy(deep=True)
        self.df = data.copy(deep=True)
        self.dataset_name = name
        self.update_status()

    def load_sample(self):
        try:
            data = make_sample_dataset()
            self._set_dataset(data, "sample_sales_dataset.csv")
            self.show_page("Home")
            messagebox.showinfo("Sample dataset", f"Loaded {len(data)} synthetic sales records.")
        except Exception as exc:
            messagebox.showerror("Sample data error", str(exc))

    def _tree(self, parent, data, max_rows=100, height=13):
        wrap = tk.Frame(parent, bg="white")
        wrap.pack(fill="both", expand=True)
        columns = [str(c) for c in data.columns]
        tree = ttk.Treeview(wrap, columns=columns, show="headings", height=height)
        vs = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        hs = ttk.Scrollbar(wrap, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vs.grid(row=0, column=1, sticky="ns")
        hs.grid(row=1, column=0, sticky="ew")
        wrap.grid_rowconfigure(0, weight=1); wrap.grid_columnconfigure(0, weight=1)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=max(110, min(190, len(col)*12)), minwidth=80, stretch=False)
        for row in data.head(max_rows).itertuples(index=False, name=None):
            values = [self._display_value(v) for v in row]
            tree.insert("", "end", values=values)
        return wrap

    @staticmethod
    def _display_value(value):
        if pd.isna(value): return "—"
        if isinstance(value, (float, np.floating)): return f"{value:.4g}"
        return str(value)

    def page_overview(self):
        self.heading(self.content, "Data overview", "A quick quality check and preview of your currently active working dataset.")
        if not self.require_data(): return
        metrics = tk.Frame(self.content, bg=BG); metrics.pack(fill="x", pady=(0, 14))
        vals = [("Rows", f"{len(self.df):,}"), ("Columns", len(self.df.columns)),
                ("Missing cells", int(self.df.isna().sum().sum())),
                ("Duplicate rows", int(self.df.duplicated().sum()))]
        for i, (t, v) in enumerate(vals):
            c = self.card(metrics, t, v)
            c.grid(row=0, column=i, sticky="nsew", padx=(0, 9)); metrics.grid_columnconfigure(i, weight=1)
        details = pd.DataFrame({"Column": self.df.columns.astype(str),
                                "Data type": [str(x) for x in self.df.dtypes],
                                "Missing": self.df.isna().sum().values,
                                "Unique": self.df.nunique(dropna=True).values})
        tk.Label(self.content, text="COLUMN DETAILS", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 7))
        self._tree(self.content, details, max_rows=100, height=6)
        tk.Label(self.content, text="DATA PREVIEW — FIRST 100 RECORDS", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(15, 7))
        self._tree(self.content, self.df, max_rows=100, height=12)

    def page_cleaning(self):
        self.heading(self.content, "Data cleaning", "Changes apply only to the working copy. Reset restores the original uploaded data.")
        if not self.require_data(): return
        top = tk.Frame(self.content, bg="white", padx=16, pady=12); top.pack(fill="x", pady=(0, 12))
        ttk.Button(top, text="Reset to original", command=self.reset_data).pack(side="left")
        ttk.Button(top, text="Remove duplicate rows", command=self.remove_duplicates).pack(side="left", padx=7)
        ttk.Button(top, text="Drop rows with missing values", command=self.drop_missing).pack(side="left", padx=7)
        ttk.Button(top, text="Missing-value report", command=self.show_missing_report).pack(side="left", padx=7)
        box = tk.LabelFrame(self.content, text="Fill missing values", bg="white", padx=12, pady=10)
        box.pack(fill="x", pady=5)
        self.fill_col = tk.StringVar(value=str(self.df.columns[0]))
        self.fill_method = tk.StringVar(value="mean")
        ttk.Label(box, text="Column").grid(row=0, column=0, padx=5, pady=5)
        ttk.Combobox(box, textvariable=self.fill_col, values=list(self.df.columns), state="readonly", width=24).grid(row=0, column=1, padx=5)
        ttk.Label(box, text="Method").grid(row=0, column=2, padx=5)
        ttk.Combobox(box, textvariable=self.fill_method, values=["mean", "median", "mode"], state="readonly", width=14).grid(row=0, column=3, padx=5)
        ttk.Button(box, text="Apply fill", command=self.fill_missing).grid(row=0, column=4, padx=8)
        box2 = tk.LabelFrame(self.content, text="Column operations", bg="white", padx=12, pady=10)
        box2.pack(fill="x", pady=5)
        self.rename_old = tk.StringVar(value=str(self.df.columns[0]))
        self.rename_new = tk.StringVar()
        ttk.Label(box2, text="Rename").grid(row=0, column=0, padx=5)
        ttk.Combobox(box2, textvariable=self.rename_old, values=list(self.df.columns), state="readonly", width=20).grid(row=0, column=1, padx=5)
        ttk.Label(box2, text="to").grid(row=0, column=2)
        ttk.Entry(box2, textvariable=self.rename_new, width=22).grid(row=0, column=3, padx=5)
        ttk.Button(box2, text="Rename column", command=self.rename_column).grid(row=0, column=4, padx=5)
        self.drop_col = tk.StringVar(value=str(self.df.columns[0]))
        ttk.Label(box2, text="Remove column").grid(row=1, column=0, padx=5, pady=9)
        ttk.Combobox(box2, textvariable=self.drop_col, values=list(self.df.columns), state="readonly", width=20).grid(row=1, column=1, padx=5)
        ttk.Button(box2, text="Drop column", command=self.drop_column).grid(row=1, column=2, padx=5)
        ttk.Label(box2, text="Convert type").grid(row=1, column=3, padx=5)
        self.convert_type = tk.StringVar(value="numeric")
        ttk.Combobox(box2, textvariable=self.convert_type, values=["numeric", "datetime", "string"], state="readonly", width=12).grid(row=1, column=4)
        self.convert_col = tk.StringVar(value=str(self.df.columns[0]))
        ttk.Combobox(box2, textvariable=self.convert_col, values=list(self.df.columns), state="readonly", width=18).grid(row=1, column=5, padx=5)
        ttk.Button(box2, text="Convert", command=self.convert_column).grid(row=1, column=6, padx=5)
        tk.Label(self.content, text=f"Current working data: {len(self.df):,} rows × {len(self.df.columns)} columns",
                 bg=BG, fg=MUTED).pack(anchor="w", pady=12)

    def confirm_destructive(self, message):
        return messagebox.askyesno("Confirm data change", message + "\n\nThis changes the working copy only. You can reset to the original.")

    def remove_duplicates(self):
        if self.confirm_destructive("Remove duplicate records?"):
            before = len(self.df); self.df = self.df.drop_duplicates().reset_index(drop=True)
            messagebox.showinfo("Cleaning complete", f"Removed {before-len(self.df)} duplicate rows.")
            self.show_page("Data Cleaning"); self.update_status()

    def drop_missing(self):
        if self.confirm_destructive("Drop every row containing at least one missing value?"):
            before = len(self.df); self.df = self.df.dropna().reset_index(drop=True)
            messagebox.showinfo("Cleaning complete", f"Removed {before-len(self.df)} rows.")
            self.show_page("Data Cleaning"); self.update_status()

    def fill_missing(self):
        col, method = self.fill_col.get(), self.fill_method.get()
        if col not in self.df: return
        series = self.df[col]
        if not series.isna().any():
            messagebox.showinfo("No change", "This column has no missing values."); return
        if method in ("mean", "median"):
            if not pd.api.types.is_numeric_dtype(series):
                messagebox.showerror("Invalid method", f"{method.title()} filling requires a numeric column."); return
            value = series.mean() if method == "mean" else series.median()
        else:
            modes = series.mode(dropna=True)
            if modes.empty: messagebox.showerror("Cannot fill", "No non-missing mode is available."); return
            value = modes.iloc[0]
        if self.confirm_destructive(f"Fill missing values in '{col}' using {method} ({value})?"):
            count = int(series.isna().sum()); self.df[col] = series.fillna(value)
            messagebox.showinfo("Cleaning complete", f"Filled {count} missing values.")
            self.update_status(); self.show_page("Data Cleaning")

    def show_missing_report(self):
        report = self.df.isna().sum().rename("Missing values").to_frame()
        report["Percent"] = (report["Missing values"] / max(1, len(self.df)) * 100).round(2)
        self._show_table_window("Missing-value report", report.reset_index(names="Column"))

    def rename_column(self):
        old, new = self.rename_old.get(), self.rename_new.get().strip()
        if not new: messagebox.showwarning("Column name required", "Enter a new column name."); return
        if new in self.df.columns and new != old: messagebox.showerror("Name exists", "A column with that name already exists."); return
        if self.confirm_destructive(f"Rename '{old}' to '{new}'?"):
            self.df = self.df.rename(columns={old: new}); self.update_status(); self.show_page("Data Cleaning")

    def drop_column(self):
        col = self.drop_col.get()
        if len(self.df.columns) <= 1: messagebox.showwarning("Not allowed", "A dataset must retain at least one column."); return
        if self.confirm_destructive(f"Remove column '{col}'?"):
            self.df = self.df.drop(columns=[col]); self.update_status(); self.show_page("Data Cleaning")

    def convert_column(self):
        col, kind = self.convert_col.get(), self.convert_type.get()
        try:
            if not self.confirm_destructive(f"Convert '{col}' to {kind}?"): return
            if kind == "numeric": converted = pd.to_numeric(self.df[col], errors="coerce")
            elif kind == "datetime": converted = pd.to_datetime(self.df[col], errors="coerce")
            else: converted = self.df[col].astype("string")
            self.df[col] = converted
            self.update_status(); self.show_page("Data Cleaning")
            messagebox.showinfo("Conversion complete", f"Column '{col}' is now {kind}. Invalid values may have become missing.")
        except Exception as exc: messagebox.showerror("Conversion failed", str(exc))

    def reset_data(self):
        if messagebox.askyesno("Reset working data", "Discard all cleaning changes and restore the original upload?"):
            self.df = self.original_df.copy(deep=True); self.update_status(); self.show_page("Data Cleaning")

    def page_analysis(self):
        self.heading(self.content, "Statistical analysis", "Descriptive statistics, percentiles, correlations and category counts.")
        if not self.require_data(): return
        nums = self.df.select_dtypes(include=np.number)
        if nums.empty:
            tk.Label(self.content, text="No numeric columns are available for numerical statistics.", bg=BG, fg=MUTED).pack(anchor="w")
        else:
            tk.Label(self.content, text="NUMERICAL SUMMARY", bg=BG, fg=MUTED,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 6))
            summary = self._summary_frame().round(4)
            self._tree(self.content, summary, max_rows=100, height=10)
        lower = tk.Frame(self.content, bg=BG); lower.pack(fill="both", expand=True, pady=14)
        left = tk.Frame(lower, bg=BG); left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        right = tk.Frame(lower, bg=BG); right.pack(side="left", fill="both", expand=True, padx=(8, 0))
        tk.Label(left, text="CORRELATION MATRIX", bg=BG, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 6))
        if len(nums.columns) >= 2:
            corr = nums.corr(numeric_only=True).round(3).reset_index(names="Column")
            self._tree(left, corr, max_rows=30, height=10)
        else: tk.Label(left, text="At least two numeric columns are needed.", bg=BG, fg=MUTED).pack(anchor="w")
        tk.Label(right, text="UNIQUE-VALUE COUNTS", bg=BG, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 6))
        unique = pd.DataFrame({"Column": self.df.columns.astype(str),
                               "Unique values": self.df.nunique(dropna=True).values,
                               "Missing": self.df.isna().sum().values})
        self._tree(right, unique, max_rows=40, height=10)
        ttk.Button(self.content, text="Export statistical summary CSV", command=self.export_summary_csv).pack(anchor="w", pady=5)

    def page_visualization(self):
        self.heading(self.content, "Visualization studio", "Choose chart settings and render a chart inside the desktop application.")
        if not self.require_data(): return
        controls = tk.Frame(self.content, bg="white", padx=14, pady=12)
        controls.pack(fill="x")
        self.chart_type = tk.StringVar(value="Bar chart")
        self.x_col = tk.StringVar(value=str(self.df.columns[0]))
        numeric = list(self.df.select_dtypes(include=np.number).columns)
        self.y_col = tk.StringVar(value=str(numeric[0] if numeric else self.df.columns[0]))
        self.agg = tk.StringVar(value="sum")
        self.chart_title = tk.StringVar(value="Data visualization")
        self.cat_col = tk.StringVar(value=str(self.df.columns[0]))
        choices = ["Bar chart", "Horizontal bar chart", "Line chart", "Pie chart", "Scatter plot",
                   "Histogram", "Box plot", "Area chart", "Heatmap", "Count plot"]
        fields = [
            ("Chart", ttk.Combobox(controls, textvariable=self.chart_type, values=choices, state="readonly", width=20)),
            ("X / Category", ttk.Combobox(controls, textvariable=self.x_col, values=list(self.df.columns), state="readonly", width=18)),
            ("Y / Numeric", ttk.Combobox(controls, textvariable=self.y_col, values=list(self.df.columns), state="readonly", width=18)),
            ("Aggregation", ttk.Combobox(controls, textvariable=self.agg, values=["sum", "mean", "count", "median", "min", "max"], state="readonly", width=12)),
        ]
        for i, (label, widget) in enumerate(fields):
            tk.Label(controls, text=label, bg="white", fg=MUTED).grid(row=0, column=i, sticky="w", padx=5)
            widget.grid(row=1, column=i, padx=5, pady=(3, 8), sticky="ew")
        tk.Label(controls, text="Chart title", bg="white", fg=MUTED).grid(row=2, column=0, sticky="w", padx=5)
        ttk.Entry(controls, textvariable=self.chart_title, width=25).grid(row=3, column=0, padx=5, sticky="ew")
        tk.Label(controls, text="Count plot category", bg="white", fg=MUTED).grid(row=2, column=1, sticky="w", padx=5)
        ttk.Combobox(controls, textvariable=self.cat_col, values=list(self.df.columns), state="readonly", width=18).grid(row=3, column=1, padx=5)
        ttk.Button(controls, text="Chart color", command=self.choose_chart_color).grid(row=3, column=2, padx=5, sticky="w")
        ttk.Button(controls, text="Generate chart", style="Accent.TButton", command=self.generate_chart).grid(row=3, column=3, padx=5, sticky="w")
        ttk.Button(controls, text="Save chart", command=self.save_chart).grid(row=3, column=4, padx=5, sticky="w")
        self.chart_host = tk.Frame(self.content, bg="white")
        self.chart_host.pack(fill="both", expand=True, pady=(12, 0))
        tk.Label(self.chart_host, text="Your chart will appear here.", bg="white", fg=MUTED).pack(pady=70)

    def choose_chart_color(self):
        color = colorchooser.askcolor(color=self.chart_color, title="Choose chart color")[1]
        if color: self.chart_color = color

    def generate_chart(self):
        if not self.require_data(): return
        kind, x, y = self.chart_type.get(), self.x_col.get(), self.y_col.get()
        data = self.df
        try:
            fig, ax = plt.subplots(figsize=(9.2, 4.8), dpi=100)
            color = self.chart_color
            if kind in ("Bar chart", "Horizontal bar chart", "Line chart", "Area chart", "Pie chart"):
                if x not in data: raise ValueError("Select a valid X/category column.")
                if kind != "Pie chart" and y not in data: raise ValueError("Select a valid Y column.")
                if kind == "Pie chart":
                    counts = data[x].dropna().astype(str).value_counts().head(12)
                    if counts.empty: raise ValueError("No category values are available.")
                    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90)
                    ax.axis("equal")
                else:
                    if not pd.api.types.is_numeric_dtype(data[y]) and self.agg.get() != "count":
                        raise ValueError("Y column must be numeric for this aggregation.")
                    grouped = data.groupby(x, dropna=False)[y].agg(self.agg.get()).dropna().sort_values(ascending=False)
                    if grouped.empty: raise ValueError("No values are available for the selected chart.")
                    grouped = grouped.head(30)
                    if kind == "Bar chart": ax.bar(grouped.index.astype(str), grouped.values, color=color)
                    elif kind == "Horizontal bar chart": ax.barh(grouped.index.astype(str), grouped.values, color=color); ax.invert_yaxis()
                    elif kind == "Line chart": ax.plot(grouped.index.astype(str), grouped.values, marker="o", color=color)
                    elif kind == "Area chart": ax.fill_between(range(len(grouped)), grouped.values, alpha=.3, color=color); ax.plot(range(len(grouped)), grouped.values, color=color); ax.set_xticks(range(len(grouped))); ax.set_xticklabels(grouped.index.astype(str), rotation=35, ha="right")
                    ax.tick_params(axis="x", rotation=35)
            elif kind == "Scatter plot":
                if not pd.api.types.is_numeric_dtype(data[x]) or not pd.api.types.is_numeric_dtype(data[y]):
                    raise ValueError("Scatter plot requires numeric X and Y columns.")
                sns.scatterplot(data=data, x=x, y=y, color=color, ax=ax, alpha=.75)
            elif kind == "Histogram":
                if not pd.api.types.is_numeric_dtype(data[x]): raise ValueError("Histogram requires a numeric X column.")
                sns.histplot(data=data, x=x, color=color, kde=True, ax=ax)
            elif kind == "Box plot":
                if not pd.api.types.is_numeric_dtype(data[y]): raise ValueError("Box plot requires a numeric Y column.")
                if x == y: sns.boxplot(data=data, y=y, color=color, ax=ax)
                else: sns.boxplot(data=data, x=x, y=y, color=color, ax=ax)
            elif kind == "Heatmap":
                nums = data.select_dtypes(include=np.number)
                if len(nums.columns) < 2: raise ValueError("Heatmap requires at least two numeric columns.")
                sns.heatmap(nums.corr(), annot=True, cmap="coolwarm", center=0, ax=ax, fmt=".2f")
            elif kind == "Count plot":
                cat = self.cat_col.get()
                if cat not in data: raise ValueError("Select a valid category column.")
                order = data[cat].astype("string").value_counts().head(25).index
                sns.countplot(data=data, x=cat, order=order, color=color, ax=ax)
                ax.tick_params(axis="x", rotation=35)
            ax.set_title(self.chart_title.get().strip() or kind, fontsize=13, weight="bold")
            if kind not in ("Pie chart", "Heatmap"): ax.grid(axis="y", alpha=.2)
            fig.tight_layout()
            self._display_figure(fig)
        except Exception as exc:
            plt.close("all")
            messagebox.showerror("Chart could not be generated", str(exc))

    def _display_figure(self, fig):
        if self.current_figure is not None: plt.close(self.current_figure)
        for child in self.chart_host.winfo_children(): child.destroy()
        self.current_figure = fig
        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_host)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.chart_host, pack_toolbar=False)
        self.toolbar.update(); self.toolbar.pack(side="bottom", fill="x")

    def save_chart(self):
        if self.current_figure is None:
            messagebox.showwarning("No chart", "Generate a chart before saving."); return
        path = filedialog.asksaveasfilename(defaultextension=".png",
            filetypes=[("PNG image", "*.png"), ("PDF document", "*.pdf")],
            initialdir=EXPORT_DIR, initialfile="data_insight_chart.png")
        if not path: return
        try:
            self.current_figure.savefig(path, dpi=300, bbox_inches="tight")
            messagebox.showinfo("Chart saved", f"Saved chart to:\n{path}")
        except Exception as exc: messagebox.showerror("Export failed", str(exc))

    def page_insights(self):
        self.heading(self.content, "Automatic insights", "Calculated observations from the active dataset. These are descriptive, not predictions.")
        if not self.require_data(): return
        items = []
        missing = self.df.isna().sum()
        if missing.max() > 0:
            col = missing.idxmax(); items.append(f"Most missing values: '{col}' has {int(missing[col])} missing cells ({missing[col]/len(self.df)*100:.1f}% of rows).")
        else: items.append("No missing values were found in the active dataset.")
        nums = self.df.select_dtypes(include=np.number)
        for col in nums.columns:
            s = nums[col].dropna()
            if not s.empty:
                items.append(f"'{col}': minimum {s.min():,.4g}, maximum {s.max():,.4g}, mean {s.mean():,.4g}, median {s.median():,.4g}.")
        cats = self.df.select_dtypes(exclude=np.number)
        for col in cats.columns:
            modes = cats[col].mode(dropna=True)
            if not modes.empty: items.append(f"Most frequent value in '{col}': {modes.iloc[0]} ({int((cats[col] == modes.iloc[0]).sum())} records).")
        if len(nums.columns) >= 2:
            corr = nums.corr()
            pairs = []
            for i, a in enumerate(corr.columns):
                for b in corr.columns[i+1:]:
                    value = corr.loc[a, b]
                    if pd.notna(value): pairs.append((abs(value), value, a, b))
            if pairs:
                _, value, a, b = max(pairs)
                items.append(f"Strongest absolute numeric correlation: '{a}' and '{b}' have correlation {value:.3f}. Correlation does not establish causation.")
                positive = [p for p in pairs if p[1] > 0]
                negative = [p for p in pairs if p[1] < 0]
                if positive:
                    _, v, a, b = max(positive); items.append(f"Strongest positive pair: '{a}' and '{b}' ({v:.3f}).")
                if negative:
                    _, v, a, b = max(negative, key=lambda p: p[1]); items.append(f"Strongest negative pair: '{a}' and '{b}' ({v:.3f}).")
        for i, item in enumerate(items, 1):
            card = tk.Frame(self.content, bg="white", padx=15, pady=12)
            card.pack(fill="x", pady=4)
            tk.Label(card, text=f"{i:02d}", bg="white", fg=ACCENT, font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 12))
            tk.Label(card, text=item, bg="white", fg=TEXT, wraplength=1000, justify="left").pack(side="left", fill="x", expand=True)

    def page_export(self):
        self.heading(self.content, "Export results", "Save a copy of your working dataset, summary tables and charts.")
        if not self.require_data(): return
        panel = tk.Frame(self.content, bg="white", padx=20, pady=18); panel.pack(fill="x")
        actions = [
            ("Export working dataset as CSV", self.export_csv),
            ("Export working dataset as Excel", self.export_excel),
            ("Export statistical summary as CSV", self.export_summary_csv),
            ("Export complete Excel workbook (data + summary)", self.export_workbook),
        ]
        for label, command in actions:
            ttk.Button(panel, text=label, command=command).pack(anchor="w", pady=6)
        tk.Label(self.content, text="Charts can be saved as PNG or PDF from the Visualization Studio.",
                 bg=BG, fg=MUTED).pack(anchor="w", pady=15)

    def _save_path(self, title, ext, types, filename):
        return filedialog.asksaveasfilename(title=title, defaultextension=ext,
            filetypes=types, initialdir=EXPORT_DIR, initialfile=filename)

    def export_csv(self):
        path = self._save_path("Export dataset as CSV", ".csv", [("CSV", "*.csv")], "cleaned_dataset.csv")
        if not path: return
        try: self.df.to_csv(path, index=False); messagebox.showinfo("Export complete", f"Saved:\n{path}")
        except Exception as exc: messagebox.showerror("Export failed", str(exc))

    def export_excel(self):
        path = self._save_path("Export dataset as Excel", ".xlsx", [("Excel workbook", "*.xlsx")], "cleaned_dataset.xlsx")
        if not path: return
        try: self.df.to_excel(path, index=False); messagebox.showinfo("Export complete", f"Saved:\n{path}")
        except Exception as exc: messagebox.showerror("Export failed", str(exc))

    def _summary_frame(self):
        nums = self.df.select_dtypes(include=np.number)
        if nums.empty:
            return pd.DataFrame({"Information": ["No numeric columns available"]})
        rows = []
        for column in nums.columns:
            values = nums[column].dropna()
            if values.empty:
                rows.append({"Column": str(column), "Count": 0})
                continue
            modes = values.mode()
            rows.append({
                "Column": str(column),
                "Count": int(values.count()),
                "Mean": values.mean(),
                "Median": values.median(),
                "Mode": modes.iloc[0] if not modes.empty else np.nan,
                "Minimum": values.min(),
                "Maximum": values.max(),
                "Range": values.max() - values.min(),
                "Std Dev": values.std(),
                "Variance": values.var(),
                "Q1 (25%)": values.quantile(.25),
                "Q3 (75%)": values.quantile(.75),
                "P10": values.quantile(.10),
                "P90": values.quantile(.90),
            })
        return pd.DataFrame(rows)

    def export_summary_csv(self):
        if not self.require_data(): return
        path = self._save_path("Export statistical summary", ".csv", [("CSV", "*.csv")], "statistical_summary.csv")
        if not path: return
        try: self._summary_frame().to_csv(path, index=False); messagebox.showinfo("Export complete", f"Saved:\n{path}")
        except Exception as exc: messagebox.showerror("Export failed", str(exc))

    def export_workbook(self):
        path = self._save_path("Export complete workbook", ".xlsx", [("Excel workbook", "*.xlsx")], "data_insight_results.xlsx")
        if not path: return
        try:
            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                self.df.to_excel(writer, sheet_name="Data", index=False)
                self._summary_frame().to_excel(writer, sheet_name="Statistics", index=False)
                self.df.isna().sum().rename("Missing values").to_frame().to_excel(writer, sheet_name="Missing Values")
            messagebox.showinfo("Export complete", f"Saved workbook:\n{path}")
        except Exception as exc: messagebox.showerror("Export failed", str(exc))

    def _show_table_window(self, title, data):
        win = tk.Toplevel(self); win.title(title); win.geometry("850x500")
        self._tree(win, data, max_rows=500, height=18)

    def page_about(self):
        self.heading(self.content, "About the project", "A beginner-friendly desktop tool for local exploratory data analysis.")
        sections = [
            ("Purpose", "DATA INSIGHT helps students and small teams inspect datasets, clean data, calculate descriptive statistics, create visualizations and export results without writing analysis code."),
            ("Technology", "Python 3, Tkinter/ttk, Pandas, NumPy, Matplotlib, Seaborn and OpenPyXL. SciPy is optional for future extensions."),
            ("Privacy and operation", "Files are read and processed on your computer. The application does not upload datasets to a server and does not require internet access after dependencies are installed."),
            ("Important interpretation note", "Descriptive statistics and correlations summarize observed data. Correlation does not prove causation, and automatically generated insights are not predictive claims."),
            ("Limitations", "Very large files may require substantial memory. Legacy .xls support requires xlrd. Excel formulas are read as stored values; macros are not executed. Advanced statistical tests and automated predictive modelling are not included."),
            ("License", "This project is provided as an educational example. Python and third-party packages retain their respective licenses. Review package licenses before redistribution.")
        ]
        for title, body in sections:
            box = tk.Frame(self.content, bg="white", padx=16, pady=13); box.pack(fill="x", pady=5)
            tk.Label(box, text=title, bg="white", fg=ACCENT, font=("Segoe UI", 10, "bold")).pack(anchor="w")
            tk.Label(box, text=body, bg="white", fg=TEXT, justify="left", wraplength=1050).pack(anchor="w", pady=(5, 0))

    def on_exit(self):
        if messagebox.askyesno("Exit DATA INSIGHT", "Close the application? Unsaved working changes will be lost."):
            if self.current_figure is not None: plt.close(self.current_figure)
            self.destroy()


if __name__ == "__main__":
    try:
        app = DataInsightApp()
        app.mainloop()
    except Exception as error:
        messagebox.showerror("Application error", f"DATA INSIGHT could not start:\n{error}\n\n{traceback.format_exc()}")
        raise
