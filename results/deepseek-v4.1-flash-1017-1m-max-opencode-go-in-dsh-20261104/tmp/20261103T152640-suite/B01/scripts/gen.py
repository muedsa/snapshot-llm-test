# -*- coding: utf-8 -*-
"""B01: ten independent showcase pieces."""
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

TASK = "B01"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

def R(x, y, w, h, c, r=0, b=None):
    return K.rect(x, y, w, h, color=c, radius=r, border=b)

def Tx(x, y, s, w, size, c, bold=False, align=None, label=None):
    return K.text(x, y, s, width=w, size=size, color=c, bold=bold, align=align, label=label)

# ---------------------------------------------------------------- 1. FIDS
def case1():
    W, H = 1920, 1080
    bg, ink, dim, acc = "#0A1017", "#EDF4FF", "#7C8CA3", "#F2B84B"
    p = [R(0, 0, W, H, bg), R(0, 0, W, 8, acc)]
    p.append(Tx(72, 42, "北屿国际机场 · 离港", 700, 26, dim))
    p.append(Tx(72, 78, "DEPARTURES", 1200, 64, ink, True))
    p.append(Tx(1500, 60, "22:41", 280, 54, acc, True, "RIGHT"))
    p.append(Tx(1500, 122, "2026-11-07 周六", 280, 22, dim, align="RIGHT"))
    heads = [("起飞", 72, 150), ("航班", 240, 240), ("目的地", 500, 420), ("登机口", 940, 200),
             ("状态", 1180, 300), ("备注", 1500, 340)]
    p.append(R(72, 170, 1776, 2, "#1E2A38"))
    for label, x, w in heads:
        p.append(Tx(x, 182, label, w, 22, dim, True))
    rows = [("22:55", "BL 412", "上海浦东", "A12", "登机中", "BOARDING", acc),
            ("23:10", "BL 738", "成都天府", "B04", "准点", "ON TIME", "#4ADE80"),
            ("23:25", "BL 206", "广州白云", "A07", "延误 25 分", "DELAYED", "#F87171"),
            ("23:40", "BL 991", "首尔仁川", "C11", "准点", "ON TIME", "#4ADE80"),
            ("23:55", "BL 305", "深圳宝安", "B09", "登机中", "BOARDING", acc),
            ("00:15", "BL 660", "东京羽田", "C02", "值机截止", "CLOSING", "#F87171"),
            ("00:30", "BL 118", "西安咸阳", "A03", "准点", "ON TIME", "#4ADE80"),
            ("00:45", "BL 887", "昆明长水", "B12", "取消", "CANCELLED", "#94A3B8")]
    for i, (t, f, dest, gate, st, en, col) in enumerate(rows):
        y = 240 + i * 82
        if i % 2 == 0:
            p.append(R(72, y - 10, 1776, 74, "#111C28", 8))
        p.append(Tx(72, y, t, 150, 40, ink, True))
        p.append(Tx(240, y + 6, f, 240, 32, acc, True))
        p.append(Tx(500, y + 4, dest, 420, 34, ink))
        p.append(Tx(940, y + 4, gate, 200, 34, ink, True))
        p.append(Tx(1180, y + 4, st, 300, 30, col, True))
        p.append(Tx(1500, y + 12, en, 340, 22, dim))
    p.append(R(72, 940, 1776, 2, "#1E2A38"))
    p.append(Tx(72, 962, "登机口将在起飞前 15 分钟关闭 · 请留意广播", 1200, 24, dim))
    p.append(Tx(1400, 962, "层 3 · 安检后右转", 448, 24, dim, align="RIGHT"))
    return K.document(W, H, p, background=bg)

