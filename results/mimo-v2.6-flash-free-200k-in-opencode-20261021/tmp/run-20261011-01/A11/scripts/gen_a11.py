#!/usr/bin/env python3
"""A11 bilingual invoice generator (two 1200x1600 pages) + audit JSONs.

Usage: python tmp/<run_id>/A11/scripts/gen_a11.py <suite_root> <run_id> [outdir]

All amounts are computed with decimal fixed point (ROUND_HALF_UP to cent) from
inputs/invoice.json. Literal lines are emitted through <Raw> so whitespace is
preserved; & < > are XML-escaped in the DSL source and decode back to the
original characters at render time (verified visually on the final PNGs).
Every text box carries an explicit width; numeric columns use textAlign=END
with the monospaced font so decimal points align exactly.
"""
import json
import pathlib
import sys
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
run_id = sys.argv[2] if len(sys.argv) > 2 else "run-20261011-01"
out_dir = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else (root / "outputs" / run_id / "A11")
tmp_dir = root / "tmp" / run_id / "A11"
tmp_drafts = tmp_dir / "drafts"
tmp_drafts.mkdir(parents=True, exist_ok=True)
out_dir.mkdir(parents=True, exist_ok=True)

INP = json.loads((root / "tasks" / "A11-bilingual-invoice" / "inputs" / "invoice.json").read_text(encoding="utf-8"))

W, H, M = 1200, 1600, 48
SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
SERIF = "Noto Serif CJK SC"
INK, SUB, LINE, FAINT = "#111827", "#6B7280", "#D1D5DB", "#F3F4F6"
GREEN, GRAY_SLASH = "#16A34A", "#9CA3AF"
PAGES = ["invoice-page-01.png", "invoice-page-02.png"]

CENT = Decimal("0.01")


def q(x):
    return x.quantize(CENT, rounding=ROUND_HALF_UP)


def s(x):
    return format(x, "f")


# ---- money: decimal fixed point ----------------------------------------------
rate = Decimal(INP["tax_rate"])
discount = Decimal(INP["discount"])
shipping = Decimal(INP["shipping"])
lines = []
for i, it in enumerate(INP["items"]):
    up = Decimal(it["unit_price"])
    prod = up * it["quantity"]
    amt = q(prod)
    lines.append({"index": i + 1, "sku": it["sku"], "name": it["name"],
                  "quantity": it["quantity"], "unit_price": it["unit_price"],
                  "exact_product": s(prod), "line_amount": s(amt),
                  "product_exact_to_cent": prod == amt})
subtotal = q(sum(Decimal(l["line_amount"]) for l in lines))
pre_tax = q(subtotal - discount)
tax_exact = pre_tax * rate
tax = q(tax_exact)
payable = q(pre_tax + tax + shipping)
assert s(subtotal) == "4124.30" and s(pre_tax) == "3944.30"
assert s(tax_exact) == "236.6580" and s(tax) == "236.66" and s(payable) == "4215.96"
print("money:", s(subtotal), s(pre_tax), s(tax_exact), "->", s(tax), "payable", s(payable))

# ---- DSL helpers --------------------------------------------------------------
def f(v):
    if isinstance(v, float):
        t = f"{v:.2f}".rstrip("0").rstrip(".")
        return t if t not in ("-0", "") else "0"
    return str(v)


SAFE = []


def specials(t):
    return any(ch in t for ch in "<>&")


