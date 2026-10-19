# -*- coding: utf-8 -*-
"""B01 · 十个真实场景用例 DSL 生成器。
每件独立尺寸/场景/视觉语言；全部纯 DSL 构造（无外部素材）。
"""
import json
import os
from pathlib import Path

TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
OUT = TASK_ROOT / "outputs" / RUN / "B01"
CJK = "Noto Sans CJK SC"
NUM = "Inter"


def fnum(v):
    s = f"{float(v):.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


def rect(s, x, y, w, h, color, radius=0, border=None):
    a = (f'<Positioned left="{fnum(x)}" top="{fnum(y)}" width="{fnum(w)}" '
         f'height="{fnum(h)}"><Container width="{fnum(w)}" height="{fnum(h)}"')
    if color:
        a += f' color="{color}"'
    if radius:
        a += f' borderRadius="{fnum(radius)}"'
    if border:
        a += f' border="{border}"'
    s.append(a + " /></Positioned>")


def txt(s, x, y, content, size, color, bold=False, family=CJK, align=None,
        box_w=None):
    sty = f'<Text fontSize="{fnum(size)}" color="{color}" fontFamily="{family}"'
    if bold:
        sty += ' fontStyle="BOLD"'
    if align:
        sty += f' textAlign="{align}"'
    sty += ">"
    if box_w is not None:
        s.append(f'<Positioned left="{fnum(x)}" top="{fnum(y)}" '
                 f'width="{fnum(box_w)}">{sty}{content}</Text></Positioned>')
    else:
        s.append(f'<Positioned left="{fnum(x)}" top="{fnum(y)}">{sty}'
                 f'{content}</Text></Positioned>')


def wrap_dsl(w, h, body, bg):
    return (f'<Snapshot background="{bg}" type="png">\n<Stack>\n'
            f'<SizedBox width="{w}" height="{h}" />\n' + "\n".join(body) +
            "\n</Stack>\n</Snapshot>\n")


def vline(s, x, y0, y1, color, wd=2):
    rect(s, x, y0, wd, y1 - y0, color)


def hline(s, x0, x1, y, color, ht=2):
    rect(s, x0, y, x1 - x0, ht, color)


def pill(s, x, y, w, h, color, label, fsize, fcolor, bold=True,
         font=CJK, radius=None):
    rect(s, x, y, w, h, color, radius if radius is not None else h / 2)
    txt(s, x, y + (h - fsize - 2) / 2, label, fsize, fcolor, bold=bold,
        family=font, align="CENTER", box_w=w)


def diamonds(s, x0, x1, y, band, color):
    """半高菱形带（象征高警示）。"""
    step = (y + band) - (y + band) * 0  # placeholder
    d = band * 0.72
    span = x1 - x0
    i = 0
    x = x0
    while x + d / 2 < x1:
        cx, cy = x, y + band / 2
        rot = (f'<Transform matrix="(0.707107,-0.707107,0,0,0.707107,0.707107,'
               f'0,0,0,0,1,0,0,0,0,1)" origin="({fnum(d / 2)},{fnum(d / 2)})">')
        inner = (f'<Container width="{fnum(d)}" height="{fnum(d)}" '
                 f'color="{color}" />')
        s.append(f'<Positioned left="{fnum(cx - d / 2)}" top="{fnum(cy - d / 2)}" '
                 f'width="{fnum(d)}" height="{fnum(d)}">{rot}{inner}'
                 f'</Transform></Positioned>')
        x += d * 1.35
        i += 1
    return i


def bar_row(s, x, y, w_full, w_val, h, color, track):
    rect(s, x, y, w_full, h, track, h / 2)
    if w_val > 0:
        rect(s, x, y, w_val, h, color, h / 2)


def citrus(s, cx, cy, r, body="#FF9A3C", deep="#E07B18", ring="#FFC154",
           leaf=True):
    rect(s, cx - r, cy - r, 2 * r, 2 * r, body, r,
         f"6 SOLID {deep}")
    s.append(f'<Positioned left="{fnum(cx - r * 0.72)}" top="{fnum(cy - r * 0.72)}" '
             f'width="{fnum(r * 1.44)}" height="{fnum(r * 1.44)}">'
             f'<Container width="{fnum(r * 1.44)}" height="{fnum(r * 1.44)}" '
             f'color="{ring}" borderRadius="{fnum(r * 0.72)}" /></Positioned>')
    s.append(f'<Positioned left="{fnum(cx - r * 0.5)}" top="{fnum(cy - r * 0.5)}" '
             f'width="{fnum(r)}" height="{fnum(r)}">'
             f'<Container width="{fnum(r)}" height="{fnum(r)}" color="{body}" '
             f'borderRadius="{fnum(r / 2)}" /></Positioned>')
    if leaf:
        lw, lh = r * 0.6, r * 0.2
        s.append(f'<Positioned left="{fnum(cx + r * 0.35 - lw / 2)}" '
                 f'top="{fnum(cy - r - lh / 2)}" width="{fnum(lw)}" '
                 f'height="{fnum(lh)}">'
                 f'<Transform matrix="(0.866,-0.5,0,0,0.5,0.866,0,0,0,0,1,0,0,0,0,1)" '
                 f'origin="({fnum(lw / 2)},{fnum(lh / 2)})">'
                 f'<Container width="{fnum(lw)}" height="{fnum(lh)}" '
                 f'color="#3E8E4E" borderRadius="{fnum(lh / 2)}" />'
                 f'</Transform></Positioned>')