# ---------------------------------------------------------------- 2. pour-over recipe
def case2():
    W, H = 1080, 1350
    bg, ink, dim, acc = "#F6EFE4", "#2A1F16", "#8A7460", "#B4622A"
    p = [R(0, 0, W, H, bg)]
    p.append(R(0, 0, W, 10, acc))
    p.append(Tx(72, 64, "手冲 · 埃塞 日晒", 600, 24, dim))
    p.append(Tx(72, 104, "一杯的配方", 900, 54, ink, True))
    p.append(Tx(72, 182, "V60 · 15g 粉 · 250g 水 · 2:30", 900, 24, dim))
    steps = [("01", "闷蒸", "0:00–0:30", "注水 45g，等粉层塌陷", "45 g"),
             ("02", "第一段", "0:30–1:05", "中心画圈到 140g", "95 g"),
             ("03", "第二段", "1:05–1:40", "水流放稳到 220g", "80 g"),
             ("04", "收尾", "1:40–2:10", "补到 250g 后轻摇", "30 g"),
             ("05", "完成", "2:30", "滴滤结束，立即取出滤杯", "—")]
    for i, (n, name, t, desc, w) in enumerate(steps):
        y = 250 + i * 152
        p.append(R(72, y, 936, 132, "#FFFFFF", 14, "1 SOLID #E3D6C4"))
        p.append(Tx(96, y + 20, n, 80, 34, acc, True))
        p.append(Tx(176, y + 16, name, 240, 30, ink, True))
        p.append(Tx(176, y + 58, t, 300, 22, dim))
        p.append(Tx(176, y + 90, desc, 560, 22, ink))
        p.append(Tx(800, y + 40, w, 180, 34, ink, True, "RIGHT"))
    p.append(R(72, 1040, 936, 2, "#E3D6C4"))
    p.append(Tx(72, 1064, "研磨：中细 · 水温 92℃ · 水质 80ppm", 900, 24, ink))
    p.append(Tx(72, 1112, "风味：柑橘 / 红茶 / 蜂蜜", 900, 24, acc, True))
    p.append(Tx(72, 1206, "Slow Bar · 每日 08:00–18:00", 700, 22, dim))
    p.append(Tx(72, 1246, "slowbar.example", 700, 22, dim))
    return K.document(W, H, p, background=bg)

# ---------------------------------------------------------------- 3. podcast cover
def case3():
    S = 1400
    bg, ink, acc = "#1A1033", "#F3EFFF", "#C4B5FD"
    p = [R(0, 0, S, S, bg)]
    for i in range(28):
        h = 40 + int(180 * abs(math.sin(i * 0.9)))
        p.append(R(80 + i * 44, 980 - h, 22, h, acc if i % 3 else "#8B5CF6", 11))
    p.append(Tx(80, 96, "EP. 42", 400, 30, acc, True))
    p.append(Tx(80, 152, "把复杂", 1240, 92, ink, True))
    p.append(Tx(80, 268, "讲清楚", 1240, 92, ink, True))
    p.append(Tx(80, 420, "和一位信息设计师聊三小时", 1240, 34, acc))
    p.append(R(80, 500, 120, 6, "#8B5CF6"))
    p.append(Tx(80, 540, "结构电台", 800, 44, ink, True))
    p.append(Tx(80, 612, "STRUCTURE FM", 800, 26, acc))
    p.append(Tx(80, 1080, "本期嘉宾 · 林川 / 苏言", 900, 26, "#B9AEE0"))
    p.append(Tx(80, 1130, "2026.11.07 · 时长 03:12:40", 900, 26, "#B9AEE0"))
    p.append(Tx(80, 1240, "structure.fm", 800, 28, ink, True))
    return K.document(S, S, p, background=bg)