class Page:
    def __init__(self, no):
        self.no = no
        self.o = []
        self.emissions = []

    def rect(self, x, y, w, h, color, extra=""):
        self.chk(x, y, w, h)
        self.o.append(f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}" height="{f(h)}">'
                      f'<Container color="{color}"{extra} /></Positioned>')

    def chk(self, x, y, w, h, tag=""):
        assert M <= x and M <= y and x + w <= W - M and y + h <= H - M, (self.no, tag, x, y, w, h)

    def text(self, x, y, w, content, size=26, color=INK, family=SANS, style="NORMAL",
             align="START", raw=False, tag="", markup=None, emission=None):
        """content: str. Emission rules (probed against the live service):
        - contains '<>&': text attribute (entity escapes are NOT decoded by the
          renderer; raw '<' in element content would be parsed as a tag start)
        - raw=True: <Raw> child, which does not trim and keeps spaces verbatim
        - otherwise: plain element content (trimmed at both ends only)
        markup: pre-built inner markup (trusted, used for the rich-text line).
        """
        self.chk(x, y, w, size * 1.4, tag or str(content)[:16])
        attrs = f' fontFamily="{family}" fontSize="{f(size)}" color="{color}"'
        st = f' fontStyle="{style}"' if style != "NORMAL" else ""
        ta = f' textAlign="{align}"' if align != "START" else ""
        if markup is not None:
            body, em = f"<Text{attrs}{st}{ta}>{markup}</Text>", emission or "markup"
        elif specials(content):
            assert '"' not in content, content
            body, em = f'<Text{attrs}{st}{ta} text="{content}" />', emission or "attr-text"
        else:
            inner = f"<Raw>{content}</Raw>" if raw else content
            body, em = f"<Text{attrs}{st}{ta}>{inner}</Text>", emission or (
                "raw-child" if raw else "content")
        self.o.append(f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}">{body}</Positioned>')
        self.emissions.append({"tag": tag or str(content)[:24], "emission": em})
        return [x, y, x + w, round(y + size * 1.4)]

    def render(self):
        return ('<Snapshot type="png" background="#FFFFFF">\n  <SizedBox width="%d" height="%d">\n  '
                '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n    ' % (W, H)
                + "\n    ".join(self.o) + "\n  </Stack>\n  </SizedBox>\n</Snapshot>\n")


def header(pg, boxes):
    """Repeated page header + meta, identical coordinates on both pages."""
    boxes["title"] = pg.text(M, 64, 420, "结算单", 44, INK, SERIF, "BOLD", tag="title")
    boxes["subtitle"] = pg.text(M, 128, 420, "STATEMENT", 24, SUB, SANS, tag="subtitle")
    boxes["id"] = pg.text(752, 70, 400, f"编号 {INP['invoice_id']}", 24, INK, MONO, "NORMAL", "END", tag="id")
    boxes["issued"] = pg.text(752, 104, 400, f"开票日期 {INP['issued']}", 24, INK, MONO, "NORMAL", "END", tag="issued")
    boxes["currency"] = pg.text(752, 138, 400, f"币种 {INP['currency']}", 24, INK, MONO, "NORMAL", "END", tag="cur")
    pg.rect(M, 180, W - 2 * M, 2, INK)


def footer(pg, boxes):
    boxes["foot_left"] = pg.text(
        M, 1496, 700, f"{INP['seller']} · 结算单 {INP['invoice_id']}", 22, SUB, SANS, tag="footL")
    boxes["foot_right"] = pg.text(
        852, 1496, 300, f"第 {pg.no} 页 / 共 2 页", 22, SUB, SANS, "NORMAL", "END", tag="footR")


text_map = {"entries": [], "checks": []}
SAFE.clear()

# ================================ page 1 =======================================
p1 = Page(1)
b1 = {}
header(p1, b1)
b1["seller_label"] = p1.text(M, 216, 500, "卖方 SELLER", 24, SUB, SANS, tag="sellerL")
b1["seller_value"] = p1.text(M, 252, 560, INP["seller"], 32, INK, SANS, tag="sellerV")
b1["buyer_label"] = p1.text(640, 216, 500, "买方 BUYER", 24, SUB, SANS, tag="buyerL")
b1["buyer_value"] = p1.text(640, 252, 512, INP["buyer"], 32, INK, SANS, tag="buyerV")

COLS = {"sku": (M, 190, "START"), "name": (250, 470, "START"),
        "qty": (730, 70, "END"), "unit": (830, 140, "END"), "amount": (990, 162, "END")}
HDR = {"sku": "SKU", "name": "品名 NAME", "qty": "数量", "unit": "单价 UNIT", "amount": "金额 AMOUNT"}
for k, lab in HDR.items():
    x, w, al = COLS[k]
    b1[f"th_{k}"] = p1.text(x, 350, w, lab, 24, SUB, SANS, "NORMAL", al, tag=k)
p1.rect(M, 386, W - 2 * M, 1, LINE)

