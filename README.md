# Student Performance and Study-Hours Dashboard

> **Python Programming Laboratory Project**  
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

## ⚙️ Installation & Requirements

### 1. Prerequisites
- Python 3.10, 3.11, or 3.14
- Standard desktop graphical support (Tkinter is included with standard Windows Python installers).

### 2. Install Required Third-Party Packages
Open PowerShell, Command Prompt, or Windows Terminal:
```bash
py -m pip install numpy pandas matplotlib scipy python-docx
```
*(Or use `python -m pip install numpy pandas matplotlib scipy python-docx`)*

---

## 🚀 How to Run the Project

### Option A: Running in Python IDLE (Recommended for Lab Viva)
1. Launch **Python IDLE**.
2. Click **File → Open...** and navigate to `student_dashboard_idle.py`.
3. Press **F5** (or click **Run → Run Module**).
4. The desktop GUI dashboard window opens automatically with the preloaded 125-row dataset.

### Option B: Running from Terminal / Command Prompt
```bash
# Launch interactive Tkinter Desktop GUI
py student_dashboard.py

# Or run non-interactively in CLI mode and regenerate figure plots
py student_dashboard.py --cli --save-figures
```

### Option C: Running the Automated Test Suite
To verify all 8 test cases specified in the project report (Section 7):
```bash
py test_student_dashboard.py
```
*Expected Result:*
```text
Ran 9 tests in 0.522s
OK
```

### Option D: Regenerating the Word (.docx) Project Report
```bash
py build_report_docx.py
```
*Outputs:* `Student_Performance_Dashboard_Report.docx`

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

## 👥 Individual Group Contributions

For laboratory assessment and individual viva evaluation, responsibilities across team members are partitioned as follows:

| Member Name | Role | Specific Module Contributions |
| :--- | :--- | :--- |
| **Student 1 (Lead Developer)** | OOP Architecture & Ingestion | Developed `student_record.py` (`StudentRecord` class, `is_valid_score()`, `score_to_grade()`) and input validation pipeline. |
| **Student 2** | Statistical Modeling & NumPy | Implemented `iqr_mask()`, percentile evaluations ($Q_1, Q_3$), dispersion metrics, and outlier detection logic. |
| **Student 3** | Data Aggregation & SciPy | Handled course-wise group-by aggregations in Pandas and Pearson/Spearman correlation sensitivity comparisons in `student_dashboard.py`. |
| **Student 4** | Data Visualization & Matplotlib | Designed embedded Matplotlib figures (`draw_scatter()`, `draw_scores()`, `draw_courses()`) with dual regression lines and color palettes. |
| **Student 5** | GUI Engineering & Documentation | Engineered the Tkinter desktop GUI (`Dashboard` class), metric cards, Treeview record viewer, unit test suite, and the final Word report. |

---

## 🎓 Viva Voce Preparation (Sample Questions & Answers)

1. **Q: Why derive letter grades dynamically rather than saving them in the CSV file?**  
   *A:* Storing derived data introduces redundant state and risks inconsistencies if raw marks are modified. Computing grades dynamically via `score_to_grade()` ensures single-source-of-truth integrity.

2. **Q: How does the Interquartile Range (IQR) rule identify outliers?**  
   *A:* $IQR = Q_3 - Q_1$. Thresholds are set at $Q_1 - 1.5 \times IQR$ (lower fence) and $Q_3 + 1.5 \times IQR$ (upper fence). Any score or reported study hour outside this interval is flagged as statistically extreme.

3. **Q: Why does Pearson's correlation jump from 0.308 to 0.651 when 4 outliers are removed?**  
   *A:* Pearson's $r$ evaluates linear distance from the mean. Outliers with extreme coordinates (e.g., student S901 studying 45 hours but scoring only 22 marks) exert high leverage on the covariance sum, dampening the estimated linear slope.

4. **Q: Why is Spearman's rank correlation ($\rho$) more stable than Pearson's ($r$)?**  
   *A:* Spearman replaces raw numeric values with their relative ordinal ranks (1st, 2nd, 3rd, ...). Extreme distances are compressed into sequential integers, making rank correlation robust against heavy-tailed outliers.

5. **Q: Can we conclude that studying more hours causes higher exam scores?**  
   *A:* No. Observational correlation does not establish causality. Confounding variables such as student prior knowledge, attendance, effective study methodologies, and self-reporting bias readily account for performance variations.

---

## 🌐 Step-by-Step GitHub Repository Setup & Push Guide

To submit your project via GitHub and provide open access:

### Method 1: Using the Command Line (Git)
If `git` is installed on your computer:
```bash
# 1. Navigate to the project directory
cd "C:\Users\Anoushka\.gemini\antigravity\scratch\student_performance_dashboard"

# 2. Initialize local repository
git init

# 3. Stage all source files, documentation, and the Word report
git add .

# 4. Commit files
git commit -m "Initial commit: Student Performance and Study-Hours Dashboard with full report and tests"

# 5. Create a new Public repository on github.com (e.g. named 'student-performance-dashboard')

# 6. Link and push to your remote GitHub repository
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/student-performance-dashboard.git
git branch -M main
git push -u origin main
```

### Method 2: Uploading via GitHub Web Interface (No Git installation needed)
1. Log into your account at [github.com](https://github.com).
2. Click the **+** icon in the top right corner and select **New repository**.
3. Repository name: `student-performance-dashboard`.
4. Select **Public** (Open Access).
5. Leave "Add a README file" unchecked (you already have a complete README).
6. Click **Create repository**.
7. On the next screen, click the link: **"uploading an existing file"**.
8. Drag and drop all files and folders from:
   `C:\Users\Anoushka\.gemini\antigravity\scratch\student_performance_dashboard\`
   (including `student_dashboard.py`, `student_record.py`, `generate_data.py`, `test_student_dashboard.py`, `student_records.csv`, `Student_Performance_Dashboard_Report.docx`, `README.md`, and the `figures/` folder).
9. Enter commit message: `Submit source code, test suite, dataset, and docx report`.
10. Click **Commit changes**.

### Submitting to the Google Sheet
1. Copy your repository URL:  
   `https://github.com/<YOUR_GITHUB_USERNAME>/student-performance-dashboard`
2. Open the attached Google Sheet.
3. Paste your public repository URL in the designated submission cell under Project 3.
