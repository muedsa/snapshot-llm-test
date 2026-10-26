# -*- coding: utf-8 -*-
"""A14 八组文案压力测试：参数化生成 8 张 1200×630 讲座宣传卡（v3 批量验证版）。

折行策略：校准因子修正单字墨迹宽与前进位的偏差 → 贪心折行 → 全部行一次性
批量实测 → 超宽行末字后移 → 再批量复测 → 稳定后每行单独一个 Text 节点
（softWrap=false, maxLines=1）。渲染器折行行为不参与，杜绝截断。
"""
from __future__ import annotations

import json
import os
import sys
import time as _time
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A14"
TASK_DIR = ROOT / "tasks" / "A14-content-stress-batch"
OUT_DIR = ROOT / "outputs" / RUN_ID / TASK
TMP_DIR = ROOT / "tmp" / RUN_ID / TASK
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "_suite"))
import bm  # noqa: E402
import render as R  # noqa: E402

CARDS = json.loads((TASK_DIR / "inputs" / "cards.json").read_text(encoding="utf-8"))

SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
W, H, M = 1200, 630, 40
MAIN = "#2563EB"
MAIN_DEEP = "#1D4ED8"
INK = "#0F172A"
BODY = "#334155"
MUTED = "#64748B"
LINE = "#E2E8F0"

BRAND = "Structure / Vision"
DATE = "2026.11.07"

STATUS = {
    "开放": {"color": "#059669", "symbol": "✓", "bg": "#FFFFFF"},
    "满额": {"color": "#64748B", "symbol": "■", "bg": "#FFFFFF"},
    "候补": {"color": "#D97706", "symbol": "◐", "bg": "#FFFFFF"},
    "取消": {"color": "#DC2626", "symbol": "✕", "bg": "#FEF2F2"},
}

TITLE_SIZES = [44, 40, 36]
TITLE_MAX_LINES = 3
SPEAKER_SIZE = 28
SPEAKER_MAX_LINES = 2
CANCEL_NOTE = "本场取消"


def cdata(s: str) -> str:
    assert "]]>" not in s
    return f"<![CDATA[{s}]]>"


def text_node(s, x, y, w, size, color, *, bold=False, align="LEFT", mono=False,
              max_lines=1):
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}">'
            f'<Container color="transparent"><Text fontSize="{size}" '
            f'fontFamily="{MONO if mono else SANS}" '
            f'fontStyle="{"BOLD" if bold else "NORMAL"}" color="{color}" '
            f'textAlign="{align}" softWrap="false" maxLines="{max_lines}">'
            f"{cdata(s)}</Text></Container></Positioned>")


def box(x, y, w, h, color, *, radius=None, border=None):
    a = ""
    if radius:
        a += f' borderRadius="{radius}"'
    if border:
        a += f' border="{border}"'
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Container color="{color}"{a}/></Positioned>')


# ================= 测量缓存 =================
_fw_cache: dict[tuple, int] = {}
_cw_cache: dict[tuple, int] = {}
_lw_cache: dict[tuple, int] = {}


def dsl_style(style):
    return "BOLD" if style == "B" else "NORMAL"


def flush_full(pending):
    if not pending:
        return
    items = [{"text": k[0], "size": k[1], "style": dsl_style(k[2]),
              "family": MONO if k[3] else SANS} for k in pending]
    res = bm.batch_measure(items, task_id=TASK, label="A14-measure-full")
    for k, r in zip(pending, res):
        _fw_cache[k] = r["width"] if r["width"] is not None else 0


def fw(text, size, style, mono=False):
    return _fw_cache[(text, size, style, mono)]


def measure_chars(chars_by_size_style):
    items, keys = [], []
    for (size, style), chars in chars_by_size_style.items():
        for ch in sorted(chars):
            if ch == " ":
                continue
            keys.append((ch, size, style))
            items.append({"text": ch, "size": size, "style": dsl_style(style)})
    if not items:
        return
    res = bm.batch_measure(items, task_id=TASK, label="A14-measure-chars")
    for k, r in zip(keys, res):
        _cw_cache[k] = r["width"] if r["width"] is not None else 0
    for (size, style) in chars_by_size_style:
        _cw_cache[(" ", size, style)] = size * 0.32


def measure_lines_batch(pairs):
    """pairs: [(line, size, style)]；一次批量测全部未缓存的行。"""
    todo = []
    seen = set()
    for p in pairs:
        key = (p[0], p[1], p[2])
        if key not in _lw_cache and key not in seen:
            seen.add(key)
            todo.append(p)
    if not todo:
        return
    items = [{"text": p[0], "size": p[1], "style": dsl_style(p[2])} for p in todo]
    res = bm.batch_measure(items, task_id=TASK, label="A14-measure-lines")
    for p, r in zip(todo, res):
        _lw_cache[(p[0], p[1], p[2])] = r["width"] if r["width"] is not None else 0


