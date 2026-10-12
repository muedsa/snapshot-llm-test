"""B01 case-02 · 独立音乐节三日主视觉海报（1080×1620）。

受众：购票用户在地铁灯箱 / 社交竖图前 3 秒内记住活动、日期与主舞台结构。
品牌「潮汐声场 TIDAL FIELD」与全部艺人名、价格均为虚构演示。
主要能力：镂空描边大字、textShadow 色散霓虹、SWEEP 色轮、RADIAL 光、旋转斜切带、
行内 WidgetSpan 徽标、嵌套富文本。
"""
import os
import sys
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
sys.path.insert(0, str(root / "tmp" / rid / "B01"))
from dslkit import Doc, TextFit, minutes  # noqa: E402
import b01kit as K  # noqa: E402

OUT = root / "tmp" / rid / "B01" / "case-02"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1800
d = Doc(W, H, bg="#07070F", palette={"cyan": "#22D3EE", "amber": "#FBBF24",
                                      "green": "#34D399", "pink": "#F472B6",
                                      "violet": "#A78BFA", "red": "#FB7185"})
P = d.P
tf = TextFit()

DAYS = [
    dict(no="08.14", wk="周五", stage="主舞台 · 潮汐",
         head="无人电台", sub=["苔原", "玻璃海"],
         acts=["三十七度二", "夜航西飞", "铁与棉花", "长日将尽", "盐与铁",
               "海妖协议", "反重力少女", "南方群岛", "白噪音旅店的猫", "潮汐合唱团"]),
    dict(no="08.15", wk="周六", stage="主舞台 · 回声",
         head="热带失眠", sub=["灯塔少年", "慢速光"],
         acts=["雨季来临之前", "气体", "黑色柳丁", "十七吨", "岛屿信号", "月球背面",
               "西瓜船", "长夜", "回声舱", "沙丘邮局"]),
    dict(no="08.16", wk="周日", stage="主舞台 · 落日",
         head="落日车队", sub=["洋流", "折叠海"],
         acts=["海边的曼彻斯特乐队", "二十三点", "浮冰", "热带鱼", "无线电云",
               "落日大道", "玻璃缸", "潮汐力", "南十字", "晚安地球"]),
]

N_ACTS = sum(1 + len(x["sub"]) + len(x["acts"]) for x in DAYS)

# ---------- 背景 ----------
d.rect(0, 0, W, H, "#07070F")
K.radial_disc(d, 380, 60, 900, ["#0E7490", "#07070F"], radius="0.55")
K.radial_disc(d, -320, 1180, 900, ["#7C3AED", "#07070F"], radius="0.6")
# SWEEP 色轮太阳（主舞台隐喻）
K.sweep_disc(d, 860, 300, 250,
             ["#22D3EE", "#34D399", "#FBBF24", "#F472B6", "#A78BFA", "#22D3EE"],
             hole=0.0)
d.pos(610, 50, 500, 500, d.box(500, 500, color="#07070F44", radius=250))
# 斜切色带
K.rotated(d, -180, 470, 1500, 74, 6,
          d.box(1500, 74, color="#FBBF24"))
K.rotated(d, -180, 520, 1500, 10, -3, d.box(1500, 10, color="#22D3EE"))

# ---------- 顶部信息 ----------
d.pos(60, 46, 700, 26, d.box(700, 26, align="CENTER_LEFT",
                             inner=K.T("TIDAL FIELD FESTIVAL · 2026", d.font,
                                       color="#E2E8F0", fontSize=22,
                                       fontStyle="BOLD", letterSpacing="6")))
d.label(60, 80, 700, 24, "星海湾露天公园 · 三舞台 · 三日不重演", P["t1"], 20)
d.pos(60, 112, 640, 34, d.box(640, 34, align="CENTER_LEFT",
                              inner=K.T("第 9 届 · %d 组艺人 · 首演 14:30" % N_ACTS, d.font,
                                        color="#22D3EE", fontSize=24,
                                        fontStyle="BOLD",
                                        textShadow="3 3 0 #F472B699")))

# ---------- 主标题 ----------
K.stroke(d, 60, 168, 960, 200, "潮汐声场", 196, "#F1F5F9", sw=4)
d.pos(60, 372, 980, 96, d.box(980, 96, align="CENTER_LEFT",
                              inner=K.T("TIDAL FIELD", d.font, color="#F1F5F9",
                                        fontSize=86, fontStyle="BOLD",
                                        letterSpacing="-2",
                                        textShadow="6 7 0 #F472B6CC,-6 -5 0 #22D3EE99,"
                                                   "0 0 22 #FFFFFF44")))
d.pos(52, 458, 596, 56, d.box(596, 56, color="#07070FF2", radius=10))
d.pos(68, 466, 900, 40, d.box(900, 40, align="CENTER_LEFT",
                              inner=K.T("声 场 · 潮 汐 · 三 日", d.font,
                                        color="#FBBF24", fontSize=26,
                                        fontStyle="BOLD", letterSpacing="8")))

# ---------- 日期三卡（压在斜带上） ----------
for i, day in enumerate(DAYS):
    x = 60 + i * 330
    d.pos(x, 560, 300, 118, d.box(300, 118, color="#0D111D", radius=14,
                                  border="2 SOLID %s" % P["amber"],
                                  shadow="0 12 26 0 #000000CC NORMAL"))
    d.label(x + 20, 574, 200, 44, day["no"], P["t0"], 38, "BOLD")
    d.label(x + 20, 620, 200, 24, day["wk"], P["t2"], 19)
    d.label(x + 20, 648, 268, 24, day["stage"], P["amber"], 19, "BOLD")
    d.chip(x + 224, 584, 56, 30, "D%d" % (i + 1), "#06111F", P["cyan"], 18)