# ---------------------------------------------------------------- 4. transit map
def case4():
    W, H = 1600, 900
    bg, ink, dim = "#FFFFFF", "#10131A", "#6B7280"
    p = [R(0, 0, W, H, bg)]
    p.append(Tx(64, 48, "溪城轨道 · 内环示意", 700, 28, dim))
    p.append(Tx(64, 84, "三线换乘", 900, 44, ink, True))
    A, B, C = "#E11D48", "#0EA5E9", "#16A34A"
    # A: horizontal y=300, x 200..1000
    p.append(R(200, 293, 800, 14, A, 7))
    # B: vertical x=680, y 180..700
    p.append(R(673, 180, 14, 520, B, 7))
    # C: horizontal y=540, x 680..1320
    p.append(R(680, 533, 640, 14, C, 7))
    a_st = [(200, "西苑"), (360, "旧城"), (520, "中庭"), (680, "广场"), (840, "东门"), (1000, "新城")]
    b_st = [(180, "北塔"), (240, "河湾"), (300, "广场"), (420, "会展"), (540, "港前"), (660, "南苑")]
    c_st = [(680, "广场"), (820, "工坊"), (960, "林园"), (1100, "长堤"), (1240, "远山")]
    for x, name in a_st:
        p.append(R(x - 11, 289, 22, 22, "#FFFFFF", 11, f"4 SOLID {A}"))
        if name == "广场":
            p.append(Tx(x - 150, 246, name, 130, 22, ink, align="RIGHT"))
        else:
            p.append(Tx(x - 50, 246, name, 110, 22, ink, align="CENTER"))
    for y, name in b_st:
        p.append(R(669, y - 11, 22, 22, "#FFFFFF", 11, f"4 SOLID {B}"))
        if name == "广场":
            continue
        if name == "港前":
            p.append(Tx(700, y + 12, name, 130, 22, ink))
        else:
            p.append(Tx(700, y - 14, name, 130, 22, ink))
    for x, name in c_st:
        p.append(R(x - 11, 529, 22, 22, "#FFFFFF", 11, f"4 SOLID {C}"))
        if name == "广场":
            continue
        p.append(Tx(x - 52, 566, name, 104, 22, ink, align="CENTER"))
    for i, (label, col) in enumerate((("A 线 · 东西", A), ("B 线 · 南北", B), ("C 线 · 东环", C))):
        yy = 660 + i * 52
        p.append(R(64, yy + 8, 40, 10, col, 5))
        p.append(Tx(120, yy, label, 300, 24, ink, True))
    p.append(Tx(64, 848, "站名与线路均为示意，不对应真实城市；A/B 在「广场」交汇，C 线自 B 线「港前」引出", 900, 20, dim))
    return K.document(W, H, p, background=bg)
# ---------------------------------------------------------------- 5. training week
def case5():
    W, H = 1080, 1350
    bg, card, ink, dim, acc = "#0E1116", "#171C24", "#F2F5F9", "#8A94A6", "#34D399"
    p = [R(0, 0, W, H, bg)]
    p.append(Tx(64, 56, "第 7 周 · 力量基础", 700, 24, dim))
    p.append(Tx(64, 92, "训练周计划", 900, 48, ink, True))
    days = [("一", "上肢推", "卧推 4×6", 1), ("二", "下肢", "深蹲 5×5", 1), ("三", "休息", "步行 30′", 0),
            ("四", "上肢拉", "硬拉 4×5", 1), ("五", "技术", "抓举 6×2", 1), ("六", "有氧", "划船 20′", 1),
            ("日", "休息", "拉伸 15′", 0)]
    for i, (d, kind, detail, train) in enumerate(days):
        y = 190 + i * 148
        p.append(R(64, y, 952, 128, card, 14, f"1 SOLID {'#243040' if not train else acc + '55'}"))
        p.append(R(64, y, 8, 128, acc if train else "#3A4658", 4))
        p.append(Tx(96, y + 20, d, 80, 40, ink, True))
        p.append(Tx(180, y + 18, kind, 320, 30, ink, True))
        p.append(Tx(180, y + 62, detail, 520, 24, dim))
        p.append(Tx(760, y + 40, "训练" if train else "恢复", 220, 24,
                    acc if train else dim, True, "RIGHT"))
    p.append(Tx(64, 1250, "本周总量 18 组 · 目标 RPE 7–8 · 睡眠 ≥7h", 900, 22, dim))
    return K.document(W, H, p, background=bg)