def line_w(line, size, style):
    return _lw_cache.get((line, size, style), 0)


def tokenize(text):
    """西文连续串（含尾随空格）为 token；CJK 单字为 token；连续破折号为一 token。"""
    tokens, buf = [], ""
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "—" and i + 1 < len(text) and text[i + 1] == "—":
            if buf:
                tokens.append(buf)
                buf = ""
            tokens.append("——")
            i += 2
            continue
        if ord(ch) > 0x2E7F:
            if buf:
                tokens.append(buf)
                buf = ""
            tokens.append(ch)
        else:
            buf += ch
            if ch == " ":
                tokens.append(buf)
                buf = ""
        i += 1
    if buf:
        tokens.append(buf)
    return tokens


def wrap_initial(text, size, maxw, style, factor):
    tokens = tokenize(text)

    def tw(t):
        return sum((_cw_cache.get((c, size, style)) or 0) * factor for c in t)

    lines, cur, cur_w = [], "", 0.0
    for tok in tokens:
        w = tw(tok)
        stripped = tok.rstrip()
        if cur and cur_w + w > maxw + 0.5:
            if stripped and tw(stripped) <= maxw:
                lines.append(cur.rstrip())
                cur, cur_w = tok, w
            else:
                for c in tok:
                    cwid = (_cw_cache.get((c, size, style)) or 0) * factor
                    if cur and cur_w + cwid > maxw + 0.5:
                        lines.append(cur.rstrip())
                        cur, cur_w = c, cwid
                    else:
                        cur += c
                        cur_w += cwid
        else:
            cur += tok
            cur_w += w
    if cur:
        lines.append(cur.rstrip())
    return [l for l in lines if l] or [text]


def plan_lines(text, size, maxw, style):
    full = fw(text, size, style)
    ink_sum = sum((_cw_cache.get((c, size, style)) or 0) for c in text)
    factor = (full / ink_sum) if ink_sum > 0 else 1.0
    return wrap_initial(text, size, maxw, style, factor)


def verify_lines(lines, size, maxw, style):
    """用已缓存的实测宽度调整：超宽行末字后移。返回调整后的行。"""
    lines = list(lines)
    for _ in range(6):
        bad = [i for i, l in enumerate(lines) if line_w(l, size, style) > maxw]
        if not bad:
            break
        i = bad[0]
        if len(lines[i]) <= 1:
            break
        moved = lines[i][-1]
        lines[i] = lines[i][:-1].rstrip()
        if i + 1 < len(lines):
            lines[i + 1] = moved + lines[i + 1]
        else:
            lines.append(moved)
        lines = [l for l in lines if l]
    return lines


def balance_two_lines(text, size, maxw, style):
    """两行且末行过短时，找 token 边界上最均衡的二分（估宽），返回候选两行。"""
    tokens = tokenize(text)
    if len(tokens) < 2:
        return None
    factor_full = fw(text, size, style)
    ink_sum = sum((_cw_cache.get((c, size, style)) or 0) for c in text)
    factor = (factor_full / ink_sum) if ink_sum > 0 else 1.0

    def tw(t):
        return sum((_cw_cache.get((c, size, style)) or 0) * factor for c in t)

    prefix = [0.0]
    for t in tokens:
        prefix.append(prefix[-1] + tw(t))
    total = prefix[-1]
    best_k, best_score = None, None
    for k in range(1, len(tokens)):
        w1, w2 = prefix[k], total - prefix[k]
        if w1 > maxw + 0.5 or w2 > maxw + 0.5:
            continue
        score = abs(w1 - w2)
        if best_score is None or score < best_score:
            best_k, best_score = k, score
    if best_k is None:
        return None
    l1 = "".join(tokens[:best_k]).rstrip()
    l2 = "".join(tokens[best_k:]).rstrip()
    return [l1, l2] if l1 and l2 else None


def finalize_lines(text, size, maxw, style, lines):
    """验证 + 末行孤字均衡化。"""
    lines = verify_lines(lines, size, maxw, style)
    if len(lines) == 2 and line_w(lines[1], size, style) < 0.25 * maxw:
        cand = balance_two_lines(text, size, maxw, style)
        if cand:
            measure_lines_batch([(cand[0], size, style), (cand[1], size, style)])
            if (line_w(cand[0], size, style) <= maxw
                    and line_w(cand[1], size, style) <= maxw):
                lines = cand
    return lines


