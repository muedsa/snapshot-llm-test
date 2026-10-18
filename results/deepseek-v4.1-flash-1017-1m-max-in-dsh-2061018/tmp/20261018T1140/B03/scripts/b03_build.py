"""B03 · ten DSL-led visual experiments for a fictional culture lab."""
from __future__ import annotations
import math, os, sys
from pathlib import Path
ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve(); RUN = os.environ["SNAPSHOT_RUN_ID"]; TASK = "B03"
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"; TMP = ROOT / "tmp" / RUN / TASK
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts")); sys.path.insert(0, str(ROOT / "tmp" / RUN / "B02" / "scripts"))
from dsl import C, Pos, SizedBox, Stack, T  # noqa: E402
from b02_build import rot, seg, dot, base  # noqa: E402
F = "Inter,Noto Sans CJK SC"; S = "Noto Serif CJK SC,Noto Sans CJK SC"; M = "Noto Sans Mono CJK SC,Inter"


def case01():
    W, H = 1080, 1350; bg = "#07090C"; n = [Pos(0, 0, C(width=W, height=H, color=bg))]
    n += [Pos(48, 36, T("NORTHSTAR CULTURE LAB / 01", size=13, color="#8B9AA8", family=M, spacing=2)),
          Pos(48, 70, T("夜航", size=210, color="#FF5D5D", weight="BOLD", family=S)),
          Pos(100, 330, T("夜航", size=210, color="#56D6C9", weight="BOLD", family=S)),
          Pos(152, 590, T("夜航", size=210, color="#F4EEE2", weight="BOLD", family=S)),
          Pos(48, 860, T("NIGHT SHIFT", size=30, color="#F4EEE2", weight="BOLD", family=M, spacing=7)),
          Pos(48, 920, T("一场关于城市入睡后的声音航行", size=25, color="#B8C5CE", family=F)),
          Pos(48, 1000, T("2026.12.05  22:00", size=38, color="#F4EEE2", weight="BOLD", family=M)),
          Pos(48, 1050, T("Northstar Hall · 站席 400", size=18, color="#8B9AA8", family=F)),
          Pos(48, 1120, T("演出 90 min · 无中场 · 建议 16+", size=16, color="#B8C5CE", family=F)),
          Pos(48, 1190, T("tickets.northstar.example / nightshift", size=15, color="#56D6C9", family=M)),
          Pos(48, 1260, T("“把耳朵交给黑暗，眼睛会听见。”", size=27, color="#FF5D5D", family=S))]
    # vertical guides
    for x in (300, 600, 900): n.append(Pos(x, 0, C(width=1, height=H, color="#1C2A34")))
    return base(W, H, bg, n)


def case02():
    W, H = 1200, 1200; bg = "#0B0E1A"; n = [Pos(0, 0, C(width=W, height=H, color=bg))]
    cx, cy = 600, 580
    for r, c, th in ((420, "#2E3A55", 1), (350, "#43506E", 1), (280, "#5B6684", 2), (210, "#8B6CFF", 2), (140, "#F2C46B", 2)):
        n.append(Pos(cx - r, cy - r, C(width=2 * r, height=2 * r, color="transparent", border=f"{th} SOLID {c}", borderRadius=r)))
    labels = ["低频 20Hz", "潮汐", "呼吸", "金属", "回声", "静默", "脉冲", "夜风", "共振", "远雷", "微光", "归零"]
    for i, lab in enumerate(labels):
        a = math.radians(-90 + i * 30); x = cx + 390 * math.cos(a); y = cy + 390 * math.sin(a)
        n += [dot(x, y, 8, "#F2C46B"), Pos(x - 40, y - 26, T(lab, size=15, color="#B8C5E8", family=F))]
    n += [Pos(390, 490, C(width=420, height=210, color="#0B0E1A", borderRadius=16)),
          Pos(430, 510, T("ORBITAL", size=54, color="#F4EEE2", weight="BOLD", family=M, spacing=4)),
          Pos(390, 580, T("环绕声", size=44, color="#F2C46B", weight="BOLD", family=S)),
          Pos(420, 650, T("2026.12.12 / 20:00", size=23, color="#B8C5E8", family=M)),
          Pos(430, 690, T("Planetarium · 120 seats", size=17, color="#7C89A8", family=F)),
          Pos(48, 48, T("NORTHSTAR CULTURE LAB / 02", size=13, color="#7C89A8", family=M, spacing=2)),
          Pos(48, 1080, T("一张唱片的两面：从 20Hz 到静默。", size=22, color="#F4EEE2", family=S))]
    return base(W, H, bg, n)


