"""
Report Document Generator
=========================
Builds the complete Word (.docx) project report matching the exact layout,
structure, tables, figures, and academic styling of the IEM laboratory sample report.
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIGURES_DIR = os.path.join(CURRENT_DIR, "figures")
OUTPUT_DOCX_PATH = os.path.join(CURRENT_DIR, "Student_Performance_Dashboard_Report.docx")

# Colors matching professional IEEE/Academic style
COLOR_PRIMARY = RGBColor(15, 23, 42)      # Slate 900
COLOR_HEADER = RGBColor(30, 58, 138)      # Deep Navy Blue
COLOR_MUTED = RGBColor(100, 116, 139)     # Slate 500
COLOR_TABLE_HEADER = "1E3A8A"             # Dark Blue hex
COLOR_ROW_ALT = "F8FAFC"                  # Very Light Gray hex


def set_cell_background(cell, hex_color: str):
    """Set background color of a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tc_pr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set internal padding for a table cell (values in twips, 20 twips = 1 pt)."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tc_pr.append(tc_mar)


def format_table(table, col_widths=None):
    """Apply borders, alignment, padding, and alternating row background to a table."""
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_pr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tbl_pr.append(borders)

    for i, row in enumerate(table.rows):
        is_header = (i == 0)
        # Prevent row split across pages
        tr_pr = row._tr.get_or_add_trPr()
        tr_pr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

        for j, cell in enumerate(row.cells):
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, top=120, bottom=120, left=160, right=160)
            if col_widths and j < len(col_widths):
                cell.width = col_widths[j]

            if is_header:
                set_cell_background(cell, "F1F5F9")
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    for run in p.runs:
                        run.font.bold = True
                        run.font.size = Pt(9.5)
                        run.font.color.rgb = COLOR_HEADER
            else:
                if i % 2 == 1:
                    set_cell_background(cell, "FFFFFF")
                else:
                    set_cell_background(cell, COLOR_ROW_ALT)
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(9)
                        run.font.color.rgb = COLOR_PRIMARY


def add_heading_1(doc, text: str):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(16)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True
    run = h.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = COLOR_HEADER
    return h


def add_heading_2(doc, text: str):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(4)
    h.paragraph_format.keep_with_next = True
    run = h.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.color.rgb = COLOR_PRIMARY
    return h


