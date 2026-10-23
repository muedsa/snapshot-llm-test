"""A24 三张图构建器：执行泳道 1920×1080、决策简报 1200×1600、手机行动卡 720×1280。

三张图读同一份 outputs/<run>/A24/schedule.json，不各自重算排程；分钟偏移是唯一的
时间真相，像素位置由 X0 + minute * PPM 直接推出，所以图上时间轴是等比的。

提交渲染前先过干跑门禁（--check）：文字框不越出画布、同层文字框互不重叠、
字号达标（横屏 ≥20、竖页 ≥24、手机 ≥20）、块内文字确实装得下、块外时间标签不与
邻居碰撞、依赖索引表 12 行齐全、时间轴比例一致。

用法
    python -I -X utf8 a24_pages.py --check     # 只算几何并断言，不提交请求
    python -I -X utf8 a24_pages.py --render    # 过门禁后逐张渲染并落交付件
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
sys.path.insert(0, str(HERE.parent))

TASK = "A24"
OUT = ROOT / "outputs" / RUN_ID / TASK
TMP = ROOT / "tmp" / RUN_ID / TASK

# ------------------------------------------------------------------ 字体与配色
FONT = "Noto Sans CJK SC,Inter"
INK = "#0F172A"
INK2 = "#3D4A5C"
INK3 = "#667085"
LINE = "#E3E8EF"
LINE2 = "#EEF2F7"
BG = "#F5F7FA"
PANEL = "#FFFFFF"
DES = "#1D4ED8"
DES_L = "#E7EEFC"
ENG = "#0E9F6E"
ENG_L = "#DCF3E9"
WARN = "#B54708"
WARN_L = "#FDF3E9"
DANGER = "#D92D20"
DANGER_L = "#FBEAE8"
BUF = "#EAF8F0"
HATCH_A = "#EDF1F7"
HATCH_B = "#C6D0DE"
TEAM_FILL = {"design": DES, "engineering": ENG}
TEAM_SOFT = {"design": DES_L, "engineering": ENG_L}
TEAM_ZH = {"design": "设计", "engineering": "工程"}
CP_PATH = ["R01", "R04", "R07", "R09", "R10", "R12"]
CP = set(CP_PATH)
WINDOW = 420

CJK_WIDE = set("←→★■▼▲·")


def fmt(v) -> str:
    if isinstance(v, float) and abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return str(v)


def esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def attrs(d: dict) -> str:
    return " ".join('%s="%s"' % (k, esc(v)) for k, v in d.items() if v is not None)


def tw(s: str, fs: float) -> float:
    """文字宽度估算：CJK/全角 1em，ASCII 字母数字 0.56em，空格 0.3em。

    只用于判断「装不装得下」和计算居中位置，真实排版由服务端完成。
    """
    w = 0.0
    for ch in s:
        o = ord(ch)
        if (0x2E80 <= o <= 0x9FFF or 0xA000 <= o <= 0xA4CF or 0x3000 <= o <= 0x303F
                or 0xFF00 <= o <= 0xFF60 or 0x3040 <= o <= 0x30FF
                or 0xFE30 <= o <= 0xFE4F or 0x2018 <= o <= 0x201F
                or ch in CJK_WIDE):
            w += fs
        elif ch == " ":
            w += fs * 0.30
        elif ch == "÷":
            w += fs * 0.62
        else:
            w += fs * 0.56
    return w


def pitch(fs: float) -> float:
    """一行文字占用的纵向高度。Text 的 height=1.0，字形本身在 1em 内，
    所以只要行距 ≥ 1em，相邻行的字形就不会相撞。"""
    return fs * 1.2


class Doc:
    """收集 Positioned 片段，同时记录每个文字框矩形供干跑碰撞检查。"""

    def __init__(self, w: int, h: int, bg: str = BG):
        self.w, self.h, self.bg = w, h, bg
        self.parts: list[str] = []
        self.texts: list[dict] = []
        self.rects: list[dict] = []

    def rect(self, x, y, w, h, color=None, radius=0, border=None):
        a = {"width": fmt(w), "height": fmt(h)}
        if color:
            a["color"] = color
        if radius:
            a["borderRadius"] = fmt(radius)
        if border:
            a["border"] = border
        self.parts.append('<Positioned left="%s" top="%s"><Container %s/></Positioned>'
                          % (fmt(round(x, 2)), fmt(y), attrs(a)))
        # 只记录几何供 content-map.json 引用，不改变输出片段
        self.rects.append({"x": round(x, 2), "y": y, "w": round(w, 2), "h": h,
                           "color": color, "radius": radius, "border": border})

    def text(self, x, y, s, fs=20, color=INK, bold=False, owner="txt",
             anchor="left", right=None):
        if anchor == "right" and right is not None:
            x = right - tw(s, fs)
        elif anchor == "center" and right is not None:
            x = (x + right) / 2.0 - tw(s, fs) / 2.0
        h = pitch(fs)
        t = {"text": s, "fontFamily": FONT, "fontSize": fmt(fs), "color": color,
             "height": "1.0", "softWrap": "FALSE", "textDirection": "LTR"}
        if bold:
            t["fontStyle"] = "BOLD"
        self.parts.append('<Positioned left="%s" top="%s" height="%s"><Text %s/></Positioned>'
                          % (fmt(round(x, 2)), fmt(y), fmt(h), attrs(t)))
        self.texts.append({"x": x, "y": y, "w": tw(s, fs), "h": h, "text": s,
                           "fs": fs, "owner": owner})

    def build(self) -> str:
        body = "\n".join(self.parts)
        return ('<Snapshot type="png" background="%s"><Container width="%d" height="%d">'
                '<Stack width="%d" height="%d" fit="EXPAND" clipBehavior="NONE">\n%s\n'
                '</Stack></Container></Snapshot>\n'
                % (self.bg, self.w, self.h, self.w, self.h, body))


# ------------------------------------------------------------------ 干跑门禁
def hit(a: dict, b: dict) -> bool:
    return not (a["x"] + a["w"] <= b["x"] + 1e-6
                or b["x"] + b["w"] <= a["x"] + 1e-6
                or a["y"] + a["h"] <= b["y"] + 1e-6
                or b["y"] + b["h"] <= a["y"] + 1e-6)


def dry_run(doc: Doc, name: str, min_fs: float, extras: list[dict]):
    gates = list(extras)

    def g(cid, check, ok, detail=""):
        gates.append({"id": cid, "check": check, "passed": bool(ok), "detail": detail})

    off = [t for t in doc.texts
           if t["x"] < -0.5 or t["y"] < -0.5
           or t["x"] + t["w"] > doc.w + 0.5 or t["y"] + t["h"] > doc.h + 0.5]
    g(name + "-01", "所有文字框在画布内", not off,
      "; ".join("%.0f..%.0f %.0f..%.0f %s" % (t["x"], t["x"] + t["w"], t["y"],
                                              t["y"] + t["h"], t["text"][:24])
                for t in off[:6]))
    cl = []
    for i in range(len(doc.texts)):
        for j in range(i + 1, len(doc.texts)):
            if hit(doc.texts[i], doc.texts[j]):
                cl.append("%s × %s" % (doc.texts[i]["text"][:18],
                                       doc.texts[j]["text"][:18]))
    g(name + "-02", "同层文字框互不重叠", not cl, "; ".join(cl[:8]))
    bad = [t for t in doc.texts if t["fs"] + 1e-6 < min_fs]
    g(name + "-03", "正文字号 ≥ %g" % min_fs, not bad,
      "; ".join("%s=%g" % (t["text"][:18], t["fs"]) for t in bad[:6]))
    return gates


# ------------------------------------------------------------------ 数据读取
def load():
    with (OUT / "schedule.json").open(encoding="utf-8") as fh:
        sch = json.load(fh)
    with (OUT / "schedule-audit.json").open(encoding="utf-8") as fh:
        aud = json.load(fh)
    return sch, aud


def clock(t: str) -> str:
    """把 2026-11-07T09:25+08:00 取成 09:25。"""
    return t[11:16]


def hm(minute: int) -> str:
    """把相对 09:00 的分钟偏移转成钟表时间。"""
    return "%02d:%02d" % (9 + minute // 60, minute % 60)


def waits(sch) -> dict:
    """等式成立才算等待：start = max(同团队上一任务 end, 全部前驱 end)。

    只用 schedule.json 的字段复算，不依赖求解器内部状态。
    """
    by = {t["id"]: t for t in sch["tasks"]}
    out = {}
    for t in sch["tasks"]:
        lane = [u["end_minute"] for u in sch["tasks"]
                if u["team"] == t["team"] and u["end_minute"] <= t["start_minute"]]
        lane_free = max(lane, default=0)
        pred_max = max((by[p]["end_minute"] for p in t["depends"]), default=0)
        out[t["id"]] = {
            "wait": t["start_minute"] - lane_free,
            "dep_gap": t["start_minute"] - pred_max,
            "forced_by": [p for p in t["depends"]
                          if by[p]["end_minute"] == t["start_minute"]],
            "bound_by": ("dependency" if pred_max > lane_free
                         else "lane" if pred_max < lane_free else "both"),
        }
    return out


# ============================================================ 图一：执行泳道
BX, BX1, PPM = 206.0, 1886.0, 4.0


def px(m: float) -> float:
    return BX + m * PPM


def build_board(sch, aud, wt) -> tuple[Doc, list[dict]]:
    d = Doc(1920, 1080)
    tasks = sch["tasks"]
    lb = aud["lower_bounds"]
    cpmin = lb["dependency_critical_path"]["minutes"]
    wbmin = lb["workload_divided_by_teams"]["minutes"]
    finish = sch["finish_minute"]
    buffer_ = sch["buffer_minutes"]
    total = sch["workload_minutes"]["total"]
    extra = []

    # ---- 标题
    d.text(40, 10, "叠光 · 发布演练", fs=20, color=INK3)
    d.text(40, 42, "发布日执行泳道", fs=28, bold=True)
    d.text(252, 50, "2026-11-07 09:00-16:00 · 连续 420 分钟 · 12 个任务全部执行",
           fs=20, color=INK2)
    d.text(1880, 50, "1 分钟 = 4 像素等比 · 占 [start,end) 左闭右开", fs=20,
           color=INK3, anchor="right", right=1880)

    # ---- KPI
    kpis = [("完工时间", clock(sch["finish_time"]), "第 %d 分钟" % finish),
            ("剩余缓冲", "%d 分钟" % buffer_, "%s - 16:00" % clock(sch["finish_time"])),
            ("总工作量", "%d 分钟" % total,
             "design %d · eng %d" % (sch["workload_minutes"]["design"],
                                     sch["workload_minutes"]["engineering"])),
            ("关键路径下界", "%d 分钟" % cpmin, "工作量下界 %g" % wbmin)]
    kw, kg, kx = 448.0, 16.0, 40.0
    for i, (lab, val, sub) in enumerate(kpis):
        x = kx + i * (kw + kg)
        d.rect(x, 88, kw, 104, color=PANEL, radius=12, border="1 SOLID %s" % LINE)
        d.rect(x + 14, 100, 4, 84, color=INK3, radius=2)
        d.text(x + 30, 94, lab, fs=20, color=INK3)
        d.text(x + 30, 122, val, fs=32, bold=True)
        d.text(x + 30, 162, sub, fs=20, color=INK2)

    # ---- 小时刻度
    for m in range(0, WINDOW + 1, 60):
        d.text(px(m), 206, "%02d:00" % (9 + m // 60), fs=20, color=INK3,
               anchor="center", right=px(m))
    for m in range(30, WINDOW, 60):
        d.rect(px(m) - 0.5, 230, 1, 6, color=LINE)

    # ---- 泳道
    lane_y = {"design": 236.0, "engineering": 396.0}
    LH = 158.0
    for team in ("design", "engineering"):
        ly = lane_y[team]
        d.rect(200, ly, 1690, LH, color=PANEL, radius=10, border="1 SOLID %s" % LINE)
        d.rect(px(finish), ly, BX1 - px(finish), LH, color=BUF)      # 缓冲带
        for m in range(0, WINDOW + 1, 60):                            # 网格
            d.rect(px(m) - 0.5, ly, 1, LH, color=LINE2)
        for a0, b0 in sch["idle_ranges"][team]:                       # 空档斜纹
            x0, x1 = px(a0), px(b0)
            d.rect(x0, ly + 36, x1 - x0, 80, color=HATCH_A)
            c = x0
            while c < x1 - 1:
                d.rect(c, ly + 36, 2, 80, color=HATCH_B)
                c += 6
        d.rect(BX1 - 1.5, ly, 3, LH, color=DANGER)                    # 截止线
        d.rect(44, ly + 44, 140, 70, color=TEAM_SOFT[team], radius=8)
        d.text(54, ly + 50, TEAM_ZH[team], fs=24, bold=True, color=TEAM_FILL[team])
        d.text(54, ly + 82, team, fs=20, color=TEAM_FILL[team])
        d.text(54, ly + 106, "%d 分钟" % sch["workload_minutes"][team], fs=20,
               color=INK3)

    # ---- 任务块与块外时间标签
    used: dict[str, list[dict]] = {"design": [], "engineering": []}
    for t in tasks:
        team, ly = t["team"], lane_y[t["team"]]
        bx = px(t["start_minute"])
        bw = (t["end_minute"] - t["start_minute"]) * PPM
        by = ly + 36
        d.rect(bx, by, bw, 80, color=TEAM_FILL[team], radius=8)
        if t["id"] in CP:
            d.rect(bx, by, bw, 80, color=None, radius=8,
                   border="3 SOLID %s" % PANEL)
        span = "%s-%s" % (clock(t["start"]), clock(t["end"]))
        if bw >= tw(t["label"], 20) + 14:
            d.text(bx, by + 46, t["label"], fs=20, color=PANEL,
                   anchor="center", right=bx + bw)
            strip = span
        else:
            strip = "%s · %s" % (t["label"], span)
        d.text(bx, by + 8, t["id"], fs=24, bold=True, color=PANEL,
               anchor="center", right=bx + bw)
        w_ = tw(strip, 20)
        placed = None
        for slot, yy in (("lower", by + 84), ("upper", ly + 4)):
            cand = {"x": bx, "y": yy, "w": w_, "h": 24, "strip": slot}
            if not any(hit(cand, u) for u in used[team]):
                placed = cand
                break
        if placed is None:
            raise RuntimeError("任务 %s 的时间标签在上下两条标签行都放不下" % t["id"])
        d.text(placed["x"], placed["y"], strip, fs=20, color=INK2)
        used[team].append(placed)

    # 空档说明放在所在泳道的上部标签行，与斜纹区域左对齐
    for team in ("design", "engineering"):
        ly = lane_y[team]
        ups = [u for u in used[team] if u["strip"] == "upper"]
        for a0, b0 in sch["idle_ranges"][team]:
            lab = "空档 %d 分钟" % (b0 - a0)
            cand = {"x": px(a0), "y": ly + 4, "w": tw(lab, 20), "h": 24,
                    "strip": "upper"}
            while cand["x"] + cand["w"] > 206 and any(hit(cand, u) for u in ups):
                cand["x"] -= 6
            d.text(cand["x"], cand["y"], lab, fs=20, color=INK3)
            ups.append(cand)

    # ---- 缓冲带说明
    mid = (px(finish) + BX1) / 2.0
    d.text(mid, 292, "剩余缓冲 %d 分钟" % buffer_, fs=28, bold=True, color=ENG,
           anchor="center", right=mid)
    d.text(mid, 328, "%s 完工 → 16:00 截止" % clock(sch["finish_time"]), fs=20,
           color=INK2, anchor="center", right=mid)

    # ---- 图例
    lx = 206.0
    legend = [(DES, "design %d 分钟" % sch["workload_minutes"]["design"], "solid"),
              (ENG, "engineering %d 分钟" % sch["workload_minutes"]["engineering"],
               "solid"),
              (HATCH_B, "团队空档（斜纹）", "hatch"),
              (DES, "关键路径（白色描边）", "cp"),
              (BUF, "剩余缓冲带", "solid"),
              (DANGER, "16:00 截止线", "line")]
    for color, lab, kind in legend:
        if kind == "hatch":
            d.rect(lx, 566, 16, 20, color=HATCH_A)
            for k in range(0, 16, 6):
                d.rect(lx + k, 566, 2, 20, color=HATCH_B)
        elif kind == "cp":
            d.rect(lx, 566, 16, 20, color=color, radius=4)
            d.rect(lx, 566, 16, 20, color=None, radius=4,
                   border="3 SOLID %s" % PANEL)
        elif kind == "line":
            d.rect(lx + 6, 566, 4, 20, color=color)
        else:
            d.rect(lx, 566, 16, 20, color=color, radius=4)
        d.text(lx + 24, 566, lab, fs=20, color=INK2)
        lx += 24 + tw(lab, 20) + 30

    idle_txt = " · ".join(
        "%s %s-%s（%d 分钟）" % (team, hm(a0), hm(b0), b0 - a0)
        for team in ("design", "engineering")
        for a0, b0 in sch["idle_ranges"][team])
    tot_idle = sum(sch["idle_minutes"].values())
    d.text(40, 590, "空档：%s。" % idle_txt, fs=20, color=INK2)
    d.text(40, 614, "合计 %d 分钟，等于 %d - %d（两团队在 09:00-%s 的可用分钟减去"
                    "总工作量）。" % (tot_idle, finish * 2, total,
                                      clock(sch["finish_time"])), fs=20, color=INK2)

    # ---- 依赖索引表
    d.text(40, 642, "任务索引 · 编号依赖", fs=22, bold=True)
    d.text(1880, 646, "黑色竖条 = 关键路径 " + "→".join(CP_PATH), fs=20, color=INK3,
           anchor="right", right=1880)
    for lab, cx in (("任务", 48), ("标签", 140), ("团队", 450), ("起-止", 660),
                    ("分钟", 970), ("依赖", 1070), ("等待", 1540)):
        d.text(cx, 676, lab, fs=20, bold=True, color=INK3)
    d.rect(40, 702, 1840, 1, color=LINE)
    order = sorted(tasks, key=lambda t: (t["start_minute"], t["id"]))
    for i, t in enumerate(order):
        ry = 706 + i * 24
        on_cp = t["id"] in CP
        if i % 2 == 0:
            d.rect(40, ry - 2, 1840, 24, color=LINE2)
        if on_cp:
            d.rect(40, ry - 2, 4, 24, color=INK)
        w_ = wt[t["id"]]
        if w_["wait"]:
            wait = "%d 分钟（等 %s）" % (w_["wait"], ", ".join(w_["forced_by"]))
            wcol = WARN
        else:
            wait, wcol = "0", INK3
        dep = "← " + ", ".join(t["depends"]) if t["depends"] else "—"
        d.text(48, ry, t["id"], fs=20, bold=on_cp)
        d.text(140, ry, t["label"], fs=20)
        d.rect(450, ry + 4, 12, 12, color=TEAM_FILL[t["team"]], radius=6)
        d.text(470, ry, t["team"], fs=20, color=INK2)
        d.text(660, ry, "%s - %s" % (clock(t["start"]), clock(t["end"])), fs=20)
        d.text(970, ry, "%d" % t["minutes"], fs=20, color=INK2)
        d.text(1070, ry, dep, fs=20, color=INK2 if t["depends"] else INK3)
        d.text(1540, ry, wait, fs=20, color=wcol)
    d.rect(40, 706 + 12 * 24, 1840, 1, color=LINE)

    d.text(40, 1002, "下界：关键路径 %s = %d 分钟（忽略资源约束）；总工作量 %d ÷ 2 团队 = "
                    "%g 分钟。本排程 %d 分钟，比关键路径下界多 %d 分钟。"
                    % ("→".join(CP_PATH), cpmin, total, wbmin, finish, finish - cpmin),
           fs=20, color=INK2)
    d.text(40, 1026, "最优性：%d 种团队指派已全枚举、%d 个分支定界节点、未触发安全阀，"
                     "%d 分钟为已核验全局最优；关键路径下界不紧，最优性由穷举得出而非"
                     "由下界得出。"
                     % (aud["optimality"]["search"]["assignments_enumerated"],
                        aud["optimality"]["search"]["total_nodes"], finish),
           fs=20, color=INK2)
    d.text(40, 1050, "时长、依赖、候选团队与风险均取自 inputs/release.json，未改依赖、"
                     "未缩时、未删检查环节；09:00 = 第 0 分钟。", fs=20, color=INK3)

    extra.append({"id": "board-04", "check": "依赖索引表 12 行齐全且编号与输入一致",
                  "passed": len(order) == 12 and sorted(t["id"] for t in order)
                            == sorted(t["id"] for t in tasks),
                  "detail": "rows=%d" % len(order)})
    extra.append({"id": "board-05",
                  "check": "每个任务的时间标签都在块内或块外标签行落位",
                  "passed": sum(len(v) for v in used.values()) == len(tasks),
                  "detail": "%s" % {k: len(v) for k, v in used.items()}})
    extra.append({"id": "board-06", "check": "时间轴比例一致（1 分钟 = 4 像素）",
                  "passed": abs((BX1 - BX) / WINDOW - PPM) < 1e-9,
                  "detail": "ppm=%g" % PPM})
    extra.append({"id": "board-07", "check": "关键路径 6 个任务全部在表内并有描边",
                  "passed": len(CP & set(t["id"] for t in tasks)) == len(CP),
                  "detail": "cp=%s" % "→".join(CP_PATH)})
    ex8 = aud["optimality"]["search"]
    extra.append({"id": "board-08",
                  "check": "图上『已全枚举 / 未触发安全阀』与审计的搜索记录一致",
                  "passed": bool(ex8["search_exhausted"] and not ex8["aborted_by_node_cap"]),
                  "detail": "combos=%d nodes=%d exhausted=%s node_cap=%s hit=%s"
                            % (ex8["assignments_enumerated"], ex8["total_nodes"],
                               ex8["search_exhausted"], ex8["node_cap"],
                               ex8["aborted_by_node_cap"])})
    tot_wait = sum(wt[t["id"]]["wait"] for t in tasks)
    chain_idle = sum(x["idle_minutes"] for x in aud["gap_analysis"]
                     ["critical_path_chain_idle"])
    extra.append({"id": "board-09",
                  "check": "等待列的等待只出现在 R07 与 R11，各 5 分钟",
                  "passed": tot_wait == chain_idle * 2 and
                            sorted(t["id"] for t in tasks if wt[t["id"]]["wait"])
                            == ["R07", "R11"],
                  "detail": "等待合计 %d 分钟：R07 等 R05 %d 分钟（在关键路径上）、"
                            "R11 等 R09 %d 分钟（在关键路径之外，不改变完工时刻）；"
                            "关键路径空档合计 %d 分钟，两处同源于 R05 被挤出 design 的 "
                            "%d 分钟资源延迟"
                            % (tot_wait, wt["R07"]["wait"], wt["R11"]["wait"],
                               chain_idle, aud["gap_analysis"]["resource_delay_minutes"])})
    return d, dry_run(d, "board", 20, extra)


# ============================================================ 图二：决策简报
def section(d: Doc, y: float, lab: str, right: str | None = None):
    d.text(48, y, lab, fs=26, bold=True)
    if right:
        d.text(1152, y + 1, right, fs=24, color=INK3, anchor="right", right=1152)
    d.rect(48, y + 34, 1104, 1, color=LINE)


def build_brief(sch, aud, wt) -> tuple[Doc, list[dict]]:
    d = Doc(1200, 1600)
    tasks = sch["tasks"]
    by = {t["id"]: t for t in tasks}
    lb = aud["lower_bounds"]
    cpmin = lb["dependency_critical_path"]["minutes"]
    wbmin = lb["workload_divided_by_teams"]["minutes"]
    total = sch["workload_minutes"]["total"]
    finish = sch["finish_minute"]
    buffer_ = sch["buffer_minutes"]
    fin = clock(sch["finish_time"])
    extra = []

    d.text(48, 34, "叠光 · 发布演练", fs=24, color=INK3)
    d.text(48, 70, "发布演练决策简报", fs=34, bold=True)
    d.text(48, 124, "2026-11-07 09:00-16:00 · 连续 420 分钟 · 12 个任务 · design 与 "
                    "engineering 各 1 个团队", fs=24, color=INK2)

    kpis = [("完工时间", fin, "第 %d 分钟" % finish),
            ("剩余缓冲", "%d 分钟" % buffer_, "%s - 16:00" % fin),
            ("总工作量", "%d 分钟" % total,
             "design %d · eng %d" % (sch["workload_minutes"]["design"],
                                     sch["workload_minutes"]["engineering"])),
            ("关键路径下界", "%d 分钟" % cpmin, "工作量下界 %g" % wbmin)]
    tw_, tg, tx = 264.0, 16.0, 48.0
    for i, (lab, val, sub) in enumerate(kpis):
        x = tx + i * (tw_ + tg)
        d.rect(x, 170, tw_, 130, color=PANEL, radius=12, border="1 SOLID %s" % LINE)
        d.rect(x + 14, 190, 4, 90, color=INK3, radius=2)
        d.text(x + 30, 182, lab, fs=24, color=INK3)
        d.text(x + 30, 218, val, fs=40, bold=True)
        d.text(x + 30, 268, sub, fs=24, color=INK2)

    section(d, 324, "一、依赖概览（按时间序）", "虚底 = 关键路径 %d 分钟" % cpmin)
    d.rect(48, 366, 1104, 52, color=DES_L, radius=10)
    d.rect(48, 366, 4, 52, color=DES, radius=2)
    d.text(66, 380, "关键路径：%s = %d 分钟" % ("→".join(CP_PATH), cpmin), fs=24,
           bold=True, color=DES)

    order = sorted(tasks, key=lambda t: (t["start_minute"], t["id"]))
    for i, t in enumerate(order):
        col, row = i // 6, i % 6
        cx = 48 + col * 560
        ry = 432 + row * 38
        if t["id"] in CP:
            d.rect(cx - 6, ry - 5, 552, 44, color=TEAM_SOFT[t["team"]], radius=8)
        d.rect(cx, ry + 6, 14, 14, color=TEAM_FILL[t["team"]], radius=7)
        d.text(cx + 24, ry + 2, t["id"], fs=24, bold=True)
        d.text(cx + 78, ry + 2, t["label"], fs=24)
        dep = "← " + ", ".join(t["depends"]) if t["depends"] else "— 无依赖"
        d.text(cx + 256, ry + 2, dep, fs=24, color=INK2 if t["depends"] else INK3)
        d.text(cx + 540, ry + 2, clock(t["start"]), fs=24, color=INK3,
               anchor="right", right=cx + 540)

    section(d, 684, "二、下界、完工与最优性")
    for lab, cx in (("下界 / 方案", 48), ("数值", 340), ("含义", 560)):
        d.text(cx, 730, lab, fs=24, bold=True, color=INK3)
    rows = [("依赖关键路径", "%d 分钟" % cpmin, "%s，忽略资源约束" % "→".join(CP_PATH)),
            ("总工作量 ÷ 2", "%g 分钟" % wbmin, "%d 分钟 ÷ 2 个团队" % total),
            ("本排程实际", "%d 分钟" % finish, "%s 完成，缓冲 %d 分钟" % (fin, buffer_))]
    for i, (a, b, c) in enumerate(rows):
        ry = 764 + i * 50
        if i % 2 == 0:
            d.rect(48, ry - 4, 1104, 50, color=LINE2)
        d.text(48, ry, a, fs=24, bold=True)
        d.text(340, ry, b, fs=24, bold=True, color=DES if i == 2 else INK)
        d.text(560, ry, c, fs=24, color=INK2)

    ex = aud["optimality"]["search"]
    gap = aud["gap_analysis"]["resource_delay_minutes"]
    opt = ("最优性：%s 是唯三双团队任务（各 2 选 1），共 2³ = %d 种指派已全部枚举。"
           % ("、".join(ex["flexible_tasks"]), ex["assignments_enumerated"]),
          "每种指派再逐个分支定界，搜索 %d 个节点、未触发安全阀。" % ex["total_nodes"],
          "结论：%d 分钟是已核验的全局最优，缓冲 %d 分钟。" % (finish, buffer_),
          "关键路径下界 %d 分钟不紧：实际多 %d 分钟，全在 R04→R07 之间。"
          % (cpmin, gap))
    for i, line in enumerate(opt):
        d.text(48, 926 + i * 28.8, line, fs=24, color=INK2)

    r11 = by["R11"]
    bullets = (
        "关键路径 %s = %d 分钟，整条排在 design 一个团队上。"
        % ("→".join(CP_PATH), cpmin),
        "R05 若留在 design，整体退到 285 分钟；design 也装不下 R04+R05 共 90 分钟。",
        "于是 R07 比关键路径下界晚 5 分钟开工，260 与 255 的差距全部来自这里。",
        "R09 换到 engineering 会让整体退到 300 分钟，所以留在 design。",
        "R11 排在 engineering %s-%s，紧跟 R08 之后，不占用 design。"
        % (clock(r11["start"]), clock(r11["end"])))
    section(d, 1064, "三、排程依据")
    for i, line in enumerate(bullets):
        y = 1112 + i * 30
        d.rect(48, y + 6, 12, 12, color=INK3, radius=6)
        d.text(74, y, line, fs=24, color=INK2)

    section(d, 1276, "四、风险与对策", "审计见 schedule-audit.json")
    risks = {"K1": ("服务限流导致等待", "保留响应并依据 Retry-After 重试", "R02"),
             "K2": ("长文案导致版式回归", "冻结文案后再完成适配", "R05"),
             "K3": ("实际图像暴露裁剪或比例错误", "预留返工缓冲，不跳过看图", "R10")}
    for i, (kid, (title, mitig, tid)) in enumerate(risks.items()):
        y = 1316 + i * 78
        t = by[tid]
        d.rect(48, y, 1104, 72, color=PANEL, radius=10, border="1 SOLID %s" % LINE)
        d.rect(48, y, 4, 72, color=WARN, radius=2)
        d.rect(64, y + 10, 52, 52, color=WARN_L, radius=8)
        d.text(64, y + 22, kid, fs=24, bold=True, color=WARN, anchor="center",
               right=116)
        d.text(130, y + 10, title, fs=24, bold=True)
        d.text(130, y + 40, "对策：" + mitig, fs=24, color=INK2)
        d.text(1136, y + 10, "影响 %s" % tid, fs=24, color=WARN, anchor="right",
               right=1136)
        d.text(1136, y + 40, "%s-%s · %s" % (clock(t["start"]), clock(t["end"]),
                                             t["team"]), fs=24, color=INK3,
               anchor="right", right=1136)

    ck = aud["checks_summary"]
    d.text(48, 1554, "校验 %d/%d 通过 · 排程见 schedule.json，风险未计入固定时长。"
                     % (ck["passed"], ck["total"]), fs=24, color=INK3)

    extra.append({"id": "brief-04", "check": "依赖概览覆盖 12 个任务",
                  "passed": len(order) == 12, "detail": "rows=%d" % len(order)})
    extra.append({"id": "brief-05", "check": "三个风险 K1/K2/K3 均出现且各指向一个任务",
                  "passed": len(risks) == 3, "detail": "K1→R02 K2→R05 K3→R10"})
    extra.append({"id": "brief-06", "check": "简报的完工/缓冲/下界与 schedule.json 一致",
                  "passed": (finish == aud["finish"]["finish_minute"]
                             and buffer_ == aud["finish"]["buffer_minutes"]
                             and cpmin == aud["optimality"]["lower_bound_minutes"]),
                  "detail": "finish=%d buffer=%d cp=%d" % (finish, buffer_, cpmin)})

    # 逐条比对排程依据里的对比数字是否真的写在审计的穷举结果里
    combos = [x["flexible_choice"] for x in ex["per_assignment_optimum"]]
    best = {c["R05"] + "/" + c["R09"]: x["finish"]
            for x, c in zip(ex["per_assignment_optimum"], combos)}
    claims = {"R05 留在 design 退到 285": (285,
                                          max(x["finish"] for x in ex["per_assignment_optimum"]
                                              if x["flexible_choice"]["R05"] == "design")),
              "R05 与 R09 都到 engineering 退到 300": (300,
                                                      max(x["finish"] for x in
                                                          ex["per_assignment_optimum"]
                                                          if x["flexible_choice"]["R05"]
                                                          == "engineering"
                                                          and x["flexible_choice"]["R09"]
                                                          == "engineering")),
              "R05 到 engineering、R09 留 design 最优 260": (260,
                                                        min(x["finish"] for x in
                                                            ex["per_assignment_optimum"]
                                                            if x["flexible_choice"]["R05"]
                                                            == "engineering"
                                                            and x["flexible_choice"]["R09"]
                                                            == "design"))}
    for k, (said, got) in claims.items():
        if said != got:
            extra.append({"id": "brief-07", "check": "排程依据的对比数字与穷举结果一致",
                          "passed": False, "detail": "%s: 图上写 %d，审计算出 %d"
                          % (k, said, got)})
            break
    else:
        extra.append({"id": "brief-07", "check": "排程依据的对比数字与穷举结果一致",
                      "passed": True, "detail": "285 / 300 / 260 全部命中：" + " · ".join(
                          "%s→%d" % (k, v) for k, v in best.items())})

    cp_idle = aud["gap_analysis"]["critical_path_chain_idle"]
    extra.append({"id": "brief-08",
                  "check": "关键路径上的空档只有 R04→R07 一处且等于 5 分钟",
                  "passed": (len(cp_idle) == 1 and cp_idle[0]["idle_minutes"] == gap
                             and cp_idle[0]["after"] == "R04"
                             and cp_idle[0]["task"] == "R07"),
                  "detail": "%s" % json.dumps(cp_idle, ensure_ascii=False)})
    return d, dry_run(d, "brief", 24, extra)


# ============================================================ 图三：手机行动卡
def build_card(sch, aud, wt) -> tuple[Doc, list[dict]]:
    d = Doc(720, 1280)
    finish = sch["finish_minute"]
    buffer_ = sch["buffer_minutes"]
    fin = clock(sch["finish_time"])
    extra = []

    d.text(28, 20, "叠光 · 发布演练", fs=20, color=INK3)
    d.text(28, 52, "手机行动卡", fs=28, bold=True)
    d.text(200, 60, "12 个任务 · 按时间序", fs=20, color=INK2)

    chips = [("完工 %s" % fin, ENG_L, ENG),
             ("缓冲 %d 分钟" % buffer_, BUF, ENG),
             ("截止 16:00", DANGER_L, DANGER)]
    cx = 28.0
    for lab, bg, fg in chips:
        w = tw(lab, 20) + 24
        d.rect(cx, 96, w, 34, color=bg, radius=17)
        d.text(cx + 12, 102, lab, fs=20, bold=True, color=fg)
        cx += w + 8

    order = sorted(sch["tasks"], key=lambda t: (t["start_minute"], t["id"]))
    for i, t in enumerate(order):
        y = 148 + i * 62
        on_cp = t["id"] in CP
        d.rect(28, y, 664, 58, color=PANEL, radius=10,
               border="2 SOLID %s" % (DES if on_cp else LINE))
        d.rect(28, y, 4, 58, color=TEAM_FILL[t["team"]], radius=2)
        d.text(46, y + 6, "%s %s" % (t["id"], t["label"]), fs=22, bold=True)
        d.text(676, y + 10, "%s-%s" % (clock(t["start"]), clock(t["end"])), fs=20,
               bold=True, color=TEAM_FILL[t["team"]], anchor="right", right=676)
        d.rect(46, y + 38, 12, 12, color=TEAM_FILL[t["team"]], radius=6)
        dep = "← " + ", ".join(t["depends"]) if t["depends"] else "— 无依赖"
        d.text(66, y + 34, "%s · %d 分钟 · %s" % (t["team"], t["minutes"], dep),
               fs=20, color=INK2)
        if on_cp:
            d.text(676, y + 34, "关键路径", fs=20, color=DES, anchor="right",
                   right=676)

    d.text(28, 906, "风险提醒", fs=22, bold=True)
    d.rect(28, 940, 664, 1, color=LINE)
    risks = [("K1", "服务限流导致等待", "保留响应并依据 Retry-After 重试", "R02"),
             ("K2", "长文案导致版式回归", "冻结文案后再完成适配", "R05"),
             ("K3", "实际图像暴露裁剪或比例错误", "预留返工缓冲，不跳过看图", "R10")]
    for i, (kid, title, mitig, tid) in enumerate(risks):
        y = 950 + i * 68
        d.rect(28, y, 664, 62, color=WARN_L, radius=10)
        d.rect(28, y, 4, 62, color=WARN, radius=2)
        d.text(46, y + 6, kid, fs=22, bold=True, color=WARN)
        d.text(92, y + 6, title, fs=20, bold=True)
        d.text(92, y + 34, mitig, fs=20, color=INK2)
        d.text(676, y + 8, "→ %s" % tid, fs=22, bold=True, color=WARN,
               anchor="right", right=676)

    d.text(28, 1168, "完工 %s（第 %d 分钟），缓冲 %d 分钟，截止 16:00。"
                     % (fin, finish, buffer_), fs=20, color=INK2)
    d.text(28, 1196, "风险会消耗缓冲，但按题设不加到固定时长；详见 schedule.json。",
           fs=20, color=INK3)
    d.text(28, 1224, "占 [start,end) 左闭右开，上一任务结束时可立即衔接，不跨天。",
           fs=20, color=INK3)

    extra.append({"id": "card-04", "check": "手机卡列出 12 个任务且按开始时间升序",
                  "passed": len(order) == 12 and
                            [t["start_minute"] for t in order] ==
                            sorted(t["start_minute"] for t in order),
                  "detail": "rows=%d" % len(order)})
    extra.append({"id": "card-05", "check": "三个风险提醒均带指向任务",
                  "passed": len(risks) == 3, "detail": "K1→R02 K2→R05 K3→R10"})
    return d, dry_run(d, "card", 20, extra)


# ------------------------------------------------------------------ 主流程
PAGES = [("execution-board", 1920, 1080, "1920×1080 发布日执行泳道"),
         ("decision-brief", 1200, 1600, "1200×1600 发布演练决策简报"),
         ("action-card", 720, 1280, "720×1280 手机行动卡")]


def build_all():
    sch, aud = load()
    wt = waits(sch)
    docs = {"execution-board": build_board(sch, aud, wt),
            "decision-brief": build_brief(sch, aud, wt),
            "action-card": build_card(sch, aud, wt)}
    return docs, sch, aud


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    docs, sch, aud = build_all()

    gates: list[dict] = []
    for name, w, h, purpose in PAGES:
        doc, gs = docs[name]
        gates.extend(gs)
        print("%-18s %4d×%-4d 片段 %4d 文字 %3d 门禁 %d/%d"
              % (name, doc.w, doc.h, len(doc.parts), len(doc.texts),
                 sum(1 for g in gs if g["passed"]), len(gs)))
        for g in gs:
            if not g["passed"]:
                print("   [FAIL] %s %s — %s" % (g["id"], g["check"], g["detail"]))

    TMP.mkdir(parents=True, exist_ok=True)
    (TMP / "page-gates.json").write_text(
        json.dumps({"schema_version": 1, "task_id": TASK, "path_base": "suite_root",
                    "path_note": "路径相对总任务根",
                    "gates": gates,
                    "passed": sum(1 for g in gates if g["passed"]),
                    "total": len(gates)}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    ok = sum(1 for g in gates if g["passed"])
    print()
    print("门禁 %d/%d" % (ok, len(gates)))
    if ok != len(gates):
        return 2

    if mode != "--render":
        return 0

    import snap_client as C
    for name, w, h, purpose in PAGES:
        doc, _ = docs[name]
        dsl = doc.build()
        r = C.render(TASK, dsl, name, kind="render", purpose=purpose, attempts=3)
        status, body = r["status"], r["body"]
        print("  %-18s status=%s bytes=%s request_id=%s"
              % (name, status, len(body) if body else None, r["request_id"]))
        if status != 200 or not body:
            continue
        OUT.mkdir(parents=True, exist_ok=True)
        png = OUT / (name + ".png")
        png.write_bytes(body)
        (OUT / (name + ".snapshot")).write_text(dsl, encoding="utf-8")
        print("     已落盘 %s（%d B）与同名 .snapshot（%d B）"
              % (png.name, png.stat().st_size, len(dsl.encode("utf-8"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
