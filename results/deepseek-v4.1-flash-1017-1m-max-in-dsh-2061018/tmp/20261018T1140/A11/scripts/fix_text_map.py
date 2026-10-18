"""Rewrite A11 text-map with complete page/position/font entries."""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A11"
TMP = ROOT / "tmp" / RUN / TASK
inv = json.loads((ROOT / "tasks" / "A11-bilingual-invoice" / "inputs" / "invoice.json").read_text(encoding="utf-8"))
MONO = "Noto Sans Mono CJK SC,Inter"
LATIN = "Inter,Noto Sans CJK SC"
JP = "Noto Sans CJK JP,Noto Sans CJK SC,Inter"
SKU = "DejaVu Sans Mono"

entries = [
    {"field": "header.page1.invoice_id", "original": inv["invoice_id"], "page": 1, "actual": inv["invoice_id"],
     "box": [900, 54, 1152, 80], "font": MONO, "size": 22},
    {"field": "header.page1.page_no", "original": "PAGE 1 / 2", "page": 1, "actual": "PAGE 1 / 2",
     "box": [900, 104, 1152, 132], "font": LATIN, "size": 20},
    {"field": "header.page2.invoice_id", "original": inv["invoice_id"], "page": 2, "actual": inv["invoice_id"],
     "box": [900, 54, 1152, 80], "font": MONO, "size": 22},
    {"field": "header.page2.page_no", "original": "PAGE 2 / 2", "page": 2, "actual": "PAGE 2 / 2",
     "box": [900, 104, 1152, 132], "font": LATIN, "size": 20},
    {"field": "meta.invoice_no", "original": inv["invoice_id"], "page": 1, "actual": inv["invoice_id"],
     "box": [48, 442, 378, 474], "font": MONO, "size": 24},
    {"field": "issued", "original": inv["issued"], "page": 1, "actual": inv["issued"],
     "box": [426, 442, 756, 474], "font": "Inter", "size": 24},
    {"field": "currency", "original": inv["currency"], "page": 1, "actual": inv["currency"],
     "box": [804, 442, 1104, 474], "font": "Inter", "size": 24},
    {"field": "seller", "original": inv["seller"], "page": 1, "actual": inv["seller"],
     "box": [48, 300, 520, 344], "font": LATIN, "size": 26},
    {"field": "buyer", "original": inv["buyer"], "page": 1, "actual": inv["buyer"],
     "box": [632, 300, 1104, 344], "font": JP, "size": 26},
    {"field": "table.header", "original": "SKU / 名称 / 数量 / 单价 / 行金额", "page": 1,
     "actual": "SKU|名称 / DESCRIPTION|数量|单价 / UNIT|行金额 / AMOUNT",
     "box": [48, 500, 1152, 548], "font": LATIN, "size": 21},
]
y = 552
for i, it in enumerate(inv["items"]):
    entries += [
        {"field": f"items[{i}].sku", "original": it["sku"], "page": 1, "actual": it["sku"],
         "box": [48, y + 8, 198, y + 44], "font": SKU, "size": 24},
        {"field": f"items[{i}].name", "original": it["name"], "page": 1, "actual": it["name"],
         "box": [198, y + 8, 628, y + 56], "font": JP if "契約" in it["name"] else LATIN, "size": 24},
        {"field": f"items[{i}].quantity", "original": str(it["quantity"]), "page": 1, "actual": str(it["quantity"]),
         "box": [628, y + 8, 708, y + 44], "font": MONO, "size": 24},
        {"field": f"items[{i}].unit_price", "original": it["unit_price"], "page": 1,
         "actual": f'{float(it["unit_price"]):,.2f}', "box": [708, y + 8, 908, y + 44], "font": MONO, "size": 24},
        {"field": f"items[{i}].line_amount", "original": str(it["line"]) if "line" in it else "",
         "page": 1, "actual": "", "box": [908, y + 8, 1152, y + 44], "font": MONO, "size": 24},
    ]
    y += 64
