"""A14 · 8-up lecture card batch from one parameterized rule."""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A14"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Pos, Row, SizedBox, Stack, T  # noqa: E402

W, H, M = 1200, 630, 40
BG = "#0B1220"
INK = "#F8FAFC"
MUTED = "#93A6C2"
FAINT = "#5F7290"
CORAL = "#F97362"
LINE = "#22314B"
STATUS = {
    "开放": ("#34D399", "#0E2A24", "●"),
    "满额": ("#F5C451", "#2A2412", "■"),
    "候补": ("#60A5FA", "#12233A", "◐"),
    "取消": ("#F87171", "#2A1418", "×"),
}
TITLE_W = 880


def Tattr(raw, size, color=INK, family="Inter,Noto Sans CJK SC", weight="BOLD", **kw):
    attrs = [f'text="{raw}"', f'fontSize="{size}"', f'color="{color}"', f'fontFamily="{family}"']
    if weight:
        attrs.append(f'fontStyle="{weight}"')
    for k, v in kw.items():
        attrs.append(f'{k}="{v}"')
    return "<Text " + " ".join(attrs) + " />"


def char_em(ch):
    if ch in "，。；：、！？（）《》“”‘’—…":
        return 0.95
    if ch == " ":
        return 0.32
    if ord(ch) < 128:
        return 0.62
    return 1.0


def text_em(t):
    return sum(char_em(c) for c in t)


def segments(title):
    out, buf = [], ""
    i = 0
    while i < len(title):
        ch = title[i]
        buf += ch
        if ch in "，。；：、！？":
            out.append(buf); buf = ""
        elif ch == "—" and i + 1 < len(title) and title[i + 1] == "—":
            buf += "—"; out.append(buf); buf = ""; i += 1
        elif ch == "”":
            out.append(buf); buf = ""
        elif ch == " " and i > 0 and title[i - 1] == "/":
            out.append(buf); buf = ""
        i += 1
    if buf:
        out.append(buf)
    return out


def fit_lines(title):
    for size in (72, 64, 56, 48, 40, 36):
        # one line if it fits
        if text_em(title) * size <= TITLE_W:
            return size, [title]
        lines, cur = [], ""
        ok = True
        for seg in segments(title):
            if text_em(seg) * size > TITLE_W:
                ok = False
                break
            if not cur:
                cur = seg
            elif (text_em(cur) + text_em(seg)) * size <= TITLE_W:
                cur += seg
            else:
                lines.append(cur)
                cur = seg
        if cur:
            lines.append(cur)
        if ok and len(lines) <= 3:
            return size, lines
    # fallback: keep title whole at min size (should not happen)
    return 36, [title]


