# -*- coding: utf-8 -*-
"""A21 round-03 对比度审计：普通文字 vs 实际合成背景 ≥4.5:1（未舍入判值）。

方法：把 round-03 DSL 生成脚本中每处文字的 Positioned 框（DSL 常量，即字形占用
范围的外包框）映射到同构布局的"去文字辅助渲染"PNG 上，逐像素取与该文字前景色
对比度最差的背景像素；前景色另在最终 PNG 的同框内验证真实存在（±3/通道）。
"""
import json
import math
from datetime import datetime, timedelta, timezone
from PIL import Image

RUN = "20261016T164020-m1"
OUT = f"outputs/{RUN}/A21/round-03"
BGP = f"tmp/{RUN}/A21/bg-data/r03-portrait-bg.png"
BGW = f"tmp/{RUN}/A21/bg-data/r03-wide-bg.png"
TZ = timezone(timedelta(hours=8))

INK, INK2, MUT = "#0F1B2D", "#2A3A54", "#44536B"
TEAL_INK = "#085F55"
CHIP_BG, CHIP_TX = "#0D2237", "#7FF3E6"
PILL_BG = "#FCFEFE"
SPONSOR_LABEL, SPONSOR_NAME = "#506681", "#44536B"


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def lin(c01):
    """sRGB 逆 EOTF 通道线性化（未舍入）。"""
    return c01 / 12.92 if c01 <= 0.04045 else ((c01 + 0.055) / 1.055) ** 2.4


def lum(rgb01):
    r, g, b = (lin(c) for c in rgb01)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def lum_hex(h):
    return lum(tuple(x / 255 for x in hexrgb(h)))


fg_cache = {}


def fg_lum(h):
    if h not in fg_cache:
        fg_cache[h] = lum_hex(h)
    return fg_cache[h]


RING_ANCHORS = {
    "portrait": [("ghost-ring-outer", (540, 380), 240),
                 ("ghost-ring-inner", (540, 380), 180)],
    "wide": [("ghost-ring-outer", (322, 344), 212),
             ("ghost-ring-inner", (322, 344), 158)],
}


def classify_bg(x, y, rgb, canvas):
    """识别最差像素所属背景成分，留证说明。"""
    r, g, b = rgb
    for kind, c, rr in RING_ANCHORS[canvas]:
        if abs(math.hypot(x - c[0], y - c[1]) - rr) <= 4:
            return kind
    if r < 40 and g < 60 and b < 80:
        return "url-chip-dark"
    if r > 240 and g > 248 and b > 248:
        return "free-pill-white"
    if abs(r - 19) < 40 and abs(g - 156) < 40 and abs(b - 217) < 40:
        return "beacon-halo"
    if abs(r - 207) < 14 and abs(g - 227) < 14 and abs(b - 239) < 14:
        return "ghost-rule-or-ring"
    return "base-gradient"


def worst_in(bgimg, box, fg_h):
    """取框内与 fg 对比度最差的背景像素（未舍入 ratio 最小者）。"""
    fgL = fg_lum(fg_h)
    l, t, r, b = box
    best = None
    px = bgimg.crop((l, t, r, b))
    w, h = px.size
    for j in range(h):
        for i in range(w):
            p = px.getpixel((i, j))[:3]
            bl = lum(tuple(c / 255 for c in p))
            hi, lo = (fgL, bl) if fgL >= bl else (bl, fgL)
            ratio = (hi + 0.05) / (lo + 0.05)
            if best is None or ratio < best["ratio"]:
                best = {
                    "x": l + i, "y": t + j, "rgb": list(p), "luminance": bl,
                    "ratio": ratio,
                }
    best["hex"] = "#{:02X}{:02X}{:02X}".format(*best["rgb"])
    best["component"] = classify_bg(best["x"], best["y"], best["rgb"], bgimg.tag)
    return best


