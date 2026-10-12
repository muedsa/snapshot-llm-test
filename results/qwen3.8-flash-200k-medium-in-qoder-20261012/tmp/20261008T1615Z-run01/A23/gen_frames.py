"""A23：12 个几何单元从分散汇聚成塔形结构 —— 封面 + 6 张透明关键帧。

用法：python gen_frames.py    ->  tmp/<run_id>/A23/frames/{cover,frame-0N}.snapshot
                                   tmp/<run_id>/A23/frames/frame-data.json
六帧由同一组参数生成：单元数、尺寸、颜色、轨迹端点完全一致，只有插值参数 t
不同；不嵌入任何预渲染图像，透明画布靠 Snapshot 的默认 background。
轨迹模型由 tune_paths.py 在 6 个采样帧上搜索得到（极角配对 + 直线插值 +
朝向在 t=0.5 前收敛到 0°），保证任一帧 12 个单元互不重叠。
"""
import json
import math
import os
import sys
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"]).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
from dslkit import Doc  # noqa: E402

OUT = root / "tmp" / rid / "A23" / "frames"
OUT.mkdir(parents=True, exist_ok=True)

FW, FH = 600, 600                      # 关键帧画布
CW, CH = 1200, 800                     # 封面画布
N = 12                                 # 单元数：六帧恒定
SIZE = 60                              # 单元边长：六帧恒定
UNIT_COLOR = "#38BDF8"                 # 主体颜色：六帧恒定
ROT_START = 45.0                       # 起始朝向
ROT_SETTLE_T = 0.5                     # 该 t 之后朝向恒为 0°
PAIR_PHASE = 2                         # 极角配对相位（tune_paths.py 搜索最优）
STAGGER = 0.30                         # 行程短的单元晚出发，避免中段挤在一起
RING_R = 250.0                         # 分散态所在圆半径
RING_PHASE = 15.0                      # 圆环相位，避免单元正对画布边
PITCH, VPITCH = 72.0, 84.0             # 塔形格距（60 + 12 / 24 间隙）
ROWS = [2, 4, 6]                       # 2+4+6 = 12，末帧为可识别塔形
FRAMES, FRAME_MS = 6, 250


def targets():
    """末帧塔形格心（返回左上角坐标），整组在 600×600 内水平垂直居中。"""
    pts, top_y = [], (FH - ((len(ROWS) - 1) * VPITCH + SIZE)) / 2.0
    for ri, cnt in enumerate(ROWS):
        row_w = (cnt - 1) * PITCH + SIZE
        for ci in range(cnt):
            pts.append((FW / 2 - row_w / 2 + ci * PITCH, top_y + ri * VPITCH))
    return pts


def starts():
    return [(FW / 2 + RING_R * math.cos(math.radians(i * (360.0 / N) + RING_PHASE)) - SIZE / 2,
             FH / 2 + RING_R * math.sin(math.radians(i * (360.0 / N) + RING_PHASE)) - SIZE / 2)
            for i in range(N)]


def paired_targets():
    """按极角顺序（相位 PAIR_PHASE）把塔形格位分配给圆环起点，泳道不交叉。"""
    tg, cx, cy = targets(), FW / 2, FH / 2
    ang = [math.degrees(math.atan2(y + SIZE / 2 - cy, x + SIZE / 2 - cx)) % 360
           for x, y in tg]
    order = sorted(range(N), key=lambda i: ang[i])
    return [tg[order[(i + PAIR_PHASE) % N]] for i in range(N)]


def smooth(t):
    return t * t * (3 - 2 * t)         # smoothstep：首尾速度 0，中段连续


def rot_of(t):
    k = min(1.0, t / ROT_SETTLE_T)
    return ROT_START * (1.0 - smooth(k))


def eased(i, t, st, tg):
    """行程短的单元晚出发（错峰），t=0 与 t=1 端点仍严格对齐。"""
    lens = [math.dist(st[j], tg[j]) for j in range(N)]
    s = STAGGER * (1.0 - lens[i] / max(lens))
    u = max(0.0, min(1.0, (t - s) / max(0.2, 1.0 - s)))
    return smooth(u), round(s, 4)