CASES = []


def case(mark, w, h):
    def deco(fn):
        CASES.append((mark, w, h, fn))
        return fn
    return deco


# ---------------- case-01 机场登机口实时看板 1920×1080 ----------------
@case("case-01", 1920, 1080)
def c01():
    BG, PANEL, P2 = "#071A2E", "#0E2B47", "#123a5e"
    CYA, AMB, GRN, RED, TXT, SUB, MUT = ("#45D0FF", "#FFC154", "#43E5A0",
                                         "#FF7A78", "#EAF6FF", "#9CC3E8", "#6E91B8")
    s = [f'<Container width="1920" height="1080" color="{BG}" />']
    rect(s, 0, 0, 1920, 6, CYA)
    txt(s, 60, 42, "云港湾国际机场 · T2 出发", 42, TXT, bold=True)
    txt(s, 60, 100, "登机口状态看板 | 值机截止前 45 分钟广播 | 示例演示数据",
        22, SUB)
    txt(s, 1580, 52, "10:24", 64, CYA, bold=True, family=NUM)
    txt(s, 1750, 120, "UTC+8", 20, MUT, family=NUM)
    bar_row(s, 60, 156, 1800, 1800 * 0.71, 8, CYA, P2)
    txt(s, 60, 172, "今日吞吐 71%（10:24 / 计划 96 班）", 20, MUT, family=NUM)
    heads = ["航班", "目的地", "登机口", "计划", "状态", "值机进度"]
    cols = [60, 300, 700, 850, 1010, 1310]
    txt(s, cols[0], 226, heads[0], 20, MUT); txt(s, cols[1], 226, heads[1], 20, MUT)
    txt(s, cols[2], 226, heads[2], 20, MUT); txt(s, cols[3], 226, heads[3], 20, MUT)
    txt(s, cols[4], 226, heads[4], 20, MUT); txt(s, cols[5], 226, heads[5], 20, MUT)
    hline(s, 40, 1880, 268, PANEL, 2)
    rows = [
        ("YL238", "新加坡", "A12", "10:35", "登机中", 0.82),
        ("YL117", "成都", "B04", "10:55", "值机开放", 0.41),
        ("YL902", "东京成田", "A21", "11:10", "值机开放", 0.22),
        ("YL065", "昆明", "C07", "11:25", "准点", 0.10),
        ("YL833", "厦门", "B15", "11:40", "准点", 0.02),
        ("YL511", "清迈", "A09", "12:05", "计划", 0.0),
        ("YL456", "莫斯科", "C02", "12:30", "延误 35 分", 0.35),
        ("YL208", "海防", "D03", "12:45", "计划", 0.0),
    ]
    ry = 290
    for i, (fl, dest, gate, tm, st, p) in enumerate(rows):
        rect(s, 40, ry, 1800, 84, PANEL if i % 2 == 0 else P2, 10)
        col = (GRN if st in ("准点", "值机开放") else
               (CYA if st == "登机中" else RED))
        txt(s, cols[0] + 24, ry + 14, fl, 30, TXT, bold=True, family=NUM)
        txt(s, cols[1], ry + 24, dest, 26, TXT)
        txt(s, cols[2], ry + 26, gate, 24, SUB, family=NUM)
        txt(s, cols[3], ry + 26, tm, 24, SUB, family=NUM)
        pill(s, cols[4], ry + 24, 150, 36, "#10241B" if GRN == col else
             ("#132A44" if col == CYA else "#2A1226"), st, 20, col)
        bar_row(s, cols[5], ry + 32, 440, 440 * p, 20, "#3AA9D8" if p >= 0.7
                else (AMB if p >= 0.45 else P2), "#0B1E33")
        txt(s, cols[5] + 452, ry + 30, f"{int(p * 100)}%", 20, MUT, family=NUM)
        ry += 94
    rect(s, 40, 1032, 1800, 2, PANEL)
    txt(s, 60, 1044, "数据源：机场运营系统演示接口（示例） · 每 30 秒刷新",
        20, MUT)
    txt(s, 1520, 1044, "YL = Yungleap 游跃航空（虚构）", 20, MUT)
    return wrap_dsl(1920, 1080, s, BG)