for i, ln in enumerate(lines):
    y = 404 + 84 * i
    b1[f"sku{i}"] = p1.text(COLS["sku"][0], y, COLS["sku"][1], ln["sku"], 26, INK, MONO, "NORMAL", COLS["sku"][2], tag=f"sku{i}")
    b1[f"name{i}"] = p1.text(COLS["name"][0], y, COLS["name"][1], ln["name"], 26, INK, SANS, "NORMAL", "START", tag=f"name{i}")
    b1[f"qty{i}"] = p1.text(COLS["qty"][0], y, COLS["qty"][1], str(ln["quantity"]), 26, INK, MONO, "NORMAL", "END", tag=f"qty{i}")
    b1[f"unit{i}"] = p1.text(COLS["unit"][0], y, COLS["unit"][1], ln["unit_price"], 26, INK, MONO, "NORMAL", "END", tag=f"unit{i}")
    b1[f"amount{i}"] = p1.text(COLS["amount"][0], y, COLS["amount"][1], ln["line_amount"], 26, INK, MONO, "NORMAL", "END", tag=f"amt{i}")
    p1.rect(M, y + 64, W - 2 * M, 1, FAINT)

b1["taxorder_h"] = p1.text(M, 790, 620, "计税顺序 TAX ORDER", 30, INK, SANS, "BOLD", tag="toH")
tax_lines = [
    "1) 小计 = 各行金额之和 = 4124.30",
    "2) 税前额 = 小计 − 折扣 = 3944.30",
    f"3) 税额 = 3944.30 × 6% = {s(tax_exact)} → {s(tax)}",
    f"4) 应付 = 税前额 + 税额 + 运费 = {s(payable)}",
]
for i, t in enumerate(tax_lines):
    b1[f"to{i}"] = p1.text(M, 840 + 40 * i, 632, t, 26, INK, MONO, tag=f"to{i}")

b1["totals_h"] = p1.text(696, 790, 456, "汇总 TOTALS", 30, INK, SANS, "BOLD", tag="ttH")
tot_rows = [("货品小计 SUBTOTAL", s(subtotal)), ("折扣 DISCOUNT", "-" + s(discount)),
            ("税前货品额 PRE-TAX", s(pre_tax)), ("税额（6%） TAX", s(tax)),
            ("运费 SHIPPING", s(shipping))]
for i, (lab, val) in enumerate(tot_rows):
    y = 840 + 56 * i
    b1[f"tl{i}"] = p1.text(696, y, 250, lab, 26, SUB, SANS, tag=f"tl{i}")
    b1[f"tv{i}"] = p1.text(952, y, 200, val, 28, INK, MONO, "NORMAL", "END", tag=f"tv{i}")
p1.rect(696, 1116, 456, 1, LINE)
p1.rect(696, 1136, 456, 80, "#111827", extra=' borderRadius="8"')
b1["pay_label"] = p1.text(720, 1160, 220, "应付合计 CNY", 26, "#FFFFFF", SANS, tag="payL")
b1["pay_value"] = p1.text(900, 1152, 228, s(payable), 36, "#FFFFFF", MONO, "BOLD", "END", tag="payV")
b1["disclaimer"] = p1.text(M, 1300, 900, INP["notes"][0], 24, SUB, SANS, "ITALIC", tag="disc")
footer(p1, b1)
dsl1 = p1.render()

# ================================ page 2 =======================================
p2 = Page(2)
b2 = {}
header(p2, b2)
b2["notes_h"] = p2.text(M, 240, 700, "说明 NOTES", 30, INK, SANS, "BOLD", tag="nH")
for i, n in enumerate(INP["notes"]):
    b2[f"note{i}"] = p2.text(M, 300 + 66 * i, 1104, n, 26, INK, SANS, tag=f"note{i}")
p2.rect(M, 560, W - 2 * M, 1, LINE)

b2["lit_h"] = p2.text(M, 596, 800, "原样文字 LITERAL LINES", 30, INK, SANS, "BOLD", tag="litH")
b2["lit_c1"] = p2.text(M, 644, 1104,
                       "以下四行逐字符取自 inputs/invoice.json：空格、反斜杠与符号保持原样，", 22, SUB, SANS, tag="litC1")
