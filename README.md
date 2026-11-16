# Student Performance and Study-Hours Dashboard

> **Python Programming Laboratory Project**
> **Members:
> **167. ANOUSHKA GHOSH 12025052003179.**
> **170. ABESH GHOSH 12025052003182.**
> **178. SOUMIK MONDAL 12025052003192.**
> **Course:** Bachelor of Technology (B.Tech) — Electronics and Communication Engineering  
> **Institute:** Institute of Engineering & Management, Kolkata  
> **Academic Session:** 2026–2027  

---

## 📌 Project Overview

This project provides an end-to-end analytical desktop dashboard and data processing pipeline designed to investigate the association between self-reported weekly study hours and student assessment marks across multiple academic courses.

### Key Capabilities:
- **Object-Oriented Record Architecture:** Encapsulation and strict field validation via the `StudentRecord` class.
- **Dynamic Letter Grade Mapping:** Standardized conversion of marks (0–100) into letter grades: `A` (70–100), `B` (60–<70), `C` (50–<60), `D` (40–<50), and `F` (<40).
- **Array-Based Numerical Dispersion (NumPy):** Percentile computation ($Q_1, Q_3$), median, standard deviation, and Interquartile Range ($IQR = Q_3 - Q_1$) outlier detection ($k = 1.5$).
- **Course Group-by Aggregation (Pandas):** Per-course statistical aggregation across Biology, Business, Computing, and Maths cohorts.
- **Parametric & Non-Parametric Associations (SciPy):** Comparison of Pearson's correlation ($r$) and Spearman's rank correlation ($\rho$) before and after outlier removal.
- **Interactive Desktop Graphical Dashboard (Tkinter / ttk):** 
  - Dynamic KPI metric cards (Students count, Mean score, Median score, Mean hours, Outlier count).
  - Multi-tabbed views (Scatter plot with dual linear fits, Histograms & Grade bars, Course comparison, Treeview record viewer with outlier highlighting, and Automated written analysis).
  - File controls (Open CSV, Use sample data, Course filter combobox, Adjustable IQR threshold, Outlier toggle, and Export filtered CSV).
- **Methodological Safeguard:** Explicit emphasis that **correlation does not imply causation**, highlighting confounding variables such as prior preparation, attendance, and self-reporting bias.

---

## 🗂️ Repository Structure

```text
student_performance_dashboard/
│
├── student_dashboard.py              # Main dashboard application (Tkinter GUI + CLI runner)
├── student_dashboard_idle.py         # IDLE-optimized launcher (Run -> Run Module / F5)
├── student_record.py                 # StudentRecord class, score validation, and grade mapping
├── generate_data.py                  # CSV loading, row validation, and dataset generation
├── test_student_dashboard.py         # Automated unit test suite (9 test cases covering Section 7)
│
├── student_records.csv               # 125-row reproducible dataset (123 valid + 2 rejected test rows)
│
├── figures/                          # High-resolution generated analytical plots
│   ├── score_and_grade_distribution.png  # Figure 1: Score histogram and grade distribution
│   ├── study_hours_vs_score_scatter.png  # Figure 2: Study hours vs score with dual linear fits
│   ├── course_performance_comparison.png # Course-wise average score and study hours
│   └── iem_logo.png                      # Institutional emblem for project report
│
├── build_report_docx.py              # Automated generator for the Word (.docx) project report
├── Student_Performance_Dashboard_Report.docx  # Final laboratory report formatted to academic standards
├── .gitignore                        # Git exclusion rules for Python caches and temporary files
└── README.md                         # Project documentation, execution guide, and viva preparation
```

---


## 📊 Dataset Schema & Verification Summary

### Input Headers
The CSV parser enforces the following required column headers:
`student_id,course,study_hours,score`

### Cohort Summary (Preloaded Demonstration Sample)
| Metric / Indicator | Observed Value |
| :--- | :--- |
| **Total Input Rows** | 125 rows |
| **Valid Ingested Records** | 123 records |
| **Rejected Rows (Sanitization)** | 2 rows (Row 124: score 140.0; Row 125: blank study hours) |
| **Average Assessment Score** | 60.70 / 100 |
| **Median Assessment Score** | 60.80 / 100 |
| **Sample Standard Deviation** | 14.64 |
| **Mean Weekly Study Hours** | 12.80 hours/week |
| **Score Quartiles ($Q_1$ / $Q_3$)** | 52.35 / 70.00 |
| **Score Interquartile Range ($IQR$)** | 17.65 |
| **Flagged Outliers ($k = 1.5$)** | 4 records (3.3%) |

### Course-Wise Breakdown
| Course | Students ($N$) | Mean Score | Mean Weekly Study Hours |
| :--- | :---: | :---: | :---: |
| **Biology** | 35 | 62.48 | 12.92 hrs |
| **Business** | 21 | 61.14 | 11.35 hrs |
| **Computing** | 40 | 57.53 | 11.50 hrs |
| **Maths** | 27 | 62.74 | 15.69 hrs |

### Correlation & Outlier Sensitivity
| Metric | All Valid Records ($N = 123$) | Without Flagged Outliers ($N = 119$) |
| :--- | :---: | :---: |
| **Pearson's Correlation ($r$)** | **0.308** | **0.651** |
| **Spearman's Rank Correlation ($\rho$)** | **0.603** | **0.665** |

> **Key Observation:** Excluding the 4 extreme records (such as high study hours with low score) increases Pearson's $r$ from 0.308 to 0.651. Spearman's rank correlation demonstrates greater robustness (0.603 to 0.665), proving that while an underlying monotonic trend exists, individual unusual records strongly dictate linear slope estimates.

---

## 🧪 Unit Testing Matrix (Section 7)

| Test Case | Expected Behaviour | Observed Status |
| :--- | :--- | :--- |
| **1. Sample startup** | Ingest 125 rows; accept 123 valid and reject 2 invalid | `PASSED` (123 accepted, 2 rejected) |
| **2. Invalid score (140)** | Score > 100 or < 0 raises `ValueError` | `PASSED` (Row 124 rejected) |
| **3. Blank study hours** | Non-numeric or missing study hours rejected | `PASSED` (Row 125 rejected) |
| **4. Default IQR ($k=1.5$)** | Detect extreme measurements in hours or scores | `PASSED` (Exactly 4 flagged: S065, S088, S901, S902) |
| **5. Course selector** | Filter by course and recompute descriptive stats | `PASSED` (Verified for all 4 courses) |
| **6. CSV import handling** | Detect malformed headers using `csv.DictReader` | `PASSED` (`ValueError` on corrupt schema) |
| **7. Hide outliers filter** | Filter dataset to 119 clean observations | `PASSED` (Pearson $r$ increases as expected) |
| **8. Export filtered CSV** | Write current filtered selection to CSV | `PASSED` (Lossless export/reload verified) |
| **9. Grade mapping** | Accurate thresholding (A: 70-100, B: 60-69, C: 50-59, D: 40-49, F: <40) | `PASSED` (All boundary conditions verified) |

---
