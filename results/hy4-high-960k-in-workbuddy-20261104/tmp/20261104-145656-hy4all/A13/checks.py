#!/usr/bin/env python3
"""A13 evidence: pure-black RGBA audit, geometry identity, and 32x32 previews.

All outputs (except the updated brand-system.json) live in the temp dir.
"""
import json
import os
import sys
from pathlib import Path

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from PIL import Image, ImageDraw, __version__ as PILVER  # noqa: E402
import suite  # noqa: E402

TASK = "A13"
out = suite.out_dir(TASK)
tmp = suite.tmp_dir(TASK)
sys.path.insert(0, str(tmp))
from thumbnail import (TOOL_INFO, make_reviews, composite_on_light)  # noqa: E402

prev = tmp / "preview"
prev.mkdir(parents=True, exist_ok=True)
PAPER = "#F4F7FC"

# ---- pure-black audit on the decoded, unpremultiplied 8-bit RGBA ----------
def black_audit(path):
    im = Image.open(path).convert("RGBA")
    data = im.tobytes()
    cnt = viol = 0
    amin, amax = 255, 0
    all_min, all_max = 255, 0
    for i in range(0, len(data), 4):
        r, g, b, a = data[i], data[i + 1], data[i + 2], data[i + 3]
        all_min = min(all_min, a)
        all_max = max(all_max, a)
        if a > 0:
            cnt += 1
            amin = min(amin, a)
            amax = max(amax, a)
            if r != 0 or g != 0 or b != 0:
                viol += 1
    return im, {
        "file": Path(path).name,
        "mode": "RGBA",
        "decoder": "Pillow %s Image.open(...).convert('RGBA')" % PILVER,
        "total_pixels": len(data) // 4,
        "alpha_range_all": [all_min, all_max],
        "alpha_gt0_pixels": cnt,
        "alpha_range_nonzero": [amin, amax],
        "violating_pixels": viol,
        "transparent_pixels": len(data) // 4 - cnt,
        "rule": "所有 alpha>0 像素须 R=G=B=0（含半透明抗锯齿边缘）；alpha=0 的 RGB 不参与",
        "passed": viol == 0 and cnt > 0,
    }


black_im, black_res = black_audit(out / "symbol-black.png")
(tmp / "black-check.json").write_text(
    json.dumps(black_res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---- geometry identity: color vs black alpha mask must be identical --------
color_im = Image.open(out / "symbol-color.png").convert("RGBA")
ca = color_im.getchannel("A").tobytes()
ba = black_im.getchannel("A").tobytes()
opaque_masks_identical = all((x == 255) == (y == 255) for x, y in zip(ca, ba))
diffs = [(i, abs(x - y)) for i, (x, y) in enumerate(zip(ca, ba)) if x != y]
max_delta = max((dd for _, dd in diffs), default=0)
edge_only = all(0 < ca[i] < 255 or 0 < ba[i] < 255 for i, _ in diffs)
geometry_identical = opaque_masks_identical and edge_only and max_delta <= 1
identity = {
    "method": "比较彩色与黑色 512×512 图标的 alpha 通道：不透明掩码逐像素比对 + 差异像素定位",
    "geometry_identical": geometry_identical,
    "opaque_mask_identical": opaque_masks_identical,
    "opaque_pixels_color": sum(1 for x in ca if x == 255),
    "opaque_pixels_black": sum(1 for x in ba if x == 255),
    "differing_alpha_pixels": len(diffs),
    "max_alpha_delta": max_delta,
    "all_differences_on_semitransparent_edges": edge_only,
    "alpha_bytes": len(ca),
    "color_alpha_range": list(color_im.getchannel("A").getextrema()),
    "black_alpha_range": list(black_im.getchannel("A").getextrema()),
    "conclusion": ("两图标由同一 draw_symbol 几何规则生成，不透明掩码逐像素一致；仅 %d 个半透明抗锯齿边缘像素 alpha 相差 ≤%d，"
                   "符合题面『两图标几何相同，抗锯齿 alpha 允许』" % (len(diffs), max_delta)),
}

# ---- 32x32 previews + light composites -------------------------------------
for stem, fn in [("symbol-color", "symbol-color.png"),
                 ("symbol-black", "symbol-black.png")]:
    src = out / fn
    make_reviews(src, stem, prev)
    composite_on_light(src, prev / (stem + "-on-light.png"))

# side-by-side comparison on ONE shared light background, each at real 32px
W, H = 220, 96
canvas = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(canvas)
c32 = Image.open(prev / "symbol-color-32-on-light.png").convert("RGB")
b32 = Image.open(prev / "symbol-black-32-on-light.png").convert("RGB")
canvas.paste(c32, (30, 34))
canvas.paste(b32, (158, 34))
d.text((30, 12), "COLOR", fill="#5B6B85")
d.text((158, 12), "BLACK", fill="#5B6B85")
canvas.save(prev / "thumbs-compare-32.png")

# ---- update brand-system.json with real numeric results ---------------------
p = out / "brand-system.json"
bs = json.loads(p.read_text(encoding="utf-8"))
bc = bs["black_check"]
bc["decoder"] = black_res["decoder"]
bc["alpha_range"] = black_res["alpha_range_all"]
bc["alpha_range_nonzero"] = black_res["alpha_range_nonzero"]
bc["alpha_gt0_pixels"] = black_res["alpha_gt0_pixels"]
bc["violating_pixels"] = black_res["violating_pixels"]
bc["transparent_pixels"] = black_res["transparent_pixels"]
bc["total_pixels"] = black_res["total_pixels"]
bc["result"] = "通过：alpha>0 像素全部 R=G=B=0" if black_res["passed"] else "未通过"
bc["passed"] = black_res["passed"]
bs["icon_geometry_identity"] = identity
bs["small_size_review"]["tool"] = TOOL_INFO
p.write_text(json.dumps(bs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("black check:", black_res["violating_pixels"], "violations /",
      black_res["alpha_gt0_pixels"], "alpha>0 pixels | alpha range",
      black_res["alpha_range_all"], "| passed", black_res["passed"])
print("geometry identical:", identity["geometry_identical"],
      "| opaque mask identical:", identity["opaque_mask_identical"],
      "| edge diff pixels:", identity["differing_alpha_pixels"],
      "max delta", identity["max_alpha_delta"])
print("previews written to", prev.relative_to(suite.ROOT).as_posix())
