"""件-02 巡检员单株档案卡（1080×2400，手持机户外强光高对比模式）。

内容任务：戴手套、单手持机、太阳直射下，巡检员要在一屏里读完档案、录入五项实测、
当场看到风险分是怎么算出来的，并得到可执行的下一步。
"强光模式"落在版面上：深底、白字、最小 18 px、行距放宽、控件加高。
"""
import datetime as dt
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "B05"))
import b05kit as B  # noqa: E402

W, H = 1080, 2400
WEIGHT = dict(tilt=0.30, cav=0.25, root=0.20, target=0.15, hist=0.10)
NAME = dict(tilt="倾斜角", cav="空洞比例", root="铺装隆起", target="暴露对象",
            hist="历史病害")


def build():
    st = B.data()
    f = st["featured"]["tree"]
    wo = json.load(open(ROOT / "tmp" / RID / "B05" / "research" / "orders.json",
                        encoding="utf-8"))
    order = [o for o in wo["orders"] if o["tree"] == f["id"]][0]
    series = st["featured"]["series"]
    mx = B.trees()
    # 倒伏半径：树高 + 6 m 安全余量（本产品的现场围挡规则）
    fall_r = round(f["height_m"] + 6.0, 1)
    days_since = (dt.date.fromisoformat(st["generated_at"][:10]) -
                  dt.date.fromisoformat(f["last_inspect"])).days

    d, tf = B.doc(W, H, ground="dark")
    MX, CW = 40, W - 80

    # ---- 状态栏 + 模式条 ----
    B.mono(d, tf, "sb", MX, 24, 200, 30, "10:05", 20, d.P["t0"])
    B.mono(d, tf, "sb2", W - MX - 220, 24, 220, 30, "离线缓存 · 41%", 17, d.P["t2"],
           align="END")
    d.rect(0, 64, W, 64, d.P["leaf"])
    B.tlab(d, tf, "mode", MX, 76, 520, 40, "强光模式 · 字号已放大一档", 22,
           "#FFFFFF", style="BOLD")
    B.chip(d, tf, "mode-off", W - MX - 168, 82, 168, 34, "回所联网同步 18:00",
           "#FFFFFF", "#00000040", size=15)

    # ---- 抬头：这棵树是谁 ----
    ny = 156
    B.mono(d, tf, "hd-id", MX, ny, 520, 54, f["id"], 38, d.P["t0"], style="BOLD")
    B.band_chip(d, tf, "hd-band", W - MX - 220, ny + 2, f["band"], w=220, h=48,
                size=20)
    B.tlab(d, tf, "hd-1", MX, ny + 62, CW, 32,
           "%s ｜ %s ｜ 种植于 %d 年 ｜ 责任巡检员 %s" %
           (f["species"], f["road"], f["planted"], f["inspector"]), 19, d.P["t1"])
    B.tlab(d, tf, "hd-2", MX, ny + 98, CW, 32,
           "上次巡检 %s ｜ 距今天 %d 天 ｜ 本路段在册 %d 棵" %
           (f["last_inspect"], days_since,
            sum(1 for t in mx["trees"] if t["road_code"] == f["road_code"])),
           19, d.P["t2"])

    # ---- 档案：静态四项 ----
    ny = 318
    ny = B.section(d, tf, "s1", MX, ny, CW, "①", "档案（不动的部分）", color=d.P["leaf"])
    cells = [("胸径", "%d" % f["dbh_cm"], "cm"), ("树高", "%.1f" % f["height_m"], "m"),
             ("冠幅", "%.1f" % f["crown_m"], "m"),
             ("树龄", "%d" % (int(st["generated_at"][:4]) - f["planted"]), "年")]
    cw = CW / 4.0
    for i, (lab, val, unit) in enumerate(cells):
        cx = MX + cw * i
        d.rect(cx, ny, cw - 12, 122, d.P["card"], radius=16,
               )
        B.tlab(d, tf, "c%d-l" % i, cx + 16, ny + 14, cw - 44, 26, lab, 16, d.P["t2"])
        B.num(d, tf, "c%d-v" % i, cx + 16, ny + 44, cw - 118, 52, val, 34, d.P["t0"])
        B.tlab(d, tf, "c%d-u" % i, cx + cw - 92, ny + 62, 70, 30, unit, 16, d.P["t2"])
    ny += 140

    # ---- 本次实测五项 + 加权 ----
    ny = B.section(d, tf, "s2", MX, ny, CW, "②", "本次实测五项（决定风险分）",
                   "数值来自左侧量测与照片判读；权重是全市统一口径，巡检员不可改")
    px, py, pw = B.card(d, tf, "meas", MX, ny, CW, 424)
    rows = [("倾斜角", "%.1f°" % f["tilt_deg"], "测斜仪 + 照片复核",
             f["subs"]["tilt"]),
            ("空洞比例", "%d%%" % f["cavity_pct"], "敲击 + 内窥镜",
             f["subs"]["cav"]),
            ("铺装隆起", "%d%%" % f["pavement_pct"], "根部区域硬化/开裂占比",
             f["subs"]["root"]),
            ("暴露对象", f["exposure_name"], "下游 12 m 内是什么",
             f["subs"]["target"]),
            ("历史病害", "%d" % f["disease_hist"], "三年内处置记录",
             f["subs"]["hist"])]
    yy = py + 6
    for i, (lab, val, how, sub) in enumerate(rows):
        key = ["tilt", "cav", "root", "target", "hist"][i]
        B.tlab(d, tf, "m%d-l" % i, px, yy, 170, 30, lab, 19, d.P["t0"])
        B.mono(d, tf, "m%d-v" % i, px + 176, yy, 190, 30, val, 21, d.P["amber"])
        B.tlab(d, tf, "m%d-h" % i, px + 372, yy + 2, 300, 30, how, 15, d.P["t2"])
        B.hbar(d, tf, "m%d-b" % i, px + 684, yy + 6, 118, 14, sub / 100.0,
               d.P["leaf"], bg="#22301F")
        B.mono(d, tf, "m%d-w" % i, px + pw - 108, yy, 108, 30,
               "%.0f ×%.2f" % (sub, WEIGHT[key]), 16, d.P["t1"], align="END")
        yy += 46
    d.rect(px, yy + 2, pw, 1, d.P["border"])
    B.tlab(d, tf, "m-sum-l", px, yy + 12, 320, 34,
           "加权合计 R = Σ(子分 × 权重)", 18, d.P["t1"])
    B.num(d, tf, "m-sum-v", px + pw - 190, yy + 6, 190, 46, "%d" % f["risk"], 40,
           d.P["rust"])
    B.tlab(d, tf, "m-thr", px, yy + 52, pw, 30,
           "阈值：≥70 立即处置 ｜ 55-69 限期 ｜ 40-54 观察 ｜ <40 正常", 16, d.P["t2"])
    ny += 440

    # ---- 倾斜示意：姿态 + 阈值标尺 + 近四次读数 ----
    ny = B.section(d, tf, "s3", MX, ny, CW, "③", "倾斜到底有多大",
                   "左：相对铅垂基线的实际姿态；右：把倾角放到 0-10° 标尺上看阈值")
    px, py, pw = B.card(d, tf, "ang", MX, ny, CW, 400)
    gx, gy = px + 132, py + 250                      # 树干基点
    d.rect(gx - 104, gy, 208, 4, d.P["line"])         # 地面
    d.line(gx, gy, gx, gy - 200, 2, d.P["t2"])        # 0° 铅垂基线
    B.tree_glyph(d, gx, gy, 176, 50, 14, tilt_deg=f["tilt_deg"],
                 crown=d.P["leaf"], trunk="#A97B4E", roots=True)
    B.tlab(d, tf, "ang-g", gx - 130, gy + 14, 260, 26,
           "铅垂基线 0°，实测 %.1f°" % f["tilt_deg"], 15, d.P["t2"], align="CENTER")
    rx, rw = px + 300, pw - 300
    B.tlab(d, tf, "g-t", rx, py + 4, 300, 28, "倾角阈值标尺（0-10°）", 17, d.P["t1"])
    by, bh = py + 44, 30
    for lo, hi, col in [(0, 4, d.P["grid"]), (4, 6, d.P["amber"]),
                        (6, 10, d.P["rust"])]:
        d.rect(rx + rw * lo / 10.0, by, rw * (hi - lo) / 10.0, bh, col)
    for v in (0, 2, 4, 6, 8, 10):
        d.rect(rx + rw * v / 10.0 - 1, by + bh, 2, 8, d.P["t2"])
        B.mono(d, tf, "g-tk%d" % v, rx + rw * v / 10.0 - 22, by + bh + 12, 44, 24,
               "%d" % v, 15, d.P["t2"], align="CENTER")
    mk = rx + rw * f["tilt_deg"] / 10.0
    d.line(mk, by - 12, mk, by + bh + 4, 4, d.P["t0"])
    B.mono(d, tf, "g-mark", mk - 70, by - 42, 140, 28, "实测 %.1f°" % f["tilt_deg"],
           16, d.P["t0"], align="CENTER")
    B.tlab(d, tf, "g-z6", rx + rw * 0.60, by + bh + 42, rw * 0.4, 26, "≥6° 立即处置参考",
           15, d.P["rust"])
    B.tlab(d, tf, "g-z4", rx + rw * 0.40, by + bh + 42, rw * 0.2, 26, "4-6° 加速关注",
           15, d.P["amber"])
    qy = by + bh + 76
    B.tlab(d, tf, "g-s", rx, qy, rw, 26, "近四次月检读数", 16, d.P["t1"])
    qy += 30
    for i, s in enumerate(series[-4:]):
        x = rx + i * (rw / 4.0)
        h = 78.0 * s["tilt_deg"] / 10.0
        col = d.P["rust"] if s["tilt_deg"] >= 6 else d.P["leaf"]
        d.rect(x + 8, qy + (78 - h), rw / 4.0 - 26, h, col, radius=4)
        B.mono(d, tf, "q-v%d" % i, x + 8, qy + (78 - h) - 26, rw / 4.0 - 26, 24,
               "%.1f°" % s["tilt_deg"], 15, d.P["t1"], align="CENTER")
        B.mono(d, tf, "q-m%d" % i, x + 8, qy + 84, rw / 4.0 - 26, 24, s["month"][2:],
               14, d.P["t2"], align="CENTER")
    B.tlab(d, tf, "ang-note", px, py + 300, pw, 56,
           "近四次读数：%.1f → %.1f → %.1f → %.1f°，月增速 %.2f°/30 天，超过 0.30 的加速阈值；"
           "连续两次加速即触发本屏的\"立即处置\"判定。" %
           (series[-4]["tilt_deg"], series[-3]["tilt_deg"], series[-2]["tilt_deg"],
            series[-1]["tilt_deg"], series[-1]["rate_deg_per_30d"]),
           16, d.P["t1"], lines=2, valign="TOP")
    ny += 416

    # ---- 现场结论与下一步 ----
    ny = B.section(d, tf, "s4", MX, ny, CW, "④", "现场结论与下一步")
    px, py, pw = B.card(d, tf, "concl", MX, ny, CW, 390,
                        title="结论：立即处置（R=%d）" % f["risk"],
                        sub="SLA %d 小时 ｜ 当前状态：%s ｜ 工单 %s" %
                            (order["sla_hours"], order["state"], order["wo"]))
    acts = [("拉起 %0.1f m 禁入半径" % fall_r, "以树干中心为圆心，倒伏方向加倍"),
            ("确认 %s 已到场" % order["crew"], "09:58 签到，正在布设围挡"),
            ("支撑加固 + 疏剪三成冠", "不砍；复核后转观察期"),
            ("48 h 内复测倾斜", "低于 5.0° 才能撤围")]
    yy = py + 10
    for i, (a, b_) in enumerate(acts):
        d.rect(px, yy, 8, 30, d.P["leaf"])
        B.tlab(d, tf, "a%d-a" % i, px + 22, yy, 430, 30, a, 19, d.P["t0"])
        B.tlab(d, tf, "a%d-b" % i, px + 470, yy + 3, pw - 482, 30, b_, 16, d.P["t2"])
        yy += 44
    d.rect(px, yy + 10, pw, 74, d.P["leaf"], radius=16)
    B.tlab(d, tf, "btn", px, yy + 24, pw, 44, "录入完成，同步到工单 " + order["wo"],
           24, "#FFFFFF", align="CENTER", style="BOLD")
    ny += 406

    # ---- 离线与同步：这些录入还没联网 ----
    ny = B.section(d, tf, "s5", MX, ny, CW, "⑤", "离线状态：点了同步也不会丢",
                   "树下没有信号；本地算分与服务器用同一份权重表（版本 v2026.09）")
    px, py, pw = B.card(d, tf, "off", MX, ny, CW, 200)
    items = [("五项实测与照片元数据", "已缓存 · 待同步", d.P["amber"]),
             ("现场照片 4 张 · 12.4 MB", "排队上传", d.P["amber"]),
             ("语音备注 1 条", "已转写为文字", d.P["leaf"]),
             ("工单 %s 服务器状态" % order["wo"], "已更新为「%s」" % order["state"],
              d.P["leaf"])]
    yy = py + 4
    for i, (a, b_, col) in enumerate(items):
        d.rect(px, yy + 9, 10, 10, col, radius=5)
        B.tlab(d, tf, "o%d-a" % i, px + 26, yy, 430, 28, a, 17, d.P["t1"])
        B.tlab(d, tf, "o%d-b" % i, px + 466, yy, pw - 466, 28, b_, 17, col, align="END")
        yy += 36
    ny += 200 + 16

    B.credit(d, tf, "foot", MX, ny, CW, [
        "演示数据：汀州市与「枝安」为虚构；五项实测值、权重与阈值由 b05data.py 固定种子",
        "生成，可复算。禁入半径 = 树高 + 6 m，是本产品自定的现场规则，不是国标。",
        "6° 参考线与 0.30°/30 天加速阈值同样是本产品的判定口径，来自题目设定的风险模型。",
        "本界面未做真实用户验证；户外强光模式的最小字号、控件高度为设计假设。"], size=15)
    return d, tf, dict(case="case-02", kind="巡检员档案卡（手持机，现场录入态）",
                       tree=f["id"], risk=f["risk"], wo=order["wo"])
