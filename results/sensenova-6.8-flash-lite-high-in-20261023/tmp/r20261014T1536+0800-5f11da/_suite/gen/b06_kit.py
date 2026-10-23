"""B06 kit: Daily information redesign visualizations
Builds on b05_kit's UIDoc class with information design focus.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b05_kit as K5
from b05_kit import *

TASK = "B06"
b01_kit.TASK = "B06"
b01_kit.OUT = b01_kit.ROOT / "outputs" / b01_kit.RUN_ID / "B06"
b01_kit.TMP = b01_kit.ROOT / "tmp" / b01_kit.RUN_ID / "B06"
from b01_kit import render_case

# Color system for information design
BG_WHITE = "#FFFFFF"
BG_DARK = "#1A1A2E"
BG_LIGHT = "#F8F9FA"
TEXT_PRIMARY = "#1A1A2E"
TEXT_SECONDARY = "#6C757D"
TEXT_LIGHT = "#FFFFFF"

ACCENT_RED = "#E63946"
ACCENT_BLUE = "#457B9D"
ACCENT_GREEN = "#2A9D8F"
ACCENT_ORANGE = "#F4A261"
ACCENT_PURPLE = "#6A4C93"
ACCENT_YELLOW = "#E9C46A"

BORDER = "#DEE2E6"
DIVIDER = "#E9ECEF"

# Doc = UIDoc from b05_kit (same class, just re-exported)
Doc = K5.Doc

# Export dry_run, save_gates, assert_gates
from b01_kit import dry_run, save_gates, assert_gates

def render(case_id, doc, label, stem="final", extra=""):
    return render_case(case_id, doc, label, stem, extra)
