import json
import pathlib

a = json.loads(pathlib.Path("outputs/run-20261011-01/A14/batch-audit.json").read_text(encoding="utf-8"))
print("all_passed:", a["all_passed"])
print("keys:", list(a.keys()))
print("cards:", len(a["cards"]), " reviews:", len(a["reviews"]))
for c in a["cards"]:
    t = c["title_typography"]
    m = c["measured"]
    print(f"{c['id']} {t['font_size_px']}px x{t['lines']}行 "
          f"status={c['source_fields']['status']} "
          f"gap={m['title_badge_gap_px']}px safe={m['within_safe_margin']} "
          f"pass={m['passed']} | {t['branch'][:38]}")
print()
print("text_fidelity all_equal:", a["verification"]["text_fidelity"]["all_equal_ignoring_spaces"])
print("review final ids:", a["review_summary"]["final_card_ids_viewed"])
print("length branches:", a["generation"]["length_branches_taken"])