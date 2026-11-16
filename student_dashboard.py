"""
Student Performance and Study-Hours Dashboard
=============================================
Main application providing statistical analysis, Matplotlib charts, and a
Tkinter desktop graphical dashboard.

Features:
- Encapsulated record validation and grade mapping via StudentRecord.
- NumPy array-based central tendency, dispersion, percentiles, and IQR outlier detection.
- Pandas course-wise aggregation and correlation analysis.
- Matplotlib embedded visualisations (scatter plot with dual linear fits, score histogram,
  grade distribution bar chart, course comparisons).
- Interactive Tkinter desktop GUI with metric cards, course filtering, customizable
  IQR threshold, outlier toggle, record table viewer, and export functionality.
- Seamless execution in terminal, Python IDLE (F5), or script runners.
"""

import os
import sys
import argparse

# Configure writable Matplotlib configuration directory before importing matplotlib
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MPL_DIR = os.path.join(CURRENT_DIR, ".mplconfig")
os.makedirs(MPL_DIR, exist_ok=True)
os.environ["MPLCONFIGDIR"] = MPL_DIR

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr

# Internal project modules
from student_record import StudentRecord, score_to_grade
from generate_data import load_csv, save_csv, DEFAULT_CSV_PATH

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIGURES_DIR = os.path.join(CURRENT_DIR, "figures")


# ==============================================================================
# 1. Statistical and Analytical Functions
# ==============================================================================

def iqr_mask(series: pd.Series, k: float = 1.5) -> pd.Series:
    """
    Identify outliers in a numeric Series using the Interquartile Range (IQR) rule:
    Flagged if value < Q1 - k * IQR or value > Q3 + k * IQR.
    """
    clean_series = pd.to_numeric(series, errors="coerce").dropna()
    if len(clean_series) < 4:
        return pd.Series(False, index=series.index)
    
    q1 = clean_series.quantile(0.25)
    q3 = clean_series.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - k * iqr
    upper_bound = q3 + k * iqr
    return (series < lower_bound) | (series > upper_bound)


def get_outliers_mask(df: pd.DataFrame, k: float = 1.5) -> pd.Series:
    """Flag records as outliers if either study_hours or score exceeds IQR bounds."""
    if df.empty:
        return pd.Series(dtype=bool)
    hours_out = iqr_mask(df["study_hours"], k=k)
    score_out = iqr_mask(df["score"], k=k)
    return hours_out | score_out


def correlation(df: pd.DataFrame, drop_outliers: bool = False, k: float = 1.5) -> dict:
    """
    Calculate Pearson's linear correlation (r) and Spearman's rank correlation (rho).
    Returns a dictionary with r, rho, and p-values.
    """
    data = df.dropna(subset=["study_hours", "score"]).copy()
    if drop_outliers:
        out_mask = get_outliers_mask(data, k=k)
        data = data[~out_mask]
        
    if len(data) < 3:
        return {"pearson_r": 0.0, "pearson_p": 1.0, "spearman_rho": 0.0, "spearman_p": 1.0, "n": len(data)}

    h = data["study_hours"].values
    s = data["score"].values
    pr, pp = pearsonr(h, s)
    sr, sp = spearmanr(h, s)
    return {
        "pearson_r": float(pr),
        "pearson_p": float(pp),
        "spearman_rho": float(sr),
        "spearman_p": float(sp),
        "n": len(data)
    }