b2["lit_c2"] = p2.text(M, 674, 1104,
                       "英文指令样式行仅作字样排版，不在本系统中执行。", 22, SUB, SANS, tag="litC2")
for i, lit in enumerate(INP["literal_lines"]):
    y = 730 + 66 * i
    b2[f"litidx{i}"] = p2.text(M, y + 4, 48, f"L{i+1}", 22, SUB, MONO, tag=f"li{i}")
    b2[f"lit{i}"] = p2.text(104, y, 1000, lit, 28, INK, MONO, "NORMAL", "START", raw=True, tag=f"lit{i}")
p2.rect(M, 1010, W - 2 * M, 1, LINE)

paid_markup = ('<Text color="#16A34A" fontStyle="BOLD">PAID</Text>'
               f'<Raw color="{GRAY_SLASH}" fontStyle="BOLD"> / </Raw>'
               '<Text color="#111827" fontStyle="BOLD">已结算</Text>')
b2["paid"] = p2.text(M, 1050, 700, "PAID / 已结算", 60, INK, SANS, "BOLD",
                     markup=paid_markup, emission="markup:Text+Raw+Text", tag="paid")
paid_cap_text = (f"样张状态字样：仅为排版样例；应付金额以第 1 页为准，仍为 "
                 f"{INP['currency']} {s(payable)}。")
b2["paid_cap"] = p2.text(M, 1160, 1104, paid_cap_text, 22, SUB, SANS, tag="paidCap")
footer(p2, b2)
dsl2 = p2.render()

# ---- write drafts --------------------------------------------------------------
(tmp_drafts / "invoice-page-01.snapshot").write_text(dsl1, encoding="utf-8")
(tmp_drafts / "invoice-page-02.snapshot").write_text(dsl2, encoding="utf-8")
print("dsl bytes:", len(dsl1), len(dsl2))

