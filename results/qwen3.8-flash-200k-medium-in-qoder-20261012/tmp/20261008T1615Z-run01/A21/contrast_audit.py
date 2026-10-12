"""A21 第 3 轮：正文对比度审计（WCAG 2.1 相对亮度比）。

对每个文字元素同时给出两个背景：
1. measured —— 直接从服务返回的 PNG 里取该元素盒内出现最多的颜色，即真实合成底
   （叠光板压过的地方会自动反映合成结果）；
2. analytic —— 按 DSL 图层顺序把覆盖该文字盒的半透明板/光线逐层 alpha 合成到
   基础底色上，用来交叉验证 measured 不是取样错误。
两者一致（通道差 <=8）且 measured 对比度 >=4.5 才算通过。

用法：
  python tmp/<run_id>/A21/contrast_audit.py --round 3 \
      --png launch-portrait=tmp/<run_id>/A21/preview/r03-portrait-v01.png ...
"""
import argparse
import json
import math
import os
from collections import Counter
from pathlib import Path

from PIL import Image

root = Path(os.environ["SNAPSHOT_TASK_ROOT"]).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
TMP = root / "tmp" / rid / "A21"

ap = argparse.ArgumentParser()
ap.add_argument("--round", type=int, required=True)
ap.add_argument("--png", action="append", default=[])
ap.add_argument("--threshold", type=float, default=4.5)
ap.add_argument("--rot-sign", type=int, default=1,
                    help="服务 Transform 的旋转方向，用装饰采样像素标定")
a = ap.parse_args()

LAY = TMP / "layouts" if a.round == 1 else TMP / "layouts" / ("round-%02d" % a.round)


