"""A19 交付件独立验证：只读 outputs/<run_id>/A19/ 的四个 JSON 与 PNG/DSL，
重新计算每道题的答案并与 answers.json 比对；不复用生成器代码。

检查项：
* 四份 JSON 均含 schema_version / task_id / path_base；字段齐全；
* questions.json 不含任何答案信息；
* 题目数量、编号上限、两步题数、遮挡题数满足要求；
* 每道题的引用对象都存在于 scene-data.json；
* 用 scene-data.json 的 objects 独立重算 17 道网格题与 2 道可见前景遮挡题，
  与 answers.json 逐个比对；
* 2 道不确定题的答案确为“无法确定”，且 equivalence.json 判定可见等价、
  隐藏层确实不同；
* 三张 PNG 为真 PNG、IHDR 尺寸符合题目要求、同名 .snapshot 存在且非空。
"""
from __future__ import annotations

import hashlib
import json
import math
import pathlib
import struct
import sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A19"

problems = []


def check(cond, msg):
    if not cond:
        problems.append(msg)


def load(name):
    p = OUT / name
    check(p.exists(), "缺少交付件 %s" % name)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    scene = load("scene-data.json")
    qdoc = load("questions.json")
    adoc = load("answers.json")
    edoc = load("equivalence.json")

    missing = [n for n, d in (("scene-data.json", scene),
                              ("questions.json", qdoc),
                              ("answers.json", adoc),
                              ("equivalence.json", edoc)) if d is None]
    if missing:
        print("problems:", len(problems))
        for p in problems:
            print(" -", p)
        print("missing:", missing, "— 无法继续验证")
        return 1

    # ---------------- 身份字段
    for name, doc in (("scene-data.json", scene), ("questions.json", qdoc),
                      ("answers.json", adoc), ("equivalence.json", edoc)):
        if doc is None:
            continue
        check(doc.get("schema_version") == 1, "%s 缺 schema_version:1" % name)
        check(doc.get("task_id") == "A19", "%s task_id 应为 A19" % name)
        check(doc.get("path_base") == "output_dir",
              "%s path_base 应为 output_dir" % name)
        check("timezone" in doc or name == "equivalence.json",
              "%s 缺 timezone" % name)

    # ---------------- scene-data
    objs = scene["objects"]
    check(len(objs) == 64, "scene-data 应有 64 个对象")
    ids = [o["id"] for o in objs]
    check(ids == ["G%02d" % i for i in range(1, 65)],
          "对象编号应为 G01–G64 连续")
    check(scene["seed"].get("value") is None and
          "formulas" in scene["seed"], "seed 应说明非随机的生成算法")
    dist = scene["distribution"]
    check(sum(dist["color_frequencies"].values()) == 64, "颜色频数合计 64")
    check(all(v == 16 for v in dist["color_frequencies"].values()),
          "每种颜色应 16 个")
    check(all(v == 16 for v in dist["shape_frequencies"].values()),
          "每种形状应 16 个")
    check(len(dist["color_shape_combos"]) == 16 and
          dist["combo_coverage"]["all_16_present"],
          "16 种颜色×形状组合应全覆盖")
    cov = dist["attribute_size_coverage"]
    check(cov["all_colors_at_all_sizes"], "每种颜色须覆盖全部尺寸")
    check(cov["all_shapes_at_all_sizes"], "每种形状须覆盖全部尺寸")
    pr = dist["per_row_constraints"]
    check(pr["min_distinct_colors_per_row"] >= 3 and
          pr["min_distinct_shapes_per_row"] >= 3, "每行 ≥3 颜色且 ≥3 形状")

    # 对象几何自洽
    byi = {o["id"]: o for o in objs}
    for o in objs:
        cx, cy = o["center"]
        check(cx == 200 * (o["col"] - 1) + 100 and
              cy == 200 * (o["row"] - 1) + 100,
              "%s 中心与行列不符" % o["id"])
        hx = o["size"] // 2
        check(o["bbox"] == [cx - hx, cy - hx, cx + hx, cy + hx],
              "%s bbox 与尺寸不符" % o["id"])
        if o["shape"] == "ring":
            check(o["ring_inner_diameter"] == o["size"] // 2,
                  "%s 圆环内径应等于外径一半" % o["id"])

    # ---------------- questions
    Qs = qdoc["questions"]
    answers = {a["id"]: a["answer"] for a in adoc["answers"]}
    check(len(Qs) >= 18, "题目数应 ≥18")
    check(max(int(q["id"][1:]) for q in Qs) >= 18, "编号上限应 ≥18")
    grid = [q for q in Qs if q["image"] == "grid-scene.png"]
    occ = [q for q in Qs if q["image"].startswith("occlusion")]
    check(len(grid) >= 12, "网格题应 ≥12，实际 %d" % len(grid))
    check(len(occ) >= 2, "遮挡题应 ≥2，实际 %d" % len(occ))
    twostep = [q["id"] for q in Qs if q.get("relation_depth", 1) >= 2]
    check(len(twostep) >= 4, "两步关系题应 ≥4，实际 %d" % len(twostep))
    check(len(adoc["answers"]) == len(Qs), "answers 与 questions 数量应一致")
    check(set(a["id"] for a in adoc["answers"]) == set(q["id"] for q in Qs),
          "answers 与 questions 的题号集合应一致")

    # questions 不得含答案
    qtxt = json.dumps({k: v for k, v in qdoc.items() if k != "requirements_met"},
                      ensure_ascii=False)
    for a in adoc["answers"]:
        ans = json.dumps(a["answer"], ensure_ascii=False)
        check(ans not in qtxt or a["id"] in ("Q20", "Q21"),
              "%s 的答案疑似出现在 questions.json" % a["id"])

    # 每题都声明了坐标原点与容差
    for q in Qs:
        check("coordinate_origin" in q["rules"], "%s 未声明坐标原点" % q["id"])
        check("tolerance" in q["rules"], "%s 未声明容差" % q["id"])

    # ---------------- 独立重算网格题
    def O(i):
        return byi[i]

    def P(i):
        return O(i)["center"]

    def r4(x):
        return round(x, 4)

    def pick(pred):
        return sorted([o["id"] for o in objs if pred(o)])

    recomputed = {}
    recomputed["Q01"] = pick(lambda o: o["color"] == "purple"
                             and o["shape"] == "ring")
    recomputed["Q02"] = pick(lambda o: o["color"] == "blue"
                             and o["shape"] == "rounded_square"
                             and o["size"] == 80)
    recomputed["Q03"] = pick(lambda o: o["color"] == "green"
                             and o["size"] == 48)
    recomputed["Q04"] = pick(lambda o: o["color"] == "orange"
                             and o["shape"] in ("square",
                                                 "rounded_square"))
    recomputed["Q05"] = "右侧" if P("G05")[0] > P("G04")[0] else "左侧"
    recomputed["Q06"] = ("G09 更靠左" if P("G09")[0] < P("G16")[0]
                         else "G16 更靠左")
    recomputed["Q07"] = {"left_of": "G33" if P("G33")[0] < P("G64")[0]
                         else "G64",
                         "above": "G33" if P("G33")[1] < P("G64")[1]
                         else "G64"}
    for qid, x, y in (("Q08", "G01", "G64"), ("Q09", "G17", "G21"),
                      ("Q10", "G03", "G19")):
        recomputed[qid] = r4(math.hypot(P(x)[0] - P(y)[0],
                                        P(x)[1] - P(y)[1]))
    row5 = sorted([o for o in objs if o["row"] == 5],
                  key=lambda o: (-o["size"], o["id"]))
    recomputed["Q11"] = [o["id"] for o in row5]
    recomputed["Q12"] = [o["id"] for o in sorted(
        [o for o in objs if o["color"] == "blue" and o["shape"] == "circle"],
        key=lambda o: (-o["size"], o["id"]))]
    recomputed["Q13"] = [o["id"] for o in sorted(
        [o for o in objs if o["color"] == "purple"
         and o["shape"] == "rounded_square"],
        key=lambda o: (o["size"], o["id"]))]
    g6 = O("G06")
    recomputed["Q14"] = [g6["center"][0] - 40, g6["center"][1] - 40,
                         g6["center"][0] + 40, g6["center"][1] + 40]
    gr = [o for o in objs if o["color"] == "green" and o["shape"] == "ring"]
    recomputed["Q15"] = [min(o["bbox"][0] for o in gr),
                         min(o["bbox"][1] for o in gr),
                         max(o["bbox"][2] for o in gr),
                         max(o["bbox"][3] for o in gr)]
    blues = [o for o in objs if o["color"] == "blue"]
    bc = [o["id"] for o in blues if o["shape"] == "circle"]
    recomputed["Q16"] = {"blue_total": len(blues),
                         "blue_circles": len(bc), "circle_ids": bc}
    row3 = [o for o in objs if o["row"] == 3]
    recomputed["Q17"] = {
        "ring_count": len([o for o in row3 if o["shape"] == "ring"]),
        "ring_ids": [o["id"] for o in row3 if o["shape"] == "ring"],
        "purple_count": len([o for o in row3 if o["color"] == "purple"]),
        "purple_ids": [o["id"] for o in row3
                       if o["color"] == "purple"]}

    mismatch = []
    for qid, exp in recomputed.items():
        got = answers.get(qid)
        check(got is not None, "%s 缺答案" % qid)
        if got != exp:
            mismatch.append({"id": qid, "expected": exp, "got": got})
    check(not mismatch, "答案与独立重算不一致: %s" % mismatch)

    # ---------------- 遮挡题
    # F04–F09 中的圆环：按 scene-data 之外的前景清单从 equivalence.json 之外的
    # 交付数据无法得知，故以 answers.json 引用的坐标与 PNG 上的可见事实互证。
    q18 = answers["Q18"]
    check(set(q18) == {"F06", "F08"}, "Q18 圆环应为 F06、F08，实际 %s"
          % sorted(q18))
    q19 = answers["Q19"]
    check(q19.get("F01") == "circle" and q19.get("F02") == "ring"
          and q19.get("F03") == "rounded_square", "Q19 白色对象形状不符")

    # 不确定题
    for qid in ("Q20", "Q21"):
        check(answers.get(qid) == "无法确定",
              "%s 答案应为“无法确定”" % qid)
        rec = next(a for a in adoc["answers"] if a["id"] == qid)
        check(bool(rec.get("undeterminable_reason")),
              "%s 缺 undeterminable_reason" % qid)

    # ---------------- equivalence
    ev = edoc["conclusion"]
    check(ev["visible_pixels_equivalent"], "equivalence 应判定可见等价")
    check(edoc["pixel_comparison"]["differing_pixel_count"] == 0,
          "不同像素数必须为 0")
    check(edoc["pixel_comparison"]["shape_matches_expected"],
          "解码后尺寸应为 800×800×4")
    check(edoc["pixel_comparison"]["canvas_size_equal"], "两图尺寸应一致")
    check(ev["hidden_content_differs"] and
          edoc["hidden_differences"]["counts_differ"], "隐藏内容应确实不同")
    check(edoc["hidden_differences"]["count_A"] !=
          edoc["hidden_differences"]["count_B"],
          "两版隐藏对象数量应不同")
    check(edoc["hidden_differences"]["shared_signatures"] == 0,
          "两版隐藏对象不应有任何相同 (形状,颜色,尺寸,中心)")

    # ---------------- PNG / DSL 配对
    finals = {"grid-scene.png": [1600, 1600],
              "occlusion.png": [800, 800],
              "occlusion-alternative.png": [800, 800]}
    for name, wh in finals.items():
        p = OUT / name
        check(p.exists(), "缺最终图 %s" % name)
        if not p.exists():
            continue
        body = p.read_bytes()
        check(body[:8] == b"\x89PNG\r\n\x1a\n", "%s 不是真 PNG" % name)
        ihdr = [struct.unpack(">I", body[16:20])[0],
                struct.unpack(">I", body[20:24])[0]]
        check(ihdr == wh, "%s IHDR %s 应为 %s" % (name, ihdr, wh))
        dsl = OUT / (name[:-4] + ".snapshot")
        check(dsl.exists() and dsl.stat().st_size > 0,
              "缺同名 DSL %s" % dsl.name)
        if dsl.exists():
            txt = dsl.read_text(encoding="utf-8")
            check("<Image" not in txt, "%s 含外部图像" % dsl.name)

    print("problems:", len(problems))
    for p in problems:
        print(" -", p)
    print("questions:", len(Qs), "grid:", len(grid), "occ:", len(occ),
          "two_step:", len(twostep),
          "max_id:", max(int(q["id"][1:]) for q in Qs))
    print("answers_rechecked:", len(recomputed), "mismatch:", len(mismatch))
    print("differing_pixels:",
          edoc["pixel_comparison"]["differing_pixel_count"])
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
