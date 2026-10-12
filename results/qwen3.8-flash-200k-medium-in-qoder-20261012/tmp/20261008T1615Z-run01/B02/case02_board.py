"""B02 case-02 会员卡正反面 1020x646（front + back 各一次真实渲染）。

设计任务：卡在柜台上被递来递去。正面 = 身份凭证（谁、哪一档、还能借几件、
什么时候到期）；背面 = 规则提示（五条 + 电话 + 安全课 + 馆址），
所以正面深色、信息少、字号大；背面浅色、行距紧、全是小字。
"""
import datetime
import os
import sys
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
for p in ("_suite/scripts", "B01", "B02"):
    sys.path.insert(0, str(root / "tmp" / rid / p))

from dslkit import TextFit  # noqa: E402
import b02kit as B  # noqa: E402

P = B.P
D = B.DATA
M = D["member"]
RU = D["brand"]["rules"]
MF = RU["member_fee"]
AL = D["active_loans"]
W, H = 1020, 646
OUT = root / "tmp" / rid / "B02" / "case-02"
OUT.mkdir(parents=True, exist_ok=True)
ver = os.environ.get("B02_VER", "v01")
TODAY = datetime.date.fromisoformat(RU["today"])
SINCE = datetime.date.fromisoformat(M["since"])
EXPIRE = datetime.date.fromisoformat(M["expires"])
TERM = (EXPIRE - SINCE).days
LEFT = (EXPIRE - TODAY).days


def front():
    tf = TextFit()
    d = B.paper_doc(W, H, dark=True, noise=13, seed=11)
    # ---- 品牌区 ----
    B.brand_mark(d, 96, 96, 40, bg=P["dark"])
    B.tlab(d, tf, "f-brand", 152, 60, 260, 56, D["brand"]["name"],
           40, d.P["t0"], "BOLD", lines=1)
    B.tlab(d, tf, "f-en", 154, 116, 360, 22, "WRENCH HOUSE · TOOL LIBRARY", 14,
           B.lighten(P["orange"], 0.34), "BOLD")
    B.tlab(d, tf, "f-type", 604, 66, 360, 26, "%s · %d 人共用" %
           (M["card"], M["household"]), 17, B.lighten(P["brass"], 0.30), "BOLD",
           align="END")
    B.tlab(d, tf, "f-type2", 604, 98, 360, 20, "MEMBER CARD", 12,
           d.P["t2"], None, align="END")
    d.rect(56, 152, 908, 1, d.P["line"])

    # ---- 会员号 / 姓名 ----
    B.tlab(d, tf, "f-no-k", 56, 176, 200, 18, "会员号", 12, d.P["t2"], None)
    B.tlab(d, tf, "f-no", 56, 196, 340, 52, M["id"], 42, d.P["t0"], "BOLD",
           features="tnum")
    B.tlab(d, tf, "f-name-k", 56, 262, 200, 18, "持卡人", 12, d.P["t2"], None)
    B.tlab(d, tf, "f-name", 56, 280, 200, 54, M["name"], 40, d.P["t0"], "BOLD")
    B.pill(d, 268, 292, 190, 34, "年卡 ¥%d" % M["fee"], P["brass"], 15, dark=True)
    B.tlab(d, tf, "f-safe", 56, 348, 420, 22, "Safety 101 已通过 · %s" %
           M["safety_101"].split(" ")[0], 15, B.lighten(P["green"], 0.30), "BOLD")

    # ---- 有效期（剩余比例，不是已过比例：快到期时一眼看出来）----
    B.tlab(d, tf, "f-term-k", 56, 402, 300, 18, "有效期", 12, d.P["t2"], None)
    B.tlab(d, tf, "f-term", 56, 420, 460, 30, "%s – %s" % (M["since"], M["expires"]),
           21, d.P["t1"], None, features="tnum")
    B.ruler(d, 56, 462, 300, LEFT / float(TERM), tone=P["brass"], h=12,
            label="剩 %d 天" % LEFT, lw=88, ls=16, dark=True)
    B.tlab(d, tf, "f-renew", 56, 494, 470, 22,
           "到期前可在馆内或小程序续期 · 逾期费 ¥%g/件·天" % RU["late_fee_per_day"],
           13, d.P["t2"], None)
    B.tlab(d, tf, "f-tag", 56, 538, 470, 26, D["brand"]["tagline"], 17,
           B.lighten(P["orange"], 0.30), "BOLD")

    # ---- 额度：3 个在借槽位 ----
    B.tlab(d, tf, "f-quota", 604, 176, 360, 30, "额度 %d / %d 件" %
           (len(AL), RU["max_active"]), 24, d.P["t0"], "BOLD", features="tnum")
    B.tlab(d, tf, "f-quota2", 604, 208, 360, 20, "同时在借已满 · 归还后可再借",
           13, B.lighten(P["red"], 0.26), "BOLD")
    for i, l in enumerate(AL):
        y = 238 + i * 62
        col = B.cat_color(l["cat"], dark=True)
        d.rect(604, y, 4, 48, col)
        B.tlab(d, tf, "f-slot%d" % i, 618, y + 2, 330, 26,
               "%s · %s" % (l["name"], l["tool"]), 17, d.P["t0"], "BOLD")
        st = ("逾期 %d 天 · 应计 ¥%g" % (l["overdue_days"], l["late_fee"])
              if l["overdue_days"] else "还剩 %d 天 · %s 应还" %
              (l["days_left"], B.date_md(l["due"])))
        B.tlab(d, tf, "f-slot%d-s" % i, 618, y + 28, 330, 20, st, 13,
               B.lighten(P["red"], 0.30) if l["overdue_days"] else d.P["t2"], None)
    B.tlab(d, tf, "f-show", 604, 434, 360, 24, "取还时出示本卡 · 卡面信息以馆内系统为准",
           13, d.P["t2"], None)
    B.stamp(d, 744, 478, 200, 56, "逾期 %d 天" % max(a["overdue_days"] for a in AL),
            P["red"], -8, 20, dark=True, tf=tf)
    B.footer(d, 56, H - 44, 908, "short", dark=True)
    return d, tf


