#!/usr/bin/env python
"""A15 锚点核验：用**同一套测量函数**分别测参考图与重建图，逐分量比较误差。

启动基准：总任务根 (suite_root)。
用法：python tmp/run-20261011-01/A15/verify_a15.py <reconstructed.png>

要点：
  * 参考坐标不是抄来的标准值，而是对公开 reference.png 做像素测量得到
    （参考图本身只是被观察/测量，没有被嵌入或裁块使用）。
  * 参考图与重建图走完全相同的测量代码，因此误差是可比的。
  * 矩形锚点四边分别比较；点锚点比较 (x,y)；边界锚点比较单个 x 或 y。
  * 判定门槛：题面规定的 ±8px（对应分量绝对误差 ≤8）。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from PIL import Image

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
REF = BASE / "tasks/A15-reference-reconstruction/inputs/reference.png"
OUTD = BASE / "tmp/run-20261011-01/A15/drafts"
TOL = 8

SIDE = (20, 35, 60)
MAIN = (243, 246, 251)
WHITE = (255, 255, 255)
BLUE = (36, 92, 228)
SIDE2 = (35, 57, 84)
SEL = (41, 68, 103)
MINT = (100, 219, 182)
GRID = (231, 237, 245)
PILL3 = (220, 245, 236)


def near(c, t, tol=12):
    return abs(c[0] - t[0]) <= tol and abs(c[1] - t[1]) <= tol and abs(c[2] - t[2]) <= tol


def bbox_color(im, region, target, tol=12):
    px = im.load()
    x0, y0, x1, y1 = region
    xs, ys = [], []
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if near(px[x, y][:3], target, tol):
                xs.append(x)
                ys.append(y)
    return [min(xs), min(ys), max(xs), max(ys)] if xs else None


def bbox_ink(im, region, bg, thr=30, exclude_border=True):
    """字形墨迹包围盒。exclude_border=True 时忽略贴近卡片描边的像素列，
    避免把 1px 描边当成文字（首版 A24 就是被描边列把 y 顶到 190 的）。"""
    px = im.load()
    x0, y0, x1, y1 = region
    xs, ys = [], []
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = px[x, y][:3]
            if abs(c[0] - bg[0]) + abs(c[1] - bg[1]) + abs(c[2] - bg[2]) <= thr:
                continue
            if exclude_border and (near(c, (226, 232, 241), 10) or near(c, MAIN, 10)):
                continue
            xs.append(x)
            ys.append(y)
    return [min(xs), min(ys), max(xs), max(ys)] if xs else None


def bbox_card(im, region):
    """白卡外轮廓 = 纯白填充 ∪ 1px #E2E8F1 描边的像素包围盒。

    不能用「非主背景色」的包围盒：那会把卡内文字也算进去（首版就是这么误判的，
    KPI 卡被量成文字块的框而不是卡片框）。"""
    px = im.load()
    x0, y0, x1, y1 = region
    xs, ys = [], []
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = px[x, y][:3]
            if near(c, WHITE, 6) or near(c, (226, 232, 241), 6):
                xs.append(x)
                ys.append(y)
    return [min(xs), min(ys), max(xs), max(ys)] if xs else None


def bbox_notcolor(im, region, target, tol=12):
    """区域内「不是 target 色」的像素包围盒（用于取白色卡片在浅底上的外轮廓）。"""
    px = im.load()
    x0, y0, x1, y1 = region
    xs, ys = [], []
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if not near(px[x, y][:3], target, tol):
                xs.append(x)
                ys.append(y)
    return [min(xs), min(ys), max(xs), max(ys)] if xs else None


def edge_x(im, y, x0, x1, bg, tol=10):
    """从 x0 向右找离开 bg 的第一个像素 x（即该区块左边界）。"""
    px = im.load()
    for x in range(x0 + 1, x1):
        if not near(px[x, y][:3], bg, tol):
            return x
    return None


def edge_x_right(im, y, x0, x1, bg, tol=10):
    px = im.load()
    last = x0
    for x in range(x0, x1):
        if near(px[x, y][:3], bg, tol):
            last = x
    return last


def span_x(im, y, x0, x1, target, tol=12, minrun=20):
    """在行 y 上找 target 色的连续段，返回 (起点, 终点)。"""
    px = im.load()
    runs, cur, s = [], None, None
    for x in range(x0, x1 + 1):
        if near(px[x, y][:3], target, tol):
            if cur is None:
                s = x
            cur = x
        else:
            if cur is not None and cur - s >= minrun:
                runs.append((s, cur))
            cur = None
    if cur is not None and cur - s >= minrun:
        runs.append((s, cur))
    return max(runs, key=lambda r: r[1] - r[0]) if runs else None


# ---------------------------------------------------------------- 锚点定义
# kind: rect / point / edge
ANCHORS = [
    dict(id="A01", name="侧栏右边界", kind="edge_x", quadrant="左上",
         desc="侧栏深色区块与主区浅底的交界 x",
         ref=220,
         measure=lambda im: edge_x(im, 450, 0, 300, SIDE)),
    dict(id="A02", name="导航选中态外框", kind="rect", quadrant="左上",
         desc="侧栏第一项 Overview 的高亮圆角矩形外轮廓",
         measure=lambda im: bbox_color(im, (0, 100, 215, 180), SEL)),
    dict(id="A03", name="品牌标记外框", kind="rect", quadrant="左上",
         desc="NORTHSTAR 左侧薄荷色标记方块外轮廓",
         measure=lambda im: bbox_color(im, (18, 22, 68, 72), MINT)),
    dict(id="A04", name="主标题可见字形框左上角", kind="point", quadrant="左上",
         desc="「Workspace Overview」可见字形包围盒的左上角 (x, y)",
         measure=lambda im: (lambda b: (b[0], b[1]))(
             bbox_ink(im, (250, 24, 760, 76), MAIN, 34))),
    dict(id="A05", name="KPI 卡 1 外框", kind="rect", quadrant="左上",
         desc="REVENUE 卡片外轮廓",
         measure=lambda im: bbox_card(im, (250, 130, 630, 292))),
    dict(id="A06", name="KPI 卡 2 外框", kind="rect", quadrant="上",
         desc="ORDERS 卡片外轮廓",
         measure=lambda im: bbox_card(im, (630, 130, 1010, 292))),
    dict(id="A07", name="KPI 卡 3 外框", kind="rect", quadrant="右上",
         desc="REFUND RATE 卡片外轮廓",
         measure=lambda im: bbox_card(im, (1012, 130, 1430, 292))),
    dict(id="A08", name="导出报告按钮外框", kind="rect", quadrant="右上",
         desc="页眉右上蓝色按钮外轮廓",
         measure=lambda im: bbox_color(im, (1150, 30, 1425, 105), BLUE)),
    dict(id="A09", name="净收入图表卡外框", kind="rect", quadrant="右上",
         desc="Net revenue 白色卡片外轮廓",
         measure=lambda im: bbox_card(im, (250, 303, 1012, 602))),
    dict(id="A10", name="图表零线左端点", kind="point", quadrant="右上",
         desc="0 值网格线（零线）的左端点 (x, y)",
         measure=lambda im: (lambda s: (s[0], 549))(span_x(im, 549, 300, 1000, GRID))),
    dict(id="A11", name="图表 120 网格线右端点", kind="point", quadrant="右上",
         desc="最上一条网格线的右端点 (x, y)",
         measure=lambda im: (lambda s: (s[1], 405))(span_x(im, 405, 300, 1000, GRID))),
    dict(id="A12", name="最后一根柱的顶部中心", kind="point", quadrant="右上",
         desc="Sep 柱（值 108）的顶部中心 (x, y)",
         measure=lambda im: (lambda b: (round((b[0] + b[2]) / 2, 1), b[1]))(
             bbox_color(im, (850, 400, 930, 555), BLUE))),
    dict(id="A13", name="第一根柱的顶部中心", kind="point", quadrant="左",
         desc="Apr 柱（值 54）的顶部中心 (x, y)",
         measure=lambda im: (lambda b: (round((b[0] + b[2]) / 2, 1), b[1]))(
             bbox_color(im, (345, 400, 425, 555), BLUE))),
    dict(id="A14", name="活动卡外框", kind="rect", quadrant="右",
         desc="Team activity 白色卡片外轮廓",
         measure=lambda im: bbox_card(im, (1015, 303, 1430, 602))),
    dict(id="A15", name="项目表格卡外框", kind="rect", quadrant="下",
         desc="Recent projects 白色卡片外轮廓",
         measure=lambda im: bbox_card(im, (250, 616, 1430, 856))),
    dict(id="A16", name="表格表头底色带", kind="rect", quadrant="下",
         desc="表头 PROJECT/OWNER/STATUS/DUE 的浅色底带外轮廓",
         measure=lambda im: bbox_color(im, (270, 684, 1390, 726), MAIN, 4)),
    dict(id="A17", name="最后一行状态标签外框", kind="rect", quadrant="右下",
         desc="第三行 Done 药丸外轮廓",
         measure=lambda im: bbox_color(im, (1000, 790, 1210, 838), PILL3)),
    dict(id="A18", name="第一行状态标签外框", kind="rect", quadrant="右",
         desc="第一行 In progress 药丸外轮廓",
         # tol 必须收紧：药丸填充 #E7EFFF 与主背景 #F3F6FB 在 tol=12 下会被混为一谈，
         # 量到的是搜索区边界而不是药丸。
         measure=lambda im: bbox_color(im, (1010, 722, 1200, 758), (231, 239, 255), 4)),
    dict(id="A19", name="PRO 工作区卡片外框", kind="rect", quadrant="左下",
         desc="侧栏底部 PRO WORKSPACE 卡片外轮廓",
         measure=lambda im: bbox_color(im, (0, 735, 215, 885), SIDE2)),
    dict(id="A20", name="页脚文字可见框左上角", kind="point", quadrant="左下",
         desc="「All data is fictional · Snapshot benchmark」字形包围盒左上角",
         measure=lambda im: (lambda b: (b[0], b[1]))(
             bbox_ink(im, (250, 856, 820, 886), MAIN, 34))),
    dict(id="A21", name="表格第三行项目名可见框左上角", kind="point", quadrant="左下",
         desc="「Orbit / Launch」字形包围盒左上角",
         measure=lambda im: (lambda b: (b[0], b[1]))(
             bbox_ink(im, (288, 796, 700, 826), WHITE, 40))),
    dict(id="A22", name="侧栏导航第三项圆点中心", kind="point", quadrant="左",
         desc="Analytics 项圆点中心 (x, y)",
         measure=lambda im: (lambda b: (round((b[0] + b[2]) / 2, 1),
                                        round((b[1] + b[3]) / 2, 1)))(
             bbox_color(im, (28, 248, 54, 278), (119, 145, 179)))),
    dict(id="A23", name="活动卡第三项圆点中心", kind="point", quadrant="右下",
         desc="Render complete 项圆点中心 (x, y)",
         measure=lambda im: (lambda b: (round((b[0] + b[2]) / 2, 1),
                                        round((b[1] + b[3]) / 2, 1)))(
             bbox_color(im, (1046, 508, 1072, 540), (22, 130, 103)))),
    dict(id="A24", name="KPI 卡 1 数值可见框左上角", kind="point", quadrant="左上",
         desc="「¥128,400」字形包围盒左上角",
         measure=lambda im: (lambda b: (b[0], b[1]))(
             bbox_ink(im, (275, 190, 620, 238), WHITE, 40))),
]


def norm(v):
    if v is None:
        return None
    if isinstance(v, tuple):
        return [round(float(a), 1) for a in v]
    if isinstance(v, list):
        return [round(float(a), 1) for a in v]
    return round(float(v), 1)


def main() -> None:
    rec_path = BASE / (sys.argv[1] if len(sys.argv) > 1
                       else "outputs/run-20261011-01/A15/reconstructed.png")
    with Image.open(REF) as s:
        s.load()
        ref_im = s.convert("RGB")
    with Image.open(rec_path) as s:
        s.load()
        rec_im = s.convert("RGB")

    rows = []
    for a in ANCHORS:
        rv = a["measure"](ref_im)
        mv = a["measure"](rec_im)
        rec = {"id": a["id"], "name": a["name"], "type": a["kind"],
               "quadrant": a["quadrant"], "object": a["desc"],
               "reference_estimated": norm(rv), "reconstructed_actual": norm(mv)}
        if rv is None or mv is None:
            rec["component_errors"] = None
            rec["passed"] = False
            rec["note"] = "某一侧未能测得该对象（返回 None）"
        elif a["kind"] == "rect":
            errs = [round(abs(mv[i] - rv[i]), 1) for i in range(4)]
            rec["component_errors"] = dict(zip(["left", "top", "right", "bottom"], errs))
            rec["max_abs_error_px"] = max(errs)
            rec["passed"] = max(errs) <= TOL
        elif a["kind"] == "edge_x":
            e = round(abs(mv - rv), 1)
            rec["component_errors"] = {"x": e}
            rec["max_abs_error_px"] = e
            rec["passed"] = e <= TOL
        else:
            errs = [round(abs(mv[i] - rv[i]), 1) for i in range(len(rv))]
            rec["component_errors"] = dict(zip(["x", "y"], errs))
            rec["max_abs_error_px"] = max(errs)
            rec["passed"] = max(errs) <= TOL
        rec["method"] = "参考图与重建图使用同一测量函数；边界锚点比较 x，点锚点比较 (x,y)，矩形锚点四边分别比较"
        rows.append(rec)
        e = rec["max_abs_error_px"]
        print(f"{a['id']} {a['name'][:22]:24} ref={rec['reference_estimated']} "
              f"rec={rec['reconstructed_actual']} err={e} "
              f"{'PASS' if rec['passed'] else 'FAIL'}")

    quads = sorted({r["quadrant"] for r in rows})
    out = {
        "schema_version": 1, "task_id": "A15", "round": "round-01",
        "path_base": "output_dir",
        "tolerance_px": TOL,
        "tolerance_rule": "题面：对应分量的绝对误差均 ≤8px；矩形四边分别比较，不平均抵消",
        "measurement_note": "参考坐标由对公开 reference.png 的像素测量得到（参考图仅被观察与测量，"
                            "未嵌入、未裁块）；参考与重建走同一测量代码",
        "reference": {"path": "tasks/A15-reference-reconstruction/inputs/reference.png",
                      "size": list(ref_im.size)},
        "reconstructed": {"path": str(sys.argv[1] if len(sys.argv) > 1
                                      else "outputs/run-20261011-01/A15/reconstructed.png"),
                          "size": list(rec_im.size)},
        "quadrants_covered": quads,
        "anchors": rows,
        "anchor_count": len(rows),
        "all_passed": all(r["passed"] for r in rows),
        "worst_error_px": max([r["max_abs_error_px"] for r in rows
                              if r["max_abs_error_px"] is not None] or [None]),
        "worst_error_anchor": max(
            [r for r in rows if r["max_abs_error_px"] is not None],
            key=lambda r: r["max_abs_error_px"])["name"]
        if any(r["max_abs_error_px"] is not None for r in rows) else None,
    }
    p = OUTD / "anchor-verify.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nanchors={len(rows)} quadrants={quads} all_passed={out['all_passed']} "
          f"worst={out['worst_error_px']}px")
    print("->", p.as_posix())


if __name__ == "__main__":
    main()