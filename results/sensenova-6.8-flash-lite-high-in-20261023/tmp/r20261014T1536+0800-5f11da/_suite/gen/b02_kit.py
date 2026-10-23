"""B02 共用构件：复用 b01_kit 几何 API，将 TASK/OUT/TMP 指向 B02 目录。"""
from __future__ import annotations
import pathlib, sys, datetime as dt, json

HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
sys.path.insert(0, str(HERE.parent))

import b01_kit as K

# 覆盖 B01 → B02
K.TASK = "B02"
K.OUT = ROOT / "outputs" / RUN_ID / "B02"
K.TMP = ROOT / "tmp" / RUN_ID / "B02"
K.TZ = dt.timezone(dt.timedelta(hours=8))
K.TZ_NAME = "Asia/Shanghai (UTC+08:00)"

# re-export Doc class and standalone functions
Doc = K.Doc
dry_run = K.dry_run
assert_gates = K.assert_gates
save_gates = K.save_gates
log_iteration = K.log_iteration
render_case = K.render_case
contrast = K.contrast
d_e = K.d_e
check_palette = K.check_palette
tool_call = K.tool_call
append_jsonl = K.append_jsonl
rel = K.rel
now = K.now
ring = K.ring
tw = K.tw
pitch = K.pitch
fmt = K.fmt
esc = K.esc
FONT = K.FONT
ROOT_PATH = ROOT