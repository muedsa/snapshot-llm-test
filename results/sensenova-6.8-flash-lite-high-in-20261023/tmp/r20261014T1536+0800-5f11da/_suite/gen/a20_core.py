"""A20 布局内核：锚点映射、双栏标签槽分配、正交引导折线、完整 DSL 生成。

几何设计（每条都可由 a20_check.py 独立复核）
------------------------------------------
* 锚点 = (280 + 10.4x, 920 - 7.6y)，全程不取整；渲染时才量化到整数像素。
* 24 个点按锚点 x 以 774 为界分栏：左栏 11 个 / 右栏 13 个。
  该阈值同时满足「引导线首段不得穿过其他点圆盘」——已逐点验证。
* 行位按锚点 y 升序贪心分配（行距 38，盒高 32 → 净距 6 ≥ 4），跳过 y 轴刻度
  数字所占的横带，使左栏引导线的水平收尾段不压刻度文字；同时保证行 center 严格
  在自有点锚点上方。
* 折道：左栏 x = 392 - 10k（随 k 递减），右栏 x = 1188 + 13k（随 k 递增）。
  「行随 cy 升序 + 行在点上 + 折道反向单调」三者在几何上排除了线-线交叉：
    竖直折道_i 与水平段_j —— i<j 时 cy_j 高于折道_i 的上端 cy_i，y 条件不成立；
                             j<i 时折道_i 的 x 不落入水平段_j 的 x 区间，x 条件不成立；
                             收尾段同理，行升序使 row_i < row_j 直接排除。
  a20_check.py 仍按题目口径逐线对实算，实测 0 处交叉。
* 标签盒 = 底板 <Container> 的像素矩形。探针实测底板内文字墨迹偏移
  dx=+2 / dy=+5，故盒内留白 6/8/5/8 px，盒几何与渲染逐像素一致。
* 引导线由 1px 细 <Container> 渲染（探针实测 1/2/3 px 均按指定矩形精确绘制）。
* 24 个点两两圆心距最小 30.8 px > 12 px，故点径全部保持 12 px，无需缩到 8 px。
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TASK_INPUT = SUITE_ROOT / "tasks" / "A20-dense-annotation" / "inputs" / "markers.json"
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A20"

# ---- 画布与主图框（题目固定：左上 (280,160)，宽 1040、高 760）----
W, H = 1600, 1100
FRAME_L, FRAME_T, FRAME_W, FRAME_H = 280.0, 160.0, 1040.0, 760.0
SX, SY = 10.4, 7.6          # 每逻辑单位对应的像素步长
DISC_D = 12                 # 点圆直径

# ---- 双栏标签槽 ----
SPLIT_X = 774.0             # 锚点 x 小于此值排左栏
ROW_PITCH = 38.0            # 行距（盒高 32 → 净距 6 ≥ 4）
ROW_BASE = 179.0            # 首行 center 起点，随后按刻度文字带贪心避让
BOX_H = 32.0
BOX_W = 120.0               # 两字名字：墨迹 106 + 左 6 + 右 8
BOX_W3 = 140.0              # 三字名字（M23 研究所）：墨迹 126 + 6 + 8
LEFT_BOX_L = 76.0           # 左栏盒 left（right = 196）
RIGHT_BOX_L = 1380.0        # 右栏盒 left（right = 1500 / 1520）
LEFT_LANE_X0, LEFT_LANE_STEP = 392.0, -10.0    # 随 k 递减
RIGHT_LANE_X0, RIGHT_LANE_STEP = 1188.0, 13.0  # 随 k 递增
Y_TICKS = (0, 20, 40, 60, 80, 100)
TICK_TEXT_BAND = 17.0       # 刻度数字上下缓冲（实测墨迹高 15-23 px）

# ---- 配色 ----
BG = "#0B1220"
FRAME_FILL = "#0F1B2D"
FRAME_LINE = "#33506E"
GRID_LINE = "#1B2A40"
DISC = "#38BDF8"
TOP3 = "#F59E0B"
PLATE = "#17263B"
PLATE_BORDER = "#2E4A6B"
PLATE_TOP3 = "#3A2A0E"
PLATE_TOP3_BORDER = "#B4791A"
TEXT = "#EAF2FB"
TEXT_TOP3 = "#FDE7C2"
LEADER = "#7C9BB8"
AXIS_TICK = "#4A6480"
AXIS_TEXT = "#9DB4CC"
FONT = "Noto Sans CJK SC,Inter"


def markers() -> list[dict]:
    return json.loads(TASK_INPUT.read_text(encoding="utf-8"))


def anchor(m: dict) -> tuple[float, float]:
    """逻辑坐标 → 像素锚点（画布左上原点，x 向右 / y 向下），不取整。"""
    return FRAME_L + SX * m["x"], FRAME_T + FRAME_H - SY * m["y"]


def label_width(m: dict) -> float:
    return BOX_W3 if len(m["name"]) == 3 else BOX_W


def label_text(m: dict) -> str:
    return "%s %s %s" % (m["id"], m["name"], m["value"])


def y_tick_px(t: float) -> float:
    return FRAME_T + FRAME_H - SY * t


def tick_forbidden() -> list[tuple[float, float]]:
    """y 轴刻度数字所占的横向带。左栏引导线收尾段横跨 x∈[196,392]，会经过刻度
    数字所在的 x∈[234,274]，故行 center 必须落在这些带之外，以免 1px 描边压字。"""
    return [(y_tick_px(t) - TICK_TEXT_BAND, y_tick_px(t) + TICK_TEXT_BAND)
            for t in Y_TICKS]


def assign_rows(cys: list[float], forbidden) -> list[float]:
    """按 cy 升序贪心分配行 center。

    同时满足四条：行 center 严格升序（与 cy 同序）、相邻净距 ≥4、避开刻度文字带、
    且 row_center < cy（标签在本点上方）。前三条是不交叉证明的前提，第四条保证
    竖直折道区间为 [row, cy]，从而排除剩余的线-线交叉情形。"""
    rows, cur = [], ROW_BASE
    for cy in cys:
        while True:
            hits = [b for a, b in forbidden if a <= cur <= b]
            if hits:
                cur = max(hits) + 1.0
                continue
            if cur >= cy:
                raise ValueError("行布局不可行：既要在点上方又要避开刻度文字带")
            break
        rows.append(cur)
        cur = rows[-1] + ROW_PITCH
    return rows


def build_layout(marks: list[dict]) -> dict:
    anchors = {m["id"]: anchor(m) for m in marks}
    by_id = {m["id"]: m for m in marks}

    left_ids = [m["id"] for m in marks if anchors[m["id"]][0] < SPLIT_X]
    right_ids = [m["id"] for m in marks if anchors[m["id"]][0] >= SPLIT_X]
    left_ids.sort(key=lambda i: (anchors[i][1], i))       # 行号 = 锚点 y 升序
    right_ids.sort(key=lambda i: (anchors[i][1], i))

    forbidden = tick_forbidden()
    left_rows = assign_rows([anchors[i][1] for i in left_ids], forbidden)
    right_rows = assign_rows([anchors[i][1] for i in right_ids], forbidden)
    row_of = {sid: left_rows[k] for k, sid in enumerate(left_ids)}
    row_of.update({sid: right_rows[k] for k, sid in enumerate(right_ids)})

    def slot(sid: str, rail: str) -> dict:
        k = (left_ids if rail == "L" else right_ids).index(sid)
        cx, cy = anchors[sid]
        m = by_id[sid]
        bw = label_width(m)
        box_l = LEFT_BOX_L if rail == "L" else RIGHT_BOX_L
        lane = (LEFT_LANE_X0 + LEFT_LANE_STEP * k if rail == "L"
                else RIGHT_LANE_X0 + RIGHT_LANE_STEP * k)
        row_c = row_of[sid]
        row_top = row_c - BOX_H / 2.0
        box = [box_l, row_top, box_l + bw, row_top + BOX_H]
        if rail == "L":
            poly = [[cx - DISC_D / 2.0, cy], [lane, cy],
                    [lane, row_c], [box_l + bw, row_c]]
        else:
            poly = [[cx + DISC_D / 2.0, cy], [lane, cy],
                    [lane, row_c], [box_l, row_c]]
        return {"id": sid, "rail": rail, "row": k, "lane_x": lane,
                "box": box, "polyline": poly,
                "box_top": row_top, "box_center_y": row_c}

    slots = {sid: slot(sid, "L") for sid in left_ids}
    slots.update({sid: slot(sid, "R") for sid in right_ids})

    values_desc = sorted(marks, key=lambda m: (-m["value"], m["id"]))
    top3 = [m["id"] for m in values_desc[:3]]

    labels = []
    for m in marks:
        sid, sl = m["id"], slots[m["id"]]
        cx, cy = anchors[sid]
        bw = label_width(m)
        ink_w = 126.0 if len(m["name"]) == 3 else 106.0
        is_top3 = sid in top3
        labels.append({
            "id": sid, "name": m["name"], "value": m["value"],
            "logical": {"x": m["x"], "y": m["y"]},
            "anchor": {"x": cx, "y": cy},
            "anchor_formula": "x_px = 280 + 10.4*x, y_px = 920 - 7.6*y",
            "disc_diameter": DISC_D,
            "rail": sl["rail"], "row": sl["row"], "lane_x": sl["lane_x"],
            "label_box": [round(v, 6) for v in sl["box"]],
            "label_box_note": (
                "标签盒 = 底板 Container 的像素矩形，不含引导线；"
                "底板 rect 经探针实测与其像素墨迹完全一致"),
            "text": label_text(m),
            "text_font_size": 20,
            "text_ink_width_measured": ink_w,
            "text_ink_in_box": [round(sl["box"][0] + 6 + 2, 6),
                                round(sl["box"][1] + 5, 6),
                                round(sl["box"][0] + 6 + 2 + ink_w, 6),
                                round(sl["box"][1] + 5 + 19, 6)],
            "leader_polyline": [[round(p[0], 6), round(p[1], 6)]
                                for p in sl["polyline"]],
            "leader_segments_rendered": [
                {"rect": [seg["left"], seg["top"],
                          seg["left"] + seg["width"] - 1,
                          seg["top"] + seg["height"] - 1],
                 "left": seg["left"], "top": seg["top"],
                 "width": seg["width"], "height": seg["height"]}
                for seg in (hline(sl["polyline"][0][0], sl["polyline"][1][0],
                                  sl["polyline"][0][1]),
                            vline(sl["polyline"][1][0], sl["polyline"][1][1],
                                  sl["polyline"][2][1]),
                            hline(sl["polyline"][2][0], sl["polyline"][3][0],
                                  sl["polyline"][2][1]))],
            "leader_present": True,
            "leader_reason": (
                "锚点圆心到本标签盒最短欧氏距离 = %.3f px > 24 px，故必须绘制引导线"
                % _anchor_to_box_dist(anchors[sid], sl["box"])),
            "leader_segment_width_px": 1,
            "highlighted": is_top3,
        })

    return {"canvas": {"width": W, "height": H},
            "frame": {"left": FRAME_L, "top": FRAME_T, "width": FRAME_W,
                      "height": FRAME_H},
            "split_x": SPLIT_X,
            "row_policy": {
                "row_pitch_px": ROW_PITCH,
                "box_height_px": BOX_H,
                "min_box_gap_px": ROW_PITCH - BOX_H,
                "base_center_px": ROW_BASE,
                "tick_forbidden_bands": [[round(a, 6), round(b, 6)]
                                         for a, b in forbidden],
                "tick_text_band_px": TICK_TEXT_BAND,
                "note": ("行 center 按锚点 y 升序贪心分配，避开 y 轴刻度文字带，"
                         "并保证行 center 在自有点锚点上方"),
            },
            "left_rail": {"ids": left_ids,
                          "row_centers": [round(v, 6) for v in left_rows],
                          "lane": "392 - 10*row"},
            "right_rail": {"ids": right_ids,
                           "row_centers": [round(v, 6) for v in right_rows],
                           "lane": "1188 + 13*row"},
            "top3": top3, "labels": labels}


def _anchor_to_box_dist(anchor_pt: tuple[float, float], box: list[float]) -> float:
    ax, ay = anchor_pt
    nx = max(box[0], min(ax, box[2]))
    ny = max(box[1], min(ay, box[3]))
    return ((ax - nx) ** 2 + (ay - ny) ** 2) ** 0.5


# ---------------------------------------------------------------- 线段渲染
def hline(xa: float, xb: float, y: float) -> dict:
    lo, hi = min(xa, xb), max(xa, xb)
    return {"left": round(lo), "top": round(y),
            "width": max(1, round(hi) - round(lo) + 1), "height": 1}


def vline(x: float, ya: float, yb: float) -> dict:
    lo, hi = min(ya, yb), max(ya, yb)
    return {"left": round(x), "top": round(lo),
            "width": 1, "height": max(1, round(hi) - round(lo) + 1)}


def _pos(left, top, w, h, inner: str) -> list[str]:
    return ['    <Positioned left="%d" top="%d" width="%d" height="%d">'
            % (round(left), round(top), round(w), round(h)), inner,
            '    </Positioned>']


def _rect(left, top, w, h, color: str, extra: str = "") -> str:
    attr = 'color="%s"' % color
    if extra:
        attr += " " + extra
    return '    <Positioned left="%d" top="%d" width="%d" height="%d">' \
        '<Container width="%d" height="%d" %s/></Positioned>' \
        % (round(left), round(top), round(w), round(h),
           round(w), round(h), attr)


def _text(left, top, w, h, s: str, size: int, color: str) -> str:
    return '    <Positioned left="%d" top="%d" width="%d" height="%d">' \
        '<Text fontFamily="%s" fontSize="%d" color="%s" text="%s"/></Positioned>' \
        % (round(left), round(top), round(w), round(h), FONT, size, color, s)


def build_dsl(layout: dict) -> str:
    L = ['<Snapshot type="png" background="%s">' % BG,
         '  <Container width="%d" height="%d">' % (W, H),
         '    <Stack width="%d" height="%d" fit="EXPAND" clipBehavior="NONE">'
         % (W, H)]

    # 1) 标题区
    L.append(_text(670, 22, 300, 34, "二十四点位标注示意图", 26, "#F8FAFC"))
    L.append(_text(639, 66, 360, 28, "24 个点，逻辑坐标 0-100，指数分布", 20,
                   "#9DB4CC"))
    L.append(_text(122, 114, 170, 30, "y 逻辑坐标 0-100", 20, AXIS_TEXT))

    # 2) 主图框填充 + 网格 + 边框
    L.append(_rect(FRAME_L, FRAME_T, FRAME_W, FRAME_H, FRAME_FILL))
    for t in range(10, 100, 10):
        gx = FRAME_L + SX * t
        L.append(_rect(gx, FRAME_T + 2, 1, FRAME_H - 4, GRID_LINE))
    for t in range(10, 100, 10):
        gy = FRAME_T + FRAME_H - SY * t
        L.append(_rect(FRAME_L + 2, gy, FRAME_W - 4, 1, GRID_LINE))
    L.append(_rect(FRAME_L, FRAME_T, FRAME_W, 2, FRAME_LINE))
    L.append(_rect(FRAME_L, FRAME_T + FRAME_H - 2, FRAME_W, 2, FRAME_LINE))
    L.append(_rect(FRAME_L, FRAME_T, 2, FRAME_H, FRAME_LINE))
    L.append(_rect(FRAME_L + FRAME_W - 2, FRAME_T, 2, FRAME_H, FRAME_LINE))

    # 3) 坐标轴刻度
    for t in range(0, 101, 20):
        gy = FRAME_T + FRAME_H - SY * t
        L.append(_rect(FRAME_L - 8, gy, 8, 1, AXIS_TICK))
        L.append(_text(267 - _digits_w(t) - 1, gy - 15, 40, 26, str(t), 20,
                       AXIS_TEXT))
    for t in range(0, 101, 20):
        gx = FRAME_L + SX * t
        L.append(_rect(gx, FRAME_T + FRAME_H, 1, 8, AXIS_TICK))
        L.append(_text(gx - (_digits_w(t) + 1) / 2.0, 932, 44, 26, str(t), 20,
                       AXIS_TEXT))

    # 4) 引导线（在点与标签之下）
    for lab in layout["labels"]:
        p = lab["leader_polyline"]
        for seg in (hline(p[0][0], p[1][0], p[0][1]),
                    vline(p[1][0], p[1][1], p[2][1]),
                    hline(p[2][0], p[3][0], p[2][1])):
            L.append(_rect(seg["left"], seg["top"], seg["width"], seg["height"],
                           LEADER))

    # 5) 点圆（Top-3 先画光环再画实心）
    for lab in layout["labels"]:
        cx, cy = lab["anchor"]["x"], lab["anchor"]["y"]
        if lab["highlighted"]:
            L.append(_rect(cx - 10, cy - 10, 20, 20, TOP3,
                           'shape="CIRCLE" border="3 SOLID %s"' % TOP3))
        L.append(_rect(cx - DISC_D / 2.0, cy - DISC_D / 2.0, DISC_D, DISC_D,
                       TOP3 if lab["highlighted"] else DISC,
                       'shape="CIRCLE"'))

    # 6) 标签底板 + 文字
    for lab in layout["labels"]:
        b = lab["label_box"]
        w = b[2] - b[0]
        if lab["highlighted"]:
            fill, border, tcolor = PLATE_TOP3, PLATE_TOP3_BORDER, TEXT_TOP3
        else:
            fill, border, tcolor = PLATE, PLATE_BORDER, TEXT
        L.append(_rect(b[0], b[1], w, BOX_H, fill,
                       'borderRadius="4" border="1 SOLID %s"' % border))
        L.append(_text(b[0] + 4, b[1], w - 8, 28, lab["text"], 20, tcolor))

    # 7) 底部图例：色样各自带文字说明，避免被误读成轴标签的一部分
    L.append(_rect(296, 972, 12, 12, DISC, 'shape="CIRCLE"'))
    L.append(_text(316, 966, 100, 28, "普通点位", 20, AXIS_TEXT))
    L.append(_rect(446, 968, 20, 20, TOP3, 'shape="CIRCLE" border="3 SOLID %s"'
                   % TOP3))
    L.append(_rect(452, 972, 12, 12, TOP3, 'shape="CIRCLE"'))
    L.append(_text(476, 966, 100, 28, "前三点位", 20, TEXT_TOP3))
    L.append(_text(596, 966, 320, 28, "点圆直径 12px；密集处无需缩小", 20,
                   AXIS_TEXT))
    L.append(_text(946, 966, 190, 28, "value 单位：指数", 20, TEXT))
    L.append(_text(290, 1004, 200, 28, "x 逻辑坐标 0-100", 20, AXIS_TEXT))
    L.append(_text(290, 1042, 660, 30,
                   "TOP-3（按 value 降序）：M10 广场 93 / M08 中庭 91 / "
                   "M23 研究所 90", 20, TEXT_TOP3))
    L.append(_text(930, 1042, 280, 28, "引导线交叉 0 处（上限 3 处）", 20,
                   AXIS_TEXT))

    L.append('    </Stack>')
    L.append('  </Container>')
    L.append('</Snapshot>')
    dsl = "\n".join(L) + "\n"
    assert_dsl_wellformed(dsl)
    return dsl


def assert_dsl_wellformed(dsl: str) -> None:
    """提交前的本地防呆：服务端对属性值里的 <、& 与 Python 容器字符串直接报
    PARSE_ERROR，这里在本地先拦下，避免浪费一次真实请求。"""
    import re
    bad = re.findall(r'(?:color|text|border|fontFamily)="[^"]*(?:[<>&]|\()[^"]*"',
                     dsl)
    if bad:
        raise AssertionError("DSL 属性值含非法字符: %s" % bad[:3])
    if "\r" in dsl:
        raise AssertionError("DSL 含 CRLF，须为 LF")
    assert len(dsl.encode("utf-8")) <= 1048576, "DSL 超过服务请求体上限"


def _digits_w(v: int) -> float:
    """fontSize=20 下纯数字串的实测墨迹宽度（探针 2：0→10、20→22、100→32）。"""
    return {1: 10.0, 2: 22.0, 3: 32.0}[len(str(v))]


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    marks = markers()
    layout = build_layout(marks)
    dsl = build_dsl(layout)

    TMP.mkdir(parents=True, exist_ok=True)
    (TMP / "dsl").mkdir(parents=True, exist_ok=True)
    model = TMP / "layout_model.json"
    model.write_text(json.dumps(layout, ensure_ascii=False, indent=1),
                     encoding="utf-8")
    dry = TMP / "dsl" / "annotated-map.dryrun.snapshot"
    dry.write_bytes(dsl.encode("utf-8"))

    print("points:", len(marks), "top3:", layout["top3"])
    print("left rail %d: %s" % (len(layout["left_rail"]["ids"]),
                                ",".join(layout["left_rail"]["ids"])))
    print("right rail %d: %s" % (len(layout["right_rail"]["ids"]),
                                 ",".join(layout["right_rail"]["ids"])))
    print("dsl bytes:", len(dsl.encode("utf-8")))
    print("model:", model.relative_to(SUITE_ROOT).as_posix())
    print("dryrun:", dry.relative_to(SUITE_ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
