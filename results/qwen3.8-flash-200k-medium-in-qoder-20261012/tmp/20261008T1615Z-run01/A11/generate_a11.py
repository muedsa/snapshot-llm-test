"""A11: two 1200x1600 settlement pages built entirely from plan_a11.json.

Page 1  结算与明细: parties, id/date/currency, four SKU rows, the six-line total block,
        the tax chain and a per-line re-check table.
Page 2  说明与原样文字: the four notes, the four literal_lines verbatim, the
        "PAID / 已结算" rich-text status sample and the font/consistency appendix.

Layout is cursor-driven: every text box gets height hh(size, lines) = size*1.45*lines
with `lines` from the same width estimator, so no box is under-sized vertically.
v01 used the shared TextFit.need() rule (single line needs only h >= fontSize) and the
totals amounts came back with their lower half clipped.

Fidelity rules learned by probe (tmp/<run_id>/A11/probes/):
  * the parser has no <RichText>/<TextSpan> tag; inline runs are <Text> + nested <Raw>
    (p03 ok, p01/p02 PARSE_ERROR "Unknown element tag").
  * plain text nodes are trimmed, so a trailing space in "L1 " disappears (p04) ->
    every fidelity-sensitive string goes through <Raw text="..."/>.
  * the parser does NOT decode entities: text="A&lt;B" renders the literal "&lt;" (p04),
    while raw < > & in an attribute render as themselves -> raw characters only.

Every emitted text box is registered in text_map (page/position/size/font) and every
audited string also lands in measurements as a concrete pixel window, which is what
check_a11.py reads.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "_suite" / "scripts"))
from dslkit import Doc, TextFit          # noqa: E402

TASK = "A11"
TEMP = ROOT / "tmp" / RID / TASK
OUT = ROOT / "outputs" / RID / TASK
VERSION = os.environ.get("DSL_VERSION", "v02")
plan = json.loads((TEMP / "plan_a11.json").read_text(encoding="utf-8"))

W, H = plan["canvas"]
MG = plan["margin"]
MON = plan["money"]
DISP = MON["display"]
TY = plan["typography"]
SANS, MONO, JP = TY["sans"], TY["mono"], TY["cjk_jp"]
LF = TY["line_height_factor"]
PAPER, RULE, INK = "#FFFFFF", "#C9D4E4", "#0F1B2D"
DIM, FAINT, ACCENT, GREEN = "#42536B", "#7A8AA0", "#1D4ED8", "#15803D"
BAND = "#F5F8FD"
BODY_MIN, FOOT_MIN = TY["body_min_pt"], TY["footnote_min_pt"]

# table column edges (canvas x). The amount column is END-aligned on amt_r for every
# row, which is what puts all decimal points on one vertical line.
SKU_L, SKU_W = MG + 8, 160
NAME_L, NAME_W = 236, 476
QTY_R, QTY_W = 812, 96
UNIT_R, UNIT_W = 946, 132
AMT_R, AMT_W = W - MG - 8, 176
LAB_X, LAB_W = MG + 256, 520          # totals labels stop short of the amount ink window
HEAD_RULE_Y, BAND_RULE_Y = 132, 226
FOOTER_RULE_Y, PAGE_NO_Y = 1508, 1524
HDR_TOP = 250
GAP = 14


def hh(size, lines=1):
    return round(size * LF * lines)


def raw_attr(s):
    """Attribute value for <Raw text="...">. The parser decodes nothing, so the string
    is written verbatim; only the quote itself would need escaping."""
    assert '"' not in s and "\\'" not in s, s
    return s


text_map = []
fit = TextFit()
windows = {"decimal_column": [], "literal_rows": [], "richtext": None}
p = None


def emit(s, x, y, w, size, color, font, style, align, va, inner, tag, section, page,
         nl, note=None):
    p.pos(x, y, w, hh(size, nl), p.box(w, hh(size, nl), inner=inner, align=va))
    rec = {"page": page, "tag": tag, "section": section,
           "box_canvas_xywh": [round(x, 1), round(y, 1), round(w, 1), hh(size, nl)],
           "font_family": font, "font_size_pt": size, "font_style": style or "NORMAL",
           "text_align": align, "line_box_height": hh(size, nl), "text": s}
    if note:
        rec["note"] = note
    text_map.append(rec)


def gate(tag, s, size, w, max_lines):
    nl = fit.lines(s, size, w)
    fit.check(tag, s, size, w, hh(size, nl), lines=nl)
    if nl > max_lines:
        fit.problems.append(f"{tag}: {s[:26]} needs {nl} lines > allowed {max_lines} "
                            f"at {size}pt in {w}px")
    return nl


def t(s, x, y, w, size, color=INK, font=SANS, style=None, align="START",
      valign="TOP", max_lines=1, tag="", section="", page=None, note=None):
    # START/END are the only alignments this page set uses; CENTER would clip.
    assert align in ("START", "END"), align
    va = {"TOP": "TOP", "MIDDLE": "CENTER", "BOTTOM": "BOTTOM"}[valign]
    va += "_RIGHT" if align == "END" else "_LEFT"
    nl = gate(tag or f"p{page}-{int(x)}-{int(y)}", s, size, w, max_lines)
    a = f'color="{color}" fontSize="{size}" fontFamily="{font}"'
    if style:
        a += f' fontStyle="{style}"'
    if align != "START":
        a += f' textAlign="{align}"'
    emit(s, x, y, w, size, color, font, style, align, va,
         f"<Text {a}>{_body(s)}</Text>", tag, section, page, nl, note)
    return hh(size, nl)


def _body(s):
    """CDATA for < > in plain <Text> nodes (the parser takes them literally)."""
    return f"<![CDATA[{s}]]>" if ("<" in s or ">" in s) else s


def raw_line(runs, x, y, w, size, font=SANS, align="START", valign="TOP",
             max_lines=1, tag="", page=None, section="", note=""):
    """One paragraph made of <Raw> inline runs - the only form that keeps whitespace."""
    est = "".join(rt for rt, _, _ in runs)
    nl = gate(tag, est, size, w, max_lines)
    inner = "".join(f'<Raw text="{raw_attr(rt)}" color="{c}" fontSize="{size}" '
                    f'fontFamily="{f}"/>' for rt, c, f in runs)
    va = {"TOP": "TOP_LEFT", "MIDDLE": "CENTER_LEFT", "BOTTOM": "BOTTOM_LEFT"}[valign]
    if align == "END":
        va = {"TOP": "TOP_RIGHT", "MIDDLE": "CENTER_RIGHT", "BOTTOM": "BOTTOM_RIGHT"}[valign]
    a = f'fontSize="{size}" fontFamily="{font}"'
    if align != "START":
        a += f' textAlign="{align}"'
    emit(est, x, y, w, size, INK, font, None, align, va,
         f"<Text {a}>{inner}</Text>", tag, section, page, nl, note)
    text_map[-1]["inline_runs"] = [{"text": rt, "color": c, "fontFamily": f}
                                   for rt, c, f in runs]
    return hh(size, nl)


def rule(y, x0=MG, x1=W - MG, color=RULE, th=1):
    p.line(x0, y, x1, y, th, color)


def rect(x, y, w, h, color, radius=None, border=None):
    p.pos(x, y, w, h, p.box(w, h, color=color, radius=radius, border=border))


def amount(s, label, y, size, color, style=None, page=1, section="合计", tag=""):
    """END-aligned money cell on the shared right edge + its measurement window."""
    h = t(s, AMT_R - AMT_W, y, AMT_W, size, color, MONO, style, align="END",
          tag=tag or f"p{page}-amt-{label}", page=page, section=section)
    windows["decimal_column"].append(
        {"page": page, "label": label, "text": s, "band_y": [y, y + h],
         "x_range": [AMT_R - 150, AMT_R + 30], "font": MONO, "font_size_pt": size})
    return h


def header(page):
    t("结算单", MG, 44, 320, 34, INK, SANS, "BOLD", tag=f"p{page}-title", page=page,
      section="页眉")
    t("SETTLEMENT STATEMENT", MG, 98, 360, 20, FAINT, tag=f"p{page}-title2", page=page,
      section="页眉")
    t(f"编号 {plan['document']['invoice_id']}", 600, 48, W - MG - 600, 24, INK, MONO,
      align="END", page=page, section="页眉", tag=f"p{page}-id")
    t(f"开票日期 {plan['document']['issued']}    币种 {plan['document']['currency']}",
      600, 90, W - MG - 600, 20, DIM, align="END", page=page, section="页眉",
      tag=f"p{page}-date")
    rule(HEAD_RULE_Y)
    d = plan["document"]
    y = 150
    t("卖方 / Seller", MG, y, 540, 20, FAINT, page=page, section="双方", tag=f"p{page}-s1")
    t(d["seller"], MG, y + hh(20, 1) + 4, 540, 26, INK, f"{SANS},{JP}", page=page,
      section="双方", tag=f"p{page}-s2")
    t("买方 / Buyer", 612, y, 540, 20, FAINT, page=page, section="双方", tag=f"p{page}-b1")
    t(d["buyer"], 612, y + hh(20, 1) + 4, 540, 26, INK, f"{SANS},{JP}", page=page,
      section="双方", tag=f"p{page}-b2")
    rule(BAND_RULE_Y)
    return HDR_TOP


def footer(page):
    rule(FOOTER_RULE_Y)
    t(f"第 {page} 页 / 共 {plan['pages']} 页", MG, PAGE_NO_Y, 320, 20, DIM,
      page=page, section="页脚", tag=f"p{page}-pgno")
    t(f"{plan['document']['invoice_id']} · 货币 {plan['document']['currency']} · "
      f"金额均四舍五入至分", 380, PAGE_NO_Y, W - MG - 380, 20, FAINT, align="END",
      page=page, section="页脚", tag=f"p{page}-pgfoot")


def section_title(s, sub, y, page):
    h = t(s, MG, y, 640, 24, INK, SANS, "BOLD", page=page, section=s,
          tag=f"p{page}-sect-{int(y)}")
    if sub:
        t(sub, AMT_R - 300, y + (hh(24, 1) - hh(20, 1)) // 2, 300, 20, FAINT,
          align="END", page=page, section=s, tag=f"p{page}-sectsub-{int(y)}")
    rule(y + h + 8)
    return y + h + 8 + 12


def page1():
    global p
    p = Doc(W, H, bg=PAPER, font=SANS)
    y = header(1)
    y = section_title("明细 / Line items", f"共 {len(MON['items'])} 行", y, 1)
    # column heads
    hy = y
    heads = [("SKU / 编号", SKU_L, SKU_W, "START"), ("品名 / Description", NAME_L, NAME_W,
              "START"), ("数量", QTY_R - QTY_W, QTY_W, "END"),
             ("单价", UNIT_R - UNIT_W, UNIT_W, "END"),
             ("行金额", AMT_R - AMT_W, AMT_W, "END")]
    for s, x, w, al in heads:
        t(s, x, hy, w, 20, FAINT, align=al, page=1, section="明细表",
          tag=f"p1-head-{x}")
    y = hy + hh(20, 1) + 10
    rule(y, color="#DCE5F1")
    y += 14
    for k, it in enumerate(MON["items"]):
        nlines = fit.lines(it["name"], 24, NAME_W)
        row_h = max(hh(26, 1), hh(24, nlines)) + 22
        if k % 2:
            rect(MG, y - 6, W - 2 * MG, row_h - 6, BAND)
        t(it["sku"], SKU_L, y + (row_h - hh(24, 1)) // 2 - 6, SKU_W, 24, INK, MONO,
          page=1, section="明细表", tag=f"p1-sku{k}")
        t(it["name"], NAME_L, y + (row_h - hh(24, nlines)) // 2 - 6, NAME_W, 24, INK,
          f"{SANS},{JP}", max_lines=3, page=1, section="明细表", tag=f"p1-name{k}")
        t(DISP["quantities"][k], QTY_R - QTY_W, y + (row_h - hh(24, 1)) // 2 - 6, QTY_W,
          24, DIM, MONO, align="END", page=1, section="明细表", tag=f"p1-qty{k}")
        t(DISP["unit_prices"][k], UNIT_R - UNIT_W, y + (row_h - hh(26, 1)) // 2 - 6,
          UNIT_W, 26, DIM, MONO, align="END", page=1, section="明细表", tag=f"p1-unit{k}")
        amount(DISP["line_amounts"][k], f"item{it['sku']}", y + (row_h - hh(26, 1)) // 2 - 6,
               26, INK, page=1, section="明细表", tag=f"p1-amt{k}")
        y += row_h
        rule(y - 8, color="#E8EEF6")
    y += GAP
    # ---- totals
    t("结算 / Settlement", MG, y, 400, 22, FAINT, SANS, "BOLD", page=1, section="合计",
      tag="p1-tot-h")
    y += hh(22, 1) + 10
    for k, (lab, val, hi) in enumerate(plan["totals_display"]):
        size_v = 30 if hi else 26
        size_l = 24 if hi else 22
        row_h = max(hh(size_v, 1), hh(size_l, 1)) + 10
        if hi:
            rect(LAB_X - 16, y - 6, W - 2 * MG - LAB_X + 16, row_h - 2, "#EAF1FF", radius=8)
        t(lab, LAB_X, y, LAB_W, size_l, INK if hi else DIM, SANS,
          "BOLD" if hi else None, max_lines=2, page=1, section="合计", tag=f"p1-tot{k}")
        amount(val, f"total{k}", y + (row_h - hh(size_v, 1)) // 2, size_v,
               ACCENT if hi else INK, "BOLD" if hi else None, page=1, tag=f"p1-totv{k}")
        if k == 2:
            rule(y + row_h - 8, x0=MG + 256, x1=AMT_R, color="#DCE5F1")
        y += row_h
    y += GAP + 6
    # ---- tax chain
    y = section_title("计税顺序（依据 notes 第 2、3 条）", "decimal fixed-point", y, 1)
    chain = [
        ("1", "货品小计 = 3×268.50 + 12×39.90 + 2×580.00 + 1×1680.00", DISP["subtotal"]),
        ("2", "折扣在税前从货品小计扣除", DISP["discount"]),
        ("3", "税前货品额 = 精确计税基数", DISP["tax_base"]),
        ("4", f"税额 = 基数 × {plan['document']['tax_rate']} = "
              f"{MON['tax_exact_unrounded']} → 四舍五入至分", DISP["tax"]),
        ("5", "运费不计税，仅在最后加入应付", DISP["shipping"]),
        ("6", "应付合计 = 计税基数 + 税额 + 运费", DISP["total"]),
    ]
    for k, (no, desc, val) in enumerate(chain):
        h = t(no, MG, y, 26, 22, FAINT, MONO, page=1, section="计税过程", tag=f"p1-ch{k}n")
        dh = t(desc, MG + 36, y, 780, 24, DIM, page=1, section="计税过程", tag=f"p1-ch{k}")
        ah = amount(val, f"chain{k}", y, 24, INK, page=1, section="计税过程",
                    tag=f"p1-chv{k}")
        y += max(h, dh, ah) + 8
    t("数据来源：inputs/invoice.json。本页金额均为十进制定点计算，逐项复核与"
      "原样文字见第二页。", MG, y + GAP + 6, 1104, 20,
      FAINT, max_lines=2, page=1, section="脚注", tag="p1-note")
    footer(1)
    return y


def page2():
    global p
    p = Doc(W, H, bg=PAPER, font=SANS)
    y = header(2)
    y = section_title("说明 / Notes", "来自 inputs 原文", y, 2)
    for k, note in enumerate(plan["notes"]):
        nl = fit.lines(note, 24, 1060)
        hh_ = hh(24, nl) + 10
        t(str(k + 1), MG, y, 26, 24, FAINT, MONO, page=2, section="说明", tag=f"p2-n{k}i")
        t(note, MG + 36, y, 1060, 24, INK, f"{SANS},{JP}", max_lines=3, page=2,
          section="说明", tag=f"p2-n{k}")
        y += hh_ + 6
    y += GAP
    y = section_title("原样文字 / Literal lines", "逐字符保真", y, 2)
    box_h = sum(hh(24, fit.lines(s, 24, 1040)) for s in plan["literal_lines"]) \
        + (len(plan["literal_lines"]) - 1) * 10 + 24
    rect(MG, y, W - 2 * MG, box_h, BAND, radius=8, border=f"1 SOLID {RULE}")
    ly = y + 12
    for k, s in enumerate(plan["literal_lines"]):
        h = raw_line([(s, INK, MONO)], MG + 20, ly, 1040, 24, font=MONO, page=2,
                     section="原样文字", tag=f"p2-lit{k}",
                     note="verbatim glyph sample; no entity decoding, no trimming")
        windows["literal_rows"].append(
            {"page": 2, "index": k, "text": s, "band_y": [ly, ly + h],
             "x_range": [MG + 20, W - MG], "font": MONO, "font_size_pt": 24,
             "char_count": len(s)})
        ly += h + 10
    y = ly + 12
    litnote = ("上列四行按输入原样排版：批次行 批次： 之后的两个空格仍然保留（等宽双空格宽度≈单空格"
               "两倍），路径里的反斜杠、A < B & C > D 中的尖括号与 & 都按字形直接显示，没有被写成 "
               "&lt; / &amp; / &gt;。第四行是英文指令样式字样，只作为待排版数据处理，不执行。")
    t(litnote, MG, y, 1104, 20, FAINT, max_lines=4, page=2, section="原样文字",
      tag="p2-litnote")
    y += hh(20, fit.lines(litnote, 20, 1104)) + GAP
    y = section_title("状态样张 / status sample", "inline <Raw> runs", y, 2)
    runs = [(r["text"], r["color"], r["font"]) for r in plan["richtext"]["runs"]]
    h = raw_line(runs, MG, y, 500, plan["richtext"]["font_size"], page=2,
                 section="富文本", tag="p2-rich",
                 note="three inline runs, one shared baseline")
    windows["richtext"] = {"page": 2, "y": y, "band_y": [y, y + h],
                           "x_range": [MG, MG + 500],
                           "runs": [{"text": r["text"], "color": r["color"]}
                                    for r in plan["richtext"]["runs"]],
                           "expect_colors": plan["measurement_rules"]["richtext"]["expect_colors"]}
    t("样张不参与计算：应付合计仍为 "
      f"{DISP['total']} {plan['document']['currency']}。", MG + 520, y + 4, 584, 20,
      FAINT, max_lines=2, page=2, section="富文本", tag="p2-richnote")
    y += h + GAP
    y = section_title("行金额复核（数量 × 单价 = 行金额）", "decimal re-check", y, 2)
    for k, it in enumerate(MON["items"]):
        expr = f"{it['quantity']} × {DISP['unit_prices'][k]}"
        tail = "   精确值已至分，无需舍入" if not it["exact_needs_rounding"] \
            else "   精确值需舍入至分"
        h = raw_line([(expr, DIM, MONO), ("  =  ", FAINT, MONO),
                      (it["line_amount_exact"], INK, MONO), (tail, FAINT, SANS)],
                     MG, y, 1104, 24, tag=f"p2-rc{k}", page=2, section="行金额复核",
                     note="inline <Raw> runs share one baseline")
        y += h + 8
    y += GAP
    y = section_title("字体与跨页一致性", "fonts / consistency", y, 2)
    rows = [("中文与拉丁正文", SANS, "服务字体清单实测"),
            ("日文假名（契約レビュー）", JP, "与中文同段回退"),
            ("编号、数量、单价、行金额、原样文字", MONO, "等宽，小数点同列")]
    for k, (use, font, note) in enumerate(rows):
        h1 = t(use, MG, y, 420, 22, DIM, max_lines=2, page=2, section="附录", tag=f"p2-f{k}")
        h2 = t(font, MG + 430, y, 300, 20, FAINT, MONO, max_lines=2, page=2,
               section="附录", tag=f"p2-fb{k}")
        t(note, MG + 740, y, 364, 20, FAINT, align="END", max_lines=2, page=2,
          section="附录", tag=f"p2-fc{k}")
        y += max(h1, h2) + 10
    t("两页共用同一页眉、双方信息与编号；页码见每页页脚。", MG, y + 6, 800, 20, FAINT,
      max_lines=2, page=2, section="附录", tag="p2-consist")
    footer(2)
    return y


report = {}
BODY_LIMIT = FOOTER_RULE_Y - 42       # body copy must clear the footer rule + page no.
for page, build in ((1, page1), (2, page2)):
    fit = TextFit()
    final_y = build()
    for e in text_map:
        if e["page"] == page and e["section"] not in ("页脚",) and \
                e["box_canvas_xywh"][1] + e["box_canvas_xywh"][3] > BODY_LIMIT:
            fit.problems.append(f"overflow: p{page} {e['tag']} bottom "
                                f"{e['box_canvas_xywh'][1] + e['box_canvas_xywh'][3]} "
                                f"> {BODY_LIMIT}")
    dsl = p.dsl()
    elements = len(re.findall(r"<[A-Za-z]", dsl))
    assert elements <= 4000, elements
    sizes = [int(s) for s in re.findall(r'fontSize="(\d+)"', dsl)]
    report[page] = {"version": VERSION, "page": page, "bytes": len(dsl.encode("utf-8")),
                    "elements": elements, "text_items": fit.n,
                    "body_bottom_cursor_y": round(final_y, 1),
                    "fit_problems": fit.problems, "min_font_pt": min(sizes),
                    "max_font_pt": max(sizes),
                    "fonts_used": sorted(set(re.findall(r'fontFamily="([^"]+)"', dsl)))}
    assert min(sizes) >= FOOT_MIN, min(sizes)
    assert max(sizes) <= 44
    (TEMP / f"fit-report-p{page}-{VERSION}.json").write_text(
        json.dumps(report[page], ensure_ascii=False, indent=1), encoding="utf-8")
    (TEMP / f"page{page}-{VERSION}.snapshot").write_text(dsl, encoding="utf-8")
    print(json.dumps(report[page], ensure_ascii=False))

plan["layout_produced_by"] = f"generate_a11.py {VERSION}"
plan["columns"] = {"sku": [SKU_L, SKU_W], "name": [NAME_L, NAME_W], "qty": [QTY_R, QTY_W],
                   "unit": [UNIT_R, UNIT_W], "amount_right_edge": AMT_R}
mr = plan["measurement_rules"]
plan["measurements"] = {
    "note": "check_a11.py 不含任何硬编码像素位置；以下窗口全部由 generate_a11.py "
            f"{VERSION} 的游标版面实测写出",
    "page_geometry": {"expected_size": [W, H], "margin": MG,
                      "rule_y": [HEAD_RULE_Y, BAND_RULE_Y, FOOTER_RULE_Y]},
    "decimal_column": {"font": MONO, "right_edge_canvas_x": AMT_R,
                       "tolerance_px": mr["decimal_column"]["tolerance_px"],
                       "advance_tolerance_px": mr["decimal_column"]["advance_tolerance_px"],
                       "method": mr["decimal_column"]["method"],
                       "rows": windows["decimal_column"]},
    "literal_fidelity": {"font": MONO,
                         "double_space_row": mr["literal_fidelity"]["double_space_row"],
                         "single_space_reference_row":
                             mr["literal_fidelity"]["single_space_reference_row"],
                         "assertions": mr["literal_fidelity"]["assertions"],
                         "row_char_counts": mr["literal_fidelity"]["row_char_counts"],
                         "rows": windows["literal_rows"]},
    "richtext": windows["richtext"],
    "type_floor": mr["type_floor"],
}
plan["text_map"] = text_map

(TEMP / f"plan_a11-{VERSION}.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1),
                                               encoding="utf-8")
if VERSION == "final":
    OUT.mkdir(parents=True, exist_ok=True)
    for page in (1, 2):
        (OUT / f"invoice-page-{page:02d}.snapshot").write_text(
            (TEMP / f"page{page}-{VERSION}.snapshot").read_text(encoding="utf-8"),
            encoding="utf-8")
    (OUT / "text-map.json").write_text(json.dumps(
        {"schema_version": 2, "path_base": "suite_root", "task_id": TASK, "run_id": RID,
         "generated_by": f"generate_a11.py {VERSION}",
         "line_box_rule": f"height = round(fontSize * {LF} * lines)",
         "note": "每段文字的页面/位置/字号/字体；box_canvas_xywh 为画布坐标",
         "entries": text_map}, ensure_ascii=False, indent=1), encoding="utf-8")
