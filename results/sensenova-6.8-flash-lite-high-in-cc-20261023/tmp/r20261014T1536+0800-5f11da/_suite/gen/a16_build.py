"""A16 生成器：由 source.csv 计算 corrected-data.json 并生成 corrected-report DSL。

设计要点（对应 findings.json 的修正项）：
  * 柱图共同零起点：轴 0..200 万元，px_per_wan = 1.4，柱底全部落在 0 基线上；
  * 图例与柱体一致：蓝 = 收入、橙 = 成本；
  * 柱高严格按值等比（同一 px_per_wan），不再靠标签兜底；
  * 标题与重点季度由数据论证：Q4 利润 54 万元、利润率 30.0% 均为四季最高；
  * 利润明细全部四季，附利润率；
  * 正文 >=22px、标注 >=18px；无外部图像；提示框文字色改为深墨以保证对比度。

运行方式：
    python -I tmp/<run_id>/_suite/gen/a16_build.py            # 只生成 DSL 与 JSON
    python -I tmp/<run_id>/_suite/gen/a16_build.py --render   # 生成并请求服务渲染
"""
from __future__ import annotations

import csv
import json
import os
import pathlib
import sys
import time
import uuid

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TASK = SUITE_ROOT / "tasks" / "A16-visual-data-forensics"
OUT_DIR = SUITE_ROOT / "outputs" / RUN_ID / "A16"
TMP_DIR = SUITE_ROOT / "tmp" / RUN_ID / "A16"

# ---- 布局常量（原点左上，像素单位） -----------------------------------------
W, H = 1280, 900
MARGIN = 56
CONTENT_W = W - 2 * MARGIN          # 1168

CANVAS_BG = "#F7F6F0"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#E2E8F1"
INK = "#18283F"                     # 主文字
INK_2 = "#5B6B80"                   # 次要文字（画布上 5.03）
INK_3 = "#63748F"                   # 标注（仅用于白底卡片，4.75）
FOOTER_INK = "#5B6B80"              # 画布上的标注：#63748F 只有 4.38，不达标
GRID = "#E7EDF5"
BASELINE = "#94A3B8"
REVENUE = "#245CE4"                 # 蓝 = 收入
COST = "#C96F1E"                    # 橙 = 成本（对比白底 3.64，高于 WCAG 3.0）
PROFIT_UP = "#168267"
CALLOUT_BG = "#FFF1D9"
CALLOUT_BORDER = "#E8A33D"
CALLOUT_INK = "#5C4A2E"             # 对比 CALLOUT_BG 约 7.6

FONT_CJK = "Noto Sans CJK SC"
FONT_LATIN = "Inter"

# 图表几何
CARD_Y, CARD_H = 142, 452
PLOT_X0, PLOT_X1 = 196, 1196
PLOT_Y_ZERO = 530
PLOT_Y_TOP = 250
AXIS_MAX = 200
AXIS_STEP = 40
PX_PER_WAN = (PLOT_Y_ZERO - PLOT_Y_TOP) / AXIS_MAX   # 1.4
BAR_W = 76          # 组内总宽 76+12+76=164，组距 250，组间隙 86
BAR_GAP = 12
GROUP_CENTERS = [320, 570, 820, 1070]

# 底部两块
PANEL_Y, PANEL_H = 620, 204
PROFIT_CARD_X = MARGIN
PROFIT_CARD_W = 764
CALLOUT_X = 848
CALLOUT_W = W - MARGIN - CALLOUT_X   # 376

FONT_TITLE = 34
FONT_SUBTITLE = 22
FONT_CARD_TITLE = 26
FONT_LEGEND = 20
FONT_ANNOTATION = 18
FONT_UNIT = 18
FONT_AXIS = 18
FONT_BAR_LABEL = 19
FONT_X_LABEL = 20
FONT_PANEL_TITLE = 24
FONT_QUARTER = 18
FONT_PROFIT_VALUE = 26
FONT_MARGIN_NOTE = 18
FONT_CALLOUT_BODY = 22
FONT_FOOTER = 18


def esc(s: str) -> str:
    """XML 属性/文本转义；遇未处理的引号直接报错，避免生成坏 DSL。"""
    if any(c in s for c in ('"', "<", ">")):
        raise ValueError(f"不允许出现在文本中的字符：{s!r}")
    return s.replace("&", "&amp;")