# ---------------------------------------------------------------- 6. book chapter opener
def case6():
    W, H = 1200, 1600
    bg, ink, dim, acc = "#FBF9F4", "#1A1A1A", "#6B6558", "#9A3412"
    p = [R(0, 0, W, H, bg)]
    p.append(R(120, 120, 2, 240, acc))
    p.append(Tx(160, 118, "第三章", 600, 26, acc, True))
    p.append(Tx(160, 168, "把信息", 900, 72, ink, True))
    p.append(Tx(160, 252, "排成队列", 900, 72, ink, True))
    p.append(Tx(160, 360, "关于秩序、留白与阅读节奏的一章", 860, 26, dim))
    p.append(R(160, 430, 880, 2, "#D9D2C4"))
    body = ["读者在页面上移动视线的方式，决定了信息应该以什么顺序出现。",
            "把标题、日期、正文、注释按同一条基线排好，视线就不需要反复跳跃。",
            "留白不是空的，它是段落之间的呼吸；每一处间距都应当可以被解释。"]
    for i, line in enumerate(body):
        p.append(Tx(160, 470 + i * 44, line, 880, 26, ink))
    p.append(R(160, 640, 880, 1, "#E5DFD2"))
    cols = [("01", "先分组", "同类收进一个单元。"),
            ("02", "再排序", "用字号与位置排序。"),
            ("03", "后对齐", "边缘落在同一线。")]
    for i, (n, t, d) in enumerate(cols):
        x = 160 + i * 300
        p.append(Tx(x, 690, n, 120, 30, acc, True))
        p.append(Tx(x, 736, t, 260, 30, ink, True))
        p.append(Tx(x, 782, d, 280, 20, dim))
    p.append(R(160, 900, 880, 1, "#E5DFD2"))
    for i in range(9):
        p.append(R(160, 940 + i * 46, 880 if i % 4 else 700, 10, "#EDE8DC"))
    p.append(Tx(160, 1420, "结构设计手册 · 第 3 章", 700, 22, dim))
    p.append(Tx(940, 1420, "063", 100, 22, dim, align="RIGHT"))
    return K.document(W, H, p, background=bg)

# ---------------------------------------------------------------- 7. festival clashfinder
def case7():
    W, H = 1600, 1000
    bg, ink, dim = "#0B0B0F", "#F5F5F7", "#8B8B96"
    p = [R(0, 0, W, H, bg)]
    p.append(Tx(64, 42, "河谷音乐节 · 第 9 届", 700, 24, dim))
    p.append(Tx(64, 76, "时间表", 800, 48, ink, True))
    stages = [("主舞台", "#F43F5E"), ("电子台", "#38BDF8"), ("民谣台", "#FBBF24")]
    for i, (name, col) in enumerate(stages):
        x = 300 + i * 420
        p.append(R(x, 160, 380, 46, col + "22", 8))
        p.append(Tx(x + 16, 168, name, 300, 24, col, True))
    hours = ["16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00"]
    for i, h in enumerate(hours):
        y = 220 + i * 104
        p.append(Tx(64, y, h, 200, 22, dim))
        p.append(R(300, y, 1220, 1, "#1C1C24"))
    acts = [(0, 0, 2, "潮汐", "#F43F5E"), (0, 2, 2, "北纬三十", "#F43F5E"), (0, 4, 2, "回声湖", "#F43F5E"),
            (1, 1, 2, "KAI", "#38BDF8"), (1, 3, 2, "夜航", "#38BDF8"), (1, 5, 2, "MONO", "#38BDF8"),
            (2, 0, 3, "木吉他", "#FBBF24"), (2, 3, 2, "旧信", "#FBBF24"), (2, 5, 2, "山雀", "#FBBF24")]
    for st, slot, span, name, col in acts:
        x = 300 + st * 420
        y = 224 + slot * 104
        h = span * 104 - 12
        p.append(R(x + 6, y, 368, h, col + "26", 10, f"1 SOLID {col}"))
        p.append(Tx(x + 22, y + 16, name, 330, 30, ink, True))
        p.append(Tx(x + 22, y + 58, f"{16 + slot:02d}:00–{16 + slot + span:02d}:00", 330, 20, col))
    p.append(Tx(64, 952, "演出时间以现场为准 · 电子台为主舞台的午夜接力", 1000, 20, dim))
    return K.document(W, H, p, background=bg)

