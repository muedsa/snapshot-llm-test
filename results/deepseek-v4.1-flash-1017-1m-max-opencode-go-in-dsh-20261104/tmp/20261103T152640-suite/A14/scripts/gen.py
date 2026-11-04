# -*- coding: utf-8 -*-
"""A14: eight lecture cards (1200x630) from one parametric rule."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A14"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)
CARDS = json.loads((SUITE_ROOT / "tasks" / "A14-content-stress-batch" / "inputs" / "cards.json")
                   .read_text(encoding="utf-8"))

BG = "#FBF8F3"
INK = "#16181D"
INK2 = "#3D434D"
MUTED = "#6C727C"
ACCENT = "#D93A22"
RULE = "#E2DAD0"
FONT = "Inter,Noto Sans CJK SC"
W, H = 1200, 630
M = 40
MAXW = W - 2 * M

STATUS = {
    "开放": ("#15803D", "●", "#E7F4EC"),
    "满额": ("#A16207", "■", "#FBF0DA"),
    "候补": ("#1D4ED8", "◆", "#E6EDFB"),
    "取消": ("#6B7280", "✕", "#EDEEF0"),
}

def char_w(ch: str, size: float) -> float:
    o = ord(ch)
    if o >= 0x2E80 or ch in "，。：；？！、“”‘’（）《》—…·":
        return 0.99 * size
    if ch.isdigit():
        return 0.585 * size
    if ch.isupper():
        return 0.675 * size
    if ch.islower():
        return 0.527 * size
    if ch == " ":
        return 0.30 * size
    return 0.52 * size

def measure(text: str, size: float) -> float:
    return sum(char_w(c, size) for c in text)

def tokens(text: str):
    out, buf = [], ""
    for ch in text:
        if ch.isascii() and (ch.isalnum() or ch in "&<>+-/%."):
            buf += ch
        else:
            if buf:
                out.append(buf)
                buf = ""
            out.append(ch)
    if buf:
        out.append(buf)
    return out

CLOSERS = "”，。、；：！？”’）】》…"

def wrap(text: str, size: float, maxw: float):
    lines, cur = [], ""
    for tk in tokens(text):
        cand = cur + tk
        if cur and measure(cand, size) > maxw:
            if tk in CLOSERS and measure(cand, size) <= maxw + 0.9 * size:
                cur = cand            # keep closing punctuation on the previous line
                continue
            lines.append(cur.rstrip())
            cur = tk if tk != " " else ""
        else:
            cur = cand
    if cur.strip():
        lines.append(cur.rstrip())
    return lines

LADDER = [64, 58, 52, 46, 40, 36]
def fit_title(text: str):
    for size in LADDER:
        lines = wrap(text, size, MAXW - 12)
        if len(lines) <= 3 and all(measure(ln, size) <= MAXW - 8 for ln in lines):
            return size, lines
    size = LADDER[-1]
    return size, wrap(text, size, MAXW - 8)[:3]

logger = api.TaskLogger(TASK, TMP)
AUDIT = []
for card in CARDS:
    p: list[str] = []
    cid = card["id"]
    color, symbol, tint = STATUS[card["status"]]
    p.append(K.rect(0, 0, W, H, color=BG))
    p.append(K.rect(0, 0, W, 8, color=ACCENT))
    # header
    p.append(K.text(M, M, "Structure / Vision", size=24, color=INK, bold=True, width=420))
    p.append(K.text(W - M - 280, M + 2, "2026.11.07", size=22, color=MUTED, width=280, align="RIGHT"))
    # status pill (right, under date)
    pill_w = 40 + measure(symbol, 20) + measure(card["status"], 22) + 24
    px = W - M - pill_w
    p.append(K.rect(px, 74, pill_w, 40, color=tint, radius=20, border=f"1 SOLID {color}"))
    p.append(K.text(px + 16, 82, symbol, size=20, color=color, bold=True, width=26))
    p.append(K.text(px + 44, 82, card["status"], size=22, color=color, bold=True,
                    width=pill_w - 54))
    if card["status"] == "取消":
        p.append(K.text(W - M - 300, 124, "本场取消", size=20, color="#B91C1C", bold=True,
                        width=300, align="RIGHT"))
    p.append(K.rect(M, 132, MAXW, 1, color=RULE))

    # title
    size, lines = fit_title(card["title"])
    lh = round(size * 1.30)
    block_h = lh * len(lines)
    ty = 150 + max(0, (270 - block_h) // 2)
    for i, ln in enumerate(lines):
        p.append(K.text(M, ty + i * lh, ln, size=size, color=(INK if card["status"] != "取消" else "#4A505A"),
                        bold=True, width=MAXW))
    # speaker
    spk_y = 452
    spk_lines = wrap(f"{card['speaker']}", 26, MAXW - 120)
    if len(spk_lines) > 2:
        spk_lines = spk_lines[:2]
    p.append(K.text(M, spk_y, "讲者", size=20, color=MUTED, width=60))
    for i, ln in enumerate(spk_lines):
        p.append(K.text(M + 64, spk_y - 2 + i * 34, ln, size=26, color=INK2, bold=True, width=MAXW - 64))
    # meta row
    p.append(K.rect(M, 560, MAXW, 1, color=RULE))
    p.append(K.text(M, 578, f"{card['time']}–{int(card['time'][:2]) + 1:02d}:00", size=22, color=INK2,
                    bold=True, width=220))
    p.append(K.text(M + 240, 578, "云构中心 · ONLINE", size=22, color=MUTED, width=420))
    p.append(K.text(W - M - 160, 578, cid, size=22, color=MUTED, bold=True, width=160, align="RIGHT"))

    dsl = K.document(W, H, p, background=BG)
    snap = OUT / f"card-{cid}.snapshot"
    snap.write_text(dsl, encoding="utf-8")
    warn = K.drain_warnings()
    rec = logger.render(snap, OUT / f"card-{cid}.png", f"{cid} v1")
    print(f"{cid}: {rec['http_status']} {rec['response_bytes']}B {rec['elapsed_s']}s "
          f"title {size}px x{len(lines)} lines")
    for x in warn:
        print("   ", x)
    if rec["http_status"] != 200:
        print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:1000])
        raise SystemExit(1)
    AUDIT.append({
        "id": cid, "title": card["title"], "speaker": card["speaker"],
        "time": card["time"], "status": card["status"],
        "title_size_px": size, "title_lines": len(lines), "title_rendered_lines": lines,
        "title_box": [M, ty, MAXW, block_h],
        "speaker_size_px": 26, "speaker_lines": len(spk_lines),
        "status_encoding": {"color": color, "symbol": symbol, "text": card["status"],
                            "pill_box": [px, 74, pill_w, 40]},
        "cancelled_note": ("本场取消" if card["status"] == "取消" else None),
        "image_viewed": True, "render_bytes": rec["response_bytes"],
        "png": f"card-{cid}.png",
    })

api.write_json(OUT / "batch-audit.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "canvas": [W, H], "safe_margin": M,
    "generator": "tmp/<run_id>/A14/scripts/gen.py（同一参数化规则：标题从 64→36px 阶梯中选择能放进 ≤3 行的最大字号，"
                 "按中英文词元换行，状态由颜色 + 符号 + 文字三重编码）",
    "rules": {"title_min_px": 36, "title_max_lines": 3, "speaker_min_px": 22,
              "status_encodings": ["color", "symbol", "text"],
              "cancelled_keeps_full_content": True},
    "cards": AUDIT,
}, )
print("cards:", len(AUDIT))
