"""B03 kit - extends b01_kit for B03 tasks."""
import sys, os, json, pathlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b01_kit as K

# Override task/output dirs for B03
K.TASK = "B03"
ROOT = K.ROOT
RUN_ID = K.RUN_ID
K.OUT = ROOT / "outputs" / RUN_ID / "B03"
K.TMP = ROOT / "tmp" / RUN_ID / "B03"

from b01_kit import (
    Doc, dry_run, assert_gates, save_gates, render_case,
    contrast, d_e, check_palette, tool_call, append_jsonl,
    rel, now, ring, tw, pitch, fmt, esc, FONT
)
