"""件-04 高危树处置单（1240×1754，A4 竖版打印，已派单态）。

内容任务：把"谁负责、做什么、什么时候做完、怎么证明做完了"落在一张能签字、
能三联留存、能贴在现场围挡上的纸面上。打印件没有交互，所以每一栏都要能自解释。
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "B05"))
import b05kit as B  # noqa: E402

W, H = 1240, 1754
MX = 70
CW = W - 2 * MX
WEIGHT = dict(tilt=0.30, cav=0.25, root=0.20, target=0.15, hist=0.10)
NAME = dict(tilt="树干倾斜", cav="主干空洞", root="根系铺装", target="暴露对象",
            hist="历史病害")
HOW = dict(tilt="测斜仪 + 照片复核", cav="敲击 + 内窥镜", root="根部硬化/开裂占比",
           target="现场量距 12 m", hist="三年内处置记录")
KEYS = ("tilt", "cav", "root", "target", "hist")


def build():
    st = B.data()
    f = st["featured"]["tree"]
    wo = json.load(open(ROOT / "tmp" / RID / "B05" / "research" / "orders.json",
                        encoding="utf-8"))
    order = [o for o in wo["orders"] if o["tree"] == f["id"]][0]
    fall_r = round(f["height_m"] + 6.0, 1)

    d, tf = B.doc(W, H, ground="light")
    # ---- 页眉 ----
    B.tlab(d, tf, "hd-org", MX, 62, 700, 30, "汀州市园林绿化中心 · 行道树养护科", 20,
           d.P["t2"], font=B.SERIF)
    B.tlab(d, tf, "hd-t", MX, 96, 800, 62, "行道树隐患处置单", 46, d.P["t0"],
           style="BOLD", font=B.SERIF)
    B.num(d, tf, "hd-wo", W - MX - 330, 66, 330, 40, order["wo"], 30, d.P["t0"])
    B.chip(d, tf, "hd-state", W - MX - 330, 116, 330, 46,
           "状态：%s ｜ 限 24 小时内完成" % order["state"], "#FFFFFF", B.RUST, size=18)
    d.rect(MX, 172, CW, 4, B.RUST)
    d.rect(MX, 182, CW, 1, d.P["line"])

    # ---- 标的树 ----
    B.tlab(d, tf, "tr-lab", MX, 200, 130, 30, "处置对象", 19, d.P["t2"])
    B.num(d, tf, "tr-id", MX + 132, 194, 420, 44, f["id"], 34, d.P["t0"], align="START")
    B.band_chip(d, tf, "tr-band", MX + 560, 196, f["band"], w=180, h=42, size=19)
    B.tlab(d, tf, "tr-sub", MX + 760, 202, CW - 760, 34,
           "风险分 R = %d（阈值 ≥70）" % f["risk"], 19, d.P["t1"], align="END")
    meta = [("路段 / 位置", "%s 126 号门前" % f["road"]),
            ("树种 / 栽植年", "%s ｜ %d 年" % (f["species"], f["planted"])),
            ("胸径 / 树高 / 冠幅", "%d cm ｜ %.1f m ｜ %.1f m" %
             (f["dbh_cm"], f["height_m"], f["crown_m"])),
            ("下游暴露对象", "%s（12 m 内）" % f["exposure_name"]),
            ("开单时间", order["opened"].replace("T", " ") + " ｜ %s" % f["inspector"]),
            ("作业班组", "%s ｜ 现场负责人待签到" % order["crew"]),
            ("上次巡检", "%s ｜ 巡检员 %s" % (f["last_inspect"], f["inspector"])),
            ("关联上报", "1 件市民报修，已并入本单")]
    for i, (k, v) in enumerate(meta):
        x = MX + (i % 2) * (CW / 2.0)
        y = 254 + (i // 2) * 46
        d.rect(x, y + 34, CW / 2 - 24, 1, d.P["line"])
        B.tlab(d, tf, "mt%dl" % i, x, y, 190, 28, k, 17, d.P["t2"])
        B.tlab(d, tf, "mt%dv" % i, x + 196, y, CW / 2 - 220, 28, v, 18, d.P["t0"])

    # ---- 一、判定依据 ----
    y = 452
    B.tlab(d, tf, "s1", MX, y, 700, 34, "一、现场判定依据（实测值决定风险分）", 22,
           d.P["t0"], style="BOLD", font=B.SERIF)
    cols = [("判定项", 200, "START"), ("实测值", 210, "START"),
            ("子分", 90, "END"), ("权重", 90, "END"),
            ("加权", 90, "END"), ("量测方式", CW - 680, "START")]
    rows = [[NAME[k], MEAS_val(f, k), "%.1f" % f["subs"][k], "×%.2f" % WEIGHT[k],
             "%.1f" % (f["subs"][k] * WEIGHT[k]), HOW[k]] for k in KEYS]
    y2 = B.coltable(d, tf, "t1", MX, y + 42, CW, cols, rows, row_h=38, head_h=36,
                    size=19, head_size=17)
    d.rect(MX, y2, CW, 2, d.P["t1"])
    B.tlab(d, tf, "t1-sum", MX, y2 + 8, 700, 34,
           "R = Σ(子分 × 权重) = " + " + ".join(
               "%.1f" % (f["subs"][k] * WEIGHT[k]) for k in KEYS), 18, d.P["t1"],
           font=B.MONO)
    B.num(d, tf, "t1-r", W - MX - 260, y2 + 2, 260, 44, "R = %d" % f["risk"], 32,
          B.RUST)

    # ---- 二、处置措施 ----
    y = y2 + 66
    B.tlab(d, tf, "s2", MX, y, 800, 34, "二、处置措施（完成一项勾一项，未勾项不得归档）",
           22, d.P["t0"], style="BOLD", font=B.SERIF)
    acts = [("设置禁入区并硬质围挡", "%.1f m 半径（树高 %.1f + 余量 6）" %
             (fall_r, f["height_m"]), "到场即做", True),
            ("支撑加固（三脚钢撑）", "迎风侧为主撑，垫木不伤皮", "4 小时内", True),
            ("疏剪冠幅三成", "先疏内膛，不截主枝", "6 小时内", False),
            ("处理隆起铺装，留根系生长带", "开口 1.8 m × 1.2 m，覆木片", "48 小时内",
             False),
            ("取消下游停车位、移候车线", "报交警与公交公司会签", "本次同步", False)]
    yy = y + 42
    for i, (a, b_, due, done) in enumerate(acts):
        B.outline_rect(d, MX, yy + 4, 26, 26, d.P["t1"], thick=2)
        if done:
            B.tlab(d, tf, "ck%d-x" % i, MX, yy - 2, 26, 34, "✓", 24, B.RUST,
                   align="CENTER")
        B.tlab(d, tf, "ck%d-a" % i, MX + 44, yy, 380, 30, a, 19,
               d.P["t2"] if done else d.P["t0"])
        B.tlab(d, tf, "ck%d-b" % i, MX + 430, yy + 3, 400, 28, b_, 17, d.P["t2"])
        B.tlab(d, tf, "ck%d-c" % i, W - MX - 150, yy, 150, 28, due, 17, d.P["t1"],
               align="END")
        d.rect(MX, yy + 36, CW, 1, d.P["line"])
        yy += 42

    # ---- 三、平面示意 ｜ 四、时间线 ----
    y = yy + 20
    B.tlab(d, tf, "s3", MX, y, 520, 34, "三、作业范围平面示意", 22, d.P["t0"],
           style="BOLD", font=B.SERIF)
    B.tlab(d, tf, "s4", MX + 560, y, 480, 34, "四、时间线与签认", 22, d.P["t0"],
           style="BOLD", font=B.SERIF)
    dy = y + 46
    pw = 520
    d.rect(MX, dy + 70, pw, 74, "#E9E2D4")             # 车行道
    d.rect(MX, dy + 70, pw, 2, d.P["line"])
    d.rect(MX, dy + 142, pw, 2, d.P["line"])
    for i in range(4):
        d.rect(MX + 16 + i * 132, dy + 105, 72, 3, "#FFFDF8")
    d.rect(MX, dy + 144, pw, 30, "#F7F3EA")            # 人行道
    d.rect(MX, dy + 174, pw, 2, d.P["line"])
    cx, cy, r = MX + 180, dy + 159, 90
    B.disc(d, cx - 4, cy - 4, 8, B.BARK)
    d.line(cx, cy, cx + r, cy, 2, B.RUST)
    B.disc_outline(d, cx, cy, r, 3, B.RUST)
    B.mono(d, tf, "pl-r", cx + 12, cy - 30, 150, 26, "%.1f m" % fall_r, 17, B.RUST)
    B.tlab(d, tf, "pl-tree", cx - 176, cy - 60, 170, 26, f["id"], 16, d.P["t0"],
           align="END")
    d.line(cx - 176, cy - 47, cx - 30, cy - 12, 1, d.P["t2"])
    d.rect(cx + 150, dy + 112, 96, 28, "#CFC7B6")      # 停车位
    B.tlab(d, tf, "pl-b2", cx + 150, dy + 114, 96, 24, "停车位", 15, "#4A4436",
           align="CENTER")
    d.rect(cx + 150, dy + 150, 96, 22, "#CFC7B6")      # 公交站
    B.tlab(d, tf, "pl-b1", cx + 150, dy + 150, 96, 22, "公交站", 15, "#4A4436",
           align="CENTER")
    B.tlab(d, tf, "pl-road", MX + 6, dy + 40, 300, 26, "建设路（双向两车道）", 15,
           d.P["t2"])
    for x, lab in [(MX + 300, "0"), (MX + 322, "5"), (MX + 344, "10 m")]:
        d.rect(x, dy + 214, 2, 14, d.P["t0"])
        B.mono(d, tf, "pl-sc%s" % lab, x - 12, dy + 232, 66, 24, lab, 15, d.P["t2"])
    d.rect(MX + 300, dy + 220, 44, 3, d.P["t0"])
    d.line(MX + 470, dy + 232, MX + 470, dy + 198, 3, d.P["t0"])
    d.line(MX + 470, dy + 198, MX + 462, dy + 212, 3, d.P["t0"])
    d.line(MX + 470, dy + 198, MX + 478, dy + 212, 3, d.P["t0"])
    B.mono(d, tf, "pl-n", MX + 484, dy + 204, 40, 26, "N", 17, d.P["t0"])
    B.tlab(d, tf, "pl-note", MX, dy + 264, pw, 26, "按档案坐标绘制，比例 1 像素 ≈ 0.22 m",
           15, d.P["t2"])

    steps = [("10-11 08:20", "开单", "巡检员 %s 现场判定 R=%d" % (f["inspector"],
                                                                 f["risk"]), True),
             ("10-11 09:20", "报修并入", "1 件市民上报，不重复派单", True),
             ("10-11 09:58", "班组签到", "%s 到场" % order["crew"], True),
             ("10-11 12:00", "围挡 + 支撑", "本单前两项勾销", False),
             ("10-11 15:00", "值班复核", "核对照片与量具编号", False),
             ("10-13 前", "48 h 复测", "倾斜 < 5.0° 方可撤围", False)]
    ty = dy
    for i, (t, name, note, done) in enumerate(steps):
        col = B.RUST if done else d.P["t2"]
        if done:
            B.disc(d, MX + 572, ty + 12, 7, B.RUST)
        else:
            B.disc_outline(d, MX + 572, ty + 12, 7, 2, d.P["t2"])
        if i < 5:
            d.line(MX + 572, ty + 20, MX + 572, ty + 48, 2, d.P["line"])
        B.mono(d, tf, "ts%dt" % i, MX + 592, ty, 150, 26, t, 16, col)
        B.tlab(d, tf, "ts%dn" % i, MX + 750, ty, 170, 26, name, 18, d.P["t0"])
        B.tlab(d, tf, "ts%dp" % i, MX + 592, ty + 24, CW - 604, 22, note, 15, d.P["t2"])
        ty += 48

    # ---- 五、三联签认 ----
    y = dy + 302
    B.tlab(d, tf, "s5", MX, y, 800, 34, "五、签认（一式三联：班组 / 巡检员 / 值班室）",
           22, d.P["t0"], style="BOLD", font=B.SERIF)
    sigs = [("现场作业人", order["crew"]), ("巡检员复核", f["inspector"]),
            ("值班科长", "待签")]
    for i, (role, who) in enumerate(sigs):
        x = MX + i * (CW / 3.0)
        B.outline_rect(d, x, y + 42, CW / 3 - 16, 112, d.P["line"], thick=1)
        B.tlab(d, tf, "sg%dr" % i, x + 14, y + 52, CW / 3 - 44, 26, role, 16, d.P["t2"])
        B.tlab(d, tf, "sg%dn" % i, x + 14, y + 80, CW / 3 - 44, 28, "签字：" + who,
               18, d.P["t1"])
        B.tlab(d, tf, "sg%dh" % i, x + 14, y + 112, CW / 3 - 44, 26, "日期：", 17,
               d.P["t1"])
        d.rect(x + 86, y + 136, CW / 3 - 116, 1, d.P["line"])

    B.credit(d, tf, "foot", MX, y + 182, CW, [
        "演示单据：汀州市与「枝安」为虚构，树号 / 工单号 / 坐标 / 时间与全部数字均由",
        "b05data.py（固定种子 %d）生成，不对应任何真实市政系统、单位或人员。" % st["seed"],
        "「禁入半径 = 树高 + 6 m」「48 h 复测、倾斜 < 5.0° 撤围」是本产品自定的现场规则，",
        "不是国家标准；复印或拍照留存时请确认本页四角页边未被裁切。"], size=15)
    return d, tf, dict(case="case-04", kind="高危树处置单（A4 打印，已派单态）",
                       tree=f["id"], wo=order["wo"], risk=f["risk"],
                       fall_radius_m=fall_r)


def MEAS_val(f, k):
    return dict(tilt="%.1f°" % f["tilt_deg"], cav="%d %%" % f["cavity_pct"],
                root="%d %%" % f["pavement_pct"], target=f["exposure_name"],
                hist="%d 分" % f["disease_hist"])[k]
