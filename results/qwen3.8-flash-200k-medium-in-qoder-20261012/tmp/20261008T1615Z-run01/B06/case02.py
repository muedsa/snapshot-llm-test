"""件-02「末班车还赶得上吗」1080×2160 手机竖屏。

原始口径：站内告示"末班 23:41"——一个孤立的时刻。
换算：把"要几点到家"倒推成六段时间条，得到最迟动身时刻与缓冲。
行动：现在几点、还差几分钟、哪两种情况这张卡算不出来。

数值全部来自 research/demo.json（b06data.py，固定种子）。城市、线路与全部时长均为
虚构演示值；本件不声称知道任何真实运营时刻表。
"""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
for _p in (ROOT / "tmp" / RID / "_suite" / "scripts", ROOT / "tmp" / RID / "B06"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import b06kit as K  # noqa: E402

W, H = 1080, 2160
NOW = "23:07"          # 手机状态栏时间，也是本件的判断基准


def m24(s):
    hh, mm = s.split(":")
    return int(hh) * 60 + int(mm)


def hm(v):
    v = int(round(v)) % 1440
    return "%02d:%02d" % (v // 60, v % 60)


def build():
    d, tf = K.doc(W, H, ground="dark")
    P = d.P
    c = K.data()["cases"]["case02"]
    last = m24(c["last_train"])
    must_leave = m24(c["must_leave_now"])
    platform = m24(c["must_reach_platform"])
    now = m24(NOW)
    remain = must_leave - now

    # ---------- 手机外框 ----------
    iy = K.phone(d, tf, "ph", 40, 40, 1000, 1962, title="赶车倒推", time=NOW)
    K.appbar(d, tf, "ab", 60, iy, 960, "末班车还赶得上吗",
             sub="从「几点到家」倒推，而不是从「末班 23:41」正推")
    y = iy + 116

    # ---------- ① 原始口径 ----------
    px, pw = 60, 960
    x1, cy1, w1 = K.card(d, tf, "c1", px, y, pw, 286, "① 告示只给了一个时刻",
                         "站台上你能看到的全部信息")
    K.mono(d, tf, "c1-big", x1, cy1, 300, 72, c["last_train"], 58, P["amber"])
    K.tlab(d, tf, "c1-u", x1 + 12, cy1 + 74, 300, 26, "开往城西 · 只此一班", 15, P["t2"])
    K.tlab(d, tf, "c1-q1", x1 + 360, cy1 + 6, 560, 28,
           "可我今晚必须 00:35 前到家——", 18, P["t1"])
    K.tlab(d, tf, "c1-q2", x1 + 360, cy1 + 40, 560, 28,
           "这班上车以后到底来不来得及？", 18, P["t1"])
    K.note_band(d, tf, "c1-n", x1 + 360, cy1 + 78, 560,
                ["告示不含：换乘走行、二线车程、出站步行、闸机排队。",
                 "这四项加起来，比末班时刻更能决定赶不赶得上。"], size=14)
    assert cy1 + 78 + 76 <= y + 286 - 22
    y += 286 + 18

    # ---------- ② 倒推六段 ----------
    x2, cy2, w2 = K.card(d, tf, "c2", px, y, pw, 524, "② 换算：把这一小时摊成六段",
                         sub="从上往下＝从动身到到家")
    rows = [
        ("动身", must_leave, c["walk_in"], "走到本站", "walk"),
        ("上站台", platform, c["buffer"], "闸机与排队缓冲", "wait"),
        ("发车", last, 26, "一线乘车 6 站", "ride"),
        ("到换乘站", last + 26, 5, "换乘走行", "walk"),
        ("二线发车", last + 31, 14, "二线乘车", "ride"),
        ("出闸", last + 45, 9, "出站步行到家", "walk"),
    ]
    COL = {"walk": P["teal"], "ride": P["gold"], "wait": P["rust"]}
    scale = 470.0 / 26.0            # px / min，最长一段 26 min 铺满
    ry = cy2 + 6
    for i, (lab, t0, dur, name, kind) in enumerate(rows):
        col = COL[kind]
        K.mono(d, tf, "c2-t%d" % i, x2, ry, 92, 30, hm(t0), 21, P["t0"])
        K.hbar(d, tf, "c2-b%d" % i, x2 + 104, ry + 4, 470, 26, dur / 26.0, col,
               bg=P["grid"])
        K.mono(d, tf, "c2-d%d" % i, x2 + 586, ry, 66, 30, "%d min" % dur, 15,
               P["t1"], align="END")
        K.tlab(d, tf, "c2-n%d" % i, x2 + 664, ry, 296, 30, "%s·%s" % (lab, name),
               15, P["t1"])
        ry += 46
    # 合计与"告示只说了一格"的对比
    ry += 6
    d.line(x2, ry, x2 + w2, ry, 2, P["border"])
    ry += 14
    span = rows[5][1] + rows[5][2] - must_leave
    K.tlab(d, tf, "c2-sum", x2, ry, 640, 30,
           "从动身到到家共 %d min（含缓冲）＝那一个时刻之后的全部路程" % span,
           16, P["t0"])
    K.mono(d, tf, "c2-sum2", x2 + 660, ry, 300, 30, "到家 %s" % c["home_at"], 16,
           P["teal"], align="END")
    ry += 34
    K.tlab(d, tf, "c2-note", x2, ry, w2, 26,
           "跨了零点：%s 到家已是次日，卡上按 24 h 盘回绕显示" % c["home_at"], 14,
           P["t2"])
    # 可调参数条：这六个数是这张卡的输入
    ry += 34
    K.tlab(d, tf, "c2-p0", x2, ry, 300, 26, "这六段是我填的输入：", 14, P["t2"])
    pxs = x2 + 236
    for i, (lab, _t, dur, _n, kind) in enumerate(rows):
        wch = 96
        K.chip(d, tf, "c2-c%d" % i, pxs + i * (wch + 8), ry - 4, wch, 38,
               "%s %d" % (lab[:2], dur), P["t1"], P["card2"],
               border="1 SOLID " + P["border"], size=14)
    assert ry + 40 <= y + 524 - 22, ry
    y += 524 + 18

    # ---------- ③ 结论 ----------
    x3, cy3, w3 = K.card(d, tf, "c3", px, y, pw, 292, "③ 结论：最迟什么时候动身",
                         sub="现在 %s，看这一屏就够" % NOW)
    K.mono(d, tf, "c3-big", x3, cy3, 340, 84, hm(must_leave), 66, P["leaf"])
    K.tlab(d, tf, "c3-lab", x3 + 12, cy3 + 86, 320, 28, "最迟动身时刻", 16, P["t2"])
    K.tlab(d, tf, "c3-r1", x3 + 380, cy3 + 4, 560, 30,
           "现在 %s → 还有 %d 分钟" % (NOW, remain), 20, P["t0"])
    window = must_leave - m24(c["check_at"])
    K.hbar(d, tf, "c3-bar", x3 + 380, cy3 + 44, 560, 26,
           max(0.0, remain) / float(window),
           P["leaf"] if remain > 0 else P["rust"], bg=P["grid"])
    K.tlab(d, tf, "c3-r2", x3 + 380, cy3 + 82, 560, 28,
           "绿色满格＝%s 起的 %d min 决策窗" % (c["check_at"], window), 15, P["t2"])
    K.tlab(d, tf, "c3-r3", x3, cy3 + 128, w3, 30,
           "到 %s 还没进闸机：那 %d min 缓冲已经用掉，再冲闸机没有意义"
           % (hm(platform), c["buffer"]), 15, P["t1"])
    K.tlab(d, tf, "c3-r4", x3, cy3 + 160, w3, 30,
           "错过 %s：这班没了，卡上算不出下一班（见 ④）" % hm(last), 15, P["t1"])
    y += 292 + 18

    # ---------- ④ 三种情况 ----------
    x4, cy4, w4 = K.card(d, tf, "c4", px, y, pw, 372, "④ 三种情况，只有第一种算得出",
                         sub="把「能算」和「要现场看」分开写")
    cases = [
        ("现在 %s，行李少" % NOW, "赶：%s 前动身，%s 上站台" % (hm(must_leave), hm(platform)),
         P["leaf"], "本卡按六段输入算得"),
        ("%s 之后才到站厅" % hm(must_leave), "别冲闸机：缓冲只有 %d min，"
         "少一段就可能卡在换乘走行上" % c["buffer"], P["amber"], "本卡能给风险，不能给决定"),
        ("末班已开走", "本卡算不出下一班：是否有加班车／夜班公交，"
         "以站内当日公告为准", P["rust"], "本卡不含该信息，不编造"),
    ]
    ry = cy4
    for i, (cond, act, col, kind) in enumerate(cases):
        d.rect(x4, ry, 6, 74, col, radius=3)
        K.tlab(d, tf, "c4-a%d" % i, x4 + 22, ry + 2, 300, 30, cond, 17, P["t0"])
        K.tlab(d, tf, "c4-b%d" % i, x4 + 340, ry + 2, 580, 34, act, 15, P["t1"],
               lines=2, valign="TOP")
        K.tlab(d, tf, "c4-c%d" % i, x4 + 340, ry + 46, 580, 24, kind, 13, P["t2"])
        ry += 86
    assert ry <= y + 372 - 22, ry
    y += 372 + 18

    # ---------- ⑤ 口径与限制 ----------
    nb = K.note_band(d, tf, "c5", px, y, pw, [
        "「缓冲 %d min」是我给的保守值，不含临时限流、末端限乘与末班加班车；"
        "各段时长为虚构演示值，不是任何城市真实运营数据。" % c["buffer"],
        "跨零点显示：24 h 盘回绕后 %s 属于次日，卡上不做日期切换提示以外的处理。"
        % c["home_at"],
        "本卡不替你决定赶不赶：它只把「末班 23:41」这一个数换算成你能执行的时刻。",
    ], size=14)
    assert nb <= 40 + 1962 - 40, nb

    K.credit(d, tf, "credit", 60, 2040, 960, [
        "数据：tmp/%s/B06/research/demo.json（b06data.py，seed=%s）｜"
        "汀州市（虚构）｜条形长度＝分钟数，比例尺 470 px = 26 min。" % (RID, K.data()["seed"]),
    ], size=12)
    info = {"case": "02", "kind": "everyday-info-reinvented", "canvas": [W, H],
            "last_train": c["last_train"], "must_leave": hm(must_leave),
            "now": NOW, "remain_min": remain, "home_at": c["home_at"],
            "segments": [r[2] for r in rows], "total_min": span,
            "total_min_note": "含最后 9 min 出站步行；v04 之前的 build-log 记的是 63（漏末段），"
                              "该历史记录未改写，此处为元数据修正，画面无变化"}
    return d, tf, info
