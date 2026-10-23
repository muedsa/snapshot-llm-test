"""A07 交付图 2：720x1280 旅行卡 travel-card。

三条普通旅程（Q1/Q2/Q3）按 (最少站间边数, 最少换乘) 的字典序给出，逐条列出
站序、线路段、边数与换乘次数，并判定其能否作为无障碍旅程；普通旅程不满足
无障碍约束时（Q2）另给出满足约束的最短无障碍旅程。

数据全部来自 tmp/<rid>/A07/model.json 的 queries 节点，本脚本不重算路由。
视觉系统与 network-map 共用 a07_style（同背景、同面板、同线宽、同圆点、同色板）；
排版为纵向卡片分区，与示意图「地图面板 + 右侧图例」不同。全部正文 >= 20px。

线路条布局（高 108，两端各内缩 42 以免首末站名越出卡片）：
  y0+1  .. y0+38   换乘标记（仅换乘站）
  y0+45 .. y0+71   线路字母角标（d=26）
  y0+52 .. y0+64   线路色条（lw=12）
  y0+74 .. y0+106  站名 20px

用法：python -I tmp/<rid>/A07/gen/a07_build_card.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a07_io as IO  # noqa: E402
import a07_style as ST  # noqa: E402

# ---------------- 版面常量（高度预算全部由这些量相加得出） ----------------
W, H = 720, 1280
SIDE = 24.0
FRAME_W = W - SIDE * 2                    # 672
PAD = 14.0                                # 卡片内边距
INNER_W = FRAME_W - PAD * 2               # 644
FRAME_GAP = 12.0
HEAD_Y0 = 122.0
HEAD_H = 66.0                             # 卡头（Q 徽标 48 高）
GAP_A = 8.0                               # 卡头 → 统计行
STATS_H = 27.0
GAP_B = 6.0                               # 统计行 → 线路条
STRIP_H = 108.0
EXTRA_GAP = 10.0                          # 分隔线前的空档
DIV_GAP = 8.0
LINE_H = 27.0
LINE_GAP = 22.0
STRIP2_GAP = 20.0
STRIP_INSET = 42.0                        # 线路条两端内缩（站名不越出卡片）
STRIP_W = INNER_W - STRIP_INSET * 2       # 560
FOOT_TOP = 1104.0
FOOT_H = 152.0

ACC_YES_BG = "#CCFBF1"
ACC_NO_BG = "#FEE2E2"


def line_at(route: dict) -> dict[str, str]:
    """每个站在该条旅程中的乘车线路（用于圆点描边）。

    换乘站在前后两段各出现一次，描边一律改用深色圈，此处取值不影响结果。
    """
    out: dict[str, str] = {}
    for seg in route["segments"]:
        for sid in seg["stations"]:
            out[sid] = seg["line"]
    return out


def route_strip(L: list[str], x0: float, y0: float, w: float,
                route: dict, stations: dict, LINES: dict) -> None:
    """在 (x0, y0, w, STRIP_H) 内画一条旅程的线路条。

    绘制顺序决定遮挡：色条先画，圆点盖住接缝（Stack 后画者在上）。
    字母角标取段的中点；段含偶数个区间时中点正好落在某站上，此时右移半格，
    避免角标压住圆点。
    """
    st_ids = route["stations"]
    n = len(st_ids)
    mid = y0 + 58.0
    xs = [x0 + w * i / (n - 1) for i in range(n)]
    transfers = set(route["transfer_stations"])
    lay = line_at(route)

    for seg in route["segments"]:
        lid = seg["line"]
        i0 = st_ids.index(seg["stations"][0])
        i1 = st_ids.index(seg["stations"][-1])
        m_i = (i0 + i1) / 2.0
        if abs(m_i - round(m_i)) < 1e-9:
            m_i += 0.5
        L.append(ST.hseg(xs[i0], xs[i1], mid, LINES[lid]["color"], lw=12.0))
        L.append(ST.badge(x0 + w * m_i / (n - 1), mid, LINES[lid]["letter"],
                          LINES[lid]["color"], 26, 20, radius=8))

    for i, sid in enumerate(st_ids):
        tr = sid in transfers
        ring = ST.TRANSFER_RING if tr else LINES[lay[sid]]["color"]
        L.append(ST.marker(xs[i], mid, stations[sid]["accessible"], tr, ring,
                           d=30.0 if tr else 24.0,
                           bd=4.0 if tr else 3.0,
                           inner=12.0 if tr else 10.0))

    for i, sid in enumerate(st_ids):
        L.append(ST.txt_c(xs[i], y0 + 90.0, f"{sid} {stations[sid]['name']}",
                          20, ST.INK, True))
        if sid in transfers:
            pw = ST.text_w("换乘", 20) + 14
            L.append(P(xs[i] - pw / 2, y0 + 1, "换乘", 20, "#FFFFFF",
                       ST.TRANSFER_RING, pad_x=7, pad_y=4, radius=8))


def stats(route: dict, stations: dict) -> str:
    parts = [f"{route['intervals']} 个站间边", f"{route['transfers']} 次换乘"]
    ts = route["transfer_stations"]
    parts.append("换乘站：" + "、".join(f"{s} {stations[s]['name']}"
                                      for s in ts) if ts else "全程同一条线路")
    return "  ·  ".join(parts)


def pill_w(s: str, size: float = 20.0, pad_x: float = 13.0) -> float:
    """与 ST.pill 同公式的宽度（右对齐定位需要先知道宽度）。"""
    return ST.text_w(s, size) + pad_x * 2


def P(left, top, s, size=20.0, fg=ST.INK, bg=ST.PANEL, pad_x=14.0,
      pad_y=8.0, radius=None, border=None) -> str:
    """ST.pill 只取片段（ST.pill 返回 (片段, 宽, 高) 三元组）。"""
    return ST.pill(left, top, s, size, fg, bg, pad_x=pad_x, pad_y=pad_y,
                   radius=radius, border=border)[0]


def frame_height(q: dict) -> float:
    """一张旅程卡的高度（由版面常量相加得出）。

    校验脚本 a07_inspect_card 与 routes.json 生成器都从这里取，避免各算一套。
    普通旅程与无障碍旅程站序/换乘不同时，多出说明行与第二条线路条。
    """
    h = PAD + HEAD_H + GAP_A + STATS_H + GAP_B + STRIP_H
    if not same_route(q):
        h += EXTRA_GAP + 1 + DIV_GAP + LINE_H + LINE_GAP + LINE_H \
            + STRIP2_GAP + STRIP_H
    return h + PAD


def same_route(q: dict) -> bool:
    """普通旅程与无障碍旅程是否完全一致（站序与换乘次数）。"""
    normal = q["normal"]
    acc = q["accessible"]
    return normal["stations"] == acc["stations"] and \
        normal["transfers"] == acc["transfers"]


def journey(L: list[str], y0: float, q: dict, stations: dict,
            LINES: dict) -> float:
    """画一张旅程卡；返回卡片高度。"""
    h = frame_height(q)
    same = same_route(q)

    x = SIDE
    L.append(ST.frame(x, y0, FRAME_W, h))

    fx = x + PAD
    fy = y0 + PAD

    # 卡头：Q 徽标 + 起终点 + 无障碍判定
    L.append(ST.badge(fx + 24, fy + 24, q["query_id"], ST.TRANSFER_RING,
                      48, 24, radius=12))
    head = f"{q['from']} {stations[q['from']]['name']}  →  " \
           f"{q['to']} {stations[q['to']]['name']}"
    L.append(ST.txt(fx + 66, fy + 15, head, 20, ST.INK, True))

    right = x + FRAME_W - PAD
    if same:
        txt_ = "可作无障碍旅程"
        L.append(P(right - pill_w(txt_), fy + 5, txt_, 20, ST.ACC_YES,
                   ACC_YES_BG, radius=8, border="1 SOLID " + ST.ACC_YES))
    else:
        txt_ = "不可作无障碍旅程"
        L.append(P(right - pill_w(txt_), fy + 5, txt_, 20,
                   ST.ACC_NO_TXT, ACC_NO_BG, radius=8,
                   border="1 SOLID " + ST.ACC_NO_TXT))

    y = fy + HEAD_H + GAP_A
    L.append(ST.txt(fx, y, stats(normal, stations), 20, ST.INK2))
    route_strip(L, fx + STRIP_INSET, y + STATS_H + GAP_B, STRIP_W,
                normal, stations, LINES)

    if not same:
        sy = y + STATS_H + GAP_B + STRIP_H + EXTRA_GAP
        L.append(ST.box(fx, sy, INNER_W, 1, "#E2E8F0"))
        sy += 1 + DIV_GAP
        L.append(ST.txt(fx, sy,
                        f"普通换乘站 "
                        + " ".join(f"{s} {stations[s]['name']}"
                                   for s in normal["transfer_stations"])
                        + " 不具备无障碍设施，同边数下需多一次换乘。",
                        20, ST.ACC_NO_TXT, True))
        sy += LINE_GAP + LINE_H
        L.append(ST.txt(fx, sy,
                        f"无障碍最短：{acc['intervals']} 个站间边 · "
                        f"{acc['transfers']} 次换乘（换乘站均可无障碍）",
                        20, ST.ACC_YES, True))
        sy += STRIP2_GAP + LINE_H
        route_strip(L, fx + STRIP_INSET, sy, STRIP_W, acc, stations, LINES)

    return h


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    _, tmp = IO.dirs()
    model = json.loads((tmp / "model.json").read_text(encoding="utf-8"))
    LINES = model["lines"]
    stations = model["stations"]
    queries = model["queries"]

    L: list[str] = []
    L += ST.canvas_open(W, H)

    # ---------------- 页眉 ----------------
    L.append(ST.txt(32, 24, "旅行卡 · 三条最短旅程", 30, ST.INK, True))
    L.append(ST.txt(34, 74,
                    "虚构城市 · 最少站间边数优先，边数相同再取最少换乘",
                    20, ST.INK2))
    L.append(P(W - SIDE - pill_w("普通旅程 × 3"), 34,
               "普通旅程 × 3", 20, "#FFFFFF", ST.TRANSFER_RING,
               radius=8))
    L.append(ST.box(SIDE, 108, FRAME_W, 1, "#E2E8F0"))

    # ---------------- 三张旅程卡 ----------------
    y = HEAD_Y0
    for q in queries:
        y += journey(L, y, q, stations, LINES) + FRAME_GAP

    # ---------------- 底部说明 ----------------
    fy = FOOT_TOP
    L.append(ST.box(SIDE, fy, FRAME_W, FOOT_H, ST.RULE_WARN, 12,
                    "1 SOLID " + ST.RULE_WARN_EDGE))
    lines = [
        ("换乘 = 改变乘坐线路，第一次上车不计；站数 ≠ 站间边数。", ST.RULE_WARN_TXT, True),
        ("青核 = 具备无障碍设施；灰核 = 不具备。", "#78350F", True),
        ("不具备的站可以乘车途经，但不可作为起点、终点或换乘站。", "#B91C1B", True),
        ("完整站序见 routes.json；拓扑见 network-map.png。", "#78350F", False),
    ]
    for i, (s, col, bold) in enumerate(lines):
        L.append(ST.txt(SIDE + 22, fy + 22 + i * 28, s, 20, col, bold))

    L += ST.canvas_close()
    dsl = "\n".join(L) + "\n"
    print(f"DSL {len(dsl)} 字符, {dsl.count('<Positioned')} Positioned")
    print(f"三卡占用 {y - FRAME_GAP - HEAD_Y0:.1f}px，末卡底 {y - FRAME_GAP:.1f}"
          f"，页脚顶 {FOOT_TOP:g}")

    rec = IO.submit(dsl, label="A07 旅行卡 · 720x1280 第二版（线路条内缩/换乘标签上移）",
                    rid="req-a07-card-v2", dsl_version="v2",
                    out_png="travel-card.png", out_dsl="travel-card.snapshot",
                    kind="render")
    print("HTTP", rec["http_status"], "bytes", rec["response_bytes"],
          "ct", rec["content_type"])
    if rec["error_summary"]:
        print("ERROR", rec["error_summary"])
        print((rec.get("_error_json") or "")[:900])
        return
    print("输出 →", (IO.dirs()[0] / "travel-card.png").relative_to(IO.ROOT))


if __name__ == "__main__":
    main()
