"""
Student Performance Dashboard - IDLE Launcher
=============================================
IDLE-friendly launch script for the Student Performance and Study-Hours Dashboard.

Usage:
1. Open this file in Python IDLE:
   File -> Open -> student_dashboard_idle.py
2. Press F5 (or Run -> Run Module).
3. The interactive Tkinter dashboard window will launch automatically.
"""

import os
import sys

# Ensure current directory is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from student_dashboard import Dashboard, DEFAULT_CSV_PATH

if __name__ == "__main__":
    print("Launching Student Performance and Study-Hours Dashboard...")
    Dashboard.launch(DEFAULT_CSV_PATH)
