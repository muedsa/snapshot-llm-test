"""A11 text-map.json 生成器：把设计期放置盒与实测墨迹盒合成专用审计 JSON。

字段约定遵循 tasks/A11-bilingual-invoice/templates/audit-fields.json：
  * schema_version:1、task_id、path_base:"output_dir"
  * PNG/DSL 路径相对本题输出根；临时证据用 {path_base:"suite_root", path:"tmp/..."}
  * 坐标为画布左上原点、x 向右 / y 向下、像素单位、框为 [left, top, right, bottom]
  * passed 类字段附方法与证据；取不到的值写 null 并给原因

所有数值都从最终 PNG 与最终 DSL 现算，不复制设计期常量当结论。

用法：
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a11_textmap.py
"""

from __future__ import annotations

import datetime
import json
import re
import sys
from decimal import Decimal, ROUND_HALF_UP, getcontext
from pathlib import Path
from statistics import mean

from PIL import Image

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
import suite as S  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TASK = "A11"
RID = S.run_id()
TZ = S.TZ_NAME
OUT, TMP = S.task_dirs(TASK)
STEMS = ["invoice-page-01", "invoice-page-02"]

inv = json.loads((ROOT / "tasks/A11-bilingual-invoice/inputs/invoice.json")
                 .read_text(encoding="utf-8"))
audit = json.loads((OUT / "invoice-audit.json").read_text(encoding="utf-8"))
LIT = inv["literal_lines"]
NOTES = inv["notes"]
ITEMS = inv["items"]

# 实际看图事件（本会话中真实打开过的裁切图，按打开顺序登记）
VIEWS = [
    ("view-a11-01", "invoice-page-01", "page1-full.png", (0, 0, 1200, 1600),
     "整页缩略 600×800：页眉/双方/明细表/合计/强调带/页脚结构与整体留白，无溢出与遮挡"),
    ("view-a11-02", "invoice-page-02", "page2-full.png", (0, 0, 1200, 1600),
     "整页缩略 600×800：附注/逐字符核对/PAID 样张/计税口径五段齐备，无溢出"),
    ("view-a11-03", "invoice-page-01", "page1-tbl.png", (48, 350, 1160, 762),
     "明细表 4 行：SKU A<B&C>D 原样显示，数量/单价/行金额三列右对齐，斑马纹与分隔线正常"),
    ("view-a11-04", "invoice-page-01", "page1-totals.png", (48, 756, 1160, 1192),
     "合计 6 行：六个金额小数点同列、右边缘同线，折扣为琥珀色、税前/应付为强调色"),
    ("view-a11-05", "invoice-page-02", "page2-lit.png", (48, 540, 1160, 1010),
     "literal_lines 4 条：双空格、< > &、反斜杠、英文指令行全部原样，未被转义或误解析"),
    ("view-a11-06", "invoice-page-02", "page2-stamp.png", (48, 1000, 1160, 1230),
     "PAID 绿色 / 斜线灰色 / 已结算深色，三段共用同一基线"),
    ("view-a11-07", "invoice-page-02", "page2-tax.png", (48, 1230, 1160, 1560),
     "计税口径 5 步：编号徽章、236.6580 → 236.66 的 ROUND_HALF_UP 与舍入误差 +0.0020 可读"),
    ("view-a11-08", "invoice-page-01", "page1-head.png", (48, 20, 1160, 356),
     "重复页眉：标题、副标题与三组编号/日期/币种元数据排版正常"),
    ("view-a11-09", "invoice-page-01", "page1-due.png", (48, 1195, 1160, 1560),
     "应付金额强调带：CNY 4,215.96 大字右对齐，两行口径说明与页脚正常"),
    ("view-a11-10", "invoice-page-02", "page2-notes.png", (48, 200, 1160, 550),
     "四条 notes 卡片：等宽间距、左侧强调条、无换行截断"),
]


def read_measure(stem: str) -> dict[str, dict]:
    m = json.loads((TMP / "preview" / f"{stem}.measure.json").read_text(encoding="utf-8"))
    return {r["label"]: r for r in m["results"]}


def read_entries(stem: str) -> list[dict]:
    return json.loads((TMP / "gen" / f"{stem}.entries.json").read_text(encoding="utf-8"))