# ---------------------------------------------------------------- 8. menu
def case8():
    W, H = 1080, 1600
    bg, ink, dim, acc = "#F7F2E8", "#231C14", "#7A6A56", "#8C5A2B"
    p = [R(0, 0, W, H, bg)]
    p.append(R(0, 0, W, 12, acc))
    p.append(Tx(72, 88, "时令菜单", 900, 30, acc, True))
    p.append(Tx(72, 132, "秋季 · 六道", 900, 62, ink, True))
    p.append(Tx(72, 216, "2026.10 – 2026.12 · 主厨 苏言", 900, 24, dim))
    p.append(R(72, 268, 936, 2, "#DCCFBB"))
    items = [("前菜", "炭烤南瓜 · 发酵奶油 · 榛子", "48"),
             ("汤", "栗子浓汤 · 烟熏培根沫", "42"),
             ("主菜", "慢烤羊肩 · 黑蒜 · 迷迭香汁", "168"),
             ("配菜", "烤根茎拼盘 · 香草盐", "38"),
             ("甜点", "梨子塔 · 肉桂冰淇淋", "56"),
             ("餐后", "手冲 · 单一产地", "32")]
    for i, (sec, desc, price) in enumerate(items):
        y = 320 + i * 150
        p.append(Tx(72, y, sec, 160, 22, acc, True))
        p.append(Tx(72, y + 36, desc, 700, 28, ink))
        p.append(Tx(812, y + 36, price, 196, 30, ink, True, "RIGHT"))
        p.append(R(72, y + 104, 936, 1, "#E6DCCB"))
    p.append(Tx(72, 1290, "另供：四杯配酒 +198 · 无酒精搭配 +128", 900, 24, dim))
    p.append(R(72, 1352, 936, 2, "#DCCFBB"))
    p.append(Tx(72, 1380, "每日 17:30 起 · 周一休", 600, 24, ink))
    p.append(Tx(72, 1428, "订位 menu.example / 0571-0000", 700, 22, dim))
    return K.document(W, H, p, background=bg)

