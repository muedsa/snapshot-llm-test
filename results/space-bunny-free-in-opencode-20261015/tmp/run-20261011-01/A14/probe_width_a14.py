#!/usr/bin/env python
"""A14 字宽模型标定探针：量出服务端真实的字面宽度，修正 est_em_str() 的估算系数。

启动基准：总任务根 (suite_root)。
动机：K05 首版把 "Color, Alpha & Contrast " 估成 663.7px（按 TITLE_FIT_W=676 判定放得下），
但 700px 的 Text 框装不下真实字面宽，右端被**服务端裁掉**，画面上整段 "Contrast " 消失。
本探针把每类字符以 100px 字号渲染在 1600px 宽的框里，用 PIL 量墨迹宽度，
反推出「CJK 系数」与「拉丁/数字/标点系数」，写进 est_em_str() 使用。

用法：python tmp/run-20261011-01/A14/probe_width_a14.py   （生成 drafts/probe-width.snapshot）
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/A14")
from build_a14 import F_HEAD, F_MIX_HEAD, F_SC  # noqa: E402

SIZE = 100.0
ROWS = [
    # (标签, 字符串, 字族)
    ("cjk-plain", "从颜色到可读性", F_SC),
    ("cjk-punct", "当所有信息都想成为标题：密集内容中的取舍与层级", F_SC),
    ("cjk-long", "把一次失败变成可复现记录——服务、字体、数据与视觉检查", F_SC),
    ("cjk-dash", "把一次失败变成可复现记录——服务", F_SC),
    ("cjk-comma", "服务、字体、数据与视觉检查", F_SC),
    ("latin-word", "Color, Alpha & Contrast ", F_HEAD),
    ("latin-cmp", "A < B & C > D", F_HEAD),
    ("latin-org", "Northstar Research ", F_HEAD),
    ("latin-site", "layerlight ", F_HEAD),
    ("digits", "2026.11.07 ", F_MIX_HEAD),
    ("digits2", "09:00 ", F_MIX_HEAD),
    ("mixed", "Color, Alpha & Contrast / ", F_MIX_HEAD),
]
BOX_W, ROW_H = 1600, 150


def build() -> tuple[str, list[tuple[int, int, str]]]:
    """返回 DSL 与每行在图上的 y 区间 [(y0, y1, label)]。"""
    H = ROW_H * len(ROWS) + 40
    parts = []
    spans = []
    for i, (label, text, fam) in enumerate(ROWS):
        y = 20 + i * ROW_H
        parts.append(f'<Positioned left="0" top="{y}" width="{BOX_W}" height="{ROW_H}">'
                     f'<Text fontSize="{int(SIZE)}" color="#FFFFFF" fontFamily="{fam}" '
                     f'text="{text}"/></Positioned>')
        spans.append((y, y + ROW_H, label))
    dsl = (f'<Snapshot type="png">\n<Container width="{BOX_W}" height="{H}" color="#000000">'
           f'<Stack fit="EXPAND">{"".join(parts)}</Stack></Container>\n</Snapshot>\n')
    return dsl, spans


def main() -> None:
    base = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    d = base / "tmp/run-20261011-01/A14/drafts"
    d.mkdir(parents=True, exist_ok=True)
    dsl, spans = build()
    (d / "probe-width.snapshot").write_text(dsl, encoding="utf-8")
    # 把行区间写出去，测量脚本直接读
    (d / "probe-width-rows.json").write_text(
        __import__("json").dumps([{"y0": a, "y1": b, "label": c} for a, b, c in spans],
                                 ensure_ascii=False, indent=2), encoding="utf-8")
    print("probe-width.snapshot bytes=", len(dsl.encode()))


if __name__ == "__main__":
    main()