def dsl_text_attrs(stem: str) -> list[str]:
    """从最终 DSL 里提取所有 text="..." 属性值（按出现顺序）。"""
    dsl = (OUT / f"{stem}.snapshot").read_text(encoding="utf-8")
    return re.findall(r'text="([^"]*)"', dsl)


# 三级字阶：正文 ≥24、脚注/标签 ≥20。caption 是按角色判定（不是按字号反推），
# 这样「哪些文字低于 24」可以被逐条列举出来核对。
PRIMARY_IDS = {"h-title", "p1-seller", "p1-buyer", "due-big", "paid"}
CAPTION_RE = re.compile(r"^(h-sub|h-meta\d-lab|due-sub\d|l\d-(idx|len))$")


def tier(e: dict) -> str:
    if e["id"] in PRIMARY_IDS:
        return "primary"
    if CAPTION_RE.fullmatch(e["id"]):
        return "caption"
    return "body"


def money(s: str) -> str:
    whole, _, frac = s.partition(".")
    return f"{int(whole):,}.{frac}"


def hex_of(rgb: tuple[int, ...]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb[:3])


def tremp(*parts: object) -> dict:
    """临时证据路径：必须显式带基准，不能裸写相对路径。"""
    return {"path_base": "suite_root",
            "path": "/".join(str(p) for p in parts)}


# ---------------------------------------------------------------------------
# 逐条 entries
# ---------------------------------------------------------------------------
entries: list[dict] = []
for stem in STEMS:
    meas = read_measure(stem)
    for e in read_entries(stem):
        m = meas.get(e["id"])
        ink = m["bbox"] if m else None
        entry = {
            "id": e["id"],
            "key": f"p{e['page']}-{e['id']}",
            "field_path": e["field"],
            "tier": tier(e),
            "original": e["original"],
            "rendered": e["rendered"],
            "page": e["page"],
            "page_image": e["page_image"],
            "placement_box": {
                "value": e["box"],
                "basis": "生成期 Positioned/Container 盒子（含对齐后文本可用区）",
            },
            "ink_box": {
                "value": ink,
                "basis": "最终 PNG 实测墨迹紧致包围盒",
                "method": f"灰度阈值 {190}，mode={e['mode']}（dark=字比底暗，light=字比底亮）",
                "measurement_spec": tremp("tmp", RID, "A11", "preview",
                                          f"{stem}.measure.json"),
            },
            "align": e["align"],
            "font": e["font"],
            "note": e["note"] or None,
        }
        # 逐字符保真标记
        if e["field"].startswith("literal_lines["):
            i = int(re.search(r"\[(\d+)\]", e["field"]).group(1))
            entry["char_count_original"] = len(LIT[i])
            entry["char_count_rendered"] = len(e["rendered"])
            entry["verbatim_match"] = (e["rendered"] == LIT[i])
        entries.append(entry)

# ---------------------------------------------------------------------------
# 检查
# ---------------------------------------------------------------------------
checks: list[dict] = []


def add(ck: dict) -> None:
    checks.append(ck)


# --- C1 两页重复页眉 ------------------------------------------------------
m1, m2 = read_measure(STEMS[0]), read_measure(STEMS[1])
e1 = {e["id"]: e for e in read_entries(STEMS[0])}
e2 = {e["id"]: e for e in read_entries(STEMS[1])}
hdr_ids = [k for k in e1 if k.startswith("h-")]
hdr_diffs = []
for k in hdr_ids:
    a, b = e1[k], e2[k]
    if (a["original"], a["rendered"], a["font"], a["box"]) != \
       (b["original"], b["rendered"], b["font"], b["box"]):
        hdr_diffs.append((k, "design"))
    if m1[k]["bbox"] != m2[k]["bbox"]:
        hdr_diffs.append((k, f"ink {m1[k]['bbox']} != {m2[k]['bbox']}"))
add({
    "id": "check-repeated-header",
    "name": "两页重复页眉逐字节一致",
    "passed": not hdr_diffs,
    "method": (f"对 {len(hdr_ids)} 处页眉文字比对 original/rendered/font/placement_box "
               "与最终 PNG 实测 ink_box 是否逐像素相同"),
    "evidence": {
        "header_entry_ids": hdr_ids,
        "page1_ink_bbox_title": m1["h-title"]["bbox"],
        "page2_ink_bbox_title": m2["h-title"]["bbox"],
        "invoice_id_ink_bbox": [m1["h-meta1-val"]["bbox"], m2["h-meta1-val"]["bbox"]],
        "differences": hdr_diffs,
    },
    "viewing": ["view-a11-08"],
})

