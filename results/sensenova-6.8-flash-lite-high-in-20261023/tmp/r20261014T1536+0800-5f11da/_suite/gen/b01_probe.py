"""B01 构件探针：写十件作品之前，用一次真实渲染确认新用基元的可用性。

要验证的东西（都是 A24 没用过的）：
  1. <Positioned><Opacity><Container/></Positioned> 的 Opacity 包裹
  2. <Container> 的 gradientType / gradientColors / gradientStops / gradientBegin / gradientEnd
  3. borderRadius = 半径 得到的圆形
  4. 扫描线多边形填充与折线描边是否真的画出形状
  5. 环形扇区（arc）与角度方向
  6. 片段数与渲染耗时在什么量级

这是探索性请求，requests.jsonl 里 case_id=null，不计入任何用例。
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
sys.path.insert(0, str(HERE.parent))
import b01_kit as K  # noqa: E402
import snap_client as C  # noqa: E402

TWO_PI = 2 * math.pi
UP = -math.pi / 2          # 12 点方向


def build() -> tuple:
    d = K.Doc(900, 620, "#0B1020")

    # 1. 线性渐变面板
    d.rect(24, 24, 400, 250, color="#141B33", radius=18,
           grad={"gradientType": "LINEAR", "gradientColors": "#1E2A55,#0B1020",
                 "gradientBegin": "TOP_LEFT", "gradientEnd": "BOTTOM_RIGHT"},
           owner="grad")
    # 2. 径向渐变
    d.rect(450, 24, 200, 200, color="#241033", radius=20,
           grad={"gradientType": "RADIAL", "gradientColors": "#7C3AED,#160A2A",
                 "gradientCenter": "CENTER", "gradientRadius": "0.72"},
           owner="radial")
    # 3. 扫描线多边形填充（不规则五边形）
    d.fill([(24, 300), (300, 280), (420, 360), (300, 500), (90, 470)],
           "#1D4ED8", step=1, owner="poly")
    # 4. 折线描边
    d.stroke([(24, 560), (140, 520), (250, 580), (360, 500), (470, 545)],
             "#38BDF8", width=4, step=1, owner="stroke")
    # 5. 环形扇区：刻度轨道 + 三段彩色弧（从 12 点顺时针）
    cx, cy = 620, 392
    d.arc(cx, cy, 104, 124, UP, UP + TWO_PI - 0.01, "#1F2A44", step=1, owner="track")
    d.arc(cx, cy, 104, 124, UP, UP + 1.0, "#34D399", step=1)
    d.arc(cx, cy, 104, 124, UP + 1.0, UP + 1.9, "#FBBF24", step=1)
    d.arc(cx, cy, 104, 124, UP + 1.9, UP + 2.6, "#60A5FA", step=1)
    # 6. Opacity 包裹
    d.rect(676, 24, 180, 90, color="#E879F9", radius=14, opacity=0.35,
           owner="opacity")
    # 7. 圆形（borderRadius = 半径）
    d.rect(676, 140, 120, 120, color="#22D3EE", radius=60, owner="circle")
    # 8. 实心圆盘（扫描线填充）
    d.circle(620, 300, 34, "#F59E0B", step=1, owner="disc")

    d.text(40, 44, "构件探针 B01", 26, "#F8FAFC", bold=True)
    d.text(40, 82, "gradient / opacity / fill / stroke / arc", 15, "#94A3B8")
    d.text_c(cx, cy - 12, "arc", 18, "#F8FAFC", bold=True)
    d.text_r(856, 40, "半径 60", 15, "#F8FAFC")
    d.text(40, 300, "五边形扫描线填充 step=1", 15, "#FFFFFF")
    d.text(40, 588, "折线描边 width=4", 15, "#FFFFFF")
    d.text_c(cx, cy + 52, "环形扇区三段", 15, "#94A3B8")
    d.text_c(cx, 268, "圆盘", 15, "#94A3B8")

    gates = K.dry_run(d, "probe", 15)
    K.check_palette("probe", [("#34D399", "#FBBF24"), ("#FBBF24", "#60A5FA"),
                              ("#34D399", "#60A5FA")], gates)
    return d, gates


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    doc, gates = build()
    K.assert_gates(gates, "probe")
    st = doc.stats()
    dsl = doc.build()
    print("parts=%d texts=%d shapes=%d  dsl=%d 字符"
          % (st["parts"], st["texts"], st["shapes"], len(dsl)))
    print("色彩可分性:", json.dumps(
        [g for g in gates if g["id"].endswith("-cbr")], ensure_ascii=False))

    res = C.render(K.TASK, dsl, "b01-kit-probe", kind="probe",
                   purpose="验证 B01 新基元：Opacity 包裹、线性/径向渐变、"
                           "borderRadius 圆形、扫描线填充、折线描边、环形扇区",
                   attempts=2, extra={"case_id": None,
                                      "note": "探索性请求，不计入任何用例"})
    rec = {"case_id": None, "label": "b01-kit-probe",
           "request_id": res["request_id"], "http_status": res["status"],
           "response_bytes": len(res["body"]) if res["body"] else 0,
           "attempts": res["attempt"], "elapsed_ms": res["meta"].get("elapsed_ms"),
           "started_at": res["meta"].get("started_at"),
           "ended_at": res["meta"].get("ended_at"),
           "parts": st["parts"], "shapes": st["shapes"],
           "dimensions": [doc.w, doc.h], "dsl_chars": len(dsl)}
    K.log_iteration(rec)

    if res["status"] == 200 and res["body"]:
        (K.TMP / "probe").mkdir(parents=True, exist_ok=True)
        (K.TMP / "probe" / "probe.png").write_bytes(res["body"])
        (K.TMP / "probe" / "probe.snapshot").write_bytes(dsl.encode("utf-8"))
        (K.TMP / "probe" / "probe-gates.json").write_text(
            json.dumps(gates, ensure_ascii=False, indent=1), encoding="utf-8")
        print("HTTP 200  %d B  %s ms  → tmp/%s/B01/probe/probe.png"
              % (len(res["body"]), res["meta"].get("elapsed_ms"), RUN_ID))
    else:
        print("HTTP %s  error=%s"
              % (res["status"], (res["meta"].get("error") or "")[:300]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
