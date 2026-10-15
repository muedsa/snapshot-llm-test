#!/usr/bin/env python
"""A13 探针：透明底 + 圆环(border) + 纯黑(alpha 检查) + 旋转圆角矩形。

启动基准：总任务根 (suite_root)。输出 tmp/run-20261011-01/A13/preview/probe-ring.png。
要验证三件事：
  1. `Container` 用 `border` + 透明 `color` 能否画出**中间镂空**的圆环（且只算 1 个构件）；
  2. 只画 #000000 的图形、画布透明时，alpha>0 的像素 RGB 是否全为 0；
  3. `Transform(rot)` 绕 CENTER 旋转圆角矩形是否正确。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import snapkit as sk  # noqa: E402

DRAFTS = "tmp/run-20261011-01/A13/drafts"
W, H = 760, 420


def ring(cx, cy, d, t, color):
    return (f'<Positioned left="{cx - d / 2}" top="{cy - d / 2}" width="{d}" height="{d}">'
            f'<Container width="{d}" height="{d}" color="#FFFFFF00" borderRadius="{d / 2}" '
            f'border="{t} SOLID {color}"/></Positioned>')


def sq_frame(x, y, w, h, t, r, color):
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
            f'<Container width="{w}" height="{h}" color="#FFFFFF00" borderRadius="{r}" '
            f'border="{t} SOLID {color}"/></Positioned>')


def rrect(cx, cy, w, h, deg, r, color):
    return (f'<Positioned left="{cx - w / 2}" top="{cy - h / 2}" width="{w}" height="{h}">'
            f'<Transform matrix="{sk.rot_matrix(deg)}" alignment="CENTER">'
            f'<Container width="{w}" height="{h}" color="{color}" borderRadius="{r}"/>'
            f'</Transform></Positioned>')


def circle(cx, cy, d, color):
    return (f'<Positioned left="{cx - d / 2}" top="{cy - d / 2}" width="{d}" height="{d}">'
            f'<ClipOval><Container width="{d}" height="{d}" color="{color}"/></ClipOval></Positioned>')


def main() -> None:
    P = []
    A = P.append
    A(f'<Positioned left="0" top="0" width="{W}" height="{H}">'
      f'<Container width="{W}" height="{H}" color="#FFFFFF"/></Positioned>')
    A(sk.text("A13 探针：透明圆环(border) / 旋转圆角矩形 / 纯黑", size=26, color="#0F172A",
              family=sk.F_HEAD, left=24, top=18, width=700, height=34))

    # 1) 白底上：圆环 + 圆环 + 方框
    A(ring(110, 130, 180, 34, "#1D4ED8"))
    A(sq_frame(216, 40, 180, 180, 34, 30, "#0F766E"))
    A(sk.text("1  border 圆环 / 圆角方框（应镂空）", size=16, color="#334155",
              family=sk.F_BODY, left=30, top=232, width=380, height=22))

    # 2) 白底上：旋转圆角矩形叠加
    A(rrect(500, 130, 150, 44, -30, 22, "#1D4ED8"))
    A(rrect(500, 130, 150, 44, 0, 22, "#0F766E"))
    A(rrect(500, 130, 150, 44, 30, 22, "#B45309"))
    A(sk.text("2  三层旋转圆角矩形（绕 CENTER）", size=16, color="#334155",
              family=sk.F_BODY, left=400, top=232, width=340, height=22))

    # 3) 透明底 + 纯黑图形（供解码后检查 alpha>0 处的 RGB 是否为 0）
    A(f'<Positioned left="600" top="40" width="130" height="130">'
      f'<Container width="130" height="130" color="#FFFFFF00" borderRadius="65" '
      f'border="26 SOLID #000000"/></Positioned>')
    A(circle(665, 230, 70, "#000000"))
    A(sk.text("3  纯黑（此格画布为透明底，空白区域 alpha=0）", size=15, color="#334155",
              family=sk.F_BODY, left=596, top=280, width=150, height=60))

    dsl = f'<Snapshot type="png">\n<Container width="{W}" height="{H}">'
    dsl += '<Stack fit="EXPAND">' + "".join(P) + '</Stack></Container>\n</Snapshot>\n'
    p = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")) / DRAFTS
    p.mkdir(parents=True, exist_ok=True)
    (p / "probe-ring.snapshot").write_text(dsl, encoding="utf-8")
    print("bytes:", len(dsl.encode()))


if __name__ == "__main__":
    main()