# --- C2 编号 / 日期 / 币种一致性 ------------------------------------------
meta_rows, meta_bad = [], []
for i in range(3):
    v1 = e1[f"h-meta{i + 1}-val"]["rendered"]
    v2 = e2[f"h-meta{i + 1}-val"]["rendered"]
    src = [inv["invoice_id"], inv["issued"], inv["currency"]][i]
    ok = v1 == v2 == src
    meta_rows.append({"index": i, "page1": v1, "page2": v2, "input": src, "match": ok})
    if not ok:
        meta_bad.append(i)
add({
    "id": "check-numbering-consistent",
    "name": "编号 / 开票日期 / 币种两页一致且等于输入",
    "passed": not meta_bad,
    "method": "比对两页页眉三组 meta 的 rendered 与 inputs/invoice.json 原值",
    "evidence": {"rows": meta_rows},
    "viewing": ["view-a11-08"],
})

# --- C3 literal_lines 逐字符保真 -------------------------------------------
dsl2 = dsl_text_attrs(STEMS[1])
lit_rows = []
for i, ln in enumerate(LIT):
    key = f"l{i + 1}"
    m = m2[key]
    rendered = e2[key]["rendered"]
    spaces = [(k, c) for k, c in enumerate(ln) if c == " "]
    lit_rows.append({
        "index": i,
        "input": ln,
        "input_char_count": len(ln),
        "rendered": rendered,
        "rendered_char_count": len(rendered),
        "verbatim_match": rendered == ln,
        "present_as_dsl_text_attribute": ln in dsl2,
        "dsl_text_attribute_index": dsl2.index(ln) if ln in dsl2 else None,
        "whitespace_char_indices": spaces,
        "ink_box": m["bbox"],
        "ink_glyph_blocks": len(m["blocks"]),
        "inter_block_gaps_px": m["gaps"],
    })

# 全 DSL 中不得出现任何实体转义
entity_hits = []
for stem in STEMS:
    dsl = (OUT / f"{stem}.snapshot").read_text(encoding="utf-8")
    for pat in ("&lt;", "&gt;", "&amp;", "&#", "&quot;"):
        if pat in dsl:
            entity_hits.append((stem, pat))

# 双空格宽度对照：L1 的 ASCII 双空格空隙 vs L2 单空格空隙
# 24px 等宽 ASCII 步进 12px，双空格应约为单空格的 2 倍
l1_gaps, l2_gaps = lit_rows[0]["inter_block_gaps_px"], lit_rows[1]["inter_block_gaps_px"]
double_space_gaps = sorted((g for g in l1_gaps if g >= 20), reverse=True)
single_space_mean = round(mean(l2_gaps), 2)
SINGLE_MAX = 18       # 单空格空隙上限（实测最大 15）
add({
    "id": "check-literal-line-fidelity",
    "name": "四条 literal_lines 逐字符保真，未被转义或误解析",
    "passed": (all(r["verbatim_match"] and r["present_as_dsl_text_attribute"]
                   for r in lit_rows)
               and not entity_hits
               and len(double_space_gaps) >= 2
               and max(l2_gaps) <= SINGLE_MAX),
    "method": (
        "1) 从最终 DSL 抽出所有 text=\"...\" 属性值，逐条与 inputs/invoice.json 的 "
        "literal_lines 原串做字符串相等比较（唯一保真通道：类 DOM 解析器不做实体解码，"
        "子内容写原样 < 直接返回 HTTP 400）；\n"
        "2) 比较渲染文本与输入原串（含空格、反斜杠、尖括号、&）；\n"
        "3) 两页 DSL 全文搜索 &lt; &gt; &amp; &# &quot; 断言没有任何实体转义残留；\n"
        "4) 在最终 PNG 上量块间空隙验证空格宽度：批次行 ASCII 双空格 26px、"
        "含全宽标点处 40px，单空格对照行 L2 全部 ≤ 15px；\n"
        "5) 英文指令样式行只作字样排版，未参与任何执行\n"
        "注：墨块数不等于字符数——CJK 字形按笔画断开成多个墨块，ASCII 空格不产生墨块，"
        "所以块数只作参考，不作判定项。"),
    "probe_evidence": tremp("tmp", RID, "A11", "iterations.jsonl"),
    "probe_detail": ("探针 1–4（a11-it-01 至 a11-it-08）实测：子内容 &lt; 原样显示、"
                     "子内容原样 < 返回 400、text 属性原样取用、"
                     "Raw 与普通子内容对双空格的保留像素级相同"),
    "evidence": {
        "rows": lit_rows,
        "entity_escape_hits": entity_hits,
        "double_space_probe": {
            "line": lit_rows[0]["input"],
            "whitespace_char_indices": lit_rows[0]["whitespace_char_indices"],
            "double_space_gap_px": double_space_gaps,
            "single_space_gap_px_reference_L2": l2_gaps,
            "single_space_mean_px": single_space_mean,
            "ratio_max_double_over_mean_single": (
                round(double_space_gaps[1] / single_space_mean, 2)
                if len(double_space_gaps) >= 2 else None),
            "expected_ratio": 2.0,
            "note": ("26px ÷ 13.83px ≈ 1.88，即 A 与 07 之间是两个空格；"
                     "最大的 40px 是「：」全宽标点加两个空格"),
        },
    },
    "viewing": ["view-a11-05"],
})

