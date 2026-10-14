"""Append the logged B06 plan deviations to work-plan.json (criteria left untouched)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fp = ROOT / "work-plan.json"
plan = json.loads(fp.read_text(encoding="utf-8"))
import importlib.util
spec = importlib.util.spec_from_file_location("md", ROOT / "make_docs.py")
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
    devs = mod.DEVIATIONS
except SystemExit:
    devs = None
if not devs:
    raise SystemExit("could not read DEVIATIONS")
plan["deviations_logged_after_delivery"] = devs
plan["note_on_deviations"] = (
    "以上偏差在定稿后登记，原始验收标准保持写于第一次渲染之前的文本，未回改。")
fp.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("work-plan.json: criteria kept, deviations appended")