# ---------------- case-02 社区疫苗诊所叫号屏 1080×1920 ----------------
@case("case-02", 1080, 1920)
def c02():
    BG, PANEL = "#04241F", "#0B3A31"
    MINT, AMB, TXT, SUB, MUT = "#4BE3A4", "#FFC154", "#EFFFF8", "#93CFC0", "#5C8A7E"
    s = [f'<Container width="1080" height="1920" color="{BG}" />']
    rect(s, 0, 0, 1080, 10, MINT)
    txt(s, 60, 60, "澜川社区卫生服务中心 · 接种叫号", 34, TXT, bold=True)
    txt(s, 60, 112, "流感疫苗专场 · 请在候诊区留意屏幕与广播", 22, SUB)
    rect(s, 60, 170, 960, 400, PANEL, 24, f"2 SOLID {MINT}")
    txt(s, 60, 210, "当前叫号", 24, MUT)
    txt(s, 60, 246, "A-042", 170, MINT, bold=True, family=NUM)
    txt(s, 640, 430, "请前往 3 号接种台", 36, TXT, bold=True)
    txt(s, 640, 492, "叫号 10:24:07", 22, SUB, family=NUM)
    steps = ["登记", "预检", "接种", "留观 30 分"]
    sw = (960 - 3 * 24) / 4
    for i, stq in enumerate(steps):
        x = 60 + i * (sw + 24)
        rect(s, x, 610, sw, 88, "#0D4A3E", 14)
        rect(s, x, 610, sw, 6, MINT if i <= 2 else "#1D5C4F", 14)
        txt(s, x, 640, stq, 24, TXT if i <= 2 else MUT, bold=(i <= 2),
            align="CENTER", box_w=sw)
    txt(s, 60, 760, "即将叫号", 24, MUT)
    q = ["A-043", "A-044", "A-045", "A-046", "A-047"]
    yy = 804
    for i, num in enumerate(q):
        rect(s, 60, yy, 960, 96, PANEL if i % 2 == 0 else "#0A332B", 12)
        rect(s, 60, yy, 6, 96, MINT if i == 0 else "#16584A", 12)
        txt(s, 92, yy + 24, num, 40, TXT if i == 0 else SUB, bold=(i == 0),
            family=NUM)
        txt(s, 320, yy + 34, f"已等候 {14 + i * 6} 分钟", 22, SUB)
        txt(s, 760, yy + 30, f"接种台 {(i % 3) + 2} 号", 24, AMB)
        yy += 108
    rect(s, 60, 1352, 465, 240, PANEL, 16)
    rect(s, 548, 1352, 472, 240, PANEL, 16)
    txt(s, 88, 1380, "今日已接种", 22, MUT)
    txt(s, 88, 1420, "328", 84, MINT, bold=True, family=NUM)
    txt(s, 88, 1524, "剂（目标 500 剂）", 22, SUB)
    txt(s, 576, 1380, "平均等待", 22, MUT)
    txt(s, 576, 1420, "23", 84, AMB, bold=True, family=NUM)
    txt(s, 576, 1524, "分钟（含留观前）", 22, SUB)
    bar_row(s, 60, 1626, 960, 960 * 328 / 500, 18, MINT, "#0A332B")
    txt(s, 60, 1656, "65.6%", 20, MUT, family=NUM)
    txt(s, 60, 1830, "演示数据 · 澜川社区（虚构） · 服务台：一楼大厅东侧",
        20, MUT)
    return wrap_dsl(1080, 1920, s, BG)


# ---------------- case-03 咖啡烘焙批次卡 900×500 ----------------
@case("case-03", 900, 500)
def c03():
    PAPER, INK, SOFT, ACC, LINE = "#F3ECDD", "#3A2A1C", "#6B543C", "#B5622D", "#D8C7AA"
    s = [f'<Container width="900" height="500" color="{PAPER}" />']
    rect(s, 24, 24, 852, 452, "#00000000" if False else PAPER, 2,
         f"3 SOLID {INK}")
    rect(s, 34, 34, 832, 432, "#00000000" if False else PAPER, 2, None
         if True else None)
    vline(s, 38, 38, 462, LINE, 1)
    vline(s, 862, 38, 462, LINE, 1)
    vline(s, 38, 38, 38, LINE, 824)
    txt(s, 70, 62, "叠光手冲", 44, INK, bold=True)
    txt(s, 280, 74, "SHANDIE ROASTWORKS", 20, SOFT, family=NUM)
    rect(s, 70, 132, 240, 34, ACC, 4)
    txt(s, 70, 138, "单一产地 · 浅中烘", 20, PAPER, bold=True,
        align="CENTER", box_w=240)
    txt(s, 70, 190, "云南 保山 · 山雾庄园", 34, INK, bold=True)
    txt(s, 70, 240, "批次 NB-20261018-07", 26, INK, family=NUM)
    rows = [("豆种", "铁皮卡（水洗）"), ("干燥度", "11.4%"), ("烘焙度", "浅中 City+"),
            ("杯测", "88.25 分 · 茉莉白桃"), ("养豆期", "第 5–14 天最佳")]
    yy = 292
    for k, v in rows:
        txt(s, 70, yy, k, 20, SOFT)
        txt(s, 210, yy, v, 22, INK)
        yy += 30
    # 火力曲线小图
    x0, y0, wd, ht = 560, 250, 250, 120
    rect(s, x0 - 12, y0 - 30, wd + 24, ht + 44, "#FBF6EA", 6, f"1 SOLID {LINE}")
    curve = [0.30, 0.42, 0.52, 0.62, 0.74, 0.86, 0.95, 1.0, 0.9, 0.7]
    bw = wd / 3 / 10
    for i, v in enumerate(curve):
        bh = v * ht
        rect(s, x0 - 12 + 12 + i * bw, y0 + ht - bh, bw * 0.62, bh,
             ACC if i < 7 else "#8C6A4A", 2)
    txt(s, x0 - 12, y0 + ht + 2, "烘焙火力曲线（示意）", 17, SOFT)
    # 条码
    bx, by = 560, 396
    i = 0
    x = bx
    while x < bx + 220 - 8:
        bw2 = 3 + ((i * 7) % 5) * 2.2
        rect(s, x, by, bw2, 40, INK)
        x += bw2 + 3.2 + ((i * 5) % 4) * 1.6
        i += 1
    txt(s, 596, 440, "6 920214 202618", 20, INK, family=NUM)
    txt(s, 70, 444, "风味：茉莉 / 白桃 / 红茶尾韵 · 烘于 2026-10-18 07:20 · 200 g",
        18, SOFT)
    txt(s, 850, 62, "01", 22, SOFT, family=NUM, align="RIGHT", box_w=None) \
        if False else None
    return wrap_dsl(900, 500, s, PAPER)


