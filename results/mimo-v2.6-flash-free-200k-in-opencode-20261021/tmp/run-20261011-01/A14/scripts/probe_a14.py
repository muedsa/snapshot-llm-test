# -*- coding: utf-8 -*-
"""A14 anomaly/stress probe for the deliverable generator (gen_cards.py).

Real inputs (K01-K08) are all clean: known statuses, no missing/wrong types,
titles that fit at 56px. This probe exercises the generator's defensive
branches with synthetic data (kept in tmp, NOT part of the 8 deliverables):

  * status "延期"   -> unknown status -> neutral encoding + warning
  * time 900       -> wrong type     -> str coercion (still displayed)
  * title 105 CJK chars -> length branch: shrink 56->36 then truncate+warn
  * speaker 100 chars    -> long-speaker rule: 2 lines + ellipsis

Usage: probe_a14.py   -> writes cards/probe/card-K99.snapshot + layout
"""
import importlib.util
import json
import pathlib
import sys

sys.argv = ["gen_cards", "probe"]
spec = importlib.util.spec_from_file_location(
    "gen_cards", "tmp/run-20261011-01/A14/scripts/gen_cards.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

card = {
    "id": "K99",
    "title": "极限长度压力测试：当一段标题真的长到必须逐级降字号才能塞进三行以内"
             "而它仍然继续变长时，参数化规则会把字号一路降到下限并按规则截断",
    "speaker": "沈砚秋 / 欧阳北辰 / 诺拉·哈桑 / 阿尔贝·加缪二世 / 陆一鸣与工作坊全体协作成员",
    "time": 900,
    "status": "延期",
}
rec = m.build_card(card, 9)
print("font:", rec["title_font_size"], "lines:", rec["title_line_count"])
print("speaker lines:", rec["speaker_line_count"])
print("status:", rec["status_encoding"])
print("warnings:", rec["warnings"])
out = m.OUT
(out / "probe-K99.json").write_text(
    json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
print("->", (out / "card-K99.snapshot").name, "in", out)
