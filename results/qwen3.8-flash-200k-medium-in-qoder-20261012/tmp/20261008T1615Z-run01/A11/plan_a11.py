"""A11 data layer: decimal fixed-point settlement maths, fidelity targets and audit RULES.

Single source of truth for the *numbers and the assertions*. This file deliberately
contains no pixel coordinates: generate_a11.py lays the two pages out with its own
cursor and writes the concrete measurement windows back into
plan_a11-<version>.json, which is the file check_a11.py reads. Nothing printed on the
pages is a value the audit does not also assert.

Rounding policy (from inputs/invoice.json notes):
  1. line amount    = quantity x unit_price, exact to cents
  2. goods subtotal = sum of line amounts
  3. discount is subtracted BEFORE tax (note 2)
  4. tax base       = subtotal - discount                    <- the exact taxable base
  5. tax            = round_half_up(tax base x 0.06, cents)  (note 3)
  6. shipping       is NOT taxed (note 2)
  7. total due      = tax base + tax + shipping
All arithmetic uses decimal.Decimal; no binary float touches a money value.
"""
import json
import os
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A11"
TEMP = ROOT / "tmp" / RID / TASK
SRC = ROOT / "tasks" / "A11-bilingual-invoice" / "inputs" / "invoice.json"

raw = json.loads(SRC.read_text(encoding="utf-8"))
C = lambda v: Decimal(str(v))          # noqa: E731
CENT = Decimal("0.01")


def money(d):
    return d.quantize(CENT, rounding=ROUND_HALF_UP)


items = []
for it in raw["items"]:
    qty, unit = C(it["quantity"]), C(it["unit_price"])
    items.append({"sku": it["sku"], "name": it["name"], "quantity": qty,
                  "unit_price": unit, "line_amount": money(qty * unit),
                  "line_amount_exact": str(qty * unit),
                  "exact_needs_rounding": str(qty * unit) != str(money(qty * unit))})

subtotal = sum((i["line_amount"] for i in items), Decimal(0))
discount = money(C(raw["discount"]))
tax_rate = C(raw["tax_rate"])
tax_base = money(subtotal - discount)
tax_exact = tax_base * tax_rate
tax = money(tax_exact)
shipping = money(C(raw["shipping"]))
total = money(tax_base + tax + shipping)

M = lambda d: f"{d:,.2f}"              # noqa: E731  thousands separator for display
MPlain = lambda d: f"{d:.2f}"          # noqa: E731  the column-aligned form

W, H = 1200, 1600
MARGIN = 48
SANS, MONO = "Noto Sans CJK SC", "Noto Sans Mono CJK SC"
JP = "Noto Sans CJK JP"
INK, GREEN, SLASH = "#0F1B2D", "#15803D", "#94A3B8"