# ---------------- case-04 马拉松配速分段海报 1200×2000 ----------------
@case("case-04", 1200, 2000)
def c04():
    BG, P1, P2, TXT, SUB, MUT = "#16092E", "#221045", "#2B1558", "#F4EEFF", "#C0A9EF", "#7A63B3"
    NEON, AMB, RED = "#7CFFD4", "#FFC154", "#FF7A78"
    s = [f'<Container width="1200" height="2000" color="{BG}" />']
    rect(s, 0, 0, 1200, 14, NEON)
    txt(s, 70, 60, "环湾夜跑城市马拉松", 56, TXT, bold=True)
    txt(s, 70, 138, "2026-11-15 19:00 鸣枪 | 起终点：湾心广场 | 全马 42.195 km",
        24, SUB)
    pill(s, 70, 190, 300, 54, NEON, "关门 6 小时 15 分", 24, "#0C2A24")
    pill(s, 390, 190, 240, 54, "#2A1550", "配速 8:52 /km", 24, NEON)
    # 分段表
    txt(s, 70, 286, "分段配速与关门时刻", 30, TXT, bold=True)
    seg_names = ["湾心广场", "灯塔公园", "跨湾桥", "渔人码头", "湿地栈道",
                 "半程折返", "大学城", "老城巷弄", "港湾大桥", "湾心冲刺"]
    segs = [("5K", 0.471), ("10K", 0.942), ("15K", 1.414), ("20K", 1.885),
            ("25K", 2.356), ("30K", 2.827), ("35K", 3.299), ("40K", 3.770),
            ("42.195K", 3.973), ("终点", 4.444)]
    # 距离列（累计） + 预计时刻（按 345 目标）
    y = 346
    times = ["00:41", "01:24", "02:09", "02:55", "03:44", "04:38",
             "05:41", "06:44 *", "07:32 *", "07:46"]
    accs = ["5 K", "10 K", "15 K", "20 K", "25 K", "30 K", "35 K", "40 K",
            "42 K", "42.195 K"]
    txt(s, 70, y - 26, "PC", 18, MUT, family=NUM)
    txt(s, 180, y - 26, "地点", 18, MUT)
    txt(s, 470, y - 26, "累计", 18, MUT)
    txt(s, 640, y - 26, "预计通过", 18, MUT)
    txt(s, 830, y - 26, "强度", 18, MUT)
    hline(s, 60, 1140, y + 6, P2, 2)
    y += 40
    for i, ((k, ratio), t, a, nm) in enumerate(zip(segs, times, accs, seg_names)):
        rect(s, 50, y, 1100, 78, P1 if i % 2 == 0 else P2, 10)
        txt(s, 70, y + 22, f"{i + 1:02d}", 24, MUT, family=NUM)
        txt(s, 180, y + 22, nm, 26, TXT, bold=(i in (4, 9)))
        txt(s, 470, y + 24, a, 24, SUB, family=NUM)
        txt(s, 640, y + 22, t, 26, NEON if not t.endswith("*") else RED,
            bold=True, family=NUM)
        # 强度条
        inten = [0.35, 0.5, 0.42, 0.55, 0.65, 0.72, 0.8, 0.9, 0.72, 0.55][i]
        bar_row(s, 830, y + 30, 260, 260 * inten, 16,
                AMB if inten > 0.68 else NEON, "#1A0D38")
        if t.endswith("*"):
            txt(s, 700, y + 52, "警示关门收紧", 15, RED)
        y += 88
    # 海拔剖面
    txt(s, 70, y + 16, "赛道海拔（每 4 km 抽样）", 30, TXT, bold=True)
    px, py, pw, ph = 70, y + 76, 1060, 260
    rect(s, px, py, pw, ph, P1, 12, f"1 SOLID {P2}")
    prof = [12, 14, 22, 47, 60, 38, 20, 27, 44, 70, 80, 76, 52, 30]
    bw = pw / 14
    for i, v in enumerate(prof):
        bh = v / 80 * (ph - 60)
        rect(s, px + 12 + i * bw, py + ph - 34 - bh, bw - 10, bh,
             NEON if (i % 3) else P2, 6)
    txt(s, px + 8, py + ph - 30, "0 m", 18, MUT, family=NUM)
    txt(s, px + pw - 60, py + ph - 30, "80 m", 18, MUT, family=NUM)
    txt(s, px + 8, py + 8, "最高段：港湾大桥爬升段（60–80 m）", 18, SUB)
    txt(s, 70, 1940, "演示数据 · 叠光路跑俱乐部 · 让每公里都被看见", 20, MUT)
    return wrap_dsl(1200, 2000, s, BG)


