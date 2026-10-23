"""A07 交付图 2（travel-card.png）的独立像素校验。

期望值只从 model.json 重新推导；排版常量从 a07_build_card 导入（那是排版决策，
不属于模型数据）。校验对象是实际渲染的 PNG，因此若版面算错，检查会直接失败。

检查项（编号与 task-metrics.json 的 checks 字段对应）：
  D1 画布 720x1280
  D2 DSL 全部文字字号 >= 20（手机正文要求）
  D3 每条线路条上每个站间边的色条颜色 = 该段所属线路色（无他线色混入）
  D4 每个站圆点：核色 = 无障碍状态色；外圈 = 换乘深圈 / 所属线路色
  D5 每个线路段的字母角标位于两站之间（不压圆点），颜色为本线色
  D6 换乘站有「换乘」标记，非换乘站没有
  D7 每个站名下有墨迹（站名实际渲染出来）
  D8 同一条线路条内的站名区块互不重叠，且全部落在卡片框内（未被裁切）
  D9 卡头无障碍判定标 = 该查询的判定结果
  D10 页脚区块内有墨迹，且三张旅程卡与页脚不重叠

用法：python -I tmp/<rid>/A07/gen/a07_inspect_card.py
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a07_build_card as BC    # noqa: E402  仅取排版常量，不执行 main
import a07_io as IO            # noqa: E402
import a07_style as ST         # noqa: E402

from PIL import Image as PILImage  # noqa: E402

GATE_NORM, GATE_T, GATE_RESID = 60.0, 0.6, 25.0


def color_gate(im, hexc, resid_lim=GATE_RESID, t_lim=GATE_T):
    c = np.array([int(hexc[1:3], 16), int(hexc[3:5], 16), int(hexc[5:7], 16)], float)
    w = 255.0 - c
    v = 255.0 - im.astype(float)
    t = np.clip(np.sum(v * w, axis=2) / float(np.dot(w, w)), 0.0, 1.0)
    resid = np.linalg.norm(v - t[..., None] * w, axis=2)
    return (np.linalg.norm(v, axis=2) > GATE_NORM) & (t >= t_lim) & (resid < resid_lim)


def tight(im, hexc):
    """只认纯色块内部像素（残差 < 14），用于「是否有他色侵入」。"""
    return color_gate(im, hexc, resid_lim=14.0, t_lim=0.75)


def make_clamp(lim):
    def clamp(v: int) -> int:
        return max(0, min(lim - 1, v))
    return clamp


def rect_sl(l, t, w, h, shape2):
    H, W = shape2
    x0 = max(0, int(math.floor(l)))
    y0 = max(0, int(math.floor(t)))
    x1 = min(W, int(math.ceil(l + w)) + 1)
    y1 = min(H, int(math.ceil(t + h)) + 1)
    return y0, max(y1, y0), x0, max(x1, x0)


def line_at(route):
    out = {}
    for seg in route["segments"]:
        for sid in seg["stations"]:
            out[sid] = seg["line"]
    return out


def frame_height(q) -> float:
    extra = 0.0
    if not (q["normal"]["stations"] == q["accessible"]["stations"]
            and q["normal"]["transfers"] == q["accessible"]["transfers"]):
        extra = BC.EXTRA_GAP + 1 + BC.DIV_GAP + BC.LINE_H + BC.LINE_GAP \
            + BC.LINE_H + BC.STRIP2_GAP + BC.STRIP_H
    return (BC.PAD + BC.HEAD_H + BC.GAP_A + BC.STATS_H + BC.GAP_B
            + BC.STRIP_H + extra + BC.PAD)


def strip_geometry(model):
    """重算每条线路条的位置（y0、x0、宽、色条中线）。"""
    out, y = [], BC.HEAD_Y0
    for q in model["queries"]:
        fy = y + BC.PAD
        strips = [("normal", fy + BC.HEAD_H + BC.GAP_A + BC.STATS_H + BC.GAP_B)]
        if len(strips) == 1 and not (q["normal"]["stations"]
                                     == q["accessible"]["stations"]
                                     and q["normal"]["transfers"]
                                     == q["accessible"]["transfers"]):
            s2 = (strips[0][1] + BC.STRIP_H + BC.EXTRA_GAP + 1 + BC.DIV_GAP
                  + BC.LINE_H + BC.LINE_GAP + BC.LINE_H + BC.STRIP2_GAP)
            strips.append(("accessible", s2))
        for kind, top in strips:
            out.append({"query": q["query_id"], "kind": kind, "top": top,
                        "x0": BC.SIDE + BC.PAD + BC.STRIP_INSET, "w": BC.STRIP_W,
                        "mid": top + 58.0})
        y += frame_height(q) + BC.FRAME_GAP
    return out, y - BC.FRAME_GAP


def verdict_same(q) -> bool:
    return (q["normal"]["stations"] == q["accessible"]["stations"]
            and q["normal"]["transfers"] == q["accessible"]["transfers"])


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    out, tmp = IO.dirs()
    model = json.loads((tmp / "model.json").read_text(encoding="utf-8"))
    LINES = model["lines"]
    stations = model["stations"]
    png = out / "travel-card.png"
    dsl = (out / "travel-card.snapshot").read_text(encoding="utf-8")
    im = np.asarray(PILImage.open(png).convert("RGB"))
    rc, cc = make_clamp(im.shape[0]), make_clamp(im.shape[1])
    S2 = im.shape[:2]

    ink = np.linalg.norm(255.0 - im.astype(float), axis=2) > 120
    T = {lid: tight(im, LINES[lid]["color"]) for lid in ("R", "B", "G")}
    M_RING = tight(im, ST.TRANSFER_RING)
    M_YES = tight(im, ST.ACC_YES)
    M_NO = tight(im, ST.ACC_NO)
    M_REDTXT = tight(im, "#B91C1B")

    results = []
    def check(cid, ok, detail):
        results.append((cid, bool(ok), detail))

    strips, last_bottom = strip_geometry(model)
    qby = {q["query_id"]: q for q in model["queries"]}

    # ---- D1 尺寸 ----
    check("D1 canvas 720x1280", im.shape[1] == 720 and im.shape[0] == 1280,
          f"{im.shape[1]}x{im.shape[0]}")

    # ---- D2 字号 ----
    sizes = [int(v) for v in re.findall(r'fontSize="(\d+)"', dsl)]
    check("D2 DSL 文字字号 >= 20", bool(sizes) and min(sizes) >= 20,
          f"共 {len(sizes)} 个文本，最小 {min(sizes)}px" if sizes else "无文本")

    bar_bad, dot_bad, badge_bad, tag_bad, lbl_bad, lbl_ovl = [], [], [], [], [], []
    n_edges, n_dots, n_badges, n_labels = 0, 0, 0, 0

    for g in strips:
        q = qby[g["query"]]
        route = q[g["kind"]]
        st_ids = route["stations"]
        n = len(st_ids)
        xs = [g["x0"] + g["w"] * i / (n - 1) for i in range(n)]
        mid = int(round(g["mid"]))
        trset = set(route["transfer_stations"])
        lay = line_at(route)
        tag = f"{g['query']}/{g['kind']}"

        # D3 每个站间边：色条颜色正确且无他线色
        for seg in route["segments"]:
            n_edges += 1
            i0 = st_ids.index(seg["stations"][0])
            i1 = st_ids.index(seg["stations"][-1])
            cx = int(round((xs[i0] + xs[i1]) / 2))
            found = False
            for k in (-10, 0, 10):
                if any(T[seg["line"]][rc(mid + oy), cc(cx + k + ox)]
                       for oy in range(-4, 5) for ox in range(-4, 5)):
                    found = True
                    break
            if not found:
                bar_bad.append(f"{tag} {seg['line']} 无本线色")
                continue
            for other in ("R", "B", "G"):
                if other == seg["line"]:
                    continue
                b0 = rect_sl(cx - 5, mid - 5, 11, 11, S2)
                if T[other][b0[0]:b0[1], b0[2]:b0[3]].sum() > 0:
                    bar_bad.append(f"{tag} {seg['line']} 边混入 {other}")

        # D4 圆点核色与外圈
        for i, sid in enumerate(st_ids):
            n_dots += 1
            tr = sid in trset
            d = 30.0 if tr else 24.0
            bx, by = int(round(xs[i])), mid
            mcore = M_YES if stations[sid]["accessible"] else M_NO
            if not all(mcore[by + oy, bx + ox] for oy in (-1, 0, 1) for ox in (-1, 0, 1)):
                dot_bad.append(f"{tag} {sid} 核色")
            mr = M_RING if tr else T[lay[sid]]
            r = d / 2 - 2.0
            hits = sum(
                1 for a in range(0, 360, 45)
                if mr[rc(by + int(round(r * math.sin(math.radians(a))))),
                     cc(bx + int(round(r * math.cos(math.radians(a)))))] )
            if hits < 7:
                dot_bad.append(f"{tag} {sid} 外圈 {hits}/8")

        # D5 字母角标：位于两站之间，环上为本线色
        for seg in route["segments"]:
            n_badges += 1
            i0 = st_ids.index(seg["stations"][0])
            i1 = st_ids.index(seg["stations"][-1])
            m_i = (i0 + i1) / 2.0
            if abs(m_i - round(m_i)) < 1e-9:
                m_i += 0.5
            bx = g["x0"] + g["w"] * m_i / (n - 1)
            # 角标（d=26）与圆点（d=24/30）不得相碰：圆心距 >= 13+15+2
            gap = min(abs(bx - xk) for xk in xs)
            if gap < 30.0:
                badge_bad.append(f"{tag} {seg['line']} 与圆点相距 {gap:.1f} < 30")
                continue
            # 角标本体：26x26 本线色块 + 居中白字（比环取样更稳，避开圆角与字形）
            b0 = rect_sl(bx - 13, mid - 13, 26, 26, S2)
            fill = int(T[seg["line"]][b0[0]:b0[1], b0[2]:b0[3]].sum())
            cx0, cy0 = int(round(bx)) - 5, mid - 5
            center = im[rc(cy0):rc(cy0 + 10), cc(cx0):cc(cx0 + 10)]
            white = int((np.linalg.norm(255.0 - center.astype(float), axis=2) < 40).sum())
            if fill < 350:
                badge_bad.append(f"{tag} {seg['line']} 色块仅 {fill}px")
            elif white < 15:
                badge_bad.append(f"{tag} {seg['line']} 无白字（白 {white}px）")

        # D6 换乘标记
        pw = ST.text_w("换乘", 20) + 14
        th = 20 * 1.45 + 8
        for sid, bx_ in [(sid, xs[i]) for i, sid in enumerate(st_ids)
                         if sid in trset]:
            b0 = rect_sl(bx_ - pw / 2, g["top"] + 1, pw, th, S2)
            if M_RING[b0[0]:b0[1], b0[2]:b0[3]].sum() < 400:
                tag_bad.append(f"{tag} {sid} 缺少换乘标记")
        for i, sid in enumerate(st_ids):
            if sid in trset:
                continue
            b0 = rect_sl(xs[i] - pw / 2, g["top"] + 1, pw, th, S2)
            if M_RING[b0[0]:b0[1], b0[2]:b0[3]].sum() > 0:
                tag_bad.append(f"{tag} {sid} 误标换乘")

        # D7 / D8 站名
        rects = []
        for i, sid in enumerate(st_ids):
            n_labels += 1
            s = f"{sid} {stations[sid]['name']}"
            lw_ = ST.text_w(s, 20)
            l, t = xs[i] - lw_ / 2, g["top"] + 90 - 16
            rects.append((f"{tag} {sid}", l, t, lw_, 32.0))
            b0 = rect_sl(l, t, lw_, 32.0, S2)
            if ink[b0[0]:b0[1], b0[2]:b0[3]].sum() < 30:
                lbl_bad.append(f"{tag} {sid} 无墨迹")
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, b = rects[i], rects[j]
                if (a[1] < b[1] + b[3] - 2 and b[1] < a[1] + a[3] - 2
                        and a[2] < b[2] + b[4] - 2 and b[2] < a[2] + a[4] - 2):
                    lbl_ovl.append((a[0], b[0]))
        for a in rects:
            if not (a[1] >= BC.SIDE + 1 and a[1] + a[3] <= BC.SIDE + BC.FRAME_W - 1):
                lbl_bad.append(f"{a[0]} 越出卡片")

    check("D3 站间边色条 = 所属线路色且无他线混入", not bar_bad,
          f"{n_edges} 条站间边全部通过" if not bar_bad else f"异常 {bar_bad}")
    check("D4 圆点核色/外圈", not dot_bad,
          f"{n_dots} 个圆点全部一致" if not dot_bad else f"异常 {dot_bad}")
    check("D5 线路字母角标位于两站之间", not badge_bad,
          f"{n_badges} 个角标全部通过" if not badge_bad else f"异常 {badge_bad}")
    check("D6 换乘标记只在换乘站", not tag_bad,
          f"{len(strips)} 条线路条全部通过" if not tag_bad else f"异常 {tag_bad}")
    check("D7 站名有墨迹", not lbl_bad,
          f"{n_labels} 个站名全部渲染" if not lbl_bad else f"异常 {lbl_bad}")
    check("D8 站名区块不重叠且在卡内", not lbl_ovl,
          f"{n_labels} 个站名两两检查" if not lbl_ovl else f"重叠 {lbl_ovl}")

    # ---- D9 卡头无障碍判定标 ----
    verdict_bad, y = [], BC.HEAD_Y0
    for q in model["queries"]:
        fy = y + BC.PAD
        same = verdict_same(q)
        s = "可作无障碍旅程" if same else "不可作无障碍旅程"
        w = ST.text_w(s, 20) + 26
        b0 = rect_sl(BC.SIDE + BC.FRAME_W - BC.PAD - w, fy + 5, w, 37, S2)
        hit = (M_YES if same else M_REDTXT)[b0[0]:b0[1], b0[2]:b0[3]].sum()
        if hit < 120:
            verdict_bad.append(f"{q['query_id']} 判定标 {int(hit)}px")
        y += frame_height(q) + BC.FRAME_GAP
    check("D9 卡头无障碍判定标", not verdict_bad,
          "Q1/Q3 青色、Q2 红色，与 routes 一致" if not verdict_bad
          else f"异常 {verdict_bad}")

    # ---- D10 分区 ----
    fb = rect_sl(BC.SIDE + 22, BC.FOOT_TOP + 22, BC.FRAME_W - 44,
                 BC.FOOT_H - 44, S2)
    foot_ink = int(ink[fb[0]:fb[1], fb[2]:fb[3]].sum())
    check("D10 卡片/页脚分区", last_bottom <= BC.FOOT_TOP and foot_ink > 800,
          f"末卡底 {last_bottom:g} ≤ 页脚顶 {BC.FOOT_TOP:g}；页脚墨迹 {foot_ink}px")

    npass = sum(1 for _, ok, _ in results if ok)
    print(f"PNG {png.stat().st_size} B  尺寸 {im.shape[1]}x{im.shape[0]}")
    print(f"通过 {npass}/{len(results)}\n")
    for cid, ok, detail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {cid}  — {detail}")

    rep = {"image": str(png.relative_to(IO.ROOT)),
           "dsl": str((out / "travel-card.snapshot").relative_to(IO.ROOT)),
           "canvas": [im.shape[1], im.shape[0]],
           "checks": [{"id": c, "pass": ok, "detail": d} for c, ok, d in results],
           "passed": npass, "total": len(results)}
    (tmp / "inspect-card.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n校验报告 → tmp/{IO.TASK}/inspect-card.json")
    return 0 if npass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
