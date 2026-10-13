"""B02 case-09 - 2026 第三季度公开数据报告 (1000x2000 长图).

Touchpoint: the quarterly transparency long-image that goes into the community group chat
and gets printed for the noticeboard. Residents and the funder should be able to check
every bar against the same monthly log the duty wall and the poster use: alert counts,
resident reports, tasks closed, response-time percentiles computed from the sorted log,
volunteer hours and where the money went.

Run:  python tmp/<run_id>/B02/case09_report.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "B02"))
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
import data  # noqa: E402
import tide  # noqa: E402
from bkit import MONO, SANS, tw  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B02"
W, H = 1000, 1780
M = 56
Q = data.QLOG
MONTHS = data.MONTHS


def pctl(vals, k):
    s2 = sorted(vals)
    return s2[min(len(s2) - 1, int(round(k * (len(s2) - 1))))]


def build():
    s = tide.sheet(W, H, min_font=20)
    tide.assert_contrast([(tide.INK, tide.PAPER, "ink"), (tide.PAPER, tide.INK, "reverse")],
                         4.5)
    q_reports = sum(Q["resident_reports"])
    q_tasks = sum(Q["tasks_done"])
    q_alerts = sum(Q["alerts_sent"])
    q_hours = sum(Q["hours_volunteer"])
    q_drills = sum(Q["drills"])
    spend = Q["spend_wan"]
    total_spend = sum(spend.values())
    # response percentiles recomputed from the monthly figures, not copied from the label
    p50_q = pctl(Q["response_min_p50"], 0.5)
    p90_worst = max(Q["response_min_p90"])
    assert p50_q == 9.2 and q_tasks == 163 and q_reports == 191

    tide.lockup(s, M, 44, 56, tide.INK, latin=False)
    s.text("doc", "季度公开数据 · 第 3 季", W - M, 56, 24, tide.INK_3, align="right",
           font=MONO)
    s.text("title", "这一季度，水位线做了什么", M, 132, 40, tide.INK, bold=True)
    s.text("sub", "2026-07-01 至 2026-09-30 · 江北街道 6 个社区 · 数据随任务板与小程序一致",
           M, 190, 22, tide.INK_2)
    y = 232

    # ---- KPI tiles
    kpis = [(f"{q_alerts}", "条预警推送", "含升级 3 次"),
            (f"{q_reports}", "件居民上报", f"核实率 {100 - 6}%"),
            (f"{q_tasks}", "项任务完成", f"中位 {p50_q} 分"),
            (f"{q_hours}", "小时志愿工时", f"注册 {data.REGISTERED} 人")]
    cw = (W - 2 * M - 3 * 16) / 4
    for i, (big, lab, note) in enumerate(kpis):
        x = M + i * (cw + 16)
        s.rect(x, y, cw, 132, tide.INK, radius=12)
        s.text("kb", big, x + 16, y + 16, 44, tide.PAPER, bold=True, font=MONO)
        s.text("kl", lab, x + 16, y + 76, 22, tide.PAPER)
        s.text("kn", note, x + 16, y + 102, 20, "#9FB2BE")
        assert tw(big, 44, True) <= cw - 32 and tw(lab, 22) <= cw - 32 and tw(note, 20) <= cw - 32, lab
    y += 168

    # ---- monthly bars: reports vs tasks
    s.text("h1", "上报与完成的任务（按月）", M, y, 26, tide.INK, bold=True)
    y += 40
    bx, bw, bh = M, W - 2 * M, 210
    s.line(bx, y + bh, bx + bw, y + bh, tide.INK, 2)
    mx = max(max(Q["resident_reports"]), max(Q["tasks_done"]))
    grp = (bw - 40) / 3
    for i, mn in enumerate(MONTHS):
        cx = bx + 20 + i * grp
        for j, (key, col, lab) in enumerate((("resident_reports", tide.CYAN, "上报"),
                                             ("tasks_done", tide.SAFE, "完成"))):
            v = Q[key][i]
            h = bh * v / mx
            x = cx + 26 + j * (grp / 2 - 30)
            s.rect(x, y + bh - h, grp / 2 - 46, h, col, radius=4)
            s.text("v", f"{v}", x + (grp / 2 - 46) / 2, y + bh - h - 26, 22, tide.INK,
                   align="center", bold=True, font=MONO)
        s.text("mn", mn, cx + grp / 2 - 23, y + bh + 10, 22, tide.INK_2)
    tide.legend_row(s, bx, y + bh + 46, [(tide.CYAN, "居民上报"), (tide.SAFE, "完成任务")],
                    size=20)
    y += bh + 96

    # ---- response time
    s.text("h2", "响应时长：从上报到有人到场（分钟）", M, y, 26, tide.INK, bold=True)
    y += 46
    s.line(bx, y + 150, bx + bw, y + 150, tide.INK, 2)
    mx2 = max(Q["response_min_p90"])
    for i, mn in enumerate(MONTHS):
        cx = bx + 60 + i * (bw - 120) / 2
        for j, (key, col, lab) in enumerate((("response_min_p50", tide.SAFE, "中位"),
                                             ("response_min_p90", tide.SAND, "90 分位"))):
            h = 150 * Q[key][i] / mx2
            s.rect(cx - 24 + j * 30, y + 150 - h, 24, h, col, radius=4)
            s.text("rv", f"{Q[key][i]:.1f}", cx - 24 + j * 30 + 12,
                   max(y + 2, y + 150 - h - 26), 20, tide.INK_2, align="center",
                   font=MONO)
        s.text("mn2", mn, cx + 6, y + 160, 22, tide.INK_2, align="center")
    s.text("nt", f"最慢的 90 分位从 26.0 分降到 19.2 分；单点最慢 {p90_worst:.1f} 分。",
           M, y + 196, 20, tide.INK_3)
    y += 244

    # ---- spend
    s.text("h3", "钱花在哪（万元）", M, y, 26, tide.INK, bold=True)
    y += 40
    x = M
    for i, (k, v) in enumerate(spend.items()):
        w = (W - 2 * M) * v / total_spend
        col = [tide.INK, tide.CYAN, tide.SAFE, tide.SAND][i]
        s.rect(x, y, w - 3, 56, col, radius=4)
        s.text("sk", f"{v:.1f}", x + 10, y + 16, 22, tide.PAPER if i == 0 else tide.INK,
               bold=True, font=MONO)
        s.text("sn", k, x, y + 66, 20, tide.INK_2)
        assert tw(k, 20) <= w + 20, k
        x += w
    s.text("st", f"合计 {total_spend:.1f} 万元 · 来自街道专项与社区共建资金（示例数字）",
           M, y + 96, 20, tide.INK_3)
    y += 140

    # ---- three changes + next quarter
    s.line(M, y, W - M, y, tide.LINE, 1.5)
    y += 22
    s.text("h4", "这一季度真正改变的三件事", M, y, 26, tide.INK, bold=True)
    y += 42
    for i, t in enumerate([
            f"南门桥下加了第二道挡水板，去年这里淹到台阶，今年 {MONTHS[1]} 的 31 条预警里没有一处进水报告。",
            "上报回执从「不知道有没有人看」变成 5 分钟内自动派单，中位到场时间缩短到 9.2 分钟。",
            f"演练 {q_drills} 次，其中 2 次夜间演练；集合点夜间开放状态第一次在小程序里实时显示。"]):
        end = s.para("cg", f"{i + 1}．{t}", M, y, 22, tide.INK_2, width=W - 2 * M)
        y = end + 10
    y += 14
    s.rect(M, y, W - 2 * M, 116, "#EAF1EC", radius=12)
    s.text("nh", "下一季度要做", M + 20, y + 14, 24, tide.SAFE, bold=True)
    for i, t in enumerate(["把 4 台过期药品包与 3 件缺失反光背心补齐（见物资柜封条清单）；",
                           "在 L-04 俱乐部增加夜间开放值班，覆盖东侧 2 个社区。"]):
        s.text("nl", "· " + t, M + 20, y + 50 + i * 28, 22, tide.INK_2)
    y += 140
    tide.footer(s, M, y, W - 2 * M,
                ["口径：预警＝推送到已绑定门牌的消息条数；上报＝居民提交且经核实的事件；",
                 "响应时长＝上报时间到第一位志愿者到达现场。全部为虚构演示数据。"],
                size=20)
    assert y <= H - 20, y
    return s, {"kpis": {"alerts": q_alerts, "reports": q_reports, "tasks": q_tasks,
                        "hours": q_hours, "drills": q_drills},
               "monthly": {k: Q[k] for k in ("alerts_sent", "resident_reports", "tasks_done",
                                             "response_min_p50", "response_min_p90",
                                             "hours_volunteer")},
               "spend_wan": spend, "spend_total": round(total_spend, 1),
               "p50_quarter": p50_q, "p90_worst": p90_worst,
               "used_height": round(y, 1)}


if __name__ == "__main__":
    s, d = build()
    (TMP / "case09.snapshot").write_text(s.dsl(), encoding="utf-8")
    (TMP / "case09-data.json").write_text(json.dumps(d, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    print(json.dumps(s.audit(margin=40), ensure_ascii=False))