# ---------------- case-05 扶梯检修警示牌 A4 794×1123 ----------------
@case("case-05", 794, 1123)
def c05():
    Y, K, R, TXT = "#F7C600", "#111111", "#D32531", "#111111"
    s = [f'<Container width="794" height="1123" color="{Y}" />']
    rect(s, 24, 24, 746, 26, K)  # 顶部黑带
    # 菱形警示带
    diamonds(s, 48, 746, 26, 26, Y)
    diamonds(s, 48, 746, 1082, 24, K)
    txt(s, 60, 96, "! 检修中 !", 0, K, bold=True) if False else None
    rect(s, 247, 66, 300, 74, R, 8)
    txt(s, 247, 86, "设备检修", 34, "#FFFFFF", bold=True, align="CENTER",
        box_w=300)
    txt(s, 60, 172, "3 号自动扶梯", 62, K, bold=True)
    txt(s, 60, 258, "今日暂停使用", 62, K, bold=True)
    hline(s, 48, 746, 342, K, 8)
    txt(s, 60, 372, "检修时段：10-18（周六） 22:00 – 次日 06:00", 30, TXT,
        bold=True)
    txt(s, 60, 424, "请改用 1 / 2 号扶梯或东侧无障碍电梯", 28, TXT)
    # 禁行大标
    rect(s, 60, 500, 674, 220, K, 10)
    rect(s, 96, 536, 148, 148, Y, 74)
    rect(s, 96 + 34, 536 + 66, 80, 16, K)  # 禁止横杠（简形）
    txt(s, 272, 548, "禁止乘人", 44, Y, bold=True)
    txt(s, 272, 612, "设备已断电锁定", 30, "#FFFFFF")
    txt(s, 272, 654, "负责人：王工（安全部）", 26, "#FFFFFF")
    # 三条提示行
    tips = ["扶梯运行可能与检修作业发生干涉",
            "随身行李请走垂直电梯或楼梯",
            "发现异常立即联系值班室 8888"]
    yy = 756
    for i, tp in enumerate(tips):
        pill(s, 60, yy, 46, 46, K, f"{i + 1}", 26, Y, font=NUM)
        txt(s, 126, yy + 8, tp, 26, TXT)
        yy += 66
    rect(s, 60, 966, 674, 96, "#FFFFFF", 8, f"2 SOLID {K}")
    txt(s, 84, 984, "澜川地铁 2 号线 · 车站安全告示（示例演示）", 24, TXT,
        bold=True)
    txt(s, 84, 1022, "报修电话 0900-8888 · 票务服务台与站台两侧均设绕行指引",
        22, TXT)
    return wrap_dsl(794, 1123, s, Y)


# ---------------- case-06 演出 LED 侧屏曲目单 1366×768 ----------------
@case("case-06", 1366, 768)
def c06():
    BG, TXT, MUT = "#050505", "#FFEFFB", "#8E7796"
    MAG, CYA2, AMB = "#FF3EA5", "#37E1E1", "#FFC154"
    s = [f'<Container width="1366" height="768" color="{BG}" />']
    # 顶部荧光条
    rect(s, 0, 0, 1366, 4, MAG)
    txt(s, 56, 30, "叠光声场 · 2026 巡演 杭州", 40, TXT, bold=True)
    txt(s, 56, 92, "夜间场 LIVE | 20:38 | 第 7 / 12 首", 22, MAG)
    txt(s, 1080, 34, "SETLIST", 26, MUT, family=NUM)
    rows = [("01", "开场：声呐", "3'12", False), ("02", "叠光", "4'02", False),
            ("03", "夜航西", "3'48", False), ("04", "灰域", "5'06", False),
            ("05", "潮汐广播", "4'20", False), ("06", "万花筒", "3'30", False),
            ("07", "午夜霓虹", "4'44", True), ("08", "安可预埋", "2'58", False)]
    y = 138
    for code, song, dur, live in rows:
        rect(s, 40, y, 880, 66, "#120A16" if live else "#080409", 10)
        rect(s, 40, y, 6, 66, MAG if live else "#241528", 10)
        txt(s, 66, y + 12, code, 26, MAG if live else MUT, bold=True,
            family=NUM)
        txt(s, 150, y + 10, song, 30, TXT if live else "#B9A7C6",
            bold=live)
        txt(s, 760, y + 18, dur, 22, MAG if live else MUT, family=NUM)
        if live:
            pill(s, 640, y + 16, 92, 34, MAG, "LIVE", 18, "#20070F", font=NUM)
        y += 74
    # 舞台信息区（右）
    rect(s, 952, 138, 380, 440, "#0A0710", 14, f"1 SOLID #2A1B33")
    txt(s, 984, 166, "NEXT", 22, CYA2, family=NUM)
    txt(s, 984, 200, "午夜霓虹 → 万花筒", 26, TXT, bold=True)
    txt(s, 984, 258, "BPM 128 · D 大调", 22, SUB if False else "#B9A7C6")
    # VU 条装饰
    heights = [0.4, 0.7, 0.5, 0.9, 0.65, 0.8, 0.35, 0.6]
    for i, v in enumerate(heights):
        h2 = int(v * 150)
        rect(s, 984 + i * 42, 500 - h2, 26, h2, MAG if i % 2 else CYA2, 6)
    txt(s, 984, 516, "现场声压（装饰可视化）", 18, MUT)
    rect(s, 952, 610, 380, 118, "#0A0710", 14, "1 SOLID #2A1B33")
    txt(s, 984, 628, "舞台提示", 22, AMB, bold=True)
    txt(s, 984, 662, "08 结束后全暗 8 秒 → 灯阵换色", 20, TXT)
    txt(s, 56, 726, "示例曲目 · 叠光声场（虚构乐队） · 屏幕比例 16:9", 18, MUT)
    return wrap_dsl(1366, 768, s, BG)


