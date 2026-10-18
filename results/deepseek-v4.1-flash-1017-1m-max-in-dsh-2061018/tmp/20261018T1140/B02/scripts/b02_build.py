"""B02 · TIDEPOOL one client, ten touchpoints."""
from __future__ import annotations
import math, os, sys
from pathlib import Path
ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve(); RUN = os.environ["SNAPSHOT_RUN_ID"]; TASK = "B02"
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"; TMP = ROOT / "tmp" / RUN / TASK
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from dsl import C, Pos, SizedBox, Stack, T  # noqa: E402
F = "Inter,Noto Sans CJK SC"; S = "Noto Serif CJK SC,Noto Sans CJK SC"; M = "Noto Sans Mono CJK SC,Inter"
NAVY = "#062A33"; FOAM = "#EAF5F0"; CORAL = "#FF7C5C"; TEAL = "#4BC3B0"; SAND = "#E8C98F"; INK = "#08252B"


def rot(deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"


def seg(x1, y1, x2, y2, color, th=2):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2; ln = math.hypot(x2 - x1, y2 - y1); a = math.degrees(math.atan2(y2 - y1, x2 - x1))
    return Pos(mx - ln / 2, my - th / 2, f'<Transform matrix="{rot(a)}" alignment="CENTER">{C(width=ln, height=th, color=color)}</Transform>')


def dot(x, y, d, color, border=None):
    kw = {"width": d, "height": d, "color": color, "borderRadius": d / 2}
    if border: kw["border"] = border
    return Pos(x - d / 2, y - d / 2, C(**kw))


def base(w, h, bg, n):
    return f'<Snapshot type="png" background="{bg}">\n' + Stack([SizedBox(w, h)] + n, width=w, height=h) + "\n</Snapshot>\n"


def mark(x, y, s=1.0, dark=False):
    c = CORAL if not dark else FOAM
    n = []
    for i, w in enumerate((54, 72, 40)):
        n.append(Pos(x, y + i * 14 * s, C(width=w * s, height=7 * s, color=c, borderRadius=4 * s)))
    n += [Pos(x + 62 * s, y + 26 * s, C(width=26 * s, height=26 * s, color="transparent", border=f"{3*s:.1f} SOLID {c}", borderRadius=13 * s)),
          Pos(x + 70 * s, y + 34 * s, C(width=10 * s, height=10 * s, color=TEAL, borderRadius=5 * s))]
    return n


def case01():
    W, H = 1080, 1350; n = [Pos(0, 0, C(width=W, height=H, color=NAVY))]
    n += mark(54, 48, 1.0)
    n += [Pos(152, 42, T("TIDEPOOL / 潮汐池", size=26, color=FOAM, weight="BOLD", family=F)),
          Pos(152, 74, T("社区海洋科学 · 东礁", size=15, color="#9DC5C1", family=F)),
          Pos(54, 190, T("把海", size=150, color=FOAM, weight="BOLD", family=S)),
          Pos(54, 350, T("带回家", size=150, color=CORAL, weight="BOLD", family=S)),
          Pos(54, 530, T("每周六 07:00 · 东礁潮池\n免费 · 6 岁以上 · 需成人陪同", size=27, color=FOAM, family=F, height="1.5"), w=700, h=110),
          Pos(54, 720, C(width=900, height=2, color="#3C6A6C")),
          Pos(54, 760, T("下一次", size=15, color=TEAL, weight="BOLD", family=M, spacing=2)),
          Pos(54, 790, T("11.14  07:00–10:30", size=45, color=FOAM, weight="BOLD", family=M)),
          Pos(54, 860, T("东礁公园 3 号门 · 潮池观察站", size=22, color="#C5DFDA", family=F)),
          Pos(54, 960, T("扫码报名 / 30 个家庭名额", size=19, color=FOAM, family=F)),
          Pos(780, 940, C(width=220, height=220, color=FOAM, borderRadius=8)),
          Pos(806, 966, C(width=168, height=168, color=NAVY)),
          Pos(830, 990, C(width=120, height=120, color=FOAM)),
          Pos(854, 1014, C(width=72, height=72, color=NAVY)),
          Pos(54, 1200, T("“先观察，再提问；只带走照片。”", size=31, color=TEAL, family=S))]
    return base(W, H, NAVY, n)


def case02():
    W, H = 1600, 1000; n = [Pos(0, 0, C(width=W, height=H, color=FOAM))]
    n += mark(48, 42, .8)
    n += [Pos(140, 36, T("TIDEPOOL / 潮汐池", size=22, color=NAVY, weight="BOLD", family=F)),
          Pos(48, 110, T("潮间带一日课", size=52, color=NAVY, weight="BOLD", family=S)),
          Pos(48, 178, T("2026.11.14 · 东礁公园 3 号门 · 07:00 集合", size=21, color="#3E6668", family=F)),
          Pos(48, 228, C(width=1504, height=3, color=NAVY))]
    slots = [("07:00", "集合 / 潮位说明", "3 号门 · 领防水卡", CORAL),
             ("07:40", "潮池观察", "A/B/C 站 · 6 组轮转", TEAL),
             ("09:00", "显微镜实验室", "遮棚 · 海水样本", SAND),
             ("10:00", "净滩 / 记录", "北滩 · 分类称重", CORAL)]
    for i, (t, title, sub, c) in enumerate(slots):
        x = 48 + i * 380
        n += [Pos(x, 290, C(width=340, height=510, color="#FFFFFF", borderRadius=12, border="1 SOLID #C9DDD6")),
              Pos(x, 290, C(width=340, height=10, color=c, borderRadius=5)),
              Pos(x + 24, 324, T(t, size=34, color=c, weight="BOLD", family=M)),
              Pos(x + 24, 388, T(title, size=26, color=NAVY, weight="BOLD", family=F)),
              Pos(x + 24, 434, T(sub, size=18, color="#55777A", family=F)),
              Pos(x + 24, 500, C(width=290, height=1, color="#D7E5DF"))]
        details = [
            ["07:00 签到 / 分组", "07:20 潮位与安全", "07:40 出发去 A 站"],
            ["A/B/C 站各 40 min", "6 组顺时针轮转", "记录表交回集合点"],
            ["装片 / 对焦 / 拍照", "海水样本 3 管", "10:00 前归还显微镜"],
            ["手套 / 夹子 / 秤", "分类称重并上传", "10:30 分享与离场"],
        ][i]
        for j, lab in enumerate(details):
            n += [Pos(x + 24, 530 + j * 54, T(f"0{j+1}" if False else "—", size=14, color="#7B9695", family=M)),
                  Pos(x + 50, 530 + j * 54, T(lab, size=17, color=NAVY, family=F))]
    n += [Pos(48, 850, T("带什么", size=16, color=CORAL, weight="BOLD", family=F)),
          Pos(48, 878, T("防滑鞋 · 遮阳帽 · 水壶 · 换洗衣物；不带走活体，不踩珊瑚。", size=18, color="#3E6668", family=F)),
          Pos(48, 936, T("雨天照常（室内实验室）· 台风预警取消 · 咨询 6688", size=15, color="#6C8B8A", family=M))]
    return base(W, H, FOAM, n)


def case03():
    W, H = 1600, 1000; n = [Pos(0, 0, C(width=W, height=H, color="#DDF0E8"))]
    n += mark(40, 34, .7)
    n += [Pos(126, 30, T("TIDEPOOL / FIELD MAP", size=14, color=NAVY, weight="BOLD", family=M, spacing=2)),
          Pos(40, 78, T("东礁观察站地图", size=42, color=NAVY, weight="BOLD", family=F)),
          Pos(40, 132, T("集合点 3 号门 → A/B/C/D 站 · 全程 1.2 km · 约 3 小时", size=18, color="#3E6668", family=F))]
    # sea
    n += [Pos(40, 190, C(width=1100, height=760, color="#B7DCD2", borderRadius=10, border="2 SOLID #6AA79E")),
          Pos(740, 190, C(width=400, height=760, color="#79BFC5"))]
    # coast shapes
    n += [Pos(40, 700, C(width=700, height=250, color="#EFE0B9", borderRadius=10)),
          Pos(40, 190, C(width=600, height=230, color="#EFE0B9", borderRadius=10)),
          Pos(330, 420, C(width=410, height=280, color="#E7D3A3", borderRadius=80))]
    n += [Pos(900, 230, T("开放海域", size=16, color="#1D5B66", family=F)),
          Pos(80, 220, T("北滩", size=18, color="#6D572D", weight="BOLD", family=F)),
          Pos(80, 730, T("东礁步道", size=18, color="#6D572D", weight="BOLD", family=F))]
    # route
    pts = [(160, 880), (260, 800), (380, 760), (470, 670), (560, 600), (660, 530), (760, 460), (860, 400)]
    for a, b in zip(pts, pts[1:]): n.append(seg(*a, *b, CORAL, 8))
    for x, y in pts: n.append(dot(x, y, 12, CORAL))
    stations = [("A", 300, 760, "入口/集合"), ("B", 470, 670, "潮池观察"), ("C", 660, 530, "显微镜"), ("D", 860, 400, "净滩")]
    for s, x, y, lab in stations:
        n += [dot(x, y, 46, FOAM, f"4 SOLID {NAVY}"), Pos(x - 9, y - 18, T(s, size=24, color=NAVY, weight="BOLD", family=M)),
              Pos(x + 30, y - 10, T(lab, size=17, color=NAVY, weight="BOLD", family=F))]
    # amenities
    n += [Pos(1170, 190, C(width=390, height=300, color="#FFFFFF", borderRadius=10, border="1 SOLID #B9D6CE")),
          Pos(1194, 210, T("设施", size=22, color=NAVY, weight="BOLD", family=F)),
          Pos(1194, 246, T("● 集合点 / 3 号门\n● 饮水点 · 入口右侧\n● 无障碍厕所 · 服务台\n● 急救站 · B 站旁\n● 冲洗点 · 停车场", size=17, color="#3E6668", family=F, height="1.6"), w=330, h=180),
          Pos(1170, 520, C(width=390, height=150, color=NAVY, borderRadius=10)),
          Pos(1194, 542, T("紧急联系", size=14, color=CORAL, family=F)),
          Pos(1194, 568, T("现场 6688 / 急救 120", size=23, color=FOAM, weight="BOLD", family=M)),
          Pos(1170, 710, T("蓝色区域为潮水覆盖区；\n涨潮前 30 分钟必须离开。", size=16, color="#3E6668", family=F, height="1.5"), w=390, h=70)]
    return base(W, H, "#DDF0E8", n)


def case04():
    W, H = 1080, 1350; n = [Pos(0, 0, C(width=W, height=H, color=NAVY))]
    n += mark(48, 42, .8, dark=True)
    n += [Pos(140, 38, T("TIDEPOOL / 潮汐池", size=20, color=FOAM, weight="BOLD", family=F)),
          Pos(48, 120, T("缺的不是热情，\n是下一班岗。", size=62, color=FOAM, weight="BOLD", family=S, height="1.35"), w=900, h=190),
          Pos(48, 330, T("11.14 潮间带日 · 招募 18 名志愿者", size=22, color=CORAL, weight="BOLD", family=F))]
    roles = [("观察引导", "带 6–8 人小组\n轮转 A/B/C 站", "6 人"), ("显微镜助教", "装片/对焦/记录\n无需专业背景", "4 人"),
             ("净滩记录", "分类/称重/拍照\n能搬 5 kg", "5 人"), ("摄影/补给", "拍记录照/发水\n自备相机更佳", "3 人")]
    for i, (title, body, num) in enumerate(roles):
        x = 48 + (i % 2) * 500; y = 400 + (i // 2) * 230
        n += [Pos(x, y, C(width=470, height=200, color="#0D3E48", borderRadius=12, border="1 SOLID #2E6267")),
              Pos(x + 20, y + 18, T(title, size=25, color=FOAM, weight="BOLD", family=F)),
              Pos(x + 20, y + 60, T(body, size=18, color="#B5D6D0", family=F, height="1.45"), w=360, h=70),
              Pos(x + 390, y + 20, T(num, size=22, color=CORAL, weight="BOLD", family=M))]
    n += [Pos(48, 920, T("培训", size=15, color=TEAL, weight="BOLD", family=F)),
          Pos(48, 948, T("11.12 19:00 线上 30 min（必须参加）\n11.14 06:30 现场交接 · 提供早餐", size=19, color=FOAM, family=F, height="1.5"), w=700, h=74),
          Pos(48, 1080, C(width=984, height=2, color="#2E6267")),
          Pos(48, 1110, T("报名：tidepool.example / volunteer", size=19, color=FOAM, family=F)),
          Pos(48, 1160, T("联系人 阿岚 · 6688（08:00–20:00）", size=17, color="#9DC5C1", family=F))]
    return base(W, H, NAVY, n)


def case05():
    W, H = 1200, 600; n = [Pos(0, 0, C(width=W, height=H, color=FOAM))]
    n += [Pos(0, 0, C(width=W, height=18, color=CORAL))]
    n += mark(40, 38, .7)
    n += [Pos(128, 34, T("TIDEPOOL / 潮汐池", size=18, color=NAVY, weight="BOLD", family=F)),
          Pos(40, 110, T("潮汐通行证", size=52, color=NAVY, weight="BOLD", family=S)),
          Pos(40, 180, T("2026.11.14 · 07:00–10:30", size=27, color=NAVY, weight="BOLD", family=M)),
          Pos(40, 224, T("东礁公园 3 号门 · 家庭场", size=20, color="#3E6668", family=F)),
          Pos(40, 284, T("持此证入场 · 限 2 成人 + 2 儿童", size=17, color="#6C8B8A", family=F)),
          Pos(40, 340, T("NO. 014", size=25, color=CORAL, weight="BOLD", family=M)),
          Pos(40, 390, T("紧急联系人：阿岚 6688", size=16, color="#3E6668", family=F))]
    # perforation
    for y in range(30, 570, 22):
        n.append(Pos(760, y, C(width=2, height=10, color="#9DBDB5")))
    n += [Pos(800, 36, T("ADMIT ONE / 家庭", size=15, color=NAVY, weight="BOLD", family=M)),
          Pos(800, 70, T("TIDE\nPOOL", size=54, color=NAVY, weight="BOLD", family=M, height="1.0"), w=300, h=150),
          Pos(800, 240, T("入场 07:00\n开始 07:20", size=22, color=NAVY, family=M)),
          Pos(800, 320, C(width=150, height=150, color=FOAM, border="2 SOLID #062A33")),
          Pos(820, 340, C(width=110, height=110, color=NAVY)),
          Pos(840, 360, C(width=70, height=70, color=FOAM)),
          Pos(860, 380, C(width=30, height=30, color=NAVY)),
          Pos(800, 500, T("请携带防水袋 / 不带走活体", size=14, color="#6C8B8A", family=F))]
    return base(W, H, FOAM, n)


def case06():
    W, H = 1080, 1350; n = [Pos(0, 0, C(width=W, height=H, color="#F4E9D2"))]
    n += mark(44, 38, .75)
    n += [Pos(132, 34, T("TIDEPOOL / SAFETY", size=14, color=NAVY, weight="BOLD", family=M, spacing=2)),
          Pos(44, 100, T("潮汐安全卡", size=56, color=NAVY, weight="BOLD", family=F)),
          Pos(44, 176, T("涨潮比你想的快。看旗、看表、看退路。", size=22, color="#6B4E2E", family=F))]
    # tide clock
    n += [Pos(44, 230, C(width=480, height=480, color=NAVY, borderRadius=240)),
          Pos(84, 270, C(width=400, height=400, color="transparent", border="2 SOLID #4BC3B0", borderRadius=200)),
          Pos(264, 450, C(width=40, height=40, color=CORAL, borderRadius=20))]
    # clock hands
    n += [seg(284, 470, 284, 330, FOAM, 8), seg(284, 470, 390, 500, CORAL, 6),
          Pos(250, 300, T("满潮", size=13, color=FOAM, family=F)), Pos(400, 470, T("退潮", size=13, color=CORAL, family=F)),
          Pos(214, 500, T("07:00", size=16, color=TEAL, weight="BOLD", family=M))]
    n += [Pos(560, 240, T("今天", size=18, color="#6B4E2E", family=F)),
          Pos(560, 270, T("低潮 07:42\n高潮 13:18", size=38, color=NAVY, weight="BOLD", family=M, height="1.4"), w=440, h=130),
          Pos(560, 410, T("安全窗口\n07:00–10:30", size=24, color=CORAL, weight="BOLD", family=F, height="1.3"), w=400, h=100)]
    rules = [("01", "只在绿旗时下水", "黄旗只观察，红旗不上礁。"), ("02", "鞋要防滑", "礁石有苔；不要穿拖鞋。"), ("03", "不背对海", "每 10 分钟看一次潮线。"), ("04", "儿童一臂距离", "指定成人看护，不追浪。"), ("05", "离场带走", "垃圾/装备/照片，只留脚印。")]
    y = 760
    for num, t1, t2 in rules:
        n += [Pos(44, y, T(num, size=18, color=CORAL, weight="BOLD", family=M)),
              Pos(84, y - 4, T(t1, size=23, color=NAVY, weight="BOLD", family=F)),
              Pos(84, y + 28, T(t2, size=17, color="#6B4E2E", family=F))]
        y += 92
    n += [Pos(44, 1240, T("紧急：现场 6688 / 120 · 最近医院 2.4 km", size=15, color=NAVY, family=M))]
    return base(W, H, "#F4E9D2", n)


def case07():
    W, H = 900, 1200; n = [Pos(0, 0, C(width=W, height=H, color=NAVY))]
    n += mark(40, 36, .65, dark=True)
    n += [Pos(124, 32, T("TIDEPOOL / SPECIES CARD", size=12, color=FOAM, weight="BOLD", family=M, spacing=2)),
          Pos(40, 96, T("六种潮池生物", size=42, color=FOAM, weight="BOLD", family=S)),
          Pos(40, 150, T("只看不抓 · 拍完就放 · 不翻大石", size=17, color=TEAL, family=F))]
    species = [("海葵", "触手环 / 岩缝", "A 站", CORAL), ("寄居蟹", "螺壳 / 沙底", "A/B 站", SAND), ("海星", "五腕 / 潮池", "B 站", CORAL),
               ("海胆", "刺球 / 洞穴", "C 站", "#B7A4E8"), ("藤壶", "白锥 / 岩面", "全站", FOAM), ("海藻", "带状 / 水线", "北滩", TEAL)]
    for i, (name, form, station, c) in enumerate(species):
        x = 40 + (i % 2) * 420; y = 210 + (i // 2) * 290
        n += [Pos(x, y, C(width=400, height=260, color="#0D3E48", borderRadius=10, border="1 SOLID #2E6267")),
              Pos(x + 24, y + 160, T(name, size=28, color=FOAM, weight="BOLD", family=F)),
              Pos(x + 24, y + 198, T(form, size=16, color="#B5D6D0", family=F)),
              Pos(x + 320, y + 18, T(station, size=13, color=TEAL, family=M))]
        # simple morphology icons (no external images)
        cx2, cy2 = x + 86, y + 86
        if name == "海葵":
            n.append(dot(cx2, cy2, 44, "transparent", f"2 SOLID {c}"))
            for k in range(10):
                a = math.radians(k * 36); n.append(seg(cx2, cy2, cx2 + 32 * math.cos(a), cy2 + 32 * math.sin(a), c, 3))
        elif name == "寄居蟹":
            n.append(dot(cx2, cy2, 54, c)); n.append(dot(cx2 + 18, cy2 + 10, 40, "#0D3E48"))
            n.append(C and Pos(cx2 - 30, cy2 - 30, C(width=16, height=16, color=NAVY)))
        elif name == "海星":
            for k in range(5):
                a = math.radians(-90 + k * 72); n.append(seg(cx2, cy2, cx2 + 40 * math.cos(a), cy2 + 40 * math.sin(a), c, 7))
            n.append(dot(cx2, cy2, 20, c))
        elif name == "海胆":
            n.append(dot(cx2, cy2, 42, c))
            for k in range(12):
                a = math.radians(k * 30); n.append(seg(cx2 + 14 * math.cos(a), cy2 + 14 * math.sin(a), cx2 + 44 * math.cos(a), cy2 + 44 * math.sin(a), c, 2))
        elif name == "藤壶":
            for dx, dy in ((-24, -14), (18, -18), (-4, 22)):
                n.append(dot(cx2 + dx, cy2 + dy, 34, "transparent", f"3 SOLID {c}"))
        else:
            for dx in (-20, 0, 20):
                n.append(seg(cx2 + dx, cy2 - 28, cx2 + dx + 8, cy2, c, 5)); n.append(seg(cx2 + dx + 8, cy2, cx2 + dx - 4, cy2 + 28, c, 5))
    n += [Pos(40, 1110, T("记录：日期 / 站号 / 数量 / 照片；发现受伤生物请联系 B 站。", size=13, color="#9DC5C1", family=F))]
    return base(W, H, NAVY, n)


def case08():
    W, H = 1200, 800; n = [Pos(0, 0, C(width=W, height=H, color=NAVY))]
    n += [Pos(0, 0, C(width=W, height=14, color=TEAL))]
    n += mark(48, 44, .75, dark=True)
    n += [Pos(134, 38, T("TIDEPOOL / 潮汐池", size=18, color=FOAM, weight="BOLD", family=F)),
          Pos(48, 120, T("潮汐会员", size=30, color=TEAL, weight="BOLD", family=M)),
          Pos(48, 170, T("林见鹿", size=48, color=FOAM, weight="BOLD", family=S)),
          Pos(48, 240, T("MEMBER NO. 027 · 2026", size=16, color="#9DC5C1", family=M)),
          Pos(48, 300, T("权益", size=14, color=CORAL, family=F)),
          Pos(48, 326, T("● 活动优先报名（提前 48h）\n● 季度潮池夜观 1 次\n● 年刊与物种卡套装\n● 合作书店 9 折", size=19, color=FOAM, family=F, height="1.55"), w=520, h=150),
          Pos(48, 560, T("续费：tidepool.example / member", size=15, color="#9DC5C1", family=F))]
    # wave mark right
    n += [Pos(720, 220, C(width=380, height=380, color="#0D3E48", borderRadius=190, border="2 SOLID #2E6267"))]
    for i, rr in enumerate((150, 120, 90)):
        n += [Pos(910 - rr, 410 - rr, C(width=2 * rr, height=2 * rr, color="transparent", border=f"3 SOLID {TEAL if i==0 else CORAL if i==1 else SAND}", borderRadius=rr))]
    n += [dot(910, 410, 26, FOAM)]
    n += [Pos(760, 640, T("每一次观察，都是下一次保护。", size=18, color=TEAL, family=S))]
    return base(W, H, NAVY, n)


def case09():
    W, H = 900, 1200; n = [Pos(0, 0, C(width=W, height=H, color=FOAM))]
    n += mark(40, 34, .65)
    n += [Pos(120, 30, T("TIDEPOOL / SEA STATE", size=12, color=NAVY, weight="BOLD", family=M, spacing=2)),
          Pos(40, 92, T("今日海况旗", size=48, color=NAVY, weight="BOLD", family=F)),
          Pos(40, 154, T("决定是否下水 / 上礁", size=18, color="#3E6668", family=F))]
    flags = [("GREEN", "开放", "可下水 / 上礁\n按分组路线", "#2E8B57", "07:00–10:30"),
             ("YELLOW", "受限", "只观察 / 不涉水\n改室内实验室", "#D99A2B", "风力 > 20 km/h"),
             ("RED", "关闭", "不上海礁\n活动改期", "#C64B3C", "雷电 / 台风 / 大浪")]
    for i, (en, zh, body, c, when) in enumerate(flags):
        y = 230 + i * 290
        n += [Pos(40, y, C(width=820, height=250, color="#FFFFFF", borderRadius=12, border=f"3 SOLID {c}")),
              Pos(64, y + 18, T(en, size=17, color=c, weight="BOLD", family=M, spacing=2)),
              Pos(64, y + 48, T(zh, size=48, color=c, weight="BOLD", family=F)),
              Pos(64, y + 118, T(body, size=22, color=NAVY, family=F, height="1.4"), w=420, h=90),
              Pos(560, y + 54, T(when, size=18, color="#55777A", family=F)),
              dot(760, y + 90, 80, c)]
    n += [Pos(40, 1090, T("当前：GREEN · 更新 06:30 / 下次 11:30", size=20, color="#2E8B57", weight="BOLD", family=F)),
          Pos(40, 1130, T("以现场旗杆为准；不要只看网页。", size=15, color="#6C8B8A", family=F))]
    return base(W, H, FOAM, n)


def case10():
    W, H = 1200, 1600; n = [Pos(0, 0, C(width=W, height=H, color=NAVY))]
    n += mark(48, 40, .8, dark=True)
    n += [Pos(136, 34, T("TIDEPOOL / ANNUAL 2026", size=13, color=FOAM, weight="BOLD", family=M, spacing=2)),
          Pos(48, 130, T("海一直在，\n我们只是学会了看。", size=58, color=FOAM, weight="BOLD", family=S, height="1.3"), w=1000, h=180),
          Pos(48, 360, T("年度报告 · 社区海洋科学计划", size=22, color=TEAL, family=F))]
    stats = [("1,240", "kg", "净滩垃圾"), ("48", "场", "潮池观察"), ("312", "人", "志愿者"), ("6", "站", "长期监测")]
    for i, (num, unit, lab) in enumerate(stats):
        x = 48 + (i % 2) * 540; y = 470 + (i // 2) * 230
        n += [Pos(x, y, C(width=500, height=200, color="#0D3E48", borderRadius=12, border="1 SOLID #2E6267")),
              Pos(x + 24, y + 24, T(num, size=64, color=FOAM, weight="BOLD", family=M)),
              Pos(x + 24, y + 108, T(unit, size=20, color=CORAL, family=F)),
              Pos(x + 24, y + 146, T(lab, size=18, color="#B5D6D0", family=F))]
    n += [Pos(48, 980, T("钱花在哪", size=20, color=TEAL, weight="BOLD", family=F))]
    bars = [("观察设备/显微镜", 42, CORAL), ("净滩与运输", 26, SAND), ("志愿者培训", 18, TEAL), ("社区免费场", 14, "#B7A4E8")]
    for i, (lab, pctv, c) in enumerate(bars):
        y = 1020 + i * 54
        n += [Pos(48, y, T(lab, size=17, color=FOAM, family=F)),
              Pos(420, y + 4, C(width=560 * pctv / 100, height=18, color=c, borderRadius=9)),
              Pos(1000, y, T(f"{pctv}%", size=17, color=c, weight="BOLD", family=M))]
    n += [Pos(48, 1270, T("2027 计划", size=20, color=TEAL, weight="BOLD", family=F)),
          Pos(48, 1306, T("新增 2 个无障碍观察站；把物种卡做成盲文/大字版；\n与 3 所小学共备一堂潮池课。", size=19, color=FOAM, family=F, height="1.5"), w=1000, h=80),
          Pos(48, 1460, T("tidepool.example · 公开年报 / 数据附录", size=14, color="#9DC5C1", family=F))]
    return base(W, H, NAVY, n)


B = {"case-01": (case01, 1080, 1350), "case-02": (case02, 1600, 1000), "case-03": (case03, 1600, 1000),
     "case-04": (case04, 1080, 1350), "case-05": (case05, 1200, 600), "case-06": (case06, 1080, 1350),
     "case-07": (case07, 900, 1200), "case-08": (case08, 1200, 800), "case-09": (case09, 900, 1200),
     "case-10": (case10, 1200, 1600)}


def main():
    (TMP / "dsl").mkdir(parents=True, exist_ok=True); (TMP / "renders").mkdir(parents=True, exist_ok=True)
    for cid, (fn, w, h) in B.items():
        (TMP / "dsl" / f"{cid}-{VERSION}.snapshot").write_text(fn(), encoding="utf-8")
    print("B02", VERSION, "built", len(B))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
