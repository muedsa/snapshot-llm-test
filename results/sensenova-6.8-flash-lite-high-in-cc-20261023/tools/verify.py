"""渲染结果的像素级几何核验工具。

用途：不靠肉眼，用像素坐标核验最终图的几何是否与计算一致（柱高、零基线、
折线端点、网格线位置、文本是否存在等）。静态 PNG 无法悬停，故几何核验必须做。

启动基准：总任务根；路径可相对总任务根。
"""

from __future__ import annotations

import struct
from pathlib import Path

import numpy as np
from PIL import Image


def load(path) -> np.ndarray:
    p = Path(path)
    if not p.is_absolute():
        p = Path.cwd() / p
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.int16)


def parse_hex(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def mask_of(arr: np.ndarray, color: str, tol: int = 12) -> np.ndarray:
    r, g, b = parse_hex(color)
    d = np.abs(arr - np.array([r, g, b], dtype=np.int16)).sum(axis=2)
    return d <= tol


def bbox(mask: np.ndarray) -> tuple[int, int, int, int] | None:
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def column_top(mask: np.ndarray, x: int, tol: int = 1) -> int | None:
    """给定列 x（可容差），返回该列中该颜色的最小 y（柱顶）。"""
    lo, hi = max(0, x - tol), min(mask.shape[1], x + tol + 1)
    sub = mask[:, lo:hi]
    ys, xs = np.nonzero(sub)
    if len(ys) == 0:
        return None
    return int(ys.min())


def column_bottom(mask: np.ndarray, x: int, tol: int = 1) -> int | None:
    lo, hi = max(0, x - tol), min(mask.shape[1], x + tol + 1)
    sub = mask[:, lo:hi]
    ys, xs = np.nonzero(sub)
    if len(ys) == 0:
        return None
    return int(ys.max())


def row_y(mask: np.ndarray, x_lo: int, x_hi: int) -> int | None:
    """在 [x_lo,x_hi) 区间内寻找横向细线的 y（取像素数最多的行）。"""
    sub = mask[:, x_lo:x_hi]
    counts = sub.sum(axis=1)
    idx = int(np.argmax(counts))
    if counts[idx] == 0:
        return None
    return idx


def components(mask: np.ndarray, min_px: int = 4) -> list[tuple[int, int, int, int]]:
    """连通域（4 邻域 BFS），返回 bbox 列表。用于找标记点/散点位置。"""
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    out = []
    for y in range(h):
        for x in range(w):
            if not mask[y, x] or seen[y, x]:
                continue
            stack = [(y, x)]
            seen[y, x] = True
            pts = []
            while stack:
                cy, cx = stack.pop()
                pts.append((cy, cx))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
            if len(pts) >= min_px:
                ys = [p[0] for p in pts]
                xs = [p[1] for p in pts]
                out.append((min(xs), min(ys), max(xs), max(ys)))
    return out


def line_vertex(mask: np.ndarray, x: int) -> int | None:
    """折线在第 x 列的中心 y（用于核验折线经过的像素点）。"""
    lo, hi = max(0, x - 1), min(mask.shape[1], x + 2)
    sub = mask[:, lo:hi]
    ys, xs = np.nonzero(sub)
    if len(ys) == 0:
        return None
    return int(round((ys.min() + ys.max()) / 2))


def report(name: str, expected, actual, tol: float = 2.0) -> dict:
    ok = actual is not None and expected is not None and abs(actual - expected) <= tol
    return {"check": name, "expected": expected, "actual": actual,
            "ok": ok, "delta": None if actual is None else round(actual - expected, 3)}


def png_dims(path) -> tuple[int, int]:
    p = Path(path)
    if not p.is_absolute():
        p = Path.cwd() / p
    b = p.read_bytes()[:24]
    return struct.unpack(">II", b[16:24])
