# -*- coding: utf-8 -*-
"""Patch gen_cards.py: center-align the four pill texts."""
import pathlib

p = pathlib.Path('tmp/run-20261011-01/A14/scripts/gen_cards.py')
s = p.read_text(encoding='utf-8')
reps = [
    ('''    els.append(text_el(ib[0], ib[1] + 6, ib[2] - ib[0], 30, P["index_size"],
                       P["primary"], cid, font=MONO))''',
     '''    els.append(text_el(ib[0], ib[1] + 6, ib[2] - ib[0], 30, P["index_size"],
                       P["primary"], cid, font=MONO, align="CENTER"))'''),
    ('''    els.append(text_el(P["time_x"], P["bottom_y"] + 8, time_w, 32, 24,
                       "#E2E8F0", time_, font=MONO))''',
     '''    els.append(text_el(P["time_x"], P["bottom_y"] + 8, time_w, 32, 24,
                       "#E2E8F0", time_, font=MONO, align="CENTER"))'''),
    ('''    els.append(text_el(badge_x, P["bottom_y"] + 8, badge_w, 32, 24,
                       s_hex, badge_text))''',
     '''    els.append(text_el(badge_x, P["bottom_y"] + 8, badge_w, 32, 24,
                       s_hex, badge_text, align="CENTER"))'''),
    ('''        els.append(text_el(ann_x, P["bottom_y"] + 8, ann_w, 32, 24,
                           "#450A0A", "✕ " + ann_text, bold=True))''',
     '''        els.append(text_el(ann_x, P["bottom_y"] + 8, ann_w, 32, 24,
                           "#450A0A", "✕ " + ann_text, bold=True,
                           align="CENTER"))'''),
]
for old, new in reps:
    assert s.count(old) == 1, 'not unique: ' + old[:70]
    s = s.replace(old, new)
p.write_text(s, encoding='utf-8')
print('4 alignments patched')
