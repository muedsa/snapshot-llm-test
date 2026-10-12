"""件-01 市民随手拍报修（1080×2340，手机全屏界面）。

内容任务：让一个路过的人用 20 秒把"这棵树歪了"变成一条能被处置的记录，
并且当场看见系统已经认出是哪棵树、它已经在办——避免重复派单。
数据全部来自 tmp/<run>/B05/research/（b05data.py 生成），件内不手填数字。
"""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "B05"))
import b05kit as B  # noqa: E402

W, H = 1080, 2340


def build():
    st = B.data()
    f = st["featured"]["tree"]
    import json
    wo = json.load(open(ROOT / "tmp" / RID / "B05" / "research" / "orders.json",
                        encoding="utf-8"))
    order = [o for o in wo["orders"] if o["tree"] == f["id"]][0]

    d, tf = B.doc(W, H, ground="light")
    MX, CW = 44, W - 88

    # ---- 状态栏 ----
    B.mono(d, tf, "sb-time", MX, 26, 120, 30, "09:20", 20, d.P["t0"])
    for i, hh in enumerate([10, 14, 18, 22]):
        d.rect(W - 200 + i * 12, 46 - hh, 8, hh, d.P["t1"], radius=2)
    B.outline_rect(d, W - 140, 28, 44, 20, d.P["t1"], radius=5)
    d.rect(W - 137, 31, 26, 14, d.P["leaf"], radius=3)
    B.mono(d, tf, "sb-bat", W - 86, 28, 46, 22, "64%", 15, d.P["t2"])
    d.rect(0, 66, W, 1, d.P["border"])

    # ---- 顶部导航 ----
    d.line(MX + 16, 104, MX + 4, 116, 4, d.P["t0"])
    d.line(MX + 4, 116, MX + 16, 128, 4, d.P["t0"])
    B.tlab(d, tf, "hd-t", MX + 36, 92, 470, 46, "报告一棵树的问题", 30, d.P["t0"],
           style="BOLD")
    B.chip(d, tf, "hd-a", W - MX - 150, 96, 150, 44, "我的报修 3", d.P["leaf"],
           d.P["card2"], size=16)

    # ---- 取景框：现场画面（DSL 绘制，非照片）----
    cy0 = 168
    d.rect(MX, cy0, CW, 372, "#DCE6EA", radius=22)
    d.rect(MX, cy0 + 250, CW, 122, "#CFC6B4")            # 人行道
    d.rect(MX, cy0 + 250, CW, 4, "#B7AD98")
    for i, bw in enumerate([120, 86, 150, 104]):          # 街对面建筑
        d.rect(MX + 20 + sum([120, 86, 150, 104][:i]) + i * 14, cy0 + 90, bw, 160,
               "#C3CBD2")
    # 公交站：雨棚 + 两根立柱 + 长椅 + 站牌
    d.rect(MX + CW - 176, cy0 + 150, 132, 12, "#8E9AA2", radius=4)
    d.rect(MX + CW - 172, cy0 + 162, 8, 88, "#7C878F")
    d.rect(MX + CW - 52, cy0 + 162, 8, 88, "#7C878F")
    d.rect(MX + CW - 160, cy0 + 214, 108, 8, "#9AA6AE", radius=3)
    d.rect(MX + CW - 206, cy0 + 176, 22, 74, "#6E7A82", radius=3)
    B.tree_glyph(d, MX + 430, cy0 + 268, 150, 62, 15, tilt_deg=f["tilt_deg"],
                 crown="#4E7A4A", trunk="#6B4A2A", roots=False)
    B.disc(d, MX + 430 + 22, cy0 + 268 - 150 - 18, 30, "#5E8E58")
    d.rect(MX + 372, cy0 + 262, 118, 8, "#B7AD98", radius=3)   # 根系顶起的路面
    d.line(MX + 400, cy0 + 262, MX + 424, cy0 + 270, 2, "#9C927E")
    d.line(MX + 440, cy0 + 262, MX + 458, cy0 + 271, 2, "#9C927E")
    # 取景角标（四条 L 形白角，标明识别框范围）
    rx0, ry0, rx1, ry1 = MX + 330, cy0 + 62, MX + 592, cy0 + 282
    for cx, cyp, sx, sy in [(rx0, ry0, 1, 1), (rx1, ry0, -1, 1),
                            (rx0, ry1, 1, -1), (rx1, ry1, -1, -1)]:
        d.rect(cx if sx > 0 else cx - 40, cyp if sy > 0 else cyp - 5, 40, 5, "#FFFDF8")
        d.rect(cx if sx > 0 else cx - 5, cyp if sy > 0 else cyp - 40, 5, 40, "#FFFDF8")
    B.outline_rect(d, rx0, ry0, rx1 - rx0, ry1 - ry0, "#FFFDF8", radius=14, thick=3)
    B.chip(d, tf, "cam-flag", MX + 20, cy0 + 306, 300, 44,
           "现场照片 · 已压缩 1.8 MB", "#FFFDF8", "#00000073", size=15)

    # ---- 自动匹配到的档案 ----
    ny = 566
    px, py, pw = B.card(d, tf, "match", MX, ny, CW, 268,
                        title="系统已认出这棵树", sub="依据：拍摄定位 + 树干粗度 + 树种")
    B.mono(d, tf, "match-id", px, py + 4, 300, 40, f["id"], 26, d.P["leaf"],
           style="BOLD")
    B.chip(d, tf, "match-band", px + pw - 190, py, 190, 40, f["band"], "#FFFFFF",
           B.BAND_COLOR[f["band"]], size=17)
    B.tlab(d, tf, "match-1", px, py + 56, pw, 30,
           "%s ｜ %s ｜ 胸径 %d cm ｜ 上次巡检 %s" %
           (f["species"], f["road"], f["dbh_cm"], f["last_inspect"]), 18, d.P["t1"])
    B.tlab(d, tf, "match-2", px, py + 92, pw, 30,
           "档案里的实测倾斜 %0.1f°，风险分 %d（%s 开单）" %
           (f["tilt_deg"], f["risk"], f["inspector"] + " " + f["last_inspect"]),
           18, d.P["t1"])
    d.rect(px, py + 128, pw, 1, d.P["border"])
    B.tlab(d, tf, "match-3", px, py + 138, pw, 30,
           "所以这次不用重复排队：你的照片会并入下面这条工单", 17, d.P["t2"])

    # ---- 现象多选 ----
    ny = 862
    ny = B.section(d, tf, "sec-a", MX, ny, CW, "①", "你看到了什么",
                   "可多选；选中项会写进巡检员的复核单")
    tags = [("树体倾斜", True), ("断枝垂落", False), ("树洞/空洞", True),
            ("根部路面隆起", True), ("压到线路", False), ("树皮剥落", False)]
    tx, ty = MX, ny
    for i, (t_, on) in enumerate(tags):
        wch = 46 + len(t_) * 22
        if tx + wch > MX + CW:
            tx, ty = MX, ty + 60
        B.chip(d, tf, "tag%d" % i, tx, ty, wch, 48, t_,
               "#FFFFFF" if on else d.P["t1"], d.P["leaf"] if on else d.P["card2"],
               size=17)
        if on:
            d.rect(tx + wch - 16, ty + 16, 8, 8, "#FFFDF8", radius=4)
        tx += wch + 16
    ny = ty + 84

    # ---- 位置 + 照片 ----
    ny = B.section(d, tf, "sec-b", MX, ny, CW, "②", "位置与照片",
                   "定位精度 8 m；照片最多 4 张，第 1 张用于识别树干")
    px, py, pw = B.card(d, tf, "pos", MX, ny, CW, 150)
    d.rect(px, py, 118, 108, "#E4EBE6", radius=12)
    for i in range(3):
        d.rect(px + 14, py + 16 + i * 30, 90, 3, "#CBD8CE")
    for i in range(3):
        d.rect(px + 16 + i * 34, py + 10, 3, 88, "#CBD8CE")
    B.disc(d, px + 74, py + 46, 9, d.P["rust"])
    B.disc(d, px + 74, py + 46, 4, "#FFFDF8")
    B.tlab(d, tf, "pos-1", px + 140, py + 6, pw - 150, 34,
           "建设路 126 号门前，公交站东侧 12 m", 20, d.P["t0"])
    B.mono(d, tf, "pos-2", px + 140, py + 44, pw - 150, 28,
           "26.1184° N  119.2976° E  ±8 m", 16, d.P["t2"])
    B.tlab(d, tf, "pos-3", px + 140, py + 76, pw - 150, 28,
           "在档案里对应：TZ-JS-0417（同一路段间距 0.9 m）", 16, d.P["leaf"])
    ny += 168
    for i in range(3):
        bx = MX + i * 200
        B.panel(d, bx, ny, 184, 132, ["#DCE6EA", "#CFC6B4", "#C3CBD2"][i],
                radius=14, border="1 SOLID " + d.P["border"])
        B.tree_glyph(d, bx + 92, ny + 104, 56, 24, 7,
                     tilt_deg=[6.8, 0.0, 2.2][i], crown="#4E7A4A", trunk="#6B4A2A")
        B.mono(d, tf, "th%d" % i, bx, ny + 136, 184, 24,
               ["IMG_4471", "IMG_4472", "IMG_4473"][i], 14, d.P["t2"], align="CENTER")
    B.chip(d, tf, "th-add", MX + 600, ny, 184, 132, "＋ 加一张", d.P["t2"],
           d.P["card2"], size=18, radius=14)
    ny += 176

    # ---- 补充说明 ----
    ny = B.section(d, tf, "sec-c", MX, ny, CW, "③", "补一句话（可选）")
    px, py, pw = B.card(d, tf, "txt", MX, ny, CW, 132)
    B.tlab(d, tf, "txt-v", px, py + 8, pw, 92,
           "每天早上候车的人站在这棵树底下，风一大树影晃得很厉害。", 20, d.P["t0"],
           lines=2, valign="TOP")
    B.mono(d, tf, "txt-n", px + pw - 120, py + 76, 120, 26, "26 / 200", 15,
           d.P["t2"], align="END")
    ny += 140

    # ---- 联系方式 + 提交 ----
    B.field(d, tf, "fld-cb", MX, ny, CW, "回访方式（只在需要确认现场时联系）",
            "手机尾号 7731", h=78, hint="不填也能提交；系统只在工作日 9:00-18:00 联系一次")
    ny += 142
    d.rect(MX, ny, CW, 92, d.P["leaf"], radius=20)
    B.tlab(d, tf, "sub-t", MX, ny + 14, CW, 40, "提交并关注这棵树", 26, "#FFFFFF",
           align="CENTER", style="BOLD")
    B.tlab(d, tf, "sub-s", MX, ny + 56, CW, 26,
           "提交后 24 小时内应有巡检员到场复核（当前 SLA：%d 小时）" % order["sla_hours"],
           16, "#EAF3EC", align="CENTER")
    ny += 100

    # ---- 合并提示 ----
    px, py, pw = B.card(d, tf, "mrg", MX, ny, CW, 236,
                        title="已并入现有工单 " + order["wo"],
                        sub="这棵树今晨 %s 由 %s 开单，现状态：%s" %
                            (order["opened"][11:16], f["inspector"], order["state"]))
    flow = wo["flow"]
    idx = flow.index(order["state"])
    B.hbar(d, tf, "mrg-bar", px, py + 40, pw, 12, (idx + 1) / float(len(flow)),
           d.P["leaf"])
    for i, s_ in enumerate(flow):
        cx = px + pw * (i + 0.5) / len(flow)
        d.rect(cx - 1, py + 34, 2, 24, "#FFFDF8")
        B.tlab(d, tf, "mrg-f%d" % i, cx - pw / len(flow) / 2 + 2, py + 62,
               pw / len(flow) - 4, 24, s_, 13,
               d.P["leaf"] if i <= idx else d.P["t2"], align="CENTER")
    B.tlab(d, tf, "mrg-1", px, py + 92, pw, 30,
           "你的 3 张照片与 2 个现象已附到工单，无需二次派单；进度会同步给你",
           17, d.P["t1"], lines=2, valign="TOP")
    ny += 250

    # ---- 底部导航 ----
    B.tabbar(d, tf, "tab", 0, H - 236, W,
             [("报修", "tree"), ("进度", "list"), ("附近", "map"), ("我的", "me")],
             active=0)
    B.credit(d, tf, "foot", MX, H - 118, CW, [
        "演示数据：汀州市为虚构城市，「枝安」为虚构产品，树种/坐标/工单号与所有数字均来自",
        "本仓库 b05data.py（固定种子 20261011，可复算）。现场画面由 DSL 绘制，未嵌入任何照片。",
        "界面元素的作用都在本件 case.md 里逐条说明；未做真实用户验证。"], size=14)
    return d, tf, dict(case="case-01", kind="市民报修（手机，未提交态）",
                       tree=f["id"], wo=order["wo"])
