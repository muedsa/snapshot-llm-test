"""A11 探针 4：用最终写法与真实数据试排，像素度量后定稿。

已确认的写法（探针 1–3）：
  * 解析器不做实体解码，子内容里的 &lt; 会原样显示 → 不能用实体
  * 子内容里写原样 < 会 400（被当成标签起始）
  * **属性 text="..." 的值按字面取用**，可直接包含 < > & —— 这是保真的唯一正解
本探针用真实 invoice 数据验证：4 条 literal_lines 的逐字符保真、等宽下的双空格宽度、
以及金额列右对齐后小数点的实际 x 坐标是否一致。

用法：
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a11_probe4.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import suite as S  # noqa: E402
import a11_client as C  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TASK = "A11"
RID = S.run_id()
W, H, M = 1200, 920, 48
CJK = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

inv = json.loads((ROOT / "tasks/A11-bilingual-invoice/inputs/invoice.json")
                 .read_text(encoding="utf-8"))
LIT = inv["literal_lines"]

p = ['<Snapshot background="#FFFFFF">',
     '<Container width="%d" height="%d">' % (W, H),
     '<Stack width="%d" height="%d">' % (W, H),
     '<Positioned left="0" top="0" width="%d" height="6">'
     '<Container color="#0F766E" /></Positioned>' % W,
     '<Positioned left="%d" top="24" width="%d" height="44">'
     '<Text fontFamily="%s" fontSize="28" fontStyle="BOLD" color="#0F172A">'
     '探针 4 · 真实数据试排</Text>'
     '</Positioned>' % (M, W - 2 * M, CJK)]

# --- A 组：4 条 literal_lines，全部走 text 属性 -------------------------
y = 92
p.append('<Positioned left="%d" top="%d" width="%d" height="26">'
         '<Text fontFamily="%s" fontSize="20" color="#64748B">'
         'A · literal_lines 原样排版（等宽，text 属性）</Text>'
         '</Positioned>' % (M, y, W - 2 * M, CJK))
y += 34
for i, line in enumerate(LIT):
    p.append('<Positioned left="%d" top="%d" width="150" height="44">'
             '<Text fontFamily="%s" fontSize="22" color="#94A3B8">L%d</Text>'
             '</Positioned>' % (M, y + 6, CJK, i + 1))
    p.append('<Positioned left="%d" top="%d" width="%d" height="44">'
             '<Border border="1 SOLID #E2E8F0">'
             '<Container width="%d" height="44" alignment="CENTER_LEFT">'
             '<Text fontFamily="%s" fontSize="24" color="#0F172A" text="%s" />'
             '</Container></Border></Positioned>' % (
                 M + 150, y, W - 2 * M - 150, W - 2 * M - 150, MONO, line))
    y += 58

# --- B 组：双空格对照：text 属性 / Raw 子内容 / 普通子内容 ---------------
y += 20
p.append('<Positioned left="%d" top="%d" width="%d" height="26">'
         '<Text fontFamily="%s" fontSize="20" color="#64748B">'
         'B · 批次行双空格：三种写法对比</Text>'
         '</Positioned>' % (M, y, W - 2 * M, CJK))
y += 34
variants = [
    ('B1 text 属性', '<Text fontFamily="%s" fontSize="26" color="#0F172A" '
     'text="%s" />' % (MONO, LIT[0])),
    ('B2 Raw 子内容', '<Text fontFamily="%s" fontSize="26" color="#0F172A">'
     '<Raw>%s</Raw></Text>' % (MONO, LIT[0])),
    ('B3 普通子内容', '<Text fontFamily="%s" fontSize="26" color="#0F172A">'
     '%s</Text>' % (MONO, LIT[0])),
]
for cap, inner in variants:
    p.append('<Positioned left="%d" top="%d" width="200" height="34">'
             '<Text fontFamily="%s" fontSize="20" color="#94A3B8">%s</Text>'
             '</Positioned>' % (M, y + 5, CJK, cap))
    p.append('<Positioned left="%d" top="%d" width="%d" height="34">'
             '<Container width="%d" height="34" alignment="CENTER_LEFT">%s</Container>'
             '</Positioned>' % (M + 200, y, W - 2 * M - 200, W - 2 * M - 200, inner))
    y += 44

# --- C 组：金额右对齐，6 个不同金额，量小数点 x ------------------------
y += 18
p.append('<Positioned left="%d" top="%d" width="%d" height="26">'
         '<Text fontFamily="%s" fontSize="20" color="#64748B">'
         'C · 金额列右对齐（固定宽 240，量小数点 x 是否一致）</Text>'
         '</Positioned>' % (M, y, W - 2 * M, CJK))
y += 34
amounts = ["805.50", "478.80", "1160.00", "1680.00", "4124.30", "4215.96"]
for i, amt in enumerate(amounts):
    p.append('<Positioned left="%d" top="%d" width="240" height="36">'
             '<Container width="240" height="36" alignment="CENTER_RIGHT">'
             '<Text fontFamily="%s" fontSize="26" color="#0F172A" text="%s" />'
             '</Container></Positioned>' % (W - M - 240, y, MONO, amt))
    p.append('<Positioned left="%d" top="%d" width="240" height="36">'
             '<Text fontFamily="%s" fontSize="18" color="#94A3B8">%s</Text>'
             '</Positioned>' % (W - M - 240 - 260, y + 6, CJK, "row%d" % (i + 1)))
    y += 42

p.append('<Positioned left="%d" top="%d" width="%d" height="24">'
         '<Text fontFamily="%s" fontSize="20" color="#64748B">探针 4 · %s</Text>'
         '</Positioned>' % (M, H - M, W - 2 * M, CJK, RID))
p += ['</Stack>', '</Container>', '</Snapshot>']
dsl = "\n".join(p) + "\n"

r = C.render(TASK, dsl, "probe4b-layout",
             purpose="真实数据试排：literal_lines 保真、双空格宽度、金额小数点列对齐",
             dsl_name="probe4b-layout.snapshot")
print("HTTP %s rid=%s bytes=%s" % (r["status"], r["request_id"],
                                   r["log"].get("response_bytes")))
if r["status"] == 200:
    (S.task_dirs(TASK)[1] / "preview" / "probe4b-layout.png").write_bytes(r["body"])
S.log_iteration(TASK, {
    "id": "a11-it-08", "seq": 8, "phase": "diagnostic", "kind": "probe",
    "started_at": r["log"].get("started_at"), "ended_at": r["log"].get("ended_at"),
    "label": "probe4b-layout", "purpose": "真实数据试排并像素度量，定稿排版方案",
    "request_ids": [r["request_id"]], "http_status": [r["status"]],
    "outcome": "done" if r["status"] == 200 else "incomplete",
    "detail": "a11-it-07 的页面高 760 太矮，第 5、6 个金额行被裁掉；本版 920 全容纳。"
              "4 条 literal_lines 用 text 属性原样排版；批次行三种空白写法对比；"
              "6 个金额右对齐后度量小数点 x",
    "image_path": S.rel(S.task_dirs(TASK)[1] / "preview" / "probe4b-layout.png")
    if r["status"] == 200 else None,
})