def profile_core(img, box, fg, exclude_below=None):
    """行剖面墨迹框：crop 内逐行统计与 fg（±3/通道）匹配的像素，
    返回 union bbox（绝对坐标）与像素数；exclude_below 为 y 排除线（归属链用）。"""
    fr, fgr_, fb = hexrgb(fg)
    l, t, r, b = box
    crop = img.crop(box)
    cpx = crop.load()
    cw, ch = crop.size
    xs, ys, cnt = [], [], 0
    for j in range(ch):
        ya = t + j
        if exclude_below is not None and ya <= exclude_below:
            continue
        hit = False
        for i in range(cw):
            p = cpx[i, j]
            if abs(p[0] - fr) <= 3 and abs(p[1] - fgr_) <= 3 and abs(p[2] - fb) <= 3:
                cnt += 1
                hit = True
                xs.append(i)
        if hit:
            ys.append(ya)
    if not xs:
        return None, 0
    return [l + min(xs), min(ys), l + max(xs), max(ys)], cnt


def chain_bands(fin, canvas, chain_ids, runs_list):
    """链脊柱整体行剖面 → 连续墨带 → 按期望墨顶(box_t+0.2H)就近归属。"""
    src = {it[0]: it for it in runs_list}
    boxes = [src[r][3] for r in chain_ids]
    fg = src[chain_ids[0]][4]
    ub = (min(b[0] for b in boxes), min(b[1] for b in boxes),
          max(b[2] for b in boxes), max(b[3] for b in boxes))
    l, t, r, b = ub
    crop = fin.crop(ub)
    cpx = crop.load()
    cw, ch = crop.size
    fr, fgr_, fb = hexrgb(fg)
    bands = []
    cur = None
    for j in range(ch):
        n = 0
        x0 = x1 = None
        for i in range(cw):
            p = cpx[i, j]
            if abs(p[0] - fr) <= 3 and abs(p[1] - fgr_) <= 3 and abs(p[2] - fb) <= 3:
                n += 1
                x0 = i if x0 is None else x0
                x1 = i
        y = t + j
        if n:
            if cur is None:
                cur = [y, y, l + x0, l + x1, n]
            else:
                cur[1] = y
                cur[2] = min(cur[2], l + x0)
                cur[3] = max(cur[3], l + x1)
                cur[4] += n
        else:
            if cur:
                bands.append(tuple(cur))
                cur = None
    if cur:
        bands.append(tuple(cur))
    assigned = {}
    used = set()
    for rid, box in zip(chain_ids, boxes):
        exp = box[1] + (box[3] - box[1]) * 0.2
        best, bestd = None, 1e9
        for bd in bands:
            if id(bd) in used:
                continue
            d = abs(bd[0] - exp)
            if d < bestd and bd[0] <= exp + 10 and bd[0] >= exp - 8:
                best, bestd = bd, d
        if best is None:
            assigned[rid] = None
            continue
        used.add(id(best))
        assigned[rid] = best
    return assigned