def est_w(s: str, size: float) -> float:
    """粗略墨宽估计。刻意偏大：容器宽有余量才不会把文字裁掉，
    定位一律靠 CENTER 对齐到目标点，不依赖估计精度。"""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E80:
            w += size * 1.08
        elif ch == " ":
            w += size * 0.32
        elif ch in "iljtI!|1,.:;\'\"":
            w += size * 0.34
        else:
            w += size * 0.74
    return round(w, 2)


def pick_font(s: str) -> str:
    return FONT_LATIN if all(ord(c) < 0x2E80 for c in s) else FONT_CJK


def load_rows() -> list[dict]:
    rows = []
    with (TASK / "inputs" / "source.csv").open(encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            rev = float(r["revenue_wan"])
            cost = float(r["cost_wan"])
            profit = round(rev - cost, 4)
            rows.append({
                "quarter": r["quarter"].strip(),
                "revenue_wan": rev,
                "cost_wan": cost,
                "profit_wan": profit,
                "margin_pct": round(profit / rev * 100, 1),
            })
    return rows


def build_axes(rows: list[dict]) -> dict:
    """按共同零起点计算所有柱的 x / height / top。"""
    bars = []
    for i, r in enumerate(rows):
        cx = GROUP_CENTERS[i]
        for key, color, dx in (("revenue_wan", REVENUE, -BAR_W - BAR_GAP // 2),
                               ("cost_wan", COST, BAR_GAP // 2)):
            value = r[key]
            h = round(value * PX_PER_WAN, 2)
            bars.append({
                "quarter": r["quarter"],
                "series": "revenue" if key.startswith("rev") else "cost",
                "value_wan": value,
                "color": color,
                "x": round(cx + dx, 1),
                "width": BAR_W,
                "height_px": h,
                "top_y": round(PLOT_Y_ZERO - h, 1),
                "base_y": PLOT_Y_ZERO,
                "label_x": round(cx + dx + BAR_W / 2, 1),
                "label_text": f"{value:g}",
            })
    ticks = []
    v = 0
    while v <= AXIS_MAX:
        ticks.append({
            "value_wan": v,
            "y": round(PLOT_Y_ZERO - v * PX_PER_WAN, 1),
            "label": f"{v:g}",
        })
        v += AXIS_STEP
    return {
        "unit": "万元",
        "zero_baseline": True,
        "common_zero_start": True,
        "min_wan": 0,
        "max_wan": AXIS_MAX,
        "step_wan": AXIS_STEP,
        "px_per_wan": PX_PER_WAN,
        "plot_area": {"x0": PLOT_X0, "x1": PLOT_X1,
                      "y_top": PLOT_Y_TOP, "y_zero": PLOT_Y_ZERO},
        "ticks": ticks,
        "group_centers_x": GROUP_CENTERS,
        "bar_width_px": BAR_W,
        "bar_gap_px": BAR_GAP,
        "bars": bars,
    }


def write_corrected_data(rows: list[dict], axes: dict) -> dict:
    top_profit = max(rows, key=lambda r: r["profit_wan"])
    top_margin = max(rows, key=lambda r: r["margin_pct"])
    bottom_profit = min(rows, key=lambda r: r["profit_wan"])
    rev = [r["revenue_wan"] for r in rows]
    doc = {
        "schema_version": 1,
        "task_id": "A16",
        "path_base": "output_dir",
        "source": {"path": "tasks/A16-visual-data-forensics/inputs/source.csv",
                   "note": "唯一可信原始数据；图上文字与柱高均以此为准",
                   "unit": "万元"},
        "quarters": rows,
        "derived": {
            "total_revenue_wan": round(sum(rev), 1),
            "total_cost_wan": round(sum(r["cost_wan"] for r in rows), 1),
            "total_profit_wan": round(sum(r["profit_wan"] for r in rows), 1),
            "avg_margin_pct": round(sum(r["margin_pct"] for r in rows) / len(rows), 2),
            "revenue_peak": {"quarter": max(rows, key=lambda r: r["revenue_wan"])["quarter"],
                             "value_wan": max(rev)},
            "revenue_trough": {"quarter": min(rows, key=lambda r: r["revenue_wan"])["quarter"],
                               "value_wan": min(rev)},
            "revenue_q2_to_q3_delta_wan": rows[2]["revenue_wan"] - rows[1]["revenue_wan"],
            "revenue_q2_to_q3_delta_pct": round(
                (rows[2]["revenue_wan"] - rows[1]["revenue_wan"]) /
                rows[1]["revenue_wan"] * 100, 1),
            "revenue_q4_vs_q1_pct": round(
                (rows[3]["revenue_wan"] - rows[0]["revenue_wan"]) /
                rows[0]["revenue_wan"] * 100, 1),
        },
        "axes": axes,
        "conclusion": {
            "title": f"季度复盘：{top_profit['quarter']} 利润最高"
                     f"（{top_profit['profit_wan']:g} 万元）",
            "subtitle": "Q3 收入环比回落 7 万元（−5.2%），Q4 回升至全年最高 180 万元",
            "focus_quarter": top_profit["quarter"],
            "focus_evidence": [
                {"field": "profit_wan", "value": top_profit["profit_wan"],
                 "claim": "四季最高利润", "rank": 1,
                 "others": {r["quarter"]: r["profit_wan"] for r in rows
                            if r["quarter"] != top_profit["quarter"]}},
                {"field": "margin_pct", "value": top_profit["margin_pct"],
                 "claim": "四季最高利润率", "rank": 1,
                 "others": {r["quarter"]: r["margin_pct"] for r in rows
                            if r["quarter"] != top_profit["quarter"]}},
            ],
            "counter_evidence": {
                "quarter": bottom_profit["quarter"],
                "profit_wan": bottom_profit["profit_wan"],
                "margin_pct": bottom_profit["margin_pct"],
                "claim": "Q3 利润 32 万元为四季最低，利润率 25.0% 与 Q1 并列、"
                         "低于 Q4 的 30.0%；Q3 收入 128 万元仅高于 Q1 的 120 万元。",
            },
            "callout_lines": [
                "Q4 利润 54 万元",
                "利润率 30.0%，两项均四季最高",
                "Q3 利润 32 万元为四季最低",
            ],
        },
        "text_scale_rules": {
            "body_min_px": 22,
            "annotation_min_px": 18,
            "actual": {"page_title": FONT_TITLE, "subtitle": FONT_SUBTITLE,
                       "card_title": FONT_CARD_TITLE, "legend": FONT_LEGEND,
                       "x_label": FONT_X_LABEL, "bar_label": FONT_BAR_LABEL,
                       "axis_label": FONT_AXIS, "unit": FONT_UNIT,
                       "quarter": FONT_QUARTER, "profit_value": FONT_PROFIT_VALUE,
                       "margin_note": FONT_MARGIN_NOTE,
                       "callout_title": FONT_PANEL_TITLE,
                       "callout_body": FONT_CALLOUT_BODY,
                       "footer": FONT_FOOTER},
        },
    }
    return doc


def txt(text: str, x: float, y: float, w: float, h: float, size: int,
        color: str, *, bold: bool = False, align: str = "CENTER_LEFT") -> str:
    box = f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
    inner = f'<Container width="{w}" height="{h}" alignment="{align}">'
    attrs = (f'fontFamily="{pick_font(text)}" fontSize="{size}" color="{color}"')
    if bold:
        attrs += ' fontStyle="BOLD"'
    return (f'{box}{inner}<Text {attrs} text="{esc(text)}" />'
            f'</Container></Positioned>')


def rect(x: float, y: float, w: float, h: float, color: str,
         *, radius: float | None = None, border: str | None = None,
         top_radius: float | None = None) -> str:
    a = f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
    p = f'width="{w}" height="{h}" color="{color}"'
    if radius:
        p += f' borderRadius="{radius}"'
    if top_radius:
        p += f' borderRadiusTopLeft="{top_radius}" ' \
             f'borderRadiusTopRight="{top_radius}"'
    if border:
        p += f' border="{border}"'
    return f'{a}<Container {p} /></Positioned>'


def build_dsl(rows: list[dict], doc: dict) -> str:
    axes = doc["axes"]
    L: list[str] = []
    A = L.append
    A(f'<Snapshot type="png">')
    A(f'<Container width="{W}" height="{H}">')
    A(f'<Stack width="{W}" height="{H}">')
    A(rect(0, 0, W, H, CANVAS_BG))

    # ---- 页眉 ----
    A(txt(doc["conclusion"]["title"], MARGIN, 42, 900, 46, FONT_TITLE, INK,
          bold=True))
    A(txt(doc["conclusion"]["subtitle"], MARGIN, 96, 1100, 30, FONT_SUBTITLE,
          INK_2))

    # ---- 柱图卡片 ----
    A(rect(MARGIN, CARD_Y, CONTENT_W, CARD_H, CARD_BG, radius=14,
           border=f'1 SOLID {CARD_BORDER}'))
    A(txt("收入与成本对比", MARGIN + 32, CARD_Y + 24, 420, 34, FONT_CARD_TITLE,
          INK, bold=True))
    A(txt("单位：万元", MARGIN + 32, CARD_Y + 62, 200, 24, FONT_UNIT, INK_3))

    # 图例（蓝=收入、橙=成本，与柱色一致）
    A(rect(948, CARD_Y + 30, 18, 18, REVENUE, radius=4))
    A(txt("收入", 978, CARD_Y + 26, 120, 26, FONT_LEGEND, INK, align="CENTER"))
    A(rect(1086, CARD_Y + 30, 18, 18, COST, radius=4))
    A(txt("成本", 1116, CARD_Y + 26, 120, 26, FONT_LEGEND, INK,
          align="CENTER"))

    # 网格线与刻度（刻度标签统一居中于 x=152，容器留足余量避免裁字）
    for t in axes["ticks"]:
        ty = t["y"]
        is_zero = t["value_wan"] == 0
        A(rect(PLOT_X0, ty, PLOT_X1 - PLOT_X0, 1,
               BASELINE if is_zero else GRID))
        A(txt(t["label"], 152 - 40, ty - 12, 80, 24, FONT_AXIS, INK_3,
              align="CENTER"))

    # 柱体与柱标签（标签以柱中心为轴居中，容器比估计墨宽大 30px）
    for b in axes["bars"]:
        A(rect(b["x"], b["top_y"], b["width"], b["height_px"], b["color"],
               top_radius=6))
        bw = max(est_w(b["label_text"], FONT_BAR_LABEL) + 30, 60)
        A(txt(b["label_text"], b["label_x"] - bw / 2, b["top_y"] - 30, bw, 24,
              FONT_BAR_LABEL, INK, bold=True, align="CENTER"))

    # x 轴季度标签
    for i, r in enumerate(rows):
        A(txt(r["quarter"], GROUP_CENTERS[i] - 35, PLOT_Y_ZERO + 14, 70, 26,
              FONT_X_LABEL, INK_2, bold=True, align="CENTER"))

    # ---- 利润明细卡片 ----
    A(rect(PROFIT_CARD_X, PANEL_Y, PROFIT_CARD_W, PANEL_H, CARD_BG, radius=14,
           border=f'1 SOLID {CARD_BORDER}'))
    A(txt("利润明细（收入 − 成本）", PROFIT_CARD_X + 32, PANEL_Y + 24, 600, 32,
          FONT_PANEL_TITLE, INK, bold=True))
    pitch = 172
    x0 = PROFIT_CARD_X + 32
    for i, r in enumerate(rows):
        x = x0 + i * pitch
        A(txt(r["quarter"], x, PANEL_Y + 72, 60, 22, FONT_QUARTER, INK_3,
              bold=True))
        A(txt(f'{r["profit_wan"]:g} 万元', x, PANEL_Y + 96, 150, 34,
              FONT_PROFIT_VALUE, INK, bold=True))
        A(txt(f'利润率 {r["margin_pct"]:.1f}%', x, PANEL_Y + 138, 150, 22,
              FONT_MARGIN_NOTE, PROFIT_UP, bold=True))

    # ---- 重点观察 ----
    A(rect(CALLOUT_X, PANEL_Y, CALLOUT_W, PANEL_H, CALLOUT_BG, radius=14,
           border=f'4 SOLID {CALLOUT_BORDER}'))
    A(txt(f'重点观察 · {doc["conclusion"]["focus_quarter"]}',
          CALLOUT_X + 30, PANEL_Y + 26, 300, 32, FONT_PANEL_TITLE, INK,
          bold=True))
    for i, line in enumerate(doc["conclusion"]["callout_lines"]):
        A(txt(line, CALLOUT_X + 30, PANEL_Y + 70 + i * 30, 300, 30,
              FONT_CALLOUT_BODY, CALLOUT_INK))

    # ---- 页脚 ----
    A(txt("数据源 inputs/source.csv（唯一可信原始数据）· 柱高按共同零点等比绘制"
          "· 修正版", MARGIN, 848, 1168, 24, FONT_FOOTER, FOOTER_INK))

    A('</Stack>')
    A('</Container>')
    A('</Snapshot>')
    return "\n".join(L) + "\n"


def main() -> int:
    render = "--render" in sys.argv
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dsl_tmp = TMP_DIR / "dsl"
    dsl_tmp.mkdir(parents=True, exist_ok=True)

    rows = load_rows()
    axes = build_axes(rows)
    doc = write_corrected_data(rows, axes)
    (OUT_DIR / "corrected-data.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    dsl = build_dsl(rows, doc)
    (OUT_DIR / "corrected-report.snapshot").write_text(dsl, encoding="utf-8")

    if not render:
        print("corrected-data.json / corrected-report.snapshot 已生成")
        print(f'  quarters: ' + ", ".join(
            f'{r["quarter"]}={r["revenue_wan"]:g}/{r["cost_wan"]:g}/'
            f'{r["profit_wan"]:g}({r["margin_pct"]:.1f}%)' for r in rows))
        print(f'  px_per_wan={PX_PER_WAN}  zero_baseline  bars='
              f'{len(axes["bars"])}')
        return 0

    # ---- 请求服务 ----
    # tools/suite.py 通过 SNAPSHOT_RUN_ID 解析题目录，先注入本进程的 run_id。
    os.environ.setdefault("SNAPSHOT_RUN_ID", RUN_ID)
    os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(SUITE_ROOT))
    sys.path.insert(0, str(SUITE_ROOT / "tools"))
    import suite as S  # noqa: E402
    import http.client  # noqa: E402

    promote = "--promote" in sys.argv
    # 版本号：取 tmp/dsl 下已有 vNN 的最大值 +1，保证不覆盖历史版本
    existing = sorted(dsl_tmp.glob("v*-corrected-report.snapshot"))
    ver = int(existing[-1].name[1:3]) + 1 if existing else 1
    vname = f"v{ver:02d}-corrected-report"
    dsl_path = dsl_tmp / (vname + ".snapshot")
    dsl_path.write_text(dsl, encoding="utf-8")
    label = "corrected-report"
    rid = "req-a16-%s-%s" % (vname, uuid.uuid4().hex[:6])

    last: dict = {}
    for attempt in range(1, 4):
        full = rid if attempt == 1 else f"{rid}-a{attempt}"
        t0 = time.monotonic()
        started = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
        try:
            status, body, meta = S.snapshot_request("A16", dsl, label,
                                                    timeout=180)
            kind_status, err = (status,
                                S.error_summary(body) if status != 200
                                else None)
        except (TimeoutError, ConnectionError, http.client.HTTPException) as exc:
            kind_status, body = 0, None
            err = f"{type(exc).__name__} after {time.monotonic()-t0:.1f}s: {exc}"
            meta = {"status": 0, "content_type": None, "headers": {},
                    "error": err, "started_at": started,
                    "ended_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
                    "elapsed_ms": round((time.monotonic() - t0) * 1000, 1)}
        elapsed = meta.get("elapsed_ms")
        ended = meta.get("ended_at")
        if body and status == 200:
            ext = ".png"
            resp_path = TMP_DIR / "responses" / (full + ext)
            resp_path.write_bytes(body)
            last = {"request_id": full, "status": status, "bytes": len(body),
                    "response": str(resp_path.relative_to(SUITE_ROOT))}
            if promote:
                (OUT_DIR / "corrected-report.png").write_bytes(body)
                (OUT_DIR / "corrected-report.snapshot").write_text(
                    dsl, encoding="utf-8")
                last["promoted"] = str(vname)
        else:
            resp_path = TMP_DIR / "responses" / (full + ".error.json")
            resp_path.write_bytes(body or b"")
            last = {"request_id": full, "status": kind_status, "error": err,
                    "response": str(resp_path.relative_to(SUITE_ROOT))}
        S.log_request("A16", {
            "request_id": full, "task_id": "A16", "kind": "render",
            "purpose": f"{vname}：生成修正版可信报告"
                       + ("（提升为最终交付）" if promote else ""),
            "version": vname,
            "dsl_path": S.rel(dsl_path),
            "started_at": started, "ended_at": ended,
            "timezone": "Asia/Shanghai (UTC+08:00)",
            "elapsed_ms": elapsed, "http_status": kind_status,
            "content_type": meta.get("content_type"),
            "response_bytes": len(body) if body else None,
            "response_path": S.rel(resp_path),
            "error_summary": err,
        })
        if status == 200:
            break
        time.sleep(3)

    print(json.dumps(last, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
