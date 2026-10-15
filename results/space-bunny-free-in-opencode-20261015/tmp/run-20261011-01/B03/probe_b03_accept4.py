#!/usr/bin/env python
"""B03 能力边界探针 · 阶段 A4：修正 r01 的嵌套顺序，并补最后几个语义。

r01 的教训：Positioned 必须是 Stack 的**直接**子节点，不能被 Transform 包住
（否则 400 renderBox.parentData must be StackParentData）。
正确顺序是 Stack > Positioned > Transform > Text/Container。

启动基准：总任务根 (suite_root)。用法：python tmp/run-20261011-01/B03/probe_b03_accept4.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TASK = "B03"
TEMP = "tmp/run-20261011-01/B03"
PROBE = f"{TEMP}/probe4"

ROT = "(0,-1,0,0,1,0,0,0,0,0,1,0,0,0,0,1)"   # 绕中心逆时针 90°
SHEAR = "(1,0.5774,0,0,0,1,0,0,0,0,1,0,0,0,0,1)"  # x 轴斜切


def wrap(body: str, w=420, h=300, bg="#101828") -> str:
    return (f'<Snapshot type="png">\n<Container width="{w}" height="{h}" color="{bg}">'
            f'<Stack fit="EXPAND">{body}</Stack></Container>\n</Snapshot>\n')


def pos(l, t, w, h, inner: str) -> str:
    return f'<Positioned left="{l}" top="{t}" width="{w}" height="{h}">{inner}</Positioned>'


def box(w, h, attrs: str) -> str:
    return f'<Container width="{w}" height="{h}"{attrs}/>'


CASES: list[tuple[str, str]] = [
    ("s01-rotated-text", wrap(
        pos(40, 30, 60, 240,
            f'<Transform matrix="{ROT}" alignment="CENTER">'
            '<Container width="60" height="240" alignment="CENTER_LEFT">'
            '<Text fontSize="30" color="#F5A524" fontFamily="Noto Serif CJK SC,Noto Sans CJK SC">'
            '竖排侧标签</Text></Container></Transform>') +
        pos(180, 40, 200, 80, f'<Transform matrix="{SHEAR}" alignment="CENTER">'
            + box(200, 80, ' color="#4C8DFF"') + "</Transform>"))),
    # 短轴 REPEAT：渐变轴只走盒子的一半 → 一盒内出现两条 tile
    ("s02-tile-short-axis", wrap(pos(30, 30, 360, 240, box(
        360, 240, ' gradientType="LINEAR" gradientColors="#4C8DFF,#0A0F1E"'
        ' gradientStops="0,1" gradientTileMode="REPEAT"'
        ' gradientBegin="CENTER_LEFT" gradientEnd="CENTER"')))),
    ("s03-tile-vertical", wrap(pos(30, 30, 360, 240, box(
        360, 240, ' gradientType="LINEAR" gradientColors="#F5A524,#0A0F1E"'
        ' gradientTileMode="REPEAT" gradientBegin="TOP_CENTER" gradientEnd="CENTER"')))),
    # ClipPath 裁一个渐变：路径既是形状也是渐变载体
    ("s04-path-gradient", wrap(pos(30, 30, 360, 240,
        '<ClipPath path="M0 240 L60 140 L130 190 L200 60 L260 150 L360 40 L360 240 Z">'
        '<Container width="360" height="240" gradientType="LINEAR"'
        ' gradientColors="#4C8DFF,#22C7A9" gradientBegin="TOP_LEFT"'
        ' gradientEnd="BOTTOM_RIGHT"/></ClipPath>'))),
    # ClipPath + ImageFiltered：路径边界自带柔化
    ("s05-path-blur", wrap(pos(60, 40, 300, 220,
        '<ImageFiltered sigmaX="10" sigmaY="10">'
        '<ClipPath path="M10 200 L70 80 L140 160 L220 40 L290 120 L290 210 L10 210 Z">'
        + box(300, 220, ' color="#F45B8C') + "</ClipPath></ImageFiltered>"))),
    # Text backgroundColor + 圆角文本底
    ("s06-text-bg", wrap(pos(30, 110, 360, 80,
        '<Text fontSize="30" color="#0A0F1E" backgroundColor="#22C7A9"'
        ' fontFamily="Inter,Noto Sans CJK SC">带底色的标签</Text>'))),
    # ClipOval 里放图片式渐变 + 外描边（仪表盘用）
    ("s07-gauge-ring", wrap(
        pos(30, 30, 360, 240, box(360, 240, ' color="#121B2E"')) +
        pos(90, 50, 240, 240, '<ClipOval><Container width="240" height="240" '
            'gradientType="SWEEP" gradientColors="#F45B8C,#F5A524,#22C7A9,#4C8DFF,#F45B8C"'
            '/></ClipOval>') +
        pos(130, 90, 160, 160, box(160, 160, ' color="#121B2E"')))),
    # 装饰类：Container 的 foregroundColor 叠一层
    ("s08-fg-color", wrap(pos(40, 50, 340, 200,
        '<DecoratedBox position="FOREGROUND" foregroundColor="#22C7A9"'
        ' foregroundGradientType="LINEAR" foregroundGradientColors="#22C7A9,#4C8DFF">'
        + box(340, 200, ' color="#18233B"') + "</DecoratedBox>"))),
]


def render(name: str, dsl_rel: str, out_rel: str, first: bool = True):
    cmd = [sys.executable, str(ROOT / "tmp/run-20261011-01/_suite/scripts/snapshot_render.py"),
           "--task", TASK, "--version", name, "--dsl", dsl_rel, "--out", out_rel,
           "--log", f"{TEMP}/requests.jsonl", "--responses-dir", f"{TEMP}/responses",
           "--extra", json.dumps({} if first else {"is_retry": True})]
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=str(ROOT))
    try:
        return json.loads((proc.stdout or "").strip().splitlines()[-1])
    except Exception:  # noqa: BLE001
        return {"ok": False, "error": f"stdout={(proc.stdout or '')!r} stderr={(proc.stderr or '')!r}"}


def main() -> None:
    (ROOT / PROBE).mkdir(parents=True, exist_ok=True)
    results = []
    for name, dsl in CASES:
        src = f"{PROBE}/{name}.snapshot"
        (ROOT / src).write_text(dsl, encoding="utf-8")
        r = None
        for a in range(1, 4):
            r = render(name, src, f"{PROBE}/{name}.png", a == 1)
            if r.get("ok") and (ROOT / PROBE / f"{name}.png").stat().st_size > 0:
                break
            time.sleep(2)
        size = (ROOT / PROBE / f"{name}.png").stat().st_size if (ROOT / PROBE / f"{name}.png").exists() else 0
        results.append({"probe": name, "ok": bool(r.get("ok")), "status": r.get("status"),
                        "bytes": size,
                        "error": (r.get("error_body") or "")[:240] if not r.get("ok") else None})
        print(json.dumps(results[-1], ensure_ascii=False))
    (ROOT / PROBE / "accept-results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n== {sum(1 for x in results if x['ok'])}/{len(results)} 受理 ==")


if __name__ == "__main__":
    main()