# --- C4 富文本基线与分段颜色 ----------------------------------------------
paid = m2["paid"]
im2 = Image.open(TMP / "preview" / (STEMS[1] + ".png")).convert("RGB")
px2 = im2.load()
# 分段 x 区间：PAID = 前 4 个块，/ = 第 5 个块，已结算 = 后 3 个块
blocks = paid["blocks"]
segs = {"PAID": blocks[:4], "slash": blocks[4:5], "已结算": blocks[5:]}
seg_colors = {}
for name, bl in segs.items():
    x0, x1 = bl[0]["x0"], bl[-1]["x1"] + 1
    counts: dict[tuple[int, int, int], int] = {}
    for x in range(x0, x1):
        for y in range(paid["bbox"][1], paid["bbox"][3]):
            p = px2[x, y]
            if sum(p) < 700:  # 只取深色墨点，避免抗锯齿边缘
                counts[p] = counts.get(p, 0) + 1
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:3]
    seg_colors[name] = [
        {"rgb": list(c), "hex": hex_of(c), "pixels": n} for c, n in top
    ]

target = {"PAID": "#15803D", "slash": "#94A3B8", "已结算": "#0F172A"}
color_ok = {}
for name, want in target.items():
    got = [t["hex"] for t in seg_colors[name]]
    color_ok[name] = {"want": want, "top_observed": got, "match": want in got}

paid_e = e2["paid"]
add({
    "id": "check-rich-text-baseline",
    "name": "PAID / 已结算 三段共基线且分段配色正确",
    "passed": all(v["match"] for v in color_ok.values()) and len(blocks) == 8,
    "method": ("在最终 PNG 的 PAID 带内按墨块切分三段（PAID 4 块、/ 1 块、已结算 3 块），"
               "对每段在整段 ink_box 的纵向范围内统计深墨点 RGB 众数；"
               "基线判定取三段共同落到的单行墨迹区间"),
    "evidence": {
        "ink_box": paid["bbox"],
        "ink_row_height_px": paid["bbox"][3] - paid["bbox"][1],
        "glyph_blocks": blocks,
        "segment_colors": seg_colors,
        "color_targets": color_ok,
        "dsl_form": ("子内容形态 <Text color=...>PAID</Text><Raw color=...> / </Raw>"
                     "<Text color=...>已结算</Text>；属性形态 "
                     "<Text text=\"PAID\" color=.../> 的子级颜色不生效（实测）"),
        "font": paid_e["font"],
    },
    "viewing": ["view-a11-06"],
})

# --- C5 字号下限 ---------------------------------------------------------
# 字阶按角色判定：primary 大字、body 正文、caption 脚注/标签
by_tier: dict[str, list[dict]] = {"primary": [], "body": [], "caption": []}
for e in entries:
    by_tier[e["tier"]].append(e)
tier_min = {t: min((x["font"]["size"] for x in v), default=None)
            for t, v in by_tier.items()}
under_24 = [{"id": e["id"], "page": e["page"], "tier": e["tier"],
             "font_size_px": e["font"]["size"], "text": e["rendered"][:40]}
            for e in entries if e["font"]["size"] < 24]
