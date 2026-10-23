"""A13 像素级工具：alpha 几何量测、纯黑合规检查、预乘 alpha 的 32×32 检查预览。

本题三条硬校验都落在这里，因为它们不能靠看图或看 DSL 推断：

1. **透明底**：`<Snapshot>` 的 background 默认是 transparent（parser-tags 参考：
   "background color transparent 透明画布背景；白底需显式设置"），所以不写 background
   就是透明画布。这里仍对落盘 PNG 实测四角与整体 alpha，确认服务真按 RGBA 输出。

2. **纯黑合规**：题面要求「对原始 PNG 解码后的未预乘 8 位 RGBA 执行，所有 alpha>0
   的像素均须 R=G=B=0，包括半透明抗锯齿边缘；alpha=0 的 RGB 不参与判断」。
   PIL 的 convert("RGBA") 给的就是未预乘 8 位 RGBA。注意抗锯齿边缘的 RGB 不是
   "接近黑"就够——必须逐通道严格等于 0，所以只要有一个构件用了非黑彩色并且和
   另一个构件在黑色版里重叠，边缘像素就可能带色；本工具逐像素判定并给出违规样本。

3. **32×32 检查预览**：题面指定「预乘 alpha 的 Lanczos 重采样，再恢复未预乘表示」。
   直接对未预乘 RGBA 做 Lanczos 会在高对比边缘产生振铃并把白色混进半透明像素；
   预乘后再重采样让每个像素只携带自己那部分覆盖，最后再除回覆盖值，alpha=0 处
   RGB 无意义（题面明确忽略）。

用法（作为库）：
    from a13_pixels import open_rgba, alpha_report, black_check, thumb32
用法（命令行）：
    SNAPSHOT_RUN_ID=<rid> python -I a13_pixels.py <png> [--thumb] [--sheet <png2>]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageChops

import numpy as np

TASK = "A13"
LIGHT_BG = (248, 250, 252)   # 检查用浅底，接近交付白底的浅灰

# Pillow 10.0 的 resize() 没有 antialiased 参数（10.1 才有）；LANCZOS 本身
# 就是带抗锯齿的重采样器，这里只取滤镜常量。
_LANCZOS = getattr(Image, "Resampling", Image).LANCZOS


def open_rgba(path) -> tuple[Image.Image, dict]:
    """读原始 PNG 并转成未预乘 8 位 RGBA，同时返回解码元信息。"""
    im = Image.open(path)
    meta = {"path": str(path), "png_mode": im.mode, "size": list(im.size),
            "png_bits": im.info.get("bits"),
            "png_color_type": im.info.get("color_type"),
            "has_alpha": "A" in im.mode or im.mode in ("LA", "RGBA", "P")}
    im = im.convert("RGBA")
    meta["decoded_mode"] = im.mode
    meta["converted"] = meta["png_mode"] != "RGBA"
    return im, meta


def arr(im: Image.Image) -> np.ndarray:
    """RGBA → uint8 (H, W, 4) 数组。"""
    return np.asarray(im, dtype=np.uint8).astype(np.int16)


def alpha_report(im: Image.Image, corners: bool = True) -> dict:
    """alpha 通道统计与四角透明度（确认画布透明）。"""
    a = arr(im)[:, :, 3]
    h, w = a.shape
    out = {
        "size": [w, h],
        "alpha_min": int(a.min()), "alpha_max": int(a.max()),
        "n_alpha_gt0": int((a > 0).sum()),
        "n_alpha_eq255": int((a == 255).sum()),
        "n_alpha_between": int(((a > 0) & (a < 255)).sum()),
        "n_alpha_eq0": int((a == 0).sum()),
        "coverage_pct": round(float((a > 0).sum()) / (h * w) * 100, 3),
        "distinct_alpha_steps": int(len(np.unique(a))),
    }
    if corners:
        out["corner_alpha"] = {"tl": int(a[0, 0]), "tr": int(a[0, -1]),
                               "bl": int(a[-1, 0]), "br": int(a[-1, -1]),
                               "center": int(a[h // 2, w // 2])}
    return out


def alpha_bbox(im: Image.Image, tol: int = 1) -> list[int] | None:
    """alpha > tol 的包围盒 [left, top, right, bottom]；无墨返回 None。"""
    a = arr(im)[:, :, 3]
    ys, xs = np.nonzero(a > tol)
    if len(xs) == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]


def alpha_in(im: Image.Image, box: list[int], tol: int = 1) -> list[int] | None:
    """给定窗口 [l, t, w, h] 内 alpha>tol 的局部包围盒（返回绝对坐标）。"""
    l, t, w, h = box
    a = arr(im)[t:t + h, l:l + w, 3]
    ys, xs = np.nonzero(a > tol)
    if len(xs) == 0:
        return None
    return [int(l + xs.min()), int(t + ys.min()),
            int(l + xs.max()), int(t + ys.max())]


def profile(im: Image.Image, box: list[int], tol: int = 1) -> dict:
    """窗口内每行 / 每列的覆盖像素数，用于判断圆环孔径、条宽与间距。"""
    l, t, w, h = box
    a = arr(im)[t:t + h, l:l + w, 3]
    rows = (a > tol).sum(axis=1)
    cols = (a > tol).sum(axis=0)
    return {"box": box, "rows": [int(v) for v in rows],
            "cols": [int(v) for v in cols],
            "row_runs": _runs(rows, tol), "col_runs": _runs(cols, tol)}


def line_runs(im: Image.Image, axis: str, at: int, tol: int = 1) -> list[list[int]]:
    """沿一条直线切出 alpha>tol 的实心段，返回 [[起, 止, 峰值], ...]（绝对坐标）。

    profile() 的剖面是"每行有多少覆盖"，只能切出纵向空隙；量圆环描边宽必须
    沿圆心那条线读真实 alpha 值。
    """
    a = arr(im)[:, :, 3]
    v = a[at, :] if axis == "x" else a[:, at]
    out, s = [], None
    for i, val in enumerate(v):
        if val > tol and s is None:
            s = i
        elif val <= tol and s is not None:
            out.append([int(s), int(i - 1), int(v[s:i].max())])
            s = None
    if s is not None:
        out.append([int(s), int(len(v) - 1), int(v[s:].max())])
    return out


def _runs(vec: np.ndarray, tol: int) -> list[list[int]]:
    """把一条覆盖剖面切成 [(起, 止, 峰值)] 的实心段，起止为窗口内相对下标。"""
    runs, s = [], None
    for i, v in enumerate(vec):
        if v > tol and s is None:
            s = i
        elif v <= tol and s is not None:
            seg = vec[s:i]
            runs.append([s, i - 1, int(seg.max())])
            s = None
    if s is not None:
        seg = vec[s:]
        runs.append([s, len(vec) - 1, int(seg.max())])
    return runs


def black_check(im: Image.Image) -> dict:
    """纯黑合规：所有 alpha>0 的像素必须 R=G=B=0。

    逐通道严格相等（不是"接近黑"），半透明抗锯齿边缘同样在判。alpha=0 的像素
    RGB 无意义，不计入。
    """
    d = arr(im)
    a = d[:, :, 3]
    mask = a > 0
    rgb = d[:, :, :3]
    viol = mask & ~np.all(rgb == 0, axis=2)
    n = int(viol.sum())
    out: dict = {
        "method": "对 PNG 解码后的未预乘 8 位 RGBA 逐像素判定 (alpha>0) 且 "
                  "(R!=0 或 G!=0 或 B!=0)；alpha=0 的 RGB 不参与",
        "n_alpha_gt0": int(mask.sum()),
        "n_violation": n,
        "compliant": n == 0,
    }
    if n:
        ys, xs = np.nonzero(viol)
        al = a[ys, xs]
        out.update({
            "violation_alpha_min": int(al.min()),
            "violation_alpha_max": int(al.max()),
            "violation_samples": [
                {"x": int(x), "y": int(y), "rgba": [int(rgb[y, x, 0]),
                                                    int(rgb[y, x, 1]),
                                                    int(rgb[y, x, 2]),
                                                    int(a[y, x])]}
                for x, y in list(zip(xs, ys))[:20]],
        })
    else:
        # 合规时仍记录半透明边缘的实际 RGB，证明不是"没有边缘"而是"边缘为黑"
        edge = mask & (a < 255)
        if int(edge.sum()):
            er = rgb[edge]
            out["edge_pixels"] = int(edge.sum())
            out["edge_rgb_unique"] = [list(t) for t in sorted(
                {tuple(int(v) for v in p) for p in er[:4096]})[:8]]
            out["edge_rgb_max"] = int(er.max())
            out["edge_alpha_range"] = [int(a[edge].min()), int(a[edge].max())]
        else:
            out["edge_pixels"] = 0
    return out


def thumb32(im: Image.Image, size: int = 32) -> tuple[Image.Image, dict]:
    """预乘 alpha → Lanczos 重采样 → 恢复未预乘的 32×32 检查预览。

    返回缩略图与参数记录。alpha=0 处 RGB 置 0（原图值无意义，题面允许忽略）。
    """
    d = arr(im).astype(np.float64)
    a = d[:, :, 3:4] / 255.0
    prem = np.concatenate([d[:, :, :3] * a, d[:, :, 3:4]], axis=2)
    p = Image.fromarray(np.clip(prem, 0, 255).astype(np.uint8), "RGBA")
    small = p.resize((size, size), _LANCZOS)
    s = np.asarray(small, dtype=np.float64).astype(np.float64)
    sa = s[:, :, 3:4]
    inv = np.where(sa > 0, 255.0 / np.maximum(sa, 1.0), 0.0)
    back = np.concatenate([np.clip(s[:, :, :3] * inv, 0, 255),
                           s[:, :, 3:4]], axis=2)
    out = Image.fromarray(np.round(back).astype(np.uint8), "RGBA")
    meta = {
        "tool": "Pillow (PIL)", "pillow_version": Image.__version__,
        "numpy_version": np.__version__,
        "resample_filter": "Image.Resampling.LANCZOS (B-spline/Lanczos 重采样器)",
        "target_size": [size, size],
        "source_size": list(im.size),
        "scale_ratio": round(size / im.width, 6),
        "method": "RGB 预乘 alpha → Lanczos 重采样四通道 → 除以 alpha 恢复"
                  "未预乘表示；alpha=0 处 RGB 置 0（忽略）",
        "added_stroke_or_sharpening": False,
    }
    return out, meta


def composite(im: Image.Image, bg=LIGHT_BG, scale: int = 1) -> Image.Image:
    """合成到浅底上用于肉眼查看；scale=1 即原尺寸，不做任何锐化。"""
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    base = Image.new("RGB", im.size, bg)
    base.paste(im, (0, 0), im)
    return base


def sheet(cells: list[tuple[str, Image.Image]], cell: int = 32,
          magnify: int = 4, pad: int = 24, bg=LIGHT_BG,
          cols: int | None = None) -> Image.Image:
    """检查表：每格左侧是 cell×cell 原尺寸缩略（合成在浅底上），右侧是最近邻
    放大到 cell*magnify 用于看边缘。放大图仅作观察辅助，不替代原尺寸检查。"""
    n = len(cells)
    cols = cols or n
    rows = (n + cols - 1) // cols
    w_cell = cell + cell * magnify + 24
    W = pad + cols * w_cell + (cols - 1) * pad
    H = pad + rows * (cell + 80) + (rows - 1) * pad
    sheet = Image.new("RGB", (W, H), bg)
    for i, (label, im) in enumerate(cells):
        r, c = divmod(i, cols)
        x = pad + c * (w_cell + pad)
        y = pad + r * (cell + 80 + pad)
        sheet.paste(composite(im, bg, 1).resize((cell, cell), Image.NEAREST),
                    (x, y))
        mag = composite(im, bg, magnify).resize(
            (cell * magnify, cell * magnify), Image.NEAREST)
        sheet.paste(mag, (x + cell + 24, y))
    return sheet


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    im, meta = open_rgba(sys.argv[1])
    print(json.dumps({"meta": meta, "alpha": alpha_report(im),
                      "bbox": alpha_bbox(im),
                      "black": black_check(im)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
