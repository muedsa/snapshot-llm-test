"""核验图例尾注里的两组关系（不提交服务，纯代数）：

  T07 = mirror_H ∘ rotate90   T08 = rotate90 ∘ mirror_H
  T11 = rotate30              T12 = mirror_V ∘ rotate30

结论用于 snapshot-usage.md 与图例尾注，避免图上写错关系。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import a09_geom as G        # noqa: E402


def mul(a, b):
    """按 (a,e,0,0,b,f,0,0,tx,ty,...) 列主序 2×3 仿射乘法：先 b 后 a。"""
    return (
        a[0] * b[0] + a[1] * b[2],
        a[0] * b[1] + a[1] * b[3],
        a[2] * b[0] + a[3] * b[2],
        a[2] * b[1] + a[3] * b[3],
        a[0] * b[4] + a[1] * b[5] + a[4],
        a[2] * b[4] + a[3] * b[5] + a[5],
    )


def det(m):
    return m[0] * m[3] - m[1] * m[2]


def r6(m):
    return [round(v, 6) for v in m]


def main() -> None:
    os.environ.setdefault("SNAPSHOT_RUN_ID", "r20261014T1536+0800-5f11da")
    m7 = G.compose([{"op": "mirror_horizontal"}, {"op": "rotate", "deg": 90}])
    m8 = G.compose([{"op": "rotate", "deg": 90}, {"op": "mirror_horizontal"}])
    m11 = G.compose([{"op": "rotate", "deg": 30}])
    m12 = G.compose([{"op": "mirror_vertical"}, {"op": "rotate", "deg": 30}])
    r180 = G.compose([{"op": "rotate", "deg": 180}])

    c78 = mul(m7, m8)
    print("T07      =", r6(m7))
    print("T08      =", r6(m8))
    print("T07 o T08=", r6(c78))
    print("rotate180=", r6(r180))
    same = all(abs(a - b) < 1e-9 for a, b in zip(c78, r180))
    print("T07 o T08 == rotate180 :", same,
          "  → T07 与 T08 相差一个 180° 旋转（不是镜像）")
    print("det T07 / T08 =", r6([det(m7), det(m8)]), "（均为 −1，二者都是反射）")
    print("det T11 =", round(det(m11), 6), "det T12 =", round(det(m12), 6),
          "（+1 旋转 / −1 反射）")
    # 反例：若声称「互为 y=x 镜像」，T07∘T08 应为单位矩阵
    ident = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    print("T07 o T08 == identity :", all(abs(a - b) < 1e-9 for a, b in zip(c78, ident)),
          "（若互为同一反射则合成恒等；实测否 → 该说法错误）")
    assert same and not all(abs(a - b) < 1e-9 for a, b in zip(c78, ident))
    assert round(det(m11), 6) == 1.0 and round(det(m12), 6) == -1.0
    print("\n代数核验通过")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
