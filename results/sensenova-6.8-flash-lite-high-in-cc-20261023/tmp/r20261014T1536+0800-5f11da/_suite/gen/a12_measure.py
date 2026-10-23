"""A12 像素量测：从真实 PNG 量出指定区域的墨迹盒，供折行/字号/重叠/溢出核验。

设计要点（与 A11 的经验一致）：
- 墨迹判定不写死「深色就是文字」：先用区域内**众数颜色**估计背景，再按欧氏距离
  判墨迹。这样深底浅字的 CTA 带和浅底深字都能量。
- 返回的墨迹盒是**实际渲染范围**，与 DSL 声明盒对照才是核验：声明盒只是意图。

用法：
    python -I a12_measure.py --png <png> --regions regions.json --out out.json
regions.json：{"mode": "light", "regions": [{"tag": "标题", "box": [x, y, w, h],
                                             "window": [x, y, w, h]}]}
`box` 是 DSL 声明盒，`window` 是量测窗口（默认等于 box）。窗口取得比声明盒略大时，
才能量出「墨迹溢出声明盒」；但窗口过大又会把相邻文字的墨迹算进来，所以要手动给。
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
import suite as S  # noqa: E402


def estimate_bg(im: Image.Image, box: list[int]) -> tuple[int, int, int]:
    """区域众数颜色作为背景基准（背景像素数占绝对多数）。"""
    x0, y0, w, h = box
    crop = im.crop((x0, y0, min(x0 + w, im.width), min(y0 + h, im.height)))
    return Counter(crop.getdata()).most_common(1)[0][0][:3]


def ink_bbox(im: Image.Image, box: list[int], tol: float = 40.0) -> list[int] | None:
    """区域内墨迹的 [left, top, right, bottom]；无墨迹返回 None。"""
    x0, y0, w, h = box
    x1 = min(x0 + w, im.width)
    y1 = min(y0 + h, im.height)
    bg = estimate_bg(im, box)
    bbox: list[int] | None = None
    px = im.load()
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y][:3]
            d = ((r - bg[0]) ** 2 + (g - bg[1]) ** 2 + (b - bg[2]) ** 2) ** 0.5
            if d > tol:
                if bbox is None:
                    bbox = [x, y, x, y]
                else:
                    bbox[0] = min(bbox[0], x)
                    bbox[1] = min(bbox[1], y)
                    bbox[2] = max(bbox[2], x)
                    bbox[3] = max(bbox[3], y)
    return bbox


def overlap(a: list[int], b: list[int]) -> list[int] | None:
    """两个 [l, t, r, b] 的相交矩形；不相交返回 None。"""
    l, t = max(a[0], b[0]), max(a[1], b[1])
    r, bo = min(a[2], b[2]), min(a[3], b[3])
    if r < l or bo < t:
        return None
    return [l, t, r, bo]


def run(png: str, regions_spec: str, out: str) -> int:
    im = Image.open(png).convert("RGB")
    spec = json.loads(Path(regions_spec).read_text(encoding="utf-8"))
    results = []
    for reg in spec["regions"]:
        tag = reg["tag"]
        box = list(reg["box"])
        window = list(reg.get("window") or box)
        w, h = box[2], box[3]
        ink = ink_bbox(im, window)
        rec = {
            "tag": tag,
            "box": box,
            "window": window,
            "box_right": box[0] + w,
            "box_bottom": box[1] + h,
            "ink_bbox": ink,
        }
        if ink is not None:
            rec.update({
                "ink_w": ink[2] - ink[0] + 1,
                "ink_h": ink[3] - ink[1] + 1,
                "overflow_left": max(0, box[0] - ink[0]),
                "overflow_right": max(0, ink[2] - (box[0] + w)),
                "overflow_top": max(0, box[1] - ink[1]),
                "overflow_bottom": max(0, ink[3] - (box[1] + h)),
            })
        results.append(rec)
    print(f"png={S.rel(Path(png))} {im.width}x{im.height}")
    for r in results:
        ink = r["ink_bbox"]
        print("  %-16s box=[%d,%d,%d,%d] ink=%s" % (
            r["tag"], r["box"][0], r["box"][1], r["box"][2], r["box"][3], ink))
        if ink is not None:
            print("        ink_w=%d ink_h=%d 溢出 L%d R%d T%d B%d" % (
                r["ink_w"], r["ink_h"], r["overflow_left"], r["overflow_right"],
                r["overflow_top"], r["overflow_bottom"]))
    Path(out).write_text(json.dumps(
        {"png": S.rel(Path(png)), "size_px": [im.width, im.height],
         "mode": spec.get("mode"), "regions": results},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print("out", S.rel(Path(out)))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", required=True)
    ap.add_argument("--regions", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    raise SystemExit(run(a.png, a.regions, a.out))
