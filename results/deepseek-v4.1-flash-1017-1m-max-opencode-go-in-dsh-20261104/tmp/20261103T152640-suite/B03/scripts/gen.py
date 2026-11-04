# -*- coding: utf-8 -*-
"""B03: ten pieces exploring DSL technique, each in a real scenario."""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "B03"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

def R(x, y, w, h, c, r=0, b=None):
    return K.rect(x, y, w, h, color=c, radius=r, border=b)

def T(x, y, s, w, size, c, bold=False, align=None, label=None):
    return K.text(x, y, s, width=w, size=size, color=c, bold=bold, align=align, label=label)

def raw_text(s, w, size, c, bold=False):
    esc = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return ('<Text width="%g" fontSize="%g" color="%s"%s>%s</Text>'
            % (w, size, c, ' fontWeight="bold"' if bold else '', esc))


def clip(x, y, w, h, path, color, rule="NON_ZERO"):
    return (f'<Positioned left="{x:g}" top="{y:g}"><ClipPath path="{path}" fillRule="{rule}" '
            f'clipBehavior="ANTI_ALIAS"><Container width="{w:g}" height="{h:g}" color="{color}"/>'
            f'</ClipPath></Positioned>')

def rot(x, y, w, h, ang, inner, ox, oy):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    tx = ox - (c * ox - s * oy)
    ty = oy - (s * ox + c * oy)
    return (f'<Positioned left="{x:g}" top="{y:g}"><Transform '
            f'matrix="({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,{tx:.4f},{ty:.4f},0,1)" '
            f'alignment="TOP_LEFT">{inner}</Transform></Positioned>')

def ring_path(cx, cy, r):
    return (f"M{cx + r:g} {cy:g} a{r:g} {r:g} 0 1 0 {-2*r:g} 0 a{r:g} {r:g} 0 1 0 {2*r:g} 0 ")

# ---------------------------------------------------------------- 1. record sleeve (concentric rings)
def c1():
    W = H = 1200
    p = [R(0, 0, W, H, "#101014")]
    cx, cy = 600, 600
    for i, r in enumerate([300, 262, 224, 186, 148, 110]):
        col = "#E8E2D2" if i % 2 == 0 else "#101014"
        p.append(R(cx - r, cy - r, 2 * r, 2 * r, col, r))
    p.append(R(cx - 66, cy - 66, 132, 132, "#C8452D", 66))
    p.append(R(cx - 14, cy - 14, 28, 28, "#101014", 14))
    p.append(T(72, 72, "SIDE A", 300, 22, "#E8E2D2"))
    p.append(T(72, 962, "夜航", 500, 64, "#E8E2D2", True))
    p.append(T(72, 1046, "MONO · 2026 · 33⅓ RPM", 600, 20, "#8A8578"))
    p.append(T(940, 1046, "NR-009", 188, 20, "#8A8578", align="RIGHT"))
    return K.document(W, H, p, background="#101014")

# ---------------------------------------------------------------- 2. exhibition poster (rotated type)
def c2():
    W, H = 1080, 1440
    p = [R(0, 0, W, H, "#F2EFE6")]
    p.append(R(72, 72, 936, 2, "#1A1A1A"))
    p.append(T(72, 96, "市立美术馆 · 三层", 600, 20, "#6B6558"))
    # giant rotated word
    inner = ""
    p.append(T(60, 300, "结构", 900, 190, "#1A1A1A", True))
    p.append(rot(90, 516, 900, 190, -6, raw_text("与留白", 900, 190, "#1A1A1A", True), 450, 95))
    p.append(R(72, 792, 300, 6, "#C8452D"))
    p.append(T(72, 830, "10.18 – 12.06", 600, 34, "#1A1A1A", True))
    p.append(T(72, 880, "每日 10:00–18:00 · 周一闭馆", 700, 22, "#6B6558"))
    p.append(T(72, 930, "三层 A 厅 · 免费", 700, 22, "#6B6558"))
    p.append(R(72, 980, 936, 1, "#D8D2C2"))
    p.append(T(72, 1010, "本次展览把版面当作建筑：十二组排版实验，", 900, 22, "#1A1A1A"))
    p.append(T(72, 1044, "从报纸到地铁导视，看结构如何决定阅读。", 900, 22, "#1A1A1A"))
    p.append(T(72, 1330, "museum.example", 500, 20, "#6B6558"))
    p.append(T(72, 1364, "封面：展览主视觉第 1 号", 600, 18, "#9A9484"))
    return K.document(W, H, p, background="#F2EFE6")