def back():
    tf = TextFit()
    d = B.paper_doc(W, H, noise=13, seed=5)
    d.rect(0, 0, W, 62, P["ink"])
    B.tlab(d, tf, "b-head", 56, 18, 420, 30, "扳手屋 · 借阅规则", 20,
           B.lighten(P["white"], 0.9), "BOLD")
    B.tlab(d, tf, "b-head2", 560, 22, 404, 24, "%s · %s · 请阅读以下五条" %
           (M["id"], M["card"]), 14, B.lighten(P["brass"], 0.25), None,
           align="END", features="tnum")

    rules = [
        ("无押金，借出不另收费", "押金 ¥%d · 年卡含全部工具使用" % RU["deposit"]),
        ("借期 %d 天，可续借 %d 天" % (RU["loan_days"], RU["renew_days"]),
         "每件一个续借额度，到期前办理"),
        ("同时在借最多 %d 件" % RU["max_active"], "家庭卡 %d 人共用同一个额度"
         % M["household"]),
        ("逾期 ¥%g/件·天" % RU["late_fee_per_day"],
         "逾期满 %d 天暂停借出，归还没清前不能续借" % RU["suspend_days"]),
        (RU["repair_by"], "故障请带回馆内登记，不要自行拆解"),
    ]
    for i, (t1, t2) in enumerate(rules):
        y = 86 + i * 58
        B.hex_chip(d, 74, y + 16, 15, P["orange"], "%d" % (i + 1), size=12,
                   bg=P["paper"])
        B.tlab(d, tf, "b-r%d" % i, 104, y, 392, 26, t1, 19, P["ink"], "BOLD")
        B.tlab(d, tf, "b-r%d-s" % i, 104, y + 27, 392, 22, t2, 14, P["ink2"], None)
        if i < 4:
            d.rect(56, y + 52, 440, 1, d.P["line"])
    # 五条以外的两处硬信息，用小标题和规则区隔开
    B.section_head(d, 56, 372, 440, 3, "时间与取还", "望江驿为自助柜")
    B.tlab(d, tf, "b-return", 56, 416, 440, 24, "%s · 取还都在营业时间内"
           % RU["return_point"], 15, P["steel"], "BOLD")
    B.tlab(d, tf, "b-hours", 56, 442, 440, 22, "%s %s–%s（%s）" %
           (B.DATA["brand"]["hours"]["days"], B.DATA["brand"]["hours"]["open"],
            B.DATA["brand"]["hours"]["close"], B.DATA["brand"]["hours"]["closed_note"]),
           14, P["ink2"], None, features="tnum")

    rx, rw = 560, 404
    B.section_head(d, rx, 86, rw, 1, "联系与安全", "24h 电话")
    B.tlab(d, tf, "b-phone", rx, 130, rw, 34, B.DATA["brand"]["phone"], 26,
           P["ink"], "BOLD", features="tnum")
    B.tlab(d, tf, "b-phone2", rx, 168, rw, 22, "服务与紧急联系电话 · 登记手机 %s"
           % M["phone"], 14, P["ink2"], None, features="tnum")
    B.tlab(d, tf, "b-safe", rx, 200, rw, 24, "Safety 101 安全课 %d 分钟"
           % RU["safety_101_min"], 16, P["green"], "BOLD")
    B.tlab(d, tf, "b-safe2", rx, 228, rw, 22, "首次借电动/气动工具前必须完成 · 本人 %s"
           % M["safety_101"], 13, P["ink2"], None)

    B.section_head(d, rx, 268, rw, 2, "两个取还点", "同一张卡通用")
    for i, s in enumerate(B.DATA["brand"]["sites"]):
        B.tlab(d, tf, "b-site%d" % i, rx, 312 + i * 26, rw, 24, s, 15,
               P["ink"], None)
    B.tlab(d, tf, "b-prog-k", rx, 366, rw, 18, "常设活动", 12, P["ink3"], None)
    B.tlab(d, tf, "b-prog", rx, 386, rw, 44, " · ".join(B.DATA["brand"]["programs"]),
           14, P["ink2"], None, lines=2)

    d.rect(56, 486, 908, 1, d.P["line"])
    B.barcode(d, 56, 500, 380, 46, M["id"], P["ink"])
    B.tlab(d, tf, "b-code", 56, 550, 380, 20, "%s / %d / %dP" %
           (M["id"], MF["家庭年卡"], M["household"]), 12, P["ink3"], None,
           features="tnum")
    d.rect(460, 500, 1, 66, d.P["line"])
    B.tlab(d, tf, "b-term", 476, 500, 200, 20, "有效期", 12, P["ink3"], None)
    B.tlab(d, tf, "b-term2", 476, 518, 300, 26, "%s – %s" % (M["since"], M["expires"]),
           17, P["ink"], "BOLD", features="tnum")
    B.pill(d, 476, 548, 300, 26, "遗失请立即致电挂失冻结", P["steel"], 13)
    B.footer(d, 56, H - 40, 908, "short", note="虚构演示内容")
    return d, tf


for key, fn in (("case-02f", front), ("case-02b", back)):
    d, tf = fn()
    dsl = d.dsl()
    (OUT / ("%s-%s.snapshot" % (key, ver))).write_text(dsl, encoding="utf-8")
    print(key, len(dsl), "textfit:", tf.n, "problems:", len(tf.problems))
    for p in tf.problems[:10]:
        print("  !", p)
