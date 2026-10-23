"""A14 像素级工具：白底彩卡的「墨迹」量测与颜色取证。

与 A13 的 a13_pixels.py 不同：A13 交付的是透明底，靠 alpha 找几何；A14 的卡是
实底白卡（#FFFFFF 铺满画布），alpha 恒为 255，alpha 通道里没有几何信息。所以
这里的判据换成「颜色」：把画布与每个槽位的背景色当作参考，凡与参考色相差
超过阈值的像素就算墨迹。

三条硬校验落在这里，因为它们不能靠看图或看 DSL 推断：

1. **安全边距 40**——量整幅墨迹包围盒，四个方向到画布边缘的净空都必须 ≥40。
   这是全批唯一的「不逐槽位硬改」证据链：槽位越界时是墨迹先越出 40，而不是
   先越出我们声明的盒。

2. **标题不与状态徽标碰撞**——在标题盒与徽标盒之间量横向净空：标题墨迹右缘
   与徽标墨迹左缘都必须存在，且两者之间有零墨迹间隙。只靠声明坐标不够，
   因为文字实际墨宽可能超过估算。

3. **状态体系真的画出来了**——在徽标盒内按色相统计像素，确认前景色与底色都
   真的出现在画面上（各有一定像素数），而不是「配色表里写了但没渲染出来」。
   这是「颜色加文字/符号共同区分」的像素级证据：颜色部分靠这里，文字部分靠
   DSL 与逐张查看。

用法（作为库）：
    from a14_pixels import open_rgb, ink_bbox, region_ink, color_counts
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

_LANCZOS = getattr(Image, "Resampling", Image).LANCZOS
PAPER = (255, 255, 255)      # 卡片铺底色
INK_TOL = 24                 # 与参考色的最大分量差 ≤ 此值即算「不是墨迹」


def open_rgb(path) -> tuple[Image.Image, dict]:
    """读 PNG，转成未预乘 8 位 RGB，返回图像与解码元信息。"""
    im = Image.open(path)
    meta = {"path": str(path), "png_mode": im.mode, "size": list(im.size),
            "png_bits": im.info.get("bits"),
            "png_color_type": im.info.get("color_type")}
    im = im.convert("RGB")
    meta["decoded_mode"] = im.mode
    meta["bytes"] = Path(path).stat().st_size if Path(path).exists() else None
    return im, meta


def arr(im: Image.Image) -> np.ndarray:
    return np.asarray(im, dtype=np.uint8).astype(np.int16)


def ink_mask(im: Image.Image, box=None, ref=PAPER, tol=INK_TOL) -> np.ndarray:
    """「墨迹」掩膜：与参考色任一通道相差超过 tol 的像素。

    box 为 [l, t, w, h] 时只在该窗口内取；返回布尔数组（窗口局部坐标）。
    """
    d = arr(im)
    if box is not None:
        l, t, w, h = box
        d = d[t:t + h, l:l + w]
    ref = np.array(ref, dtype=np.int16)
    return np.any(np.abs(d[:, :, :3] - ref) > tol, axis=2)


def ink_bbox(im: Image.Image, box=None, ref=PAPER, tol=INK_TOL,
             local: bool = False) -> list[int] | None:
    """墨迹包围盒 [left, top, right, bottom]；local=True 时返回窗口局部坐标。"""
    m = ink_mask(im, box, ref, tol)
    ys, xs = np.nonzero(m)
    if len(xs) == 0:
        return None
    l, t = (box[0], box[1]) if (box is not None and not local) else (0, 0)
    return [int(l + xs.min()), int(t + ys.min()),
            int(l + xs.max()), int(t + ys.max())]


def region_ink(im: Image.Image, box, ref=PAPER, tol=INK_TOL) -> dict:
    """窗口内的墨迹统计：有没有墨、墨迹实际包围盒、四向净空。

    box 为声明盒 [l, t, r, b]（含右/下缘），返回值给出「墨迹是否越出盒」的
    四向差值：负数表示墨迹已经越出该盒。
    """
    l, t, r, b = [int(round(v)) for v in box]
    win = [l, t, max(0, r - l), max(0, b - t)]
    bb = ink_bbox(im, win, ref, tol, local=False)
    out = {"declared": [l, t, r, b], "ink": bb, "has_ink": bb is not None}
    if bb:
        out.update({
            "ink_w": bb[2] - bb[0] + 1, "ink_h": bb[3] - bb[1] + 1,
            "ink_px": int(ink_mask(im, win, ref, tol).sum()),
            "clear": {"left": round(bb[0] - l, 2),
                      "top": round(bb[1] - t, 2),
                      "right": round(r - bb[2], 2),
                      "bottom": round(b - bb[3], 2)},
        })
    return out


def color_counts(im: Image.Image, box, targets: dict, tol=32) -> dict:
    """窗口内逐个目标色的像素数与占比。

    targets 形如 {"foreground": "#15803D", "background": "#DCFCE7"}。
    tol 给宽一点：文字与图形的抗锯齿边缘会与纯色目标有梯度，32 能覆盖主要
    实心部分，又不至于把相邻色相算进来。
    """
    l, t, r, b = [int(round(v)) for v in box]
    d = arr(im)[t:b, l:r]
    out = {}
    for name, hexc in targets.items():
        hx = hexc.lstrip("#")
        target = np.array([int(hx[i:i + 2], 16) for i in (0, 2, 4)],
                          dtype=np.int16)
        near = np.all(np.abs(d[:, :, :3] - target) <= tol, axis=2)
        n = int(near.sum())
        out[name] = {"target": hexc, "pixels": n,
                     "pct_of_region": round(n / max(1, (r - l) * (b - t)) * 100, 3)}
    return out


def row_bands(im: Image.Image, box, ref=PAPER, tol=INK_TOL) -> list[list[int]]:
    """窗口内按行统计墨迹，切成连续的行带。用来数「标题实际排成了几行」。"""
    l, t, r, b = [int(round(v)) for v in box]
    m = ink_mask(im, [l, t, r - l, b - t], ref, tol)
    rows = m.sum(axis=1)
    bands, s = [], None
    for i, v in enumerate(rows):
        if v > 0 and s is None:
            s = i
        elif v == 0 and s is not None:
            bands.append([int(t + s), int(t + i - 1)])
            s = None
    if s is not None:
        bands.append([int(t + s), int(t + len(rows) - 1)])
    return bands


def dominant(im: Image.Image, box=None, topn: int = 6) -> list:
    """窗口内最主要的颜色（量化到 8 级），用于确认「没灰底」这类判断。"""
    d = arr(im)
    if box is not None:
        l, t, r, b = box
        d = d[t:b, l:r]
    q = (d[:, :, :3] // 32) * 32
    flat = [tuple(int(v) for v in p) for p in q.reshape(-1, 3)]
    uniq = {}
    for p in flat:
        uniq[p] = uniq.get(p, 0) + 1
    tot = sum(uniq.values())
    return [{"rgb": list(c), "pixels": n,
             "pct": round(n / max(1, tot) * 100, 2)}
            for c, n in sorted(uniq.items(), key=lambda kv: -kv[1])[:topn]]


def contact_sheet(images: list[tuple[str, Image.Image]], out: Path,
                  cell_w: int = 600, gap: int = 16, bg=(226, 232, 240)) -> tuple:
    """接触表：两列排布，每张卡等比缩到 cell_w 宽。仅作一致性检查辅助，
    **不替代**逐张查看最终服务原图。"""
    scale = cell_w / images[0][1].width
    ch = int(round(images[0][1].height * scale))
    cols, n = 2, len(images)
    rows = (n + cols - 1) // cols
    W = gap + cols * cell_w + (cols - 1) * gap
    H = gap + rows * (ch + 22) + (rows - 1) * gap
    sheet = Image.new("RGB", (W, H), bg)
    for i, (label, im) in enumerate(images):
        r, c = divmod(i, cols)
        x = gap + c * (cell_w + gap)
        y = gap + r * (ch + 22 + gap)
        sheet.paste(im.convert("RGB").resize((cell_w, ch), _LANCZOS), (x, y))
    sheet.save(out, format="PNG")
    return {"path": str(out), "size": [W, H], "cell_w": cell_w, "cell_h": ch,
            "cols": cols, "rows": rows, "gap": gap, "cells": [l for l, _ in images]}


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    im, meta = open_rgb(sys.argv[1])
    import json
    print(json.dumps({"meta": meta, "ink_bbox": ink_bbox(im),
                      "dominant": dominant(im)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
