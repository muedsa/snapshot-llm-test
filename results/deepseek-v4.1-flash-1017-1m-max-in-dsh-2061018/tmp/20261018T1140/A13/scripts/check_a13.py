"""A13 checks: black purity, alpha mask match, premultiplied 32x32 previews."""
from __future__ import annotations

import json
import os
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A13"
TMP = ROOT / "tmp" / RUN / TASK
prev = TMP / "previews"
prev.mkdir(parents=True, exist_ok=True)
col = Image.open(TMP / "renders/symbol-color/v004.png").convert("RGBA")
blk = Image.open(TMP / "renders/symbol-black/v004.png").convert("RGBA")

# black purity
viol = 0
amin, amax = 255, 0
for (r, g, b, a) in blk.getdata():
    if a > 0:
        amin = min(amin, a)
        amax = max(amax, a)
        if r != 0 or g != 0 or b != 0:
            viol += 1
alpha_diff = ImageChops.difference(col.getchannel("A"), blk.getchannel("A"))
adiff_max = max(alpha_diff.getdata())
adiff_count = sum(1 for v in alpha_diff.getdata() if v > 0)
outside = 0
for (r, g, b, a) in col.getdata():
    if a == 0 and (r or g or b):
        outside += 1


def premul_resize(im: Image.Image, size=(32, 32)) -> Image.Image:
    src = im.copy()
    px = list(src.getdata())
    prem = [(r * a // 255, g * a // 255, b * a // 255, a) for r, g, b, a in px]
    pim = Image.new("RGBA", src.size)
    pim.putdata(prem)
    small = pim.resize(size, Image.Resampling.LANCZOS)
    out = []
    for r, g, b, a in small.getdata():
        if a == 0:
            out.append((0, 0, 0, 0))
        else:
            out.append((min(255, round(r * 255 / a)), min(255, round(g * 255 / a)),
                        min(255, round(b * 255 / a)), a))
    r = Image.new("RGBA", size)
    r.putdata(out)
    return r


def composite(im: Image.Image, bg=(244, 241, 233)) -> Image.Image:
    base = Image.new("RGBA", im.size, bg + (255,))
    return Image.alpha_composite(base, im).convert("RGB")


for name, im in [("color", col), ("black", blk)]:
    small = premul_resize(im)
    small.save(prev / f"symbol-{name}-32.png")
    composite(small).save(prev / f"view-{name}-32.png")
    composite(small).resize((128, 128), Image.Resampling.NEAREST).save(prev / f"view-{name}-32-4x.png")

for name in ["preview-a", "preview-b"]:
    im = Image.open(prev / f"{name}.png").convert("RGBA")
    small = premul_resize(im)
    small.save(prev / f"{name}-32.png")
    composite(small).save(prev / f"view-{name}-32.png")
    composite(small).resize((128, 128), Image.Resampling.NEAREST).save(prev / f"view-{name}-32-4x.png")

bs = json.loads((TMP / "brand-system.json").read_text(encoding="utf-8"))
bs["black_audit"] = {
    "image": "symbol-black.png",
    "size": [512, 512],
    "alpha_gt_0_pixels": sum(1 for p in blk.getdata() if p[3] > 0),
    "rgb_nonzero_violations": viol,
    "alpha_range": [amin, amax],
    "passed": viol == 0,
    "method": "PIL 解码未预乘 8 位 RGBA；逐像素检查 alpha>0 时 R=G=B=0。",
}
bs["alpha_mask"] = {"color_vs_black_max_diff": adiff_max, "pixels_with_diff": adiff_count,
                    "color_outside_alpha0_rgb_nonzero": outside,
                    "note": "两图标使用同一 logo_a 几何与相同不透明度；差异仅来自抗锯齿。",
                    "passed": adiff_max <= 1}
bs["small_size_check"] = {
    "size": [32, 32],
    "tool": f"Pillow {Image.__version__}",
    "method": "premultiplied RGB + LANCZOS resize + unpremultiply; actual 32px composite on #F4F1E9",
    "alpha_previews": ["tmp/%s/A13/previews/symbol-color-32.png" % RUN, "tmp/%s/A13/previews/symbol-black-32.png" % RUN],
    "view_previews": ["tmp/%s/A13/previews/view-color-32.png" % RUN, "tmp/%s/A13/previews/view-black-32.png" % RUN],
    "direction_previews": ["tmp/%s/A13/previews/view-preview-a-32.png" % RUN, "tmp/%s/A13/previews/view-preview-b-32.png" % RUN],
}
bs["preview_directions"] = [
    {"id": "A", "file": "tmp/%s/A13/previews/preview-a.png" % RUN, "summary": "三层圆角条 + 珊瑚圆环 + 点"},
    {"id": "B", "file": "tmp/%s/A13/previews/preview-b.png" % RUN, "summary": "两条对角梁 + 菱形 + 点"},
]
bs["selected_direction"] = "A"
(TMP / "brand-system.json").write_text(json.dumps(bs, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"black_violations": viol, "alpha_range": [amin, amax], "alpha_diff_max": adiff_max,
                  "alpha_diff_count": adiff_count, "outside_nonzero": outside,
                  "pil": Image.__version__}, ensure_ascii=False))
