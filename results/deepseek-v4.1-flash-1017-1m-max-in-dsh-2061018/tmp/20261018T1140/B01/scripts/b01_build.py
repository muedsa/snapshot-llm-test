"""B01 · ten independent real-world visual pieces, pure Snapshot DSL."""
from __future__ import annotations
import math, os, sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "B01"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from dsl import C, Pos, SizedBox, Stack, T  # noqa: E402

F = "Inter,Noto Sans CJK SC"
S = "Noto Serif CJK SC,Noto Sans CJK SC"
M = "Noto Sans Mono CJK SC,Inter"


def rot(deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"


def seg(x1, y1, x2, y2, color, th=2):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    ln = math.hypot(x2 - x1, y2 - y1); ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    return Pos(mx - ln / 2, my - th / 2,
               f'<Transform matrix="{rot(ang)}" alignment="CENTER">{C(width=ln, height=th, color=color)}</Transform>')


def dot(x, y, d, color, border=None):
    kw = {"width": d, "height": d, "color": color, "borderRadius": d / 2}
    if border:
        kw["border"] = border
    return Pos(x - d / 2, y - d / 2, C(**kw))


def line_v(x, y, h, color, th=1):
    return Pos(x, y, C(width=th, height=h, color=color))


def line_h(x, y, w, color, th=1):
    return Pos(x, y, C(width=w, height=th, color=color))


def base(w, h, bg, nodes):
    return f'<Snapshot type="png" background="{bg}">\n' + Stack([SizedBox(w, h)] + nodes, width=w, height=h) + "\n</Snapshot>\n"


def case01():
    W, H = 1600, 1000; bg = "#07131B"; ink = "#EAF2F6"; mut = "#93A9B8"; red = "#FF6B5E"; green = "#58D6B0"; amber = "#FFC15E"
    n = [Pos(0, 0, C(width=W, height=H, color=bg)), Pos(0, 0, C(width=W, height=6, color=red)),
         Pos(40, 34, T("NORTHSTAR ICU · 03:00 夜班交接", size=18, color=red, weight="BOLD", family=M, spacing=1.5)),
         Pos(40, 66, T("交接不是复述，是排优先级", size=38, color=ink, weight="BOLD", family=F)),
         Pos(40, 118, T("4 位病人 · 6 项待办 · 2 个升级阈值 · 接班医生 03:10 到位", size=19, color=mut, family=F)),
         Pos(1220, 48, T("NIGHT / 03:00", size=22, color=ink, weight="BOLD", family=M)),
         Pos(1220, 82, T("BED 04–07", size=18, color=mut, family=M))]
    pts = [
        ("P1", "BED 04", "术后 6h · 低血压", [("MAP", "62", "↓", red), ("HR", "108", "↑", amber), ("SpO₂", "94%", "↓", red)],
         "去甲肾上腺素 0.04 µg/kg/min", "若 MAP<60 连续 5min → 呼叫二线", red),
        ("P2", "BED 05", "COPD 急性加重", [("MAP", "78", "→", green), ("HR", "92", "→", green), ("SpO₂", "89%", "↓", amber)],
         "无创通气 12/5 cmH₂O · FiO₂ 0.35", "若 SpO₂<88% 或意识改变 → 准备插管", amber),
        ("P3", "BED 06", "急性胰腺炎", [("MAP", "84", "→", green), ("HR", "86", "→", green), ("SpO₂", "97%", "→", green)],
         "镇痛泵 2 mL/h · 禁食", "若尿量<0.5 mL/kg/h ×2h → 补液复核", green),
        ("P4", "BED 07", "房颤 · 快速心室率", [("MAP", "70", "↓", amber), ("HR", "126", "↑", red), ("SpO₂", "96%", "→", green)],
         "地尔硫䓬 5 mg/h · 监测 BP", "若 HR>140 或胸痛 → 同步电复律", red),
    ]
    for i, (pid, bed, dx, vit, med, esc, col) in enumerate(pts):
        x = 40 + (i % 2) * 760; y = 172 + (i // 2) * 292
        n += [Pos(x, y, C(width=740, height=268, color="#0D2230", borderRadius=12, border=f"1 SOLID #1E3A4A")),
              Pos(x, y, C(width=8, height=268, color=col, borderRadius=4)),
              Pos(x + 24, y + 18, T(f"{pid} · {bed}", size=24, color=ink, weight="BOLD", family=M)),
              Pos(x + 190, y + 22, T(dx, size=21, color=ink, family=F)),
              Pos(x + 620, y + 18, T("风险", size=15, color=col, weight="BOLD", family=F))]
        for j, (k, v, arrow, c2) in enumerate(vit):
            vx = x + 24 + j * 128
            n += [Pos(vx, y + 66, T(k, size=15, color=mut, family=M)),
                  Pos(vx, y + 86, T(v, size=30, color=c2, weight="BOLD", family=M)),
                  Pos(vx + 76, y + 92, T(arrow, size=18, color=c2, family=M))]
        n += [Pos(x + 24, y + 146, T("用药", size=14, color=mut, family=F)),
              Pos(x + 24, y + 168, T(med, size=18, color=ink, family=F)),
              Pos(x + 24, y + 204, T("升级", size=14, color=mut, family=F)),
              Pos(x + 24, y + 226, T(esc, size=16, color=col, family=F))]
    n += [Pos(40, 800, C(width=1520, height=158, color="#0D2230", borderRadius=12, border="1 SOLID #1E3A4A")),
          Pos(64, 818, T("接班后 10 分钟必做", size=22, color=ink, weight="BOLD", family=F)),
          Pos(64, 854, T("□ 床旁核对 4 位病人身份与过敏史    □ 复查 P1/P4 的 MAP 与 HR    □ 确认 P2 无创通气面罩无压疮", size=17, color=mut, family=F)),
          Pos(64, 890, T("□ 与二线确认 P1 升压药上限    □ 记录 P4 地尔硫䓬起始时间    □ 03:10 前完成交接签名", size=17, color=mut, family=F)),
          Pos(1260, 818, T("升级电话", size=15, color=mut, family=F)),
          Pos(1260, 844, T("二线 6688", size=26, color=red, weight="BOLD", family=M)),
          Pos(1420, 844, T("ICU 值班 6621", size=20, color=ink, family=M))]
    return base(W, H, bg, n)


def case02():
    W, H = 1200, 1600; bg = "#EFE5D3"; ink = "#171512"; accent = "#A64B2A"
    n = [Pos(0, 0, C(width=W, height=H, color=bg)),
         Pos(0, 0, C(width=18, height=H, color=ink)),
         Pos(56, 44, T("NATURAL HISTORY MUSEUM · SPECIAL EXHIBITION", size=16, color=accent, weight="BOLD", family=M, spacing=2)),
         Pos(56, 108, T("深时", size=230, color=ink, weight="BOLD", family=S)),
         Pos(74, 370, T("DEEP TIME", size=44, color=accent, weight="BOLD", family=M, spacing=10)),
         Pos(74, 430, T("从 46 亿年前到此刻，\n一块石头记住的气候。", size=34, color=ink, family=S, height="1.5"), w=700, h=120),
         Pos(74, 600, T("2026.11.12 — 2027.03.08", size=30, color=ink, weight="BOLD", family=M)),
         Pos(74, 644, T("周二至周日 10:00–18:00 · 西馆 B1 特展厅", size=22, color="#5C4E3E", family=F))]
    strata = [("#2E3B33", 100), ("#5A4A35", 66), ("#B06A3B", 48), ("#D5B68A", 34), ("#7C8B72", 76), ("#3B4D52", 52)]
    y = 700
    for i, (c, h) in enumerate(strata):
        n += [Pos(56 + i * 4, y, C(width=980 - i * 8, height=h, color=c)), Pos(1050, y + 8, T(f"{46 - i * 7}.{i} 亿年前", size=15, color="#4A4034", family=M))]
        y += h + 8
    n += [Pos(56, 1148, T("展品", size=18, color=accent, weight="BOLD", family=F)),
          Pos(56, 1178, T("126 件岩芯、化石与现场录音；\n含一块 4.2 亿年前的珊瑚礁。", size=24, color=ink, family=F, height="1.5"), w=900, h=80),
          Pos(56, 1260, C(width=1088, height=2, color=ink)),
          Pos(56, 1284, T("购票：northstar-museum.example / 深时", size=20, color=ink, family=F)),
          Pos(56, 1320, T("地铁 2 号线 · 自然博物馆站 B 口 · 轮椅可达", size=18, color="#5C4E3E", family=F)),
          Pos(56, 1400, T("“我们不是站在时间之外看它，\n我们就在地层正在形成的那一页。”", size=26, color=accent, family=S, height="1.5"), w=1000, h=90)]
    return base(W, H, bg, n)


def case03():
    W, H = 1600, 1000; bg = "#F4F1E8"; ink = "#16202A"
    n = [Pos(0, 0, C(width=W, height=H, color=bg)),
         Pos(40, 30, T("RIVERSIDE / FLOOD EVACUATION", size=16, color="#B33A2B", weight="BOLD", family=M, spacing=2)),
         Pos(40, 66, T("河畔社区防洪疏散图", size=40, color=ink, weight="BOLD", family=F)),
         Pos(40, 120, T("水位 4.2m · 预警橙 · 集合点开放", size=20, color="#B33A2B", weight="BOLD", family=F))]
    # map area
    n += [Pos(40, 170, C(width=1120, height=760, color="#E9E2D2", borderRadius=10, border="2 SOLID #16202A"))]
    # river
    n += [Pos(720, 170, C(width=240, height=760, color="#A8D3DF")),
          Pos(760, 210, T("RIVER", size=18, color="#245B6B", family=M, spacing=4))]
    for i in range(9):
        x = 70 + i * 120
        n.append(line_v(x, 190, 720, "#B9AE99", 2))
    for j in range(7):
        y = 200 + j * 100
        n.append(line_h(70, y, 1020, "#B9AE99", 2))
    # zone blocks
    zones = [("A", 80, 210, "#F2B36A", "A 区 · 优先撤"), ("B", 300, 210, "#E8896B", "B 区 · 准备"),
             ("C", 80, 500, "#F4D06F", "C 区 · 留意"), ("D", 300, 500, "#A8C6A1", "D 区 · 待命")]
    for z, x, y, c, lab in zones:
        n += [Pos(x, y, C(width=210, height=180, color=c, borderRadius=8)),
              Pos(x + 14, y + 12, T(z, size=34, color=ink, weight="BOLD", family=M)),
              Pos(x + 14, y + 142, T(lab, size=17, color=ink, weight="BOLD", family=F))]
    # route
    route = [(420, 640), (520, 640), (520, 780), (700, 780), (700, 860), (870, 860)]
    for (x1, y1), (x2, y2) in zip(route, route[1:]):
        n.append(seg(x1, y1, x2, y2, "#B33A2B", 10))
    for x, y in route:
        n.append(dot(x, y, 16, "#B33A2B"))
    n += [Pos(400, 600, T("撤离路线", size=20, color="#B33A2B", weight="BOLD", family=F)),
          Pos(840, 820, T("集合点", size=20, color="#B33A2B", weight="BOLD", family=F)),
          dot(900, 870, 28, "#FFFFFF", "4 SOLID #B33A2B"),
          Pos(930, 852, T("社区中心\n高台", size=17, color=ink, weight="BOLD", family=F))]
    # legend / instructions
    n += [Pos(1200, 170, C(width=360, height=360, color="#FFFFFF", borderRadius=10, border="1 SOLID #C9BFAC")),
          Pos(1220, 190, T("现在做什么", size=24, color=ink, weight="BOLD", family=F)),
          Pos(1220, 228, T("1  带上手机、药物、钥匙\n2  不走地下通道\n3  帮邻居老人/轮椅\n4  到集合点登记", size=18, color=ink, family=F, height="1.6"), w=320, h=150),
          Pos(1220, 390, T("不要", size=16, color="#B33A2B", weight="BOLD", family=F)),
          Pos(1220, 416, T("不驾车穿水、不返回取物", size=18, color="#B33A2B", family=F))]
    n += [Pos(1200, 560, C(width=360, height=170, color="#16202A", borderRadius=10)),
          Pos(1220, 580, T("紧急电话", size=15, color="#F2B36A", family=F)),
          Pos(1220, 606, T("119 / 社区值班 6688", size=24, color="#FFFFFF", weight="BOLD", family=M)),
          Pos(1220, 650, T("演练：2026.11.08 15:00", size=17, color="#C9D5DD", family=F)),
          Pos(1220, 780, T("自拟社区网格 · 非官方预警", size=14, color="#6F7D88", family=F))]
    return base(W, H, bg, n)


def case04():
    W, H = 1080, 1350; bg = "#E86A3A"; ink = "#1D1712"; cream = "#F7EAD7"
    n = [Pos(0, 0, C(width=W, height=H, color=bg)),
         Pos(42, 42, T("SALT & LIGHT BOOKS", size=16, color=ink, weight="BOLD", family=M, spacing=3)),
         Pos(42, 76, T("独立书店 · 夜谈 07", size=16, color=ink, family=F)),
         Pos(42, 190, T("盐与光", size=150, color=cream, weight="BOLD", family=S)),
         Pos(42, 380, T("一场关于离开与返回的夜谈", size=30, color=ink, family=S)),
         Pos(42, 450, C(width=996, height=3, color=ink)),
         Pos(42, 490, T("作者", size=14, color=ink, family=F)),
         Pos(42, 514, T("林见鹿", size=40, color=cream, weight="BOLD", family=S)),
         Pos(500, 490, T("对谈", size=14, color=ink, family=F)),
         Pos(500, 514, T("苏言", size=40, color=cream, weight="BOLD", family=S)),
         Pos(42, 620, T("2026.11.14  周六  19:30", size=28, color=ink, weight="BOLD", family=M)),
         Pos(42, 668, T("盐与光书店 · 二层 / 42 座", size=22, color=ink, family=F)),
         Pos(42, 720, T("门票 38 元（含一杯热苹果茶）", size=22, color=cream, family=F))]
    # ticket stub
    n += [Pos(42, 830, C(width=996, height=210, color=cream, borderRadius=14)),
          Pos(64, 852, T("ADMIT ONE", size=15, color=ink, weight="BOLD", family=M, spacing=3)),
          Pos(64, 882, T("夜谈入场", size=44, color=ink, weight="BOLD", family=S)),
          Pos(64, 952, T("19:00 入场 · 19:30 开始 · 请保留此联", size=18, color=ink, family=F)),
          Pos(760, 852, T("NO. 042", size=18, color=ink, weight="BOLD", family=M)),
          Pos(760, 886, T("扫码报名", size=18, color=ink, family=F)),
          Pos(760, 918, C(width=104, height=104, color="#F7EAD7", borderRadius=4, border="2 SOLID #1D1712")),
          Pos(780, 940, C(width=64, height=64, color="#1D1712")),
          Pos(796, 956, C(width=32, height=32, color="#F7EAD7"))]
    n += [Pos(42, 1110, T("“我们带着盐离开，\n又带着光回来。”", size=44, color=cream, family=S, height="1.5"), w=900, h=140),
          Pos(42, 1288, T("saltandlight.example / events", size=16, color=ink, family=M))]
    return base(W, H, bg, n)


def case05():
    W, H = 1200, 800; bg = "#171411"; ink = "#F2E7D4"; amber = "#D9A05B"; mut = "#9C8A74"
    n = [Pos(0, 0, C(width=W, height=H, color=bg)),
         Pos(40, 36, T("LOT 27 · 2026 HARVEST", size=14, color=amber, weight="BOLD", family=M, spacing=2)),
         Pos(40, 66, T("El Mirador", size=44, color=ink, weight="BOLD", family=S)),
         Pos(40, 120, T("Huehuetenango, Guatemala · 1,720 m", size=18, color=mut, family=F)),
         Pos(40, 170, C(width=520, height=1, color="#4A3B2E")),
         Pos(40, 190, T("VARIETAL", size=12, color=mut, family=M)),
         Pos(40, 208, T("Bourbon / Caturra", size=21, color=ink, family=F)),
         Pos(40, 252, T("PROCESS", size=12, color=mut, family=M)),
         Pos(40, 270, T("Washed · 36 h", size=21, color=ink, family=F)),
         Pos(40, 314, T("ROAST", size=12, color=mut, family=M)),
         Pos(40, 332, T("Medium · 11:20", size=21, color=ink, family=F)),
         Pos(40, 376, T("CUPPING", size=12, color=mut, family=M)),
         Pos(40, 398, T("橙花 / 黄桃 / 焦糖", size=26, color=amber, family=S)),
         Pos(40, 450, T("“干净、甜感长，冷却后像红茶。”", size=19, color=ink, family=S)),
         Pos(40, 520, T("BREW", size=12, color=mut, family=M)),
         Pos(40, 540, T("15 g / 240 g 水 · 92°C · 2:30", size=20, color=ink, family=M)),
         Pos(40, 700, T("NORTHSTAR ROASTERS · BATCH 027", size=13, color=mut, family=M, spacing=2))]
    # roast curve panel
    n += [Pos(620, 40, C(width=540, height=720, color="#211B16", borderRadius=12, border="1 SOLID #3A2C21")),
          Pos(644, 62, T("Roast profile", size=24, color=ink, weight="BOLD", family=F)),
          Pos(644, 96, T("bean temp °C / time", size=14, color=mut, family=M))]
    x0, y0, x1, y1 = 660, 540, 1120, 140
    for i in range(6):
        yy = y0 - i * 80
        n += [Pos(x0, yy, C(width=x1 - x0, height=1, color="#3A2C21")), Pos(624, yy - 8, T(str(120 + i * 30), size=12, color=mut, family=M))]
    pts = [(0, 180), (2, 196), (4, 208), (6, 216), (8, 221), (10, 225), (12, 228)]
    for (t1, v1), (t2, v2) in zip(pts, pts[1:]):
        n.append(seg(x0 + t1 / 12 * 440, y0 - (v1 - 120) / 180 * 380, x0 + t2 / 12 * 440, y0 - (v2 - 120) / 180 * 380, amber, 4))
    n += [Pos(660, 566, T("0", size=12, color=mut, family=M)), Pos(1050, 566, T("12 min", size=12, color=mut, family=M)),
          Pos(660, 604, T("First crack 9:10 · Development 18%", size=18, color=ink, family=F))]
    return base(W, H, bg, n)


def case06():
    W, H = 1080, 1350; bg = "#E9EFE7"; ink = "#12312A"; green = "#1E6B52"; amber = "#C77C2B"
    n = [Pos(0, 0, C(width=W, height=H, color=bg)),
         Pos(0, 0, C(width=W, height=14, color=green)),
         Pos(48, 48, T("STEP-FREE TRANSFER / 04", size=15, color=green, weight="BOLD", family=M, spacing=2)),
         Pos(48, 86, T("无障碍换乘", size=56, color=ink, weight="BOLD", family=F)),
         Pos(48, 158, T("河湾站 2 号线 → 7 号线 · 全程无台阶", size=22, color="#3C5A50", family=F)),
         Pos(48, 224, T("跟着绿色走，约 6 分钟。", size=30, color=green, weight="BOLD", family=F))]
    steps = [("01", "站台 2 号线", "下车后向车头方向 30 m\n找到绿色电梯标识", "电梯 A · 宽 1.4 m"),
             ("02", "站厅层", "出电梯右转，沿盲道直行\n经过服务台（有人值守）", "服务台 08:00–22:00"),
             ("03", "宽闸机", "3 号闸机常开，宽 0.95 m\n刷卡后不要停留", "3 号闸机"),
             ("04", "7 号线站台", "再乘电梯下到 B3\n电梯 B 在柱子 12 旁", "电梯 B · 语音报层"),
             ("05", "上车", "候车区 7-2，屏蔽门与站台齐平\n可呼叫站务协助上车", "按红色求助钮")]
    y = 300
    for i, (num, title, body, meta) in enumerate(steps):
        n += [Pos(48, y, C(width=72, height=72, color=green, borderRadius=36)),
              Pos(66, y + 14, T(num, size=28, color="#FFFFFF", weight="BOLD", family=M)),
              Pos(146, y - 2, T(title, size=28, color=ink, weight="BOLD", family=F)),
              Pos(146, y + 36, T(body, size=19, color="#3C5A50", family=F, height="1.45"), w=700, h=60),
              Pos(850, y + 8, T(meta, size=16, color=green, family=F), w=190, h=50)]
        if i < 4:
            n.append(line_v(84, y + 72, 92, "#A9C7B8", 4))
        y += 164
    n += [Pos(48, 1190, C(width=984, height=92, color="#12312A", borderRadius=12)),
          Pos(70, 1206, T("如果电梯停运", size=18, color="#F4C77B", weight="BOLD", family=F)),
          Pos(70, 1234, T("站台 2 号线 → 地面 1 号口 → 步行 180 m → 7 号线无障碍入口（有坡道）", size=16, color="#F4F8F4", family=F))]
    return base(W, H, bg, n)


def case07():
    W, H = 900, 1200; bg = "#F3EBDD"; ink = "#243326"; green = "#4C7A4A"; amber = "#C98532"; mut = "#6E7A68"
    n = [Pos(0, 0, C(width=W, height=H, color=bg)),
         Pos(44, 36, T("BALCONY SEED CALENDAR", size=13, color=green, weight="BOLD", family=M, spacing=2)),
         Pos(44, 70, T("阳台播种日历", size=44, color=ink, weight="BOLD", family=F)),
         Pos(44, 126, T("温带示例 · 最后一次霜冻 04.10 · 容器 30 cm 深", size=17, color=mut, family=F)),
         Pos(44, 174, T("播种", size=13, color=green, family=F)), Pos(44, 194, C(width=12, height=12, color=green)),
         Pos(104, 174, T("移栽", size=13, color=amber, family=F)), Pos(104, 194, C(width=12, height=12, color=amber)),
         Pos(164, 174, T("收获", size=13, color=ink, family=F)), Pos(164, 194, C(width=12, height=12, color=ink))]
    months = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
    x0, x1 = 150, 850
    for i, m in enumerate(months):
        x = x0 + i * (x1 - x0) / 12
        n += [line_v(x, 230, 760, "#D8CDB9", 1), Pos(x + 4, 210, T(m, size=13, color=mut, family=M))]
    crops = [("番茄", 3, 5, 7, 9, green), ("罗勒", 4, 6, 6, 9, amber), ("生菜", 2, 4, 4, 6, green),
             ("萝卜", 3, 4, 5, 6, amber), ("辣椒", 3, 6, 7, 10, green), ("豌豆", 2, 3, 5, 6, green)]
    for j, (name, s, t, h1, h2, c) in enumerate(crops):
        y = 260 + j * 112
        n += [Pos(44, y + 8, T(name, size=22, color=ink, weight="BOLD", family=F)),
              line_h(150, y + 26, 700, "#D8CDB9", 1)]
        for a, b, col, lab in ((s, t, green, "播"), (t, h1, amber, "栽"), (h1, h2, ink, "收")):
            bx = x0 + (a - 1) * (x1 - x0) / 12; bw = (b - a) * (x1 - x0) / 12
            n += [Pos(bx + 2, y + 4, C(width=max(6, bw - 4), height=34, color=col, borderRadius=5)),
                  Pos(bx + 8, y + 10, T(lab, size=14, color="#FFFFFF" if col != amber else "#2B1B08", weight="BOLD", family=F))]
    n += [Pos(44, 990, T("一季三件事", size=24, color=ink, weight="BOLD", family=F)),
          Pos(44, 1028, T("04.10 后定植番茄 / 05.15 追肥一次 / 07.01 开始收罗勒", size=18, color=mut, family=F)),
          Pos(44, 1108, T("NORTHSTAR SEEDS · 演示品种，不保证各地气候", size=13, color=mut, family=M))]
    return base(W, H, bg, n)


def case08():
    W, H = 1200, 900; bg = "#F5E8D2"; ink = "#2B241C"; red = "#C5523F"; teal = "#2C6E6A"; amber = "#D9953F"
    n = [Pos(0, 0, C(width=W, height=H, color=bg)),
         Pos(40, 34, T("REPAIR CAFÉ · SAT 10:00–14:00", size=15, color=teal, weight="BOLD", family=M, spacing=2)),
         Pos(40, 66, T("坏了？带来看看。", size=44, color=ink, weight="BOLD", family=F)),
         Pos(40, 120, T("社区维修咖啡馆 · 免费 · 不保证修好 · 欢迎旁观学习", size=18, color="#6A5B49", family=F)),
         Pos(40, 170, C(width=1120, height=3, color=ink))]
    tables = [("TABLE 01", "小家电", "台灯 / 电水壶 / 风扇", red, "阿岚"),
              ("TABLE 02", "衣物缝补", "裤脚 / 拉链 / 纽扣", teal, "Mina"),
              ("TABLE 03", "自行车", "刹车 / 补胎 / 链条", amber, "老周")]
    for i, (tno, cat, what, c, who) in enumerate(tables):
        x = 40 + i * 380
        n += [Pos(x, 210, C(width=350, height=330, color="#FFFDF8", borderRadius=12, border="1 SOLID #D9C9B4")),
              Pos(x + 20, 230, T(tno, size=14, color=c, weight="BOLD", family=M, spacing=2)),
              Pos(x + 20, 258, T(cat, size=30, color=ink, weight="BOLD", family=F)),
              Pos(x + 20, 306, T(what, size=18, color="#6A5B49", family=F, height="1.5"), w=310, h=70),
              Pos(x + 20, 396, T("志愿者", size=13, color="#8A7A66", family=F)),
              Pos(x + 20, 418, T(who, size=22, color=ink, weight="BOLD", family=F)),
              Pos(x + 20, 472, T("10:00–13:30 随到随排", size=16, color=c, family=F))]
    # schedule strip
    n += [Pos(40, 580, C(width=1120, height=104, color="#2B241C", borderRadius=10)),
          Pos(60, 596, T("10:00", size=14, color="#F5E8D2", family=M)), Pos(60, 620, T("开门 / 领号", size=18, color="#FFFFFF", weight="BOLD", family=F)),
          Pos(300, 596, T("11:00", size=14, color="#F5E8D2", family=M)), Pos(300, 620, T("安全说明", size=18, color="#FFFFFF", weight="BOLD", family=F)),
          Pos(540, 596, T("12:30", size=14, color="#F5E8D2", family=M)), Pos(540, 620, T("集体午餐", size=18, color="#FFFFFF", weight="BOLD", family=F)),
          Pos(780, 596, T("13:30", size=14, color="#F5E8D2", family=M)), Pos(780, 620, T("最后收件", size=18, color="#FFFFFF", weight="BOLD", family=F)),
          Pos(1000, 596, T("14:00", size=14, color="#F5E8D2", family=M)), Pos(1000, 620, T("归还/带走", size=18, color="#FFFFFF", weight="BOLD", family=F))]
    n += [Pos(40, 720, T("带什么", size=20, color=ink, weight="BOLD", family=F)),
          Pos(40, 752, T("坏件 + 说明书/配件 + 愿意等 30–60 分钟；不带来路不明的燃气/电池设备。", size=18, color="#6A5B49", family=F)),
          Pos(40, 812, T("河畔社区中心 · 一楼多功能厅 · 无障碍入口", size=16, color=teal, family=F)),
          Pos(40, 846, T("repair-cafe.example / 每月第二个周六", size=14, color="#8A7A66", family=M))]
    return base(W, H, bg, n)


def case09():
    W, H = 1080, 1350; bg = "#07111F"; ink = "#E8F0FF"; dim = "#8FA3C2"; red = "#FF6B6B"; gold = "#F2C46B"
    n = [Pos(0, 0, C(width=W, height=H, color=bg)),
         Pos(40, 32, T("NORTHSTAR ASTRO CLUB · OBSERVING NIGHT", size=13, color=gold, weight="BOLD", family=M, spacing=2)),
         Pos(40, 64, T("今晚看什么", size=42, color=ink, weight="BOLD", family=F)),
         Pos(40, 118, T("2026.11.14 · 20:00–23:00 · 西郊观测点", size=18, color=dim, family=F)),
         Pos(820, 66, T("MOON 12%", size=14, color=gold, family=M))]
    # sky circle
    cx, cy, r = 330, 500, 250
    n += [Pos(cx - r, cy - r, C(width=2 * r, height=2 * r, color="transparent", border="1 SOLID #29405C", borderRadius=r)),
          Pos(cx - 2, cy - 260, T("N", size=13, color=dim, family=M)), Pos(cx - 2, cy + 240, T("S", size=13, color=dim, family=M))]
    for ang in range(0, 360, 30):
        a = math.radians(ang); x1 = cx + (r - 8) * math.sin(a); y1 = cy - (r - 8) * math.cos(a)
        x2 = cx + r * math.sin(a); y2 = cy - r * math.cos(a)
        n.append(seg(x1, y1, x2, y2, "#3A5570", 1))
    # stars and constellation
    stars = [(250, 380, "织女星", gold), (430, 330, "天津四", ink), (360, 450, "牛郎星", ink), (300, 600, "毕宿五", gold), (470, 620, "参宿四", red), (410, 700, "参宿七", ink)]
    for x, y, lab, c in stars:
        n += [dot(x, y, 10 if c == gold else 7, c), Pos(x + 12, y - 8, T(lab, size=14, color=dim, family=F))]
    for (x1, y1, _, _), (x2, y2, _, _) in zip(stars[3:5], stars[4:6]):
        n.append(seg(x1, y1, x2, y2, "#5E7898", 1))
    n += [Pos(40, 820, T("目标", size=20, color=gold, weight="BOLD", family=F)),
          Pos(40, 856, T("20:15  织女星  ·  西偏北 18°  ·  肉眼", size=18, color=ink, family=F)),
          Pos(40, 892, T("20:45  昴星团  ·  东 22°  ·  双筒", size=18, color=ink, family=F)),
          Pos(40, 928, T("21:20  木星  ·  东南 35°  ·  肉眼", size=18, color=ink, family=F)),
          Pos(40, 964, T("22:00  猎户座大星云  ·  东南 48°  ·  望远镜", size=18, color=ink, family=F)),
          Pos(40, 1000, T("22:40  月球  ·  西南 12°  ·  滤镜", size=18, color=ink, family=F)),
          Pos(40, 1088, C(width=1000, height=2, color="#29405C")),
          Pos(40, 1112, T("红光模式 · 到场后请关闭白光；三脚架区在 circle B。", size=16, color=dim, family=F)),
          Pos(40, 1160, T("天气取消：cloud-cover > 60% 或 风速 > 25 km/h，群内 18:00 通知。", size=15, color=red, family=F)),
          Pos(40, 1240, T("方位/时间为演示观测计划 · 请以现场星图复核", size=13, color="#5F748F", family=M))]
    return base(W, H, bg, n)


def case10():
    W, H = 1600, 1200; bg = "#F2EFE5"; ink = "#1D2A24"; green = "#3E7C59"; amber = "#D98A2B"; red = "#BF4A3F"
    n = [Pos(0, 0, C(width=W, height=H, color=bg)),
         Pos(40, 32, T("CLIMATE FIELD GUIDE · DEMO SCORES", size=13, color=green, weight="BOLD", family=M, spacing=2)),
         Pos(40, 64, T("同一片社区，三种风险", size=44, color=ink, weight="BOLD", family=F)),
         Pos(40, 118, T("河湾社区 · 2026 夏季演练 · 评分 0–5，越高越需行动", size=18, color="#64736B", family=F)),
         Pos(40, 170, C(width=1520, height=2, color=ink))]
    zones = ["北堤", "老市场", "新桥", "低洼田"]
    risks = [("热", [2, 4, 3, 5], "遮阳/饮水/错峰"), ("涝", [4, 3, 2, 5], "抬升/沙袋/撤离"), ("风", [3, 4, 2, 3], "加固/修剪/停棚")]
    x0, y0 = 280, 240; cw, ch = 300, 190
    n += [Pos(160, y0, T("区域", size=15, color="#64736B", family=F))]
    for j, z in enumerate(zones):
        n += [Pos(x0 + j * cw + 20, y0, T(z, size=22, color=ink, weight="BOLD", family=F))]
    for i, (risk, vals, action) in enumerate(risks):
        y = y0 + 50 + i * ch
        n += [Pos(40, y + 40, T(risk, size=38, color=ink, weight="BOLD", family=S)),
              Pos(40, y + 90, T(action, size=15, color="#64736B", family=F))]
        for j, v in enumerate(vals):
            c = green if v <= 2 else (amber if v == 3 else red)
            n += [Pos(x0 + j * cw, y, C(width=cw - 18, height=140, color=c, borderRadius=10)),
                  Pos(x0 + j * cw + 20, y + 18, T(str(v), size=54, color="#FFFFFF", weight="BOLD", family=M)),
                  Pos(x0 + j * cw + 20, y + 88, T(["低", "低", "中", "高", "高", "极高"][v], size=16, color="#FFFFFF", family=F))]
    n += [Pos(40, 850, C(width=740, height=250, color="#1D2A24", borderRadius=12)),
          Pos(64, 872, T("本周行动", size=22, color="#F2C46B", weight="BOLD", family=F)),
          Pos(64, 910, T("1  低洼田：先清沟，再备 200 个沙袋\n2  老市场：检查遮阳棚固定点\n3  北堤：为独居老人建联络名单", size=19, color="#F2EFE5", family=F, height="1.55"), w=690, h=140)]
    n += [Pos(820, 850, C(width=740, height=250, color="#FFFFFF", borderRadius=12, border="1 SOLID #D6CDBD")),
          Pos(844, 872, T("读图规则", size=22, color=ink, weight="BOLD", family=F)),
          Pos(844, 910, T("分数是演练共识，不是气象预警；\n红=本周内行动，橙=两周内，绿=监测。\n每次更新须重算，不把颜色当永久结论。", size=18, color="#64736B", family=F, height="1.5"), w=690, h=120)]
    n += [Pos(40, 1140, T("NORTHSTAR RESILIENCE LAB · 自拟评分 · 非官方预警", size=13, color="#64736B", family=M))]
    return base(W, H, bg, n)


BUILDERS = {
    "case-01": (case01, "夜班交接板", 1600, 1000),
    "case-02": (case02, "深时：地质展海报", 1200, 1600),
    "case-03": (case03, "社区防洪疏散图", 1600, 1000),
    "case-04": (case04, "盐与光：书店夜谈", 1080, 1350),
    "case-05": (case05, "咖啡批次卡", 1200, 800),
    "case-06": (case06, "无障碍换乘指南", 1080, 1350),
    "case-07": (case07, "播种日历", 900, 1200),
    "case-08": (case08, "维修咖啡馆排期", 1200, 900),
    "case-09": (case09, "观星夜目标卡", 1080, 1350),
    "case-10": (case10, "气候风险田图", 1600, 1200),
}


def main():
    (TMP / "dsl").mkdir(parents=True, exist_ok=True)
    (TMP / "renders").mkdir(parents=True, exist_ok=True)
    made = []
    for cid, (fn, title, w, h) in BUILDERS.items():
        dsl = fn()
        p = TMP / "dsl" / f"{cid}-{VERSION}.snapshot"
        p.write_text(dsl, encoding="utf-8")
        made.append((cid, title, w, h, str(p)))
    print(json.dumps([{"id": c, "title": t, "w": w, "h": h} for c, t, w, h, _ in made], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    import json
    raise SystemExit(main())