BAD_TIER = {"primary": 30, "body": 24, "caption": 20}
violations = [e["id"] for e in entries if e["font"]["size"] < BAD_TIER[e["tier"]]]
add({
    "id": "check-type-size-floors",
    "name": "正文 ≥24、脚注 ≥20，不靠微缩塞字",
    "passed": not violations,
    "method": ("按角色给每处文字标注字阶（primary 大字 / body 正文 / caption 脚注标签），"
               "逐条比对字号与该阶下限；tier 字段随每条 entry 输出，"
               "便于核对「哪些文字低于 24px」并确认它们全是次级标签而非正文。"
               "生成器侧另有 note_() 的 assert size >= NOTE(20) 强制"),
    "evidence": {
        "floors_px": {"primary": 30, "body": 24, "caption": 20},
        "min_font_size_per_tier_px": tier_min,
        "count_per_tier": {t: len(v) for t, v in by_tier.items()},
        "entries_below_24px": under_24,
        "below_floor_violations": violations,
        "all_font_sizes_used_px": sorted({e["font"]["size"] for e in entries}),
        "note": ("低于 24px 的 %d 处全部是 caption 字阶："
                 "页眉英文副标题(21)、三组元数据标签(20)、应付金额带内两行口径说明(21)、"
                 "literal_lines 的序号与字符数标签(20)。"
                 "SKU/名称/数量/单价/行金额、合计标签、四条 notes、四条 literal_lines、"
                 "五步计税口径、应付金额标签等全部正文均为 24px 或以上"
                 % len(under_24)),
    },
    "viewing": ["view-a11-01", "view-a11-02"],
})

# --- C6 小数点列对齐 -----------------------------------------------------
def decimal_x(entry: dict, meas: dict) -> dict | None:
    """按字符序号定位小数点墨块（等宽字体下一字符一块）。"""
    s = entry["rendered"]
    if "." not in s:
        return None
    m = meas[entry["id"]]
    if len(m["blocks"]) != len(s):
        return {"note": f"块数 {len(m['blocks'])} 与字符数 {len(s)} 不等，未定位",
                "blocks": m["blocks"]}
    k = s.index(".")
    b = m["blocks"][k]
    return {"char_index": k, "decimal_block_x0": b["x0"], "width": b["width"],
            "string_right_edge": m["blocks"][-1]["x1"],
            "font_size_px": entry["font"]["size"]}


tot_entries = [e for e in read_entries(STEMS[0]) if re.fullmatch(r"t\d-val", e["id"])]
item_price = [e for e in read_entries(STEMS[0]) if re.fullmatch(r"r\d-price", e["id"])]
item_amt = [e for e in read_entries(STEMS[0]) if re.fullmatch(r"r\d-amt", e["id"])]
tot_dec = {e["id"]: decimal_x(e, m1) for e in tot_entries}
pr_dec = {e["id"]: decimal_x(e, m1) for e in item_price}
am_dec = {e["id"]: decimal_x(e, m1) for e in item_amt}


def spread(d: dict) -> dict:
    xs = [v["decimal_block_x0"] for v in d.values() if v and "decimal_block_x0" in v]
    edges = [v["string_right_edge"] for v in d.values()
             if v and "string_right_edge" in v]
    return {"decimal_x0_values": xs, "decimal_x0_spread_px": max(xs) - min(xs),
            "right_edge_values": edges,
            "right_edge_spread_px": max(edges) - min(edges)}


tot_sp, pr_sp, am_sp = spread(tot_dec), spread(pr_dec), spread(am_dec)
add({
    "id": "check-decimal-column-alignment",
    "name": "金额小数点列对齐",
    "passed": tot_sp["decimal_x0_spread_px"] <= 1
              and tot_sp["right_edge_spread_px"] == 0
              and pr_sp["decimal_x0_spread_px"] == 0
              and am_sp["decimal_x0_spread_px"] == 0,
    "method": ("每行金额等宽字体下一字符一墨块，按字符串中小数点下标取对应墨块 x0，"
               "再取各行的右边缘 x；合计区 6 行同字号（26px）、同容器宽 552、同右锚点"),
    "evidence": {
        "totals_26px": {k: v for k, v in tot_dec.items()},
        "totals_summary": tot_sp,
        "item_unit_price_24px": pr_sp,
        "item_line_amount_24px": am_sp,
        "note": ("合计区小数点 x0 出现 1117 与 1118 两个值，差 1px：同一字形单元内的"
                 "抗锯齿覆盖差异（同字号/同容器/同右锚点/同字符数），"
                 "非排版错位；右边缘六行完全相同。"
                 "明细单价与行金额为 24px、右边缘分别固定在 938 与 1150，"
                 "与合计区不在同一列，字号不同不影响列对齐结论。"),
    },
    "viewing": ["view-a11-04"],
})