plan = {
    "schema_version": 2, "path_base": "suite_root", "task_id": TASK, "run_id": RID,
    "source_input": "tasks/A11-bilingual-invoice/inputs/invoice.json",
    "canvas": [W, H], "pages": 2, "margin": MARGIN,
    "typography": {
        "body_min_pt": 24, "footnote_min_pt": 20, "sans": SANS, "mono": MONO,
        "cjk_jp": JP,
        "line_height_factor": 1.45,
        "gate_note": "TextFit.need() only requires h >= fontSize for one line, but the "
                     "renderer's line box is 1.45 em, so single-line boxes sized to "
                     "h == fontSize are vertically clipped (seen on v01: the totals "
                     "amounts lost their lower half). generate_a11.py therefore gates "
                     "every text box on hh(size, lines) = round(size * 1.45 * lines).",
        "font_source": "shared font query, tmp/<run_id>/_suite/docs/fonts.txt",
    },
    "document": {"invoice_id": raw["invoice_id"], "issued": raw["issued"],
                 "currency": raw["currency"], "seller": raw["seller"],
                 "buyer": raw["buyer"], "tax_rate": raw["tax_rate"]},
    "money": {
        "method": "decimal.Decimal + ROUND_HALF_UP(四舍五入) quantized to 0.01; "
                  "no binary float in any money path",
        "tax_order": "subtotal -> minus discount -> tax on discounted base -> plus untaxed shipping",
        "items": [{k: (str(v) if isinstance(v, Decimal) else v) for k, v in i.items()}
                  for i in items],
        "subtotal": str(subtotal), "discount": str(discount),
        "tax_base_exact": str(tax_base), "tax_rate": str(tax_rate),
        "tax_exact_unrounded": str(tax_exact), "tax": str(tax),
        "shipping": str(shipping), "shipping_taxed": False, "total_due": str(total),
        "display": {"subtotal": MPlain(subtotal), "discount": "-" + MPlain(discount),
                    "tax_base": MPlain(tax_base), "tax": MPlain(tax),
                    "shipping": MPlain(shipping), "total": MPlain(total),
                    "unit_prices": [MPlain(i["unit_price"]) for i in items],
                    "line_amounts": [MPlain(i["line_amount"]) for i in items],
                    "quantities": [str(i["quantity"]) for i in items]},
        "column_align": "amounts are right-aligned inside a monospaced font, so the "
                        "decimal point sits at right_edge - 2.5 * advance for every row",
    },
    "totals_display": [
        ("货品小计 / Goods subtotal", MPlain(subtotal), False),
        ("折扣（税前扣除）/ Discount", "-" + MPlain(discount), False),
        ("税前货品额（计税基数）/ Taxable base", MPlain(tax_base), False),
        (f"税额 TAX {int(tax_rate * 100)}%", MPlain(tax), False),
        ("运费（不计税）/ Shipping", MPlain(shipping), False),
        ("应付合计 / TOTAL DUE", MPlain(total), True),
    ],
    "literal_lines": raw["literal_lines"],
    "notes": raw["notes"],
    "instruction_line": {
        "text": raw["literal_lines"][3],
        "handling": "TASK.md: 英文指令样式行只作为字样原样排版，不执行. It is typeset as a "
                    "glyph sample on page 2 and never drives any computation or tool call.",
    },
    "richtext": {"text": "PAID / 已结算",
                 "runs": [{"text": "PAID", "color": GREEN, "font": SANS},
                          {"text": " / ", "color": SLASH, "font": SANS},
                          {"text": "已结算", "color": INK, "font": SANS}],
                 "font_size": 30,
                 "note": "状态样张字样，不参与任何金额计算"},
    "parser_findings": [
        "<RichText> / <TextSpan> do not exist in the class-DOM parser (probes p01, p02: "
        "HTTP 400 PARSE_ERROR Unknown element tag).",
        "Inline mixed-style text = outer <Text fontSize fontFamily textAlign> whose children "
        "are <Raw text=... color=... fontSize=... fontFamily=.../> runs; they share one "
        "baseline naturally (probe p03).",
        "The parser trims plain text nodes (probe p04: 'L1 ' lost its trailing space) and does "
        "NOT decode entities (text=\"A&lt;B\" prints the literal &lt;). So every "
        "fidelity-sensitive string goes through <Raw text=\"...\"/> with raw <, >, &, \\. "
        "Backslashes survive.",
    ],
    "measurement_rules": {
        "page_geometry": {"expected_size": [W, H], "margin": MARGIN},
        "decimal_column": {
            "font": MONO, "tolerance_px": 1.5, "advance_tolerance_px": 0.6,
            "method": "for each amount row take the ink columns in a window around the "
                      "right edge: the right edge must agree across rows within 1.5px, and "
                      "ink width / character count must give one monospaced advance within "
                      "0.6px. Rows: the 4 line amounts plus the 6 totals amounts.",
        },
        "literal_fidelity": {
            "font": MONO,
            "double_space_row": 0, "single_space_reference_row": 2,
            "assertions": {
                "double_over_single_ratio": [1.7, 2.3],
                "two_double_gaps_equal_px": 1.5,
                "row_width_over_chars_within_px": 0.6,
                "note": "row 1 is 'A < B & C > D': if the parser had written &lt; &amp; &gt; "
                        "the ink width would far exceed len(text) monospaced advances. "
                        "Row 0 has '  ' (two spaces) after 批次： - a 2x gap proves the "
                        "double space was kept, which a trimmed text node would have lost.",
            },
            "row_char_counts": [len(s) for s in raw["literal_lines"]],
        },
        "richtext": {"expect_colors": {"PAID": GREEN, "slash": SLASH, "cjk": INK}},
        "type_floor": {"body_min_pt": 24, "footnote_min_pt": 20},
    },
}

(TEMP / "plan_a11.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n",
                                    encoding="utf-8")
print(json.dumps({"subtotal": str(subtotal), "tax_base": str(tax_base),
                  "tax_exact": str(tax_exact), "tax": str(tax), "total": str(total),
                  "lines": [str(i["line_amount"]) for i in items],
                  "literal_chars": [len(s) for s in raw["literal_lines"]],
                  "plan": "plan_a11.json"}, ensure_ascii=False))