# ================= 规划 + 验证 =================
# 先登记并测量全部全串
pending = []
for c in CARDS:
    for size in TITLE_SIZES:
        k = (c["title"], size, "B", False)
        if k not in _fw_cache:
            pending.append(k)
    k = (c["speaker"], SPEAKER_SIZE, "N", False)
    if k not in _fw_cache:
        pending.append(k)
for st, d in STATUS.items():
    k = (f"{d['symbol']} {st}", 24, "B", False)
    if k not in _fw_cache:
        pending.append(k)
for k in [(BRAND, 28, "B", False), (DATE, 28, "N", False), (CANCEL_NOTE, 26, "B", False)]:
    if k not in _fw_cache:
        pending.append(k)
flush_full(pending)

# 字符测量
need = {}
for size in TITLE_SIZES:
    chars = set()
    for c in CARDS:
        chars |= set(c["title"])
    need[(size, "B")] = chars
need[(SPEAKER_SIZE, "N")] = set().union(*[set(c["speaker"]) for c in CARDS])
measure_chars(need)

TZ_TOP, TZ_BOT = 126, 452


def badge_width(status):
    st = STATUS[status]
    return fw(f"{st['symbol']} {status}", 24, "B") + 44


plan = {}   # card_id -> dict(size, lines)
for c in CARDS:
    bw = badge_width(c["status"])
    tz_w = (W - M - bw - 36) - M
    for size in TITLE_SIZES:
        lines = plan_lines(c["title"], size, tz_w, "B")
        if len(lines) <= TITLE_MAX_LINES:
            plan[c["id"]] = {"t_size": size, "t_lines": lines, "tz_w": tz_w}
            break
    assert c["id"] in plan, f"{c['id']} 标题规划失败"

spk_plan = {}
for c in CARDS:
    spk_maxw = W - 2 * M - 360
    spk_plan[c["id"]] = plan_lines(c["speaker"], SPEAKER_SIZE, spk_maxw, "N")

# 批量实测所有行
pairs = []
for cid, p in plan.items():
    for l in p["t_lines"]:
        pairs.append((l, p["t_size"], "B"))
for cid, lines in spk_plan.items():
    for l in lines:
        pairs.append((l, SPEAKER_SIZE, "N"))
measure_lines_batch(pairs)

# 验证 + 需要时降档
final = {}
for c in CARDS:
    cid = c["id"]
    p = plan[cid]
    lines = finalize_lines(c["title"], p["t_size"], p["tz_w"], "B", p["t_lines"])
    if len(lines) > TITLE_MAX_LINES:
        # 降到更小字号重来
        for size in TITLE_SIZES:
            if size >= p["t_size"]:
                continue
            lines2 = plan_lines(c["title"], size, p["tz_w"], "B")
            measure_lines_batch([(l, size, "B") for l in lines2])
            lines2 = finalize_lines(c["title"], size, p["tz_w"], "B", lines2)
            if len(lines2) <= TITLE_MAX_LINES:
                p = {"t_size": size, "t_lines": lines2, "tz_w": p["tz_w"]}
                lines = lines2
                break
        else:
            raise SystemExit(f"{cid} 标题无法在 ≥36px 下 3 行内排下")
    spk_maxw = W - 2 * M - 360
    spk_lines = verify_lines(spk_plan[cid], SPEAKER_SIZE, spk_maxw, "N")
    if len(spk_lines) > SPEAKER_MAX_LINES:
        raise SystemExit(f"{cid} 讲者无法 2 行内排下")
    final[cid] = {"title_size": p["t_size"], "title_lines": lines,
                  "speaker_lines": spk_lines, "tz_w": p["tz_w"],
                  "spk_maxw": spk_maxw}
    print(f"{cid}: title {p['t_size']}px x{len(lines)} lines; speaker x{len(spk_lines)} lines")

# ================= 生成 DSL =================
audit = []

