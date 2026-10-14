"""A10 patch 7: every per-area caption must sit on one line.

v005 wrapped ④/⑤/⑥ with a single trailing glyph on line 2. Shortened to fit 320px at
fontSize 18, and the DSL text-node count is now recorded in the audit so the "说明文字≥20"
requirement is evidenced rather than asserted.
"""
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
p = ROOT / "tmp" / RUN / "A10" / "gen.py"
s = p.read_text(encoding="utf-8")
orig = s


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new, count)


rep('"ImageFiltered 连背景文字形状一起糊"', '"ImageFiltered 连背景与文字一起糊"')
rep('"MULTIPLY 后 sigma=6，间隙被填并外溢"', '"MULTIPLY 后 sigma=6，间隙被填"')
rep('"同一结果套 r=100 圆裁，弧上锐利截断"', '"同一结果套 r=100 圆裁，弧上截断"')

# record how many explanatory text nodes the board actually carries
rep('''OUT_DIR.mkdir(parents=True, exist_ok=True)''',
    '''_dsl_text = doc.render()
_n_text = _dsl_text.count("<Text")
audit["text_inventory"] = {
    "text_nodes_total": _n_text,
    "number_title_nodes": 6,
    "explanatory_nodes": _n_text - 6,
    "requirement": "说明文字≥20",
    "satisfied": _n_text - 6 >= 20,
    "counting": "统计 DSL 中 Text 节点总数，再减去 6 个格子的编号标题；"
                "副标题、组别标签、采样点标注、每格说明与证据面板文字都算说明文字",
}

OUT_DIR.mkdir(parents=True, exist_ok=True)''')

assert s != orig
p.write_text(s, encoding="utf-8")
print("patched 7")