# ---------------------------------------------------------------- 3. data-art backdrop (blur + chart)
def c3():
    W, H = 1600, 1000
    p = [R(0, 0, W, H, "#0B0F18")]
    blobs = [(360, 300, "#3B82F6B3"), (820, 520, "#8B5CF6A6"), (1200, 280, "#22D3EE99")]
    for bx, by, col in blobs:
        p.append('<Positioned left="%g" top="%g"><SizedBox width="360" height="360">' % (bx - 180, by - 180) +
                 f'<ImageFiltered sigmaX="78" sigmaY="78" quality="HIGH">' +
                 f'<Container width="360" height="360" color="{col}" borderRadius="180"/>' +
                 '</ImageFiltered></SizedBox></Positioned>')
    p.append(T(80, 72, "数据叙事大会 2026", 700, 26, "#C7D2FE"))
    p.append(T(80, 116, "让数字被看见", 900, 64, "#FFFFFF", True))
    p.append(T(80, 202, "11.21–11.22 · 城西会展中心 · 12 位讲者", 800, 22, "#94A3B8"))
    bars = [("05", 32), ("06", 48), ("07", 41), ("08", 58), ("09", 46), ("10", 66), ("11", 52), ("12", 74)]
    for i, (m, v) in enumerate(bars):
        x = 80 + i * 108
        h = v * 5
        p.append(R(x, 800 - h, 68, h, "#FFFFFF22", 6))
        p.append(R(x, 800 - int(h * 0.62), 68, int(h * 0.62), "#E2E8F0", 6))
        p.append(T(x, 812, m + "月", 68, 18, "#94A3B8", align="CENTER"))
    p.append(T(1030, 800, "报名增速（近 8 个月，演示数据）", 500, 18, "#94A3B8", align="RIGHT"))
    p.append(T(80, 900, "大会主视觉 · 会场大屏与手册封面共用", 700, 18, "#64748B"))
    return K.document(W, H, p, background="#0B0F18")

# ---------------------------------------------------------------- 4. sound wave wall (procedural bars)
def c4():
    W, H = 1600, 900
    p = [R(0, 0, W, H, "#0E0E0E")]
    p.append(T(72, 60, "回声录音棚 · 走廊", 700, 24, "#8A8578"))
    p.append(T(72, 100, "一段 12 秒的呼吸", 900, 44, "#F2EFE6", True))
    n = 96
    for i in range(n):
        v = abs(math.sin(i * 0.31) * math.cos(i * 0.11)) * 0.8 + 0.12 * abs(math.sin(i * 1.7))
        h = int(40 + v * 420)
        x = 72 + i * 15
        col = "#C8452D" if i % 16 == 0 else "#F2EFE6"
        p.append(R(x, 700 - h, 8, h, col, 4))
    p.append(R(72, 700, 1440, 2, "#3A3A3A"))
    p.append(T(72, 740, "声压分布 · 每 125ms 采样一次 · 红色为换气点", 900, 20, "#8A8578"))
    p.append(T(72, 820, "现场装置尺寸 4.2 × 2.4 m，按 1:1 比例缩放", 900, 18, "#5A5648"))
    return K.document(W, H, p, background="#0E0E0E")

# ---------------------------------------------------------------- 5. halftone zine cover
def c5():
    W, H = 1200, 1600
    p = [R(0, 0, W, H, "#F4F1E8")]
    p.append(T(80, 80, "ZINE 04 · 手工印刷", 600, 20, "#8A8578"))
    p.append(T(80, 120, "纸上的网", 800, 64, "#141414", True))
    # halftone: dot radius varies with a wave function; one path per row band for performance
    for row in range(26):
        path = ""
        y = 280 + row * 40
        for col in range(26):
            x = 80 + col * 40
            d = (math.sin(col * 0.5 + row * 0.35) + math.cos(row * 0.22 - col * 0.18)) * 0.5
            r = 3 + abs(d) * 15
            path += f"M{x + r:g} {y:g} a{r:g} {r:g} 0 1 0 {-2*r:g} 0 a{r:g} {r:g} 0 1 0 {2*r:g} 0 "
        p.append(clip(0, 0, W, H, path, "#141414", "NON_ZERO"))
    p.append(R(80, 1380, 1040, 3, "#141414"))
    p.append(T(80, 1404, "256 个网点 · 半径 3–18px · 由两条正弦叠加决定", 1040, 20, "#3A3A3A"))
    p.append(T(80, 1470, "印刷：单色丝网 · 纸张 120g 米白", 800, 18, "#8A8578"))
    return K.document(W, H, p, background="#F4F1E8")

