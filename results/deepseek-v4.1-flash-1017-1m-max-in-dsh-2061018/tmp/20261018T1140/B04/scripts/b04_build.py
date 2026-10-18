"""B04 · research visual special on global road traffic deaths."""
from __future__ import annotations
import math, os, sys
from pathlib import Path
ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve(); RUN = os.environ["SNAPSHOT_RUN_ID"]; TASK = "B04"
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"; TMP = ROOT / "tmp" / RUN / TASK
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts")); sys.path.insert(0, str(ROOT / "tmp" / RUN / "B02" / "scripts"))
from dsl import C, Pos, SizedBox, Stack, T  # noqa: E402
from b02_build import rot, seg, dot, base  # noqa: E402
F = "Inter,Noto Sans CJK SC"; S = "Noto Serif CJK SC,Noto Sans CJK SC"; M = "Noto Sans Mono CJK SC,Inter"
INK = "#151515"; PAPER = "#F3EEE4"; RED = "#C7442E"; BLUE = "#2E5C7A"; GOLD = "#C99A3C"
SRC = "Source: WHO, Road traffic injuries, fact sheet, 20 Jul 2026 · who.int"


def case01():
    W, H = 1200, 1600; n = [Pos(0, 0, C(width=W, height=H, color=INK))]
    n += [Pos(56, 48, T("NORTHSTAR REVIEW / VISUAL DOSSIER 04", size=13, color="#B9B2A6", weight="BOLD", family=M, spacing=2)),
          Pos(56, 90, T("1.16", size=210, color=PAPER, weight="BOLD", family=M)),
          Pos(56, 390, T("million", size=64, color=RED, weight="BOLD", family=S)),
          Pos(56, 480, T("每年，道路交通事故\n夺走约 116 万人的生命。", size=48, color=PAPER, weight="BOLD", family=S, height="1.35"), w=1000, h=160),
          Pos(56, 690, T("但这不是“意外”。", size=40, color=GOLD, family=S)),
          Pos(56, 770, T("超速、分心、缺少头盔/安全带、\n不安全的道路与碰撞后延误，\n都是可以被设计改变的变量。", size=27, color="#D8D0C2", family=F, height="1.55"), w=1000, h=180),
          Pos(56, 1200, T("九个事实，拆开一个总量。", size=24, color=RED, family=F)),
          Pos(56, 1500, T(SRC, size=13, color="#8E877B", family=M))]
    # vertical red measure
    n += [Pos(980, 100, C(width=6, height=1100, color=RED)), Pos(1000, 1200, T("116万 / 年", size=16, color=RED, family=M))]
    return base(W, H, INK, n)


def case02():
    W, H = 1600, 1000; n = [Pos(0, 0, C(width=W, height=H, color=PAPER))]
    n += [Pos(56, 46, T("02 / THE MISMATCH", size=14, color=RED, weight="BOLD", family=M, spacing=2)),
          Pos(56, 84, T("死亡在低收入国家，车辆却在别处", size=44, color=INK, weight="BOLD", family=S)),
          Pos(56, 150, T("全球道路交通死亡与车辆保有量的分布", size=19, color="#605A4F", family=F)),
          Pos(56, 230, T("92%", size=140, color=RED, weight="BOLD", family=M)),
          Pos(310, 250, T("的道路交通死亡\n发生在中低收入国家", size=28, color=INK, family=F, height="1.4"), w=650, h=100),
          Pos(56, 430, T("这些国家拥有约 60% 的全球车辆", size=22, color="#605A4F", family=F)),
          Pos(56, 520, C(width=1400, height=54, color="#D9D0C2", borderRadius=8)),
          Pos(56, 520, C(width=1288, height=54, color=RED, borderRadius=8)),
          Pos(56, 590, C(width=1400, height=54, color="#D9D0C2", borderRadius=8)),
          Pos(56, 590, C(width=840, height=54, color=BLUE, borderRadius=8)),
          Pos(56, 650, T("死亡 92%", size=19, color=RED, weight="BOLD", family=M)),
          Pos(56, 698, T("车辆 60%", size=19, color=BLUE, weight="BOLD", family=M)),
          Pos(56, 800, T("注：60% 为 WHO 对全球车辆保有量的约数；两个百分比的基数不同，不能相减。", size=16, color="#605A4F", family=F)),
          Pos(56, 930, T(SRC, size=13, color="#8E877B", family=M))]
    return base(W, H, PAPER, n)


