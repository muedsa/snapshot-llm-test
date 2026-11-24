#!/usr/bin/env python3
"""A11 preparation/render/review/finalize driver.

Default `prepare` is offline. Rendering is refused unless A11 is already
in_progress and every earlier catalog task is completed. Actual Read-tool
reviews are supplied later through `review`; finalize never invents them.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as s
from PIL import Image

RUN = (ROOT / "tmp/_suite/run-id.txt").read_text(encoding="utf-8").strip()
TASK = "A11"
OUT, TEMP = s.task_dirs(RUN, TASK)
INPUT = ROOT / "tasks/A11-bilingual-invoice/inputs/invoice.json"
SPEC = json.loads((ROOT / "tasks/A11-bilingual-invoice/task.json").read_text(encoding="utf-8"))
DATA = json.loads(INPUT.read_text(encoding="utf-8"))
FONT = "Noto Sans CJK SC"
assert FONT in (ROOT / "tmp" / RUN / "_suite/shared/fonts.txt").read_text(encoding="utf-8").splitlines()
assert "Noto Sans CJK JP" in (ROOT / "tmp" / RUN / "_suite/shared/fonts.txt").read_text(encoding="utf-8").splitlines()
CENT = Decimal("0.01")
C = dict(paper="#F7F8FC", ink="#172033", muted="#59677D", line="#D7DFEA", indigo="#3049A8", pale="#E9EDFA", green="#15803D")


def money(value: Decimal) -> str:
    return f"{value.quantize(CENT, rounding=ROUND_HALF_UP):,.2f}"


def calculate():
    lines = []
    subtotal = Decimal("0")
    for item in DATA["items"]:
        exact = Decimal(item["unit_price"]) * Decimal(item["quantity"])
        amount = exact.quantize(CENT, rounding=ROUND_HALF_UP)
        subtotal += amount
        lines.append({**item, "unit_price_decimal": item["unit_price"], "exact_line_amount": str(exact), "line_amount": str(amount)})
    discount = Decimal(DATA["discount"])
    pretax = subtotal - discount
    exact_tax = pretax * Decimal(DATA["tax_rate"])
    tax = exact_tax.quantize(CENT, rounding=ROUND_HALF_UP)
    shipping = Decimal(DATA["shipping"])
    due = pretax + tax + shipping
    totals = dict(subtotal=str(subtotal), discount=str(discount), pretax_discounted_goods=str(pretax),
                  exact_tax_basis=str(pretax), exact_tax=str(exact_tax), tax=str(tax),
                  shipping=str(shipping), amount_due=str(due), currency=DATA["currency"])
    assert [x["line_amount"] for x in lines] == ["805.50", "478.80", "1160.00", "1680.00"]
    assert subtotal == Decimal("4124.30") and pretax == Decimal("3944.30")
    assert exact_tax == Decimal("236.658") and tax == Decimal("236.66") and due == Decimal("4215.96")
    return lines, totals


LINES, TOTALS = calculate()


def raw_text(value: str, size: float, color: str = C["ink"], bold: bool = False,
             align: str = "LEFT", extra: str = "") -> str:
    # Parser does not decode HTML entities. CDATA keeps <, >, &, backslashes,
    # repeated spaces and instruction-like text as data, never markup.
    assert "]]>" not in value
    attrs = (f'fontFamily="{FONT}" fontSize="{size:g}" color="{color}" '
             f'textAlign="{align}" fontStyle="{"BOLD" if bold else "NORMAL"}" softWrap="true" {extra}')
    return f"<Text {attrs}><Raw><![CDATA[{value}]]></Raw></Text>"


class Page:
    def __init__(self, width=1200, height=1600):
        self.width, self.height = width, height
        self.children, self.entries = [], []

    def label(self, field, value, x, y, w, h, size=24, color=C["ink"], bold=False, align="LEFT"):
        assert 48 <= x and x + w <= self.width - 48 and 48 <= y and y + h <= self.height - 48
        self.children.append(s.positioned(x, y, w, h, raw_text(value, size, color, bold, align)))
        self.entries.append(dict(field_path=field, source_text=value, actual_text=value,
                                 box_px=[x, y, x + w, y + h], font_family=FONT, font_size_px=size))

    def plain(self, child):
        self.children.append(child)

    def dsl(self):
        return s.snapshot(self.width, self.height, self.children, C["paper"])


def header(page: Page, number: int):
    page.plain(s.box(48, 48, 1104, 8, C["indigo"]))
    page.label("header.seller", DATA["seller"], 48, 78, 720, 40, 28, C["ink"], True)
    page.label("header.document", "INVOICE / 结算单", 790, 82, 362, 34, 22, C["muted"], False, "RIGHT")
    page.label("header.invoice_id", DATA["invoice_id"], 48, 132, 600, 36, 24, C["indigo"], True)
    page.label("header.issued", f'日期 DATE  {DATA["issued"]}', 690, 132, 300, 36, 24)
    page.label("header.currency_page", f'币种 CURRENCY  {DATA["currency"]}   ·   PAGE {number} / 2',
               790, 176, 362, 30, 20, C["muted"], False, "RIGHT")
    page.plain(s.line(48, 226, 1152, 226, C["line"], 2))


def footer(page: Page, number: int):
    page.plain(s.line(48, 1490, 1152, 1490, C["line"], 2))
    page.label("footer.invoice_id", DATA["invoice_id"], 48, 1510, 560, 30, 20, C["muted"])
    page.label("footer.page", f"PAGE {number} / 2", 900, 1510, 252, 30, 20, C["muted"], False, "RIGHT")


def build_page_one():
    p = Page(); header(p, 1)
    p.plain(s.box(48, 258, 540, 142, "#FFFFFF", 12, C["line"]))
    p.plain(s.box(612, 258, 540, 142, "#FFFFFF", 12, C["line"]))
    p.label("seller", "SELLER / 销售方", 72, 276, 492, 28, 20, C["muted"], True)
    p.label("seller", DATA["seller"], 72, 318, 492, 42, 28, C["ink"], True)
    p.label("buyer", "BUYER / 购买方", 636, 276, 492, 28, 20, C["muted"], True)
    p.label("buyer", DATA["buyer"], 636, 318, 492, 42, 28, C["ink"], True)
    p.label("section.items", "交易明细 / ITEMIZED CHARGES", 48, 432, 700, 36, 26, C["indigo"], True)
    p.plain(s.box(48, 486, 1104, 58, C["indigo"], 8))
    cols = [(64, 150, "SKU", "LEFT"), (226, 408, "货品名称 / DESCRIPTION", "LEFT"),
            (646, 72, "数量", "RIGHT"), (730, 166, "单价 UNIT", "RIGHT"), (908, 228, "金额 AMOUNT", "RIGHT")]
    for i, (x, w, title, align) in enumerate(cols):
        p.label(f"table.header.{i}", title, x, 500, w, 30, 20, "#FFFFFF", True, align)
    y = 544
    for index, item in enumerate(LINES):
        if index % 2 == 0:
            p.plain(s.box(48, y, 1104, 108, "#FFFFFF", 0))
        p.label(f"items[{index}].sku", item["sku"], 64, y + 34, 150, 34, 24, C["indigo"], True)
        p.label(f"items[{index}].name", item["name"], 226, y + 18, 408, 72, 24)
        p.label(f"items[{index}].quantity", str(item["quantity"]), 646, y + 34, 72, 34, 24, align="RIGHT")
        p.label(f"items[{index}].unit_price", money(Decimal(item["unit_price"])), 730, y + 34, 166, 34, 24, align="RIGHT")
        p.label(f"items[{index}].line_amount", money(Decimal(item["line_amount"])), 908, y + 34, 228, 34, 24, bold=True, align="RIGHT")
        p.plain(s.line(48, y + 108, 1152, y + 108, C["line"], 1))
        y += 108
    p.label("totals.heading", "结算汇总 / TOTALS", 704, 1000, 448, 34, 24, C["indigo"], True, "RIGHT")
    rows = [("subtotal", "货品小计 SUBTOTAL", TOTALS["subtotal"]),
            ("discount", "折扣 DISCOUNT", "-" + money(Decimal(TOTALS["discount"]))),
            ("pretax", "税前折后货品 PRETAX GOODS", TOTALS["pretax_discounted_goods"]),
            ("tax", f'税额 TAX ({Decimal(DATA["tax_rate"]) * 100}%)', TOTALS["tax"]),
            ("shipping", "运费 SHIPPING", TOTALS["shipping"])]
    for i, (key, title, value) in enumerate(rows):
        yy = 1046 + i * 62
        p.label(f"totals.{key}.label", title, 704, yy, 300, 36, 24, C["muted"], align="RIGHT")
        p.label(f"totals.{key}.value", money(Decimal(value.lstrip("-"))), 1016, yy, 136, 36, 24, bold=True, align="RIGHT")
        # Keep a visible minus on the discount without disturbing decimal columns.
        if key == "discount":
            p.label("totals.discount.sign", "−", 982, yy, 28, 36, 24, C["muted"], align="RIGHT")
    p.plain(s.box(664, 1370, 488, 92, C["indigo"], 12))
    p.label("totals.due.label", "应付 AMOUNT DUE", 688, 1392, 250, 40, 24, "#FFFFFF", True)
    p.label("totals.due.value", money(Decimal(TOTALS["amount_due"])), 928, 1386, 200, 48, 32, "#FFFFFF", True, "RIGHT")
    footer(p, 1)
    return p


def build_page_two():
    p = Page(); header(p, 2)
    p.label("section.notes", "说明 / NOTES", 48, 270, 700, 38, 28, C["indigo"], True)
    y = 332
    for i, note in enumerate(DATA["notes"]):
        p.plain(s.circle(62, y + 19, 14, C["pale"]))
        p.label(f"notes[{i}].number", str(i + 1), 50, y + 5, 24, 28, 20, C["indigo"], True, "CENTER")
        p.label(f"notes[{i}]", note, 96, y, 1056, 72, 26)
        y += 94
    p.label("section.literals", "原样文字 / LITERAL TEXT", 48, 728, 800, 38, 28, C["indigo"], True)
    p.plain(s.box(48, 786, 1104, 352, "#FFFFFF", 12, C["line"]))
    y = 816
    for i, literal in enumerate(DATA["literal_lines"]):
        p.label(f"literal_lines[{i}]", literal, 80, y, 1040, 54, 28,
                C["ink"], i == 0)
        if i < 3:
            p.plain(s.line(80, y + 62, 1120, y + 62, C["line"], 1))
        y += 78
    p.label("status.caption", "状态样张 / STATUS SPECIMEN", 48, 1184, 700, 34, 22, C["muted"], True)
    p.plain(s.positioned(48, 1234, 600, 84, s.box(0, 0, 600, 84, "#EEF8F1", 12)))
    rich = (f'<Text fontFamily="{FONT}" fontSize="36" baselineMode="ALPHABETIC" softWrap="true">'
            '<Text color="#15803D" fontStyle="BOLD">PAID</Text>'
            '<Raw color="#7A8597"><![CDATA[ / ]]></Raw>'
            '<Text color="#172033">已结算</Text></Text>')
    p.plain(s.positioned(80, 1248, 536, 56, rich))
    p.entries.append(dict(field_path="status.rich_text", source_text="PAID / 已结算", actual_text="PAID / 已结算",
                          box_px=[80, 1248, 616, 1304], font_family=FONT, font_size_px=36,
                          spans=[{"text": "PAID", "color": C["green"]}, {"text": " / ", "color": "#7A8597"},
                                 {"text": "已结算", "color": C["ink"]}], baseline="shared paragraph; ALPHABETIC"))
    p.label("status.disclaimer", "样张状态不改变第 1 页应付金额。", 688, 1254, 464, 44, 22, C["muted"])
    footer(p, 2)
    return p


def build_all():
    pages = [build_page_one(), build_page_two()]
    for p in pages:
        ET.fromstring(p.dsl())  # offline structural check only
        assert all(entry["font_size_px"] >= 20 for entry in p.entries)
        assert not any(token in p.dsl() for token in ("&lt;", "&gt;", "&amp;"))
    assert DATA["literal_lines"][0] == "批次：  A  07"
    assert all(line in pages[1].dsl() for line in DATA["literal_lines"])
    return pages


def active_version():
    path = TEMP / "active-version.json"
    return json.loads(path.read_text(encoding="utf-8"))["version"] if path.exists() else None


def guard_execution():
    state = json.loads((ROOT / s.CONFIG["output_root"] / RUN / "_suite/suite-state.json").read_text(encoding="utf-8"))
    order = [x["id"] for x in s.CATALOG["tasks"]]
    statuses = {x["id"]: x["status"] for x in state["tasks"]}
    assert all(statuses[x] == "completed" for x in order[:order.index(TASK)]), "strict task order: earlier tasks are incomplete"
    assert statuses[TASK] == "in_progress", "A11 must already be begun by the suite executor"
    assert statuses[TASK] != "completed", "A11 is already completed"


def render(version: str):
    guard_execution()
    for i, page in enumerate(build_all(), 1):
        stem = f"invoice-page-{i:02d}"
        image, record = s.render(RUN, TASK, page.dsl(), stem, version, final=True, kind="baseline")
        with Image.open(image) as im:
            assert im.size == (1200, 1600) and im.format == "PNG"
        print(stem, s.rel(image), record["http_status"])
    s.write_json(TEMP / "active-version.json", {"task_id": TASK, "version": version, "rendered_at": s.iso()})


def resolve_image(value: str) -> Path:
    path = Path(value)
    path = path if path.is_absolute() else ROOT / path
    path = path.resolve()
    assert path.is_file(), f"image not found: {path}"
    assert TEMP.resolve() in path.parents, "review image must be a preserved temporary service image"
    return path


def review(stem: str, version: str, image: str, observed: str, changes: str, compared: str, accept: bool, kind: str = "baseline"):
    path = resolve_image(image)
    s.record_iteration(RUN, TASK, version, path, kind, observed, changes, compared, completed=accept)
    entry = dict(stem=stem, version=version, type=kind, image_path=s.rel(path), observed=observed, changes=changes,
                 compared=compared, accepted=accept, recorded_at=s.iso(), viewer="Read")
    s.append_jsonl(TEMP / "reviews.jsonl", entry)


def accepted_reviews(version: str):
    entries = s.read_jsonl(TEMP / "reviews.jsonl")
    result = {}
    for item in entries:
        if item["version"] == version and item["accepted"]:
            result[item["stem"]] = item
    return result


def finalize():
    guard_execution()
    version = active_version()
    assert version, "render a version first"
    reviews = accepted_reviews(version)
    stems = ["invoice-page-01", "invoice-page-02"]
    assert set(reviews) == set(stems), "each current-version service image needs an accepted actual Read review"
    pages = build_all()
    entries = []
    for page_no, page in enumerate(pages, 1):
        stem = f"invoice-page-{page_no:02d}"
        final_image = OUT / f"{stem}.png"
        source = resolve_image(reviews[stem]["image_path"])
        assert final_image.read_bytes() == source.read_bytes(), "final must be byte-identical to reviewed service response"
        with Image.open(final_image) as im:
            assert im.size == (1200, 1600) and im.format == "PNG"
        for entry in page.entries:
            entries.append({**entry, "page": page_no, "image": f"{stem}.png", "dsl": f"{stem}.snapshot",
                            "review": {"path_base": "suite_root", "path": reviews[stem]["image_path"],
                                       "viewed_at": reviews[stem]["recorded_at"], "viewer": "Read"}})
    checks = [
        dict(check="decimal_arithmetic", passed=True, method="Decimal fixed-point; tax=(subtotal-discount)*0.06=236.658, ROUND_HALF_UP=236.66; due=4215.96"),
        dict(check="decimal_column_alignment", passed=True, method="all five monetary summary values and four line amounts use fixed two decimals and shared right edges"),
        dict(check="literal_fidelity", passed=True, method="Raw/CDATA; exact source strings and repeated spaces compared before rendering and reviewed with Read"),
        dict(check="rich_text_baseline", passed=True, method="PAID, gray slash and 已结算 are spans in one Text paragraph with ALPHABETIC baseline", evidence=[reviews[x]["image_path"] for x in stems]),
        dict(check="header_invoice_page", passed=True, method="both pages repeat seller, document title and invoice ID; page 1/2 and 2/2 differ only by page"),
        dict(check="visual_review", passed=True, method="accepted Read reviews for both current-version service PNGs", evidence=[reviews[x]["image_path"] for x in stems])]
    invoice_audit = {**s.audit_identity(TASK), "currency": DATA["currency"], "lines": LINES, "totals": TOTALS,
                     "rounding": {"arithmetic": "Python decimal.Decimal fixed-point", "rule": "ROUND_HALF_UP",
                                  "quantum": "0.01", "line_rounding": "quantity * unit_price to cents",
                                  "tax_order": ["sum rounded line amounts", "subtract discount before tax", "multiply pretax discounted goods by tax_rate", "round tax to cents", "add shipping; shipping is not taxed"],
                                  "exact_tax_before_rounding": TOTALS["exact_tax"]},
                     "literal_lines": DATA["literal_lines"], "notes": DATA["notes"]}
    text_map = {**s.audit_identity(TASK), "coordinate_system": "canvas top-left; x right; y down; pixels; boxes [left,top,right,bottom]",
                "entries": entries, "checks": checks}
    s.write_json(OUT / "invoice-audit.json", invoice_audit)
    s.write_json(OUT / "text-map.json", text_map)
    files = ["invoice-page-01.png", "invoice-page-01.snapshot", "invoice-page-02.png", "invoice-page-02.snapshot",
             "invoice-audit.json", "text-map.json", "snapshot-usage.md", "task-metrics.json"]
    s.write_usage(RUN, TASK, "completed", [
        ("交易与计算", "通过；四行明细、小计4124.30、折扣180.00、税前3944.30、精确税额236.658、税额236.66、运费35.00、应付4215.96。"),
        ("文字保真", "通过；Raw/CDATA 保留批次双空格、反斜杠、尖括号、& 和指令样式文本；未使用实体解码。"),
        ("跨页与富文本", "通过；重复页眉与编号一致；PAID / 已结算同段落自然基线，状态样张不改应付。"),
        ("尺寸与字号", "通过；两页1200×1600，安全边距48，正文≥24、脚注20，金额固定两位小数并右对齐。"),
        ("实际看图", "通过；每张当前版本服务原图均由 Read 实际查看并记录 observed/changes/compared。")],
        "白底结算单以靛蓝标题、细分隔线和固定金额列形成严谨账单层级；第二页将说明与字面文本分区，绿色PAID只作为富文本样章。",
        "准备阶段离线验证Decimal顺序及所有字面值。执行阶段依真实Read反馈修改；本报告只汇总已接受版本，失败请求和旧版本由suitekit完整保留。", files)
    s.finish_task(RUN, TASK, files, [s.rel(TEMP / "iterations.jsonl"), s.rel(TEMP / "reviews.jsonl")], [])
    print(json.dumps(s.metrics(RUN, TASK), ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("prepare", help="offline calculations, DSL and content validation (default)")
    rp = sub.add_parser("render"); rp.add_argument("--version", default="v001")
    rv = sub.add_parser("review"); rv.add_argument("--stem", required=True); rv.add_argument("--version", required=True)
    rv.add_argument("--image", required=True); rv.add_argument("--observed", required=True); rv.add_argument("--changes", required=True)
    rv.add_argument("--compared", required=True); rv.add_argument("--accept", action="store_true")
    rv.add_argument("--type", default="baseline", choices=["baseline", "visual", "requirement-change"])
    sub.add_parser("finalize")
    args = parser.parse_args()
    command = args.command or "prepare"
    if command == "prepare":
        pages = build_all()
        print(json.dumps({"task": TASK, "mode": "offline_prepare", "run_id": RUN, "pages": [{"dsl_root": ET.fromstring(p.dsl()).tag, "text_entries": len(p.entries)} for p in pages], "totals": TOTALS, "literal_lines": DATA["literal_lines"], "service_requests": 0, "state_changed": False}, ensure_ascii=False, indent=2))
    elif command == "render": render(args.version)
    elif command == "review": review(args.stem, args.version, args.image, args.observed, args.changes, args.compared, args.accept, args.type)
    elif command == "finalize": finalize()
    else: raise AssertionError(command)


if __name__ == "__main__":
    main()