def run_audit(dsl_path, png_path, bg_path, canvas, runs, tag):
    bg = Image.open(bg_path).convert("RGB")
    bg.tag = canvas
    fin = Image.open(png_path).convert("RGB")
    chains = {"portrait": ["TR-P02", "TR-P03", "TR-P04"],
              "wide": ["TR-W02", "TR-W03", "TR-W04"]}  # box 垂直重叠，按序归属
    chain_core = chain_bands(fin, canvas, chains[canvas], runs)
    chain_next_bottom = {}
    rep = {
        "image": dsl_path.split("/")[-1].replace(".snapshot", ".png"),
        "dsl": dsl_path,
        "canvas": canvas,
        "background_probe": {
            "path_base": "suite_root",
            "path": bg_path,
            "note": "去文字辅助渲染：同构布局删除全部 Text（含仅含 Text 的 "
                    "Positioned 包装），保留渐变底/幽灵环/点阵/白胶囊/深色网址胶囊",
        },
        "text_runs": [],
        "detailed_samples": [],
    }
    for rid, role, text, box, fg, size in runs:
        # 字形范围：行剖面墨迹核框（±3/通道）+ 外扩 2px 反锯齿边；标题链行
        # （box 垂直重叠）使用整链脊柱墨带，按期望墨顶就近归属。
        in_chain = rid in chains[canvas]
        if in_chain and chain_core.get(rid):
            y0, y1, x0, x1, cnt = chain_core[rid]
            core = [x0, y0, x1, y1]
        else:
            excl = chain_next_bottom.get(canvas) if False else None
            core, cnt = profile_core(fin, box, fg, excl)
        if core is None:
            core = list(box)
        if in_chain:
            chain_next_bottom[canvas] = core[3]
        gl = (max(box[0], core[0] - 2), max(box[1], core[1] - 2),
              min(box[2], core[2] + 3), min(box[3], core[3] + 3))
        w = worst_in(bg, gl, fg)
        fL = fg_lum(fg)
        hi, lo = (fL, w["luminance"]) if fL >= w["luminance"] else (w["luminance"], fL)
        ratio_repr = repr((hi + 0.05) / (lo + 0.05))
        ratio = (hi + 0.05) / (lo + 0.05)
        passed = ratio >= 4.5
        confirmed = cnt >= 10
        item = {
            "id": rid, "role": role, "text": text,
            "font_px": size,
            "covered_range": list(box),
            "glyph_band_core": list(core),
            "glyph_range_measured": list(gl),
            "glyph_source": "行剖面（±3/通道）墨迹核框；链行归属排除上一行墨迹；"
                            "gl = core 外扩左上2/右下3px",
            "fg_pixels_matched": cnt,
            "fg_color": fg, "fg_luminance": round(fL, 6),
            "background_source": "去文字辅助渲染实际合成背景，字形范围内逐像素取最劣",
            "worst_background": {
                "x": w["x"], "y": w["y"], "hex": w["hex"],
                "rgb": w["rgb"], "luminance": round(w["luminance"], 6),
                "component": w["component"],
            },
            "contrast_ratio_unrounded_repr": ratio_repr,
            "contrast_ratio_6dp": round(ratio, 6),
            "threshold": 4.5,
            "pass_unrounded": passed,
            "fg_render_confirmed": confirmed,
        }
        rep["text_runs"].append(item)
        rep["detailed_samples"].append({
            "sample": rid, "role": role,
            "coordinates": {"covered_range": list(box),
                            "glyph_range": list(gl),
                            "worst_pixel": [w["x"], w["y"]]},
            "colors": {
                "fg_hex": fg, "fg_rgb": list(hexrgb(fg)),
                "bg_hex": w["hex"], "bg_rgb": w["rgb"],
            },
            "luminance": {
                "fg_linear": "{!r}".format(fL),
                "bg_linear": "{!r}".format(w["luminance"]),
                "lighter": "fg" if fL >= w["luminance"] else "bg",
                "darker": "bg" if fL >= w["luminance"] else "fg",
            },
            "computation": (
                "lin(sRGB)=c/255→c≤0.04045?c/12.92:((c+0.055)/1.055)^2.4;"
                "L=0.2126R+0.7152G+0.0722B;"
                f"ratio=({'{!r}'.format(max(fL, w['luminance']))}+0.05)/("
                f"{'{!r}'.format(min(fL, w['luminance']))}+0.05)="
                + ratio_repr
            ),
            "pass_unrounded": passed,
        })
    rep["failing_runs"] = [r["id"] for r in rep["text_runs"]
                           if not r["pass_unrounded"]]
    rep["all_pass"] = all(r["pass_unrounded"] for r in rep["text_runs"])
    n = len(rep["text_runs"])
    rep["runs_total"] = n
    rep["detailed_samples_count"] = len(rep["detailed_samples"])
    print(f"[{tag}] runs={n} min="
          f"{min(r['contrast_ratio_6dp'] for r in rep['text_runs']):.4f} "
          f"all_pass={rep['all_pass']} "
          f"fg_ok={all(r['fg_render_confirmed'] for r in rep['text_runs'])}")
    for r in rep["text_runs"]:
        print(f"  {r['id']:10s} {r['contrast_ratio_6dp']:8.6f} "
              f"worst@({r['worst_background']['x']},{r['worst_background']['y']}) "
              f"bg={r['worst_background']['hex']}/{r['worst_background']['component']}")
    return rep


