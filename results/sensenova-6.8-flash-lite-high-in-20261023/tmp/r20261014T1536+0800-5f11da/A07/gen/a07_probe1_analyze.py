"""A07 探针 1 结果分析（本地，不发请求）。

第一次统计把 `#CBD5E1` 边框、`#EEF2F7`、标签灰 `#64748B` 等都算进了每种颜色
（bbox 变成整幅画布），是判定门槛太松。这里收紧为
  * 像素偏离白底 norm(v) > 60   —— 排除背景、网格、边框这类近白色
  * 投影系数 t >= 0.6           —— 该像素主体就是这个颜色
  * 残差 norm(v - t*w) < 25     —— 颜色方向对得上
对同一份已保存的响应体 `responses/req-a07-probe1-clip.body` 重新分析。

同时给 J / K2 做逐列斜率与厚度实测，判定 45° 段的真实几何。
用法：python -I tmp/<rid>/A07/gen/a07_probe1_analyze.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a07_io as IO  # noqa: E402

from PIL import Image  # noqa: E402

C = {
    "J": "#DC2626", "K": "#2563EB", "K2": "#16A34A", "L": "#7C3AED",
    "N": "#0891B2", "G": "#DB2777", "H": "#1D4ED8", "D": "#D97706",
    "E": "#475569",
}


def mask_of(im: np.ndarray, hexc: str) -> np.ndarray:
    v = 255.0 - im.astype(float)
    c = np.array([int(hexc[1:3], 16), int(hexc[3:5], 16), int(hexc[5:7], 16)])
    w = 255.0 - c
    dot = float(np.dot(w, w))
    t = np.clip(np.sum(v * w, axis=2) / dot, 0.0, 1.0)
    resid = np.linalg.norm(v - t[..., None] * w, axis=2)
    return (np.linalg.norm(v, axis=2) > 60) & (t >= 0.6) & (resid < 25)


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    # 第 1 次提交 400（txt 参数错位），第 2 次 200 落在 -1；这里读已保存的预览副本
    p = IO.dirs()[1] / "preview" / "probe1-clip.png"
    im = np.asarray(Image.open(p).convert("RGB"))
    print("canvas", im.shape[1], "x", im.shape[0], "←", p.name)
    print()

    masks = {}
    for k, hexc in C.items():
        m = mask_of(im, hexc)
        masks[k] = m
        n = int(m.sum())
        if n:
            ys, xs = np.where(m)
            print(f"  {k:<2} {hexc}  {n:7d} px   "
                  f"x {xs.min():4d}..{xs.max():4d}  y {ys.min():4d}..{ys.max():4d}")
        else:
            print(f"  {k:<2} {hexc}  {n:7d} px   （未渲染）")

    print()
    print("---- J / K2 逐列几何（色带中心 y、垂直厚度）----")
    for k in ("J", "K2", "K"):
        m = masks[k]
        runs: list[tuple[int, float, int]] = []
        for xi in range(im.shape[1]):
            ys = np.where(m[:, xi])[0]
            if len(ys) >= 2:
                # 只取最长的一段连续区间（同一列可能有多个色块）
                seg, best = [ys[0]], []
                for a, b in zip(ys[:-1], ys[1:]):
                    if b == a + 1:
                        seg.append(b)
                    else:
                        if len(seg) > len(best):
                            best = seg
                        seg = [b]
                if len(seg) > len(best):
                    best = seg
                if len(best) >= 2:
                    runs.append((xi, (best[0] + best[-1]) / 2,
                                 int(best[-1] - best[0] + 1)))
        if len(runs) < 2:
            print(f"  {k}: 逐列区间不足（{len(runs)} 列），无法拟合")
            continue
        xs = np.array([r[0] for r in runs], float)
        cy = np.array([r[1] for r in runs], float)
        th = np.array([r[2] for r in runs], float)
        # 只看斜线段：找 |Δy/Δx| 最接近 1 的区间
        print(f"  {k}: {len(runs)} 列, x {xs.min():.0f}..{xs.max():.0f}, "
              f"垂直厚度均值 {th.mean():.2f}px（8px 宽 45° 段期望 ≈11.31）")
        # 分段拟合：把相邻列斜率变化 >0.5 处切开
        d = np.diff(cy) / np.maximum(np.diff(xs), 1e-9)
        cuts = np.where(np.abs(np.diff(d)) > 0.5)[0] + 1
        bounds = [0, *list(cuts), len(xs)]
        for i in range(len(bounds) - 1):
            s, e = bounds[i], bounds[i + 1]
            if e - s < 6:
                continue
            dx = xs[e - 1] - xs[s]
            sl = (cy[e - 1] - cy[s]) / dx if dx else float("nan")
            # 最小二乘更稳
            coef = np.polyfit(xs[s:e], cy[s:e], 1)
            print(f"    段 {i}: x {xs[s]:.0f}..{xs[e - 1]:.0f}  "
                  f"端点斜率 {sl:+.3f}  最小二乘斜率 {coef[0]:+.3f}  "
                  f"厚度 {th[s:e].mean():.2f}px")


if __name__ == "__main__":
    main()