def units_at(t, scale=1.0, ox=0.0, oy=0.0):
    st, tg = starts(), paired_targets()
    rot = rot_of(t)
    out = []
    for i in range(N):
        u, s = eased(i, t, st, tg)
        out.append({"unit": i + 1,
                    "x_px": round((st[i][0] + (tg[i][0] - st[i][0]) * u) * scale + ox, 2),
                    "y_px": round((st[i][1] + (tg[i][1] - st[i][1]) * u) * scale + oy, 2),
                    "size_px": round(SIZE * scale, 2),
                    "rotation_deg": round(rot, 2),
                    "delay": s})
    return out


def min_gap(t):
    """该帧 12 个单元中心的最小间距（不重叠判定的依据）。"""
    us = units_at(t)
    c = [(u["x_px"] + u["size_px"] / 2, u["y_px"] + u["size_px"] / 2) for u in us]
    return round(min(math.dist(c[i], c[j])
                     for i in range(N) for j in range(i + 1, N)), 1)


def place(d, u, color=UNIT_COLOR, radius=10, ghost_border=None):
    """把单元画成绕自身中心旋转的圆角方块（Transform 16 值矩阵，A21 已核实）。

    ghost_border 给出描边串时只画空心轮廓（封面提示目标塔形用）。
    """
    s, r = u["size_px"], math.radians(u["rotation_deg"])
    co, si = math.cos(r), math.sin(r)
    box = (d.box(s, s, border=ghost_border, radius=radius) if ghost_border
           else d.box(s, s, color=color, radius=radius))
    seg = ('<Transform matrix="(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" '
           'alignment="CENTER">' % (f"{co:.6f}", f"{si:.6f}", f"{-si:.6f}",
                                    f"{co:.6f}")) + box + "</Transform>"
    d.pos(u["x_px"], u["y_px"], s, s, seg)


def frame_dsl(t):
    d = Doc(FW, FH, bg=None)
    for u in units_at(t):
        place(d, u)
    return d.dsl().replace(' background="None"', "")


COVER_SCALE = 0.9                      # 600×600 帧空间 -> 540×540 图示区
COVER_OX, COVER_OY = 640.0, 130.0
COVER_T = 0.42                         # 封面取汇聚中段：单元彼此分离
GHOST_BORDER = "2 SOLID #2A5079"       # 目标塔形轮廓（比 v02 更亮，读得出目标结构）


def cover_dsl():
    d = Doc(CW, CH, bg="#07101F")
    swarm, ghost = units_at(COVER_T, COVER_SCALE, COVER_OX, COVER_OY), \
        units_at(1.0, COVER_SCALE, COVER_OX, COVER_OY)
    for i, (a, b) in enumerate(zip(swarm, ghost)):   # 轨迹引线：中段 -> 目标格
        d.line(a["x_px"] + a["size_px"] / 2, a["y_px"] + a["size_px"] / 2,
               b["x_px"] + b["size_px"] / 2, b["y_px"] + b["size_px"] / 2,
               2, "#1B3A56")
    for u in ghost:                                  # 目标塔形以空心轮廓提示
        place(d, u, radius=8, ghost_border=GHOST_BORDER)
    for u in swarm:
        place(d, u)
    d.line(80, 262, 520, 262, 3, UNIT_COLOR)
    d.label(80, 288, 540, 96, "从结构到画面", color="#F2F6FC", size=64,
            style="BOLD")
    d.label(80, 396, 540, 40, "Structure converges into an image",
            color=UNIT_COLOR, size=28, style="BOLD")
    d.label(80, 448, 540, 32, "12 个几何单元 · 6 帧关键帧", color="#AEBDD4", size=24)
    d.label(80, 486, 540, 32, "每帧 250ms · 循环播放", color="#AEBDD4", size=24)
    d.label(80, 574, 540, 30, "封面 1200×800 RGB", color="#8195B2", size=22)
    d.label(80, 610, 540, 30, "关键帧 600×600 透明 PNG", color="#8195B2", size=22)
    return d.dsl()