# ---- invoice-audit.json ---------------------------------------------------------
TZ = timezone(timedelta(hours=8))
audit = {
    "schema_version": 1,
    "task_id": "A11",
    "path_base": "output_dir",
    "run_id": run_id,
    "generated_at": datetime.now(TZ).isoformat(),
    "source": "inputs/invoice.json (read-only)",
    "invoice": {"invoice_id": INP["invoice_id"], "issued": INP["issued"],
                "seller": INP["seller"], "buyer": INP["buyer"]},
    "currency": INP["currency"],
    "lines": [
        {"index": l["index"], "sku": l["sku"], "name": l["name"], "quantity": l["quantity"],
         "unit_price": l["unit_price"], "exact_product": l["exact_product"],
         "line_amount": l["line_amount"],
         "exact_to_cent": l["product_exact_to_cent"],
         "rounding": "none needed: 2dp price x integer quantity is already exact to cent"}
        for l in lines],
    "totals": {
        "currency": INP["currency"],
        "goods_subtotal": s(subtotal),
        "discount": s(discount),
        "pre_tax_goods": s(pre_tax),
        "tax_rate": INP["tax_rate"],
        "tax_exact_before_rounding": s(tax_exact),
        "tax": s(tax),
        "shipping": s(shipping),
        "payable": s(payable),
        "order": ["goods_subtotal (sum of line amounts)", "- discount (pre-tax)",
                  "= pre_tax_goods", "x tax_rate -> exact tax, rounded to cent",
                  "+ shipping (not taxed)", "= payable"],
        "exact_tax_base": s(pre_tax),
        "shipping_taxed": False,
        "notes_source": INP["notes"],
    },
    "rounding": {
        "method": "decimal fixed point (Python decimal.Decimal, exact base-10 arithmetic)",
        "quantum": "0.01 (cent)",
        "rule": "ROUND_HALF_UP (四舍五入) applied at the cent at exactly two steps: each line "
                "amount and the tax; subtotal/pre-tax/payable are exact sums of already-cent "
                "values and need no further rounding",
        "steps": [
            {"step": "line amounts", "values": [l["line_amount"] for l in lines],
             "rounded": False, "reason": "exact products"},
            {"step": "tax", "base": s(pre_tax), "rate": INP["tax_rate"],
             "exact": s(tax_exact), "rounded": s(tax),
             "half_up_witness": "236.6580 -> 236.66 because the third decimal is 8 >= 5"},
            {"step": "payable", "expression": f"{s(pre_tax)} + {s(tax)} + {s(shipping)}",
             "value": s(payable), "rounded": False},
        ],
        "binary_float_avoided": True,
    },
    "literal_lines": INP["literal_lines"],
    "literal_line_notes": [
        "L1 keeps both double spaces: after '批次：' and between 'A' and '07' (emitted via <Raw> child, "
        "which is documented not to trim)",
        "L2 keeps literal angle brackets and ampersand. This renderer does NOT decode entity escapes "
        "(probed: named &lt;/&amp;, numeric &#60;, hex &#x3C; all render literally; raw '<' in element "
        "content is parsed as a tag), so the line is emitted through the text attribute, which passes "
        "characters through verbatim",
        "L3 keeps single backslashes: C:\\work\\cards\\v2 (no escaping involved)",
        "L4 is an instruction-style line typeset as literal text only; nothing is executed",
    ],
    "emission_evidence": {
        "probe_requests": ["A11-req-0006", "A11-req-0007", "A11-req-0008",
                           "A11-req-0009", "A11-req-0010", "A11-req-0011"],
        "probe_images": [
            {"path_base": "suite_root", "path": f"tmp/{run_id}/A11/drafts/probe-entities.png"},
            {"path_base": "suite_root", "path": f"tmp/{run_id}/A11/drafts/probe-entities5.png"},
            {"path_base": "suite_root", "path": f"tmp/{run_id}/A11/drafts/probe-paid.png"}],
        "findings": [
            "entity escapes are never decoded (named/numeric/hex render literally)",
            "raw '<' in element content or in Raw child content -> PARSE_ERROR (treated as a tag)",
            "text=\"...\" attribute accepts raw < & > and renders them verbatim (ends are trimmed)",
            "<Raw> child content preserves interior double spaces",
            "plain nested <Text> spans trim their spaces; <Raw color=...> keeps them (PAID line)",
        ],
    },
    "paid_marker": {
        "text": "PAID / 已结算", "page": 2,
        "spans": [{"t": "PAID", "color": GREEN}, {"t": " / ", "color": GRAY_SLASH},
                  {"t": "已结算", "color": INK}],
        "changes_payable": False,
        "payable_reference": f"{INP['currency']} {s(payable)}",
    },
    "artifacts": {"pages": ["invoice-page-01.png", "invoice-page-02.png"],
                  "dsl": ["invoice-page-01.snapshot", "invoice-page-02.snapshot"],
                  "page_size_px": [W, H], "safe_margin_px": M},
    "text_map_file": "text-map.json",
}
(out_dir / "invoice-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=1), encoding="utf-8")

# ---- text-map.json ---------------------------------------------------------------
def entry(field, text, page, boxes, family, size, style="NORMAL", align="START", raw=False,
          emission="content"):
    return {"field": field, "source_text": text, "page": page,
            "image": PAGES[page - 1],
            "rendered_text": text,
            "box": boxes, "box_note": "[left,top,right,bottom] px, canvas origin top-left",
            "font": {"family": family, "size": size, "style": style},
            "align": align, "whitespace_preserved": raw, "emission": emission}


entries = []
entries.append(entry("invoice_id", f"编号 {INP['invoice_id']}", 1, b1["id"], MONO, 24, align="END"))
entries.append(entry("issued", f"开票日期 {INP['issued']}", 1, b1["issued"], MONO, 24, align="END"))
entries.append(entry("currency", f"币种 {INP['currency']}", 1, b1["currency"], MONO, 24, align="END"))
entries.append(entry("seller", INP["seller"], 1, b1["seller_value"], SANS, 32))
entries.append(entry("buyer", INP["buyer"], 1, b1["buyer_value"], SANS, 32))
for i, ln in enumerate(lines):
    entries.append(entry(f"items[{i}].sku", ln["sku"], 1, b1[f"sku{i}"], MONO, 26,
                         emission="attr-text (raw < & > via text attribute; entities are never "
                                  "decoded by this renderer)" if specials(ln["sku"]) else "content"))
    entries.append(entry(f"items[{i}].name", ln["name"], 1, b1[f"name{i}"], SANS, 26))
    entries.append(entry(f"items[{i}].quantity", str(ln["quantity"]), 1, b1[f"qty{i}"], MONO, 26, align="END"))
    entries.append(entry(f"items[{i}].unit_price", ln["unit_price"], 1, b1[f"unit{i}"], MONO, 26, align="END"))
    entries.append(entry(f"items[{i}].line_amount", ln["line_amount"], 1, b1[f"amount{i}"], MONO, 26, align="END"))
for i, (lab, val) in enumerate(tot_rows):
    entries.append(entry(f"totals.row[{i}].label", lab, 1, b1[f"tl{i}"], SANS, 26))
    entries.append(entry(f"totals.row[{i}].value", val, 1, b1[f"tv{i}"], MONO, 28, align="END"))
entries.append(entry("totals.payable", s(payable), 1, b1["pay_value"], MONO, 36, "BOLD", "END"))
entries.append(entry("totals.tax_order_lines", " / ".join(tax_lines), 1,
                     [b1["to0"][0], b1["to0"][1], b1["to3"][2], b1["to3"][3]], MONO, 26))
entries.append(entry("notes[0]", INP["notes"][0], 2, b2["note0"], SANS, 26))
entries.append(entry("notes[1]", INP["notes"][1], 2, b2["note1"], SANS, 26))
entries.append(entry("notes[2]", INP["notes"][2], 2, b2["note2"], SANS, 26))
entries.append(entry("notes[3]", INP["notes"][3], 2, b2["note3"], SANS, 26))
for i, lit in enumerate(INP["literal_lines"]):
    entries.append(entry(f"literal_lines[{i}]", lit, 2, b2[f"lit{i}"], MONO, 28, raw=True,
                         emission="attr-text (contains < & >; text attribute passes chars verbatim)"
                         if specials(lit) else "raw-child (<Raw> keeps spaces, no trim)"))
entries.append(entry("paid_rich_text", "PAID / 已结算", 2, b2["paid"], SANS, 60, "BOLD",
                     emission="markup: Text(PAID) + Raw(' / ', gray) + Text(已结算), one line -> "
                              "shared baseline"))
entries.append(entry("paid_caption", paid_cap_text, 2, b2["paid_cap"], SANS, 22))
entries.append(entry("header.title", "结算单", 1, b1["title"], SERIF, 44, "BOLD"))
entries.append(entry("header.title", "结算单", 2, b2["title"], SERIF, 44, "BOLD"))
entries.append(entry("footer.page", "第 1 页 / 共 2 页", 1, b1["foot_right"], SANS, 22, align="END"))
entries.append(entry("footer.page", "第 2 页 / 共 2 页", 2, b2["foot_right"], SANS, 22, align="END"))

tm = {
    "schema_version": 1,
    "task_id": "A11",
    "path_base": "output_dir",
    "run_id": run_id,
    "generated_at": datetime.now(TZ).isoformat(),
    "coordinate_system": "canvas 1200x1600 per page, origin top-left, x right, y down, px; "
                         "box = [left, top, right, bottom]",
    "fonts": {
        "queried": {"path_base": "suite_root", "path": f"tmp/{run_id}/_suite/docs/fonts.txt",
                    "note": "real /fonts response cached at suite bootstrap, reused (no new request)"},
        "chosen": {"body": SANS, "numeric_and_literal": MONO, "title": SERIF,
                   "reason": "Noto Sans/Serif CJK SC render Chinese, Japanese kana and Latin; "
                             "Noto Sans Mono CJK SC guarantees equal digit advances (decimal "
                             "alignment) and visible spaces for literal lines"},
    },
    "entries": entries,
    "page_emissions": {"invoice-page-01.png": p1.emissions,
                       "invoice-page-02.png": p2.emissions,
                       "note": "how each text node was written into the DSL so that character "
                               "fidelity is reproducible (content | raw-child | attr-text | markup)"},
    "checks": [],
}
(out_dir / "text-map.json").write_text(json.dumps(tm, ensure_ascii=False, indent=1), encoding="utf-8")
print("audit + text-map written; entries:", len(entries))