# ---------------- case-07 生鲜电商柑橘主图 2000×2000 ----------------
@case("case-07", 2000, 2000)
def c07():
    BG, TXT, MUT = "#FFF6E8", "#2B1A08", "#8A6A45"
    ORG, DEEP, GRN = "#FF8A2E", "#D95F0E", "#3E8E4E"
    s = [f'<Container width="2000" height="2000" color="{BG}" />']
    # 斜切色块
    rect(s, 0, 1480, 2000, 520, ORG)
    # 柑橘群（右上区，避让左侧文案与徽章列）
    citrus(s, 1300, 640, 330)
    citrus(s, 1750, 940, 240)
    citrus(s, 1120, 1080, 190, leaf=True)
    # 品牌与标题
    pill(s, 120, 120, 320, 72, DEEP, "鲜橙季 · 果园直供", 30, "#FFF6E8")
    txt(s, 120, 240, "赣南 脐橙", 120, TXT, bold=True)
    txt(s, 120, 388, "树上自然熟 · 甜度 13°+ · 皮薄好剥", 46, DEEP, bold=True)
    txt(s, 120, 462, "示范主图：数据与价签均为演示，不构成真实交易",
        28, MUT)
    txt(s, 120, 580, "产地直供：赣南果农合作社（示例）", 30, TXT)
    txt(s, 120, 650, "分级发货：果径 65–75 mm · 每箱附糖酸检测卡", 30, TXT)
    # 促销徽章列（左列，避开柑橘群）
    badges = ["现摘现发", "坏果包赔", "顺丰包邮"]
    for i, b in enumerate(badges):
        x = 120 + i * 270
        rect(s, x, 800, 240, 84, "#FFFFFF", 42, f"4 SOLID {ORG}")
        txt(s, x, 822, b, 30, DEEP, bold=True, align="CENTER", box_w=240)
    # 促销价区（色块上）
    txt(s, 120, 1548, "大促价", 34, "#FFE9C7")
    txt(s, 120, 1600, "¥29, .9", 0, TXT) if False else None
    txt(s, 110, 1596, "¥", 64, "#FFFFFF", bold=True, family=NUM)
    txt(s, 168, 1568, "29.9", 128, "#FFFFFF", bold=True, family=NUM)
    txt(s, 470, 1656, "/ 5 斤装（约 12 果）", 34, "#FFE9C7")
    txt(s, 120, 1760, "到手价：叠券再减 5 元", 34, "#FFFFFF", bold=True)
    # 倒计时
    pill(s, 120, 1840, 520, 90, DEEP, "限时 8 小时 24 分", 38,
         "#FFE9C7", radius=18)
    pill(s, 680, 1840, 560, 90, "#FFFFFF", "立即抢购", 38, DEEP, bold=True,
         radius=18)
    txt(s, 1300, 1880, "演示 · 叠光鲜果虚构品牌", 28, "#FFE9C7")
    return wrap_dsl(2000, 2000, s, BG)


