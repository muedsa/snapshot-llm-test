"""A12 patch 1.

v001 renders showed three real problems that the estimator-based audit missed:
  * the "云构中心 · ONLINE" chip wrapped to two lines and spilled out of its pill on
    tablet/desktop/stage — the middle dot and the spaces around it are wider in
    Noto Sans CJK SC than the 0.55em assumed for non-CJK codepoints.
  * desktop emitted the CTA twice (top-right band and bottom band).
  * tablet/desktop/stage stacked everything from the top margin, leaving the bottom
    fifth of the canvas empty.
"""
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
p = ROOT / "tmp" / RUN / "A12" / "gen.py"
s = p.read_text(encoding="utf-8")
orig = s


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new, count)


# ---------------------------------------------------------------- width estimator
rep('''def adv(text, size):
    """Estimated rendered width: CJK and full-width punctuation take 1em, the rest 0.55em."""
    return sum(size * (1.0 if ord(ch) > 0x2E80 else 0.55) for ch in text)''',
    '''def adv(text, size):
    """Estimated rendered width.

    CJK ideographs take 1em. Latin, digits and punctuation take 0.62em, and the middle
    dot U+00B7 is measured at ~0.9em in Noto Sans CJK SC — v001 wrapped the location
    chip because it was treated as an ordinary narrow glyph.
    """
    return sum(size * (1.0 if ord(ch) > 0x2E80 else (0.9 if ch == "·" else 0.62))
               for ch in text)''')

# ---------------------------------------------------------------- chips get headroom
rep('''    xx = x + 18
    for k, v in meta:
        wchip = adv(v, s["meta"]) + 24''',
    '''    xx = x + 18
    for k, v in meta:
        wchip = adv(v, s["meta"]) * 1.06 + 24''')

# ---------------------------------------------------------------- desktop: one CTA
rep('''    els, y = hero(bp, m, m, cw - 470, stack_meta=False)
    # right-hand CTA on the same baseline as the hero
    els.extend(cta(bp, W - m - 440, m, 440, 96, inline_site=False))
    els.extend(footer_site(bp, W - m - 440, m + 108, 440))
    y = max(y, m + 136) + 26''',
    '''    els, y = hero(bp, m, top, cw - 470, stack_meta=False)
    els.extend(footer_site(bp, W - m - 440, top + 6, 440))
    y = max(y, top + 136) + 30''')
rep('''def build_desktop():
    bp = "desktop"
    W, H = BP[bp]["canvas"]
    m = BP[bp]["margin"]
    cw = W - 2 * m''',
    '''def build_desktop(top=32):
    bp = "desktop"
    W, H = BP[bp]["canvas"]
    m = BP[bp]["margin"]
    cw = W - 2 * m''')
rep('''    els.extend(cta(bp, m, bottom + 26, cw, 72, inline_site=True))
    return els''',
    '''    els.extend(cta(bp, m, bottom + 30, cw, 76, inline_site=True))
    return els''')

# ---------------------------------------------------------------- top offsets
rep('def build_mobile():\n    bp = "mobile"\n    W, H = BP[bp]["canvas"]\n    m = BP[bp]["margin"]\n    cw = W - 2 * m\n    els, y = hero(bp, m, m, cw, stack_meta=True)',
    'def build_mobile(top=16):\n    bp = "mobile"\n    W, H = BP[bp]["canvas"]\n    m = BP[bp]["margin"]\n    cw = W - 2 * m\n    els, y = hero(bp, m, top, cw, stack_meta=True)')
rep('def build_tablet():\n    bp = "tablet"\n    W, H = BP[bp]["canvas"]\n    m = BP[bp]["margin"]\n    cw = W - 2 * m\n    els, y = hero(bp, m, m, cw, stack_meta=False)',
    'def build_tablet(top=32):\n    bp = "tablet"\n    W, H = BP[bp]["canvas"]\n    m = BP[bp]["margin"]\n    cw = W - 2 * m\n    els, y = hero(bp, m, top, cw, stack_meta=False)')
rep('def build_stage():\n    bp = "stage"\n    W, H = BP[bp]["canvas"]\n    m = BP[bp]["margin"]\n    cw = W - 2 * m\n    els, y = hero(bp, m, m + 8, cw, stack_meta=False)',
    'def build_stage(top=40):\n    bp = "stage"\n    W, H = BP[bp]["canvas"]\n    m = BP[bp]["margin"]\n    cw = W - 2 * m\n    els, y = hero(bp, m, top, cw, stack_meta=False)')

# ---------------------------------------------------------------- vertical centring
rep('''problems = 0
docs = {}
for bp in ("mobile", "tablet", "desktop", "stage"):
    els = BUILD[bp]()
    problems += audit(bp, els)
    docs[bp] = doc(bp, els)
    (TMP_DIR / f"{a.ver}-{bp}.snapshot").write_text(docs[bp].render() + "\\n",
                                                    encoding="utf-8")''',
    '''problems = 0
docs = {}
CENTRE = {}
for bp in ("mobile", "tablet", "desktop", "stage"):
    m = BP[bp]["margin"]
    Hc = BP[bp]["canvas"][1]
    # pass 1: build at the margin to learn the natural block height
    BUILD[bp](m)
    bottom = max(b["y"] + b["h"] for b in BOXES[bp])
    off = max(0, (Hc - 2 * m - (bottom - m)) / 2)
    top = m + off
    CENTRE[bp] = {"margin_px": m, "natural_block_bottom_px": round(bottom, 1),
                  "block_height_px": round(bottom - m, 1),
                  "centring_offset_px": round(off, 1), "content_top_px": round(top, 1)}
    # pass 2: rebuild at the centred offset, dropping pass-1 records
    BOXES[bp] = []
    for i in range(len(CONTENT_MAP) - 1, -1, -1):
        if CONTENT_MAP[i]["canvas"] == bp:
            del CONTENT_MAP[i]
    els = BUILD[bp](top)
    problems += audit(bp, els)
    docs[bp] = doc(bp, els)
    (TMP_DIR / f"{a.ver}-{bp}.snapshot").write_text(docs[bp].render() + "\\n",
                                                    encoding="utf-8")''')
rep('''    "no_image_scaling": "四份 DSL 各自由同一生成器按各自画布重新排版生成；"''',
    '''    "vertical_distribution": CENTRE,
    "no_image_scaling": "四份 DSL 各自由同一生成器按各自画布重新排版生成；"''')

assert s != orig
p.write_text(s, encoding="utf-8")
print("patched 1")
