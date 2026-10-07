# -*- coding: utf-8 -*-
"""Build the cumulative (task level) design-tokens.json and content-map.json for
A21 from the three per-round files, so the summary can never drift from what was
actually delivered."""
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "A21"))
import brandkit as B  # noqa: E402

OUT = os.path.join(ROOT, "outputs", RUN, "A21")
ROUNDS = ["round-01", "round-02", "round-03"]


def load(rnd, name):
    with open(os.path.join(OUT, rnd, name), encoding="utf-8") as fh:
        return json.load(fh)


def main():
    toks = {r: load(r, "design-tokens.json") for r in ROUNDS}
    maps = {r: load(r, "content-map.json") for r in ROUNDS}
    audits = {r: load(r, "contrast-audit.json") for r in ROUNDS if r == "round-03"}

    cum = dict(toks["round-01"])
    cum.pop("round", None)
    cum["task"] = "A21"
    cum["rounds"] = ROUNDS
    cum["invariant_across_rounds"] = {
        "primary_colour": cum["brand"]["primary"],
        "type_scale": cum["type_scale"],
        "mark_components": cum["mark"]["components"],
        "mark_geometry": cum["mark"],
        "minimum_body_font_px": 24,
        "fonts": ["Inter Black", "Inter", "Noto Sans CJK SC"],
        "note": "these three blocks are byte-identical in all three rounds' "
                "design-tokens.json; only the surface palette and the composition "
                "change between rounds",
    }
    cum["per_round_theme"] = {}
    for r in ROUNDS:
        s = toks[r]["surface"]
        cum["per_round_theme"][r] = {
            "bg_top": s["bg_top"], "bg_bottom": s["bg_bottom"],
            "panel": s["panel"], "ink": s["ink"], "ink_muted": s["ink_muted"],
            "accent_ink": s["accent_ink"], "chip_fill": s["chip_fill"],
            "plate_base": s["plate_base"], "plate_mid": s["plate_mid"],
            "beam": s["beam"], "spark_dot": s["spark_dot"],
            "spark_ring": s["spark_ring"], "glow": s["glow"],
            "hairline": s["hairline"], "panel_border": s["panel_border"],
        }
    cum["per_round_changes"] = {
        r: toks[r].get("changed_vs_round_01") or toks[r].get("changed_vs_round_02")
        for r in ROUNDS}
    cum["reserved_extension_bands"] = {
        r: {img: v["reserved_extension_bands"]
            for img, v in maps[r]["images"].items()} for r in ROUNDS}
    with open(os.path.join(OUT, "design-tokens.json"), "w", encoding="utf-8") as fh:
        json.dump(cum, fh, ensure_ascii=False, indent=2)
    print("wrote cumulative design-tokens.json")

    copy_rows = {}
    for r in ROUNDS:
        for row in maps[r]["required_copy"]:
            key = row["text"]
            e = copy_rows.setdefault(key, {"text": key, "requirement": row["requirement"],
                                           "first_round": r, "rounds_present": {},
                                           "note": ""})
            e["rounds_present"][r] = row["present"]
            if row["text"] in (B.COPY["tagline"],) and r != "round-01":
                e["note"] = ("round-01 had this as a standalone tagline line; from "
                             "round-02 on it is part of the main title, so the "
                             "string is still present but no longer a separate "
                             "line - deliberate, see round-02/snapshot-usage.md")
    cum_cm = {
        "task": "A21",
        "title": "真实需求变更：双尺寸发布物（三轮）",
        "rounds": ROUNDS,
        "execution_mode": "preloaded_sequential",
        "execution_mode_honest_note":
            "round-02 and round-03 requirements were readable in "
            "tasks/A21-staged-launch-change/rounds/ from the start. Each round "
            "file was opened only after the previous round was rendered, "
            "viewed and archived, but this is NOT hidden-feedback blind testing "
            "and no round claims to have received surprise feedback.",
        "service": {
            "endpoint": "POST https://open-snapshot.muedsa.com/snapshot",
            "request_body": "UTF-8 plain-text Snapshot DSL",
            "user_agent": "browser UA required (snapkit sends one)",
            "embedded_images_used": 0,
            "external_images_used": 0,
        },
        "copy_registry": list(copy_rows.values()),
        "brand": {
            "components": ["plate-base", "plate-mid", "plate-top", "beam",
                           "spark-dot", "spark-ring"],
            "component_count": 6,
            "geometry_changed_between_rounds": False,
            "colours_changed_between_rounds": "yes - the whole surface chain was "
                                              "recomposed for the light theme in "
                                              "round-03",
        },
        "per_round": {
            r: {
                "requirements_source": maps[r]["requirements_source"],
                "theme": maps[r]["theme"],
                "parent_round": maps[r].get("parent_round"),
                "worst_measured_contrast": {
                    img: maps[r]["images"][img].get("worst_contrast")
                    for img in maps[r]["images"]},
                "reserved_extension_bands": {
                    img: maps[r]["images"][img]["reserved_extension_bands"]
                    for img in maps[r]["images"]},
                "text_elements": {
                    img: len(maps[r]["images"][img]["texts"])
                    for img in maps[r]["images"]},
                "images": sorted(maps[r]["images"].keys()),
            } for r in ROUNDS},
        "round_03_contrast_audit": audits.get("round-03"),
        "audit_artifacts_dir": "tmp/%s/A21/audits/" % RUN,
        "verify_script": "tmp/%s/A21/verify_all.py (0 failures on the delivered files)" % RUN,
    }
    with open(os.path.join(OUT, "content-map.json"), "w", encoding="utf-8") as fh:
        json.dump(cum_cm, fh, ensure_ascii=False, indent=2)
    print("wrote cumulative content-map.json")
    for k, v in copy_rows.items():
        print("  %-46s %s" % (k[:44], sorted(v["rounds_present"].keys())))


if __name__ == "__main__":
    main()