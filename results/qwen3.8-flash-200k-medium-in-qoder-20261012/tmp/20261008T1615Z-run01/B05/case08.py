"""件-08 社区认养与遮荫收益卡（1080×1620，手机长图 / 树下张贴，长期态）。

内容任务：让认养人看懂"我认的这棵树给了我什么、我要做什么、别人做得怎么样"。
这一件和其他九件不同：它面对的是不关心风险分的普通居民，且会被贴在树下长期看，
所以只承诺**算得出来**的好处，并把"认养不改变处置结论"写在明处。
高度从计划的 1440 调到 1620：五块内容按各自文字实际行数排完后 1440 装不下
（第一版渲染出来三块内容溢出卡片、底部互相压字），第二版 1540 仍有 ① 两块
的末行压在卡片下边框上。改画布比压字号或删证据更诚实。
"""
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "B05"))
import b05kit as B  # noqa: E402

W, H = 1080, 1620
MX = 40
CW = W - 2 * MX
GAP = 12          # 卡片间距


def build():
    st = B.data()
    f = st["featured"]["tree"]
    wo = json.load(open(ROOT / "tmp" / RID / "B05" / "research" / "orders.json",
                        encoding="utf-8"))
    order = [o for o in wo["orders"] if o["tree"] == f["id"]][0]
    rad = f["crown_m"] / 2.0
    shade = math.pi * rad * rad                    # 树冠正投影面积
    rows = st["adoption"]
    ok = [r for r in rows if r["households"] >= 0]
    bad = [r for r in rows if r["households"] < 0]
    agg = {k: sum(r[k] for r in ok) for k in ("trees", "adopted", "households",
                                             "events")}
    rate = 100.0 * agg["adopted"] / agg["trees"]
    lj = [r for r in rows if r["street"] == "临江街道"][0]   # 建设路所在街道

    d, tf = B.doc(W, H, ground="light")
    # ---- 头部 ----
    B.tlab(d, tf, "h-t", MX, 34, 620, 46, "这棵树我认养了", 32, d.P["t0"],
           style="BOLD")
    B.tlab(d, tf, "h-s", MX, 86, 700, 26, "汀州市「枝安」社区认养 · 建设路示范段", 16,
           d.P["t2"])
    B.chip(d, tf, "h-c", W - MX - 220, 40, 220, 44, "认养中 · 第 6 个月", "#FFFFFF",
           B.LEAF, size=16)

    # ---- ① 树的基本档案 ----
    y1, h1 = 148, 250
    px, py, pw = B.card(d, tf, "a", MX, y1, CW, h1, "① 你认养的这棵树",
                        "档案号与实测尺寸来自巡检记录，不是估算")
    B.disc(d, px + 62, py + 52, 38, "#EAF1E7")
    B.tree_glyph(d, px + 62, py + 104, 82, 28, 8, tilt_deg=f["tilt_deg"],
                 crown=B.LEAF, trunk="#8A6440")
    B.mono(d, tf, "a-id", px + 4, py + 110, 116, 20, f["id"], 14, d.P["t0"],
           align="CENTER")
    facts = [("树种", "%s" % f["species"]), ("胸径", "%d cm" % f["dbh_cm"]),
             ("树高", "%.1f m" % f["height_m"]),
             ("冠幅（东西向）", "%.1f m" % f["crown_m"]),
             ("位置", "%s 126 号门前" % f["road"]),
             ("认养生效", "2026-04-12")]
    cellw = (pw - 150) / 3.0
    for i, (k, v) in enumerate(facts):
        cx = px + 150 + (i % 3) * cellw
        cy = py + 4 + (i // 3) * 52
        B.tlab(d, tf, "ak%d" % i, cx, cy, cellw - 12, 24, k, 15, d.P["t2"])
        B.tlab(d, tf, "av%d" % i, cx, cy + 22, cellw - 12, 26, v, 17, d.P["t0"])
    B.tlab(d, tf, "a-n", px + 150, py + 112, pw - 150, 26,
           "联名认养：6 号楼 12 户 ｜ 上次专业巡检 %s（%s）" % (f["last_inspect"],
                                                        f["inspector"]), 15, d.P["t2"])

    # ---- ② 算得出来的好处 ----
    y2, h2 = y1 + h1 + GAP, 345
    px, py, pw = B.card(d, tf, "b", MX, y2, CW, h2, "② 它给你的好处（只写算得出的）",
                        "遮荫面积＝树冠正投影，按圆面积公式；其余说明见下")
    B.num(d, tf, "b-n", px, py + 2, 260, 72, "%.1f" % shade, 60, B.LEAF,
          align="START")
    B.tlab(d, tf, "b-u", px + 140, py + 34, 200, 34, "m² 树荫", 20, d.P["t1"])
    B.chip(d, tf, "b-cmp", px + pw - 330, py + 12, 330, 52,
           "≈ 一套两居室的室内面积", "#FFFFFF", B.LEAF, size=17)
    B.tlab(d, tf, "b-f", px, py + 86, pw, 26,
           "R = 冠幅 ÷ 2 = %.2f m ｜ S = πR² = %.1f m²" % (rad, shade), 16, d.P["t2"],
           font=B.MONO)
    B.tlab(d, tf, "b-2", px, py + 118, pw, 28,
           "正午时这一整片落在树冠下，等车的人和停在路边的车都在里面。", 17,
           d.P["t1"])
    B.note_band(d, tf, "b-n", px, py + 152, pw, [
        "这张卡没有写降温几度、年固碳几公斤——那要本地实测才有意义。",
        "能确定的是下游暴露对象：树冠外 12 m 内是快速公交站候车区与 3 个路内停车位"
        "（见件-06 现场图）。"], size=15)

    # ---- ③ 双方承诺 ----
    y3, h3 = y2 + h2 + GAP, 296
    px, py, pw = B.card(d, tf, "c", MX, y3, CW, h3, "③ 双方各要做什么",
                        "认养是分工，不是把养护责任转嫁给居民")
    half = (pw - 24) / 2.0
    mine = ["干旱周（连续 7 天无雨）早上浇 2 桶水",
            "每季度绕树看一次，拍 1 张照片上传",
            "发现树皮开裂、根部隆起、明显歪斜就报修",
            "不在树干钉钉子、不缠灯串、不往根部倒污水"]
    ours = ["每 90 天内一次专业巡检并公开记录",
            "修剪、施肥、病虫害与加固全部由养护队负责",
            "R≥70 时 24 h 内到场处置，处置前在牌上告知",
            "树被移除时 30 天内贴补种计划，同路段优先"]
    for c, (title, lst, col) in enumerate([("你（认养人）", mine, B.AMBER),
                                           ("我们（养护队）", ours, B.LEAF)]):
        x = px + c * (half + 24)
        B.tlab(d, tf, "c-t%d" % c, x, py, half, 28, title, 18, col, style="BOLD")
        for i, s in enumerate(lst):
            y = py + 36 + i * 30
            B.outline_rect(d, x, y + 2, 20, 20, d.P["border"], radius=4, thick=2)
            if c == 1 and i < 2:
                B.tlab(d, tf, "c-k%d%d" % (c, i), x, y - 2, 20, 26, "✓", 17, col,
                       align="CENTER")
            B.tlab(d, tf, "c-i%d-%d" % (c, i), x + 28, y, half - 28, 26, s, 15,
                   d.P["t1"])
    B.tlab(d, tf, "c-w", px, py + 156, pw, 28,
           "一句实话：认养不改变这棵树的处置结论。它现在风险分 %d（立即处置），"
           "该加固就加固，该移除就移除。" % f["risk"], 16, B.RUST)

    # ---- ④ 别人认了多少 ----
    y4, h4 = y3 + h3 + GAP, 252
    px, py, pw = B.card(d, tf, "e4", MX, y4, CW, h4, "④ 这条街上、这座城市认了多少",
                        "口径：只统计可核的 5 个街道，异常行见下方红字")
    stats = [("%d 棵" % lj["adopted"], "临江街道已认养（在册 %s 棵）" % B.fmt(lj["trees"])),
             ("%d 户" % lj["households"], "临江街道认养户数"),
             ("%.1f %%" % rate, "全城可核 5 个街道的认养率")]
    seg = pw / 3.0
    for i, (v, k) in enumerate(stats):
        x = px + i * seg
        B.num(d, tf, "e4-n%d" % i, x, py, seg - 20, 40, v, 32, B.LEAF, align="START")
        B.tlab(d, tf, "e4-k%d" % i, x, py + 44, seg - 20, 26, k, 15, d.P["t2"],
               lines=2, valign="TOP")
    B.tlab(d, tf, "e4-w", px, py + 84, pw, 26,
           "全城认养树合计 %s 棵、%d 户、%d 次活动。" % (B.fmt(agg["adopted"]),
                                                 agg["households"], agg["events"]),
           16, d.P["t1"])
    B.tlab(d, tf, "e4-b", px, py + 112, pw, 26,
           "岩前街道的认养户数在系统里是 %d 户，这在现实中不可能，已退回核对；"
           "该街道不计入上面的合计（详见件-10）。" % bad[0]["households"], 15,
           B.RUST)

    # ---- ⑤ 这一年它身上发生了什么 ----
    y5, h5 = y4 + h4 + GAP, 214
    px, py, pw = B.card(d, tf, "t", MX, y5, CW, h5, "⑤ 这一年，它身上发生了什么",
                        "从挂牌到开单，每一步都有记录可查；末点是到场后 48 h 的复测窗口")
    B.timeline(d, tf, "tl", px + 62, py + 4, pw - 124, [
        ("2026-04-12", "认养生效", "6 号楼 12 户联名挂牌"),
        ("2026-09-28", "季度巡检", "倾斜 %.1f°、空洞 %d %%" % (f["tilt_deg"],
                                                         f["cavity_pct"])),
        ("10-11 08:20", "判级开单", "R=%d 立即处置 %s" % (f["risk"], order["wo"])),
        ("10-11 09:58", "班组到场", "%s 进场围挡加固" % order["crew"]),
        ("10-13 09:58", "复测决定", "连续两次 < 5.0° 才撤围")], dot=11, lab_h=28)

    B.credit(d, tf, "foot", MX, y5 + h5 + GAP, CW, [
        "演示卡：汀州市、建设路、树号与 6 号楼 12 户均虚构，由 b05data.py（固定种子 %d）生成。"
        % st["seed"],
        "认养期限、浇水次数、90 天巡检与 30 天补种承诺是产品自定条款，不是地方规定；"
        "本卡未做真实用户验证，也没有张贴到真实树上。"], size=13)
    return d, tf, dict(case="case-08", kind="社区认养与遮荫收益卡（手机/张贴）",
                       tree=f["id"], shade_m2=round(shade, 1),
                       adopted=agg["adopted"], trees=agg["trees"],
                       rate_pct=round(rate, 1), anomaly_rows=len(bad))