# ---------------------------------------------------------------- 6. isometric architecture
def c6():
    W, H = 1400, 1000
    p = [R(0, 0, W, H, "#EDEAE2")]
    p.append(T(72, 64, "城西文化中心 · 方案展", 700, 22, "#6B6558"))
    p.append(T(72, 100, "三种体量的叠合", 800, 44, "#1A1A1A", True))
    def face(x, y, w, h, skew, color):
        # parallelogram via skew matrix: x' = x + skew*y
        return (f'<Positioned left="{x:g}" top="{y:g}"><Transform '
                f'matrix="(1,0,0,0,{skew:.4f},1,0,0,0,0,1,0,0,0,0,1)" alignment="TOP_LEFT">'
                f'<Container width="{w:g}" height="{h:g}" color="{color}"/></Transform></Positioned>')
    p.append(face(420, 560, 420, 220, 0.5, "#1F2937"))
    p.append(face(420, 340, 420, 220, 0.5, "#374151"))
    p.append(face(460, 200, 420, 140, 0.5, "#4B5563"))
    p.append(R(430, 784, 420, 6, "#C8452D"))
    p.append(T(1010, 372, "A 座 · 展厅", 300, 22, "#1A1A1A", True))
    p.append(T(1010, 404, "净高 9m，可开合屋面", 300, 18, "#6B6558"))
    p.append(T(1010, 560, "B 座 · 排练厅", 300, 22, "#1A1A1A", True))
    p.append(T(1010, 592, "浮筑地板，隔振 52dB", 300, 18, "#6B6558"))
    p.append(R(72, 860, 600, 2, "#D8D2C2"))
    p.append(T(72, 884, "透视采用 1:2 斜投影，所有体量共用同一灭点方向。", 700, 20, "#3A3A3A"))
    return K.document(W, H, p, background="#EDEAE2")

# ---------------------------------------------------------------- 7. brand pattern sheet (even-odd knock-out)
def c7():
    W = H = 1200
    p = [R(0, 0, W, H, "#0F172A")]
    path = ""
    for i in range(6):
        for j in range(4):
            cx, cy = 120 + i * 178, 240 + j * 170
            path += ring_path(cx, cy, 62) + ring_path(cx, cy, 30)
    p.append(clip(0, 0, W, W, path, "#38BDF8", "EVEN_ODD"))
    p.append(T(80, 60, "标识延展 · 图形母版", 700, 22, "#93C5FD"))
    p.append(T(80, 940, "双环单元 24 个 · 内外径 62/30 · 可任意裁切", 900, 22, "#94A3B8"))
    p.append(T(80, 986, "应用：包装纸、导视背板、员工工牌底纹", 900, 22, "#94A3B8"))
    return K.document(W, H, p, background="#0F172A")

# ---------------------------------------------------------------- 8. overprint study
def c8():
    W, H = 1080, 1350
    p = [R(0, 0, W, H, "#F7F4EC")]
    p.append(T(72, 64, "印前实验室 · 叠印研究", 700, 22, "#6B6558"))
    p.append(T(72, 100, "三种油墨的相遇", 800, 44, "#141414", True))
    p.append(R(120, 300, 400, 400, "#0093D733"))
    p.append(R(320, 300, 400, 400, "#E4002B33"))
    p.append(R(220, 500, 400, 400, "#FFD10033"))
    p.append(R(120, 300, 400, 400, "#00000000", 0, "1 SOLID #141414"))
    p.append(R(320, 300, 400, 400, "#00000000", 0, "1 SOLID #141414"))
    p.append(R(220, 500, 400, 400, "#00000000", 0, "1 SOLID #141414"))
    p.append(R(72, 960, 936, 2, "#D8D2C2"))
    p.append(T(72, 986, "青 / 品红 / 黄以 20% 叠印，交叠处呈现真实的混色结果。", 900, 22, "#141414"))
    p.append(T(72, 1022, "该页用于向客户解释：屏幕上的浅色不等于印刷的浅色。", 900, 22, "#6B6558"))
    p.append(T(72, 1120, "编号 PR-07 · 2026", 600, 18, "#9A9484"))
    return K.document(W, H, p, background="#F7F4EC")