H = lambda s: int(s * 1.45) + 2  # DSL txt() 行高常量

portrait_runs = [
    ("TR-P01", "eyebrow", "ONLINE LAUNCH", (240, 472, 840, 472 + H(26)), TEAL_INK, 26),
    ("TR-P02", "title_line1", "当所有信息都想成为标题：", (0, 524, 1080, 524 + H(64)), INK, 64),
    ("TR-P03", "title_line2", "让复杂信息变得清晰的", (0, 602, 1080, 602 + H(64)), INK, 64),
    ("TR-P04", "title_line3", "结构化方法", (0, 680, 1080, 680 + H(64)), INK, 64),
    ("TR-P05", "tagline", "叠光 Layerlight 发布活动", (0, 768, 1080, 768 + H(30)), MUT, 30),
    ("TR-P06", "date", "2026.11.07 19:30", (0, 828, 1080, 828 + H(46)), INK, 46),
    ("TR-P07", "speakers", "讲者：林川 / 苏言", (0, 918, 1080, 918 + H(30)), INK2, 30),
    ("TR-P08", "sponsor_prefix", "赞助", (0, 986, 1080, 986 + H(26)), SPONSOR_LABEL, 26),
    ("TR-P09", "sponsor_name", "Northstar Research / 云构工具",
     (0, 986, 1080, 986 + H(26)), SPONSOR_NAME, 26),
    ("TR-P10", "free_pill_text", "免费参加 · 无需报名", (390, 1045, 690, 1045 + H(26)),
     TEAL_INK, 26),
    ("TR-P11", "tagline_en", "Clarity through structure", (0, 1108, 1080, 1108 + H(26)),
     TEAL_INK, 26),
    ("TR-P12", "url_text", "layerlight.example.org", (310, 1168, 770, 1168 + 50),
     CHIP_TX, 30),
]

wide_runs = [
    ("TR-W01", "eyebrow", "ONLINE LAUNCH", (660, 150, 1320, 150 + H(26)), TEAL_INK, 26),
    ("TR-W02", "title_line1", "当所有信息都想成为标题：", (660, 206, 1350, 206 + H(54)), INK, 54),
    ("TR-W03", "title_line2", "让复杂信息变得清晰的", (660, 268, 1350, 268 + H(54)), INK, 54),
    ("TR-W04", "title_line3", "结构化方法", (660, 330, 1350, 330 + H(54)), INK, 54),
    ("TR-W05", "tagline", "叠光 Layerlight 发布活动", (660, 398, 1350, 398 + H(28)), MUT, 28),
    ("TR-W06", "date", "2026.11.07 19:30", (660, 442, 1350, 442 + H(44)), INK, 44),
    ("TR-W07", "speakers", "讲者：林川 / 苏言", (660, 520, 1320, 520 + H(28)), INK2, 28),
    ("TR-W08", "sponsor_prefix", "赞助", (660, 572, 1350, 572 + H(26)), SPONSOR_LABEL, 26),
    ("TR-W09", "sponsor_name", "Northstar Research / 云构工具",
     (660, 572, 1350, 572 + H(26)), SPONSOR_NAME, 26),
    ("TR-W10", "tagline_en", "Clarity through structure", (660, 624, 1350, 624 + H(26)),
     TEAL_INK, 26),
    ("TR-W11", "url_text", "layerlight.example.org", (660, 679, 1120, 679 + 47),
     CHIP_TX, 30),
    ("TR-W12", "free_pill_text", "免费参加 · 无需报名", (122, 629, 398, 629 + H(26)),
     TEAL_INK, 26),
]