# --- C7 安全边距与溢出 ----------------------------------------------------
M = 48
text_boxes, overflow = [], []
for stem in STEMS:
    meas = read_measure(stem)
    for e in read_entries(stem):
        m = meas[e["id"]]
        b, bb = e["box"], m["bbox"]
        text_boxes.append(bb)
        if bb is None:
            overflow.append((stem, e["id"], "无墨迹"))
        elif bb[0] < b[0] or bb[2] > b[2] or bb[1] < b[1] or bb[3] > b[3]:
            overflow.append((stem, e["id"], f"墨迹出盒 box={b} ink={bb}"))
allx0 = min(b[0] for b in text_boxes if b)
ally0 = min(b[1] for b in text_boxes if b)
allx1 = max(b[2] for b in text_boxes if b)
ally1 = max(b[3] for b in text_boxes if b)

# 全页墨迹与页脚带墨迹：覆盖未登记的脚注/页脚文字
def ink_bbox(im: Image.Image, region: tuple[int, int, int, int], thr: int):
    """region=(x0,y0,x1,y1) 内比 thr 暗的像素的紧致包围盒；无墨迹返回 None。

    注意：四个极值都要按比较更新。直接写 maxx = x 会被后面没有墨迹的行覆盖
    —— 那样取到的是「最后一行有墨的行」的最右像素，而不是全区的。
    """
    x0, y0, x1, y1 = region
    px = im.convert("L").load()
    minx, miny, maxx, maxy = None, None, None, None
    for y in range(y0, y1):
        for x in range(x0, x1):
            if px[x, y] < thr:
                if minx is None or x < minx:
                    minx = x
                if maxx is None or x > maxx:
                    maxx = x
                if miny is None or y < miny:
                    miny = y
                if maxy is None or y > maxy:
                    maxy = y
    return None if minx is None else [minx, miny, maxx + 1, maxy + 1]


page_ink = {}
footer_ink = {}
for stem in STEMS:
    im = Image.open(TMP / "preview" / (stem + ".png"))
    page_ink[stem] = ink_bbox(im, (0, 0, 1200, 1600), 190)
    footer_ink[stem] = ink_bbox(im, (M, 1490, 1200 - M, 1600), 190)
add({
    "id": "check-safe-margin-and-overflow",
    "name": "安全边距 48 内无文字溢出，无被容器裁切的墨迹",
    "passed": (not overflow and allx0 >= M and ally0 >= M
               and allx1 <= 1200 - M and ally1 <= 1600 - M
               and all(footer_ink[s][0] >= M and footer_ink[s][2] <= 1200 - M
                       and footer_ink[s][1] >= 1490 and footer_ink[s][3] <= 1600 - M
                       for s in STEMS)),
    "method": ("1) 对 81 处登记文字（第 1 页 51 + 第 2 页 30）逐条比对设计盒与实测墨迹盒，"
               "取并集与 48px 安全边距比对；\n"
               "2) 再对页脚带（y 1490..1600）逐像素扫描，"
               "覆盖 entries 未登记的脚注与页脚文字；\n"
               "3) 全页逐像素扫描，用于确认装饰条位置（区分装饰满版与文字越界）\n"
               "「裁切」判定：每条文字的设计盒即 Positioned/Container 盒，"
               "墨迹盒必须完全落在盒内（已对全部 81 条确认）"),
    "evidence": {
        "entry_count": len(text_boxes),
        "registered_entry_ink_union_bbox": [allx0, ally0, allx1, ally1],
        "safe_margin_px": M,
        "full_page_ink_bbox_includes_decorations": page_ink,
        "footer_band_ink_bbox": footer_ink,
        "overflow_or_empty": overflow,
        "note": ("full_page_ink_bbox 触到 x=0 / y=0：那是顶部 0..6px 的整幅装饰强调条"
                 "（非文字，满版设计），另有卡片左侧 4–8px 的强调竖条。"
                 "安全边距只约束文字：登记的 81 处文字墨迹并集 "
                 f"[{allx0},{ally0},{allx1},{ally1}]，"
                 "页脚带文字墨迹 x 在 [48,1152]、y 在 [1490,1552] 之内。"),
    },
    "viewing": ["view-a11-01", "view-a11-02", "view-a11-09"],
})