# ---------------------------------------------------------------- 9. radial star chart (one path)
def c9():
    W = H = 1400
    p = [R(0, 0, W, H, "#070B14")]
    cx, cy = 700, 700
    path = ""
    for i in range(180):
        a = math.radians(i * 2)
        r1 = 150 + 30 * abs(math.sin(i * 0.7))
        r2 = 424 + 42 * abs(math.cos(i * 0.31))
        w = 0.012 if i % 5 else 0.03
        x1, y1 = cx + r1 * math.cos(a - w), cy + r1 * math.sin(a - w)
        x2, y2 = cx + r2 * math.cos(a - w), cy + r2 * math.sin(a - w)
        x3, y3 = cx + r2 * math.cos(a + w), cy + r2 * math.sin(a + w)
        x4, y4 = cx + r1 * math.cos(a + w), cy + r1 * math.sin(a + w)
        path += f"M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f} L{x3:.1f} {y3:.1f} L{x4:.1f} {y4:.1f} Z "
    p.append(clip(0, 0, W, W, path, "#BFD7FF", "NON_ZERO"))
    p.append(clip(0, 0, W, W, ring_path(cx, cy, 150) + ring_path(cx, cy, 110), "#FFD166", "EVEN_ODD"))
    p.append(T(80, 72, "天文馆 · 冬季星空海报", 700, 22, "#7C8CA3"))
    p.append(T(80, 108, "180 条视线", 800, 44, "#EDF2F8", True))
    p.append(T(80, 1288, "每条线的长度对应当晚可观测时长；加粗的每 5 条为整点标记。", 1100, 20, "#7C8CA3"))
    p.append(T(80, 1330, "中心双环为观测窗，直径 220px。", 800, 20, "#7C8CA3"))
    return K.document(W, H, p, background="#070B14")

# ---------------------------------------------------------------- 10. editorial chart page
def c10():
    W, H = 1200, 1600
    p = [R(0, 0, W, H, "#FBFAF6")]
    p.append(T(80, 72, "年报 · 第 4 节", 600, 20, "#8A8578"))
    p.append(T(80, 108, "四个季度的成本结构", 900, 44, "#141414", True))
    p.append(R(80, 176, 1040, 2, "#141414"))
    p.append(T(80, 200, "单位：万元。数据为演示。", 700, 18, "#8A8578"))
    series = [("Q1", [42, 28, 18, 12]), ("Q2", [46, 30, 16, 10]), ("Q3", [44, 33, 17, 9]),
              ("Q4", [50, 31, 15, 14])]
    colors = ["#1F2937", "#6B7280", "#9CA3AF", "#C8452D"]
    labels = ["人力", "场地", "物料", "其他"]
    base = 900
    for i, (q, vals) in enumerate(series):
        x = 140 + i * 240
        acc = 0
        for j, v in enumerate(vals):
            h = v * 5.2
            p.append(R(x, base - acc - h, 140, h, colors[j]))
            acc += h
        p.append(T(x, base + 10, q, 140, 22, "#141414", True, "CENTER"))
        p.append(T(x, base + 42, f"{sum(vals)}", 140, 20, "#8A8578", align="CENTER"))
    p.append(R(80, 972, 1040, 1, "#D8D2C2"))
    for j, lab in enumerate(labels):
        y = 1004 + j * 52
        p.append(R(80, y + 6, 16, 16, colors[j], 3))
        p.append(T(112, y, lab, 200, 20, "#141414"))
    p.append(T(80, 1240, "Q4 的「其他」升到 14 万，主要来自一次性的设备租赁。", 1000, 22, "#141414"))
    p.append(T(80, 1284, "四个季度合计 415 万元，人力占比稳定在 42%–45%。", 1000, 22, "#141414"))
    p.append(R(80, 1360, 1040, 1, "#D8D2C2"))
    p.append(T(80, 1384, "图表由 DSL 直接绘制：柱体为矩形，基线共用零起点。", 1000, 18, "#8A8578"))
    p.append(T(80, 1500, "063", 100, 18, "#8A8578", align="RIGHT"))
    return K.document(W, H, p, background="#FBFAF6")