# ---------- 阵容 ----------
d.pos(60, 712, 960, 34, d.box(960, 34, align="CENTER_LEFT",
                              inner=K.T("LINEUP 阵容（虚构演示）", d.font,
                                        color="#F1F5F9", fontSize=24,
                                        fontStyle="BOLD", letterSpacing="3")))
d.line(60, 752, 1020, 752, 2, "#F1F5F933")
for i, day in enumerate(DAYS):
    x = 60 + i * 330
    d.label(x, 768, 300, 26, "DAY %d · %s" % (i + 1, day["no"]), P["cyan"], 20,
            "BOLD")
    K.stroke(d, x, 800, 300, 62, day["head"], 52, "#F1F5F9", sw=2, align="START")
    tf.check("c2-head-%d" % i, day["head"], 52, 300, 62)
    yy = 872
    for s in day["sub"]:
        d.label(x, yy, 300, 34, s, P["amber"], 28, "BOLD")
        yy += 38
    yy += 6
    for a in day["acts"]:
        d.label(x, yy, 300, 28, a, P["t1"], 21)
        tf.check("c2-act-%d" % i, a, 21, 300, 28)
        yy += 31
    if i < 3:
        d.line(x + 314, 768, x + 314, yy - 12, 1, "#F1F5F922")

# ---------- 场地示意 ----------
VY = 1296
d.pos(60, VY, 960, 164, d.box(960, 164, color="#0B1220", radius=16,
                              border="1 SOLID #22D3EE44"))
d.pos(84, VY + 12, 520, 26, d.box(520, 26, align="CENTER_LEFT",
                                  inner=K.T("场地示意 · 星海湾露天公园（虚构）",
                                            d.font, color="#22D3EE", fontSize=19,
                                            fontStyle="BOLD", letterSpacing="2")))
# 海面（线性渐变 + 落日倒影 + 浪线）
d.pos(648, VY + 44, 348, 104,
      d.box(348, 104, radius=14,
            grad='gradientType="LINEAR" gradientColors="#0E7490,#155E75,#164E63" '
                 'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"'))
K.radial_disc(d, 754, VY + 54, 64, ["#FBBF24", "#F472B600"], radius="0.5")
for i, yy in enumerate((VY + 74, VY + 90, VY + 106, VY + 122)):
    K.rotated(d, 664, yy, 316, 2, -1.5 + i * 1.2, d.box(316, 2, color="#E2E8F055"))
d.label(664, VY + 128, 316, 18, "潮汐湾 · 落日方向", "#BAE6FD", 14, align="END")
# 舞台与场地标注
STAGES = [("潮汐主舞台", 120, VY + 70, 18, P["amber"]),
          ("回声舞台", 300, VY + 86, 13, P["cyan"]),
          ("落日舞台", 452, VY + 66, 13, P["green"])]
for name, x, y, r, col in STAGES:
    d.pos(x - r - 6, y - r - 6, (r + 6) * 2, (r + 6) * 2,
          d.box((r + 6) * 2, (r + 6) * 2, radius=r + 6, border="2 SOLID %s" % col))
    d.dot(x - 4, y - 4, 8, col)
    d.label(x - 75, y + r + 8, 150, 20, name, "#E2E8F0", 15, "BOLD", align="CENTER")
    tf.check("c2-v-%s" % name, name, 15, 150, 20)
d.chip(74, VY + 124, 92, 24, "主入口", "#06111F", "#E2E8F0", 14)
d.chip(524, VY + 112, 76, 24, "露营区", "#06111F", "#34D399", 14)
d.line(596, VY + 46, 596, VY + 24, 2, "#F1F5F966")
d.label(584, VY + 10, 26, 16, "N", P["t2"], 13, align="CENTER")

# ---------- 票务与脚注 ----------
d.pos(60, 1492, 960, 118, d.box(960, 118, color="#121E38", radius=16,
                                 border="1 SOLID #22D3EE55"))
tiers = [("单日票", "¥ 480", "14:30 – 23:00"),
         ("三日通票", "¥ 1,180", "含露营位"),
         ("早鸟（已售罄）", "¥ 380", "补票通道 07.01 开放")]
for i, (a, b, c) in enumerate(tiers):
    x = 88 + i * 316
    d.label(x, 1512, 280, 24, a, P["t2"], 19)
    d.label(x, 1538, 280, 40, b, P["t0"], 32, "BOLD")
    d.label(x, 1580, 288, 24, c, P["t1"], 18)
    if i:
        d.line(x - 18, 1512, x - 18, 1590, 1, "#22D3EE33")
d.pos(60, 1628, 960, 30, d.box(960, 30, align="CENTER_LEFT",
                               inner=K.T("购票 tidal.example/fest（示例地址，非真实售票）",
                                         d.font, color="#22D3EE", fontSize=20)))
d.label(60, 1666, 960, 56,
        "潮汐声场为虚构演示品牌，艺人名、价格与日程均为编造内容，不代表任何真实活动或已部署项目。"
        "主办：星海湾文化演示 · 交通接驳 22:00–24:00 每 20 分钟一班。", P["t2"], 18)

dsl = d.dsl()
(OUT / "case02.snapshot").write_text(dsl, encoding="utf-8")
print("bytes", len(dsl), "· textfit", tf.n, "problems", tf.problems)