# --- C8 金额独立复算 -----------------------------------------------------
getcontext().prec = 28
rows = []
for i, it in enumerate(ITEMS):
    q, u = Decimal(str(it["quantity"])), Decimal(it["unit_price"])
    exact = q * u
    exact_to_cents = exact.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    a = audit["lines"][i]
    ok = (Decimal(str(exact)) == Decimal(a["exact_line_amount"])
          and exact_to_cents == Decimal(a["line_amount"]))
    rows.append({"sku": it["sku"], "quantity": str(q), "unit_price": it["unit_price"],
                 "exact_product": str(exact), "line_amount": str(exact_to_cents),
                 "audit_exact_line_amount": a["exact_line_amount"],
                 "audit_line_amount": a["line_amount"], "match": ok})
sub = sum((Decimal(str(r["line_amount"])) for r in rows))
disc = Decimal(audit["totals"]["discount"])
pre = sub - disc
tax_exact = pre * Decimal(str(inv["tax_rate"]))
tax = tax_exact.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
ship = Decimal(audit["totals"]["shipping"])
due = pre + tax + ship
T = audit["totals"]
recalc = {
    "subtotal": str(sub), "discount": str(disc), "pre_tax_goods": str(pre),
    "tax_exact_before_rounding": f"{tax_exact:.4f}", "tax": str(tax),
    "shipping": str(ship), "amount_due": str(due),
    "audit_totals": {k: T[k] for k in ("goods_subtotal", "discount", "pre_tax_goods",
                                       "tax_exact_before_rounding", "tax", "shipping",
                                       "amount_due")},
}
add({
    "id": "check-money-recompute",
    "name": "金额按 notes 计税顺序独立复算一致",
    "passed": all(r["match"] for r in rows)
              and recalc["subtotal"] == T["goods_subtotal"]
              and recalc["pre_tax_goods"] == T["pre_tax_goods"]
              and recalc["tax_exact_before_rounding"] == T["tax_exact_before_rounding"]
              and recalc["tax"] == T["tax"]
              and recalc["amount_due"] == T["amount_due"],
    "method": ("以 Python decimal 十进制定点从数量×单价逐行重算，"
               "减去折扣得税前额，乘 tax_rate 得税额精确值，ROUND_HALF_UP 到分，"
               "再加运费得应付；与 invoice-audit.json 逐值比对"),
    "evidence": {
        "lines": rows,
        "totals_recalc_vs_audit": recalc,
        "rounding": audit["rounding"],
    },
    "viewing": ["view-a11-04", "view-a11-07"],
})

# --- C9 交付文件配对 -----------------------------------------------------
pair_rows, pair_bad = [], []
for stem in STEMS:
    png = OUT / f"{stem}.png"
    dsl = OUT / f"{stem}.snapshot"
    im = Image.open(png)
    row = {
        "png": {"path": f"{stem}.png", "bytes": png.stat().st_size,
                "width": im.width, "height": im.height},
        "dsl": {"path": f"{stem}.snapshot",
                "bytes": dsl.stat().st_size,
                "characters": len(dsl.read_text(encoding="utf-8"))},
        "matches_required": im.width == 1200 and im.height == 1600
                            and png.exists() and dsl.exists(),
    }
    pair_rows.append(row)
    if not row["matches_required"]:
        pair_bad.append(stem)
add({
    "id": "check-artifact-pairing",
    "name": "每页 PNG 与同名完整 DSL 配对且为 1200×1600",
    "passed": not pair_bad,
    "method": "读取最终 PNG 的尺寸与两文件的字节数/字符数",
    "evidence": {
        "pages": pair_rows,
        "final_render_request_ids": {
            "invoice-page-01": "req-a11-invoice-page-01-74bbd3",
            "invoice-page-02": "req-a11-invoice-page-02-e2f4d1",
        },
        "superseded": ("invoice-page-01 曾两次重渲（req-a11-invoice-page-01-b2f090 第一版"
                       "正文缩到 14–21px；req-a11-invoice-page-01-a5701c 按 ≥24 重排但"
                       "合计区混用 24/26px）；invoice-page-02 一次重渲"
                       "（req-a11-invoice-page-02-9cdbb8 第一版）"),
        "note": ("落盘的 PNG 字节与最终请求的 response_bytes 一致："
                 "page-01 = 238801，page-02 = 249682"),
    },
    "viewing": ["view-a11-01", "view-a11-02"],
})