def case03():
    W, H = 1080, 1350; bg = "#F1EADF"; ink = "#1A1A1A"; n = [Pos(0, 0, C(width=W, height=H, color=bg))]
    # two moire line grids
    for k in range(26):
        y = 250 + k * 34
        n.append(seg(40, y, 1040, y + 170, "#1A1A1A" if k % 2 else "#D65A45", 2))
    for k in range(26):
        y = 250 + k * 34
        n.append(seg(40, y + 160, 1040, y - 10, "#1A1A1A" if k % 2 else "#2E7D7A", 2))
    # translucent center panel for text
    n += [Pos(80, 780, C(width=920, height=470, color="#F1EADFEE", borderRadius=10)),
          Pos(110, 810, T("干扰", size=110, color=ink, weight="BOLD", family=S)),
          Pos(110, 940, T("INTERFERENCE", size=24, color="#D65A45", weight="BOLD", family=M, spacing=5)),
          Pos(110, 990, T("媒体艺术讲座 / 当图像开始互相干扰", size=24, color=ink, family=F)),
          Pos(110, 1060, T("11.28  19:30", size=34, color=ink, weight="BOLD", family=M)),
          Pos(110, 1108, T("讲者 林见鹿 × 苏言 · 免费 / 60 座", size=18, color="#5A5248", family=F)),
          Pos(110, 1160, T("northstar.example / interference", size=15, color="#2E7D7A", family=M)),
          Pos(40, 44, T("NORTHSTAR CULTURE LAB / 03", size=13, color="#5A5248", family=M, spacing=2))]
    return base(W, H, bg, n)


def case04():
    W, H = 1200, 1600; bg = "#15100C"; ink = "#F2E5D2"; n = [Pos(0, 0, C(width=W, height=H, color=bg))]
    y = 0; bands = [("#3E2C22", 260), ("#6E4A33", 180), ("#B46B3C", 250), ("#D8A15E", 110), ("#4E5B4A", 300), ("#242A27", 300), ("#7C5A43", 200)]
    for c, h in bands:
        n += [Pos(0, y, C(width=W, height=h, color=c)), Pos(40, y + 14, T("", size=1, color=c))]
        y += h
    # circle cutouts
    for cx, cy, r, c in ((760, 420, 190, "#B46B3C"), (350, 820, 260, "#15100C"), (920, 1130, 160, "#D8A15E")):
        n += [Pos(cx - r, cy - r, C(width=2 * r, height=2 * r, color=c, borderRadius=r)),
              Pos(cx - r + 1, cy - r + 1, C(width=2 * r - 2, height=2 * r - 2, color="transparent", border="1 SOLID #F2E5D2", borderRadius=r))]
    n += [Pos(48, 80, T("地层记忆", size=96, color=ink, weight="BOLD", family=S)),
          Pos(48, 190, T("STRATA / MEMORY", size=22, color="#D8A15E", family=M, spacing=4)),
          Pos(48, 1260, T("2026.11.20 — 2027.02.14", size=28, color=ink, weight="BOLD", family=M)),
          Pos(48, 1310, T("北星当代艺术馆 · 一层", size=18, color="#C9B8A0", family=F)),
          Pos(48, 1370, T("12 位艺术家 / 土壤、岩芯、口述史", size=18, color="#C9B8A0", family=F)),
          Pos(48, 1460, T("“每一层，都是时间的一次呼吸。”", size=26, color=ink, family=S)),
          Pos(48, 1530, T("northstar.example / strata", size=14, color="#D8A15E", family=M))]
    return base(W, H, bg, n)