def chan(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def lum(rgb):
    r, g, b = (chan(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    l1, l2 = lum(fg), lum(bg)
    if l1 < l2:
        l1, l2 = l2, l1
    return round((l1 + 0.05) / (l2 + 0.05), 2)


def hx(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def hxa(s):
    """8 位 hex -> (r,g,b,a)，全部 0..1。"""
    s = s.lstrip("#")
    return (*hx("#" + s[:6]), int(s[6:8], 16) / 255.0)


def over(src, dst):
    """src（rgba 0..1）按 alpha 叠在 dst（rgb 0..1）上。"""
    r, g, b, al = src
    return tuple(dst[i] * (1 - al) + c * al for i, c in enumerate((r, g, b)))


def to255(rgb):
    return tuple(round(c * 255) for c in rgb)


def rect_of(v):
    if "box_px" in v:
        x, y, w, h = v["box_px"]
        return (x, y, x + w, y + h)
    if "center_px" in v and "size_px" in v:
        cx, cy = v["center_px"]
        wd, ht = v["size_px"]
        r = math.radians(abs(v.get("rotation_deg", 0)))
        hw = (wd * math.cos(r) + ht * math.sin(r)) / 2
        hh = (wd * math.sin(r) + ht * math.cos(r)) / 2
        return (cx - hw, cy - hh, cx + hw, cy + hh)
    if "diameter_px" in v:
        cx, cy = v["center_px"]
        rr = v["diameter_px"] / 2
        return (cx - rr, cy - rr, cx + rr, cy + rr)
    if "from_px" in v:
        x1, y1 = v["from_px"]
        x2, y2 = v["to_px"]
        return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
    return None


def hit(v, rect):
    """该装饰元素是否真的压在文字盒上：板/点用外接矩形求交，线用采样求交。"""
    if v.get("shape") == "ray":
        (x1, y1), (x2, y2) = v["from_px"], v["to_px"]
        for k in range(0, 201):
            t = k / 200.0
            px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
            if rect[0] <= px <= rect[2] and rect[1] <= py <= rect[3]:
                return True
        return False
    b = rect_of(v)
    if not b:
        return False
    return not (b[2] <= rect[0] or rect[2] <= b[0] or b[3] <= rect[1] or rect[3] <= b[1])


report = {}
for spec in a.png:
    name, path = spec.split("=", 1)
    plane_doc = json.loads((LAY / (name + ".plane.json")).read_text(encoding="utf-8"))
    plane = plane_doc["plane"]
    img = Image.open(root / path).convert("RGB")
    base_px = Counter(list(img.getdata())[::4]).most_common(1)[0][0]
    base = tuple(c / 255.0 for c in base_px)
    order = list(plane.items())
    rows, fails = [], []
    for idx, (tag, v) in enumerate(order):
        if "text" not in v:
            continue
        x, y, w, h = v["box_px"]
        size = v["font_px"]
        ink_rect = (x, y + (h - size) / 2.0, x + v["est_width_px"], y + (h + size) / 2.0)
        crop = img.crop(tuple(int(c) for c in (x, y, x + w, y + h)))
        cnt = Counter(crop.getdata())
        nominal = hx(v["color"])
        bg_px, n = max(((c, k) for c, k in cnt.items()
                        if max(abs(c[i] - nominal[i] * 255) for i in range(3)) > 60),
                       key=lambda t: t[1])
        comp = base                   # 解析法从基础底色起算
        base_hex = "#%02X%02X%02X" % bg_px
        layers = []
        for t2, v2 in order[:idx]:
            f = v2.get("fill") or (v2.get("color")
                                if v2.get("shape") == "ray" else None)
            if not f or v2.get("shape") not in ("rotated-plate", "ray", "dot"):
                continue
            if hit(v2, ink_rect):
                src = hxa(f) if len(f.lstrip("#")) == 8 else (*hx(f), 1.0)
                comp = over(src, comp)
                layers.append(t2)
        analytic = to255(comp)
        d_meas = max(abs(bg_px[i] - analytic[i]) for i in range(3))
        r = ratio(tuple(round(c * 255) for c in nominal), bg_px)
        row = {"element": tag, "text": v["text"], "font_px": size,
               "text_color": v["color"],
               "measured_bg": base_hex, "analytic_bg": "#%02X%02X%02X" % analytic,
               "layers_under_text": layers,
               "measured_vs_analytic_max_channel_delta": d_meas,
               "contrast_vs_measured_bg": r, "required": a.threshold,
               "pass": r >= a.threshold}
        rows.append(row)
        if r < a.threshold or d_meas > 8:
            fails.append(row)
    report[name] = {"png": path, "size": list(img.size),
                    "canvas_base_color": "#%02X%02X%02X" % base_px,
                    "elements": rows,
                    "min_contrast": min(x["contrast_vs_measured_bg"] for x in rows),
                    "count": len(rows),
                    "counts_at_least_6_body_samples": len(rows) >= 6}
    # 叠层清单：每个半透明装饰单独给出解析合成色与 PNG 实测色，
    # 证明审计确实把叠光板算进来了（而不是只看两种颜色）。
    decor = []
    ink_rects = []
    for tag2, vv in order:
        if "text" not in vv:
            continue
        x, y, w, h = vv["box_px"]
        ink_rects.append((tag2, (x, y + (h - vv["font_px"]) / 2.0,
                                 x + vv["est_width_px"], y + (h + vv["font_px"]) / 2.0)))
    def covers_point(v, px, py):
        if v.get("shape") == "ray":
            (x1, y1), (x2, y2) = v["from_px"], v["to_px"]
            dx, dy = x2 - x1, y2 - y1
            L2 = dx * dx + dy * dy or 1.0
            t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
            d = math.hypot(px - (x1 + dx * t), py - (y1 + dy * t))
            return d <= v.get("thickness_px", 3) / 2.0 + 1.5
        if v.get("shape") == "rotated-plate":
            cx0, cy0 = v["center_px"]
            wd, ht = v["size_px"]
            th = math.radians(v.get("rotation_deg", 0)) * a.rot_sign
            dx, dy = px - cx0, py - cy0
            lx = abs(dx * math.cos(th) + dy * math.sin(th))
            ly = abs(-dx * math.sin(th) + dy * math.cos(th))
            # 板是圆角矩形（品牌构件的 radius = 半高，即胶囊形），角外不算覆盖
            r = min(v.get("border_radius_px", 0), wd / 2.0, ht / 2.0)
            ax, ay = wd / 2.0 - r, ht / 2.0 - r
            if lx <= ax and ly <= ht / 2.0:
                return True
            if ly <= ay and lx <= wd / 2.0:
                return True
            return math.hypot(lx - ax, ly - ay) <= r
        b = rect_of(v)
        return bool(b) and b[0] <= px <= b[2] and b[1] <= py <= b[3]

    for tag, v in plane.items():
        f = v.get("fill") or (v.get("color") if v.get("shape") == "ray" else None)
        if not f or len(f.lstrip("#")) != 8 or v.get("shape") not in (
                "rotated-plate", "ray", "dot"):
            continue
        if v.get("shape") == "ray":
            cx = (v["from_px"][0] + v["to_px"][0]) / 2.0
            cy = (v["from_px"][1] + v["to_px"][1]) / 2.0
        else:
            b = rect_of(v)
            cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        # 解析法：按 DSL 图层顺序，把该采样点上的所有半透明层依次合成
        comp = base
        stack = []
        for t2, v2 in order:
            f2 = v2.get("fill") or (v2.get("color")
                                if v2.get("shape") == "ray" else None)
            if not f2 or v2.get("shape") not in ("rotated-plate", "ray", "dot"):
                continue
            if not covers_point(v2, cx, cy):
                continue
            comp = over(hxa(f2) if len(f2.lstrip("#")) == 8 else (*hx(f2), 1.0), comp)
            stack.append(t2)
        comp = to255(comp)
        meas = img.getpixel((int(cx), int(cy)))
        ink_hits = [t for t, r in ink_rects if hit(v, r)]
        decor.append({"element": tag, "shape": v["shape"], "fill": f,
                      "alpha_pct": round(hxa(f)[3] * 100, 1),
                      "sample_px": [round(cx, 1), round(cy, 1)],
                      "stack_at_sample": stack,
                      "note": "采样点上按 DSL 顺序叠加的全部半透明层",
                      "analytic_composite": "#%02X%02X%02X" % comp,
                      "measured_at_sample": "#%02X%02X%02X" % meas,
                      "measured_vs_analytic_max_channel_delta":
                          max(abs(meas[i] - comp[i]) for i in range(3)),
                      "composite_vs_base_luminance_delta":
                          round(abs(lum(tuple(comp)) - lum(tuple(base_px))), 4),
                      "text_ink_boxes_intersecting": ink_hits})
    dmax = max(d["measured_vs_analytic_max_channel_delta"] for d in decor)
    assert dmax <= 24, "%s 叠层合成色与实测差 %s 超过 24（alpha 合成模型失效？）" % (name, dmax)
    report[name]["decor_layers"] = decor
    report[name]["decor_max_channel_delta"] = dmax
    report[name]["decor_layers_checked"] = len(decor)
    report[name]["text_over_any_plate"] = sorted(
        {t for d in decor for t in d["text_ink_boxes_intersecting"]})
    assert not report[name]["text_over_any_plate"], \
        "%s 有文字压在叠光板上：%s" % (name, report[name]["text_over_any_plate"])
    assert not fails, "%s 未通过：%s" % (name, fails)

out = LAY / "contrast-audit.json"
out.write_text(json.dumps({"round": a.round, "method": "WCAG 2.1 相对亮度比；背景取"
                           "服务 PNG 中该元素盒内的众数像素（真实合成底），并按 DSL 图层"
                           "顺序 alpha 合成做交叉验证",
                           "threshold": a.threshold,
                           "decor_note": "每个半透明装饰的采样点都按 DSL 图层顺序把覆盖它"
                           "的全部板/线/点做 alpha 合成，与服务 PNG 实测比较；旋转方向经这"
                           "组采样标定（--rot-sign 1 最大差 %d 通道，-1 最大差 83），"
                           "胶囊端头半径已按圆角计入覆盖判定，边缘亚像素混合允许 <=24。",
                           "images": report},
                          ensure_ascii=False, indent=1), encoding="utf-8")
for k, v in report.items():
    print(k, "文字元素", v["count"], "最低对比度", v["min_contrast"],
          "不达标", sum(1 for e in v["elements"] if not e["pass"]))
    for e in sorted(v["elements"], key=lambda x: x["contrast_vs_measured_bg"])[:4]:
        print("   ", e["contrast_vs_measured_bg"], e["element"], e["measured_bg"],
              "layers", e["layers_under_text"], "Δ", e["measured_vs_analytic_max_channel_delta"])
