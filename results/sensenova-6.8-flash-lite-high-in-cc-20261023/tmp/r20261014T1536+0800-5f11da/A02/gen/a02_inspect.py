"""A02 像素级自检 + 裁图。

启动基准：总任务根（cwd）。只读 outputs/<run_id>/A02/ 与 schedule-audit.json；
结果写 tmp/<run_id>/A02/inspect-report.json 与 crops/。

判据（都是「实际渲染出来的像素」，不是估算）：
  W1/M1  PNG 头 + 尺寸
  W2     三条泳道底带、午休带（带内无卡片 / 带内底色 / 带外是底带 / 两侧虚线）
  W3     15 张卡片左右缘 = X(start)/X(end)（±1.5px）：按卡片行做白色游程匹配，
         多卡、少卡、错位都会失败；卡片上下缘外侧是泳道底带
  W4     整点网格线、刻度线位置（最暗像素 vs 同泳道底带中位数）
  W5     每条 content_map 文本：墨迹存在；墨迹右缘距所属卡片内边 ≥2px（未被裁）；
         墨迹宽度 / 估算宽度 ≥ 阈值（CJK 字面窄于字距，阈值分档）
  W5b    同一张卡内各文本墨迹两两不重叠（间隔 ≥1px）
  W6/M3  页边距带内无正文（并报告实测最右/最下墨迹位置）
  M2     手机 15 张卡（强调条颜色 + 卡体白 + 卡外背景）；文本同上；页脚不超正文宽
  X1     两图字段映射与文字一致

裁图：整幅两张 + 10:00–11:15 密集区 + 泳道标题行 + 午休带 + 页脚 + 手机卡片放大。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path.cwd()
RUN = os.environ.get("SNAPSHOT_RUN_ID", "r20261014T1536+0800-5f11da")
sys.path.insert(0, str(ROOT / "tools"))
from dsl import text_width  # noqa: E402

OUT = ROOT / "outputs" / RUN / "A02"
TMP = ROOT / "tmp" / RUN / "A02"
CROPS = TMP / "crops"
CROPS.mkdir(parents=True, exist_ok=True)

# --- 几何：从 audit 的 time_axis 反读，避免与构建脚本两套数字 ---
audit = json.loads((OUT / "schedule-audit.json").read_text(encoding="utf-8"))
TA = audit["time_axis"]
PPM = TA["px_per_minute"]
PX0 = TA["plot"]["x_left"]
CW = TA["plot"]["width_px"]
T0 = TA["base_time_minutes"]
LANE_Y = TA["lane_y"]
LANE_H = TA["lane_height"]
LANES_Y, LANES_BOT = TA["lane_range"]
CARD_INSET, CARD_H = 38, 212
LX0, LX1 = TA["lunch_band"]["x_left"], TA["lunch_band"]["x_right"]
EVENTS = audit["events"]
MM, MCW, MCARD_H, MSTEP = 32, 656, 54, 58
M_AM, M_PM = 210, 761

BAND = (244, 243, 240)      # LANE_BAND #F4F3F0
LUNCH = (229, 227, 220)     # LUNCH_TINT #E5E3DC
PLANE = (249, 249, 247)     # #F9F9F7
INK = 200                   # 亮度低于此值视为墨迹（INK/INK2/MUTED/五类色均 <200）
TOL = 1.5          # 位置容差
TOL_W = 3.5        # 宽度容差（白色游程比卡片外缘各缩进约 1.5px：1px 边框 + 抗锯齿）

checks: list[dict] = []
inks: dict[tuple[str, str, str], tuple[int, int, int, int]] = {}


def ck(tag: str, name: str, ok: bool, detail: str = "") -> None:
    checks.append({"tag": tag, "check": name, "ok": bool(ok), "detail": detail})


def lum(a: np.ndarray) -> np.ndarray:
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def cut(arr: np.ndarray, x0: int, y0: int, x1: int, y1: int) -> np.ndarray:
    return arr[max(0, y0):min(arr.shape[0], y1),
               max(0, x0):min(arr.shape[1], x1)]


def X(t: int) -> float:
    return PX0 + (t - T0) * PPM


def hm(s: str) -> int:
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def runs(mask: np.ndarray) -> list[tuple[int, int]]:
    out, i, n = [], 0, len(mask)
    while i < n:
        if mask[i]:
            j = i
            while j < n and mask[j]:
                j += 1
            out.append((i, j))
            i = j
        else:
            i += 1
    return out


def same(px: np.ndarray, rgb: tuple[int, int, int], tol: int = 1) -> bool:
    return all(abs(int(px[i]) - rgb[i]) <= tol for i in range(3))


def ink_bbox(arr: np.ndarray, x0: int, y0: int, x1: int, y1: int):
    """区域内墨迹的绝对坐标包围盒；无墨迹返回 None。"""
    sub = lum(cut(arr, x0, y0, x1, y1))
    m = sub < INK
    if not m.any():
        return None
    ys, xs = np.where(m)
    return (int(xs.min()) + x0, int(ys.min()) + y0,
            int(xs.max()) + x0, int(ys.max()) + y0)


def is_cjk(s: str) -> bool:
    c = sum(1 for ch in s if ord(ch) > 0x2E7F)
    return c * 2 > len(s)


# ===========================================================================
# 大图
# ===========================================================================
wb = (OUT / "agenda-wide.png").read_bytes()
ck("W1", "agenda-wide.png 是真实 PNG",
   wb[:8] == b"\x89PNG\r\n\x1a\n", f"{len(wb)} 字节，头 {wb[:8]!r}")
pw = Image.open(OUT / "agenda-wide.png").convert("RGB")
aw = np.asarray(pw)
ck("W1", "agenda-wide 尺寸 1920×1200", aw.shape[1] == 1920 and aw.shape[0] == 1200,
   f"实际 {aw.shape[1]}×{aw.shape[0]}")

# --- 泳道底带 ---
for v, ly in LANE_Y.items():
    px = aw[ly + 30, PX0 + 6][:3]
    ck("W2", f"{v} 泳道底带存在", same(px, BAND), f"({PX0 + 6},{ly + 30}) = {tuple(px)}")

# --- 午休带：带内三泳道无卡片 ---
for v, ly in LANE_Y.items():
    row = int(ly) + CARD_INSET + 14          # 卡片顶部圆角之外、强调条之上
    seg = cut(aw, int(LX0) + 6, row, int(LX1) - 6, row + 1)[:3]
    n_white = int((seg.min(axis=-1) >= 250).sum())
    ck("W2", f"{v} 泳道午休时段带内无卡片", n_white == 0,
       f"y={row} 带内检出 {n_white} 个白色像素（应为 0）")

# --- 午休带底色（远离边缘与文字） ---
for v, ly in LANE_Y.items():
    for lab, x in (("带左", int(LX0) + 18), ("带右", int(LX1) - 18)):
        y = int(ly) + CARD_INSET + 14
        px = aw[y, x][:3]
        ck("W2", f"午休带底色 {lab}（{v} 泳道）", same(px, LUNCH, 2),
           f"({x},{y}) = {tuple(px)} 期望 #E5E3DC")

# --- 午休带外侧应是泳道底带 ---
for v, ly in LANE_Y.items():
    y = int(ly) + CARD_INSET + 14
    px = aw[y, int(LX0) - 8][:3]
    ck("W2", f"午休带左侧外侧为底带（{v} 泳道）", same(px, BAND),
       f"({LX0 - 8:.1f},{y}) = {tuple(px)}")
y = int(LANE_Y["C"]) + CARD_INSET + 14      # C 泳道 13:00–13:20 是空档，右侧外侧可测
px = aw[y, int(LX1) + 8][:3]
ck("W2", "午休带右侧外侧为底带（C 泳道）", same(px, BAND),
   f"({LX1 + 8:.1f},{y}) = {tuple(px)}")

# --- 午休带两侧虚线存在 ---
def darkest(x0: int, x1: int, y0: int, y1: int) -> float:
    return float(lum(cut(aw, x0, y0, x1, y1)).min())


for lab, x0, x1 in (("左", int(LX0) - 3, int(LX0) + 2),
                    ("右", int(LX1) - 3, int(LX1) + 2)):
    m = darkest(x0, x1, LANES_Y + 120, LANES_Y + 160)
    ck("W2", f"午休带 {lab}侧虚线存在", m < 210,
       f"x∈[{x0},{x1}] y∈[{LANES_Y + 120},{LANES_Y + 160}] 最暗亮度 {m:.1f}"
       f"（虚线 #C3C2B7 ≈193）")

# --- 卡片左右缘 ---
CARDROW = {v: int(ly) + CARD_INSET + 14 for v, ly in LANE_Y.items()}
by_lane: dict[str, list[tuple[float, float]]] = {"A": [], "B": [], "C": []}
for e in EVENTS:
    by_lane[e["venue"]].append((X(hm(e["start"])), X(hm(e["end"]))))
for v in ("A", "B", "C"):
    row = CARDROW[v]
    mask = cut(aw, 0, row, aw.shape[1], row + 1)[0].min(axis=-1) >= 252
    acts = runs(mask)
    exp = [(round(a, 1), round(b, 1)) for a, b in sorted(by_lane[v])]
    n_act = len(acts)
    ok = n_act == len(exp)
    det = f"游程数 {n_act} vs 期望 {len(exp)}；"
    if ok:
        # 白色游程 = 卡内白色区域，比卡片外缘各缩进约 1.5px（1px 边框 + 抗锯齿），
        # 该内缩对称，故用「宽度」和「中心」判定，而不是端点。
        # 宽度判「时长是否被外扩/压缩」，中心判「起止位置是否偏移」。
        bad = []
        for (a0, a1), (e0, e1) in zip(acts, exp):
            dw = (a1 - a0) - (e1 - e0)
            dc = ((a0 + a1) / 2) - ((e0 + e1) / 2)
            if abs(dw) > TOL_W or abs(dc) > TOL:
                bad.append(f"x[{a0},{a1}] 期望 {e0:.1f}–{e1:.1f}"
                           f"（宽差 {dw:+.2f}px 中心差 {dc:+.2f}px）")
        ok = not bad
        det += (f"宽度误差 ≤ {TOL_W}px、中心误差 ≤ {TOL}px") if not bad \
            else "；".join(bad)
    else:
        det += f"实际 {[tuple(int(t) for t in p) for p in acts]}"
    ck("W3", f"{v} 泳道 {len(exp)} 张卡宽 = 时长×{PPM:.4f}px 且位置 = X(起止)", ok, det)

# --- 卡片上下缘外侧是底带 ---
for e in EVENTS:
    cx = X(hm(e["start"]))
    cy = int(LANE_Y[e["venue"]]) + CARD_INSET
    top = aw[cy - 3, int(cx) + 30][:3]
    bot = aw[cy + CARD_H + 3, int(cx) + 30][:3]
    ck("W3", f"{e['event_id']} 卡片上下缘外侧是底带",
       same(top, BAND) and same(bot, BAND),
       f"上 {tuple(top)} / 下 {tuple(bot)} 期望 {BAND}")

# --- 整点网格线 / 刻度线 ---
gy = LANES_BOT - 6
rowl = lum(aw[gy, :, :3])
bg = float(np.median(rowl))
for h in (10, 11, 14, 15):
    gx = int(round(X(h * 60)))
    m = float(rowl[gx - 4:gx + 5].min())
    ck("W4", f"整点网格线 {h:02d}:00 位于 x={gx}", m < bg - 8,
       f"局部最暗 {m:.1f}，底带中位数 {bg:.1f}"
       f"（12:00/13:00 由午休带虚线承担，另测）")
for h in range(9, 17):
    gx = int(round(X(h * 60)))
    m = darkest(gx - 3, gx + 3, 980, 987)
    ck("W4", f"刻度线 {h:02d}:00 位于 x={gx}", m < 235,
       f"±3px 内最暗亮度 {m:.1f}（1px 刻度 #C3C2B7 抗锯齿后 205–221，白底 255）")

# --- 文本墨迹（大图） ---
wide = [c for c in audit["content_map"] if c["image"] == "agenda-wide.png"]
blocks_w: dict[str, list[float]] = {}
for c in wide:
    if c.get("field") == "block" and c.get("event_id"):
        blocks_w[c["event_id"]] = c["box"]

fails = []
for c in wide:
    if not c.get("text") or c.get("field") in ("block", "public_break"):
        continue
    eid, fld = c["event_id"], c["field"]
    x0, y0, x1, y1 = (int(round(v)) for v in c["box"])
    bb = ink_bbox(aw, x0 - 4, y0 - 4, x1 + 6, y1 + 4)
    if bb is None:
        fails.append({"tag": "W5", "check": f"{eid} {fld} 墨迹存在", "ok": False,
                      "detail": f"盒 [{x0},{y0},{x1},{y1}] 内无任何墨迹（文字未渲染）"})
        continue
    size, bold = c.get("size", 18), c.get("bold", False)
    lines = c.get("line_text") or [c["text"]]
    est = max(text_width(s, size, bold) for s in lines)
    iw = bb[2] - bb[0] + 1
    ratio = iw / est if est else 1.0
    thr = 0.82 if is_cjk(c["text"]) else 0.90
    bx0, _, bx1, _ = blocks_w[eid]
    clear = (bx1 - 4) - bb[2]
    key = (eid, fld)
    if ratio < thr:
        fails.append({"tag": "W5", "check": f"{eid} {fld} 未右裁", "ok": False,
                      "detail": f"墨迹宽 {iw}px < 估算 {est:.1f}px 的 {thr}"
                                f"（ratio {ratio:.3f}）"})
    if clear < 2:
        fails.append({"tag": "W5", "check": f"{eid} {fld} 未溢出卡片", "ok": False,
                      "detail": f"墨迹右缘 x={bb[2]}，卡片内边 {bx1 - 4:.1f}，"
                                f"净空 {clear:.1f}px < 2px"})
    if bb[0] < bx0 + 4:
        fails.append({"tag": "W5", "check": f"{eid} {fld} 未溢出卡片左侧", "ok": False,
                      "detail": f"墨迹左缘 x={bb[0]} < 卡片内边 {bx0 + 4:.1f}"})
    if clear >= 2 and ratio >= thr:
        inks[("wide", eid, fld)] = bb
checks.extend(fails)
ck("W5", "大图文本墨迹完整（存在 / 未右裁 / 未溢出卡片）", not fails,
   "" if not fails else f"{len(fails)} 条失败")

# --- 同卡内文本两两不重叠 ---
coll = []
for eid in blocks_w:
    ks = [k for k in inks if k[0] == "wide" and k[1] == eid]
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            a, b = inks[ks[i]], inks[ks[j]]
            ox = min(a[2], b[2]) - max(a[0], b[0]) + 1
            oy = min(a[3], b[3]) - max(a[1], b[1]) + 1
            if ox > 0 and oy > 0:
                coll.append(f"{ks[i][2]}×{ks[j][2]} 重叠 {ox}×{oy}px")
ck("W5b", "同卡内文本墨迹两两不重叠", not coll,
   "" if not coll else "; ".join(coll))

# --- 页边距（并报告实测最外墨迹） ---
lw = lum(aw)
rightmost = int(np.where(lw.min(axis=0) < INK)[0].max()) \
    if (lw.min(axis=0) < INK).any() else -1
bottommost = int(np.where(lw[:, 300:1600].min(axis=1) < INK)[0].max()) \
    if (lw[:, 300:1600].min(axis=1) < INK).any() else -1
for name, band_ in (("左", lw[:, :36]), ("右", lw[:, 1884:]),
                    ("上", lw[:24, :]), ("下", lw[1182:, :])):
    n = int((band_ < INK).sum())
    ck("W6", f"wide {name}边距带内无正文", n == 0,
       "" if n == 0 else f"{name}边距带内 {n} 个墨迹像素")
ck("W6", "wide 实测最右墨迹未越正文区", rightmost <= 1880,
   f"最右墨迹 x={rightmost}（正文区右界 1880）")
ck("W6", "wide 实测最下墨迹在页内", bottommost <= 1178,
   f"最下墨迹 y={bottommost}")

# ===========================================================================
# 手机图
# ===========================================================================
mb = (OUT / "agenda-mobile.png").read_bytes()
ck("M1", "agenda-mobile.png 是真实 PNG",
   mb[:8] == b"\x89PNG\r\n\x1a\n", f"{len(mb)} 字节，头 {mb[:8]!r}")
pm_ = Image.open(OUT / "agenda-mobile.png").convert("RGB")
am = np.asarray(pm_)
ck("M1", "agenda-mobile 尺寸 720×1280", am.shape[1] == 720 and am.shape[0] == 1280,
   f"实际 {am.shape[1]}×{am.shape[0]}")

mob = [c for c in audit["content_map"] if c["image"] == "agenda-mobile.png"]
blocks_m: dict[str, list[float]] = {}
for c in mob:
    if c.get("field") == "block" and c.get("event_id"):
        blocks_m[c["event_id"]] = c["box"]

# --- 15 张卡：强调条颜色 + 卡体白 + 卡外背景 ---
mfail_card = []
for eid, box in blocks_m.items():
    mx0, my0, mx1, _ = (int(round(v)) for v in box)
    ymid = my0 + 23
    body = am[my0 + 3, mx0 + 10][:3]                 # 卡顶下方、文字之上
    outl = am[ymid, mx0 - 6][:3]
    outr = am[ymid, mx1 + 6][:3]
    top = am[my0 - 3, mx0 + 10][:3]
    ok = (same(body, (255, 255, 255), 1) and same(outl, PLANE, 2)
          and same(outr, PLANE, 2) and same(top, PLANE, 2))
    if not ok:
        mfail_card.append(f"{eid}: 卡体 {tuple(body)} 左外 {tuple(outl)} "
                          f"右外 {tuple(outr)} 上外 {tuple(top)}")
ck("M1", f"手机 {len(blocks_m)} 张卡位置正确（卡体白 / 卡外为页面底色）",
   not mfail_card, "" if not mfail_card else "; ".join(mfail_card[:4]))

# 强调条：卡内左缘 x+2 处应为五类色之一（饱和色，非白非灰）
CATCOLS = [(42, 120, 214), (235, 104, 52), (27, 175, 122), (237, 161, 0),
           (98, 80, 214)]
mfail_bar = []
for eid, box in blocks_m.items():
    mx0, my0 = int(round(box[0])), int(round(box[1]))
    px = am[my0 + 23, mx0 + 2][:3]
    if not any(all(abs(int(px[i]) - c[i]) <= 25 for i in range(3))
               for c in CATCOLS):
        mfail_bar.append(f"{eid}: {tuple(px)}")
ck("M1", "15 张卡强调条为类别色（身份不只靠颜色：同时有色块+文字）",
   not mfail_bar, "" if not mfail_bar else "; ".join(mfail_bar[:4]))

# --- 手机文本 ---
mfails = []
for c in mob:
    if not c.get("text") or c.get("field") in ("block", "public_break"):
        continue
    eid, fld = c["event_id"], c["field"]
    x0, y0, x1, y1 = (int(round(v)) for v in c["box"])
    bb = ink_bbox(am, x0 - 4, y0 - 4, x1 + 6, y1 + 4)
    if bb is None:
        mfails.append({"tag": "M2", "check": f"{eid} {fld} 墨迹存在", "ok": False,
                       "detail": f"盒 [{x0},{y0},{x1},{y1}] 内无墨迹"})
        continue
    size, bold = c.get("size", 18), c.get("bold", False)
    est = text_width(c["text"], size, bold)
    iw = bb[2] - bb[0] + 1
    ratio = iw / est if est else 1.0
    thr = 0.82 if is_cjk(c["text"]) else 0.90
    bx0, _, bx1, _ = blocks_m[eid]
    clear = (bx1 - 4) - bb[2]
    if ratio < thr:
        mfails.append({"tag": "M2", "check": f"{eid} {fld} 未右裁", "ok": False,
                       "detail": f"墨迹宽 {iw}px < 估算 {est:.1f}px 的 {thr}"
                                 f"（ratio {ratio:.3f}）"})
    if clear < 2:
        mfails.append({"tag": "M2", "check": f"{eid} {fld} 未溢出卡片", "ok": False,
                       "detail": f"墨迹右缘 x={bb[2]}，卡片内边 {bx1 - 4}，"
                                 f"净空 {clear}px < 2px"})
    if clear >= 2 and ratio >= thr:
        inks[("mobile", eid, fld)] = bb
checks.extend(mfails)
ck("M2", "手机文本墨迹完整（存在 / 未右裁 / 未溢出卡片）", not mfails,
   "" if not mfails else f"{len(mfails)} 条失败")

# --- 手机同一行内墨迹不粘连（行 1 四段） ---
stick = []
for eid in blocks_m:
    ks = [(k, inks[k]) for k in inks if k[0] == "mobile" and k[1] == eid
          and k[2] in ("venue", "id", "time", "category")]
    row1 = [b for k, b in ks if b[1] < blocks_m[eid][1] + 29]
    row1.sort(key=lambda b: b[0])
    for i in range(len(row1) - 1):
        if row1[i + 1][0] - row1[i][2] < 1:
            stick.append(f"{eid} 行1 相邻墨迹间距 "
                         f"{row1[i + 1][0] - row1[i][2]}px")
ck("M2", "手机行 1 各段墨迹互不粘连", not stick,
   "" if not stick else "; ".join(stick[:5]))

# --- 手机页脚未超正文宽 ---
mlum = lum(am)
mfoot_fail = []
for i, y in enumerate((1177, 1203, 1229)):
    seg = mlum[y - 2:y + 24, :]
    xs = np.where(seg.min(axis=0) < INK)[0]
    if len(xs) == 0:
        mfoot_fail.append(f"第 {i + 1} 行无墨迹")
    elif xs.max() > MM + MCW + 3:
        mfoot_fail.append(f"第 {i + 1} 行墨迹右缘 x={xs.max()} > {MM + MCW}")
ck("M2", "手机页脚三行未超正文宽 656px", not mfoot_fail,
   "" if not mfoot_fail else "; ".join(mfoot_fail))

# --- 手机边距 ---
for name, band_ in (("左", mlum[:, :28]), ("右", mlum[:, 692:]),
                    ("上", mlum[:22, :]), ("下", mlum[1256:, :])):
    n = int((band_ < INK).sum())
    ck("M3", f"mobile {name}边距带内无正文", n == 0,
       "" if n == 0 else f"{name}边距带内 {n} 个墨迹像素")
mright = int(np.where(mlum.min(axis=0) < INK)[0].max())
mbot = int(np.where(mlum[:, 40:680].min(axis=1) < INK)[0].max())
ck("M3", "mobile 实测最右墨迹未越正文区", mright <= MM + MCW + 3,
   f"最右墨迹 x={mright}（正文区右界 {MM + MCW}）")
ck("M3", "mobile 实测最下墨迹在页内", mbot <= 1255, f"最下墨迹 y={mbot}")

# ===========================================================================
# 两图字段映射
# ===========================================================================
WIDE_NEED = {"id", "time", "speaker", "title", "category"}
MOB_NEED = {"venue", "id", "time", "category", "title"}
xmap_fail = []
for e in EVENTS:
    eid = e["event_id"]
    wid = {c["field"] for c in wide if c.get("event_id") == eid}
    mid = {c["field"] for c in mob if c.get("event_id") == eid}
    if not WIDE_NEED <= wid:
        xmap_fail.append(f"{eid} 大图缺 {sorted(WIDE_NEED - wid)}")
    if not MOB_NEED <= mid:
        xmap_fail.append(f"{eid} 手机缺 {sorted(MOB_NEED - mid)}")
    for fld in ("time", "title"):
        a = next((c["text"] for c in wide if c.get("event_id") == eid
                  and c["field"] == fld), None)
        b = next((c["text"] for c in mob if c.get("event_id") == eid
                  and c["field"] == fld), None)
        if a != b:
            xmap_fail.append(f"{eid} {fld} 两图不一致: {a!r} vs {b!r}")
ck("X1", "15 场在两图字段齐全且时间/标题文字一致", not xmap_fail,
   "" if not xmap_fail else "; ".join(xmap_fail[:6]))
ck("X1", "讲者按 TASK.md 仅在大图（手机注明「讲者详见完整日程」）",
   all(not any(c.get("field") == "speaker" for c in mob
               if c.get("event_id") == e["event_id"]) for e in EVENTS),
   "手机图 0 条 speaker 记录")

# ===========================================================================
# 裁图
# ===========================================================================
def save(im, name, bx=None, scale=1):
    src = im.crop(bx) if bx else im
    if scale != 1:
        src = src.resize((src.width * scale, src.height * scale),
                         Image.NEAREST)
    src.save(CROPS / name)
    return name


save(pw, "wide-full.png")
save(pw, "wide-dense-1000-1115.png",
     (int(X(hm("10:00"))) - 24, LANES_Y - 34, int(X(hm("11:15"))) + 24,
      LANES_BOT + 44), 2)
save(pw, "wide-header.png", (0, 0, 1920, 160), 2)
save(pw, "wide-lane-headers.png", (0, 150, 1920, 200), 2)
save(pw, "wide-lunch-band.png",
     (int(LX0) - 100, LANES_Y, int(LX1) + 100, LANES_BOT), 2)
save(pw, "wide-footer.png", (0, 1046, 1920, 1200), 2)
save(pw, "wide-lane-c.png", (0, 700, 1920, 1000), 1)
save(pm_, "mobile-full.png")
save(pm_, "mobile-am-cards.png", (0, 196, 720, 520), 2)
save(pm_, "mobile-pm-footer.png", (0, 700, 720, 1280), 1)

# ===========================================================================
rep = {"schema_version": 1, "task_id": "A02", "run_id": RUN,
       "path_base": "suite_root",
       "images": {k: f"outputs/{RUN}/A02/{k}.png"
                  for k in ("agenda-wide", "agenda-mobile")},
       "crops": sorted(p.name for p in CROPS.glob("*.png")),
       "thresholds": {"geometry_tolerance_px": TOL, "ink_luminance_below": INK,
                      "text_ink_ratio_min_cjk": 0.82,
                      "text_ink_ratio_min_latin": 0.90,
                      "min_clear_to_card_edge_px": 2},
       "measured": {"wide_rightmost_ink_x": rightmost,
                    "wide_bottommost_ink_y": bottommost,
                    "mobile_rightmost_ink_x": mright,
                    "mobile_bottommost_ink_y": mbot},
       "total": len(checks),
       "failures": [c for c in checks if not c["ok"]],
       "checks": checks}
(TMP / "inspect-report.json").write_text(
    json.dumps(rep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

bad = rep["failures"]
print(f"checks {len(checks)}  fail {len(bad)}")
print("measured", json.dumps(rep["measured"]))
for c in bad:
    print("FAIL", c["tag"], c["check"], "|", c["detail"])
