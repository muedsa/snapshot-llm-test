# -*- coding: utf-8 -*-
"""A13 小尺寸与合规审计：
1) 32×32 预览：预乘 alpha → LANCZOS 缩小 → 反预乘恢复非预乘 RGBA，保 alpha；合成浅底看图 + 8× 边缘放大。
2) 黑版纯黑审计：alpha>0 像素 R=G=B=0；记录违例数、alpha 区间。
3) 彩版透明性审计：角落与背景透明度直方图摘要。
4) 同构检查：两版 512 的 alpha 覆盖轮廓二值化对比（几何相同）。
记录 PIL 版本与参数。"""
import io, sys, json, os
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image
OUT = "outputs/20261016T164020-m1/A13"
STEPS = "tmp/20261016T164020-m1/A13/steps"
os.makedirs(STEPS, exist_ok=True)
DEBUG = {
    "tool": "Pillow %s" % Image.__version__ if hasattr(Image, "__version__") else __import__("PIL").__version__,
    "resample": "Image.Resampling.LANCZOS",
    "pipeline": "unpremultiplied RGBA -> premultiply (c*a/255) -> LANCZOS 512->32 -> unpremultiply (c*255/a) -> clamp",
    "note": "PNG 为非预乘 RGBA；线性预乘避免暗边晕染；黑版权重核用解码后的非预乘像素",
}
try:
    import PIL
    DEBUG["tool"] = "Pillow " + PIL.__version__
except Exception:
    pass

def premultiply_to_32(path, size=32):
    im = Image.open(path).convert("RGBA")
    px = im.load()
    pm = Image.new("RGBA", im.size)
    ppx = pm.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            ppx[x, y] = (r * a // 255, g * a // 255, b * a // 255, a)
    small = pm.resize((size, size), Image.Resampling.LANCZOS)
    sp = small.load()
    out = Image.new("RGBA", (size, size))
    op = out.load()
    for y in range(size):
        for x in range(size):
            r, g, b, a = sp[x, y]
            if a > 0:
                op[x, y] = (min(255, r * 255 // max(1, a)), min(255, g * 255 // max(1, a)),
                            min(255, b * 255 // max(1, a)), a)
    return out

def on_paper(rgba, bg=(244, 249, 255)):
    bgim = Image.new("RGB", rgba.size, bg)
    bgim.paste(rgba, (0, 0), rgba)
    return bgim

report = {"tool": DEBUG, "icons": {}}
for name in ("symbol-color", "symbol-black"):
    src = os.path.join(OUT, name + ".png")
    sq = premultiply_to_32(src)
    sq.save(os.path.join(STEPS, name + "-32.png"))
    on_paper(sq).save(os.path.join(STEPS, name + "-32_on_paper.png"))
    big = sq.resize((256, 256), Image.Resampling.NEAREST)
    on_paper(big).save(os.path.join(STEPS, name + "-32_zoom8.png"))
    im = Image.open(src).convert("RGBA")
    hist = im.getchannel("A").histogram()
    nz = sum(hist[1:])
    report["icons"][name] = {
        "size": im.size, "mode": im.mode,
        "alpha_hist_nonzero_buckets": {str(i): c for i, c in enumerate(hist) if c},
        "opaque_px": hist[255], "transparent_px": hist[0], "partial_px": nz - hist[255] - hist[0],
    }

# ---- 黑版纯黑审计（非预乘解码像素） ----
im = Image.open(os.path.join(OUT, "symbol-black.png")).convert("RGBA")
px = im.load()
viol, alpha_min, alpha_max = 0, None, 0
for y in range(im.height):
    for x in range(im.width):
        r, g, b, a = px[x, y]
        if a > 0:
            alpha_min = a if alpha_min is None else min(alpha_min, a)
            alpha_max = max(alpha_max, a)
            if r != 0 or g != 0 or b != 0:
                viol += 1
report["black_purity"] = {
    "requirement": "非预乘 RGBA 中一切 alpha>0 像素 RGB 必须为 0",
    "violating_px": viol, "alpha_range_active": [alpha_min, alpha_max],
    "pass": viol == 0,
}

# ---- 同构：彩版/黑版 alpha 覆盖轮廓（阈值 a≥8 的二值盒并集）是否一致 ----
def silhouette(path):
    im = Image.open(path).convert("RGBA")
    ss = im.resize((64, 64), Image.Resampling.BILINEAR)
    sp = ss.load()
    S = set()
    for y in range(64):
        for x in range(64):
            if sp[x, y][3] >= 8:
                S.add((x, y))
    return S
s1, s2 = silhouette(os.path.join(OUT, "symbol-color.png")), silhouette(os.path.join(OUT, "symbol-black.png"))
sym_diff = len(s1 ^ s2)
report["geometry_match"] = {"unmatched_cells_64": sym_diff, "pass": sym_diff <= 6,
                            "method": "两版各双线性缩至 64、alpha≥8 二值掩码对称差（AA 边缘容差 6 格）"}

json.dump(report, open(os.path.join(STEPS, "size-audit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({"black": report["black_purity"], "geometry": report["geometry_match"],
                  "color_alpha_nonzero": report["icons"]["symbol-color"]["alpha_hist_nonzero_buckets"]},
                 ensure_ascii=False))
