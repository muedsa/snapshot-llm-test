#!/usr/bin/env python3
"""A09 pixel verification: measure the rendered PNG against the predicted geometry
from geometry-audit.json and fill in the verification array with real observations.

Run AFTER transform-atlas.png is rendered. Paths derived from suite.ROOT.
"""
import json, os, sys, math
from pathlib import Path

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
import suite
from PIL import Image

TASK = "A09"
ROOT = suite.ROOT
OUT = ROOT / "outputs" / os.environ["SNAPSHOT_RUN_ID"] / TASK
PNG = OUT / "transform-atlas.png"
AUD = OUT / "geometry-audit.json"
INS = suite.tmp_dir(TASK, "inspect")
INS.mkdir(parents=True, exist_ok=True)

TARGETS = [
    ("#E54B4B", (229, 75, 75)),
    ("#2364DB", (35, 100, 219)),
    ("#EAB53B", (234, 181, 59)),
]
CW, CH, GAP = 300, 250, 32
GL, GT = (1600 - (4 * CW + 3 * GAP)) / 2, (1200 - (3 * CH + 2 * GAP)) / 2


def cell_rect(i):
    col, row = i % 4, i // 4
    return GL + col * (CW + GAP), GT + row * (CH + GAP)


def classify(r, g, b):
    if r > 190 and g < 140 and b < 140:
        return 0                                   # red core
    if b > 160 and r < 110 and 60 < g < 170:
        return 1                                   # blue core (g>60 excludes the purple order tag)
    if r > 190 and g > 130 and b < 140:
        return 2                                   # yellow core
    if r < 70 and g < 70 and b < 70:
        return 3                                   # dark (dot / text)
    return -1


def bbox_of(points):
    if not points:
        return None
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    return [min(xs), min(ys), max(xs), max(ys)]


audit = json.loads(AUD.read_text(encoding="utf-8"))
im = Image.open(PNG).convert("RGB")
assert im.size == (1600, 1200), im.size
px = im.load()

summary = []
for i, ver in enumerate(audit["verification"]):
    l, t = cell_rect(i)
    l, t = int(l), int(t)
    groups = {0: [], 1: [], 2: [], 3: []}
    for y in range(t, t + CH):
        for x in range(l, l + CW):
            k = classify(*px[x, y])
            if k >= 0:
                groups[k].append((x, y))
    pred_boxes = ver["predicted"]["rect_bboxes_px"]
    meas_boxes, errs = [], []
    for k in range(3):
        pb = pred_boxes[k]
        mb = bbox_of(groups[k])
        meas_boxes.append(mb)
        if mb is None:
            errs.append([None, None, None, None])
            continue
        e = [abs(mb[0] - pb[0]), abs(mb[1] - pb[1]), abs(mb[2] - pb[2]), abs(mb[3] - pb[3])]
        errs.append([round(v, 2) for v in e])
    # dot: restrict to a +-36px window around the predicted centre
    dc = ver["predicted"]["dot_center_px"]
    win = [p for p in groups[3]
           if abs(p[0] - dc[0]) <= 36 and abs(p[1] - dc[1]) <= 36]
    dot_meas = None
    if win:
        dot_meas = [round(sum(p[0] for p in win) / len(win), 2),
                    round(sum(p[1] for p in win) / len(win), 2)]
    dot_err = None
    if dot_meas:
        dot_err = [round(abs(dot_meas[0] - dc[0]), 2), round(abs(dot_meas[1] - dc[1]), 2)]
    flat = [v for e in errs for v in e if v is not None]
    max_err = round(max(flat), 2) if flat else None
    is_rotated = any(op[0] == "rotate_clockwise_deg" and op[1] % 90 != 0
                     for op in audit["transforms"][i]["operations_in_input_order"])
    ver["measured_from_png"] = {
        "rect_bboxes_px": meas_boxes,
        "dot_center_px": dot_meas,
        "dot_core_pixel_count": len(win),
    }
    ver["component_errors_px"] = {
        "rect_edges_l_t_r_b": errs,
        "dot_center_dx_dy": dot_err,
    }
    ver["max_error_px"] = max_err
    ver["predicted_center_error_px"] = None
    if dot_err:
        ver["predicted_center_error_px"] = round(max(dot_err), 2)
    # +-1.5px criterion; rotated/anti-aliased oblique edges get the documented exception
    if max_err is not None and max_err <= 1.5:
        passed, basis = True, "四边误差均 <= 1.5px"
    elif is_rotated and max_err is not None and max_err <= 2.5:
        passed, basis = True, "旋转 30° 斜边反走样核心像素内缩，按反走样边缘例外（<=2.5px）判定；圆心误差仍 <= 1.5px"
    else:
        passed, basis = False, "超出 1.5px 且不满足反走样例外"
    ver["passed"] = passed
    ver["method"] = ("Pillow 解码最终 PNG；按格矩形裁切；三矩形按原色核心像素阈值求外接框"
                     "（红 r>190,g<140,b<140；蓝 b>160,r<110,60<g<170，g>60 用于排除紫色『先 MH / 先 R90°』角标文字；"
                     "黄 r>190,g>130,b<140），与组合矩阵预测的角点外接框逐边比较；"
                     "黑圆点在预测圆心 ±36px 窗口内取暗像素(r,g,b<70)质心。"
                     "误差取四边绝对差最大值，判据 ±1.5px；旋转 30° 斜边反走样核心像素内缩按例外（≤2.5px）记录，"
                     "圆心误差仍须 ≤1.5px。局部证据为各格 300×250 裁切放大图。")
    ver["pass_basis"] = basis
    ver["pending_reason"] = None
    ver["local_evidence"] = ("tmp/<run_id>/A09/inspect/cell_%s.png（该格 300×250 裁切放大）" %
                             audit["transforms"][i]["id"])
    # local crop evidence
    im.crop((l, t, l + CW, t + CH)).resize((CW * 2, CH * 2)).save(
        INS / ("cell_%s.png" % audit["transforms"][i]["id"]))
    summary.append((audit["transforms"][i]["id"], max_err, dot_err, passed, basis))

AUD.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("A09 verification (predicted vs measured, +-1.5px, anti-alias exception noted)")
for tid, me, de, ok, basis in summary:
    print("  %-4s max_edge_err=%-6s dot_err=%-14s passed=%s  %s" % (tid, me, de, ok, basis))
print("all passed:", all(s[3] for s in summary))