def main():
    ts = [i / (FRAMES - 1) for i in range(FRAMES)]
    (OUT / "cover.snapshot").write_text(cover_dsl(), encoding="utf-8")
    for i, t in enumerate(ts, 1):
        (OUT / ("frame-%02d.snapshot" % i)).write_text(frame_dsl(t),
                                                       encoding="utf-8")
    st, tg = starts(), paired_targets()
    data = {
        "canvas": [FW, FH], "frames": FRAMES, "frame_ms": FRAME_MS,
        "unit_count_constant": N, "unit_size_px_constant": SIZE,
        "unit_color_constant": UNIT_COLOR,
        "rotation_deg_by_t": [[round(t, 2), round(rot_of(t), 2)] for t in ts],
        "rotation_rule": "45° 按 smoothstep 在 t=%.1f 前收敛到 0°，之后各帧轴对齐"
                         % ROT_SETTLE_T,
        "easing": "逐单元 u = s^2*(3-2s)，s = clamp((t-delay)/(1-delay),0,1)；"
                  "delay 按行程长短错峰（行程越短出发越晚），t=0 与 t=1 端点仍严格对齐",
        "stagger_max": STAGGER, "pairing_phase": PAIR_PHASE,
        "trajectory": "每个单元沿自身起点到配对塔形格心的直线段插值；起点在半径 "
                      "%d 的圆环上等角分布，格位按极角顺序（相位 %d）与圆环点配对，"
                      "因此 12 条轨迹泳道互不交叉" % (RING_R, PAIR_PHASE),
        "dispersed_ring_radius_px": RING_R, "pyramid_rows": ROWS,
        "pitch_px": [PITCH, VPITCH],
        "non_overlap_check": {
            "rule": "同帧相邻单元中心距 ≥ 60 + 24.9×(rot/45) + 4 余量（45° 菱形"
                    "外接需要 60×√2）；同时旋转外接方不得出画布",
            "min_center_distance_px_by_frame": [{"frame": k + 1, "t": round(t, 2),
                                                 "rotation_deg": round(rot_of(t), 2),
                                                 "min_center_distance_px": min_gap(t),
                                                 "required_min_px": round(
                                                     SIZE + 24.9 * rot_of(t) / ROT_START + 4, 1)}
                                                for k, t in enumerate(
                                                    [i / (FRAMES - 1) for i in range(FRAMES)])],
            "search_log": "tune_paths.py / tune_paths.log / tune_result.json："
                          "216 组配置（linear/twophase × 12 种配对相位 × 朝向收敛点 × "
                          "错峰幅度）中 10 组通过，取最小余量最大的 linear+相位2+"
                          "settle0.5+stagger0.30（逐帧余量 +40.5/+41.5/+37.4/+21.9/"
                          "+10.1/+8.0 px）",
        },
        "units": [{"unit": i + 1, "start_px": [round(x, 2) for x in st[i]],
                   "target_px": [round(x, 2) for x in tg[i]],
                   "start_angle_deg": round(i * (360.0 / N) + RING_PHASE, 1),
                   "travel_px": round(math.dist(st[i], tg[i]), 2)}
                  for i in range(N)],
        "per_frame": [{"frame": i + 1, "t": round(t, 3), "u": round(smooth(t), 4),
                       "units": units_at(t)} for i, t in enumerate(ts)],
        "cover": {"canvas": [CW, CH], "background": "#07101F",
                  "diagram_scale": COVER_SCALE, "diagram_offset_px": [COVER_OX, COVER_OY],
                  "swarm_t": COVER_T, "ghost": "目标塔形以 %s 空心轮廓提示，"
                  "12 条 #1B3A56 引线表示各单元从中段到目标格心的轨迹方向" % GHOST_BORDER,
                  "units": units_at(COVER_T, COVER_SCALE, COVER_OX, COVER_OY)},
    }
    (OUT / "frame-data.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print("frames", FRAMES, "units", N, "t", [round(x, 2) for x in ts],
          "| 最小中心距", [min_gap(t) for t in ts],
          "| 最大行程 px", round(max(u["travel_px"] for u in data["units"]), 1))


if __name__ == "__main__":
    main()