# ---------------- case-08 火锅双人菜单桌卡 1080×1620 ----------------
@case("case-08", 1080, 1620)
def c08():
    BG, PAPER, INK, SOFT, RED, GOLD = "#51160F", "#FBF3E4", "#2E1A10", "#8A6F58", "#C3271F", "#B98A2F"
    s = [f'<Container width="1080" height="1620" color="{BG}" />']
    rect(s, 40, 40, 1000, 1540, PAPER, 6)
    rect(s, 54, 54, 972, 1512, "#00000000" if False else PAPER, 4,
         f"2 SOLID {GOLD}")
    txt(s, 120, 96, "山雾老灶", 64, INK, bold=True)
    txt(s, 120, 178, "双人套餐 · 示例菜单（菜品以当日出清为准）", 22, SOFT)
    rect(s, 120, 224, 60, 12, RED)
    # 锅底
    sec = [("锅底", ["老坛酸汤鸳鸯 45", "九宫格红汤 58"]),
           ("肉类", ["吊龙伴 36", "雪花肥牛 42", "手打虾滑 38"]),
           ("蔬菜豆品", ["鲜切冬瓜 9", "贡菜 12", "鲜豆花 10"]),
           ("小吃主食", ["红糖糍粑 16", "现炸酥肉 22", "素面 8"])]
    y = 268
    for name, items in sec:
        txt(s, 120, y, name, 30, INK, bold=True)
        hline(s, 120, 960, y + 48, "#E7D9BF", 2)
        yy = y + 66
        for it in items:
            dot = it.rfind(" ")
            nm, pr = it[:dot], it[dot + 1:]
            txt(s, 148, yy, nm, 26, INK)
            txt(s, 700, yy, "· · · · · · ·", 20, GOLD)
            rect(s, 840, yy + 4, 120, 40, "#F5E7CC", 20)
            txt(s, 840, yy + 9, f"¥{pr}", 24, RED, bold=True, family=NUM,
                align="CENTER", box_w=120)
            yy += 52
        y = yy + 30
    # 套餐价签
    rect(s, 700, 1300, 256, 130, RED, 12)
    txt(s, 700, 1316, "双人套餐", 26, "#FBF3E4", bold=True,
        align="CENTER", box_w=256)
    txt(s, 700, 1352, "¥158", 56, "#FFFFFF", bold=True, family=NUM,
        align="CENTER", box_w=256)
    txt(s, 120, 1338, "加锅底换购yat?") if False else None
    txt(s, 120, 1330, "全单可任选锅底二选一", 24, SOFT)
    txt(s, 120, 1380, "毛肚/鸭血可 +19 换购", 24, SOFT)
    txt(s, 120, 1470, "堂食桌卡（演示菜单 · 山雾老灶为虚构品牌）", 20, SOFT)
    txt(s, 120, 1510, "价格单位：人民币元 · 服务费另计见前台公示", 20, SOFT)
    return wrap_dsl(1080, 1620, s, BG)


# ---------------- case-09 天气预警手机推送 720×1480 ----------------
@case("case-09", 720, 1480)
def c09():
    BG, CARD, TXT, SUB, MUT = "#101319", "#1B2027", "#EAF1FF", "#A7B7CB", "#66768C"
    RED, ORG, CY3 = "#E2483D", "#F08A24", "#3DC9F0"
    s = [f'<Container width="720" height="1480" color="{BG}" />']
    # 状态栏
    txt(s, 44, 30, "10:24", 26, TXT, bold=True, family=NUM)
    txt(s, 560, 32, "▲ ▮ ▮", 22, TXT, align="RIGHT", box_w=None) if False else None
    txt(s, 596, 30, "88%", 22, TXT, family=NUM)
    pill(s, 300, 20, 120, 36, "#000000", "", 16, TXT)
    txt(s, 44, 120, "通知", 44, TXT, bold=True)
    txt(s, 620, 130, "全部已读", 22, CY3, family=NUM)
    # 卡一：台风红警（展开）
    rect(s, 24, 196, 672, 420, CARD, 22)
    rect(s, 24, 196, 8, 420, RED, 22)
    txt(s, 60, 220, "天气预警 · 叠光天气", 24, TXT, bold=True)
    txt(s, 60, 258, "现在", 18, MUT, family=NUM)
    rect(s, 60, 292, 612, 62, "#3A1414", 12)
    txt(s, 76, 306, "台风红色预警", 32, "#FF9E96", bold=True)
    txt(s, 60, 376, "台风『山雾』（强台风级）预计明日 14 时前后在澜湾", 24, TXT)
    txt(s, 60, 414, "一带登陆，阵风 14–16 级，请立即停止户外活动并", 24, TXT)
    txt(s, 60, 452, "转移至室内避险。", 24, TXT)
    pill(s, 60, 496, 190, 56, RED, "查看避险指南", 22, "#FFFFFF")
    pill(s, 266, 496, 190, 56, "#232A33", "稍后提醒", 22, SUB)
    txt(s, 472, 508, "· 静音关", 20, MUT, family=NUM) if False else None
    txt(s, 480, 510, "·", 22, MUT) if False else None
    txt(s, 60, 574, "来源：澜湾市气象台 10:22 发布", 18, MUT)
    # 卡二：暴雨橙色（折叠）
    rect(s, 24, 640, 672, 132, CARD, 22)
    rect(s, 24, 640, 8, 132, ORG, 22)
    txt(s, 60, 664, "天气预警 · 叠光天气", 22, TXT, bold=True)
    txt(s, 512, 666, "8:12", 18, MUT, family=NUM)
    txt(s, 60, 700, "暴雨橙色预警：未来 3 小时城区累计降水将达", 22, TXT)
    txt(s, 60, 730, "80 mm，低洼路段请绕行", 22, TXT)
    # 卡三：普通通知（折叠）
    rect(s, 24, 796, 672, 108, CARD, 22)
    txt(s, 60, 820, "社区 · 叠光小区物业", 22, TXT, bold=True)
    txt(s, 560, 822, "7:40", 18, MUT, family=NUM)
    txt(s, 60, 854, "地库 B2 入口今日 22:00 起防汛挡板安装", 20, SUB)
    # 快捷操作 chips
    txt(s, 44, 950, "快捷避险", 30, TXT, bold=True)
    chip_data = [("避险清单", "#232A33", CY3), ("最近应急避难点", "#232A33", CY3),
                 ("家人位置共享", "#232A33", CY3), ("停运线路", "#3A1C08", "#FFC154")]
    cx, cy = 44, 1000
    for lab, bgc, fcc in chip_data:
        w = 24 + 22 * sum(2 if ord(ch) > 0x2E80 else 1 for ch in lab)
        pill(s, cx, cy, w, 64, bgc, lab, 24, fcc, bold=False, radius=32)
        cx += w + 20
        if cx > 560:
            cx, cy = 44, cy + 84
    rect(s, 24, 1230, 672, 2, "#232A33")
    txt(s, 44, 1260, "示例演示 · 叠光天气为虚构应用 · 预警样式参照真实分级",
        20, MUT)
    txt(s, 44, 1296, "红/橙预警按发布机构原文处理，不夸大不改写", 20, MUT)
    rect(s, 240, 1416, 240, 8, MUT, 4)
    return wrap_dsl(720, 1480, s, BG)