def case05():
    W, H = 1200, 1600; bg = "#F7F3EA"; ink = "#16211C"; n = [Pos(0, 0, C(width=W, height=H, color=bg))]
    cx, cy = 600, 820
    for j in range(34):
        for i in range(26):
            x = 90 + i * 40; y = 360 + j * 40
            d = math.hypot(x - cx, y - cy)
            rr = max(1.5, 17 * (1 - d / 600) + 3)
            c = "#16211C" if d < 420 else "#C25A3A"
            n.append(dot(x, y, rr * 2, c))
    n += [Pos(70, 60, T("HEAT ISLAND / FIELD NOTE 07", size=14, color="#C25A3A", weight="BOLD", family=M, spacing=2)),
          Pos(70, 100, T("热岛", size=64, color=ink, weight="BOLD", family=F)),
          Pos(70, 180, T("同一座城，最热与最凉的街区相差", size=20, color="#5A665E", family=F)),
          Pos(70, 220, T("5.2°C", size=110, color="#C25A3A", weight="BOLD", family=M)),
          Pos(70, 340, T("夏季午后 14:00 · 12 个街区 · 移动气象站", size=15, color="#5A665E", family=M)),
          Pos(70, 1450, T("树冠每增加 10%，午后地表温度约降 1.1°C。", size=18, color=ink, family=F)),
          Pos(70, 1490, T("数据为自拟教学样例；方法：步行 2m 高度、每 100m 采样。", size=13, color="#7A857D", family=F)),
          Pos(70, 1535, T("NORTHSTAR URBAN LAB / 2026", size=13, color="#C25A3A", family=M))]
    return base(W, H, bg, n)


def case06():
    W, H = 1200, 800; bg = "#071413"; n = [Pos(0, 0, C(width=W, height=H, color=bg))]
    # translucent glass panels
    panels = [(120, 120, 360, 520, "#56D6C9AA"), (300, 180, 360, 520, "#FF7C5C99"), (480, 100, 360, 520, "#F2C46B88"), (660, 210, 360, 460, "#8B6CFF99")]
    for x, y, w2, h2, c in panels:
        n += [Pos(x, y, C(width=w2, height=h2, color=c, borderRadius=8)),
              Pos(x, y, C(width=w2, height=h2, color="transparent", border="1 SOLID #F4EEE266", borderRadius=8))]
    n += [Pos(40, 620, C(width=620, height=120, color="#071413", borderRadius=8)),
          Pos(40, 40, C(width=540, height=190, color="#071413", borderRadius=8)),
          Pos(60, 40, T("NORTHSTAR CULTURE LAB / 06", size=12, color="#B8C5CE", family=M, spacing=2)),
          Pos(60, 80, T("透明剧场", size=52, color="#F4EEE2", weight="BOLD", family=S)),
          Pos(60, 150, T("一场关于观看与被观看的沉浸式剧场", size=18, color="#B8C5CE", family=F)),
          Pos(60, 650, T("2026.12.20  19:00 / 21:00", size=24, color="#F4EEE2", weight="BOLD", family=M)),
          Pos(60, 692, T("Glass Box · 120 人 · 含晚宴", size=16, color="#B8C5CE", family=F)),
          Pos(60, 740, T("invite.northstar.example", size=14, color="#56D6C9", family=M))]
    return base(W, H, bg, n)


