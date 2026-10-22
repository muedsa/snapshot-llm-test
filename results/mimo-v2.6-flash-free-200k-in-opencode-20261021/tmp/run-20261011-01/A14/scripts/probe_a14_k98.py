# -*- coding: utf-8 -*-
"""A14 probe K98: extreme long title -> forces shrink-to-min + truncation.

Exercises the truncation branch of fit_title (K99 probe stopped at 38px
without truncating). Same generator code as the deliverables (gen_cards.py),
synthetic record only; evidence for the defensive length branch.
"""
import importlib.util
import json
import sys

sys.argv = ["gen_cards", "probe"]
spec = importlib.util.spec_from_file_location(
    "gen_cards", "tmp/run-20261011-01/A14/scripts/gen_cards.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

card = {
    "id": "K98",
    "title": "极限截断验证：" + "这一段文字不断重复以确保标题无论如何都放不进三行以内" * 4,
    "speaker": "沈砚秋",
    "time": "16:40",
    "status": "开放",
}
rec = m.build_card(card, 9)
print("font:", rec["title_font_size"], "lines:", rec["title_line_count"])
print("last line tail:", repr(rec["displayed_title"].splitlines()[-1][-12:]))
print("warnings:", rec["warnings"])
m.OUT.joinpath("probe-K98.json").write_text(
    json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
print("->", m.OUT)