CASES = [
    ("case-01", "唱片封套 · 同心环", c1, (1200, 1200), "ClipPath 多子路径 + EVEN_ODD",
     "唱片发行：封面需要在流媒体小图与 12 寸印刷品上都成立", "用一条 EVEN_ODD 路径一次画出六道环形带与中心孔"),
    ("case-02", "展览海报 · 旋转标题", c2, (1080, 1440), "Transform 旋转 + 文字层级",
     "美术馆展览：主视觉要让标题本身成为版式", "把第二行标题旋转 −6°，与水平的第一行形成张力"),
    ("case-03", "大会主视觉 · 模糊光斑", c3, (1600, 1000), "ImageFiltered + SizedBox 包裹",
     "行业大会：会场大屏与手册封面共用一张主视觉", "三个高斯光斑（σ=110）作为背景，前景用真实报名数据柱"),
    ("case-04", "录音棚墙面 · 声波", c4, (1600, 900), "程序化几何（正弦叠加）",
     "录音棚走廊装置：把一段录音变成可施工的图形", "96 根竖条的高度由两条正弦叠加算出，每 16 根标一次换气"),
    ("case-05", "独立杂志封面 · 半调", c5, (1200, 1600), "单路径 676 个圆的半调",
     "独立杂志：单色丝网印刷的封面", "网点半径 3–18px 由两条正弦叠加决定，逐行合成一条路径"),
    ("case-06", "建筑展板 · 斜投影", c6, (1400, 1000), "Transform 斜切矩阵",
     "建筑设计展：用二维图形表达三个叠合体量", "每个体量用 skew 矩阵做成平行四边形，共用同一灭点方向"),
    ("case-07", "品牌母版 · 镂空双环", c7, (1200, 1200), "EVEN_ODD 挖空 + 重复单元",
     "品牌延展：可任意裁切的图形母版", "36 个双环单元合成为一条路径，内环由奇偶规则挖空"),
    ("case-08", "印前研究 · 叠印", c8, (1080, 1350), "8 位 alpha 叠色",
     "印前实验室：向客户解释屏幕色与印刷色的差别", "青/品红/黄各 20% 叠印，交叠处呈现真实混色"),
    ("case-09", "天文馆海报 · 放射", c9, (1400, 1400), "单路径 180 个四边形",
     "天文馆冬季星空海报", "180 条视线由极坐标算出，合成为一条填充路径，避免 180 次变换"),
    ("case-10", "年报内页 · 堆叠柱", c10, (1200, 1600), "真实数据 + 共用零起点",
     "年报第 4 节：四季度成本结构", "四组堆叠柱严格按数值绘制，基线与标注同一条参考线"),
]

logger = api.TaskLogger(TASK, TMP)
ONLY = os.environ.get("B03_ONLY", "").split(",") if os.environ.get("B03_ONLY") else None
meta = []
for cid, title, fn, size, tech, scene, method in CASES:
    if ONLY and cid not in ONLY:
        continue
    d = OUT / cid
    d.mkdir(parents=True, exist_ok=True)
    dsl = fn()
    (d / "final.snapshot").write_text(dsl, encoding="utf-8")
    warn = K.drain_warnings()
    rec = logger.render(d / "final.snapshot", d / "final.png", cid)
    ok = rec["http_status"] == 200 and api.measure_png(d / "final.png") == size
    print(f"{cid}: {rec['http_status']} {rec['response_bytes']}B {rec['elapsed_s']}s ok={ok}")
    for w in warn:
        print("   ", w)
    meta.append({"case": cid, "title": title, "size": list(size), "technique": tech,
                 "scene": scene, "method": method, "png": f"{cid}/final.png",
                 "dsl": f"{cid}/final.snapshot", "bytes": rec["response_bytes"]})
if not ONLY:
    api.write_json(TMP / "cases.json", meta)
print("rendered", len(meta))