def case07():
    W, H = 900, 1200; bg = "#F1E8D4"; ink = "#243A2C"; n = [Pos(0, 0, C(width=W, height=H, color=bg)),
         Pos(0, 0, C(width=W, height=14, color="#3F6B4A"))]
    n += [Pos(40, 40, T("NORTHSTAR CULTURE LAB / 07", size=12, color="#3F6B4A", weight="BOLD", family=M, spacing=2)),
          Pos(40, 78, T("野种子", size=58, color=ink, weight="BOLD", family=S)),
          Pos(40, 150, T("程序化植物工作坊", size=24, color="#3F6B4A", family=F)),
          Pos(40, 200, T("用规则长出一株不存在的植物，\n再把它种进城市的缝里。", size=20, color="#4A5A4C", family=F, height="1.5"), w=700, h=70)]
    # procedural plants
    for k in range(6):
        x = 110 + k * 120; basey = 900
        h = 260 + (k % 3) * 80; n.append(seg(x, basey, x + 10 * math.sin(k), basey - h, "#3F6B4A", 5))
        for j in range(4):
            yy = basey - 80 - j * 50; side = 1 if j % 2 == 0 else -1
            n.append(seg(x, yy, x + 52 * side, yy - 28, "#3F6B4A", 3))
            n.append(Pos(x + (52 * side if side > 0 else -52) - 18, yy - 54, C(width=36, height=24, color="#8FAE64", borderRadius=18)))
        n.append(dot(x, basey - h, 26, "#D9853B"))
    n += [Pos(40, 980, T("11.30  14:00–17:00", size=26, color=ink, weight="BOLD", family=M)),
          Pos(40, 1024, T("社区温室 · 自带剪刀/旧花盆", size=18, color="#4A5A4C", family=F)),
          Pos(40, 1080, T("免费 / 20 人 / 8+", size=16, color="#3F6B4A", family=F)),
          Pos(40, 1130, T("seed.northstar.example", size=13, color="#7A8574", family=M))]
    return base(W, H, bg, n)


def case08():
    W, H = 1200, 1600; bg = "#101014"; ink = "#F2E9D8"; n = [Pos(0, 0, C(width=W, height=H, color=bg))]
    n += [Pos(48, 44, T("NORTHSTAR CULTURE LAB / 08", size=13, color="#C9A86A", weight="BOLD", family=M, spacing=2)),
          Pos(48, 84, T("词语迷宫", size=96, color=ink, weight="BOLD", family=S)),
          Pos(48, 200, T("一场只能按路径读完的诗会", size=22, color="#C9A86A", family=F))]
    # maze-like line path
    pts = [(60, 300), (1080, 300), (1080, 450), (240, 450), (240, 600), (900, 600), (900, 750), (360, 750), (360, 900), (1080, 900)]
    for a, b in zip(pts, pts[1:]): n.append(seg(*a, *b, "#C9A86A", 3))
    for i, (x, y) in enumerate(pts):
        n.append(dot(x, y, 10, "#F2E9D8"))
    fragments = [("01", "在入口，先失去方向。", 100, 340), ("02", "左转，听见海。", 760, 490), ("03", "不要读最后一行。", 300, 640), ("04", "灯亮之前，诗是暗的。", 720, 790), ("05", "出口在第一个词。", 500, 940)]
    for num, text, x, y in fragments:
        n += [Pos(x, y, T(num, size=13, color="#C9A86A", family=M)), Pos(x + 34, y - 8, T(text, size=24, color=ink, family=S))]
    n += [Pos(48, 1120, T("11.22  20:00", size=42, color=ink, weight="BOLD", family=M)),
          Pos(48, 1180, T("北星书店 · 二层 · 40 人", size=20, color="#C9A86A", family=F)),
          Pos(48, 1240, T("朗读 50 min + 路径写作 30 min", size=18, color="#BDB3A3", family=F)),
          Pos(48, 1320, T("免费 / 预约入场 / 自带一支笔", size=17, color=ink, family=F)),
          Pos(48, 1420, T("“你走的那条线，就是这首诗。”", size=28, color="#C9A86A", family=S))]
    return base(W, H, bg, n)