# ---------------- case-10 手机银行月度账单 720×1280 ----------------
@case("case-10", 720, 1280)
def c10():
    BG, P1, P2, TXT, SUB, MUT = "#0B1030", "#131A4A", "#1B2460", "#EEF3FF", "#9FB0E8", "#5F6FA6"
    TEAL, AMB, RED = "#3FE0C8", "#FFC154", "#FF8A80"
    s = [f'<Container width="720" height="1280" color="{BG}" />']
    txt(s, 40, 40, "叠光钱包", 30, TXT, bold=True)
    txt(s, 40, 88, "10 月账单速览（演示数据）", 22, SUB)
    rect(s, 40, 136, 640, 210, P1, 18, f"1 SOLID {P2}")
    txt(s, 76, 164, "本月支出", 24, MUT)
    txt(s, 76, 200, "¥4,286", 76, TXT, bold=True, family=NUM)
    txt(s, 380, 164, "收入 ¥8,900", 22, TEAL)
    pill(s, 380, 204, 170, 52, "#123F3A", "环比 −12%", 22, TEAL)
    bar_row(s, 76, 292, 568, 568 * 0.48, 12, TEAL, P2)
    txt(s, 76, 310, "预算已用 48%（¥5,000 / ¥10,400）", 20, SUB)
    txt(s, 40, 396, "分类支出", 28, TXT, bold=True)
    cats = [("餐饮", 1120, 0.28, "#3FE0C8"), ("通勤", 640, 0.16, "#FFC154"),
            ("居住", 980, 0.24, "#4CC2FF"), ("购物", 720, 0.18, "#FF8A80"),
            ("娱乐", 430, 0.10, "#B18CFF"), ("其他", 396, 0.11, "#5F6FA6")]
    y = 448
    for nm, amt, frac, col in cats:
        txt(s, 40, y, nm, 24, TXT)
        txt(s, 200, y, f"¥{amt:,}", 24, SUB, family=NUM)
        txt(s, 620, y, f"{int(frac * 100)}%", 22, MUT, family=NUM)
        bar_row(s, 40, y + 38, 640, 640 * frac, 14, col, P2)
        y += 88
    rect(s, 40, y + 4, 640, 210, P1, 16, f"1 SOLID {P2}")
    txt(s, 76, y + 28, "环比提示", 24, AMB, bold=True)
    txt(s, 76, y + 66, "餐饮较上月 −¥310，购物 +¥180；娱乐卡片", 22, SUB)
    txt(s, 76, y + 100, "建议保留 ¥500 应急，余 2100 可提前还贷", 22, SUB)
    pill(s, 76, y + 138, 240, 60, TEAL, "生成省钱计划", 24, "#0B1030")
    pill(s, 340, y + 138, 240, 60, "#1B2460", "导出 PDF", 24, SUB)
    txt(s, 40, 1248, "演示界面 · 叠光钱包为虚构应用（不构成理财建议）", 18, MUT)
    return wrap_dsl(720, 1280, s, BG)


BASE = TASK_ROOT / "outputs" / RUN / "B01"


def main():
    (BASE).mkdir(parents=True, exist_ok=True)
    plan = []
    for mark, w, h, fn in CASES:
        d = BASE / mark
        d.mkdir(exist_ok=True)
        dsl = fn()
        p = d / "final.snapshot"
        p.write_text(dsl, encoding="utf-8")
        plan.append({"id": mark, "w": w, "h": h,
                     "dsl": f"{mark}/final.snapshot", "bytes": len(dsl.encode("utf-8"))})
    (TASK_ROOT / "tmp" / RUN / "B01").mkdir(parents=True, exist_ok=True)
    with open(TASK_ROOT / "tmp" / RUN / "B01" / "dsl-plan.json", "w",
              encoding="utf-8", newline="\n") as f:
        json.dump(plan, f, ensure_ascii=False, indent=1)
    for p in plan:
        print(p["id"], p["w"], "x", p["h"], p["bytes"], "bytes")


if __name__ == "__main__":
    main()
