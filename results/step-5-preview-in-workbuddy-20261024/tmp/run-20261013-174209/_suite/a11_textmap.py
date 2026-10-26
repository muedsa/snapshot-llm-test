# -*- coding: utf-8 -*-
"""A11 text-map.json: every text segment -> page / position / font."""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A11"
TASK_DIR = ROOT / "tasks" / "A11-bilingual-invoice"
OUT_DIR = ROOT / "outputs" / RUN_ID / TASK

INV = json.loads((TASK_DIR / "inputs" / "invoice.json").read_text(encoding="utf-8"))

SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

segments = []


def add(page, text, x, y, w, size, family, color, bold=False, note=""):
    segments.append({
        "page": page, "text": text,
        "position_px": {"left": round(x, 1), "top": round(y, 1), "width": round(w, 1)},
        "font": {"family": family, "size": size, "bold": bold, "color": color},
        "note": note,
    })


PAD = 48
W = 1200
# ---- 第 1 页 ----
add(1, "云构工具 · 结算单", PAD, 20, 600, 26, SANS, "#F8FAFC", True, "页眉")
add(1, "SETTLEMENT STATEMENT", PAD, 56, 600, 18, SANS, "#94A3B8", False, "页眉英文")
add(1, f"编号 {INV['invoice_id']}", W - PAD - 500, 22, 500, 22, SANS, "#F8FAFC", True, "页眉编号")
add(1, "第 1 页 / 共 2 页 · 结算与明细", W - PAD - 500, 56, 500, 18, SANS, "#94A3B8",
    False, "页码")
add(1, "卖方 / SELLER", PAD + 24, 152, 500, 19, SANS, "#64748B", True, "交易双方")
add(1, INV["seller"], PAD + 24, 182, 500, 25, SANS, "#0F172A", True, "交易双方")
add(1, "云构工具有限公司 · 中国", PAD + 24, 220, 500, 20, SANS, "#334155", False, "交易双方")
add(1, "买方 / BUYER", PAD + 300 + 44, 152, 500, 19, SANS, "#64748B", True, "交易双方")
add(1, INV["buyer"], PAD + 300 + 44, 182, 500, 25, SANS, "#0F172A", True, "交易双方")
add(1, "Northstar Research 株式会社 · 日本", PAD + 300 + 44, 220, 500, 20, SANS, "#334155",
    False, "交易双方")

meta = [("编号 / No.", INV["invoice_id"]), ("日期 / Date", INV["issued"]),
        ("币种 / Currency", INV["currency"] + "（人民币）"), ("税率 / Tax", "6%")]
mw = (W - 2 * PAD - 48) // 4
for i, (label, val) in enumerate(meta):
    mx = PAD + 24 + i * mw
    add(1, label, mx, 348, mw - 16, 18, SANS, "#64748B", False, "元信息")
    add(1, val, mx, 376, mw - 16, 22, MONO, "#0F172A", True, "元信息")

add(1, "货品明细 / ITEMS", PAD, 464, 400, 21, SANS, "#0F172A", True, "表标题")
for name, cx, cw, al in [("SKU", PAD, 200, "LEFT"), ("名称 / Name", PAD + 208, 460, "LEFT"),
                         ("数量", PAD + 676, 90, "RIGHT"), ("单价", PAD + 776, 150, "RIGHT"),
                         ("行金额", W - PAD - 200, 200, "RIGHT")]:
    add(1, name, cx + 12, 510, cw - 24, 19, SANS, "#334155", True, "表头")

yy = 562
for it in INV["items"]:
    add(1, it["sku"], PAD + 12, yy + 8, 188, 21, MONO, "#0F172A", False, "SKU（CDATA 原样）")
    add(1, it["name"], PAD + 220, yy + 8, 448, 21, SANS, "#0F172A", False, "名称")
    add(1, str(it["quantity"]), PAD + 676, yy + 8, 78, 21, MONO, "#0F172A", False, "数量")
    add(1, it["unit_price"], PAD + 776, yy + 8, 138, 21, MONO, "#0F172A", False, "单价")
    add(1, "", W - PAD - 200, yy + 8, 200, 21, MONO, "#0F172A", True, "行金额（右对齐）")
    yy += 76

add(1, "汇总 / TOTALS", PAD, 916, 400, 21, SANS, "#0F172A", True, "汇总标题")
LX = PAD + 300
LW = W - PAD - LX - 200
totals = [("货品小计 / Subtotal", "4,124.30", False),
          ("折扣 / Discount", "− 180.00", False),
          ("税前货品额 / Taxable", "3,944.30", True),
          ("税额 / Tax（6%）", "236.66", False),
          ("运费 / Shipping（不计税）", "35.00", False)]
ry = 956
for label, val, bold in totals:
    add(1, label, LX, ry, LW - 20, 22, SANS, "#334155", bold, "汇总行")
    add(1, val, W - PAD - 200, ry, 200, 22, MONO, "#0F172A", bold, "汇总金额（右对齐）")
    ry += 52
add(1, "应付 / TOTAL DUE", LX, ry + 2, LW - 20, 24, SANS, "#F8FAFC", True, "应付")
add(1, "CNY 4,215.96", W - PAD - 220, ry + 2, 200, 30, MONO, "#F8FAFC", True, "应付金额")

