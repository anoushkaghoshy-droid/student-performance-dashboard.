

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