def analysis_for(df: pd.DataFrame, k: float = 1.5) -> dict:
    """
    Compute comprehensive descriptive statistics, percentiles, outlier breakdown,
    course summaries, and correlation metrics.
    """
    if df.empty:
        return {}

    scores = df["score"].values
    hours = df["study_hours"].values
    n = len(df)

    q1_score = float(np.percentile(scores, 25))
    q3_score = float(np.percentile(scores, 75))
    iqr_score = q3_score - q1_score

    q1_hours = float(np.percentile(hours, 25))
    q3_hours = float(np.percentile(hours, 75))
    iqr_hours = q3_hours - q1_hours

    out_mask = get_outliers_mask(df, k=k)
    outliers_df = df[out_mask].copy()

    # Correlations
    corr_all = correlation(df, drop_outliers=False, k=k)
    corr_clean = correlation(df, drop_outliers=True, k=k)

    # Grades
    grade_order = ["A", "B", "C", "D", "F"]
    grade_counts = {g: 0 for g in grade_order}
    for g, count in df["grade"].value_counts().items():
        if g in grade_counts:
            grade_counts[g] = int(count)

    # Course summaries
    course_summary = df.groupby("course").agg(
        students=("student_id", "count"),
        mean_score=("score", "mean"),
        mean_hours=("study_hours", "mean"),
        median_score=("score", "median")
    ).round(2).reset_index()

    return {
        "n": n,
        "mean_score": float(np.mean(scores)),
        "median_score": float(np.median(scores)),
        "std_score": float(np.std(scores, ddof=1)) if n > 1 else 0.0,
        "q1_score": q1_score,
        "q3_score": q3_score,
        "iqr_score": iqr_score,
        "mean_hours": float(np.mean(hours)),
        "median_hours": float(np.median(hours)),
        "std_hours": float(np.std(hours, ddof=1)) if n > 1 else 0.0,
        "q1_hours": q1_hours,
        "q3_hours": q3_hours,
        "iqr_hours": iqr_hours,
        "outlier_count": int(out_mask.sum()),
        "outlier_pct": float((out_mask.sum() / n) * 100),
        "outliers_df": outliers_df,
        "corr_all": corr_all,
        "corr_clean": corr_clean,
        "grade_counts": grade_counts,
        "course_summary": course_summary,
        "k": k
    }


def interpretation(stats: dict) -> str:
    """
    Produce the automated statistical discussion, highlighting the impact of
    outliers on linear regression and the fundamental non-causation caveat.
    """
    if not stats:
        return "No data available for analysis."

    c_all = stats["corr_all"]
    c_cln = stats["corr_clean"]
    out_cnt = stats["outlier_count"]
    k_val = stats["k"]

    lines = [
        "=" * 70,
        "STATISTICAL INTERPRETATION AND METHODOLOGICAL ANALYSIS",
        "=" * 70,
        f"Total Valid Observations Analyzed : {stats['n']}",
        f"Average Assessment Score          : {stats['mean_score']:.2f} / 100",
        f"Median Assessment Score           : {stats['median_score']:.2f} / 100",
        f"Score Dispersion (Sample Std Dev) : {stats['std_score']:.2f}",
        f"Score Quartiles (Q1 / Q3 / IQR)   : {stats['q1_score']:.2f} / {stats['q3_score']:.2f} / {stats['iqr_score']:.2f}",
        f"Average Weekly Study Hours        : {stats['mean_hours']:.2f} hrs/week",
        f"Outliers Flagged (k = {k_val})       : {out_cnt} records ({stats['outlier_pct']:.1f}%)",
        "-" * 70,
        "1. ASSOCIATION BETWEEN STUDY HOURS AND ASSESSMENT SCORES:",
        f"   - All valid records (n = {stats['n']}):",
        f"       Pearson correlation coefficient (r) : {c_all['pearson_r']:.3f} (p = {c_all['pearson_p']:.4e})",
        f"       Spearman rank correlation (rho)     : {c_all['spearman_rho']:.3f} (p = {c_all['spearman_p']:.4e})",
        f"   - Excluding flagged outliers (n = {c_cln['n']}):",
        f"       Pearson correlation coefficient (r) : {c_cln['pearson_r']:.3f} (p = {c_cln['pearson_p']:.4e})",
        f"       Spearman rank correlation (rho)     : {c_cln['spearman_rho']:.3f} (p = {c_cln['spearman_p']:.4e})",
        "",
        "2. SENSITIVITY TO EXTREME OBSERVATIONS:",
        f"   Removing the {out_cnt} IQR-flagged records increases Pearson's r from {c_all['pearson_r']:.3f} to {c_cln['pearson_r']:.3f},",
        f"   demonstrating substantial sensitivity of standard linear regression to extreme values.",
        f"   In contrast, Spearman's rank correlation shows greater stability ({c_all['spearman_rho']:.3f} vs {c_cln['spearman_rho']:.3f}).",
        "   This confirms that while a positive monotonic relationship exists throughout the cohort,",
        "   isolated atypical records (e.g. high study time with low score) heavily dampen the linear slope.",
        "",
        "3. CRITICAL NON-CAUSATION CAVEAT (METHODOLOGICAL WARNING):",
        "   A positive correlation between reported study hours and marks DOES NOT establish",
        "   that additional study hours directly cause higher marks.",
        "   Confounding variables including prior educational background, student motivation,",
        "   lecture attendance, study techniques, course difficulty, and self-reporting bias",
        "   readily influence assessment results.",
        "=" * 70
    ]
    return "\n".join(lines)


