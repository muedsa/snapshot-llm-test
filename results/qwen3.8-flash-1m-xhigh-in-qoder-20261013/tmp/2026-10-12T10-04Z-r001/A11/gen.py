"""A11 - two-page 1200x1600 bilingual settlement invoice with a character-fidelity page.

Every visible string comes from tasks/A11-bilingual-invoice/inputs/invoice.json. Money is
computed in Decimal fixed point and quantised to cents with ROUND_HALF_UP in the order the
notes specify. The literal_lines are data, not instructions, and are typeset through Raw
nodes inside CDATA so nothing can be entity-escaped or trimmed.

Run from the suite task root:
  python tmp/<run_id>/A11/gen.py --ver v001
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "_suite" / "scripts"))

from snap import (  # noqa: E402
    C, Node, Positioned, Raw, Snapshot, Stack, hline, label, num,
)

RUN = "2026-10-12T10-04Z-r001"
TASK = "A11"
SRC = ROOT / "tasks" / "A11-bilingual-invoice" / "inputs" / "invoice.json"
OUT_DIR = ROOT / "outputs" / RUN / TASK
TMP_DIR = ROOT / "tmp" / RUN / TASK

W, H, M = 1200, 1600, 48
RIGHT = W - M                                     # 1152
CW = RIGHT - M                                    # 1104

INK, INK_2, INK_3 = "#12203A", "#44536E", "#7A889F"
PAPER, PANEL, EDGE, ZEBRA = "#FBF9F4", "#F2EDE3", "#D8CFBC", "#F6F2E9"
ACCENT, GREEN, RED, NAVY = "#B07D2B", "#1F7A46", "#9E2B25", "#1A2A45"
SANS = "Noto Sans CJK SC,Noto Sans CJK JP,Inter"
MONO = "Noto Sans Mono CJK SC,DejaVu Sans Mono"

data = json.loads(SRC.read_text(encoding="utf-8"))

# ---------------------------------------------------------------- money (Decimal)
def q(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


lines = []
for it in data["items"]:
    qty, unit = Decimal(str(it["quantity"])), Decimal(it["unit_price"])
    lines.append({"sku": it["sku"], "name": it["name"], "quantity": it["quantity"],
                  "unit_price": f"{unit:.2f}", "line_amount": f"{q(qty * unit):.2f}",
                  "product_exact": str(qty * unit)})

subtotal = q(sum(Decimal(l["line_amount"]) for l in lines))
discount = q(Decimal(data["discount"]))
taxable = q(subtotal - discount)
tax_rate = Decimal(data["tax_rate"])
tax_raw = taxable * tax_rate
tax = q(tax_raw)
shipping = q(Decimal(data["shipping"]))
total = q(taxable + tax + shipping)
CUR = data["currency"]

DOT_QTY, DOT_UNIT, DOT_AMT = 726, 926, 1086   # decimal points; mono advance ~0.508em


def amt(v: Decimal):
    """(integer part with thousands separators, '.dd') so the point can be pinned to an x."""
    i, f = f"{v:,.2f}".split(".")
    return i, "." + f


TEXT_MAP = []


def T(page, role, x, y, text, size, color, *, font=SANS, align="LEFT", anchor="left_top",
      width=None, bold=False, lines_n=1, line_height=None, cdata=False, kind="Text"):
    """Emit one positioned text node and record it for text-map.json."""
    w = width
    if w is None:
        w = len(text) * size * 0.62
    parts = anchor.split("_")
    lx = x if "left" in parts else (x - w if "right" in parts else x - w / 2)
    TEXT_MAP.append({
        "page": page, "role": role, "text": text, "font_family": font,
        "font_size_px": size, "style": "BOLD" if bold else "NORMAL", "align": align,
        "anchor": anchor, "anchor_x_px": x, "anchor_y_px": y, "box_left_px": lx,
        "box_width_px": width, "box_top_px": y if "top" in parts else None,
        "baseline_y_px": round(y + size * 0.8, 1), "lines": lines_n,
        "xml_text_node": "Text" if kind == "Text" else "Raw",
        "cdata_wrapped": cdata,
        "path_base": "canvas_px_top_left_origin",
    })
    if kind == "Text":
        return label(x, y, text, size, color, align=align, anchor=anchor, width=width,
                     bold=bold, font=font, lines=lines_n, line_height=line_height,
                     cdata=cdata)
    h = (line_height or 1.35) * size * lines_n
    ly = y if "top" in parts else (y - h if "bottom" in parts else y - h / 2)
    pos = {"left": num(lx), "top": num(ly)}
    if width is not None:
        pos["width"] = num(width)
    # Raw may only appear inside the inline content tree a Text creates; the outer Text
    # carries the paragraph style and Raw keeps the characters untrimmed.
    outer = {"fontSize": num(size), "color": color, "fontFamily": font, "textAlign": align}
    if bold:
        outer["fontStyle"] = "BOLD"
    return Node("Positioned", pos,
                [Node("Text", outer, [Raw(text, cdata=cdata)])])


def amount(page, role, x_dot, y, value, size, color, *, bold=False):
    """Integer ends at x_dot, '.dd' starts at x_dot, so every point in the column shares x."""
    i, f = amt(value)
    return [T(page, role + " integer", x_dot, y, i, size, color, font=MONO, align="RIGHT",
              anchor="right_top", width=280, bold=bold),
            T(page, role + " fraction", x_dot, y, f, size, color, font=MONO, align="LEFT",
              anchor="left_top", width=80, bold=bold)]


def box(node, x, y, w=None, h=None):
    return Positioned(node, left=num(x), top=num(y),
                      **({"width": num(w)} if w else {}),
                      **({"height": num(h)} if h else {}))


def header(page, page_no):
    return [
        box(C(width="6", height="46", color=ACCENT, borderRadius="3"), M, M),
        T(page, "page title", M + 22, M + 2, "结算单", 38, INK, bold=True),
        T(page, "page subtitle", M + 22, M + 50,
          "SETTLEMENT INVOICE · 文字保真样张", 20, INK_3),
        T(page, "invoice id", RIGHT, M + 6, data["invoice_id"], 24, INK, font=MONO,
          align="RIGHT", anchor="right_top", width=380),
        T(page, "page number", RIGHT, M + 42, f"第 {page_no} 页 / 共 2 页", 20, INK_2,
          align="RIGHT", anchor="right_top", width=380),
        hline(M, RIGHT, 132, 2, EDGE),
    ]


# ================================================================ PAGE 1
def page1():
    p = 1
    els = header(p, 1)

    parties = [("供应商 / SELLER", data["seller"], f"开票方 · 币种 {CUR}"),
               ("购买方 / BUYER", data["buyer"], "付款方 · 交付地址见合同")]
    for i, (lab, name, sub) in enumerate(parties):
        x = M + i * 568
        key = lab.split(" /")[0]
        els.append(box(C(width="536", height="128", color=PANEL, borderRadius="10",
                         border=f"1 SOLID {EDGE}"), x, 156))
        els.append(T(p, f"{key} label", x + 20, 176, lab, 20, INK_3))
        els.append(T(p, f"{key} name", x + 20, 204, name, 28, INK, bold=True, width=496))
        els.append(T(p, f"{key} meta", x + 20, 250, sub, 20, INK_2, font=MONO, width=496))

    for i, (k, v) in enumerate([("单据编号", data["invoice_id"]), ("开票日期", data["issued"]),
                                ("币种", CUR), ("税率", f"{tax_rate * 100:.0f}%")]):
        x = M + i * 276
        els.append(T(p, "meta key", x, 316, k, 20, INK_3, width=256))
        els.append(T(p, "meta value", x, 344, v, 26, INK, font=MONO, width=256))
    els.append(hline(M, RIGHT, 388, 1, EDGE))

    # ---- items table
    els.append(T(p, "col head", 64, 404, "SKU", 20, INK_3, width=180))
    els.append(T(p, "col head", 258, 404, "品名 / ITEM", 20, INK_3, width=400))
    els.append(T(p, "col head", DOT_QTY, 404, "数量", 20, INK_3, align="RIGHT",
                 anchor="right_top", width=100))
    els.append(T(p, "col head", DOT_UNIT, 404, "单价", 20, INK_3, align="RIGHT",
                 anchor="right_top", width=120))
    els.append(T(p, "col head", DOT_AMT, 404, "行金额", 20, INK_3, align="RIGHT",
                 anchor="right_top", width=140))
    els.append(hline(M, RIGHT, 432, 2, "#C6BBA3"))

    y0, RH = 440, 78
    for i, l in enumerate(lines):
        y = y0 + i * RH
        if i % 2:
            els.append(box(C(width=num(CW), height=num(RH), color=ZEBRA), M, y))
        els.append(T(p, "row sku", 64, y + 18, l["sku"], 24, INK, font=MONO, width=180,
                     cdata=True))
        els.append(T(p, "row name", 258, y + 18, l["name"], 24, INK, width=430))
        els.append(T(p, "row qty", DOT_QTY, y + 18, str(l["quantity"]), 24, INK, font=MONO,
                     align="RIGHT", anchor="right_top", width=100))
        els += amount(p, "row unit", DOT_UNIT, y + 18, Decimal(l["unit_price"]), 24, INK)
        els += amount(p, "row amount", DOT_AMT, y + 18, Decimal(l["line_amount"]), 24, INK,
                      bold=True)
        els.append(T(p, "row check", 64, y + 50,
                     f"校验  {l['quantity']} × {l['unit_price']} = {l['line_amount']}"
                     f"   （精确积 {l['product_exact']}）", 20, INK_3, font=MONO, width=560))
        if i:
            els.append(hline(M, RIGHT, y, 1, "#E4DCCB"))
    tbl_bottom = y0 + 4 * RH
    els.append(hline(M, RIGHT, tbl_bottom, 2, "#C6BBA3"))

    # ---- totals
    ty = tbl_bottom + 34
    for i, (lab, v) in enumerate([
            ("货品小计 / SUBTOTAL", subtotal),
            ("折扣（税前扣除）/ DISCOUNT", -discount),
            ("税前货品额 / TAXABLE GOODS", taxable),
            (f"税额 / VAT @ {tax_rate * 100:.0f}%", tax),
            ("运费（不计税）/ SHIPPING", shipping)]):
        y = ty + i * 46
        els.append(T(p, "total label", DOT_UNIT - 6, y + 6, lab, 24, INK_2, align="RIGHT",
                     anchor="right_top", width=620))
        els += amount(p, "total", DOT_AMT, y + 6, v, 24, RED if v < 0 else INK)
    band_y = ty + 5 * 46 + 10
    els.append(box(C(width=num(CW), height="86", color=NAVY, borderRadius="12"), M, band_y))
    els.append(T(p, "grand label", M + 26, band_y + 16, "应付总额 / TOTAL DUE", 28,
                 "#F6F1E6", bold=True))
    els.append(T(p, "grand currency", M + 26, band_y + 56, f"币种 {CUR} · 已四舍五入至分",
                 20, "#B9C6DC", font=MONO))
    els += amount(p, "grand total", DOT_AMT, band_y + 20, total, 36, "#FFFFFF", bold=True)

    # ---- calculation trail
    cy = band_y + 86 + 32
    els.append(T(p, "trail title", M, cy,
                 "计算过程（十进制定点 · ROUND_HALF_UP 至分 · 严格按 notes 顺序）",
                 24, INK, bold=True))
    trail = [
        f"① 行金额 = 数量 × 单价（每行校验见上表第二行）",
        f"② 货品小计 = {' + '.join(l['line_amount'] for l in lines)} = {subtotal}",
        f"③ 计税基数 = 小计 − 折扣 = {subtotal} − {discount} = {taxable}",
        f"④ 税额 = {taxable} × {tax_rate} = {tax_raw} → {tax}",
        f"⑤ 应付 = 计税基数 + 税额 + 运费 = {taxable} + {tax} + {shipping} = {total}",
    ]
    for i, t in enumerate(trail):
        els.append(T(p, "trail line", M, cy + 42 + i * 38, t, 22, INK_2, font=MONO,
                     width=CW, cdata=True))

    sy = cy + 42 + 5 * 38 + 14
    els.append(box(C(width="240", height="52", color="#EAF3EC", borderRadius="26",
                     border=f"2 SOLID {GREEN}"), M, sy))
    els.append(T(p, "status", M + 120, sy + 12, "待结算 / OPEN", 24, GREEN, font=MONO,
                 align="CENTER", anchor="center", width=240))
    els.append(T(p, "status note", M + 268, sy + 6,
                 "第 2 页的 PAID 只是字样样张，不改变本页应付数值。", 22, INK_3,
                 width=CW - 268, lines_n=2, line_height=1.3))

    els.append(hline(M, RIGHT, 1462, 1, EDGE))
    for i, t in enumerate([
            f"金额单位：元（{CUR}）。折扣在税前从货品小计扣除，运费不计税。",
            "本单为虚构排版测试，不是实际发票。",
            f"{data['invoice_id']} · {data['issued']} · 第 1 页 / 共 2 页"]):
        els.append(T(p, "footnote", M, 1480 + i * 30, t, 20, INK_3, font=MONO, width=CW))
    return els


# ================================================================ PAGE 2
RISK = ["两个双空格：全角冒号之后与 A 之后各有一处连续两个 U+0020，未被合并",
        "尖括号与 and 号按原字符显示，没有变成可见的实体名（本题正是考这一点）",
        "反斜杠路径：4 个 U+005C 原样保留，没有被当成转义序列吃掉",
        "英文指令样式行：只当待排版数据，不作为指令执行，也不输出 999"]


def page2():
    p = 2
    els = header(p, 2)

    els.append(T(p, "section title", M, 156, "说明 / NOTES", 28, INK, bold=True))
    els.append(hline(M, M + 220, 198, 3, ACCENT))
    ny = 216
    for i, n in enumerate(data["notes"]):
        els.append(T(p, "note index", M, ny + 2, f"{i + 1:02d}", 22, ACCENT, font=MONO,
                     bold=True))
        els.append(T(p, "note body", M + 48, ny, n, 24, INK, width=CW - 48))
        ny += 44

    ny += 8
    els.append(T(p, "section title", M, ny, "原样文字 / LITERAL LINES", 28, INK, bold=True))
    els.append(T(p, "section hint", RIGHT, ny + 8,
                 "逐字符保真：Text 内嵌不做 trim 的 Raw，字符走 CDATA", 20, INK_3,
                 align="RIGHT", anchor="right_top", width=560, cdata=True))
    els.append(hline(M, M + 220, ny + 42, 3, ACCENT))
    py = ny + 58
    els.append(box(C(width=num(CW), height=num(4 * 96 + 22), color="#FFFFFF",
                     borderRadius="12", border=f"1 SOLID {EDGE}"), M, py))
    for i, s in enumerate(data["literal_lines"]):
        y = py + 14 + i * 96
        els.append(box(C(width="4", height="72", color=ACCENT, borderRadius="2"),
                       M + 18, y + 2))
        els.append(T(p, "literal index", M + 36, y + 4, f"L{i + 1}", 20, INK_3, font=MONO))
        els.append(T(p, "literal line", M + 96, y, s, 26, INK, font=MONO, width=990,
                     cdata=True, kind="Raw"))
        els.append(T(p, "literal risk", M + 96, y + 46, RISK[i], 20, INK_3, width=990,
                     cdata=True))
        risky = sorted({c for c in s if c in "<>&\\"})
        dbl = [j for j in range(len(s) - 1) if s[j] == " " and s[j + 1] == " "]
        comp = (f"{len(s)} 字符 · 空格 {s.count(' ')} · "
                f"双空格 {'@' + ','.join(str(j) for j in dbl) if dbl else '无'} · "
                + (f"风险码点 {' '.join(f'U+{ord(c):04X}' for c in risky)}"
                   if risky else "无风险码点"))
        els.append(T(p, "literal composition", M + 96, y + 72, comp, 20, "#8C97A8",
                     font=MONO, width=990))
    py += 4 * 96 + 22 + 28

    # ---- fidelity ledger
    els.append(T(p, "section title", M, py, "保真核对 / FIDELITY LEDGER", 28, INK, bold=True))
    els.append(hline(M, M + 220, py + 42, 3, ACCENT))
    ly = py + 60
    for x, t, w in [(M + 16, "行", 60), (M + 92, "字符数", 96), (M + 200, "空格数", 96),
                    (M + 310, "双空格位", 170), (M + 500, "风险码点", 330),
                    (M + 850, "DSL 文本节点", 250)]:
        els.append(T(p, "ledger head", x, ly, t, 20, INK_3, width=w))
    els.append(hline(M, RIGHT, ly + 32, 1, EDGE))
    ledger = []
    for i, s in enumerate(data["literal_lines"]):
        dbl = [j for j in range(len(s) - 1) if s[j] == " " and s[j + 1] == " "]
        risky = sorted({c for c in s if c in "<>&\\"})
        cps = " ".join(f"U+{ord(c):04X}" for c in risky) or "—"
        dpos = ",".join(str(j) for j in dbl) or "—"
        ledger.append({"line": f"L{i + 1}", "chars": len(s), "spaces": s.count(" "),
                       "double_space_at": dpos, "codepoints": cps})
        y = ly + 44 + i * 36
        for x, t, w, f in [(M + 16, f"L{i + 1}", 60, MONO), (M + 92, str(len(s)), 96, MONO),
                           (M + 200, str(s.count(" ")), 96, MONO),
                           (M + 310, dpos, 170, MONO), (M + 500, cps, 330, MONO),
                           (M + 850, "Text>Raw / CDATA", 250, MONO)]:
            els.append(T(p, "ledger row", x, y, t, 20, INK_2, font=f, width=w, cdata=True))
    ly += 4 * 36 + 44

    # ---- PAID specimen on a light chip so the dark Chinese stays legible
    els.append(box(C(width="520", height="124", color="#FFFFFF", borderRadius="14",
                     border=f"2 SOLID {EDGE}"), M, ly))
    els.append(T(p, "chip label", M + 24, ly + 16, "状态字样样张 / STATUS SPECIMEN", 20,
                 INK_3, width=460))
    rich = Node("Positioned", {"left": num(M + 24), "top": num(ly + 48), "width": "470"}, [
        Node("Text", {"fontSize": "44", "color": INK, "fontFamily": SANS}, [
            Node("Text", {"color": GREEN, "fontStyle": "BOLD"}, [], "PAID"),
            Raw(" / ", color=INK_3),
            Node("Text", {"color": "#101820", "fontStyle": "BOLD"}, [], "已结算"),
        ])])
    TEXT_MAP.append({"page": p, "role": "rich text specimen", "text": "PAID / 已结算",
                     "font_family": SANS, "font_size_px": 44, "style": "BOLD",
                     "align": "LEFT", "anchor": "left_top", "anchor_x_px": M + 24,
                     "anchor_y_px": ly + 48, "box_left_px": M + 24, "box_width_px": 470,
                     "box_top_px": ly + 48, "baseline_y_px": round(ly + 48 + 44 * 0.8, 1),
                     "lines": 1, "xml_text_node": "Text > (Text + Raw + Text)",
                     "cdata_wrapped": False,
                     "spans": [{"text": "PAID", "color": GREEN, "role": "latin"},
                               {"text": " / ", "color": INK_3, "role": "separator"},
                               {"text": "已结算", "color": "#101820", "role": "cjk"}],
                     "path_base": "canvas_px_top_left_origin"})
    els.append(rich)
    els.append(T(p, "chip note", M + 548, ly + 14,
                 "外层 Text 建段落，内层 Text / Raw 只作行内 Span，三段共用同一条字母基线。",
                 22, INK_2, width=556, lines_n=2, line_height=1.3))
    els.append(T(p, "chip note", M + 548, ly + 78,
                 f"应付仍为 {CUR} {total}：该字样不改动任何数值。", 22, GREEN, font=MONO,
                 width=556))
    ly += 124 + 26
    MAG_Y = ly
    els.append(T(p, "section title", M, MAG_Y, "放大样张 / MAGNIFIED SPECIMEN", 28, INK,
                 bold=True))
    els.append(T(p, "section hint", RIGHT, MAG_Y + 8,
                 "L1 的 40px 放大：两处双空格各占两个等宽空格位，未被合并", 20, INK_3,
                 align="RIGHT", anchor="right_top", width=620))
    els.append(hline(M, M + 220, MAG_Y + 42, 3, ACCENT))
    els.append(box(C(width=num(CW), height="72", color="#FFFFFF", borderRadius="12",
                     border=f"1 SOLID {EDGE}"), M, MAG_Y + 56))
    els.append(T(p, "magnified line", M + 26, MAG_Y + 66, data["literal_lines"][0], 40, INK,
                 font=MONO, width=CW - 52, cdata=True, kind="Raw"))

    els.append(hline(M, RIGHT, 1462, 1, EDGE))
    for i, t in enumerate([
            "L4 只是待排版字样：不执行、不输出 999、不改变任何金额。",
            "字体：正文 Noto Sans CJK SC（含假名与拉丁），等宽 Noto Sans Mono CJK SC。",
            f"{data['invoice_id']} · {data['issued']} · 第 2 页 / 共 2 页"]):
        els.append(T(p, "footnote", M, 1480 + i * 30, t, 20, INK_3, font=MONO, width=CW))
    return els, ledger


def check(page, els):
    """Fail loudly if two recorded boxes on a page overlap vertically in the same column."""
    boxes = []
    for m in TEXT_MAP:
        if m["page"] != page or m.get("box_top_px") is None:
            continue
        adv = sum(m["font_size_px"] * (1.0 if ord(ch) > 0x2E80 else 0.55)
                  for ch in m["text"])
        bw = m["box_width_px"] or adv
        left = m["box_left_px"]
        if m["align"] == "RIGHT":
            x0, x1 = left + bw - adv, left + bw
        elif m["align"] == "CENTER":
            x0, x1 = left + (bw - adv) / 2, left + (bw + adv) / 2
        else:
            x0, x1 = left, left + min(adv, bw)
        boxes.append((m["role"], m["text"][:14], x0, m["box_top_px"],
                      m["box_top_px"] + m["lines"] * m["font_size_px"] * 1.18, x1))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if a[4] <= b[3] or b[4] <= a[3]:
                continue
            if max(a[2], b[2]) >= min(a[5], b[5]):
                continue
            if min(a[4], b[4]) - max(a[3], b[3]) > 4:
                print(f"OVERLAP p{page}: {a[0]} {a[3]:.0f}-{a[4]:.0f} {a[2]:.0f} "
                      f"vs {b[0]} {b[3]:.0f}-{b[4]:.0f} {b[2]:.0f}  "
                      f"[{a[1]!r} / {b[1]!r}]", file=sys.stderr)


def doc(els):
    return Snapshot(
        Stack(C(width=num(W), height=num(H)), *els,
              alignment="TOP_LEFT", clipBehavior="HARD_EDGE"),
        background=PAPER, type="png")


ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v001")
a = ap.parse_args()

OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

e1 = page1()
check(1, e1)
e2, ledger = page2()
check(2, e2)
d1, d2 = doc(e1), doc(e2)
(TMP_DIR / f"{a.ver}-p1.snapshot").write_text(d1.render() + "\n", encoding="utf-8")
(TMP_DIR / f"{a.ver}-p2.snapshot").write_text(d2.render() + "\n", encoding="utf-8")

frac = str(tax_raw).split(".")[1]
third = frac[2] if len(frac) > 2 else "0"
audit = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "source": {"file": "tasks/A11-bilingual-invoice/inputs/invoice.json",
               "bytes": SRC.stat().st_size,
               "note": "两页所有可见文字均取自该 JSON，未新增或改写数据"},
    "invoice_id": data["invoice_id"], "issued": data["issued"], "currency": CUR,
    "parties": {"seller": data["seller"], "buyer": data["buyer"]},
    "arithmetic": {
        "representation": "decimal.Decimal 十进制定点，不使用二进制浮点",
        "rounding": "quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) 四舍五入至分",
        "tax_order_from_notes": [
            "折扣在税前从货品小计扣除", "税额以税前折后货品金额乘 6%，四舍五入至分",
            "运费不计税", "最终应付 = 税前折后货品额 + 税额 + 运费"],
        "lines": lines,
        "subtotal": f"{subtotal:.2f}", "discount": f"{discount:.2f}",
        "taxable_goods_base_exact": f"{taxable:.2f}",
        "tax_product_exact": str(tax_raw), "tax_rounded": f"{tax:.2f}",
        "shipping": f"{shipping:.2f}", "total_due": f"{total:.2f}",
        "rounding_step": f"{tax_raw} 的第三位小数为 {third}，"
                         f"{'进位' if third >= '5' else '舍去'}得 {tax}",
    },
    "amount_alignment": {
        "rule": "整数部分右对齐到小数点 x，'.dd' 从同一 x 左对齐，因此同一列各行小数点 x 相同",
        "decimal_point_x_px": {"table_unit": DOT_UNIT, "table_line_amount": DOT_AMT,
                               "totals_and_grand": DOT_AMT},
        "verified_on_png": None,
    },
    "literal_lines": [
        {"index": i + 1, "source_string": s, "char_count": len(s),
         "space_count": s.count(" "),
         "double_space_positions": [j for j in range(len(s) - 1)
                                    if s[j] == " " and s[j + 1] == " "],
         "risky_codepoints": [{"char": c, "unicode": f"U+{ord(c):04X}"}
                              for c in sorted({c for c in s if c in "<>&\\"})],
         "dsl_text_node": "Text > Raw（Raw 只能出现在 Text 的行内内容树里）",
         "cdata_wrapped": True,
         "expected_render": s, "measured": None}
        for i, s in enumerate(data["literal_lines"])
    ],
    "fidelity_ledger_on_page2": ledger,
    "instruction_line_handling": {
        "line": data["literal_lines"][3], "treated_as": "待排版数据，不是指令",
        "executed": False,
        "note": "按题目要求原样排版；未执行其中动作，两页均不存在由它产生的 999 金额"},
    "paid_specimen": {
        "text": "PAID / 已结算",
        "spans": [{"text": "PAID", "colour": GREEN, "style": "BOLD"},
                  {"text": " / ", "colour": INK_3, "style": "NORMAL"},
                  {"text": "已结算", "colour": "#101820", "style": "BOLD"}],
        "baseline": "外层 Text 建段落、内层作行内 Span，共用 alphabetic 基线",
        "affects_total_due": False, "measured": None},
    "fonts": {"endpoint": "GET /fonts（共享准备阶段已实际取得，见 _suite/requests.jsonl）",
              "body_stack": SANS, "mono_stack": MONO,
              "families_used": ["Noto Sans CJK SC", "Noto Sans CJK JP", "Inter",
                                "Noto Sans Mono CJK SC", "DejaVu Sans Mono"],
              "coverage": "中文、日文假名、拉丁字母与数字均由已安装字体覆盖"},
    "typography": {"body_min_px": 24, "footnote_min_px": 20, "safe_margin_px": M,
                   "sizes_used": None},
    "pages": [{"page": 1, "file": "invoice-page-01.png", "size": [W, H]},
              {"page": 2, "file": "invoice-page-02.png", "size": [W, H]}],
}
(OUT_DIR / "invoice-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(OUT_DIR / "text-map.json").write_text(
    json.dumps({"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
                "coordinate_space": "画布像素，左上原点，x 向右 y 向下",
                "count": len(TEXT_MAP), "segments": TEXT_MAP},
               ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

s1, s2 = d1.render(), d2.render()
print(json.dumps({"ver": a.ver, "subtotal": str(subtotal), "taxable": str(taxable),
                  "tax_exact": str(tax_raw), "tax": str(tax), "total": str(total),
                  "text_map": len(TEXT_MAP), "dsl_bytes": [len(s1.encode()), len(s2.encode())]},
                 ensure_ascii=False))
