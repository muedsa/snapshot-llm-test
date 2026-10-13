"""A24 - three views of one schedule: 1920x1080 board, 1200x1600 brief, 720x1280 card.

All three read schedule.json written by plan.py, so a time, a team or a dependency can
never disagree between them. Text is wrapped by measured width and placed with a greedy
anti-collision pass; the build reports every overlap, overflow and sub-floor font size so
nothing ships that the layout check has not seen.

Run:  python tmp/<run_id>/A24/make.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
sys.path.insert(0, str(ROOT / "tmp" / RUN / "A24"))
from snap import (C, Container, Node, Positioned, Snapshot, Stack,  # noqa: E402
                  num)

TMP = ROOT / "tmp" / RUN / "A24"
SANS, MONO = "Noto Sans CJK SC", "Noto Sans Mono CJK SC"
CJK_EM, LATIN_EM, MONO_EM, LINE_H = 1.0, 0.62, 0.52, 1.46
BRAND = "叠光 · 发布演练"

P = {"bg": "#F5F7FC", "card": "#FFFFFF", "line": "#E1E7F2", "ink": "#111C36",
     "ink2": "#2C3B5C", "ink3": "#5A6B8C", "design": "#1B4FBF", "eng": "#C97415",
     "design_soft": "#E7EDFB", "eng_soft": "#FBEEDD", "crit": "#B3261E",
     "buffer": "#E8F3E9", "buffer_ink": "#1F6B3A", "gap": "#DDE3EF",
     "chip": "#E7ECF8", "accent": "#1B4FBF", "edge": "#C6CFE4"}


def tw(t, size, mono=False):
    return sum(size * (CJK_EM if ord(c) > 0x2E80 else (MONO_EM if mono else LATIN_EM))
               for c in t)


def tokens(text):
    out, cur = [], ""
    for ch in text:
        if ch.isascii() and not ch.isspace():
            cur += ch
        else:
            if cur:
                out.append(cur)
                cur = ""
            out.append(ch)
    if cur:
        out.append(cur)
    return out


def wrap(text, size, width, mono=False):
    rows, cur = [], ""
    for tk in tokens(text):
        if cur and tw(cur, size, mono) + tw(tk, size, mono) > width:
            if not tk.strip():
                rows.append(cur.rstrip())
                cur = ""
                continue
            rows.append(cur.rstrip())
            cur = tk.lstrip()
        else:
            cur += tk
    if cur.strip():
        rows.append(cur.rstrip())
    return rows


class Sheet:
    def __init__(self, w, h, min_font, name, margin=24):
        self.w, self.h, self.min_font, self.name = w, h, min_font, name
        self.margin = margin
        self.nodes = [C(width=num(w), height=num(h), color=P["bg"])]
        self.items = []

    def text(self, role, t, x, y, size, colour, *, font=SANS, bold=False, align="left"):
        mono = font == MONO
        w = tw(t, size, mono)
        if align == "right":
            x -= w
        elif align == "center":
            x -= w / 2
        a = {"fontSize": num(size), "color": colour, "fontFamily": font}
        if bold:
            a["fontStyle"] = "BOLD"
        # bold rendering widens advances a little; give the drawn box headroom so the
        # service never wraps a single-line label, while the registered box stays the
        # measured one so the overlap audit keeps its meaning.
        self.nodes.append(Positioned(Node("Text", a, [], t), left=num(x), top=num(y),
                                     width=num(w * 1.14 + 10)))
        self.items.append({"role": role, "text": t,
                           "box": [round(x, 2), round(y, 2), round(x + w, 2),
                                   round(y + size * 1.06, 2)],
                           "font_size": size, "colour": colour, "font": font})
        return y + size * LINE_H

    def para(self, role, t, x, y, size, colour, width, *, font=SANS, bold=False,
             gap=6):
        for ln in wrap(t, size, width, font == MONO):
            y = self.text(role, ln, x, y, size, colour, font=font, bold=bold) + gap
        return y - gap

    def rect(self, x, y, w, h, colour, *, radius=None, shape=None):
        # the parser rejects borderRadius together with shape=CIRCLE
        # (400 PARSE_ERROR "Attr [borderRadius] can not be used with shape CIRCLE")
        a = {"width": num(w), "height": num(h), "color": colour}
        if shape:
            a["shape"] = shape
        elif radius is not None:
            a["borderRadius"] = num(radius)
        self.nodes.append(Positioned(C(**a), left=num(x), top=num(y)))

    def finish(self):
        return Snapshot(Stack(C(width=num(self.w), height=num(self.h)), *self.nodes),
                        background=P["bg"], type="png")

    def audit(self):
        m = self.margin
        ov = [(x["text"], y["text"]) for i, x in enumerate(self.items)
              for y in self.items[i + 1:]
              if not (x["box"][2] <= y["box"][0] or y["box"][2] <= x["box"][0]
                      or x["box"][3] <= y["box"][1] or y["box"][3] <= x["box"][1])]
        out = [i["text"] for i in self.items
               if i["box"][0] < m or i["box"][1] < 8 or i["box"][2] > self.w - m
               or i["box"][3] > self.h - 8]
        small = [i["text"] for i in self.items if i["font_size"] < self.min_font]
        return {"view": self.name, "size": [self.w, self.h], "margin_px": m,
                "texts": len(self.items), "overlap_n": len(ov), "overlaps": ov[:8],
                "outside_n": len(out), "outside": out[:8],
                "below_min_font_n": len(small), "below_min_font": small[:8],
                "min_font": self.min_font}


def hh(minute):
    h, m = divmod(9 * 60 + int(minute), 60)
    return f"{h:02d}:{m:02d}"


def load():
    return json.loads((TMP / "schedule.json").read_text(encoding="utf-8"))


def place(labels, min_gap=10):
    placed, prev = [], -1e9
    for text, x0, w in labels:
        x = max(x0, prev + min_gap)
        placed.append((text, x, w))
        prev = x + w
    return placed


# ------------------------------------------------------------------ board
def board(S):
    sc = Sheet(1920, 1080, 20, "execution-board", margin=40)
    x0, x1 = 260, 1880
    scale = (x1 - x0) / 420.0

    def X(m):
        return x0 + m * scale

    sc.text("brand", BRAND, 48, 36, 26, P["accent"], bold=True, font=MONO)
    sc.text("title", "发布执行泳道图 · 12 项任务 / 2 个团队", 48, 70, 40, P["ink"],
            bold=True)
    sc.text("window", "2026-11-07 09:00 开工 → 16:00 截止 · 连续 420 分钟不扣休 · "
                      "横轴同一时间尺度 · 团队切换不计时", 48, 126, 22, P["ink3"])
    sc.text("head_right", f"全部完成 {hh(S['finish_minute'])} · 剩余缓冲 "
                          f"{S['buffer_minutes']} 分钟", x1, 52, 28, P["buffer_ink"],
            bold=True, align="right")
    sc.text("head_note", f"关键路径 {S['critical_path_minutes']}′ · 总工时 "
                         f"{S['total_work_minutes']}′ · 两团队下界 "
                         f"{S['total_work_minutes'] / 2}′ · 本方案完工 "
                         f"{S['finish_minute']}′", x1, 96, 22, P["ink2"], align="right")

    for m in range(0, 421, 60):
        sc.rect(X(m), 186, 1, 610, P["line"])
        align = "center" if 0 < m < 420 else ("left" if m == 0 else "right")
        sc.text("tick", hh(m), X(m), 156, 22, P["ink3"], align=align, font=MONO)

    lanes = [("design", 206, P["design"], P["design_soft"]),
             ("engineering", 466, P["eng"], P["eng_soft"])]
    crit = set(S["critical_path_chain"])
    gaps_found = []
    for team, ly, col, soft in lanes:
        rows = sorted([t for t in S["tasks"] if t["team"] == team],
                      key=lambda t: t["start_minute"])
        sc.rect(x0, ly, x1 - x0, 210, P["card"], radius=12)
        sc.rect(x0, ly, 6, 210, col, radius=3)
        sc.text("lane_team", team, 48, ly + 24, 30, P["ink"], bold=True, font=MONO)
        sc.text("lane_cn", "设计团队" if team == "design" else "工程团队", 48, ly + 68,
                24, P["ink2"])
        sc.text("lane_load", f"{S['team_load_minutes'][team]} 分钟 · {len(rows)} 项",
                48, ly + 104, 22, P["ink3"])
        sc.rect(X(S["finish_minute"]), ly + 10, X(420) - X(S["finish_minute"]) - 4, 190,
                P["buffer"], radius=10)
        sc.text("buffer", f"缓冲 {S['buffer_minutes']} 分钟",
                (X(S["finish_minute"]) + X(420)) / 2, ly + 92, 24, P["buffer_ink"],
                bold=True, align="center")
        cur = 0
        for t in rows:
            if t["start_minute"] > cur:
                gaps_found.append((team, cur, t["start_minute"]))
                if t["start_minute"] < S["finish_minute"]:
                    sc.rect(X(cur), ly + 60, max((t["start_minute"] - cur) * scale, 3),
                            64, P["gap"], radius=4)
            cur = t["end_minute"]
        tops, bots = [], []
        for t in rows:
            bx, bw = X(t["start_minute"]), (t["end_minute"] - t["start_minute"]) * scale
            sc.rect(bx, ly + 60, bw, 64, col, radius=8)
            if t["id"] in crit:
                sc.rect(bx, ly + 60, bw, 8, P["crit"], radius=4)
            sc.text("bar_id", t["id"], bx + bw / 2, ly + 82, 24, "#FFFFFF", bold=True,
                    align="center", font=MONO)
            tops.append((t["label"], bx, tw(t["label"], 22)))
            txt = f"{hh(t['start_minute'])}-{hh(t['end_minute'])} · {t['minutes']}′"
            bots.append((txt, bx, tw(txt, 20, True)))
        for text, x, w in place(tops):
            sc.text("bar_label", text, x, ly + 22, 22, P["ink"])
        for text, x, w in place(bots, min_gap=16):
            sc.text("bar_time", text, x, ly + 134, 20, P["ink2"], font=MONO)

    sc.rect(X(S["finish_minute"]) - 1, 148, 3, 648, P["buffer_ink"])
    sc.text("finish_line", f"{hh(S['finish_minute'])} 全部完成",
            X(S["finish_minute"]) - 12, 806, 24, P["buffer_ink"], bold=True,
            align="right")
    sc.rect(X(420) - 1, 148, 3, 648, P["crit"])
    sc.text("deadline_line", "16:00 截止线", X(420) - 8, 806, 24, P["crit"], bold=True,
            align="right")

    sc.rect(48, 850, 1824, 1, P["line"])
    ly = 872
    for i, (col, label) in enumerate([(P["design"], "design 任务块"),
                                      (P["eng"], "engineering 任务块"),
                                      (P["crit"], "关键路径任务"),
                                      (P["gap"], "团队空档"),
                                      (P["buffer"], "截止前缓冲")]):
        x = 48 + i * 250
        sc.rect(x, ly + 4, 18, 18, col, radius=4)
        sc.text("legend", label, x + 26, ly, 22, P["ink2"])
    gap_txt = "空档：" + " · ".join(
        f"{t} {hh(a)}-{hh(b)}（{b - a}′）" for t, a, b in gaps_found) +         " · 其余时段两团队连续作业，切换不计时"
    sc.text("gap_note", gap_txt, 48, ly + 34, 22, P["ink2"])

    deps = "   ".join(f"{t['id']}←" + ("—" if not t["depends"]
                                    else ",".join(t["depends"])) for t in S["tasks"])
    sc.text("dep_head", "依赖索引（编号即任务 ID；不画交叉连线以免遮挡时间块）", 48,
            ly + 68, 22, P["ink"], bold=True)
    sc.text("deps", deps, 48, ly + 98, 22, P["ink2"], font=MONO)
    sc.text("risk_head", "输入风险：", 48, ly + 128, 22, P["ink"], bold=True)
    sc.para("risks", "　　".join(f"{r['id']}（{r['task']}）{r['impact']} → {r['mitigation']}"
                                for r in S["source_risks"]), 210, ly + 128, 22,
            P["ink2"], 1662)
    return sc


def BRIEF_WHY(S):
    return [
        f"① 下界：只按依赖算，关键路径 {S['critical_path_minutes']} 分钟，任何排程都不可能更早；"
        f"总工时 {S['total_work_minutes']} ÷ 2 团队 = {S['total_work_minutes'] / 2} 分钟；"
        f"取大者 {S['lower_bound_minutes']} 分钟。",
        "② 求解：穷举全部「优先级序 × 团队指派」的活跃排程（2184 状态，按 maxend、"
        "依赖最早完成、两团队负载三条可行下界剪枝 983 支），最小完工 260 分钟。",
        "③ 5 分钟差来自 R05：它依赖 R01（第 25 分才结束），design 的 25-85 分被 R04 占满，"
        "engineering 只能先做 R03 再回头做 R05，R07 因此 90 分才开工，后续整链顺延。",
        "④ 换法更差（同一搜索加约束实测）：R05 给 design → 285′；R09 给 "
        "engineering → 285′；R12 换队 → 仍 260′。不删检查、不缩时长、不改依赖。",
    ]


# ------------------------------------------------------------------ brief
def brief(S):
    sc = Sheet(1200, 1600, 24, "decision-brief", margin=48)
    by = {t["id"]: t for t in S["tasks"]}
    sc.text("brand", BRAND, 56, 40, 26, P["accent"], bold=True, font=MONO)
    sc.text("title", "发布决策简报", 56, 74, 44, P["ink"], bold=True)
    sc.text("sub", "2026-11-07 09:00 开工 · 16:00 截止 · 双团队各一组 · 同团队不可并行不可抢占",
            56, 136, 24, P["ink3"])

    kpis = [("全部完成", hh(S["finish_minute"]), f"第 {S['finish_minute']} 分钟"),
            ("剩余缓冲", f"{S['buffer_minutes']}′", "2 小时 40 分钟"),
            ("总工时", f"{S['total_work_minutes']}′", "12 项求和"),
            ("关键路径", f"{S['critical_path_minutes']}′", "忽略团队的下界")]
    for i, (k, v, note) in enumerate(kpis):
        x = 56 + i * 276
        sc.rect(x, 186, 260, 156, P["card"], radius=12)
        sc.rect(x, 186, 260, 5, P["accent"], radius=2)
        sc.text("kpi_k", k, x + 20, 204, 24, P["ink3"])
        sc.text("kpi_v", v, x + 20, 240, 44, P["ink"], bold=True, font=MONO)
        sc.text("kpi_n", note, x + 20, 298, 24, P["ink2"])

    sc.text("dep_title", "依赖概览（按最早开始分层，连线指向后继任务）", 56, 372, 28,
            P["ink"], bold=True)
    levels = [["R01", "R02"], ["R03", "R04", "R05"], ["R06", "R07"], ["R08", "R09"],
              ["R10", "R11"], ["R12"]]
    crit = set(S["critical_path_chain"])
    lx, ly0, colw, rowh = 56, 418, 190, 96
    pos = {}
    for c, col in enumerate(levels):
        for r, tid in enumerate(col):
            pos[tid] = (lx + c * colw + 62, ly0 + r * rowh + 34)
    for t in S["tasks"]:
        for d in t["depends"]:
            x1_, y1_ = pos[d]
            x2_, y2_ = pos[t["id"]]
            sc.rect(x1_ + 48, y1_ - 1, x2_ - x1_ - 96, 2, P["edge"])
            sc.rect(x2_ - 48, min(y1_, y2_) - 1, 2, abs(y2_ - y1_) + 2, P["edge"])
            sc.rect(x2_ - 48, y2_ - 1, 8, 2, P["edge"])
    for tid, (x, y) in pos.items():
        t = by[tid]
        col = P["design"] if t["team"] == "design" else P["eng"]
        sc.rect(x - 48, y - 30, 96, 60, P["card"], radius=10)
        sc.rect(x - 48, y - 30, 5, 60, col, radius=2)
        sc.text("node_id", tid, x + 2, y - 26, 24, P["ink"], bold=True, align="center",
                font=MONO)
        sc.text("node_min", f"{t['minutes']}′", x + 2, y + 2, 24, P["ink3"],
                align="center", font=MONO)
        if tid in crit:
            sc.rect(x + 30, y - 26, 12, 12, P["crit"], radius=6, shape="CIRCLE")
    sc.text("lv_note", "红点＝关键路径 R01→R04→R07→R09→R10→R12（合计 255 分钟）；"
                       "同层任务彼此无依赖", 56, ly0 + 3 * rowh + 36, 24, P["ink2"])
    why_top = ly0 + 3 * rowh + 96

    why_items = BRIEF_WHY(S)
    why_lines = [ln for it in why_items for ln in wrap(it, 24, 1032)]
    why_h = 58 + len(why_lines) * 36 + (len(why_items) - 1) * 6
    sc.rect(56, why_top, 1088, why_h, P["card"], radius=14)
    sc.text("why_h", "排程依据", 80, why_top + 20, 28, P["ink"], bold=True)
    y = why_top + 62
    for line in why_items:
        y = sc.para("why", line, 80, y, 24, P["ink2"], 1032, gap=1) + 6
    ry = why_top + why_h + 26

    sc.text("risk_h", "三风险与对策（缓冲用于吸收返工与等待，不擅自加进题面时长）", 56,
            ry, 28, P["ink"], bold=True)
    for i, r in enumerate(S["source_risks"]):
        y = ry + 42 + i * 92
        sc.rect(56, y, 1088, 82, P["card"], radius=12)
        sc.rect(56, y, 6, 82, P["crit"], radius=3)
        sc.text("risk_id", f"{r['id']} · {r['task']} {by[r['task']]['label']}", 80,
                y + 10, 26, P["ink"], bold=True)
        sc.text("risk_imp", f"影响：{r['impact']}", 80, y + 48, 24, P["ink2"])
        sc.text("risk_mit", f"对策：{r['mitigation']}", 620, y + 48, 24, P["buffer_ink"])
    foot_y = ry + 42 + 3 * 92 + 4
    sc.rect(56, foot_y, 1088, 1, P["line"])
    sc.text("foot", "数据源 inputs/release.json · 三张图与两份 JSON 同源 schedule.json",
            56, foot_y + 12, 24, P["ink3"])
    return sc


# ------------------------------------------------------------------ card
def card(S):
    sc = Sheet(720, 1280, 20, "action-card", margin=16)
    by = {t["id"]: t for t in S["tasks"]}
    crit = set(S["critical_path_chain"])
    risk_by_task = {r["task"]: r["id"] for r in S["source_risks"]}
    sc.rect(0, 0, 720, 164, P["accent"])
    sc.text("brand", BRAND, 32, 22, 24, "#FFFFFF", bold=True, font=MONO)
    sc.text("title", "今日行动卡", 32, 54, 40, "#FFFFFF", bold=True)
    sc.text("sub", f"09:00 开工 · {hh(S['finish_minute'])} 全部完成 · 16:00 截止"
                   f"（缓冲 {S['buffer_minutes']}′）", 32, 116, 22, "#DCE6FF")
    sc.text("legend", "design 蓝 · engineering 橙 · 红点＝关键路径 · ⚠＝输入风险",
            32, 176, 20, P["ink3"])

    rows = sorted(S["tasks"], key=lambda t: (t["start_minute"], t["id"]))
    y = 206
    for t in rows:
        col = P["design"] if t["team"] == "design" else P["eng"]
        soft = P["design_soft"] if t["team"] == "design" else P["eng_soft"]
        sc.rect(20, y, 680, 60, P["card"], radius=10)
        sc.rect(20, y, 6, 60, col, radius=3)
        sc.rect(34, y + 6, 128, 48, soft, radius=8)
        sc.text("time", f"{hh(t['start_minute'])}-{hh(t['end_minute'])}", 98, y + 8,
                22, P["ink"], bold=True, align="center", font=MONO)
        sc.text("mins", f"{t['minutes']} 分钟", 98, y + 33, 20, P["ink3"],
                align="center", font=MONO)
        sc.text("id", t["id"], 176, y + 8, 24, col, bold=True, font=MONO)
        if t["id"] in crit:
            sc.rect(222, y + 14, 12, 12, P["crit"], radius=6, shape="CIRCLE")
        sc.text("label", t["label"], 244, y + 8, 24, P["ink"], bold=True)
        rk = risk_by_task.get(t["id"])
        sc.text("team", f"{t['team']} · 依赖 "
                        + ("—" if not t["depends"] else "、".join(t["depends"])),
                176, y + 34, 20, P["ink2"])
        if rk:
            sc.text("risk", f"⚠ {rk}", 688, y + 12, 24, P["crit"], bold=True,
                    align="right")
        y += 66
    sc.rect(20, y + 2, 680, 1, P["line"])
    y += 14
    y = sc.text("now_h", "开工前 3 件事", 20, y, 24, P["ink"], bold=True) + 4
    for line in [
        "1. design 起 R01、engineering 起 R02 同时开工（09:00）",
        "2. R01 一结束就把 R05 交给 engineering（唯一卡 5 分钟的点）",
        f"3. {hh(S['finish_minute'])} 前完成 R12 即达标，剩余 {S['buffer_minutes']}′ "
        "留给 K1/K2/K3"]:
        y = sc.para("now", line, 20, y, 20, P["ink2"], 680, gap=1) + 6
    y += 6
    y = sc.para("riskkey", "K1（R02）服务限流→按 Retry-After 重试；K2（R05）长文案→"
                           "先冻结再适配；K3（R10）图像缺陷→用缓冲返工，不跳过看图",
                20, y, 20, P["ink3"], 680, gap=1)
    assert y <= 1280 - 16, f"card footer overflows: {y}"
    return sc


def main():
    S = load()
    sheets = {"execution-board": board(S), "decision-brief": brief(S),
              "action-card": card(S)}
    rep = []
    for name, sc in sheets.items():
        (TMP / f"{name}.snapshot").write_text(sc.finish().render() + "\n",
                                              encoding="utf-8")
        a = sc.audit()
        a["dsl"] = f"{name}.snapshot"
        rep.append(a)
    (TMP / "layout-audit.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps([{"view": a["view"], "overlap_n": a["overlap_n"],
                       "outside_n": a["outside_n"],
                       "below_min_font_n": a["below_min_font_n"],
                       "texts": a["texts"]} for a in rep], ensure_ascii=False))


if __name__ == "__main__":
    main()
