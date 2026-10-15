#!/usr/bin/env python
"""B03 能力边界探针 · 阶段 A2：修正「Positioned 必须有子节点」后的补测。

阶段 A 的结论：任何**自闭合的 Positioned** 都会 400
（"ProxyWidget has no widget, can not create render box"）——
渐变/阴影都属于 Container/Border/DecoratedBox，不属于 Positioned。
本轮把渐变、阴影、透明底、IndexedStack 全部改为「Positioned 包一个带样式的子节点」，
并补测一批还没打过的属性。

启动基准：总任务根 (suite_root)。用法：python tmp/run-20261011-01/B03/probe_b03_accept2.py
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
PROBE = f"{TEMP}/probe2"


def wrap(body: str, w=420, h=300, bg="#101828") -> str:
    return (f'<Snapshot type="png">\n<Container width="{w}" height="{h}" color="{bg}">'
            f'<Stack fit="EXPAND">{body}</Stack></Container>\n</Snapshot>\n')


def pos(l, t, w, h, inner: str) -> str:
    return f'<Positioned left="{l}" top="{t}" width="{w}" height="{h}">{inner}</Positioned>'


def box(w, h, attrs: str) -> str:
    return f'<Container width="{w}" height="{h}"{attrs}/>'


CASES: list[tuple[str, str]] = [
    ("q01-linear-gradient", wrap(pos(30, 30, 360, 240, box(
        360, 240, ' gradientType="LINEAR" gradientColors="#FF6B35,#2E86C1,#0B132B"'
        ' gradientStops="0,0.55,1" gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT"')))),
    ("q02-linear-rotation", wrap(pos(30, 30, 360, 240, box(
        360, 240, ' gradientType="LINEAR" gradientColors="#FFFFFF00,#FF6B35FF"'
        ' gradientRotation="1.5708"')))),
    ("q03-radial", wrap(pos(30, 30, 360, 240, box(
        360, 240, ' gradientType="RADIAL" gradientColors="#FFE08A,#E8453C80,#0B132B00"'
        ' gradientCenter="(0.35,0.35)" gradientRadius="0.9"')))),
    ("q04-radial-focal", wrap(pos(30, 30, 360, 240, box(
        360, 240, ' gradientType="RADIAL" gradientColors="#FFFFFF,#5A7DFF"'
        ' gradientFocal="(0.3,0.25)" gradientFocalRadius="0.12"'
        ' gradientCenter="(0.5,0.5)" gradientRadius="0.7"')))),
    ("q05-sweep", wrap(pos(30, 30, 360, 240, box(
        360, 240, ' gradientType="SWEEP" gradientColors="#4C8DFF,#22C7A9,#F5A524,#F45B8C,#4C8DFF"'
        ' gradientStartAngle="0" gradientEndAngle="6.2832"')))),
    ("q06-tile-repeat", wrap(pos(30, 30, 360, 240, box(
        360, 240, ' gradientType="LINEAR" gradientColors="#4C8DFF,#0A0F1E"'
        ' gradientTileMode="REPEAT" gradientRotation="0.5"')))),
    ("q07-tile-mirror", wrap(pos(30, 30, 360, 240, box(
        360, 240, ' gradientType="LINEAR" gradientColors="#F5A524,#0A0F1E"'
        ' gradientTileMode="MIRROR" gradientRotation="0.5"')))),
    ("q08-tile-decal", wrap(pos(30, 30, 360, 240, box(
        360, 240, ' gradientType="LINEAR" gradientColors="#4C8DFF,#0A0F1E"'
        ' gradientTileMode="DECAL" gradientRotation="0.6"')))),
    ("q09-multishadow", wrap(pos(40, 60, 340, 180, box(
        340, 180, ' color="#18233B" borderRadius="24"'
        ' boxShadow="12 18 24 0 #000000AA, -8 -8 18 0 #4C8DFF66, 0 2 4 0 #00000088"')))),
    ("q10-transparent-bg", '<Snapshot type="png" background="transparent">\n'
                           '<Container width="420" height="300"><Stack fit="EXPAND">'
                           + pos(60, 60, 300, 180, box(300, 180, ' color="#F45B8C"'))
                           + '</Stack></Container>\n</Snapshot>\n'),
    ("q11-imagefiltered-blur", wrap(pos(30, 30, 360, 240,
        '<ImageFiltered sigmaX="18" sigmaY="18" tileMode="CLAMP">'
        '<Stack fit="EXPAND">' + box(90, 90, ' color="#F5A524"').join(("", "")) + "</Stack>"
        "</ImageFiltered>"))),
    ("q12-indexedstack", wrap(pos(60, 30, 300, 240,
        '<IndexedStack index="0" fit="EXPAND">' + box(300, 240, ' color="#22C7A9"')
        + box(300, 240, ' color="#F45B8C"') + "</IndexedStack>"))),
    ("q13-blend-softlight", wrap(pos(30, 30, 360, 240,
        '<ColorFiltered color="#9B6BFF" blendMode="SOFT_LIGHT">'
        + box(360, 240, ' color="#F5A524"') + "</ColorFiltered>"))),
    ("q14-blend-screen", wrap(pos(30, 30, 360, 240,
        '<ColorFiltered color="#3A2E6E" blendMode="SCREEN">'
        + box(360, 240, ' color="#F5A524"') + "</ColorFiltered>"))),
    ("q15-blend-hardlight", wrap(pos(30, 30, 360, 240,
        '<ColorFiltered color="#9B6BFF" blendMode="HARD_LIGHT">'
        + box(360, 240, ' color="#5A7DFF"') + "</ColorFiltered>"))),
    ("q16-blend-modulate", wrap(pos(30, 30, 360, 240,
        '<ColorFiltered color="#9B6BFF" blendMode="MODULATE">'
        + box(360, 240, ' color="#F5A524"') + "</ColorFiltered>"))),
    ("q17-blend-luminosity", wrap(pos(30, 30, 360, 240,
        '<ColorFiltered color="#FFD166" blendMode="LUMINOSITY">'
        + box(360, 240, ' gradientType="LINEAR" gradientColors="#4C8DFF,#F45B8C"')
        + "</ColorFiltered>"))),
    ("q18-blend-dodge", wrap(pos(30, 30, 360, 240,
        '<ColorFiltered color="#FFD166" blendMode="COLOR_DODGE">'
        + box(360, 240, ' color="#4C8DFF"') + "</ColorFiltered>"))),
    ("q19-clippath-fill", wrap(pos(30, 30, 360, 240,
        '<ClipPath path="M0 200 L40 120 C90 40 150 190 240 60 L240 240 L0 240 Z"'
        ' viewBox="0 0 240 240" fit="FILL"><Container color="#4C8DFF"/></ClipPath>'))),
    ("q20-aspect-fraction", wrap(
        '<Positioned left="30" top="30" width="360" height="240">'
        '<Stack fit="EXPAND"><AspectRatio aspectRatio="1.6">'
        + box(200, 125, ' color="#22C7A9"') + "</AspectRatio>"
        '<Positioned left="20" top="150" width="320" height="70">'
        '<FractionallySizedBox widthFactor="0.5" heightFactor="0.5">'
        + box(100, 100, ' color="#F5A524"') + "</FractionallySizedBox></Positioned>"
        "</Stack></Positioned>")),
    ("q21-shape-circle", wrap(pos(30, 30, 360, 240, box(
        360, 240, ' shape="CIRCLE" gradientType="RADIAL"'
        ' gradientColors="#F5A524,#F45B8C" gradientRadius="0.6"')))),
    ("q22-decoratedbox-fg", wrap(pos(30, 30, 360, 240,
        '<DecoratedBox position="FOREGROUND" border="4 SOLID #22C7A9" borderRadius="20">'
        + box(360, 240, ' color="#18233B"') + "</DecoratedBox>"))),
    ("q23-clippath-shrink", wrap(pos(30, 30, 360, 240,
        '<ClipPath path="M20 20 H220 V220 H20 Z" viewBox="0 0 240 240" fit="CONTAIN">'
        + box(360, 240, ' gradientType="SWEEP" gradientColors="#4C8DFF,#22C7A9,#4C8DFF"')
        + "</ClipPath>"))),
    ("q24-opacity-stack", wrap(
        pos(30, 30, 360, 240, box(360, 240, ' color="#4C8DFF"')) +
        pos(80, 80, 200, 140, '<Opacity opacity="0.45">' + box(200, 140, ' color="#F5A524"')
            + "</Opacity>"))),
    ("q25-unconstrained", wrap(
        pos(30, 30, 360, 240, '<UnconstrainedBox alignment="TOP_LEFT">'
            '<Row mainAxisSize="MIN"><Expanded flex="1">'
            + box(120, 120, ' color="#22C7A9"') + "</Expanded>"
            + box(200, 200, ' color="#F45B8C"') + "</Row></UnconstrainedBox>"))),
    ("q26-text-maxlines", wrap(pos(30, 30, 360, 240,
        '<Text fontSize="28" color="#F2F6FC" maxLines="3" overflow="ELLIPSIS"'
        ' fontFamily="Noto Serif CJK SC">这是一段很长的说明文字，用来检验 maxLines 与 ELLIPSIS '
        '是否真的生效，文字应该只显示三行并且最后一行末尾出现省略号。</Text>'))),
    ("q27-baseline-row", wrap(
        pos(30, 30, 360, 240, '<Row crossAxisAlignment="BASELINE" mainAxisSize="MIN">'
            '<Text fontSize="72" color="#F5A524" fontFamily="Inter,Noto Sans CJK SC">32</Text>'
            '<Text fontSize="22" color="#9AA9BF" fontFamily="Inter,Noto Sans CJK SC">'
            '次/场</Text></Row>'))),
    ("q28-boxshadow-elev", wrap(pos(40, 60, 340, 180, box(
        340, 180, ' color="#18233B" borderRadius="24" boxShadow="ELEVATION_12"')))),
    ("q29-wordspacing", wrap(pos(30, 30, 360, 240,
        '<Text fontSize="30" color="#F2F6FC" letterSpacing="8" wordSpacing="20"'
        ' fontFamily="Inter,Noto Sans CJK SC">SPACE 间距 测试</Text>'))),
    ("q30-vertical-rotate", wrap(pos(160, 30, 100, 240,
        '<Transform matrix="(0,-1,0,0,1,0,0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">'
        + box(220, 40, ' color="#4C8DFF"') + "</Transform>"))),
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