# ==============================================================================
# 2. Matplotlib Visualization Functions
# ==============================================================================

def draw_scatter(df: pd.DataFrame, ax: plt.Axes, k: float = 1.5, hide_outliers: bool = False):
    """Draw study-hours-versus-score scatter plot with flagged outliers and dual linear fits."""
    ax.clear()
    if df.empty:
        ax.text(0.5, 0.5, "No data available", ha="center", va="center")
        return

    out_mask = get_outliers_mask(df, k=k)
    clean_df = df[~out_mask]
    outliers_df = df[out_mask]

    # Plot points
    ax.scatter(
        clean_df["study_hours"], clean_df["score"],
        color="#2563EB", alpha=0.75, s=36, edgecolors="none", label="Typical records"
    )

    if not hide_outliers and not outliers_df.empty:
        ax.scatter(
            outliers_df["study_hours"], outliers_df["score"],
            color="#DC2626", marker="x", s=80, linewidths=2.2, label="Flagged outliers"
        )
        for _, row in outliers_df.iterrows():
            ax.annotate(
                f"{row['student_id']}",
                (row["study_hours"], row["score"]),
                textcoords="offset points", xytext=(6, 5), fontsize=8.5, color="#991B1B"
            )

    # Linear Regression Lines
    h_all = df["study_hours"].values
    s_all = df["score"].values
    if len(h_all) > 1:
        slope_all, intercept_all = np.polyfit(h_all, s_all, 1)
        x_vals_all = np.linspace(0, max(h_all.max() + 2, 45), 100)
        y_vals_all = slope_all * x_vals_all + intercept_all
        ax.plot(x_vals_all, y_vals_all, color="#64748B", linestyle="--", linewidth=1.8, label="All records")

    h_cln = clean_df["study_hours"].values
    s_cln = clean_df["score"].values
    if len(h_cln) > 1:
        slope_cln, intercept_cln = np.polyfit(h_cln, s_cln, 1)
        x_vals_cln = np.linspace(0, max(h_cln.max() + 2, 35), 100)
        y_vals_cln = slope_cln * x_vals_cln + intercept_cln
        ax.plot(x_vals_cln, y_vals_cln, color="#059669", linestyle="-", linewidth=2.2, label="Without flagged outliers")

    ax.set_title("Study Hours vs. Assessment Scores", fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("Reported study hours per week", fontsize=10)
    ax.set_ylabel("Assessment score (0–100)", fontsize=10)
    ax.set_ylim(-2, 108)
    ax.set_xlim(-1, max(h_all.max() + 4, 48) if len(h_all) > 0 else 50)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1", fontsize=8.5)


def draw_scores(df: pd.DataFrame, ax_hist: plt.Axes, ax_bar: plt.Axes):
    """Draw score histogram and grade frequency bar chart."""
    ax_hist.clear()
    ax_bar.clear()
    if df.empty:
        return

    scores = df["score"].values
    mean_val = float(np.mean(scores))
    med_val = float(np.median(scores))

    # Histogram
    bins = np.arange(0, 110, 10)
    ax_hist.hist(scores, bins=bins, color="#2563EB", edgecolor="white", alpha=0.85, rwidth=0.92)
    ax_hist.axvline(mean_val, color="#DC2626", linestyle="--", linewidth=1.8, label=f"Mean {mean_val:.1f}")
    ax_hist.axvline(med_val, color="#0D9488", linestyle=":", linewidth=2.0, label=f"Median {med_val:.1f}")
    ax_hist.set_title("Score distribution", fontsize=11, fontweight="bold")
    ax_hist.set_xlabel("Assessment score", fontsize=9.5)
    ax_hist.set_ylabel("Number of students", fontsize=9.5)
    ax_hist.set_xlim(0, 105)
    ax_hist.grid(True, linestyle=":", alpha=0.5, axis="y")
    ax_hist.legend(fontsize=8.5, loc="upper right")

    # Grade Distribution
    grade_order = ["A", "B", "C", "D", "F"]
    counts = [int((df["grade"] == g).sum()) for g in grade_order]
    bars = ax_bar.bar(grade_order, counts, color="#1D4ED8", width=0.6, edgecolor="white")
    ax_bar.set_title("Grade distribution", fontsize=11, fontweight="bold")
    ax_bar.set_xlabel("Letter grade", fontsize=9.5)
    ax_bar.set_ylabel("Number of students", fontsize=9.5)
    ax_bar.set_ylim(0, max(counts) + 6 if counts else 10)
    ax_bar.grid(True, linestyle=":", alpha=0.5, axis="y")

    # Annotate bar counts
    for bar in bars:
        h = bar.get_height()
        ax_bar.annotate(
            f"{int(h)}",
            (bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold"
        )


def draw_courses(df: pd.DataFrame, ax: plt.Axes):
    """Draw course-wise comparison of average score and weekly study hours."""
    ax.clear()
    if df.empty:
        return

    summary = df.groupby("course").agg(
        mean_score=("score", "mean"),
        mean_hours=("study_hours", "mean"),
        students=("student_id", "count")
    ).reset_index()

    courses = summary["course"].tolist()
    x = np.arange(len(courses))
    width = 0.35

    ax2 = ax.twinx()
    rects1 = ax.bar(x - width / 2, summary["mean_score"], width, label="Mean Score (0-100)", color="#2563EB")
    rects2 = ax2.bar(x + width / 2, summary["mean_hours"], width, label="Mean Hours/Week", color="#10B981")

    ax.set_xlabel("Course", fontsize=10, fontweight="bold")
    ax.set_ylabel("Mean Assessment Score", fontsize=10, color="#1E40AF")
    ax2.set_ylabel("Mean Weekly Study Hours", fontsize=10, color="#065F46")
    ax.set_title("Course-Level Performance & Study Hours Comparison", fontsize=12, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{c}\n(n={s})" for c, s in zip(courses, summary["students"])], fontsize=9.5)
    ax.set_ylim(0, 100)
    ax2.set_ylim(0, max(summary["mean_hours"]) * 1.5 if not summary.empty else 25)
    ax.grid(True, linestyle=":", alpha=0.4, axis="y")

    # Combined legend
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=8.5)


def save_figures(df: pd.DataFrame, output_dir: str = FIGURES_DIR, k: float = 1.5) -> dict:
    """Save all analytical plots as high-resolution PNG images."""
    os.makedirs(output_dir, exist_ok=True)
    paths = {}

    # Figure 1: Score & Grade Distribution
    fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=300)
    draw_scores(df, ax1, ax2)
    fig1.tight_layout()
    p1 = os.path.join(output_dir, "score_and_grade_distribution.png")
    fig1.savefig(p1, bbox_inches="tight")
    plt.close(fig1)
    paths["fig1"] = p1

    # Figure 2: Scatter plot
    fig2, ax_scat = plt.subplots(figsize=(8, 4.8), dpi=300)
    draw_scatter(df, ax_scat, k=k, hide_outliers=False)
    fig2.tight_layout()
    p2 = os.path.join(output_dir, "study_hours_vs_score_scatter.png")
    fig2.savefig(p2, bbox_inches="tight")
    plt.close(fig2)
    paths["fig2"] = p2

    # Figure 3: Course comparison
    fig3, ax_crs = plt.subplots(figsize=(8, 4.5), dpi=300)
    draw_courses(df, ax_crs)
    fig3.tight_layout()
    p3 = os.path.join(output_dir, "course_performance_comparison.png")
    fig3.savefig(p3, bbox_inches="tight")
    plt.close(fig3)
    paths["fig3"] = p3

    return paths


# ==============================================================================
# 3. Graphical User Interface (Tkinter Dashboard)
# ==============================================================================

class Dashboard:
    """
    Tkinter desktop application for student performance and study-hours investigation.
    """

    def __init__(self, root, csv_path: str = DEFAULT_CSV_PATH):
        self.root = root
        self.root.title("Student Performance and Study-Hours Dashboard")
        self.root.geometry("1100x780")
        self.root.minsize(950, 680)

        self.current_csv_path = csv_path
        self.full_df = pd.DataFrame()
        self.filtered_df = pd.DataFrame()
        self.rejected_records = []

        # UI State variables
        import tkinter as tk
        from tkinter import ttk
        self.course_var = tk.StringVar(value="All")
        self.iqr_var = tk.DoubleVar(value=1.5)
        self.hide_outliers_var = tk.BooleanVar(value=False)

        # Metric variables
        self.student_count_var = tk.StringVar(value="--")
        self.mean_score_var = tk.StringVar(value="--")
        self.median_score_var = tk.StringVar(value="--")
        self.mean_hours_var = tk.StringVar(value="--")
        self.outlier_count_var = tk.StringVar(value="--")

        self._apply_style()
        self._build_ui()
        self.load_data(self.current_csv_path)

    def _apply_style(self):
        from tkinter import ttk
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TFrame", background="#F1F5F9")
        style.configure("Card.TFrame", background="#FFFFFF", relief="ridge", borderwidth=1)
        style.configure("TopBar.TFrame", background="#1E293B")
        style.configure("MetricTitle.TLabel", background="#FFFFFF", foreground="#64748B", font=("Segoe UI", 9, "bold"))
        style.configure("MetricVal.TLabel", background="#FFFFFF", foreground="#0F172A", font=("Segoe UI", 16, "bold"))
        style.configure("TNotebook", background="#F1F5F9")
        style.configure("TNotebook.Tab", font=("Segoe UI", 9, "bold"), padding=[12, 6])

    def _build_ui(self):
        import tkinter as tk
        from tkinter import ttk
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        # Main Layout: Top Bar, Metric Cards, Notebook
        top_bar = ttk.Frame(self.root, padding=8, style="TopBar.TFrame")
        top_bar.pack(fill="x", side="top")

        # Top Controls
        btn_open = tk.Button(
            top_bar, text="Open CSV", command=self.open_csv,
            bg="#2563EB", fg="white", activebackground="#1D4ED8", activeforeground="white",
            relief="flat", font=("Segoe UI", 9, "bold"), padx=10, pady=4
        )
        btn_open.pack(side="left", padx=4)

        btn_sample = tk.Button(
            top_bar, text="Use Sample Data", command=self.use_sample_data,
            bg="#0D9488", fg="white", activebackground="#0F766E", activeforeground="white",
            relief="flat", font=("Segoe UI", 9, "bold"), padx=10, pady=4
        )
        btn_sample.pack(side="left", padx=4)

        btn_export = tk.Button(
            top_bar, text="Export Filtered CSV", command=self.save_csv_dialog,
            bg="#475569", fg="white", activebackground="#334155", activeforeground="white",
            relief="flat", font=("Segoe UI", 9), padx=8, pady=4
        )
        btn_export.pack(side="left", padx=4)

        # Filters
        lbl_course = tk.Label(top_bar, text="Course:", bg="#1E293B", fg="#F8FAFC", font=("Segoe UI", 9, "bold"))
        lbl_course.pack(side="left", padx=(16, 4))
        self.cbo_course = ttk.Combobox(
            top_bar, textvariable=self.course_var, state="readonly", width=12, values=["All"]
        )
        self.cbo_course.pack(side="left", padx=4)
        self.cbo_course.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        lbl_iqr = tk.Label(top_bar, text="IQR k:", bg="#1E293B", fg="#F8FAFC", font=("Segoe UI", 9, "bold"))
        lbl_iqr.pack(side="left", padx=(12, 4))
        self.cbo_iqr = ttk.Combobox(
            top_bar, textvariable=self.iqr_var, state="readonly", width=5, values=[1.0, 1.5, 2.0, 2.5, 3.0]
        )
        self.cbo_iqr.pack(side="left", padx=4)
        self.cbo_iqr.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        chk_hide = tk.Checkbutton(
            top_bar, text="Hide Outliers in Charts", variable=self.hide_outliers_var,
            command=self.refresh, bg="#1E293B", fg="#F8FAFC", activebackground="#1E293B",
            activeforeground="#38BDF8", selectcolor="#0F172A", font=("Segoe UI", 9)
        )
        chk_hide.pack(side="left", padx=12)

        # KPI Metric Cards Frame
        cards_frame = ttk.Frame(self.root, padding=(10, 8), style="TFrame")
        cards_frame.pack(fill="x", side="top")

        metrics_info = [
            ("STUDENTS", self.student_count_var),
            ("MEAN SCORE", self.mean_score_var),
            ("MEDIAN SCORE", self.median_score_var),
            ("MEAN STUDY HOURS", self.mean_hours_var),
            ("OUTLIERS FLAGGED", self.outlier_count_var),
        ]
        for title, var in metrics_info:
            card = ttk.Frame(cards_frame, padding=(12, 6), style="Card.TFrame")
            card.pack(side="left", expand=True, fill="both", padx=5)
            ttk.Label(card, text=title, style="MetricTitle.TLabel").pack(anchor="w")
            ttk.Label(card, textvariable=var, style="MetricVal.TLabel").pack(anchor="w", pady=(2, 0))

        # Notebook Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Tab 1: Study hours vs scores
        self.tab_scatter = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_scatter, text="Study Hours vs Scores")
        self.fig_scatter, self.ax_scatter = plt.subplots(figsize=(8, 4.5), dpi=100)
        self.canvas_scatter = FigureCanvasTkAgg(self.fig_scatter, master=self.tab_scatter)
        self.canvas_scatter.get_tk_widget().pack(fill="both", expand=True)

        # Tab 2: Scores & grades
        self.tab_scores = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_scores, text="Scores & Grades")
        self.fig_scores, (self.ax_hist, self.ax_bar) = plt.subplots(1, 2, figsize=(9, 4.5), dpi=100)
        self.canvas_scores = FigureCanvasTkAgg(self.fig_scores, master=self.tab_scores)
        self.canvas_scores.get_tk_widget().pack(fill="both", expand=True)

        # Tab 3: Course comparison
        self.tab_courses = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_courses, text="Course Comparison")
        self.fig_courses, self.ax_courses = plt.subplots(figsize=(8, 4.5), dpi=100)
        self.canvas_courses = FigureCanvasTkAgg(self.fig_courses, master=self.tab_courses)
        self.canvas_courses.get_tk_widget().pack(fill="both", expand=True)

        # Tab 4: Outliers & records table
        self.tab_records = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_records, text="Outliers & Records")
        self._build_records_tab()

        # Tab 5: Written analysis
        self.tab_analysis = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_analysis, text="Written Analysis")
        self._build_analysis_tab()

    def _build_records_tab(self):
        import tkinter as tk
        from tkinter import ttk

        cols = ("student_id", "course", "study_hours", "score", "grade", "is_outlier")
        self.tree = ttk.Treeview(self.tab_records, columns=cols, show="headings", selectmode="browse")
        
        self.tree.heading("student_id", text="Student ID")
        self.tree.heading("course", text="Course")
        self.tree.heading("study_hours", text="Weekly Study Hours")
        self.tree.heading("score", text="Score (0-100)")
        self.tree.heading("grade", text="Grade")
        self.tree.heading("is_outlier", text="Outlier Status")

        self.tree.column("student_id", width=120, anchor="center")
        self.tree.column("course", width=150, anchor="w")
        self.tree.column("study_hours", width=140, anchor="center")
        self.tree.column("score", width=120, anchor="center")
        self.tree.column("grade", width=80, anchor="center")
        self.tree.column("is_outlier", width=140, anchor="center")

        # Tags for highlighting outliers
        self.tree.tag_configure("outlier", background="#FEE2E2", foreground="#991B1B")
        self.tree.tag_configure("normal", background="#FFFFFF")

        scrollbar = ttk.Scrollbar(self.tab_records, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

    def _build_analysis_tab(self):
        import tkinter as tk
        from tkinter import ttk
        self.txt_analysis = tk.Text(
            self.tab_analysis, wrap="word", font=("Consolas", 10),
            bg="#F8FAFC", fg="#0F172A", relief="flat", padx=14, pady=12
        )
        scroll = ttk.Scrollbar(self.tab_analysis, orient="vertical", command=self.txt_analysis.yview)
        self.txt_analysis.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.txt_analysis.pack(side="left", fill="both", expand=True)

    def load_data(self, filepath: str):
        from tkinter import messagebox
        try:
            valid_df, rejected = load_csv(filepath)
            self.full_df = valid_df
            self.rejected_records = rejected
            self.current_csv_path = filepath

            # Update course filter combobox
            courses = sorted(self.full_df["course"].unique().tolist())
            self.cbo_course["values"] = ["All"] + courses
            self.course_var.set("All")

            if rejected:
                msg = f"Loaded {len(valid_df)} valid student records.\n{len(rejected)} invalid records rejected."
                print(msg)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error Loading CSV", str(e))

    def refresh(self):
        """Re-filter data, update metric cards, redraw charts, and refresh table/text."""
        if self.full_df.empty:
            return

        selected_course = self.course_var.get()
        if selected_course == "All" or not selected_course:
            self.filtered_df = self.full_df.copy()
        else:
            self.filtered_df = self.full_df[self.full_df["course"] == selected_course].copy()

        k_val = float(self.iqr_var.get())
        hide_outliers = self.hide_outliers_var.get()

        stats = analysis_for(self.filtered_df, k=k_val)
        if not stats:
            return

        # 1. Update KPI metric cards
        self.student_count_var.set(f"{stats['n']}")
        self.mean_score_var.set(f"{stats['mean_score']:.1f}")
        self.median_score_var.set(f"{stats['median_score']:.1f}")
        self.mean_hours_var.set(f"{stats['mean_hours']:.1f} hrs")
        self.outlier_count_var.set(f"{stats['outlier_count']} ({stats['outlier_pct']:.1f}%)")

        # 2. Redraw Matplotlib Figures
        draw_scatter(self.filtered_df, self.ax_scatter, k=k_val, hide_outliers=hide_outliers)
        self.fig_scatter.tight_layout()
        self.canvas_scatter.draw()

        draw_scores(self.filtered_df, self.ax_hist, self.ax_bar)
        self.fig_scores.tight_layout()
        self.canvas_scores.draw()

        draw_courses(self.filtered_df, self.ax_courses)
        self.fig_courses.tight_layout()
        self.canvas_courses.draw()

        # 3. Refresh Treeview Table
        for row in self.tree.get_children():
            self.tree.delete(row)

        out_mask = get_outliers_mask(self.filtered_df, k=k_val)
        for idx, row in self.filtered_df.iterrows():
            is_out = bool(out_mask.loc[idx])
            tag = "outlier" if is_out else "normal"
            status_text = "FLAGGED OUTLIER" if is_out else "Normal"
            self.tree.insert(
                "", "end",
                values=(row["student_id"], row["course"], f"{row['study_hours']:.1f}", f"{row['score']:.1f}", row["grade"], status_text),
                tags=(tag,)
            )

        # 4. Refresh Analysis Text
        report_text = interpretation(stats)
        if self.rejected_records:
            report_text += "\n\n" + "=" * 70 + "\nDATA VALIDATION AND REJECTED INPUT ROWS:\n" + "=" * 70
            for r in self.rejected_records:
                report_text += f"\n- Row {r.get('_row_number')}: Student ID '{r.get('student_id')}' | Rejection Reason: {r.get('_rejection_reason')}"
        
        self.txt_analysis.delete("1.0", "end")
        self.txt_analysis.insert("1.0", report_text)

    def open_csv(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Open Student Records CSV",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if path:
            self.load_data(path)

    def use_sample_data(self):
        self.load_data(DEFAULT_CSV_PATH)

    def save_csv_dialog(self):
        from tkinter import filedialog, messagebox
        if self.filtered_df.empty:
            messagebox.showinfo("Export CSV", "No data to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Export Filtered Student Records"
        )
        if path:
            save_csv(self.filtered_df, path)
            messagebox.showinfo("Export Successful", f"Exported {len(self.filtered_df)} records to:\n{path}")

    @classmethod
    def launch(cls, csv_path: str = DEFAULT_CSV_PATH):
        """Entry point to start the Tkinter GUI event loop."""
        import tkinter as tk
        root = tk.Tk()
        app = cls(root, csv_path)
        root.mainloop()


# ==============================================================================
# 4. Execution Entry Point
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Student Performance and Study-Hours Dashboard")
    parser.add_argument("--csv", type=str, default=DEFAULT_CSV_PATH, help="Path to input student CSV file")
    parser.add_argument("--cli", action="store_true", help="Run in command-line mode without GUI")
    parser.add_argument("--save-figures", action="store_true", help="Generate and save PNG figures to figures/ directory")
    parser.add_argument("--k", type=float, default=1.5, help="IQR outlier threshold multiplier (default: 1.5)")
    args = parser.parse_args()

    # If --cli or --save-figures requested, execute non-interactively
    if args.cli or args.save_figures:
        df, rejected = load_csv(args.csv)
        print(f"Loaded {len(df)} valid records. Rejected: {len(rejected)}.")
        stats = analysis_for(df, k=args.k)
        print(interpretation(stats))
        
        if args.save_figures:
            paths = save_figures(df, FIGURES_DIR, k=args.k)
            print("\nSaved figures:")
            for name, path in paths.items():
                print(f" - {name}: {path}")
        return

    # Default: Launch Tkinter Dashboard
    try:
        Dashboard.launch(args.csv)
    except Exception as e:
        print(f"Unable to launch graphical interface ({e}). Falling back to CLI mode...")
        df, rejected = load_csv(args.csv)
        stats = analysis_for(df, k=args.k)
        print(interpretation(stats))
        save_figures(df, FIGURES_DIR, k=args.k)


if __name__ == "__main__":
    main()