def case09():
    W, H = 1200, 1600; bg = "#081018"; ink = "#EAF2F5"; n = [Pos(0, 0, C(width=W, height=H, color=bg))]
    cx, cy = 600, 720
    n += [Pos(cx - 300, cy - 380, C(width=600, height=760, color="transparent", border="1 SOLID #26404D", borderRadius=300))]
    # bars skyline as "portrait"
    vals = [120, 210, 80, 260, 190, 320, 150, 230, 100, 280, 170, 240, 90, 200, 130, 300, 160, 220]
    for i, v in enumerate(vals):
        x = 180 + i * 46; h = v
        n += [Pos(x, 980 - h, C(width=28, height=h, color="#56D6C9" if i % 4 == 0 else "#F2C46B" if i % 4 == 1 else "#FF7C5C", borderRadius=6))]
    # rings over
    for r, c in ((190, "#F2C46B"), (130, "#FF7C5C"), (70, "#56D6C9")):
        n.append(Pos(cx - r, cy - r, C(width=2 * r, height=2 * r, color="transparent", border=f"2 SOLID {c}", borderRadius=r)))
    n += [Pos(48, 44, T("NORTHSTAR URBAN OBSERVATORY / 09", size=12, color="#56D6C9", family=M, spacing=2)),
          Pos(48, 80, T("城市脉搏", size=64, color=ink, weight="BOLD", family=S)),
          Pos(48, 160, T("一份用 18 个街区数据画出的年度肖像", size=18, color="#9FB5C0", family=F)),
          Pos(70, 1110, T("57%", size=58, color="#F2C46B", weight="BOLD", family=M)), Pos(70, 1180, T("通勤发生在高峰", size=17, color="#9FB5C0", family=F)),
          Pos(300, 1110, T("18", size=58, color="#56D6C9", weight="BOLD", family=M)), Pos(300, 1180, T("个街区样本", size=17, color="#9FB5C0", family=F)),
          Pos(500, 1110, T("4.1", size=58, color="#FF7C5C", weight="BOLD", family=M)), Pos(500, 1180, T("平均换乘次数", size=17, color="#9FB5C0", family=F)),
          Pos(70, 1280, T("“城市不是背景，是一组正在发生的数据。”", size=24, color=ink, family=S)),
          Pos(70, 1420, T("报告 northstar.example / pulse", size=14, color="#6F8794", family=M))]
    return base(W, H, bg, n)


def case10():
    W, H = 1080, 1350; bg = "#E9DCC3"; ink = "#2B1E15"; n = [Pos(0, 0, C(width=W, height=H, color=bg))]
    # folded paper geometric panels
    n += [Pos(40, 300, C(width=420, height=520, color="#D46A4C")),
          Pos(460, 300, C(width=420, height=520, color="#2E6F6A")),
          Pos(40, 820, C(width=420, height=360, color="#D9A441")),
          Pos(460, 820, C(width=420, height=360, color="#2B1E15"))]
    # diagonal folds
    for x1, y1, x2, y2 in ((40, 300, 460, 820), (460, 300, 880, 820), (40, 820, 460, 1180), (460, 820, 880, 1180)):
        n.append(seg(x1, y1, x2, y2, "#E9DCC3", 4))
    n += [Pos(40, 44, T("NORTHSTAR CULTURE LAB / 10", size=12, color="#2B1E15", weight="BOLD", family=M, spacing=2)),
          Pos(40, 80, T("折页", size=60, color=ink, weight="BOLD", family=S)),
          Pos(40, 156, T("独立杂志市集 / 纸的第二次生命", size=20, color="#5A4635", family=F)),
          Pos(40, 1220, T("12.06–12.07  11:00–19:00", size=24, color=ink, weight="BOLD", family=M)),
          Pos(40, 1264, T("北星旧仓库 · 32 个摊位 · 免费", size=17, color="#5A4635", family=F)),
          Pos(40, 1310, T("zine.northstar.example / tables", size=13, color="#2E6F6A", family=M))]
    return base(W, H, bg, n)


B = {"case-01": (case01,1080,1350), "case-02": (case02,1200,1200), "case-03": (case03,1080,1350), "case-04": (case04,1200,1600),
     "case-05": (case05,1200,1600), "case-06": (case06,1200,800), "case-07": (case07,900,1200), "case-08": (case08,1200,1600),
     "case-09": (case09,1200,1600), "case-10": (case10,1080,1350)}


def main():
    (TMP/"dsl").mkdir(parents=True,exist_ok=True); (TMP/"renders").mkdir(parents=True,exist_ok=True)
    for cid,(fn,w,h) in B.items(): (TMP/"dsl"/f"{cid}-{VERSION}.snapshot").write_text(fn(),encoding="utf-8")
    print("B03",VERSION,"built",len(B)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