def make_card(card):
    cid = card["id"]
    color, sbg, sym = STATUS[card["status"]]
    cancelled = card["status"] == "取消"
    size, title_lines = fit_lines(card["title"])
    lh = size * 1.16
    title_h = len(title_lines) * lh + 6
    bg = "#150D13" if cancelled else BG
    nodes = [SizedBox(W, H),
             Pos(0, 0, C(width=W, height=H, gradientType="LINEAR", gradientColors=bg + ",#101E33",
                         gradientBegin="TOP_LEFT", gradientEnd="BOTTOM_RIGHT"))]
    for i in range(8):
        nodes.append(Pos(60 + i * 150, 0, C(width=1, height=H, color="#142136")))
    nodes.append(Pos(0, 0, C(width=8, height=H, color=color)))
    nodes += [
        Pos(M, 34, T("STRUCTURE / VISION", size=14, color=CORAL, weight="BOLD", family="Inter", spacing=3)),
        Pos(920, 35, T("2026.11.07", size=15, color=MUTED, family="Inter", spacing=1)),
        Pos(940, 80, C(width=220, height=48, color=sbg, borderRadius=24, border=f"1 SOLID {color}",
                       alignment="CENTER", child=Row([T(sym, size=18, color=color, family="Inter"),
                                                       HGap(8), T(card["status"], size=18, color=color, weight="BOLD")]))),
        Pos(975, 382, T(cid, size=100, color="#142033", weight="BOLD", family="DejaVu Sans Mono"), w=190, h=130),
        Pos(80, 150, Col([Tattr(line, size=size, color=INK, max_lines="1", height="1.12") for line in title_lines],
                         crossAxisAlignment="START"), w=TITLE_W, h=title_h),
        Pos(80, 456, T("讲者 / SPEAKER", size=13, color=FAINT, weight="BOLD", family="Inter", spacing=2)),
        Pos(80, 478, T(card["speaker"], size=26, color=INK, max_lines=2), w=760, h=70),
        Pos(980, 456, T("TIME", size=13, color=FAINT, weight="BOLD", family="Inter", spacing=2)),
        Pos(980, 476, T(card["time"], size=44, color=color, weight="BOLD", family="Inter"), w=160, h=60),
        Pos(80, 560, C(width=1080, height=1, color=LINE)),
        Pos(80, 570, T("Structure / Vision · 2026.11.07 · 讲座系列", size=14, color=FAINT)),
        Pos(990, 570, T(f"{cid} / 08", size=13, color=FAINT, family="Inter", spacing=1)),
    ]
    if cancelled:
        nodes += [
            Pos(80, 400, T("× 本场取消 · 仍保留完整标题与时间", size=16, color=color, weight="BOLD")),
            Pos(0, 0, C(width=W, height=4, color=color)),
        ]
    return f'<Snapshot type="png" background="{BG}">\n' + Stack(nodes, width=W, height=H) + "\n</Snapshot>\n", size, title_lines, title_h


def main() -> int:
    cards = json.loads((ROOT / "tasks" / "A14-content-stress-batch" / "inputs" / "cards.json").read_text(encoding="utf-8"))
    (TMP / "dsl").mkdir(parents=True, exist_ok=True)
    (TMP / "renders").mkdir(parents=True, exist_ok=True)
    audit = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
             "generation": {"script": "tmp/%s/A14/scripts/generate_a14.py" % RUN,
                            "rule": "title size ladder 72/64/56/48/40/36, conservative 1em per char, width 880, max 3 lines; status map shared; cancelled adds note and red band",
                            "title_width": TITLE_W, "status_map": {k: {"color": v[0], "bg": v[1], "symbol": v[2]} for k, v in STATUS.items()},
                            "safe_margin": M},
             "cards": [], "reviews": []}
    for card in cards:
        dsl, size, title_lines, title_h = make_card(card)
        (TMP / "dsl" / f"{card['id']}-{VERSION}.snapshot").write_text(dsl, encoding="utf-8")
        audit["cards"].append({
            "id": card["id"], "original": card, "actual": card,
            "png": f"card-{card['id']}.png", "dsl": f"card-{card['id']}.snapshot",
            "title": card["title"], "title_size": size, "title_lines": len(title_lines), "title_line_texts": title_lines, "max_lines": 3,
            "title_box": [80, 150, 80 + TITLE_W, 150 + title_h],
            "speaker_box": [80, 478, 840, 550], "speaker_size": 26,
            "time_box": [980, 476, 1140, 536], "time_size": 44,
            "status": card["status"], "status_encoding": {"color": STATUS[card["status"]][0],
                                                          "symbol": STATUS[card["status"]][2],
                                                          "text": card["status"]},
            "cancelled_note": ("× 本场取消 · 仍保留完整标题与时间" if card["status"] == "取消" else None),
            "safe_margins": {"left": 40, "top": 34, "right": 40, "bottom": 40},
            "views": [],
        })
    (TMP / "batch-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print("A14", VERSION, "built", [(c["id"], c["title_size"], c["title_lines"], c["title_line_texts"]) for c in audit["cards"]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
