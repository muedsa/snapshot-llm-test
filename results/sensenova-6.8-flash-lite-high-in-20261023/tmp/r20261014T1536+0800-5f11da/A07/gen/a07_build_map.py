"""A07 交付图 1：1600×1000 非地理地铁示意图 network-map。

几何与站序全部来自 tmp/<rid>/A07/model.json（该模型已断言：18 段全部为
0°/45°/90°、不同线路严格内部交叉 0 处、无线路穿过非本线车站、换乘站折线
在共享站相遇）。本脚本不改动几何，只负责排版与渲染。

要求覆盖：
  * 颜色 + 线路字母双编码（线上字母角标 + 图例）
  * 16 站编号与站名完整（标签 20px）
  * 折线，转折 45°/90°
  * 单纯交叉不读成换乘（几何上已保证 0 处，图上换乘站另有深色加粗圈标记）
  * 每站无障碍状态标注 + 图例
  * 明确标注「非地理示意图」
路径相对总任务根。用法：python -I tmp/<rid>/A07/gen/a07_build_map.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a07_io as IO  # noqa: E402
import a07_style as ST  # noqa: E402

W, H = 1600, 1000

# 版面分区
MAP_BOX = (40.0, 130.0, 1136.0, 716.0)        # x, y, w, h
LEG_BOX = (1204.0, 130.0, 356.0, 716.0)
NOTE_BOX = (40.0, 864.0, 1520.0, 120.0)

# 站标签方向与水平微调（逐站避让线路与相邻标签，均为目视+几何核对后确定）
LABEL_SIDE = {
    "S01": ("down", 0), "S02": ("up", 0), "S03": ("down", 0),
    "S04": ("up", 55), "S05": ("down", 52), "S06": ("up", -22),
    "S12": ("right", 0), "S16": ("left", 0),
    "S07": ("down", 0), "S08": ("up", 55), "S15": ("down", 0),
    "S14": ("down", 0), "S13": ("down", 0),
    "S09": ("left", 0), "S10": ("left", 0), "S11": ("left", 0),
}

# 查询编号角标位置（在对应站标记旁，方向避开该站标签）
Q_TAG = {
    "S01": ("q", -73, -19), "S11": ("q", 26, -19),
    "S13": ("q", -73, -19), "S12": ("q", -73, -19),
    "S07": ("q", -73, -19), "S16": ("q", 26, -19),
}

# 线路字母角标：置于线路「肩部」，不压住折线（避免被误读成换乘/断点）
LETTER_CHIP = {
    "R": (630.0, 358.0),
    "B": (1044.0, 360.0),
    "G": (360.0, 556.0),
}


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    model = json.loads((IO.dirs()[1] / "model.json").read_text(encoding="utf-8"))
    LINES = model["lines"]                      # dict: id → {color, letter, name_cn}
    stations = list(model["stations"].values())  # list of station dicts
    segs = model["geometry"]["segments"]

    L: list[str] = []
    L += ST.canvas_open(W, H)

    # ---------------- 页眉 ----------------
    L.append(ST.txt(44, 22, "虚构城市 · 非地理地铁示意图", 30, ST.INK, True))
    L.append(ST.txt(46, 70,
                    "16 站 · 3 条线路 · 16 条站间边（相邻站双向可乘，各边耗时相同）",
                    20, ST.INK2))
    frag, pw, ph = ST.pill(W - 44 - ST.text_w("非地理示意图 · 不按真实比例", 20) - 28,
                           40, "非地理示意图 · 不按真实比例", 20, ST.RULE_WARN_TXT,
                           ST.RULE_WARN, border="1 SOLID #F59E0B")
    L.append(frag)
    L.append(ST.box(40, 112, W - 80, 1, "#E2E8F0"))

    # ---------------- 地图面板 ----------------
    mx, my, mw, mh = MAP_BOX
    L.append(ST.frame(mx, my, mw, mh))
    frag, pw, ph = ST.pill(mx + 24, my + mh - 62, "示意图 · NOT TO SCALE", 20,
                           "#64748B", "#F1F5F9", radius=8, border="1 SOLID #CBD5E1")
    L.append(frag)

    # ---------------- 线路（先画线路，后画标记与标签） ----------------
    for s in segs:
        p1, p2 = s["p1"], s["p2"]
        L.append(ST.seg((p1[0], p1[1]), (p2[0], p2[1]), LINES[s["line"]]["color"]))

    # 线路字母角标：线路色底 + 白色字母（颜色+字母双编码）
    for lid, (cx, cy) in LETTER_CHIP.items():
        L.append(ST.badge(cx, cy, LINES[lid]["letter"], LINES[lid]["color"], 32, 20))

    # ---------------- 站标记 ----------------
    for s in stations:
        sid, cx, cy = s["id"], float(s["x"]), float(s["y"])
        tr = s["is_transfer"]
        ring = ST.TRANSFER_RING if tr else LINES[s["lines"][0]]["color"]
        L.append(ST.marker(cx, cy, s["accessible"], tr, ring))

    # ---------------- 站标签 ----------------
    for s in stations:
        sid = s["id"]
        side, nudge = LABEL_SIDE[sid]
        L.append(ST.label(float(s["x"]), float(s["y"]), sid, s["name"],
                          s["accessible"], side, nudge))

    # ---------------- 查询角标 ----------------
    for s in stations:
        sid = s["id"]
        if sid not in Q_TAG:
            continue
        _, dx, dy = Q_TAG[sid]
        qid = next(q["query_id"] for q in model["queries"]
                   if sid in (q["from"], q["to"]))
        L.append(ST.tag(float(s["x"]) + dx, float(s["y"]) + dy, qid))

    # ---------------- 图例 ----------------
    lx, ly, lw_, lh_ = LEG_BOX
    L.append(ST.frame(lx, ly, lw_, lh_))
    ip = lx + 24                       # 内边距
    y = ly + 22
    L.append(ST.txt(ip, y, "图例", 26, ST.INK, True))
    y = ly + 76
    L.append(ST.box(ip, y, lw_ - 48, 1, "#E2E8F0"))
    y += 18
    L.append(ST.txt(ip, y, "线路 · 颜色 + 字母双编码", 20, ST.INK2, True))

    for lid in ("R", "B", "G"):
        y += 54
        ln = LINES[lid]
        st_ids = [s["id"] for s in stations if lid in s["lines"]]
        n_st = len(st_ids)
        L.append(ST.badge(ip + 16, y + 16, ln["letter"], ln["color"], 32, 20))
        L.append(ST.txt(ip + 46, y, ln["name_cn"], 22, ST.INK, True))
        L.append(ST.txt(ip + 46, y + 27,
                        f"{n_st} 站 · {n_st - 1} 区间", 17, ST.INK3))

    y += 52
    L.append(ST.box(ip, y, lw_ - 48, 1, "#E2E8F0"))
    y += 18
    L.append(ST.txt(ip, y, "车站标记", 20, ST.INK2, True))

    # 单线站样例
    y += 42
    L.append(ST.marker(ip + 14, y + 14, True, False, LINES["R"]["color"]))
    L.append(ST.txt(ip + 44, y + 2, "单线站：圈色 = 所属线路", 20, ST.INK, True))
    # 换乘站样例
    y += 48
    L.append(ST.marker(ip + 17, y + 17, True, True, ST.TRANSFER_RING))
    L.append(ST.txt(ip + 50, y + 2, "换乘站：深色加粗圈", 20, ST.INK, True))
    L.append(ST.txt(ip + 50, y + 29, "（两条线路的共享站）", 17, ST.INK3))

    y += 62
    L.append(ST.box(ip, y, lw_ - 48, 1, "#E2E8F0"))
    y += 18
    L.append(ST.txt(ip, y, "无障碍状态（每站均已标注）", 20, ST.INK2, True))

    y += 44
    L.append(ST.marker(ip + 14, y + 14, True, False, "#64748B"))
    L.append(ST.txt(ip + 46, y + 2, "青核 = 具备无障碍设施", 20, ST.ACC_YES, True))
    y += 48
    L.append(ST.marker(ip + 14, y + 14, False, False, "#64748B"))
    L.append(ST.txt(ip + 46, y + 2, "灰核 = 不具备", 20, ST.ACC_NO_TXT, True))

    y += 42
    L.append(ST.txt(ip, y, "不具备的站可以乘车途经，", 17, "#B91C1B", True))
    L.append(ST.txt(ip, y + 24, "但不可作为起点、终点或换乘站。", 17, "#B91C1B", True))

    # ---------------- 底部说明 ----------------
    nx, ny, nw, nh = NOTE_BOX
    L.append(ST.box(nx, ny, nw, nh, ST.RULE_WARN, 12,
                    "1 SOLID " + ST.RULE_WARN_EDGE))
    L.append(ST.txt(nx + 26, ny + 20,
                    "注意：本图为非地理示意图——站距、方位与线条走向均不代表真实空间关系，"
                    "仅表达线路拓扑与换乘关系；所有线路均为折线，转折角度为 45° 或 90°。",
                    20, ST.RULE_WARN_TXT, True))
    L.append(ST.txt(nx + 26, ny + 58,
                    "换乘 = 改变乘坐线路（第一次上车不计）；最短旅程按 "
                    "(最少站间边数, 最少换乘) 的字典序选取，站数不等于区间数。",
                    20, "#78350F"))
    L.append(ST.txt(nx + 26, ny + 92,
                    "图上 Q1–Q3 角标标出三组查询的起终点；普通旅程与无障碍判定见 "
                    "travel-card.png，完整站序与线路段见 routes.json。",
                    20, "#78350F"))

    L += ST.canvas_close()
    dsl = "\n".join(L) + "\n"
    print(f"DSL {len(dsl)} 字符, {dsl.count('<Positioned')} Positioned")

    rec = IO.submit(dsl, label="A07 示意图 · 1600x1000 第四版（站标签两行均 20px）",
                    rid="req-a07-map-v4", dsl_version="v4",
                    out_png="network-map.png", out_dsl="network-map.snapshot",
                    kind="render")
    print("HTTP", rec["http_status"], "bytes", rec["response_bytes"],
          "ct", rec["content_type"])
    if rec["error_summary"]:
        print("ERROR", rec["error_summary"])
        print((rec.get("_error_json") or "")[:900])
        return

    print("输出 →", (IO.dirs()[0] / "network-map.png").relative_to(IO.ROOT))


if __name__ == "__main__":
    main()