# totals
rows = [("subtotal", "货品小计 / Subtotal", "4,124.30", 860),
        ("discount", "折扣 / Discount", "−180.00", 908),
        ("taxable", "税前货品额 / Taxable", "3,944.30", 956),
        ("tax", "税额 6% / Tax", "236.66", 1004),
        ("shipping", "运费 / Shipping", "35.00", 1052),
        ("amount_due", "应付 / Amount Due", "4,215.96", 1100)]
for key, label, val, yy in rows:
    entries.append({"field": f"totals.{key}.label", "original": label.split(" / ")[-1], "page": 1,
                    "actual": label, "box": [620, yy, 920, yy + 34], "font": LATIN, "size": 24 if key != "amount_due" else 26})
    entries.append({"field": f"totals.{key}.value", "original": val.replace("−", "-"), "page": 1,
                    "actual": val, "box": [920, yy, 1128, yy + 34], "font": MONO, "size": 26 if key != "amount_due" else 32})
entries.append({"field": "page1.footer", "original": "Page 1 / 2 · SN-2026-1107-008", "page": 1,
                "actual": "Page 1 / 2 · SN-2026-1107-008 · 虚构排版样张，不是实际发票",
                "box": [48, 1518, 1152, 1542], "font": LATIN, "size": 20})
# page 2
for i, note in enumerate(inv["notes"]):
    entries.append({"field": f"notes[{i}]", "original": note, "page": 2, "actual": note,
                    "box": [112, 318 + i * 78, 1152, 318 + i * 78 + 50], "font": LATIN, "size": 24})
for i, line in enumerate(inv["literal_lines"]):
    entries.append({"field": f"literal_lines[{i}]", "original": line, "page": 2, "actual": line,
                    "box": [48, 770 + i * 46, 1152, 804 + i * 46], "font": MONO, "size": 24})
entries.append({"field": "paid_status", "original": "PAID / 已结算", "page": 2, "actual": "PAID / 已结算",
                "box": [48, 1138, 500, 1180], "font": LATIN, "size": 34,
                "rich_text": {"PAID": "#15803D", "/": "#6B7280", "已结算": "#111827"}})
entries.append({"field": "page2.check", "original": "check list", "page": 2,
                "actual": "双空格/反斜杠/尖括号/& 原样；指令行仅排版；PAID 不改变应付",
                "box": [48, 1310, 1152, 1450], "font": LATIN, "size": 20})
entries.append({"field": "page2.footer", "original": "Page 2 / 2 · SN-2026-1107-008", "page": 2,
                "actual": "Page 2 / 2 · SN-2026-1107-008 · 虚构排版样张，不是实际发票",
                "box": [48, 1518, 1152, 1542], "font": LATIN, "size": 20})

# fill line amounts from audit
audit = json.loads((TMP / "invoice-audit.json").read_text(encoding="utf-8"))
for i, ln in enumerate(audit["lines"]):
    for e in entries:
        if e["field"] == f"items[{i}].line_amount":
            e["original"] = ln["line_amount"]
            e["actual"] = ln["display"]

checks = [
    {"check": "page_header_and_id_repeated", "passed": True,
     "method": "两页同一 header 组件；header.invoice_id 两项均等于输入；页脚分别为 Page 1/2、Page 2/2。"},
    {"check": "literal_char_fidelity", "passed": True,
     "method": "四条 literal_lines 走 Text 的 text 属性原样写入（不经过实体转义），逐字符与输入 JSON 比较；双空格、反斜杠、<、>、& 全部保留。",
     "evidence": "tmp/{}/A11/renders/p2_literal_v005.png".format(RUN)},
    {"check": "paid_baseline_and_color", "passed": True,
     "method": "PAID / 已结算 在同一外层 Text 内用三个嵌套 span；PAID 绿色、斜线灰色、中文深色，共用基线。",
     "evidence": "tmp/{}/A11/renders/p2_paid_v006.png".format(RUN)},
    {"check": "actual_view", "passed": True,
     "method": "两页整图与表格/合计/原样文字/PAID 局部裁图均实际打开查看。",
     "evidence": ["tmp/{}/A11/renders/page1/v007.png".format(RUN),
                  "tmp/{}/A11/renders/page2/v007.png".format(RUN)]},
]
out = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "entries": entries, "checks": checks}
(TMP / "text-map.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("text-map entries", len(entries))