img_p = run_audit("launch-portrait.snapshot", f"{OUT}/launch-portrait.png",
                  BGP, "portrait", portrait_runs, "portrait")
img_w = run_audit("launch-wide.snapshot", f"{OUT}/launch-wide.png",
                  BGW, "wide", wide_runs, "wide")

audit = {
    "schema_version": 1,
    "task_id": "A21",
    "path_base": "output_dir",
    "round": 3,
    "generated_at": datetime.now(TZ).isoformat(timespec="seconds"),
    "formula": {
        "standard": "WCAG 2.x 相对亮度对比度（sRGB 线性化）",
        "linearization": "通道 c=c_raw/255；c≤0.04045 → c/12.92，否则 ((c+0.055)/1.055)^2.4",
        "luminance": "L=0.2126*R_lin+0.7152*G_lin+0.0722*B_lin",
        "contrast": "ratio=(L_lighter+0.05)/(L_darker+0.05)",
        "threshold": 4.5,
        "unrounded_judgement": True,
        "note": "判定采用全程未舍入浮点值；JSON 中的 6 位小数仅为展示，"
                "ratio_unrounded_repr 保留 repr 精度。未使用 UA/特殊公式豁免。",
    },
    "background_method": {
        "probe": "每处文字使用同构布局的『去文字辅助渲染』PNG（删除全部 Text 及"
                 "仅含 Text 的 Positioned 包装，保留全部容器/净值装饰），在文字 "
                 "covered_range 内逐像素计算与前景色的对比度，取最小者作为该段"
                 "文字的真实背景最差位置样本（含渐变底、幽灵环、点阵、白胶囊、"
                 "深色胶囊的合成结果）。",
        "fg_check": "前景色采用 DSL 声明值，并在最终 PNG 同框内实测：与声明色"
                    "逐通道差≤3 的核心字形像素 ≥10 才认定该前景真实渲染。",
        "coverage": "text_runs 覆盖浅色主题全部普通文字（12 段/图），含 Sponsor "
                    "行两种色彩 run 与两处胶囊/胶囊内文字；背景最差样本取"
                    "『最终图实测字形范围（外扩2px）』内像素，避免把字形范围外"
                    "的装饰（信标点/渐变条/胶囊边框/圆角外侧）误计为文字背景。",
    },
    "images": [img_p, img_w],
    "evidence": [
        {
            "kind": "helper-render",
            "path_base": "suite_root",
            "paths": [BGP, BGW],
            "label": "a21-r03-portrait-bg / a21-r03-wide-bg",
            "request_id": "9538823a-657e-4a80-97ab-24abd839f041 / "
                          "ca3ad94f-db48-4eb9-9475-a60a46353618",
            "note": "HTTP 200，复用最终 DSL 结构删去文本；文件保留在临时目录不清理",
        },
        {
            "kind": "visual-review",
            "paths": [f"tmp/{RUN}/A21/steps/r03p-half.png",
                      f"tmp/{RUN}/A21/steps/r03w-half.png",
                      "r03p-top.png", "r03p-title.png", "r03p-mid.png",
                      "r03p-bottom.png", "r03w-top.png", "r03w-bottom.png",
                      "r03p-bg-half.png", "r03w-bg-half.png"],
            "note": "最终两图整图+分区放大查看与辅助版无字核验；视图存 "
                    f"tmp/{RUN}/A21/steps/（部分文件名省略前缀，见 iterations 记录）",
        },
    ],
    "summary": {
        "images": 2,
        "text_runs_total": len(portrait_runs) + len(wide_runs),
        "detailed_samples_total": 2 * 12,
        "all_pass_unrounded": img_p["all_pass"] and img_w["all_pass"],
        "min_ratio_observed_6dp": min(
            r["contrast_ratio_6dp"] for r in img_p["text_runs"] + img_w["text_runs"]
        ),
    },
}

with open(f"{OUT}/contrast-audit.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(audit, f, ensure_ascii=False, indent=1)
print("contrast-audit.json written; summary =", audit["summary"])