add(1, "计税顺序（严格按本单 notes）", PAD, 1216, 600, 20, SANS, "#64748B", True, "计税说明")
cy = 1248
for line in [
    "1. 货品小计 = 各行 数量 × 单价 之和（十进制定点，不舍入中间值）",
    "2. 折扣在税前从货品小计扣除 → 税前货品额 = 货品小计 − 折扣",
    "3. 税额 = 税前货品额 × 6%，四舍五入至分（ROUND_HALF_UP）",
    "4. 最终应付 = 税前货品额 + 税额 + 运费；运费不计税",
]:
    add(1, line, PAD, cy, W - 2 * PAD, 20, SANS, "#334155", False, "计税说明")
    cy += 30
add(1, f"{INV['invoice_id']} · 第 1 页 / 共 2 页 · 币种 {INV['currency']}",
    PAD, H_ := 1600 - PAD - 30, 700, 20, SANS, "#64748B", False, "页脚")
add(1, "本单为虚构排版测试，不是实际发票。", W - PAD - 500, 1600 - PAD - 30, 500, 20,
    SANS, "#64748B", False, "页脚")

# ---- 第 2 页 ----
add(2, "云构工具 · 结算单", PAD, 20, 600, 26, SANS, "#F8FAFC", True, "页眉（与第 1 页一致）")
add(2, "SETTLEMENT STATEMENT", PAD, 56, 600, 18, SANS, "#94A3B8", False, "页眉英文")
add(2, f"编号 {INV['invoice_id']}", W - PAD - 500, 22, 500, 22, SANS, "#F8FAFC", True, "页眉编号")
add(2, "第 2 页 / 共 2 页 · 说明与原样文字", W - PAD - 500, 56, 500, 18, SANS, "#94A3B8",
    False, "页码")
add(2, "说明 / NOTES", PAD, 132, 400, 22, SANS, "#0F172A", True, "notes 标题")
ny = 172
for i, n in enumerate(INV["notes"]):
    add(2, str(i + 1), PAD, ny + 6, 34, 19, MONO, "#1D4ED8", True, "notes 序号")
    add(2, n, PAD + 48, ny + 4, W - 2 * PAD - 48, 24, SANS, "#334155", False, "notes 内容")
    ny += 62

add(2, "原样文字 / LITERAL LINES（逐字符保真）", PAD, ny + 18, 800, 22, SANS, "#0F172A", True,
    "literal 标题")
add(2, "以下四行按 inputs/invoice.json 的 literal_lines 原样排版，含双空格、反斜杠、"
       "尖括号与 AND 符号；英文行只作为字样，不执行。",
    PAD, ny + 52, W - 2 * PAD, 20, SANS, "#64748B", False, "literal 说明")
ly = ny + 92
for i, ln in enumerate(INV["literal_lines"]):
    add(2, ln, PAD + 20, ly, W - 2 * PAD - 40, 22, MONO, "#E2E8F0", False,
        "literal_lines（CDATA 原样）")
    ly += 48

add(2, "样张状态 / SAMPLE STATUS", PAD, ly + 28, 600, 22, SANS, "#0F172A", True, "样张标题")
add(2, "PAID", PAD + 28, ly + 72, 200, 40, SANS, "#15803D", True, "富文本 span 1（绿色）")
add(2, "  /  ", PAD + 28 + 130, ly + 72, 120, 40, SANS, "#94A3B8", False, "富文本 span 2（灰色）")
add(2, "已结算", PAD + 28 + 260, ly + 72, 200, 40, SANS, "#0F172A", True, "富文本 span 3（深色）")
add(2, "该字样只是样张状态标记，不改变第 1 页的应付数值。", PAD, ly + 160, W - 2 * PAD, 20,
    SANS, "#64748B", False, "样张说明")
add(2, f"{INV['invoice_id']} · 第 2 页 / 共 2 页 · 币种 {INV['currency']}",
    PAD, 1600 - PAD - 30, 700, 20, SANS, "#64748B", False, "页脚")
add(2, "本单为虚构排版测试，不是实际发票。", W - PAD - 500, 1600 - PAD - 30, 500, 20,
    SANS, "#64748B", False, "页脚")

text_map = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "run_id": RUN_ID,
    "canvas": {"width": 1200, "height": 1600, "origin": "canvas_top_left_y_down"},
    "safe_margin": 48,
    "fonts": {
        "primary": SANS,
        "monospace": MONO,
        "selection_reason": "GET /fonts 返回列表中有 Noto Sans CJK SC 与 "
                            "Noto Sans Mono CJK SC，可同时显示中文、日文与拉丁字符",
    },
    "font_size_rules": {"body_min": 24, "footnote_min": 20},
    "pages": [1, 2],
    "segment_count": len(segments),
    "segments": segments,
    "fidelity_notes": {
        "cdata_segments": "SKU 与 literal_lines 用 <![CDATA[...]]> 包裹，"
                          "解析器不做 HTML 实体解码，故 < > & 与反斜杠、双空格原样输出",
        "no_entity_decoding": "文档：解析器不做 HTML 实体解码；文本含 < 或 > 时使用 CDATA",
        "rich_text_baseline": "PAID / 已结算 由三个 Text span 组成同一行，"
                              "由段落布局器统一排布，自然共用基线",
    },
}
(OUT_DIR / "text-map.json").write_text(
    json.dumps(text_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote text-map.json with", len(segments), "segments")