def case03():
    W, H = 1200, 1600; n = [Pos(0, 0, C(width=W, height=H, color="#F6F1E7"))]
    n += [Pos(56, 46, T("03 / AGE", size=14, color=BLUE, weight="BOLD", family=M, spacing=2)),
          Pos(56, 84, T("5–29 岁", size=100, color=INK, weight="BOLD", family=M)),
          Pos(56, 225, T("道路交通事故是这一年龄段\n全球的头号死因。", size=34, color=INK, family=S, height="1.4"), w=900, h=110),
          Pos(56, 390, T("2/3", size=140, color=RED, weight="BOLD", family=M)),
          Pos(330, 410, T("的死亡发生在\n18–59 岁工作年龄", size=28, color=INK, family=F, height="1.4"), w=700, h=100),
          Pos(56, 600, T("男性死亡约为女性的 3 倍", size=24, color=INK, family=F)),
          Pos(56, 640, T("每个方块 = 5% 的死亡；20 块合计，男:女 ≈ 3:1", size=14, color="#7B7468", family=F))]
    # 20 blocks, 15 blue / 5 red, each 5%
    for i in range(20):
        x = 60 + (i % 10) * 100; y = 700 + (i // 10) * 110
        c = BLUE if i < 15 else RED
        n.append(Pos(x, y, C(width=70, height=70, color=c, borderRadius=8)))
    n += [Pos(60, 1010, T("男性 约 75%", size=18, color=BLUE, weight="BOLD", family=F)),
          Pos(360, 1040, T("女性 约 25%", size=18, color=RED, weight="BOLD", family=F)),
          Pos(56, 1130, T("“头号死因”指该年龄段的全部死因排序；\n不是说道路事故只影响年轻人。", size=20, color="#5E574C", family=F, height="1.5"), w=1000, h=90),
          Pos(56, 1500, T(SRC, size=13, color="#8E877B", family=M))]
    return base(W, H, "#F6F1E7", n)


def case04():
    W, H = 1200, 1600; n = [Pos(0, 0, C(width=W, height=H, color=INK))]
    n += [Pos(56, 46, T("04 / WHO IS VULNERABLE", size=13, color="#B9B2A6", weight="BOLD", family=M, spacing=2)),
          Pos(56, 84, T("超过一半", size=92, color=PAPER, weight="BOLD", family=S)),
          Pos(56, 190, T("的道路交通死亡\n属于弱势道路使用者", size=34, color=GOLD, family=F, height="1.4"), w=900, h=110),
          Pos(56, 340, T("行人 / 骑行者 / 摩托车骑手", size=24, color=PAPER, family=F))]
    # 100 dots, 54 colored
    for i in range(100):
        x = 60 + (i % 20) * 54; y = 430 + (i // 20) * 54
        n.append(dot(x, y, 30, RED if i < 60 else "#3A3A36"))
    n += [Pos(60, 720, T("每个点 = 1% 的死亡；红色示意“超过一半”，不是精确统计。", size=14, color="#B9B2A6", family=F)),
          Pos(56, 820, T("同一个碰撞速度，\n行人与车内乘员承受的能量完全不同。", size=30, color=PAPER, family=S, height="1.4"), w=940, h=100),
          Pos(56, 960, T("这就是为什么“安全系统”要把\n行人、骑行者与摩托车骑手放在设计中心。", size=20, color="#CFC7B9", family=F, height="1.5"), w=980, h=90),
          Pos(56, 1500, T(SRC, size=13, color="#8E877B", family=M))]
    return base(W, H, INK, n)


def case05():
    W, H = 1600, 1000; n = [Pos(0, 0, C(width=W, height=H, color="#1B1A17"))]
    n += [Pos(56, 46, T("05 / SPEED", size=14, color=GOLD, weight="BOLD", family=M, spacing=2)),
          Pos(56, 84, T("速度 +1%，致命风险 +4%", size=44, color=PAPER, weight="BOLD", family=S)),
          Pos(56, 140, T("平均速度每增加 1%，致命碰撞风险约增加 4%，严重碰撞风险约增加 3%。", size=19, color="#BDB5A8", family=F)),
          Pos(56, 230, T("+1%", size=120, color=BLUE, weight="BOLD", family=M)),
          Pos(330, 260, T("平均速度", size=22, color="#BDB5A8", family=F)),
          Pos(56, 380, T("→", size=80, color=GOLD, family=M)),
          Pos(260, 380, T("+4%", size=120, color=RED, weight="BOLD", family=M)),
          Pos(560, 410, T("致命碰撞风险", size=22, color="#BDB5A8", family=F)),
          Pos(56, 580, T("行人死亡风险：50 → 65 km/h 约 4.5 倍", size=27, color=PAPER, family=F)),
          Pos(56, 640, T("图示为相对风险，不是每 100 人中的绝对死亡数。", size=15, color="#8E877B", family=F))]
    # speed bars 50/65
    for i, v in enumerate((50, 65)):
        x = 80 + i * 520
        n += [Pos(x, 730, T(f"{v} km/h", size=34, color=PAPER, weight="BOLD", family=M)),
              Pos(x, 790, C(width=v * 7, height=42, color=BLUE if v == 50 else RED, borderRadius=8)),
              Pos(x, 842, T("行人死亡风险", size=14, color="#8E877B", family=F)),
              Pos(x + v * 7 + 14, 796, T("1×" if v == 50 else "4.5×", size=30, color=GOLD, weight="BOLD", family=M))]
    n += [Pos(56, 930, T(SRC, size=13, color="#8E877B", family=M))]
    return base(W, H, "#1B1A17", n)


def case06():
    W, H = 1200, 1600; n = [Pos(0, 0, C(width=W, height=H, color=PAPER))]
    n += [Pos(56, 46, T("06 / PROTECTION", size=14, color=RED, weight="BOLD", family=M, spacing=2)),
          Pos(56, 84, T("三件被低估的装备", size=44, color=INK, weight="BOLD", family=S)),
          Pos(56, 140, T("正确使用时的相对保护效果；不是“用了就零风险”。", size=18, color="#605A4F", family=F))]
    cards = [("头盔", ">6×", "降低死亡风险", "脑损伤风险最多降 74%", RED),
             ("安全带", "50%", "降低车内乘员死亡", "正确佩戴 · 前后排", BLUE),
             ("儿童约束", "71%", "降低婴儿死亡", "按身高/体重选型", GOLD)]
    for i, (name, val, lab, note, c) in enumerate(cards):
        y = 240 + i * 390
        n += [Pos(56, y, C(width=1080, height=330, color="#FFFFFF", borderRadius=12, border="1 SOLID #D8CFC0")),
              Pos(56, y, C(width=10, height=330, color=c, borderRadius=5)),
              Pos(90, y + 28, T(name, size=30, color=INK, weight="BOLD", family=F)),
              Pos(90, y + 84, T(val, size=100 if len(val) < 4 else 76, color=c, weight="BOLD", family=M)),
              Pos(440, y + 96, T(lab, size=26, color=INK, family=F)),
              Pos(440, y + 146, T(note, size=18, color="#605A4F", family=F)),
              Pos(90, y + 240, T("来源：WHO 2026 fact sheet；相对风险，因人群/速度/正确使用而异。", size=13, color="#8E877B", family=F))]
    n += [Pos(56, 1530, T(SRC, size=12, color="#8E877B", family=M))]
    return base(W, H, PAPER, n)


def case07():
    W, H = 1080, 1350; n = [Pos(0, 0, C(width=W, height=H, color="#0C1418"))]
    cx, cy = 540, 600
    for r in (360, 280, 200, 120):
        n.append(Pos(cx - r, cy - r, C(width=2 * r, height=2 * r, color="transparent", border="1 SOLID #2A4B57", borderRadius=r)))
    n += [Pos(470, 540, C(width=140, height=250, color="#E7F0F2", borderRadius=18)),
          Pos(490, 562, C(width=100, height=180, color="#0C1418", borderRadius=10)),
          Pos(520, 726, T("4×", size=36, color=RED, weight="BOLD", family=M)),
          Pos(56, 46, T("07 / DISTRACTION", size=13, color="#7FB3C4", weight="BOLD", family=M, spacing=2)),
          Pos(56, 84, T("看一眼手机，\n撞车风险约 4 倍。", size=56, color="#EAF2F5", weight="BOLD", family=S, height="1.25"), w=900, h=160),
          Pos(56, 290, T("使用手机（含免手持）的驾驶人，\n发生碰撞的风险约为不使用者 4 倍。", size=22, color="#A9C4CF", family=F, height="1.5"), w=900, h=80),
          Pos(56, 1010, T("免手持并不明显更安全；\n发短信会进一步增加风险。", size=22, color=GOLD, family=F, height="1.5"), w=900, h=80),
          Pos(56, 1270, T(SRC, size=12, color="#6E8995", family=M))]
    return base(W, H, "#0C1418", n)


def case08():
    W, H = 1600, 1000; n = [Pos(0, 0, C(width=W, height=H, color="#EEF1EA"))]
    n += [Pos(56, 46, T("08 / SAFE SYSTEM", size=14, color="#2E6B4F", weight="BOLD", family=M, spacing=2)),
          Pos(56, 84, T("安全系统：四条腿，一个也不能少", size=44, color="#15251C", weight="BOLD", family=S)),
          Pos(56, 140, T("系统要容纳人的错误，而不是要求人永不犯错。", size=20, color="#4C5E53", family=F))]
    cols = [("安全道路", "人行道 / 自行车道 / 安全交叉口", "#2E6B4F"),
            ("安全速度", "限速 / 减速带 / 30 km/h 街区", "#C7442E"),
            ("安全车辆", "碰撞标准 / 稳定控制 / 气囊", "#2E5C7A"),
            ("安全使用者", "头盔 / 安全带 / 不酒驾 / 不分心", "#C99A3C")]
    for i, (title, body, c) in enumerate(cols):
        x = 56 + i * 374
        n += [Pos(x, 230, C(width=346, height=420, color="#FFFFFF", borderRadius=12, border="1 SOLID #CFD8CF")),
              Pos(x + 22, 252, T("0" + str(i + 1), size=18, color=c, weight="BOLD", family=M)),
              Pos(x + 22, 290, T(title, size=28, color="#15251C", weight="BOLD", family=F)),
              Pos(x + 22, 340, T(body, size=18, color="#4C5E53", family=F, height="1.5"), w=300, h=200),
              Pos(x + 22, 570, C(width=80, height=6, color=c, borderRadius=3))]
    n += [Pos(56, 720, C(width=1488, height=150, color="#15251C", borderRadius=12)),
          Pos(80, 742, T("碰撞后", size=24, color="#F2C46B", weight="BOLD", family=F)),
          Pos(80, 778, T("及时呼救 / 现场止血 / 快速转运 / 康复：分钟级的延误会把可救的伤变成死亡。", size=19, color="#E9EEE8", family=F)),
          Pos(56, 930, T(SRC, size=13, color="#6B7B70", family=M))]
    return base(W, H, "#EEF1EA", n)


def case09():
    W, H = 1200, 1600; n = [Pos(0, 0, C(width=W, height=H, color="#F3EEE4"))]
    n += [Pos(56, 46, T("09 / THE COST", size=14, color=RED, weight="BOLD", family=M, spacing=2)),
          Pos(56, 84, T("代价不只在死亡数字里", size=42, color=INK, weight="BOLD", family=S)),
          Pos(56, 190, T("3%", size=180, color=RED, weight="BOLD", family=M)),
          Pos(330, 240, T("多数国家 GDP\n因道路交通伤害损失约 3%", size=28, color=INK, family=F, height="1.4"), w=760, h=100),
          Pos(56, 430, T("2000–5000 万", size=80, color=BLUE, weight="BOLD", family=M)),
          Pos(56, 540, T("人 / 年 遭受非致命伤，其中许多人留下残疾。", size=24, color="#4F4A41", family=F)),
          Pos(56, 640, C(width=1088, height=2, color="#CFC5B4")),
          Pos(56, 680, T("谁在承担？", size=28, color=INK, weight="BOLD", family=F)),
          Pos(56, 730, T("伤者的治疗与康复\n家庭的照护与收入损失\n国家卫生系统与生产力", size=24, color="#4F4A41", family=F, height="1.7"), w=1000, h=150),
          Pos(56, 960, T("“3% GDP” 是 WHO 对多数国家的估计，\n不是每个国家都恰好 3%。", size=20, color=RED, family=F, height="1.5"), w=1000, h=80),
          Pos(56, 1500, T(SRC, size=13, color="#8E877B", family=M))]
    return base(W, H, "#F3EEE4", n)


def case10():
    W, H = 1200, 1600; n = [Pos(0, 0, C(width=W, height=H, color=INK))]
    n += [Pos(56, 46, T("10 / THE TARGET", size=14, color="#F2C46B", weight="BOLD", family=M, spacing=2)),
          Pos(56, 90, T("到 2030 年，\n把死亡与伤害减半。", size=58, color=PAPER, weight="BOLD", family=S, height="1.3"), w=1000, h=170),
          Pos(56, 300, T("联合国大会目标 A/RES/74/299", size=17, color="#BDB5A8", family=M))]
    # half circle diagram
    cx, cy, r = 600, 720, 260
    n += [Pos(cx - r, cy - r, C(width=2 * r, height=2 * r, color="transparent", border="24 SOLID #3A3A36", borderRadius=r)),
          Pos(cx - r, cy, C(width=2 * r, height=r, color=INK))]
    n += [Pos(cx - 80, cy - 360, T("当前", size=18, color="#BDB5A8", family=F)),
          Pos(cx - 260, cy + 80, T("2030 目标：−50%", size=26, color="#F2C46B", weight="BOLD", family=F)),
          Pos(56, 1090, T("能做的不只是“小心一点”", size=28, color=PAPER, weight="BOLD", family=F))]
    actions = ["30 km/h 街区 + 测速执法", "摩托车头盔与安全带法", "酒驾/分心执法", "碰撞后急救与康复", "把安全纳入道路设计"]
    for i, a in enumerate(actions):
        n += [Pos(80, 1150 + i * 54, T("0" + str(i + 1), size=15, color=RED, family=M)),
              Pos(126, 1146 + i * 54, T(a, size=20, color="#D8D0C2", family=F))]
    n += [Pos(56, 1510, T(SRC, size=12, color="#8E877B", family=M))]
    return base(W, H, INK, n)


B = {"case-01": (case01,1200,1600), "case-02": (case02,1600,1000), "case-03": (case03,1200,1600), "case-04": (case04,1200,1600),
     "case-05": (case05,1600,1000), "case-06": (case06,1200,1600), "case-07": (case07,1080,1350), "case-08": (case08,1600,1000),
     "case-09": (case09,1200,1600), "case-10": (case10,1200,1600)}


def main():
    (TMP/"dsl").mkdir(parents=True,exist_ok=True); (TMP/"renders").mkdir(parents=True,exist_ok=True)
    for cid,(fn,w,h) in B.items(): (TMP/"dsl"/f"{cid}-{VERSION}.snapshot").write_text(fn(),encoding="utf-8")
    print("B04",VERSION,"built",len(B)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
