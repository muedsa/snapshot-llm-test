#!/usr/bin/env python
"""B03 能力边界探针 · 阶段 A：属性/枚举「受理性」探测。

目的：把官方 parser-tags 文档里读到的属性逐条用最小 DSL 打一次服务，
      区分「文档写了但服务不认」与「服务确实支持」。只关心 200/400，不看图。

启动基准：总任务根 (suite_root)。用法：python tmp/run-20261011-01/B03/probe_b03_accept.py
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
PROBE = f"{TEMP}/probe"
(Path(ROOT) / PROBE).mkdir(parents=True, exist_ok=True)


def wrap(body: str, w=420, h=300, bg="#101828") -> str:
    return (f'<Snapshot type="png">\n<Container width="{w}" height="{h}" color="{bg}">'
            f'<Stack fit="EXPAND">{body}</Stack></Container>\n</Snapshot>\n')


# (名字, DSL 文本) —— 每个只测一件事
CASES: list[tuple[str, str]] = [
    ("p01-linear-gradient", wrap(
        '<Positioned left="30" top="30" width="360" height="240" gradientType="LINEAR" '
        'gradientColors="#FF6B35,#2E86C1,#0B132B" gradientStops="0,0.55,1" '
        'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT"/>')),
    ("p02-linear-rotation", wrap(
        '<Positioned left="30" top="30" width="360" height="240" gradientType="LINEAR" '
        'gradientColors="#FFFFFF00,#FF6B35FF" gradientRotation="1.5708"/>')),
    ("p03-radial-gradient", wrap(
        '<Positioned left="30" top="30" width="360" height="240" gradientType="RADIAL" '
        'gradientColors="#FFE08A,#E8453C60,#00000000" gradientCenter="(0.35,0.35)" '
        'gradientRadius="0.9"/>')),
    ("p04-radial-focal", wrap(
        '<Positioned left="30" top="30" width="360" height="240" gradientType="RADIAL" '
        'gradientColors="#FFFFFF,#5A7DFF" gradientFocal="(0.3,0.25)" '
        'gradientFocalRadius="0.12" gradientCenter="(0.5,0.5)" gradientRadius="0.7"/>')),
    ("p05-sweep-gradient", wrap(
        '<Positioned left="30" top="30" width="360" height="240" gradientType="SWEEP" '
        'gradientColors="#4C8DFF,#22C7A9,#F5A524,#F45B8C,#4C8DFF" '
        'gradientStartAngle="0" gradientEndAngle="6.2832"/>')),
    ("p06-tilemode-repeat", wrap(
        '<Positioned left="30" top="30" width="360" height="240" gradientType="LINEAR" '
        'gradientColors="#FFFFFF,#FFFFFF" gradientTileMode="REPEAT" '
        'gradientRotation="0.5"/>')),
    ("p07-tilemode-mirror", wrap(
        '<Positioned left="30" top="30" width="360" height="240" gradientType="LINEAR" '
        'gradientColors="#F5A524,#0A0F1E" gradientTileMode="MIRROR" '
        'gradientRotation="0.5"/>')),
    ("p08-clippath-arc", wrap(
        '<Positioned left="30" top="30" width="360" height="240">'
        '<ClipPath path="M20 60 L200 60 A60 60 0 0 1 200 180 L20 180 Z" '
        'viewBox="0 0 240 240" fit="CONTAIN"><Container color="#E8453C"/></ClipPath>'
        '</Positioned>')),
    ("p09-clippath-evenodd", wrap(
        '<Positioned left="30" top="30" width="360" height="240">'
        '<ClipPath path="M10 10 H230 V230 H10 Z M60 60 H180 V180 H60 Z" '
        'viewBox="0 0 240 240" fit="FILL" fillRule="EVEN_ODD">'
        '<Container color="#22C7A9"/></ClipPath></Positioned>')),
    ("p10-clippath-cubic-fill", wrap(
        '<Positioned left="30" top="30" width="360" height="240">'
        '<ClipPath path="M0 200 L40 120 C90 40 150 190 240 60 L240 240 L0 240 Z" '
        'viewBox="0 0 240 240" fit="NONE"><Container color="#4C8DFF"/></ClipPath>'
        '</Positioned>')),
    ("p11-imagefiltered-blur", wrap(
        '<Positioned left="30" top="30" width="360" height="240">'
        '<ImageFiltered sigmaX="18" sigmaY="18" tileMode="CLAMP">'
        '<Container width="360" height="240">'
        '<Positioned left="40" top="60" width="80" height="80" color="#F5A524"/>'
        '<Positioned left="180" top="120" width="120" height="120" color="#F45B8C"/>'
        '</Container></ImageFiltered></Positioned>')),
    ("p12-backdropfilter", wrap(
        '<Positioned left="30" top="30" width="360" height="240" color="#1B2A4A">'
        '<Positioned left="0" top="0" width="360" height="120">'
        '<Container width="360" height="120" gradientType="LINEAR" '
        'gradientColors="#4C8DFF,#22C7A9"/></Positioned></Positioned>'
        '<Positioned left="40" top="60" width="280" height="140">'
        '<ClipRRect borderRadius="20" clipBehavior="ANTI_ALIAS">'
        '<BackdropFilter sigmaX="14" sigmaY="14">'
        '<Container width="280" height="140" color="#FFFFFF22"/></BackdropFilter>'
        '</ClipRRect></Positioned></Positioned>')),
    ("p13-colorfiltered-multiply", wrap(
        '<Positioned left="30" top="30" width="360" height="240">'
        '<ColorFiltered color="#E8453C" blendMode="MULTIPLY">'
        '<Container width="360" height="240" color="#F2C14E"/></ColorFiltered>'
        '</Positioned>')),
    ("p14-colorfiltered-difference", wrap(
        '<Positioned left="30" top="30" width="360" height="240">'
        '<ColorFiltered color="#4C8DFF" blendMode="DIFFERENCE">'
        '<Container width="360" height="240" color="#22C7A9"/></ColorFiltered>'
        '</Positioned>')),
    ("p15-colorfiltered-overlay", wrap(
        '<Positioned left="30" top="30" width="360" height="240">'
        '<ColorFiltered color="#9B6BFF" blendMode="OVERLAY">'
        '<Container width="360" height="240" color="#F5A524"/></ColorFiltered>'
        '</Positioned>')),
    ("p16-text-stroke", wrap(
        '<Positioned left="30" top="90" width="360" height="120">'
        '<Text fontSize="76" color="#00000000" foregroundColor="#F2F6FC" '
        'foregroundMode="STROKE" foregroundStrokeWidth="2.5" '
        'fontFamily="Inter Black,Noto Sans CJK SC">STROKE</Text></Positioned>')),
    ("p17-text-decoration", wrap(
        '<Positioned left="30" top="30" width="360" height="240">'
        '<Text fontSize="40" color="#F2F6FC" decoration="LINE_THROUGH" '
        'decorationColor="#F45B8C" decorationThickness="3" '
        'fontFamily="Inter,Noto Sans CJK SC">¥1280 LINE_THROUGH</Text></Positioned>')),
    ("p18-text-features-tnum", wrap(
        '<Positioned left="30" top="90" width="360" height="120">'
        '<Text fontSize="48" color="#F2F6FC" fontFeatures="tnum=2" '
        'fontFamily="Noto Sans Mono CJK SC,Inter">1,234.56 元</Text></Positioned>')),
    ("p19-text-shadow", wrap(
        '<Positioned left="30" top="90" width="360" height="120">'
        '<Text fontSize="56" color="#F5A524" textShadow="6 8 4 #000000AA,-2 -2 0 #22C7A9" '
        'fontFamily="Inter Extra Bold,Noto Sans CJK SC">SHADOW</Text></Positioned>')),
    ("p20-widgetspan-inline", wrap(
        '<Positioned left="30" top="80" width="360" height="140">'
        '<Text fontSize="34" color="#F2F6FC" fontFamily="Inter,Noto Sans CJK SC">'
        '<WidgetSpan alignment="MIDDLE">'
        '<Container width="46" height="26" color="#22C7A9" borderRadius="8"/></WidgetSpan>'
        '<Raw> _INLINE_</Raw><WidgetSpan alignment="MIDDLE">'
        '<Container width="120" height="26" color="#4C8DFF" borderRadius="8"/></WidgetSpan>'
        '</Text></Positioned>')),
    ("p21-transform-affine-shear", wrap(
        '<Positioned left="200" top="150" width="160" height="90">'
        '<Transform matrix="(1,0.5774,0,0,0,1,0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">'
        '<Container width="160" height="90" color="#4C8DFF"/></Transform></Positioned>')),
    ("p22-transparent-bg", '<Snapshot type="png" background="transparent">\n'
                           '<Container width="420" height="300">'
                           '<Stack fit="EXPAND">'
                           '<Positioned left="60" top="60" width="300" height="180" color="#F45B8C"/>'
                           '</Stack></Container>\n</Snapshot>\n'),
    ("p23-clipoval", wrap(
        '<Positioned left="60" top="30" width="240" height="240">'
        '<ClipOval clipBehavior="ANTI_ALIAS">'
        '<Container width="240" height="240" gradientType="SWEEP" '
        'gradientColors="#4C8DFF,#22C7A9,#F5A524,#4C8DFF"/></ClipOval></Positioned>')),
    ("p24-multishadow", wrap(
        '<Positioned left="40" top="60" width="340" height="180" color="#18233B" borderRadius="24" '
        'boxShadow="12 18 24 0 #000000AA, -8 -8 18 0 #4C8DFF66, 0 2 4 0 #00000088"/>')),
    ("p25-textalign-end", wrap(
        '<Positioned left="40" top="120" width="340" height="60">'
        '<Text textAlign="END" fontSize="40" color="#F2F6FC" '
        'fontFamily="Noto Sans Mono CJK SC,Inter">123,456.78</Text></Positioned>')),
    ("p26-justified", wrap(
        '<Positioned left="30" top="40" width="360" height="220">'
        '<Text textAlign="JUSTIFY" softWrap="true" fontSize="22" color="#F2F6FC" height="1.6" '
        'fontFamily="Noto Serif CJK SC,Noto Sans CJK SC">这是一段用来检验两端对齐是否真的生效的长文本，'
        '需要足够长才能让对齐在视觉上被看出来，否则只有一行看不出差别。</Text></Positioned>')),
    ("p27-raw-multiline", wrap(
        '<Positioned left="30" top="80" width="360" height="160">'
        '<Text fontSize="26" color="#F2F6FC" fontFamily="Noto Sans Mono CJK SC">'
        '<Raw>  ' + chr(10) + '  行二' + chr(10) + '  行三</Raw></Text></Positioned>')),
    ("p28-gradient-decal", wrap(
        '<Positioned left="30" top="30" width="360" height="240" gradientType="LINEAR" '
        'gradientColors="#4C8DFF,#0A0F1E" gradientTileMode="DECAL" gradientRotation="0.6"/>')),
    ("p29-font-serif", wrap(
        '<Positioned left="30" top="90" width="360" height="120">'
        '<Text fontSize="52" color="#F2F6FC" fontStyle="ITALIC" letterSpacing="6" '
        'fontFamily="Noto Serif CJK SC,Noto Serif">Serif 衬线 12</Text></Positioned>')),
    ("p30-indexedstack", wrap(
        '<Positioned left="30" top="30" width="360" height="240" color="#18233B">'
        '<Stack fit="EXPAND"><Positioned left="0" top="0" width="360" height="240" color="#F45B8C"/>'
        '</Stack></Positioned>'
        '<Positioned left="60" top="60" width="300" height="180">'
        '<IndexedStack index="0" fit="EXPAND"><Container width="300" height="180" color="#22C7A9"/>'
        '</IndexedStack></Positioned>')),
]


def render(name: str, dsl_rel: str, out_rel: str, attempt_ok: bool = True):
    """直接调用 snapshot_render.py，把 PNG 落到临时目录（探针不进输出目录）。"""
    cmd = [sys.executable, str(ROOT / "tmp/run-20261011-01/_suite/scripts/snapshot_render.py"),
           "--task", TASK, "--version", name, "--dsl", dsl_rel, "--out", out_rel,
           "--log", f"{TEMP}/requests.jsonl", "--responses-dir", f"{TEMP}/responses",
           "--extra", json.dumps({} if attempt_ok else {"is_retry": True})]
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=str(ROOT))
    try:
        return json.loads((proc.stdout or "").strip().splitlines()[-1])
    except Exception:  # noqa: BLE001
        return {"ok": False, "error": f"stdout={(proc.stdout or '')!r} stderr={(proc.stderr or '')!r}"}


def main() -> None:
    results = []
    for name, dsl in CASES:
        src = f"{PROBE}/{name}.snapshot"
        p = ROOT / src
        p.write_text(dsl, encoding="utf-8")
        r = None
        for a in range(1, 4):
            r = render(name, src, f"{PROBE}/{name}.png", a == 1)
            if r.get("ok") and (ROOT / PROBE / f"{name}.png").stat().st_size > 0:
                break
            time.sleep(2)
        size = (ROOT / PROBE / f"{name}.png").stat().st_size if (ROOT / PROBE / f"{name}.png").exists() else 0
        results.append({"probe": name, "ok": bool(r.get("ok")), "status": r.get("status"),
                        "bytes": size,
                        "error": (r.get("error_body") or "")[:220] if not r.get("ok") else None})
        print(json.dumps(results[-1], ensure_ascii=False))
    (ROOT / PROBE / "accept-results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = sum(1 for x in results if x["ok"])
    print(f"\n== {ok}/{len(results)} 受理 ==")


if __name__ == "__main__":
    main()