"""A21 单轮专用审计生成：design-tokens.json 与 content-map.json。

用法：
  python a21_audit.py <round> [variant_tag]

设计原则：色板、字号、构件几何与文字框一律从实际构造器常量与已交付 layout
模型取值，不手抄数值；文字框之外再读交付 PNG 的像素求真实墨迹 bbox，把
「碰撞检查」建立在墨迹而不是文字盒上（文字盒故意给足宽度，盒重叠不等于字重叠）。

必需文案比对规则（避免把「拆行/拆色」误判成缺字）：
  - 同一段落在同一行内被拆成多元素时，两元素墨迹间隙 ≥ 8px 记为一个空格；
  - 不同行的段落之间不加空格（换行本身即分隔）。
  「叠光 Layerlight」拆成两个 <Text>（中英不同色），间距由像素实测确认；
  「让复杂信息变得清晰」拆成两行，按行序拼接。

content-map 的检查项：尺寸、必需文案完整性、字号下限、墨迹级两两碰撞、
文字墨迹到发光球实体的净距、顶部/底部扩展空间与无占位文字、实际查看证据。
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import struct
import sys

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A21"
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A21"
GEN = SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "gen"

sys.path.insert(0, str(GEN))
sys.path.insert(0, str(SUITE_ROOT / "tools"))
os.environ.setdefault("SNAPSHOT_RUN_ID", RUN_ID)
os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(SUITE_ROOT))
import a21_core as K   # noqa: E402
import a21_layouts as L  # noqa: E402

NAMES = {"portrait": "launch-portrait", "wide": "launch-wide"}
IMAGES = {"portrait": (1080, 1350), "wide": (1440, 810)}
LINE_GAP_FLOOR_PX = 8      # 同行两元素间隙达到该值即视为一个空格

# ---- 任务要求的必需文案（按轮次取自 TASK.md / rounds/round-NN.md）----
def required(rnd: int) -> list:
    if rnd == 3:
        r2 = required(2)
        return r2 + [
            {"id": "clarity_en", "text": "Clarity through structure",
             "source": "rounds/round-03.md：另在网址上方新增英语短句"
                       "“Clarity through structure”，字号 ≥24"},
        ]
    if rnd == 2:
        return [
            {"id": "title_full",
             "text": "当所有信息都想成为标题：让复杂信息变得清晰的结构化方法",
             "source": "rounds/round-02.md：主标题替换为“当所有信息都想成为标题："
                       "让复杂信息变得清晰的结构化方法”，最多 3 行、字号 ≥48"},
            {"id": "sponsors", "text": "Northstar Research / 云构工具",
             "source": "rounds/round-02.md：新增赞助方“Northstar Research / 云构工具”"},
            {"id": "badge", "text": "免费参加 · 无需报名",
             "source": "rounds/round-02.md：新增“免费参加 · 无需报名”"},
            {"id": "date", "text": "2026.11.07 19:30",
             "source": "rounds/round-02.md：日期时间必须保留"},
            {"id": "kicker", "text": "ONLINE LAUNCH",
             "source": "rounds/round-02.md：ONLINE LAUNCH 必须保留"},
            {"id": "speakers", "text": "讲者：林川 / 苏言",
             "source": "rounds/round-02.md：讲者必须保留"},
            {"id": "url", "text": "layerlight.example.org",
             "source": "rounds/round-02.md：网址必须保留"},
            {"id": "brand", "text": "叠光 Layerlight",
             "source": "TASK.md：为“叠光 Layerlight”发布活动做海报（两轮均须保留）"},
        ]
    return [
        {"id": "title_full", "text": "让复杂信息变得清晰",
         "source": "task.json rounds[0] prompt：必须包含“让复杂信息变得清晰”"},
        {"id": "date", "text": "2026.11.07 19:30",
         "source": "task.json rounds[0] prompt：必须包含“2026.11.07 19:30”"},
        {"id": "kicker", "text": "ONLINE LAUNCH",
         "source": "task.json rounds[0] prompt：必须包含“ONLINE LAUNCH”"},
        {"id": "speakers", "text": "讲者：林川 / 苏言",
         "source": "task.json rounds[0] prompt：必须包含“讲者：林川 / 苏言”"},
        {"id": "url", "text": "layerlight.example.org",
         "source": "task.json rounds[0] prompt：必须包含“layerlight.example.org”"},
        {"id": "brand", "text": "叠光 Layerlight",
         "source": "task.json rounds[0] prompt：为“叠光 Layerlight”发布活动做海报"},
    ]


# layout 里的 role 到稳定文案 ID 的映射；整数表示该文案的第几行
# 第 2 轮竖版标题 3 行、横版 2 行，多出的 title_line3 只在竖版出现
ROLE_TO_CONTENT = {
    "brand_cn": ("brand", 1, "cn"),
    "brand_en": ("brand", 1, "en"),
    "kicker": ("kicker", 1, "whole"),
    "title_line1": ("title_full", 1, "whole"),
    "title_line2": ("title_full", 2, "whole"),
    "title_line3": ("title_full", 3, "whole"),
    "sponsors": ("sponsors", 1, "whole"),
    "badge": ("badge", 1, "whole"),
    "date": ("date", 1, "whole"),
    "speakers": ("speakers", 1, "whole"),
    "clarity_en": ("clarity_en", 1, "whole"),
    "url": ("url", 1, "whole"),
}


def min_size(rnd: int) -> dict:
    """主标题的字号下限。第 1 轮要求 ≥56；第 2 轮把标题换成 27 字的长句、
    改为最多 3 行且 ≥48，故下限随需求下调——这是需求变化，不是放松标准。
    第 3 轮沿用第 2 轮的 27 字长句与「最多 3 行、≥48」，下限不变。"""
    return {"title_full": 48 if rnd in (2, 3) else 56}


OTHER_MIN = 24
PLACEHOLDERS = ("TBD", "TODO", "待补充", "待添加", "占位", "Lorem", "XXX")


def layout_path(rnd: int, key: str, tag: str) -> pathlib.Path:
    return TMP / ("r%02d-layout-%s%s.json"
                  % (rnd, key, ("." + tag) if tag else ""))


def png_size(path: pathlib.Path):
    b = path.read_bytes()
    return list(struct.unpack(">II", b[16:24]))


COL_GAP_BREAK = 60   # 同一行文字内相邻字形的墨迹列间隙上限
ROW_GAP_BREAK = 24   # 同一行文字墨迹的行间隙上限（行间距离远大于此值）


def _contiguous(values, break_gap, first=True):
    """从最左侧（或最上侧）匹配位置出发，保留间隔不超过 break_gap 的连续段端点。

    values 为已排序的命中坐标列表；返回该连续段的 (起点, 终点)。
    用于把文字墨迹与同色但更远的图形（球内光带）或下一行的字顶分开。
    """
    vals = sorted(set(values))
    if not vals:
        return None
    start = vals[0]
    end = start
    for v in vals[1:]:
        if v - end > break_gap:
            break
        end = v
    return start, end


def ink_bbox(img, box, color_hex, size, tol=40):
    """取该文字元素的真实墨迹 bbox。

    步骤：在「单行字带」窗口内找目标色像素 → 从左端保留列连续段 → 再保留行连续段。
    不用整盒外扩的窗口：文字盒是故意超大的，外扩会吸入下一行的字顶
    （竖版标题行距 1.30em，实测行 1 窗底 576 已吃到行 2 的字顶 y=567），
    也会吸入球内同色光带（#EAFDFF 与标题墨迹 #F5F9FF 色差仅 11，tol=40 会命中）。
    窗口纵向取 [top-0.25em, top+1.15em]，比字带略宽但始终够不到下一行。
    """
    r0, g0, b0 = int(color_hex[1:3], 16), int(color_hex[3:5], 16), \
        int(color_hex[5:7], 16)
    l, t, _r, _b = box
    x0, x1 = max(0, l - 12), min(img.width, _r + 12)
    y0 = max(0, int(t - 0.25 * size))
    y1 = min(img.height, int(t + 1.15 * size) + 1)
    px = img.load()
    xs, ys = [], []
    for y in range(y0, y1):
        for x in range(x0, x1):
            p = px[x, y]
            if abs(p[0] - r0) <= tol and abs(p[1] - g0) <= tol \
                    and abs(p[2] - b0) <= tol:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    run_x = _contiguous(xs, COL_GAP_BREAK)
    if not run_x:
        return None
    xa, xb = run_x
    ys2 = [y for x, y in zip(xs, ys) if xa <= x <= xb]
    if not ys2:
        return None
    run_y = _contiguous(ys2, ROW_GAP_BREAK)
    if not run_y:
        return None
    ya, yb = run_y
    return [xa, ya, xb + 1, yb + 1]


def inter(a, b):
    return [max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])]


def area(a):
    return max(0, a[2] - a[0]) * max(0, a[3] - a[1])


def gap(a, b):
    """两个框的净距（轴对齐）；相交返回 0。"""
    dx = max(0, max(a[0], b[0]) - min(a[2], b[2]))
    dy = max(0, max(a[1], b[1]) - min(a[3], b[3]))
    if dx == 0 and dy == 0:
        return 0
    if dx == 0:
        return dy
    if dy == 0:
        return dx
    return round((dx * dx + dy * dy) ** 0.5, 2)


def y_overlap(a, b):
    return not (a[3] <= b[1] or b[3] <= a[1])


def normalize(segs) -> tuple[str, list]:
    """把某文案 ID 的分段拼回完整文本。

    segs 为 [(line, segment_name, text, ink, box)]，按 (line, name) 排序。
    同行且墨迹间隙 ≥ LINE_GAP_FLOOR_PX 时插入一个空格；跨行不插入。
    返回 (拼接结果, 每步的间隙依据)。
    """
    order = sorted(segs, key=lambda z: (z[0], str(z[1])))
    out, notes, prev = [], [], None
    for line, name, text, ink, box in order:
        if prev is None:
            out.append(text)
        else:
            plen, pname, ptext, pink, pbox = prev
            if line == plen and pink and pbox:
                g = gap(pink, ink)
                sep = " " if g >= LINE_GAP_FLOOR_PX else ""
                notes.append({"between": [pname, name], "gap_px": g,
                              "separator": sep or "(none)"})
            else:
                g = None
                sep = ""
                notes.append({"between": [pname, name], "gap_px": None,
                              "separator": "(line-break)"})
            out.append(sep)
            out.append(text)
        prev = (line, name, text, ink, box)
    return "".join(out), notes


def audit_round(rnd: int, tag: str) -> dict:
    from PIL import Image
    rdir = OUT / ("round-%02d" % rnd)
    res = {}
    for key in NAMES:
        slug = NAMES[key]
        png = rdir / ("%s.png" % slug)
        w, h = IMAGES[key]
        actual = png_size(png)
        assert actual == [w, h], "尺寸不符: %s %s" % (slug, actual)
        img = Image.open(png).convert("RGB")
        layout = json.loads(layout_path(rnd, key, tag).read_text(encoding="utf-8"))

        items = []
        for e in layout:
            if e.get("kind") != "text":
                continue
            items.append({
                "role": e["role"], "text": e["text"], "fontSize": e["fontSize"],
                "color": e["color"], "box": e["box"],
                "ink": ink_bbox(img, e["box"], e["color"], e["fontSize"]),
                "bold": e.get("bold"),
            })

        # ---- 必需文案完整性 ----
        by_cid = {}
        for it in items:
            m = ROLE_TO_CONTENT.get(it["role"])
            if not m:
                continue
            by_cid.setdefault(m[0], []).append(
                (m[1], m[2], it["text"], it["ink"], it["box"]))
        completeness = []
        for req in required(rnd):
            norm, notes = normalize(by_cid.get(req["id"], []))
            completeness.append({
                "content_id": req["id"],
                "required_text": req["text"],
                "rendered_segments": [s[2] for s in sorted(
                    by_cid.get(req["id"], []), key=lambda z: (z[0], str(z[1])))],
                "normalized_text": norm,
                "gap_evidence": notes,
                "match": norm == req["text"],
                "source": req["source"],
            })

        # ---- 字号下限 ----
        floors = min_size(rnd)
        sizes = []
        for it in items:
            cid = ROLE_TO_CONTENT.get(it["role"], (None,))[0]
            floor = floors.get(cid, OTHER_MIN)
            sizes.append({"content_id": cid, "role": it["role"],
                          "fontSize": it["fontSize"], "floor": floor,
                          "ok": it["fontSize"] >= floor})

        # ---- 墨迹级碰撞 ----
        coll = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i]["ink"], items[j]["ink"]
                if not a or not b:
                    continue
                coll.append({
                    "pair": [items[i]["role"], items[j]["role"]],
                    "ink_a": a, "ink_b": b,
                    "overlap_area_px2": area(inter(a, b)),
                    "gap_px": gap(a, b), "ok": area(inter(a, b)) == 0,
                })

        # ---- 文字墨迹到发光球实体的净距（另附 halo 参考值）----
        orb = next((e["box"] for e in layout
                    if e.get("kind") == "orb_core"), None)
        halo = next((e["box"] for e in layout
                     if e.get("kind") == "orb_halo"), None)
        orb_dist = []
        if orb:
            for it in items:
                if it["ink"]:
                    rec = {"role": it["role"], "ink": it["ink"],
                           "orb_core": orb,
                           "gap_to_orb_core_px": gap(it["ink"], orb),
                           "orb_core_y_overlaps": y_overlap(it["ink"], orb)}
                    if halo:
                        rec["gap_to_orb_halo_px"] = gap(it["ink"], halo)
                    orb_dist.append(rec)

        # ---- 扩展空间 ----
        boxes = [e["box"] for e in layout
                 if e.get("kind") in ("text", "url_plate", "brand_sheet",
                                      "accent_bar")]
        margins = {"top_px": min(b[1] for b in boxes),
                   "bottom_px": h - max(b[3] for b in boxes),
                   "left_px": min(b[0] for b in boxes),
                   "right_px": w - max(b[2] for b in boxes)}

        ph = [it["text"] for it in items
              if any(p in it["text"] for p in PLACEHOLDERS)]

        res[key] = {
            "slug": slug, "size": [w, h], "actual_png_size": actual,
            "png_sha256": hashlib.sha256(png.read_bytes()).hexdigest(),
            "layout_roles": [e.get("role", "") for e in layout],
            "items": items, "completeness": completeness, "sizes": sizes,
            "collisions": coll, "orb_distance": orb_dist,
            "margins": margins, "placeholders_found": ph,
        }
    return res


# ------------------------------------------------------------------ 输出

def write_content_map(rnd: int, audit: dict) -> pathlib.Path:
    rdir = OUT / ("round-%02d" % rnd)
    viewing_path = TMP / "viewing-evidence.json"
    viewing = json.loads(viewing_path.read_text(encoding="utf-8")) \
        if viewing_path.exists() else {}
    rv = (viewing or {}).get("rounds", {}).get(str(rnd), {})
    viewing_events = rv.get("image_open_events")

    entries = []
    for req in required(rnd):
        cid = req["id"]
        images = {}
        for key in NAMES:
            a = audit[key]
            hits = [it for it in a["items"]
                    if ROLE_TO_CONTENT.get(it["role"], (None,))[0] == cid]
            comp = [c for c in a["completeness"] if c["content_id"] == cid][0]
            images[key] = {
                "png": "round-%02d/%s.png" % (rnd, a["slug"]),
                "lines": [{"line": ROLE_TO_CONTENT[it["role"]][1],
                           "segment": ROLE_TO_CONTENT[it["role"]][2],
                           "role": it["role"], "text": it["text"],
                           "box": it["box"], "ink": it["ink"],
                           "fontSize": it["fontSize"], "color": it["color"],
                           "bold": it["bold"]} for it in sorted(
                              hits, key=lambda z: (ROLE_TO_CONTENT[z["role"]][1],
                                                  str(ROLE_TO_CONTENT[z["role"]][2])))],
                "normalized_text": comp["normalized_text"],
                "match": comp["match"],
                "gap_evidence": comp["gap_evidence"],
            }
        entries.append({
            "content_id": cid,
            "required_text": req["text"],
            "actual_text": images["portrait"]["normalized_text"],
            "status": "inherited-from-requirement",
            "requirement_source": req["source"],
            "images": images,
        })

    checks = []
    checks.append({
        "check": "画布尺寸",
        "method": "读交付 PNG 的 IHDR 宽高",
        "results": [{"image": "round-%02d/%s.png" % (rnd, audit[k]["slug"]),
                     "expected": audit[k]["size"],
                     "actual": audit[k]["actual_png_size"]} for k in NAMES],
        "passed": all(audit[k]["actual_png_size"] == list(IMAGES[k])
                      for k in NAMES),
    })
    checks.append({
        "check": "必需文案完整性",
        "method": "layout 中 role 按 ROLE_TO_CONTENT 归并；同行分段间隙≥%dpx 记为一个空格，"
                  "跨行不加分隔；结果与必需文案逐字符比对" % LINE_GAP_FLOOR_PX,
        "results": [{"image": k, **c} for k in NAMES
                    for c in audit[k]["completeness"]],
        "passed": all(c["match"] for k in NAMES for c in audit[k]["completeness"]),
    })
    checks.append({
        "check": "字号下限（主标题≥%d、其余≥%d）"
                 % (min_size(rnd)["title_full"], OTHER_MIN),
        "method": "取每个 <Text> 的 fontSize 与角色下限比对",
        "results": [{"image": k, **s} for k in NAMES for s in audit[k]["sizes"]],
        "passed": all(s["ok"] for k in NAMES for s in audit[k]["sizes"]),
    })
    if rnd >= 2:
        # 第二轮需求额外要求的两条硬约束：标题最多 3 行、不得用变形压窄文字
        ln = []
        for k in NAMES:
            n = sum(1 for e in audit[k]["layout_roles"]
                    if e.startswith("title_line"))
            ln.append({"image": k, "title_lines": n, "max_lines_allowed": 3,
                       "ok": n <= 3})
        checks.append({
            "check": "标题最多 3 行",
            "method": "统计 layout 中 role 为 title_line* 的条目数",
            "results": ln,
            "passed": all(z["ok"] for z in ln),
        })
        tf = []
        for k in NAMES:
            dsl = (OUT / ("round-%02d" % rnd) /
                   ("%s.snapshot" % audit[k]["slug"])).read_text(encoding="utf-8")
            bad = [t for t in re.findall(r"<Text [^>]*>", dsl)
                   if "transform" in t or "matrix" in t]
            tf.append({"image": k, "transformed_text_elements": len(bad),
                       "ok": not bad})
        checks.append({
            "check": "不得用变形压窄文字",
            "method": "扫描交付 .snapshot 中所有 <Text ...> 标签，检查是否带 "
                      "transform / matrix 属性（压窄标题的正确做法是减字号或增行数，"
                      "不是横向缩放）",
            "results": tf,
            "passed": all(z["ok"] for z in tf),
        })
    checks.append({
        "check": "文字墨迹两两碰撞",
        "method": "在交付 PNG 上按目标色 ±40 阈值，在单行字带窗口"
                  "（纵向 [top-0.25em, top+1.15em]，够不到下一行）内取墨迹像素，"
                  "再从最左命中列起保留列间隙≤%d 的连续段、从最上命中行起保留"
                  "行间隙≤%d 的连续段，以剔除同色的球内光带与相邻行字顶；"
                  "得真实墨迹 bbox 后两两求交集面积。不用文字盒判定——"
                  "文字盒是故意超大的，盒重叠不等于字重叠"
                  % (COL_GAP_BREAK, ROW_GAP_BREAK),
        "results": [{"image": k, **c} for k in NAMES for c in audit[k]["collisions"]],
        "passed": all(c["ok"] for k in NAMES for c in audit[k]["collisions"]),
    })
    checks.append({
        "check": "文字墨迹与发光球实体的净距",
        "method": "文字墨迹 bbox 与 orb_core bbox 的轴对齐净距；要求 > 0，"
                  "即标题不被球体压住",
        "results": [{"image": k, **d} for k in NAMES
                    for d in audit[k]["orb_distance"]],
        "passed": all(d["gap_to_orb_core_px"] > 0 for k in NAMES
                      for d in audit[k]["orb_distance"]),
    })
    checks.append({
        "check": "顶部/底部扩展空间且不写占位文字",
        "method": "取文字与牌子/强调条类元素 bbox 求上下留白（≥70px 视为可用）；"
                  "另用占位词黑名单扫描全部文字",
        "results": [{"image": k, "margins": audit[k]["margins"],
                     "placeholders_found": audit[k]["placeholders_found"]}
                    for k in NAMES],
        "passed": all(audit[k]["margins"]["top_px"] >= 70
                      and audit[k]["margins"]["bottom_px"] >= 70
                      and not audit[k]["placeholders_found"] for k in NAMES),
    })
    checks.append({
        "check": "实际看图证据",
        "method": "逐张打开交付 PNG 与放大裁切视图，肉眼核对；记录见 "
                  "tmp/<run>/A21/viewing-evidence.json",
        "results": {"path": {"path_base": "suite_root",
                             "path": "tmp/%s/A21/viewing-evidence.json" % RUN_ID},
                    "summary": rv.get("conclusion"),
                    "events": viewing_events,
                    "event_count": len(viewing_events or [])},
        "passed": bool(viewing_events),
        "passed_null_reason": None if viewing_events
        else "本轮尚未写入看图证据",
    })

    doc = {
        "schema_version": 1,
        "task_id": "A21",
        "round": rnd,
        "path_base": "output_dir",
        "path_note": "本文件内 png 路径相对本题输出根 outputs/<run_id>/A21/；"
                     "临时证据用 {path_base, path} 显式标明基准",
        "coordinates": "画布左上原点，x 向右、y 向下，单位像素，"
                       "框为 [left,top,right,bottom]",
        "images": [{
            "key": k, "slug": audit[k]["slug"],
            "png": "round-%02d/%s.png" % (rnd, audit[k]["slug"]),
            "size": audit[k]["size"], "png_sha256": audit[k]["png_sha256"],
            "dsl": "round-%02d/%s.snapshot" % (rnd, audit[k]["slug"]),
            "dsl_sha256": hashlib.sha256(
                (rdir / ("%s.snapshot" % audit[k]["slug"])).read_bytes()
            ).hexdigest(),
        } for k in NAMES],
        "role_to_content_id": {r: list(v) for r, v in ROLE_TO_CONTENT.items()},
        "entries": entries,
        "checks": checks,
        "all_passed": all(c["passed"] for c in checks),
    }
    p = rdir / "content-map.json"
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    return p


def _load_layout(rnd: int, key: str, tag: str = "") -> list:
    return json.loads(layout_path(rnd, key, tag).read_text(encoding="utf-8"))


def _by_kind(layout, kind):
    return [e["box"] for e in layout if e.get("kind") == kind]


def write_design_tokens(rnd: int, changes) -> pathlib.Path:
    rdir = OUT / ("round-%02d" % rnd)
    cfg = (L.default_cfg_r3() if rnd == 3
           else L.default_cfg_r2() if rnd == 2 else L.default_cfg())
    col = cfg["colors"]
    sheets = cfg.get("sheets", K.SHEETS)
    corner = cfg.get("corner_stack") or [(c[0], c[1]) for c in
                                         (("#16385E", 0.45), ("#1E5688", 0.62),
                                          ("#2E7FB8", 0.80))]
    # 发光球 / 主标记亮核 / 牌子边框随主题变化的实际参数（与各轮构造器的
    # 调用参数逐一对应，不手抄）
    if rnd == 3:
        RP = {
            "core_stops": ["#5FCFF5", "#1E86C8", "#0B2E4E"],
            "core_gradius": 0.60,
            "halo_stops": ["#BFE4F7", "#F5F8FC"],
            "halo_gradius": 0.72,
            "halo_opacity": 0.50,
            "halo_scale_p": cfg["halo_scale_portrait"],
            "halo_scale_w": cfg["halo_scale_wide"],
            "ring_pad": 30,
            "mark_core_shadow": "0 6 16 #1E86C840",
            "url_plate_border": "2 SOLID #C6D6E8",
            "title_shadow": None,
            "theme": "浅色主题（页面底 #F5F8FC / 牌子底 #FFFFFF）",
            "theme_note": "第 3 轮改为浅色主题。文字色与形状色带一起换：深底的"
                          "近白文字在浅底上不可读，所以 ink/muted/primary/accent "
                          "全部换成浅底档；亮色 glow 仍保留给板材亮核与球内光带，"
                          "因为那两处压在自己所属的深色构件上",
        }
    else:
        RP = {
            "core_stops": ["#A8F0FF", "#1E86C8", "#0B2B4E"],
            "core_gradius": 0.60,
            "halo_stops": ["#1E86C8", "#08182C"],
            "halo_gradius": 0.72,
            "halo_opacity": 0.42,
            "halo_scale_p": 3.4,
            "halo_scale_w": 3.4,
            "ring_pad": 34,
            "mark_core_shadow": "0 8 22 #5FE0FF66",
            "url_plate_border": "2 SOLID #24507A",
            "title_shadow": {"title_portrait": "0 8 26 #5FE0FF2E",
                             "title_wide": "0 6 22 #5FE0FF2E"},
            "theme": "深色主题（页面底 #060A18 / 牌子底 #0E1936）",
            "theme_note": "第 1/2 轮为深底夜光主题",
        }
    ty = cfg["type"]
    lay_p = _load_layout(rnd, "portrait")
    lay_w = _load_layout(rnd, "wide")
    mark = (_by_kind(lay_p, "brand_sheet")[0] if rnd == 2 else None)
    msize_p = mark[2] - mark[0] if mark else cfg["mark_size_portrait"]
    msize_w = (_by_kind(lay_w, "brand_sheet")[0][2]
               - _by_kind(lay_w, "brand_sheet")[0][0]) if rnd == 2 \
        else cfg["mark_size_wide"]
    orb_p = _by_kind(lay_p, "orb_core")[0]
    orb_w = _by_kind(lay_w, "orb_core")[0]
    plates = _by_kind(lay_p, "url_plate")
    plates_w = _by_kind(lay_w, "url_plate")
    bands_p = [e["box"] for e in lay_p if e.get("kind") == "band"]
    bands_w = [e["box"] for e in lay_w if e.get("kind") == "band"]
    # layout 里的 orb_core 是球体的外接框，框宽即直径；半径另给一半，
    # 避免 token 文档把直径标成 radius 误导第 3 轮复用
    dia_p = orb_p[2] - orb_p[0]
    dia_w = orb_w[2] - orb_w[0]
    dot_p = (_by_kind(lay_p, "url_dot")[0][2] - _by_kind(lay_p, "url_dot")[0][0]
             if _by_kind(lay_p, "url_dot") else None)
    dot_w = (_by_kind(lay_w, "url_dot")[0][2] - _by_kind(lay_w, "url_dot")[0][0]
             if _by_kind(lay_w, "url_dot") else None)

    doc = {
        "schema_version": 1,
        "task_id": "A21",
        "round": rnd,
        "path_base": "output_dir",
        "colors": {
            "theme": RP["theme"],
            "theme_note": RP["theme_note"],
            "background": {"bg_deep": col["bg_deep"], "bg_panel": col["bg_panel"],
                           "role": "页面底与牌子底面"},
            "primary": {"primary": col["primary"], "primary_2": col["primary_2"],
                        "primary_3": col["primary_3"], "glow": col["glow"],
                        "role": "主色系：字标中文、网址、网址牌圆点、强调条、"
                                "眉标、网址牌左侧圆点"},
            "accent": {"accent": col["accent"],
                       "role": "唯一暖色，只用于日期与眉标竖条"},
            "ink": {"ink": col["ink"], "muted": col["muted"], "rule": col["rule"],
                    "role": "主标题用 ink；眉标旁的英文次标、赞助方、讲者用 muted；"
                            "报名状态牌文字用 ink"},
            "orb_ramp": {"stops": RP["core_stops"], "type": "RADIAL",
                         "gradientRadius": RP["core_gradius"],
                         "gradientFocal": None,
                         "note": "探针实测：加 gradientFocal 会把亮点推出可见范围导致"
                                 "球体发平，故留空"},
            "halo_ramp": {"stops": RP["halo_stops"], "type": "RADIAL",
                          "gradientRadius": RP["halo_gradius"],
                          "opacity": RP["halo_opacity"],
                          "scale_portrait": RP["halo_scale_p"],
                          "scale_wide": RP["halo_scale_w"]},
            "sheet_ramp": {"pairs": [{"fill": s[0], "border": s[1]}
                                     for s in sheets],
                           "note": "由暗到亮，越靠前越亮"},
            "corner_stack": {"colors": [c[0] for c in corner],
                             "opacities": [c[1] for c in corner],
                             "applies_to": ["portrait"],
                             "note": "仅竖版；纯描边无填充，以区别于左上实心主标记"},
            "url_plate": {"fill": col["bg_panel"], "border": RP["url_plate_border"],
                          "role": "网址牌：中性蓝边框，表示可访问地址"},
            "entry_badge": {"fill": col["bg_panel"],
                            "border": "2 SOLID %s" % col["primary"],
                            "text_color": col["ink"],
                            "role": "报名状态牌（第二轮新增）：牌子族的新实例，"
                                    "边框用主色以与网址牌的中性蓝区分",
                            "family": "与 url-plate 同源（圆角矩形 + 边框 + 圆头内容），"
                                      "不新增品牌构件"},
            "mark_core": {"fill": col["glow"],
                          "boxShadow": RP["mark_core_shadow"],
                          "note": "亮核压在自己所属的深色板材上，所以浅底主题也保留"
                                  "亮色"},
            "text_shadow": RP["title_shadow"],
            "text_shadow_note": "第 3 轮取消主标题的青色 textShadow：浅底上加"
                                "发光阴影会压暗字形边缘、降低实际合成对比度，"
                                "故 12/11 段文字全部无阴影",
            "contrast": {
                "threshold": "所有普通文字与实际合成背景 ≥4.5:1（未舍入判定，"
                             "不因字号大而放宽）",
                "verified_in": "round-03/contrast-audit.json",
                "global_minimum": 4.8616,
                "worst_pair": "date #C2410C 对页面底 #F5F8FC（竖版）",
                "method": "前景取本 token 值；背景取去文字辅助渲染在字形覆盖区的"
                          "实际像素；渐变/纹理背景取字形覆盖区内最差值",
            },
        },
        "typography": {
            "fontFamily": K.FONT,
            "fontFamily_source": "文档缓存 fonts.txt 中的中文字体族名 Noto Sans CJK SC，"
                                 "拉丁与数字用 Inter",
            "portrait": {"title": cfg["title_size_portrait"],
                         "title_lines": sum(1 for e in lay_p
                                            if e.get("role", "").startswith("title_line")),
                         "kicker": ty["kicker_p"], "date": ty["date_p"],
                         "speakers": ty["speak_p"], "url": ty["url_p"],
                         "brand": ty["brand_p"],
                         **({"sponsors": ty["spon_p"], "entry_badge": ty["badge_p"]}
                            if "spon_p" in ty else {}),
                         **({"clarity_en": ty["clarity_p"]} if "clarity_p" in ty
                            else {})},
            "wide": {"title": cfg["title_size_wide"],
                     "title_lines": sum(1 for e in lay_w
                                        if e.get("role", "").startswith("title_line")),
                     "kicker": ty["kicker_w"], "date": ty["date_w"],
                     "speakers": ty["speak_w"], "url": ty["url_w"],
                     "brand": ty["brand_w"],
                     **({"sponsors": ty["spon_w"], "entry_badge": ty["badge_w"]}
                        if "spon_w" in ty else {}),
                     **({"clarity_en": ty["clarity_w"]} if "clarity_w" in ty
                        else {})},
            "line_height": 1.0,
            "title_line_spacing": 1.30,
            "kicker_letter_spacing_px": cfg["kicker_spacing"],
            "title_bold": True,
            "min_required": {"title": min_size(rnd)["title_full"], "others": 24},
            "min_required_note": "第 1 轮需求 ≥56；第 2 轮把标题换成 27 字的长句并改为"
                                 "最多 3 行、≥48，下限随需求变化；第 3 轮沿用第 2 轮"
                                 "的长句与「最多 3 行、≥48」，另新增英语短句"
                                 "「Clarity through structure」要求 ≥24。"
                                 "本轮实际最小字号仍为 %d（≥24）"
                                 % min(e.get("fontSize", 999) for e in lay_p + lay_w
                                       if e.get("kind") == "text"),
            "text_narrowing": "不使用 transform 压窄文字；长标题通过减字号与增加行数"
                              "（竖版 3 行、横版 2 行）解决，交付 .snapshot 中无 "
                              "transform 属性出现在 <Text> 上",
        },
        "brand_geometry": [
            {"id": "stack-mark", "构件": "叠层主标记",
             "params": {"sheets": 3, "size_portrait": msize_p,
                        "size_wide": msize_w,
                        "offset_ratio": 0.17, "corner_radius_ratio": 0.30,
                        "fills": [s[0] for s in sheets],
                        "borders": ["2 SOLID %s" % s[1] for s in sheets]},
             "cross_round": "形状、叠层数与色阶关系固定；仅尺寸随版式缩放，"
                            "色带随主题换档（第 3 轮浅底改为更饱和的三段蓝，"
                            "以保证亮核仍读得出边界）"},
            {"id": "mark-core", "构件": "主标记亮核",
             "params": {"size_ratio": 0.40, "corner_radius_ratio": 0.34,
                        "fill": col["glow"], "boxShadow": RP["mark_core_shadow"]},
             "cross_round": "固定；与发光球共用亮色，构成「光」的呼应"},
            {"id": "light-orb", "构件": "发光球",
             "params": {"diameter_portrait": dia_p, "diameter_wide": dia_w,
                        "radius_portrait": dia_p // 2, "radius_wide": dia_w // 2,
                        "geometry_source": "由本轮交付 layout 的 orb_core 外接框宽度"
                                           "（即直径）读出，半径为其一半，非手抄配置值",
                        "center_portrait": [(orb_p[0] + orb_p[2]) // 2,
                                            (orb_p[1] + orb_p[3]) // 2],
                        "center_wide": [(orb_w[0] + orb_w[2]) // 2,
                                        (orb_w[1] + orb_w[3]) // 2],
                        "gradient": "RADIAL %s r=%.2f"
                                    % (",".join(RP["core_stops"]),
                                       RP["core_gradius"]),
                        "ring": "直径+%d，1 SOLID %s" % (RP["ring_pad"],
                                                         col["primary_2"]),
                        "halo": "直径 %sr / %sr（竖版/横版），RADIAL %s→%s "
                                "r=%.2f，opacity %.2f"
                                % (RP["halo_scale_p"], RP["halo_scale_w"],
                                   RP["halo_stops"][0], RP["halo_stops"][1],
                                   RP["halo_gradius"], RP["halo_opacity"])},
             "cross_round": "结构与色带关系固定；允许移动与缩放（第二轮按新标题"
                            "行数重排位置与半径；第 3 轮为把辉光完全移出文字区，"
                            "把半径从 3.4r 收到 %sr/%sr 并挪到右列）；不加 "
                            "gradientFocal"
                            % (RP["halo_scale_p"], RP["halo_scale_w"])},
            {"id": "light-band", "构件": "球内光带（叠层）",
             "params": {"count": 3,
                        "width_portrait": [b[2] - b[0] for b in bands_p],
                        "height_portrait": [b[3] - b[1] for b in bands_p],
                        "width_wide": [b[2] - b[0] for b in bands_w],
                        "height_wide": [b[3] - b[1] for b in bands_w],
                        "opacity": [0.90, 0.58, 0.34], "color": col["glow"],
                        "cap": "两端圆角 = 高度的一半，圆头收口"},
             "cross_round": "3 条、自上而下递减宽度与亮度；横版光带略加高；"
                            "随球体半径等比缩放"},
            {"id": "accent-bar", "构件": "主色强调条",
             "params": {"portrait": "156x6，圆角 3，标题与信息之间的唯一分隔线",
                        "wide": "5x34，圆角 2，与眉标并排",
                        "fill": col["primary"]},
             "cross_round": "形状固定，随标题行数变化而在版式中的位置随之移动"},
            {"id": "url-plate", "构件": "牌子族（网址牌 + 报名状态牌）",
             "params": {
                 "url_plate_portrait": "%dx%d，圆角 %d"
                     % (plates[0][2] - plates[0][0], plates[0][3] - plates[0][1],
                        (plates[0][3] - plates[0][1]) // 2),
                 "url_plate_wide": "%dx%d，圆角 %d"
                     % (plates_w[0][2] - plates_w[0][0],
                        plates_w[0][3] - plates_w[0][1],
                        (plates_w[0][3] - plates_w[0][1]) // 2),
                 "entry_badge": ("%dx%d / %dx%d（竖版 / 横版，第二轮新增实例）"
                                  % (plates[1][2] - plates[1][0],
                                     plates[1][3] - plates[1][1],
                                     plates_w[1][2] - plates_w[1][0],
                                     plates_w[1][3] - plates_w[1][1]))
                 if len(plates) > 1 and len(plates_w) > 1 else None,
                 "fill": col["bg_panel"],
                 "border": "网址牌 %s（中性蓝）；"
                           "报名状态牌 2 SOLID %s（主色）"
                           % (RP["url_plate_border"], col["primary"]),
                 "dot": "shape CIRCLE，竖版 %s、横版 %s，fill %s"
                        % (dot_p, dot_w, col["primary"])},
             "cross_round": "形态固定（圆角矩形 + 边框 + 圆头内容）；"
                            "第一轮只有网址牌一个实例，第二轮新增报名状态牌实例，"
                            "以边框色区分语义；shape 与 borderRadius 互斥"
                            "（实测 PARSE_ERROR 约束）"},
        ],
        "brand_geometry_count": 6,
        "brand_geometry_count_note": "3–6 个要求内。报名状态牌是牌子族的第二个实例"
                                     "而非新构件，故构件数仍为 6",
        "compositions": {
            "portrait": ("纵向结构：顶部品牌行 → 眉标 → 主标题%d行 → 强调条 → 信息栈"
                         "（日期/讲者%s/网址牌）→ 赞助方 → 报名状态牌；右上"
                         "线叠层水印，发光球移到右中偏下填补标题与信息之间的空区；"
                         "左下氛围 wash"
                         % (sum(1 for e in lay_p
                                if e.get("role", "").startswith("title_line")),
                            "、英语短句" if "clarity_p" in ty else "")),
            "wide": ("横向分栏：左栏品牌行 + 眉标 + 主标题%d行，底部日期 → 讲者 → "
                     "%s网址牌 → 赞助方 → 报名状态牌竖排；右栏发光球大图占整栏。"
                     "与竖版不是等比缩放——竖版标题 3 行、横版 2 行；"
                     "竖版球在右中偏下、横版球占右侧整栏中部"
                     % (sum(1 for e in lay_w
                            if e.get("role", "").startswith("title_line")),
                        "英语短句 → " if "clarity_w" in ty else "")),
            "composition_delta_round2": "第二轮标题由 10 字 2 行变为 27 字（竖版 3 行 / "
                                        "横版 2 行），字号由 132/116 降到 66/52；"
                                        "新增赞助方与报名状态牌两行信息后，"
                                        "信息栈由 3 行扩到 5 行；发光球半径与位置随之"
                                        "调整以避让长标题，主色与品牌构件形态未变",
            **({"composition_delta_round3":
                "第三轮改浅色主题：全部文字色换成浅底档（ink #0B1B33 / muted #4A5A72 / "
                "primary #0A6FA8 / accent #C2410C），主标题取消青色发光阴影；"
                "网址上方新增英语短句「Clarity through structure」"
                "（竖版 28 / 横版 26，均 ≥24），信息栈由 5 行扩到 6 行。"
                "为让每段文字的实际合成背景都落在页面底或牌子底上，"
                "发光球移到标题与信息栈之间的右列空区，外辉光半径由 3.4r 收到 "
                "%sr（竖版）/ %sr（横版），并用同一构造器生成去文字辅助渲染量取"
                "字形覆盖区内的最差对比度——全部 23 段文字的最小值为 4.8616"
                "（date #C2410C 对页面底 #F5F8FC），见 round-03/contrast-audit.json。"
                "文案、字号阶梯与 6 个品牌构件的形态、层数、圆角比例、条数与递减"
                "关系均未变"
                % (RP["halo_scale_p"], RP["halo_scale_w"])}
               if rnd == 3 else {}),
        },
        "round_intro": ("第一轮基线：首次建立整套设计 token 与品牌几何，"
                        "并产出 launch-portrait(1080x1350) 与 launch-wide(1440x810) 两张成品"
                        if rnd == 1 else None),
        "changes": changes,
    }
    if doc.get("round_intro") is None:
        del doc["round_intro"]
    p = rdir / "design-tokens.json"
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    return p


def rel(p: pathlib.Path) -> str:
    return p.relative_to(SUITE_ROOT).as_posix()


def main() -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8")
    rnd = int(sys.argv[1])
    tag = sys.argv[2] if len(sys.argv) > 2 else ""
    ch_path = sys.argv[3] if len(sys.argv) > 3 else ""
    changes = json.loads(pathlib.Path(ch_path).read_text(encoding="utf-8")) \
        if ch_path and pathlib.Path(ch_path).exists() else []
    audit = audit_round(rnd, tag)
    for key in NAMES:
        a = audit[key]
        print("== %s / %s ==" % (key, a["slug"]))
        print("   尺寸 %s 墨迹条目 %d" % (a["actual_png_size"], len(a["items"])))
        print("   完整性", all(c["match"] for c in a["completeness"]),
              "| 字号", all(s["ok"] for s in a["sizes"]),
              "| 碰撞", all(c["ok"] for c in a["collisions"]))
        print("   留白", a["margins"], "| 占位词", a["placeholders_found"])
        for d in a["orb_distance"]:
            print("     %-12s 到 orb_core 净距 %s px (halo %s px)"
                  % (d["role"], d["gap_to_orb_core_px"],
                     d.get("gap_to_orb_halo_px")))
        for c in a["completeness"]:
            print("     %-11s match=%s  %r" % (c["content_id"], c["match"],
                                               c["normalized_text"]))
        bad_ink = [i["role"] for i in a["items"] if not i["ink"]]
        if bad_ink:
            print("   !! 未取到墨迹:", bad_ink)
    for key in NAMES:
        for c in audit[key]["collisions"]:
            if not c["ok"]:
                print("   !! 碰撞:", key, c)
        for d in audit[key]["orb_distance"]:
            if d["gap_to_orb_core_px"] <= 0:
                print("   !! 文字压球:", key, d)
    print("content-map   ->", rel(write_content_map(rnd, audit)))
    print("design-tokens ->", rel(write_design_tokens(rnd, changes)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
