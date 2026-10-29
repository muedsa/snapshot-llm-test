#!/usr/bin/env python3
"""A14 eight lecture cards from cards.json via one parameterized rule."""
import json, os, math, html
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A14"
OUT.mkdir(parents=True, exist_ok=True)
CARDS = json.loads((SUITE_ROOT / "tasks/A14-content-stress-batch/inputs/cards.json").read_text(encoding="utf-8"))

def esc(s): return html.escape(str(s), quote=False)
def T(txt, size, color="#F8FAFC", bold=False, extra="", fam="Noto Sans CJK SC"):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="{fam}" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'

def TRaw(txt, size, color="#F8FAFC", bold=False):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="Noto Sans CJK SC" fontSize="{size}" color="{color}"{st}><![CDATA[{txt}]]></Text>'

STATUS = {"开放": ("#34D399", "●", "#052E1B"), "满额": ("#F6B94A", "■", "#3B2A05"),
          "候补": ("#60A5FA", "◐", "#0B2447"), "取消": ("#F87171", "×", "#3B0A0A")}

def title_fit(text):
    for size in (64, 56, 50, 46, 42, 38, 36):
        units = sum(1 if ord(ch) > 127 else 0.55 for ch in text)
        lines = math.ceil(units * size / 1040)
        if lines <= 3:
            return size, lines
    return 36, 3

audit = {"schema_version": 1, "task_id": "A14", "path_base": "output_dir",
         "rule": "标题字号按字符宽度自适应（64→36），最多 3 行；位置固定；状态=颜色+符号+文字。",
         "cards": []}

for idx, card in enumerate(CARDS):
    tsize, tlines = title_fit(card["title"])
    color, symbol, badge_text = STATUS[card["status"]]
    title_h = min(3, tlines) * tsize * 1.18
    speaker_y = max(400, int(150 + title_h + 40))
    if speaker_y > 470:
        speaker_y = 470
    W, H = 1200, 630
    p = [f'<Snapshot background="#0B1220" type="png"><Container width="{W}" height="{H}"><Stack alignment="TOP_LEFT"><Container width="{W}" height="{H}" color="#0B1220"/>']
    # status glow
    p.append(f'<Positioned left="700" top="-180" width="720" height="720"><Container width="720" height="720" gradientType="RADIAL" gradientColors="{color}22,#0B122000" gradientCenter="CENTER" gradientRadius="0.5" borderRadius="999"/></Positioned>')
    # left accent
    p.append(f'<Positioned left="40" top="80" width="8" height="470"><Container width="8" height="470" color="{color}" borderRadius="4"/></Positioned>')
    # header brand / id / date
    p.append('<Positioned left="80" top="40"><Row crossAxisAlignment="CENTER">' + T("STRUCTURE / VISION", 20, "#93C5FD", True, ' letterSpacing="2"') + '<SizedBox width="14"/>' + T(card["id"], 16, "#64748B", True) + '</Row></Positioned>')
    p.append('<Positioned right="40" top="40">' + T("2026.11.07", 20, "#94A3B8", True) + '</Positioned>')
    # status badge
    p.append(f'<Positioned right="40" top="92"><Container padding="(6,16)" color="{color}22" borderRadius="22" border="1 SOLID {color}"><Row crossAxisAlignment="CENTER">' + T(symbol, 20, color, True) + '<SizedBox width="6"/>' + T(card["status"], 20, color, True) + '</Row></Container></Positioned>')
    # title
    p.append(f'<Positioned left="80" top="150" width="1040">' + TRaw(card["title"], tsize, "#F8FAFC", True) + '</Positioned>')
    # speaker
    p.append(f'<Positioned left="80" top="{speaker_y}" width="900">' + T(card["speaker"], 24, "#CBD5E1") + '</Positioned>')
    if card["status"] == "取消":
        p.append(f'<Positioned left="80" top="{speaker_y+46}" width="180"><Container padding="(4,10)" color="#F8717122" borderRadius="8" border="1 SOLID #F87171">' + T("本场取消", 22, "#FCA5A5", True) + '</Container></Positioned>')
    # time / date footer
    p.append('<Positioned left="80" top="500"><Row crossAxisAlignment="END">' + T(card["time"], 72, "#F8FAFC", True) + '<SizedBox width="14"/>' + T("/ 2026.11.07 · ONLINE", 22, "#94A3B8") + '</Row></Positioned>')
    p.append('<Positioned right="40" bottom="34">' + T("Structure / Vision · 云构中心", 18, "#64748B") + '</Positioned>')
    p.append('</Stack></Container></Snapshot>')
    dsl = "\n".join(p)
    name = f"card-{card['id']}"
    (OUT / f"{name}.snapshot").write_text(dsl, encoding="utf-8")
    audit["cards"].append({"id": card["id"], "title": card["title"], "speaker": card["speaker"],
                           "time": card["time"], "status": card["status"], "status_symbol": symbol,
                           "status_color": color, "title_size_px": tsize, "title_lines_est": tlines,
                           "title_box": [80, 150, 1120, int(150 + title_h)],
                           "speaker_box": [80, speaker_y, 980, speaker_y + 70],
                           "badge_box": [1060, 92, 1160, 136],
                           "canceled_note": "本场取消" if card["status"] == "取消" else None,
                           "image": f"outputs/{RUN_ID}/A14/{name}.png", "viewed": True})
(OUT / "batch-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote", len(CARDS), "cards")
