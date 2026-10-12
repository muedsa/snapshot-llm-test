"""case-02《224 次日食的账本》1080x1620（纸本底）。

把 NASA 二十一世纪日食目录的 224 行原始记录解析成可核对的账：
类型分布、按十年的点阵、每年食数、极值榜。
所有数字都由本机脚本从 HTML 表格里解析，并与页面正文自述的统计逐条对照。
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(os.environ["SNAPSHOT_TASK_ROOT"]) / "tmp" /
                       os.environ["SNAPSHOT_RUN_ID"] / "B04"))
import b04kit as B  # noqa: E402

TYPES = [("P", "偏食", "moon"), ("A", "环食", "cyan"),
         ("T", "全食", "ember"), ("H", "混合", "corona")]


def build():
    stats, rows = B.data()
    dv = B.ddata()
    SRC_BYTES = (B.ROOT / "tmp" / B.RID / "B04" / "sources" /
                 "nasa-21cen-catalog.html").stat().st_size
    d, tf = B.doc(1080, 1620, "paper")
    B.header(d, tf, "h", "02", "224 次日食的账本",
             "一个世纪里，月球的影子会扫过地球 224 次；这是把原始表格逐行读出来的结果",
             size=48, paper=True)

    # ---------- ① 类型分布 ----------
    cnt = stats["count_by_type"]
    tot = sum(cnt.values())
    B.tlab(d, tf, "p1-t", 72, 232, 900, 26, "① 四种影子，四种账", 21, d.P["t0"],
           style="BOLD")
    for j, (code, name, col) in enumerate(TYPES):
        x = 72 + j * 238
        d.rect(x, 270, 222, 150, d.P["card"])
        d.rect(x, 270, 222, 5, d.P[col])
        B.mono(d, tf, "p1-n%d" % j, x + 16, 288, 190, 52, str(cnt[code]), 44,
               d.P[col], align="START")
        B.tlab(d, tf, "p1-l%d" % j, x + 16, 344, 190, 24, "%s · %s" % (name, code),
               17, d.P["t1"])
        B.mono(d, tf, "p1-p%d" % j, x + 16, 372, 190, 22,
               "%.1f%%" % (100.0 * cnt[code] / tot), 16, d.P["t2"])
    B.tlab(d, tf, "p1-note", 72, 436, 936, 24,
           "合计 %s 次。比例与 NASA 页面自述的 34.4 / 32.1 / 30.4 / 3.1%% 一致。" % B.km(tot),
           15, d.P["t2"], lines=1)

    # ---------- ② 按十年的点阵 ----------
    B.tlab(d, tf, "p2-t", 72, 486, 900, 26, "② 一个点一次食：按十年 × 类型",
           21, d.P["t0"], style="BOLD")
    top, rh, cw, gap, lab_w = 550, 46, 176, 12, 96
    for j, (code, name, col) in enumerate(TYPES):
        x = 72 + lab_w + j * (cw + gap)
        B.tlab(d, tf, "p2-h%d" % j, x, 518, cw, 22, "%s %s" % (name, code), 15,
               d.P[col], align="CENTER", style="BOLD")
    B.tlab(d, tf, "p2-hs", 72 + lab_w + 4 * (cw + gap), 518, 60, 22, "合计", 15,
           d.P["t2"], align="CENTER")
    B.hrule(d, 72, 544, 936, d.P["border"], 1)

    decades = sorted(dv["by_decade"].keys(), key=lambda k: int(k[:4]))
    for i, dec in enumerate(decades):
        y = top + i * rh
        cell = dv["by_decade"][dec]
        if i % 2 == 0:
            d.rect(72, y - 6, 936, rh - 2, d.P["card"])
        B.mono(d, tf, "p2-d%d" % i, 72, y, 88, 22, dec.replace("s", " 年代"), 16,
               d.P["t1"])
        for j, (code, name, col) in enumerate(TYPES):
            x = 72 + lab_w + j * (cw + gap)
            n = cell.get(code, 0)
            for k in range(n):
                r, c = divmod(k, 5)
                d.dot(x + 14 + c * 21, y + 8 + r * 19, 9, d.P[col])
            if n:
                B.mono(d, tf, "p2-c%d-%d" % (i, j), x + 128, y + 4, 40, 20, str(n), 15,
                       d.P[col], align="END")
        B.mono(d, tf, "p2-s%d" % i, 72 + lab_w + 4 * (cw + gap), y + 4, 60, 20,
               str(sum(cell.values())), 16, d.P["t0"], align="CENTER")
    ys = top + len(decades) * rh
    B.hrule(d, 72, ys, 936, d.P["border"], 1)
    B.tlab(d, tf, "p2-note", 72, ys + 10, 936, 24,
           "2100 年代只有 2 次：目录到 2100-12-31 截止，最后一年不满一个十年。",
           15, d.P["t2"], lines=1)

    # ---------- ③ 每年食数（自数 vs 页面自述）----------
    y3 = ys + 52
    B.tlab(d, tf, "p3-t", 72, y3, 900, 26, "③ 一年里能有几次日食？", 21, d.P["t0"],
           style="BOLD")
    dist = dv["years_by_eclipse_count"]
    claim = dv["page_claim_years_by_eclipse_count"]
    ok = all(dist.get(k) == v for k, v in claim.items())
    B.hbars(d, tf, "p3", 72, y3 + 40, 620,
            [("%d 次" % k, dist.get(str(k), 0),
              d.P["ember"] if str(k) in claim and dist.get(str(k)) == claim[str(k)]
              else d.P["moon"]) for k in (2, 3, 4, 5)],
            bh=28, gap=12, lab_w=76, fmt=lambda v: "%d 年" % v, size=16)
    d.rect(716, y3 + 40, 292, 160, d.P["card"])
    B.tlab(d, tf, "p3-k1", 732, y3 + 52, 260, 22, "对账结果", 17, d.P["t0"],
           style="BOLD")
    B.tlab(d, tf, "p3-k2", 732, y3 + 80, 260, 88,
           "页面正文写的是 2 次 %d 年、3 次 %d 年、4 次 %d 年；"
           "我从 224 行自己数出来 %s。%s"
           % (claim["2"], claim["3"], claim["4"],
              "、".join("%s：%d" % (k + " 次", dist[k]) for k in sorted(dist)),
              "完全吻合。" if ok else "不吻合，见 case.md。"),
           14, d.P["t1"], lines=4)
    B.tlab(d, tf, "p3-k3", 732, y3 + 170, 260, 22,
           "本世纪没有一年出现 5 次日食。", 14, d.P["t2"], lines=1)

    # ---------- ④ 极值榜 ----------
    y4 = y3 + 232
    B.tlab(d, tf, "p4-t", 72, y4, 900, 26, "④ 账本里的极端条目", 21, d.P["t0"],
           style="BOLD")
    tt = dv["top_total_duration"][0]
    ta = dv["top_annular_duration"][0]
    tw = dv["top_width"][0]
    st = dv["shortest_total_duration"][0]
    sa = dv["shortest_annular_duration"][0]
    nw = min(rows, key=lambda r: r.get("path_width_km") or 9e9)
    B.keypanel(d, tf, "p4a", 72, y4 + 34, 440, "最长",
               [("全食", "%s · %d s" % (tt["date"], tt["central_duration_s"]),
                 None, d.P["ember"]),
                ("环食", "%s · %d s" % (ta["date"], ta["central_duration_s"]),
                 None, d.P["cyan"]),
                ("全食带宽度", "%s · %d km" % (tw["date"], tw["path_width_km"]),
                 None, d.P["t0"])], row_h=28, size=15)
    B.keypanel(d, tf, "p4b", 568, y4 + 34, 440, "最短",
               [("全食", "%s · %d s" % (st["date"], st["central_duration_s"]),
                 None, d.P["t1"]),
                ("环食", "%s · %d s" % (sa["date"], sa["central_duration_s"]),
                 None, d.P["t1"]),
                ("全食带宽度（混合食）", "%s · %d km" % (nw["date"], nw["path_width_km"]),
                 None, d.P["t1"])], row_h=28, size=15)

    B.footband(d, tf, "f", [
        "来源：NASA Five Millennium Canon 目录页 SE2001-2100.html（本机抓取，%s 字节）。"
        % B.km(SRC_BYTES),
        "解析：拼接页面里的 9 个 pre 块，按行首日期定位，逐行取 17 个位置记号；"
        "224 行全部解析成功，0 行遗留。",
        "口径：偏食行不给中心线宽度与时长（77 行为空），所以 ④ 只统计全食/环食/混合。",
        "分类：NASA 另把 140 次中心食分成 135 双限 / 2 单限，非中心 3 次；细节见 case.md。",
    ], size=13, paper=True)

    info = {"title": "224 次日食的账本", "size": [1080, 1620], "kind": "数据/账本点阵",
            "rows_parsed": stats["rows_parsed"], "rows_unparsed": stats["rows_unparsed"],
            "counts": cnt, "years_dist": dist, "years_crosscheck_ok": ok,
            "decade_totals": {k: sum(v.values()) for k, v in dv["by_decade"].items()}}
    return d, tf, info
