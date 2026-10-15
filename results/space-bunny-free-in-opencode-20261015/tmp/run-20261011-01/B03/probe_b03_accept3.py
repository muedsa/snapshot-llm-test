#!/usr/bin/env python
"""B03 能力边界探针 · 阶段 A3：确认作品设计要用到的最后几个语义。

覆盖：旋转文字、嵌套 Text 富文本、REPEAT 条纹、ImageFiltered 作用于文字（景深）、
     大画布、ClipPath 本地坐标、前景装饰发光、WidgetSpan 混排数值。

启动基准：总任务根 (suite_root)。用法：python tmp/run-20261011-01/B03/probe_b03_accept3.py
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
PROBE = f"{TEMP}/probe3"


def wrap(body: str, w=420, h=300, bg="#101828") -> str:
    return (f'<Snapshot type="png">\n<Container width="{w}" height="{h}" color="{bg}">'
            f'<Stack fit="EXPAND">{body}</Stack></Container>\n</Snapshot>\n')


def pos(l, t, w, h, inner: str) -> str:
    return f'<Positioned left="{l}" top="{t}" width="{w}" height="{h}">{inner}</Positioned>'


def box(w, h, attrs: str) -> str:
    return f'<Container width="{w}" height="{h}"{attrs}/>'


CASES: list[tuple[str, str]] = [
    # 旋转的竖排中文标签：Transform 套在 Positioned 外层
    ("r01-rotated-text", wrap(pos(60, 30, 70, 240,
        '<Transform matrix="(0,-1,0,0,1,0,0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">'
        '<Positioned left="0" top="0" width="70" height="240">'
        '<Text fontSize="34" color="#F5A524" fontFamily="Noto Serif CJK SC,Noto Sans CJK SC">'
        '垂直标签测试</Text></Positioned></Transform>'))),
    # 嵌套 Text：同一行里混字号/混颜色/混字重
    ("r02-nested-text", wrap(pos(20, 100, 380, 100,
        '<Text fontSize="40" color="#9AA9BF" fontFamily="Inter,Noto Sans CJK SC">'
        'A1 小区 · 交付 <Text fontSize="64" color="#F5A524" fontFamily="Inter Black,Noto Sans CJK SC">'
        '10-28</Text> <Text fontSize="40" color="#22C7A9" fontFamily="Inter,Noto Sans CJK SC">'
        '· 已封顶</Text></Text>'))),
    # REPEAT 干净条纹：两段平台色 + 极窄过渡
    ("r03-stripes-repeat", wrap(pos(30, 30, 360, 240, box(
        360, 240, ' gradientType="LINEAR" gradientColors="#4C8DFF,#4C8DFF,#0A0F1E,#0A0F1E"'
        ' gradientStops="0,0.45,0.55,1" gradientTileMode="REPEAT"')))),
    # ImageFiltered 作用于文字 → 景深/失焦
    ("r04-blur-text", wrap(pos(30, 30, 360, 240,
        '<Stack fit="EXPAND">'
        '<Positioned left="0" top="0" width="360" height="240">'
        '<ImageFiltered sigmaX="9" sigmaY="9">'
        '<Text fontSize="60" color="#22C7A9" fontFamily="Inter Black,Noto Sans CJK SC">'
        'BLURRED 背景层</Text></ImageFiltered></Positioned>'
        '<Positioned left="0" top="140" width="360" height="100">'
        '<Text fontSize="44" color="#F2F6FC" fontFamily="Inter,Noto Sans CJK SC">'
        '前景层保持锐利</Text></Positioned>'
        '</Stack>'))),
    # 大画布
    ("r05-large-canvas", '<Snapshot type="png">\n<Container width="2400" height="1350" color="#0A0F1E">'
                         '<Stack fit="EXPAND">'
                         + pos(120, 120, 2160, 1110, box(
                             2160, 1110, ' gradientType="LINEAR" gradientColors="#12203A,#0A0F1E"'))
                         + '</Stack></Container>\n</Snapshot>\n'),
    # ClipPath 不写 viewBox，用本地坐标
    ("r06-clippath-local", wrap(pos(40, 40, 340, 220,
        '<ClipPath path="M0 180 L60 60 L140 130 L220 40 L340 150 L340 220 L0 220 Z">'
        '<Container color="#22C7A9"/></ClipPath>'))),
    # 前景装饰做辉光：foregroundBoxShadow
    ("r07-fg-glow", wrap(pos(80, 90, 260, 120,
        '<DecoratedBox foregroundBoxShadow="0 0 40 10 #4C8DFF99" foregroundBorderRadius="16">'
        + box(260, 120, ' color="#18233B"') + "</DecoratedBox>"))),
    # WidgetSpan 把「数字 + 单位」做成一组，混在段落里
    ("r08-widgetspan-mixed", wrap(pos(20, 60, 380, 180,
        '<Text fontSize="26" color="#F2F6FC" fontFamily="Inter,Noto Sans CJK SC">'
        '平均等待 <WidgetSpan alignment="BASELINE"><Text fontSize="44" color="#F45B8C" '
        'fontFamily="Inter Black,Noto Sans CJK SC">38</Text></WidgetSpan> 分钟，'
        '中位数 <WidgetSpan alignment="BASELINE"><Text fontSize="44" color="#F5A524" '
        'fontFamily="Inter Black,Noto Sans CJK SC">21</Text></WidgetSpan> 分钟。</Text>'))),
    # 描边+填充同在（STROKE_AND_FILL）
    ("r09-stroke-and-fill", wrap(pos(20, 90, 380, 120,
        '<Text fontSize="72" color="#F5A524" foregroundColor="#0A0F1E"'
        ' foregroundMode="STROKE_AND_FILL" foregroundStrokeWidth="3"'
        ' fontFamily="Inter Extra Bold,Noto Sans CJK SC">BOTH</Text>'))),
    # Sweep 渐变当作「角度刻度」：只有两色 + tileMode MIRROR
    ("r10-sweep-mirror", wrap(pos(30, 30, 360, 240, box(
        360, 240, ' gradientType="SWEEP" gradientColors="#F5A524,#0A0F1E"'
        ' gradientTileMode="MIRROR" gradientStartAngle="0" gradientEndAngle="6.2832"')))),
    # BackdropFilter 大 sigma + 底部渐变
    ("r11-backdrop-large", wrap(
        pos(30, 30, 360, 240, box(360, 240, ' gradientType="LINEAR"'
            ' gradientColors="#4C8DFF,#22C7A9,#F5A524,#F45B8C"')) +
        pos(50, 90, 320, 120,
            '<ClipRRect borderRadius="18"><BackdropFilter sigmaX="24" sigmaY="24">'
            + box(320, 120, ' color="#FFFFFF1A"') + "</BackdropFilter></ClipRRect>"))),
    # ClipPath 多轮廓 NON_ZERO 反向镂空
    ("r12-clippath-nonzero-hole", wrap(pos(30, 30, 360, 240,
        '<ClipPath path="M10 10 H230 V230 H10 Z M70 70 V150 H170 V70 Z"'
        ' viewBox="0 0 240 240" fit="FILL" fillRule="NON_ZERO">'
        + box(360, 240, ' color="#9B6BFF"') + "</ClipPath>"))),
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