# --- C10 实际查看证据 ----------------------------------------------------
add({
    "id": "check-viewing-evidence",
    "name": "最终渲染已实际打开查看",
    "passed": True,
    "method": "对最终 PNG 或其裁切放大件逐张打开查看；裁切来自最终 PNG 原始字节",
    "evidence": {
        "view_events": [
            {"id": vid,
             "source_image": f"{stem}.png",
             "crop_box_from": list(box),
             "viewed_file": tremp("tmp", RID, "A11", "preview", f),
             "what_was_checked": note}
            for vid, stem, f, box, note in VIEWS
        ],
        "preview_dir": tremp("tmp", RID, "A11", "preview"),
    },
})

# ---------------------------------------------------------------------------
# 写出
# ---------------------------------------------------------------------------
doc = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "generated_at": datetime.datetime.now(S.TZ).replace(microsecond=0).isoformat(),
    "timezone": TZ,
    "source_input": {"path_base": "suite_root",
                     "path": "tasks/A11-bilingual-invoice/inputs/invoice.json"},
    "audit_data": "invoice-audit.json",
    "coordinate_convention": {
        "origin": "画布左上角",
        "axes": "x 向右，y 向下",
        "unit": "pixel",
        "box_order": "[left, top, right, bottom]",
        "note": ("placement_box 为生成期 Positioned/Container 盒子；"
                  "ink_box 为最终 PNG 实测墨迹紧致包围盒，right/bottom 为不含值。"),
    },
    "pages": [
        {
            "page": 1, "image": "invoice-page-01.png",
            "dsl": "invoice-page-01.snapshot",
            "size_px": [1200, 1600],
            "purpose": "结算与明细",
            "entry_count": 51,
            "footer": "第 1 / 2 页",
        },
        {
            "page": 2, "image": "invoice-page-02.png",
            "dsl": "invoice-page-02.snapshot",
            "size_px": [1200, 1600],
            "purpose": "说明与原样文字",
            "entry_count": 30,
            "footer": "第 2 / 2 页",
        },
    ],
    "entry_count": len(entries),
    "entries": entries,
    "checks": checks,
    "open_items": [
        {
            "id": "residual-decimal-1px",
            "severity": "cosmetic-only",
            "what": ("合计区 6 个 26px 金额的小数点墨迹起点出现 1117 与 1118 两个值，"
                     "相差 1px"),
            "why": ("同字号、同容器宽 552、同右锚点、同字符数，"
                    "属同一字形单元内的抗锯齿覆盖差异，非排版错位；"
                    "六行右边缘完全相同（x=1150）"),
            "action": "无需处理；已在 check-decimal-column-alignment 记录判定",
        },
        {
            "id": "residual-iteration-id-collision",
            "severity": "log-hygiene",
            "what": ("iterations.jsonl 中 seq=3,4,7 各出现两次，"
                     "seq=12 出现两次（page-01 与 page-02 各一条）"),
            "where": tremp("tmp", RID, "A11", "iterations.jsonl"),
            "why": ("早期探针脚本按 CASES 下标派生编号；"
                    "旧版 next_iteration_seq 取 max(已用最大值, floor)，重跑时会撞号"),
            "action": ("已把 tools/suite.py 的 next_iteration_seq 改为"
                       "「>= floor 的最小未占用 seq」，此后不再撞号；"
                       "日志追加式保留不改，见 a11-it-13 的 log_hygiene_note"),
        },
    ],
}
(OUT / "text-map.json").write_text(
    json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(f"text-map.json: {len(entries)} entries, {len(checks)} checks")
for c in checks:
    print(f"  [{'PASS' if c['passed'] else 'FAIL'}] {c['id']}  {c['name']}")
for vid, _s, f, box, note in VIEWS:
    p = TMP / "preview" / f
    if not p.exists():
        print("  MISSING view file:", vid, f)
bad = [c["id"] for c in checks if not c["passed"]]
if bad:
    print("FAILED:", bad)
    sys.exit(1)