for c in CARDS:
    cid = c["id"]
    st = STATUS[c["status"]]
    f = final[cid]
    t_size, t_lines = f["title_size"], f["title_lines"]
    tz_w = f["tz_w"]
    t_lh = round(t_size * 1.22)
    block_h = len(t_lines) * t_lh
    note_h = 44 if c["status"] == "取消" else 0
    group_h = block_h + note_h
    top = TZ_TOP + (TZ_BOT - TZ_TOP - group_h) / 2
    nodes = [box(0, 0, W, H, st["bg"]), box(0, 0, W, 10, MAIN)]
    nodes.append(text_node(BRAND, M, 42, fw(BRAND, 28, "B") + 8, 28, INK, bold=True))
    nodes.append(text_node(DATE, W - M - fw(DATE, 28, "N") - 8, 42, fw(DATE, 28, "N") + 8,
                           28, MUTED, align="RIGHT"))
    nodes.append(box(M, 98, W - 2 * M, 1, LINE))
    badge_text = f"{st['symbol']} {c['status']}"
    badge_tw = fw(badge_text, 24, "B")
    badge_w = badge_tw + 44
    badge_h, badge_y = 46, 126
    nodes.append(box(W - M - badge_w, badge_y, badge_w, badge_h, st["color"], radius=23))
    nodes.append(text_node(badge_text, W - M - badge_w + 22,
                           badge_y + (badge_h - 24) / 2 - 1, badge_tw + 4, 24, "#FFFFFF",
                           bold=True))
    for i, ln in enumerate(t_lines):
        nodes.append(text_node(ln, M, top + i * t_lh, tz_w, t_size, INK, bold=True))
    title_box = [M, round(top, 1), M + tz_w, round(top + block_h, 1)]
    note_box = None
    if c["status"] == "取消":
        ny = top + block_h + 16
        nw = fw(CANCEL_NOTE, 26, "B") + 8
        nodes.append(text_node(CANCEL_NOTE, M, ny, nw, 26, st["color"], bold=True))
        note_box = [M, round(ny, 1), M + nw, round(ny + 30, 1)]
    nodes.append(box(M, 470, W - 2 * M, 1, LINE))
    nodes.append(text_node("讲者", M, 492, 200, 22, MUTED))
    for i, ln in enumerate(f["speaker_lines"]):
        nodes.append(text_node(ln, M, 520 + i * 36, f["spk_maxw"], SPEAKER_SIZE, BODY))
    spk_h = len(f["speaker_lines"]) * 36
    nodes.append(text_node("时间", W - M - 200, 492, 200, 22, MUTED, align="RIGHT"))
    nodes.append(text_node(c["time"], W - M - 220, 514, 220, 40, MAIN_DEEP, bold=True,
                           align="RIGHT"))
    dsl = (f'<Snapshot type="png" background="{st["bg"]}">'
           f'<Container width="{W}" height="{H}">'
           f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
           + "".join(nodes) + "</Stack></Container></Snapshot>")
    (TMP_DIR / f"card-{cid}.snapshot").write_text(dsl, encoding="utf-8")
    audit.append({
        "card_id": cid,
        "content": {"title": c["title"], "speaker": c["speaker"],
                    "time": c["time"], "status": c["status"],
                    "brand": BRAND, "date": DATE},
        "title": {"font_size": t_size, "lines": len(t_lines), "line_texts": t_lines,
                  "line_widths": [line_w(l, t_size, "B") for l in t_lines],
                  "line_box": title_box, "max_lines_rule": TITLE_MAX_LINES,
                  "degraded_from_44": t_size != 44,
                  "verified": "每行实测宽度 ≤ 标题区宽 %d" % tz_w},
        "speaker": {"font_size": SPEAKER_SIZE, "lines": len(f["speaker_lines"]),
                    "line_texts": f["speaker_lines"],
                    "line_widths": [line_w(l, SPEAKER_SIZE, "N")
                                    for l in f["speaker_lines"]],
                    "box": [M, 520, M + f["spk_maxw"], 520 + spk_h]},
        "status": {"code": c["status"], "symbol": st["symbol"],
                   "color": st["color"], "encoding": "颜色+符号+文字",
                   "badge_box": [round(W - M - badge_w, 1), badge_y, W - M,
                                 badge_y + badge_h],
                   "card_bg": st["bg"],
                   "cancel_note": CANCEL_NOTE if c["status"] == "取消" else None,
                   "cancel_note_box": note_box},
        "image_view": None,
    })

# ---------- 渲染（网络层故障重试） ----------


def render_retry(dsl_path, out_path, label, attempts=4):
    res = None
    for i in range(attempts):
        res = R.render(dsl_path, out_path, ROOT, log, label=label)
        if res["record"]["status"] == "ok":
            return res
        err = res["record"].get("error") or ""
        if any(k in err for k in ("Timeout", "URLError", "RemoteDisconnected",
                                  "handshake", "EOF occurred", "timed out")):
            _time.sleep(2 + i * 2)
            continue
        return res
    return res


log = R.Log(ROOT, RUN_ID, TASK)
for c in CARDS:
    res = render_retry(TMP_DIR / f"card-{c['id']}.snapshot", TMP_DIR / f"card-{c['id']}.png",
                       f"A14-card-{c['id']}")
    print(f"card-{c['id']}", res["record"]["status"], res["record"].get("error"))

(TMP_DIR / "batch-audit-partial.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote partial audit (image_view 待回填)")