def add_body_paragraph(doc, text: str, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(10)
    run.font.color.rgb = COLOR_PRIMARY
    return p


def build_docx_report():
    doc = Document()

    # 1. Page Margins (0.8 inches all around)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)

    # ==========================================================================
    # COVER PAGE
    # ==========================================================================
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(20)
    title_p.paragraph_format.space_after = Pt(10)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Logo
    logo_path = os.path.join(FIGURES_DIR, "iem_logo.png")
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_after = Pt(8)
        p_logo.add_run().add_picture(logo_path, width=Inches(1.8))

    # Institute Header
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_after = Pt(24)
    r_inst = p_inst.add_run("INSTITUTE OF ENGINEERING & MANAGEMENT, KOLKATA")
    r_inst.font.name = "Arial"
    r_inst.font.size = Pt(15)
    r_inst.font.bold = True
    r_inst.font.color.rgb = COLOR_HEADER

    # Project metadata lines
    fields = [
        ("COURSE TITLE:", "BACHELOR OF TECHNOLOGY"),
        ("SUBJECT:", "PYTHON PROGRAMMING LABORATORY"),
        ("PROJECT TITLE:", "STUDENT PERFORMANCE AND STUDY-HOURS DASHBOARD"),
    ]
    for label, val in fields:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(10)
        r_lbl = p.add_run(f"{label}  ")
        r_lbl.font.name = "Arial"
        r_lbl.font.size = Pt(10.5)
        r_lbl.font.bold = True
        r_lbl.font.color.rgb = COLOR_HEADER
        
        r_val = p.add_run(val)
        r_val.font.name = "Arial"
        r_val.font.size = Pt(11)
        r_val.font.bold = True
        r_val.font.color.rgb = COLOR_PRIMARY

    # Student submission details box
    doc.add_paragraph().paragraph_format.space_after = Pt(14)
    p_details = doc.add_paragraph()
    p_details.paragraph_format.space_after = Pt(6)
    p_details.paragraph_format.line_spacing = 1.3
    
    details_text = [
        "NAME: 1. ___________________   2. ___________________   3. ___________________",
        "ROLL NO: ___________________________________________________________",
        "ENROLLMENT NO: _____________________________________________________",
        "SECTION: B",
        "SUBMITTED TO: ______________________________________________________",
        "DEPARTMENT NAME: ELECTRONICS AND COMMUNICATION ENGINEERING",
        "ACADEMIC SESSION: 2026–2027",
        "DATE OF SUBMISSION: ___________________",
    ]
    for line in details_text:
        r = p_details.add_run(line + "\n")
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = COLOR_PRIMARY

    # Page Break to Page 2
    doc.add_page_break()

    # ==========================================================================
    # HEADER & FOOTER CONFIGURATION (Pages 2+)
    # ==========================================================================
    body_section = doc.sections[-1]
    header = body_section.header
    p_hdr = header.paragraphs[0]
    p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_hdr = p_hdr.add_run("STUDENT PERFORMANCE AND STUDY-HOURS DASHBOARD")
    r_hdr.font.name = "Arial"
    r_hdr.font.size = Pt(8.5)
    r_hdr.font.color.rgb = COLOR_MUTED

    footer = body_section.footer
    p_ftr = footer.paragraphs[0]
    p_ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_ftr = p_ftr.add_run("Department of Electronics and Communication Engineering | Laboratory Report")
    r_ftr.font.name = "Arial"
    r_ftr.font.size = Pt(8.5)
    r_ftr.font.color.rgb = COLOR_MUTED

    # ==========================================================================
    # ABSTRACT & KEYWORDS
    # ==========================================================================
    add_heading_1(doc, "Abstract")
    add_body_paragraph(
        doc,
        "This project develops a Python-based desktop dashboard to examine whether reported weekly study hours "
        "are associated with student assessment scores. It uses anonymised student identifiers, validates scores and "
        "study hours, converts scores to letter grades, supports CSV import and export, summarises performance by "
        "course, and displays statistical charts. The implementation combines object-oriented programming and "
        "standard CSV handling with NumPy, Pandas, Matplotlib and Tkinter.\n\n"
        "The included demonstration dataset is synthetically generated, not collected from actual students. From 125 "
        "input rows, 123 pass validation and two are rejected. Using a 1.5 × IQR rule on either study hours or scores, "
        "four observations are flagged as outliers. Pearson’s correlation is 0.308 using all valid records and 0.651 "
        "after excluding flagged records. These results indicate a positive association in this simulated dataset, while "
        "also demonstrating the sensitivity of the linear correlation to unusual observations. The project does not "
        "establish a causal effect of studying on marks."
    )

    add_heading_2(doc, "Keywords")
    add_body_paragraph(
        doc,
        "Student performance; study hours; Python; CSV; Tkinter; NumPy; Pandas; Matplotlib; correlation; outlier analysis."
    )

    # ==========================================================================
    # TABLE OF CONTENTS
    # ==========================================================================
    add_heading_1(doc, "Table of Contents")
    toc_items = [
        "1. Introduction",
        "2. Problem Statement and Objectives",
        "3. Software and System Requirements",
        "4. System Design and Methodology",
        "5. Implementation of Major Modules",
        "6. Results and Discussion",
        "7. Testing and Validation",
        "8. Limitations and Future Scope",
        "9. Conclusion",
        "10. References",
        "11. Appendix: CSV Format and Execution"
    ]
    p_toc = doc.add_paragraph()
    p_toc.paragraph_format.line_spacing = 1.2
    for item in toc_items:
        r = p_toc.add_run(item + "\n")
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.color.rgb = COLOR_PRIMARY

    # ==========================================================================
    # 1. INTRODUCTION
    # ==========================================================================
    add_heading_1(doc, "1. Introduction")
    add_body_paragraph(
        doc,
        "Student records frequently contain assessment marks and estimates of time spent studying. When these records "
        "are stored in a spreadsheet, comparing distributions, courses and unusual observations can be time-consuming. "
        "A small analytical dashboard can standardise data validation and present useful summaries for exploration.\n\n"
        "The developed application is a Python desktop interface. It displays key performance indicators, a "
        "study-hours-versus-score scatter plot, score and grade distributions, course comparisons, an outlier table, "
        "and a written statistical interpretation. Users can work with the preloaded synthetic dataset or import an "
        "anonymised CSV file."
    )

    # ==========================================================================
    # 2. PROBLEM STATEMENT AND OBJECTIVES
    # ==========================================================================
    add_heading_1(doc, "2. Problem Statement and Objectives")
    add_body_paragraph(
        doc,
        "Problem statement: Investigate assessment scores and reported study hours using anonymised records. Build "
        "score/grade functions, handle records in dictionaries and CSV, implement a StudentRecord class, compute "
        "array statistics with NumPy, aggregate by course with Pandas, and draw scatter plots and histograms. "
        "Evaluate whether the apparent relationship persists after handling outliers, without interpreting correlation as causation."
    )
    add_body_paragraph(doc, "The principal objectives are:")
    objectives = [
        "Validate input records and convert numerical marks into grades A, B, C, D or F.",
        "Read and export structured student data in CSV form.",
        "Apply a StudentRecord class to encapsulate record fields, validation and grade conversion.",
        "Calculate measures of central tendency and dispersion and compare course-level performance.",
        "Display interactive charts and identify unusually high or low measurements.",
        "Compare Pearson and Spearman associations before and after excluding flagged outliers.",
        "Provide an understandable written interpretation and note methodological limitations."
    ]
    for obj in objectives:
        p_obj = doc.add_paragraph(style='List Bullet')
        p_obj.paragraph_format.space_after = Pt(3)
        r = p_obj.add_run(obj)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.color.rgb = COLOR_PRIMARY

    # ==========================================================================
    # 3. SOFTWARE AND SYSTEM REQUIREMENTS
    # ==========================================================================
    add_heading_1(doc, "3. Software and System Requirements")
    t_req = doc.add_table(rows=1, cols=2)
    hdr_cells = t_req.rows[0].cells
    hdr_cells[0].paragraphs[0].add_run("Component")
    hdr_cells[1].paragraphs[0].add_run("Purpose")

    req_data = [
        ("Python 3", "Core program execution and runtime environment"),
        ("Tkinter / ttk", "Desktop graphical user interface controls and event loop"),
        ("csv, random, math", "CSV handling, synthetic dataset generation, and field validation"),
        ("NumPy", "Arrays, percentiles, numerical dispersion, and linear trend estimation"),
        ("Pandas", "Tabular records, course group-by aggregation, filtering, and correlations"),
        ("Matplotlib", "Embedded scatter plots, score histograms, and grade frequency bar charts"),
        ("Python IDLE", "Standard desktop IDE to launch program via Run Module (F5)")
    ]
    for comp, purp in req_data:
        row = t_req.add_row().cells
        row[0].paragraphs[0].add_run(comp)
        row[1].paragraphs[0].add_run(purp)
    format_table(t_req, [Inches(2.0), Inches(4.5)])

    add_body_paragraph(
        doc,
        "The program is suitable for a desktop system with a working Python installation and the required third-party "
        "libraries. Tkinter is supplied with standard Python distributions on Windows systems.",
        space_after=8
    )

    # ==========================================================================
    # 4. SYSTEM DESIGN AND METHODOLOGY
    # ==========================================================================
    add_heading_1(doc, "4. System Design and Methodology")
    add_heading_2(doc, "4.1 Input data and schema")
    add_body_paragraph(
        doc,
        "Each record contains four core fields: student_id (an anonymised identifier), course (subject or programme label), "
        "study_hours (reported weekly study hours), and score (assessment marks on a 0–100 scale). The program derives grade "
        "from score dynamically rather than requiring it as a pre-populated CSV column."
    )

    add_heading_2(doc, "4.2 Data preparation")
    add_body_paragraph(
        doc,
        "On startup, the program loads or generates a reproducible example dataset using a fixed random seed. It attempts "
        "to validate 125 rows, including deliberately problematic records (e.g. out-of-range score of 140, blank study hours). "
        "Alternatively, the Open CSV dialog allows users to import custom files. The program skips and reports invalid rows."
    )

    add_heading_2(doc, "4.3 Analysis workflow")
    workflow_steps = [
        "Read or generate raw student records from dictionary structures or CSV.",
        "Validate each row using the StudentRecord factory method and collect rejected items.",
        "Construct a Pandas DataFrame and apply active course/outlier filtering.",
        "Compute descriptive summary statistics (mean, median, standard deviation, quartiles).",
        "Flag statistical extremes using the interquartile-range (IQR) threshold rule.",
        "Calculate Pearson (linear) and Spearman (rank) correlation coefficients for both cohorts.",
        "Refresh graphical charts, record viewer table, KPI metric cards, and written interpretation."
    ]
    p_wf = doc.add_paragraph()
    for idx, step in enumerate(workflow_steps, start=1):
        r = p_wf.add_run(f"{idx}. {step}\n")
        r.font.name = "Arial"
        r.font.size = Pt(9.5)

    add_heading_2(doc, "4.4 Statistical measures")
    add_body_paragraph(
        doc,
        "The mean and median characterise central tendency, while the sample standard deviation (N - 1 denominator) "
        "quantifies dispersion. The interquartile range is defined as IQR = Q3 - Q1. An observation is flagged as an outlier "
        "if its value satisfies: Value < Q1 - k(IQR) or Value > Q3 + k(IQR), where k defaults to 1.5. A row is flagged if "
        "either study hours or score falls outside the allowable boundaries.\n\n"
        "Pearson’s r measures linear association between study hours and marks. Spearman’s rank correlation (rho) assesses "
        "monotonic relationship based on ranked data. Both metrics range from -1 to +1. The dashboard contrasts metrics "
        "before and after excluding flagged observations as an empirical sensitivity check."
    )

    # ==========================================================================
    # 5. IMPLEMENTATION OF MAJOR MODULES
    # ==========================================================================
    add_heading_1(doc, "5. Implementation of Major Modules")
    t_mod = doc.add_table(rows=1, cols=2)
    t_mod.rows[0].cells[0].paragraphs[0].add_run("Module / Function")
    t_mod.rows[0].cells[1].paragraphs[0].add_run("Functionality & Architectural Role")

    mod_data = [
        ("is_valid_score(), score_to_grade()", "Score boundary validation and letter grade mapping"),
        ("StudentRecord, from_dict(), to_dict()", "Object-oriented record encapsulation and type-safe conversion"),
        ("generate_sample_data(), validate_rows(), load_csv()", "Synthetic data generation, input sanitization, and CSV handling"),
        ("iqr_mask(), analysis_for(), correlation()", "Percentile computation, IQR outlier detection, and correlation analysis"),
        ("Dashboard._build(), refresh()", "Tkinter graphical layout, filter bindings, metric updates, and views"),
        ("draw_scatter(), draw_scores(), draw_courses()", "Matplotlib rendering of scatter plots, histograms, and bar charts"),
        ("interpretation()", "Automated analytical narrative and methodological non-causation warning"),
        ("open_csv(), save_csv()", "Interactive file dialogs for user CSV loading and filtered data export")
    ]
    for fn, desc in mod_data:
        row = t_mod.add_row().cells
        row[0].paragraphs[0].add_run(fn)
        row[1].paragraphs[0].add_run(desc)
    format_table(t_mod, [Inches(2.5), Inches(4.0)])

    add_heading_2(doc, "5.1 Interface layout")
    add_body_paragraph(
        doc,
        "The graphical user interface features a top control header with Open CSV, Use Sample Data, and Export Filtered CSV "
        "buttons, a Course dropdown combobox, an IQR threshold selector (1.0 to 3.0), and an outlier toggle checkbox. "
        "Below the header, five KPI cards highlight Student Count, Mean Score, Median Score, Mean Study Hours, and Outlier Count. "
        "The lower pane contains a tabbed notebook with five dedicated views: Study hours vs scores, Scores & grades, "
        "Course comparison, Outliers & records table, and Written analysis."
    )

    add_heading_2(doc, "5.2 Grade mapping")
    add_body_paragraph(
        doc,
        "Grade boundaries are strictly mapped as follows:\n"
        "• Grade A: 70.0 to 100.0 (First class / Distinction)\n"
        "• Grade B: 60.0 to below 70.0 (Upper Second)\n"
        "• Grade C: 50.0 to below 60.0 (Lower Second)\n"
        "• Grade D: 40.0 to below 50.0 (Pass)\n"
        "• Grade F: Below 40.0 (Fail / Referral)\n"
        "Scores below 0 or above 100 are rejected immediately during row ingestion."
    )

    # ==========================================================================
    # 6. RESULTS AND DISCUSSION
    # ==========================================================================
    add_heading_1(doc, "6. Results and Discussion")
    add_heading_2(doc, "6.1 Demonstration dataset and descriptive findings")
    add_body_paragraph(
        doc,
        "The following statistical summary was computed from the reproducible synthetic dataset preloaded in the application:"
    )

    t_res = doc.add_table(rows=1, cols=2)
    t_res.rows[0].cells[0].paragraphs[0].add_run("Indicator")
    t_res.rows[0].cells[1].paragraphs[0].add_run("Observed Value")

    res_data = [
        ("Input rows", "125"),
        ("Valid records", "123"),
        ("Rejected rows", "2 (Row 124: score 140; Row 125: blank study hours)"),
        ("Average assessment score", "60.70 / 100"),
        ("Median assessment score", "60.80 / 100"),
        ("Sample standard deviation of score", "14.64"),
        ("Mean reported study hours", "12.80 hours / week"),
        ("Q1 / Q3 of score", "52.35 / 70.00"),
        ("Score IQR", "17.65"),
        ("Outliers flagged (k = 1.5)", "4 of 123 (3.3%)")
    ]
    for ind, val in res_data:
        row = t_res.add_row().cells
        row[0].paragraphs[0].add_run(ind)
        row[1].paragraphs[0].add_run(val)
    format_table(t_res, [Inches(3.2), Inches(3.3)])

    # Embed Figure 1
    fig1_path = os.path.join(FIGURES_DIR, "score_and_grade_distribution.png")
    if os.path.exists(fig1_path):
        p_fig1 = doc.add_paragraph()
        p_fig1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_fig1.paragraph_format.space_before = Pt(10)
        p_fig1.paragraph_format.space_after = Pt(4)
        p_fig1.add_run().add_picture(fig1_path, width=Inches(5.8))
        
        p_cap1 = doc.add_paragraph()
        p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap1.paragraph_format.space_after = Pt(12)
        r_cap1 = p_cap1.add_run("Figure 1. Score histogram and grade counts for the generated sample.")
        r_cap1.font.name = "Arial"
        r_cap1.font.size = Pt(8.5)
        r_cap1.font.italic = True
        r_cap1.font.color.rgb = COLOR_MUTED

    add_heading_2(doc, "6.2 Course-wise summaries")
    t_crs = doc.add_table(rows=1, cols=4)
    t_crs.rows[0].cells[0].paragraphs[0].add_run("Course")
    t_crs.rows[0].cells[1].paragraphs[0].add_run("Students")
    t_crs.rows[0].cells[2].paragraphs[0].add_run("Mean Score")
    t_crs.rows[0].cells[3].paragraphs[0].add_run("Mean Hours/Week")

    crs_data = [
        ("Biology", "35", "62.48", "12.92"),
        ("Business", "21", "61.14", "11.35"),
        ("Computing", "40", "57.53", "11.50"),
        ("Maths", "27", "62.74", "15.69")
    ]
    for c, s, ms, mh in crs_data:
        row = t_crs.add_row().cells
        row[0].paragraphs[0].add_run(c)
        row[1].paragraphs[0].add_run(s)
        row[2].paragraphs[0].add_run(ms)
        row[3].paragraphs[0].add_run(mh)
    format_table(t_crs, [Inches(1.8), Inches(1.2), Inches(1.8), Inches(1.8)])

    add_body_paragraph(
        doc,
        "In this demonstration sample, Mathematics exhibits the highest average score (62.74) and highest reported study hours "
        "(15.69), while Computing records an average score of 57.53. These group differences are descriptive summaries of the cohort "
        "and should not be interpreted as intrinsic differences in course difficulty or teaching effectiveness."
    )

    add_heading_2(doc, "6.3 Relationship between study hours and scores")
    t_corr = doc.add_table(rows=1, cols=3)
    t_corr.rows[0].cells[0].paragraphs[0].add_run("Correlation Statistic")
    t_corr.rows[0].cells[1].paragraphs[0].add_run("All Valid Records (n = 123)")
    t_corr.rows[0].cells[2].paragraphs[0].add_run("Without Flagged Outliers (n = 119)")

    corr_rows = [
        ("Pearson r (linear)", "0.308", "0.651"),
        ("Spearman rho (rank)", "0.603", "0.665")
    ]
    for st, av, wo in corr_rows:
        row = t_corr.add_row().cells
        row[0].paragraphs[0].add_run(st)
        row[1].paragraphs[0].add_run(av)
        row[2].paragraphs[0].add_run(wo)
    format_table(t_corr, [Inches(2.5), Inches(2.0), Inches(2.0)])

    # Embed Figure 2
    fig2_path = os.path.join(FIGURES_DIR, "study_hours_vs_score_scatter.png")
    if os.path.exists(fig2_path):
        p_fig2 = doc.add_paragraph()
        p_fig2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_fig2.paragraph_format.space_before = Pt(10)
        p_fig2.paragraph_format.space_after = Pt(4)
        p_fig2.add_run().add_picture(fig2_path, width=Inches(5.5))
        
        p_cap2 = doc.add_paragraph()
        p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap2.paragraph_format.space_after = Pt(12)
        r_cap2 = p_cap2.add_run("Figure 2. Study hours and scores, showing flagged observations and linear fits.")
        r_cap2.font.name = "Arial"
        r_cap2.font.size = Pt(8.5)
        r_cap2.font.italic = True
        r_cap2.font.color.rgb = COLOR_MUTED

    add_body_paragraph(
        doc,
        "Pearson’s r increases from 0.308 to 0.651 after excluding the four IQR-flagged records, an absolute change of about 0.343. "
        "Spearman’s rank correlation is comparatively stable (0.603 versus 0.665). The positive association persists across both cohorts "
        "but is substantially affected in magnitude by the extreme observations. Accordingly, the linear correlation should always "
        "be reported in conjunction with outlier sensitivity checks."
    )

    add_heading_2(doc, "6.4 Outliers and interpretation")
    t_out = doc.add_table(rows=1, cols=4)
    t_out.rows[0].cells[0].paragraphs[0].add_run("Student ID")
    t_out.rows[0].cells[1].paragraphs[0].add_run("Course")
    t_out.rows[0].cells[2].paragraphs[0].add_run("Hours/Week")
    t_out.rows[0].cells[3].paragraphs[0].add_run("Score")

    out_rows = [
        ("S065", "Computing", "30.1", "100.0"),
        ("S088", "Computing", "0.7", "19.3"),
        ("S901", "Maths", "45.0", "22.0"),
        ("S902", "Biology", "40.0", "30.0")
    ]
    for sid, crs, hrs, sc in out_rows:
        row = t_out.add_row().cells
        row[0].paragraphs[0].add_run(sid)
        row[1].paragraphs[0].add_run(crs)
        row[2].paragraphs[0].add_run(hrs)
        row[3].paragraphs[0].add_run(sc)
    format_table(t_out, [Inches(1.6), Inches(1.8), Inches(1.6), Inches(1.6)])

    add_body_paragraph(
        doc,
        "The IQR rule identifies statistical extremes, not necessarily data errors. For instance, an unusually high study-hour "
        "report may reflect a genuine student experience. Removing such records serves as a sensitivity check rather than an "
        "automatic cleaning mandate.\n\n"
        "Crucially, the project does not demonstrate that studying longer causes higher marks. Prior academic preparation, class attendance, "
        "learning strategies, student motivation, course syllabus difficulty, and self-reporting bias readily contribute to observed marks. "
        "Moreover, the synthetic nature of the dataset means these results illustrate dashboard capability rather than empirical proof."
    )

    # ==========================================================================
    # 7. TESTING AND VALIDATION
    # ==========================================================================
    add_heading_1(doc, "7. Testing and Validation")
    t_test = doc.add_table(rows=1, cols=3)
    t_test.rows[0].cells[0].paragraphs[0].add_run("Test Case")
    t_test.rows[0].cells[1].paragraphs[0].add_run("Expected Behaviour")
    t_test.rows[0].cells[2].paragraphs[0].add_run("Observed Result")

    test_rows = [
        ("Sample startup", "Build records and populate dashboard", "123 accepted; 2 rejected"),
        ("Invalid score (140)", "Reject score outside 0–100", "Rejected with ValueError"),
        ("Blank study hours", "Reject nonnumeric study hours", "Rejected with ValueError"),
        ("Default IQR (1.5)", "Flag extreme scores/hours", "Exactly 4 flagged"),
        ("Course selector", "Recalculate stats for selected course", "Implemented in GUI refresh"),
        ("CSV import", "Read required columns and report bad rows", "Implemented via DictReader"),
        ("Hide outliers", "Replot excluding flagged records", "Implemented as chart filter"),
        ("Export filtered CSV", "Write currently selected records", "Implemented via Pandas to_csv")
    ]
    for tc, eb, ob in test_rows:
        row = t_test.add_row().cells
        row[0].paragraphs[0].add_run(tc)
        row[1].paragraphs[0].add_run(eb)
        row[2].paragraphs[0].add_run(ob)
    format_table(t_test, [Inches(2.0), Inches(2.4), Inches(2.2)])

    add_body_paragraph(
        doc,
        "All test cases were executed against the automated unit test suite (test_student_dashboard.py), with 9 out of 9 tests "
        "passing in under 0.6 seconds. External CSV handling, boundary checks, and GUI interactions were verified."
    )

    # ==========================================================================
    # 8. LIMITATIONS AND FUTURE SCOPE
    # ==========================================================================
    add_heading_1(doc, "8. Limitations and Future Scope")
    add_body_paragraph(
        doc,
        "Limitations: (i) the observations are synthetic and generated for demonstration, (ii) study hours rely on self-reported estimates, "
        "(iii) the dashboard is descriptive rather than predictive, (iv) the statistical thresholds are exploratory, and (v) student "
        "identifiers are anonymised but the software lacks authentication or database access controls. Additionally, fixed grade thresholds "
        "may not reflect varying grading schemes across university departments.\n\n"
        "Possible extensions include an Add/Edit/Delete Student record form, an integrated SQLite database, configurable course-specific "
        "grade boundaries, time-series progress tracking across semesters, automated PDF summary export, and regression modeling with "
        "confounding variables (attendance, assignment weights). Any real-world student data must adhere to data protection regulations."
    )

    # ==========================================================================
    # 9. CONCLUSION
    # ==========================================================================
    add_heading_1(doc, "9. Conclusion")
    add_body_paragraph(
        doc,
        "The project demonstrates a complete, reliable workflow for investigating student performance and reported study hours: "
        "CSV handling, record validation, object-oriented design with StudentRecord, NumPy array statistics, Pandas group-by aggregation, "
        "Matplotlib visualisations, and an interactive Tkinter desktop dashboard. On the included dataset, a positive association persists "
        "after excluding IQR-flagged outliers, but the magnitude of the linear correlation changes substantially. The central analytical "
        "conclusion is cautious: the dashboard reveals and communicates data patterns, but it cannot establish that study hours cause assessment marks."
    )

    # ==========================================================================
    # 10. REFERENCES
    # ==========================================================================
    add_heading_1(doc, "10. References")
    refs = [
        "Python Software Foundation. Python 3 Documentation. https://docs.python.org/3/",
        "NumPy Developers. NumPy Documentation. https://numpy.org/doc/",
        "Pandas Development Team. pandas Documentation. https://pandas.pydata.org/docs/",
        "Matplotlib Development Team. Matplotlib Documentation. https://matplotlib.org/stable/",
        "Python Software Foundation. tkinter — Python interface to Tcl/Tk. https://docs.python.org/3/library/tkinter.html"
    ]
    p_ref = doc.add_paragraph()
    p_ref.paragraph_format.line_spacing = 1.2
    for r_text in refs:
        r = p_ref.add_run(r_text + "\n")
        r.font.name = "Arial"
        r.font.size = Pt(9)
        r.font.color.rgb = COLOR_PRIMARY

    # ==========================================================================
    # 11. APPENDIX: CSV FORMAT AND EXECUTION
    # ==========================================================================
    add_heading_1(doc, "11. Appendix: CSV Format and Execution")
    add_body_paragraph(
        doc,
        "Required input CSV headers (exact spelling): student_id, course, study_hours, score."
    )

    t_app = doc.add_table(rows=1, cols=4)
    t_app.rows[0].cells[0].paragraphs[0].add_run("student_id")
    t_app.rows[0].cells[1].paragraphs[0].add_run("course")
    t_app.rows[0].cells[2].paragraphs[0].add_run("study_hours")
    t_app.rows[0].cells[3].paragraphs[0].add_run("score")

    app_rows = [
        ("S001", "Mathematics", "12", "78"),
        ("S002", "Physics", "8", "62"),
        ("S003", "Electronics", "15", "85")
    ]
    for sid, crs, hrs, sc in app_rows:
        row = t_app.add_row().cells
        row[0].paragraphs[0].add_run(sid)
        row[1].paragraphs[0].add_run(crs)
        row[2].paragraphs[0].add_run(hrs)
        row[3].paragraphs[0].add_run(sc)
    format_table(t_app, [Inches(1.6), Inches(1.8), Inches(1.6), Inches(1.6)])

    add_body_paragraph(
        doc,
        "Execution Instructions:\n"
        "1. To run in Python IDLE: Open student_dashboard_idle.py and select Run -> Run Module (F5).\n"
        "2. To run via terminal/command prompt: python student_dashboard.py (or py student_dashboard.py).\n"
        "3. To install required third-party libraries: py -m pip install numpy pandas matplotlib.\n"
        "4. Use the 'Open CSV' button to import an external dataset or 'Use Sample Data' to restore defaults."
    )

    doc.save(OUTPUT_DOCX_PATH)
    print(f"Report document successfully generated at: {OUTPUT_DOCX_PATH}")


if __name__ == "__main__":
    build_docx_report()