# ---------------------------------------------------------------- 9. countdown poster
def case9():
    W, H = 1080, 1350
    bg, ink, acc = "#111827", "#F9FAFB", "#60A5FA"
    p = [R(0, 0, W, H, bg)]
    p.append(R(0, 1240, W, 110, "#0B1220"))
    p.append(Tx(80, 80, "PRE-ORDER · 11.11", 700, 24, acc, True))
    p.append(Tx(80, 150, "还有", 400, 40, "#9CA3AF"))
    p.append(Tx(80, 200, "07", 400, 190, ink, True))
    p.append(Tx(320, 280, "天", 200, 40, "#9CA3AF"))
    p.append(R(80, 470, 140, 6, acc))
    p.append(Tx(80, 510, "叠光 Pro", 900, 64, ink, True))
    p.append(Tx(80, 590, "把 12 个图层，收成一张图", 900, 28, "#9CA3AF"))
    specs = [("12", "图层上限"), ("4K", "导出分辨率"), ("60", "每秒帧率"), ("0.3s", "实时预览")]
    for i, (v, k) in enumerate(specs):
        x = 80 + (i % 2) * 460
        y = 700 + (i // 2) * 140
        p.append(Tx(x, y, v, 200, 54, acc, True))
        p.append(Tx(x, y + 66, k, 380, 22, "#9CA3AF"))
    p.append(R(80, 1010, 920, 2, "#1F2937"))
    p.append(Tx(80, 1036, "预售 11.11 00:00 · 首发价 ¥399", 700, 26, ink, True))
    p.append(Tx(80, 1094, "layerlight.example/pro", 700, 24, "#9CA3AF"))
    p.append(Tx(80, 1190, "叠光 Layerlight", 700, 22, "#6B7280"))
    return K.document(W, H, p, background=bg)

# ---------------------------------------------------------------- 10. year in review
def case10():
    W, H = 1080, 1920
    bg, ink, dim, acc = "#0A0F1A", "#F1F5F9", "#7C8CA3", "#22D3EE"
    p = [R(0, 0, W, H, bg)]
    p.append(Tx(80, 110, "2026", 600, 30, acc, True))
    p.append(Tx(80, 160, "我的这一年", 900, 64, ink, True))
    p.append(Tx(80, 250, "跑步 · 阅读 · 写作", 800, 26, dim))
    stats = [("跑步", "1,284", "公里"), ("阅读", "36", "本"), ("写作", "82", "篇")]
    for i, (k, v, u) in enumerate(stats):
        x = 80 + i * 320
        p.append(Tx(x, 360, k, 200, 24, dim))
        p.append(Tx(x, 398, v, 280, 64, ink, True))
        p.append(Tx(x + 180, 426, u, 80, 24, dim))
    p.append(R(80, 520, 920, 2, "#1E293B"))
    p.append(Tx(80, 552, "每月的跑步公里数", 700, 24, ink, True))
    vals = [72, 88, 104, 120, 96, 128, 140, 116, 132, 108, 94, 76]
    for i, v in enumerate(vals):
        h = int(v * 2.2)
        x = 92 + i * 74
        p.append(R(x, 900 - h, 46, h, acc if v >= 128 else "#1E6B7A", 8))
        p.append(Tx(x - 8, 912, f"{i+1}", 62, 18, dim, align="CENTER"))
    p.append(R(80, 960, 920, 2, "#1E293B"))
    p.append(Tx(80, 992, "最长的一次", 700, 24, dim))
    p.append(Tx(80, 1028, "32.4 公里", 700, 48, ink, True))
    p.append(Tx(80, 1090, "10 月 18 日 · 沿江往返", 700, 22, dim))
    p.append(R(80, 1150, 920, 2, "#1E293B"))
    p.append(Tx(80, 1180, "12 个月的记录密度", 700, 24, dim))
    dens = [0.55, 0.62, 0.7, 0.82, 0.6, 0.88, 0.95, 0.78, 0.9, 0.66, 0.58, 0.5]
    for i, dv in enumerate(dens):
        x = 80 + i * 76
        alpha = int(40 + dv * 200)
        p.append(R(x, 1222, 62, 62, f"#22D3EE{alpha:02X}", 10))
        p.append(Tx(x - 4, 1294, f"{i+1}", 70, 16, dim, align="CENTER"))
    p.append(R(80, 1350, 920, 2, "#1E293B"))
    p.append(Tx(80, 1382, "今年写下的句子", 700, 24, dim))
    p.append(Tx(80, 1424, "「把复杂的事拆开，", 900, 32, ink))
    p.append(Tx(80, 1470, "  再一件件做掉。」", 900, 32, ink))
    p.append(R(80, 1720, 920, 2, "#1E293B"))
    p.append(Tx(80, 1750, "年度回顾 · 自动生成", 700, 22, dim))
    p.append(Tx(80, 1790, "year.example/2026", 700, 22, acc))
    return K.document(W, H, p, background=bg)

CASES = [
    ("case-01", "机场离港信息屏", case1, (1920, 1080), "公共信息", "高密度表格 + 状态色，模拟航显大屏"),
    ("case-02", "手冲咖啡配方卡", case2, (1080, 1350), "餐饮/教程", "纸质卡片语言，步骤与水量并列"),
    ("case-03", "播客单集封面", case3, (1400, 1400), "媒体/封面", "大字排版 + 声波柱"),
    ("case-04", "城市轨道示意图", case4, (1600, 900), "交通/导览", "三线换乘的示意图语言"),
    ("case-05", "训练周计划", case5, (1080, 1350), "健身/计划", "七天纵向卡片，训练与恢复区分"),
    ("case-06", "图书章节开篇", case6, (1200, 1600), "出版/排版", "衬线阅读节奏与留白"),
    ("case-07", "音乐节时间表", case7, (1600, 1000), "活动/现场", "三舞台并行的时间网格"),
    ("case-08", "餐厅时令菜单", case8, (1080, 1600), "餐饮/菜单", "分节 + 右对齐价格"),
    ("case-09", "新品倒计时海报", case9, (1080, 1350), "营销/发布", "大数字与规格并列"),
    ("case-10", "个人年度回顾", case10, (1080, 1920), "个人/数据", "竖屏故事流 + 柱状图"),
]

logger = api.TaskLogger(TASK, TMP)
meta = []
ONLY = os.environ.get("B01_ONLY", "").split(",") if os.environ.get("B01_ONLY") else None
for cid, title, fn, size, cat, note in CASES:
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
    meta.append({"case": cid, "title": title, "category": cat, "size": list(size),
                 "note": note, "png": f"{cid}/final.png", "dsl": f"{cid}/final.snapshot",
                 "bytes": rec["response_bytes"], "request_id": rec["id"]})
api.write_json(TMP / "cases.json", meta)
print("rendered", len(meta))
