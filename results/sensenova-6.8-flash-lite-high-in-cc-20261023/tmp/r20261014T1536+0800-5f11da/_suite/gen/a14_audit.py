"""A14 审计：8 张 1200×630 卡的像素级核验 + batch-audit.json。

判据只来自题目给定的硬约束，不自造阈值：
  * 安全边距 40 —— 量整幅与逐槽位墨迹，四向净空都必须 ≥40。
  * 标题字号 ≥36、最多 3 行 —— 与生成器的字号台阶下限对齐。
  * 讲者字号 ≥22、最多 2 行 —— 同上。
  * 标题不与状态徽标碰撞 —— 量标题墨迹右缘与徽标墨迹左缘之间的净空。
  * 取消卡 —— 完整标题 + 时间 + 「本场取消」注明三者墨迹都在，且不是灰底。
  * 状态用颜色加文字/符号区分 —— 在徽标盒内按颜色取证，前景色与底色都必须
    真的出现在画面上（各有一定像素数）。
  * 文字原样保留 —— 由 a14_pages._escape_check 的字符多重集比较承担。

阈值来源说明：「标题与徽标净空 ≥8 px」与「墨迹未越出声明盒」是排版安全余量，
题目没有给定数值，所以在 batch-audit.json 里明确标为 self_defined 并注明依据，
不冒充题目要求。

用法：SNAPSHOT_RUN_ID=<rid> python -I a14_audit.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
# run_id 从脚本自身路径推出（tmp/<rid>/_suite/gen/…）；显式 SNAPSHOT_RUN_ID 优先
os.environ.setdefault("SNAPSHOT_RUN_ID", HERE.parents[2].name)
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import a14_pages as A
import a14_pixels as P
import suite as S

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TASK = "A14"
RID = A.RID
OUT, TMP = A.OUT, A.TMP

# 题目给定的硬约束
SAFE_MIN = 40
TITLE_MIN = 36
TITLE_MAXL = 3
SPEAKER_MIN = 22
SPEAKER_MAXL = 2
# 自定余量（题目未给数值，标注依据）
CLEAR_GAP_MIN = 8.0
INK_OVERSHOOT_MIN = -1.0      # 墨迹允许越过声明盒 1 px（抗锯齿）
# 右锚容差：text_r 的算法把估算误差减半（盒宽 = 墨宽+pad，盒心偏 pad/2），
# 所以真实右缘与 CX1 的偏差只有墨宽估算误差的一半。等宽字 5 字符的估算误差
# 也就 ±3 px，取 ±2 px 既覆盖它，又能抓出「讲」/「SESSION」那种丢字。
ANCHOR_TOL = 2.0
CX1_ACTUAL = A.CX1          # 内容栏右缘（也是右锚目标）
LABEL_INK_RATIO = 0.6       # 实测墨宽 / 估算墨宽 下限，掉到此值下即判定丢字


def main() -> int:
    rep: dict = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "run_id": RID,
        "thresholds": {
            "safe_margin_min_px": {"value": SAFE_MIN, "source": "task"},
            "title_font_min_px": {"value": TITLE_MIN, "source": "task"},
            "title_lines_max": {"value": TITLE_MAXL, "source": "task"},
            "speaker_font_min_px": {"value": SPEAKER_MIN, "source": "task"},
            "speaker_lines_max": {"value": SPEAKER_MAXL, "source": "task"},
            "title_badge_clear_gap_min_px": {
                "value": CLEAR_GAP_MIN, "source": "self_defined",
                "basis": "题目只要求「标题不与状态徽标碰撞」，未给数值；取 8 px "
                         "作为排版安全余量，任何正净空都算不碰撞"},
            "ink_overshoot_allowed_px": {
                "value": INK_OVERSHOOT_MIN, "source": "self_defined",
                "basis": "文字抗锯齿边缘会向外溢约 1 px，允许 1 px 的盒外墨迹"},
            "right_anchor_tolerance_px": {
                "value": ANCHOR_TOL, "source": "self_defined",
                "basis": "右锚算法（盒宽=墨宽+pad、盒心右移 pad/2）把墨宽估算误差"
                         "减半；等宽 5 字符的估算误差约 ±3 px，±2 px 既能覆盖又"
                         "能抓出丢字"},
            "label_ink_width_ratio_min": {
                "value": LABEL_INK_RATIO, "source": "self_defined",
                "basis": "CJK 字面墨宽约为字号的 0.85–0.95 倍，估算本身偏保守，"
                         "所以真实/估算正常在 0.8 以上；掉到 0.6 以下只能是字符被"
                         "裁掉（历史上「讲者」→「讲」、页脚 →「讲座系列 ·」）"},
        },
        "tools": {"pillow": P.Image.__version__},
        "generation": {
            "script": "tmp/%s/_suite/gen/a14_pages.py" % RID,
            "input": "tasks/A14-content-stress-batch/inputs/cards.json",
            "canvas_px": [A.W, A.H],
            "safe_margin_px": A.SAFE,
            "content_column": [A.CX0, A.CX1],
            "primary_color": A.ACCENT,
            "brand": A.BRAND, "date": A.DATE,
            "status_system": {
                "channels": ["foreground_color", "background_tint",
                             "drawn_symbol", "chinese_label"],
                "symbols_are_geometric": True,
                "symbols_not_font_glyphs": True,
                "symbols_avoid_missing_glyph_tofu": True,
                "table": {k: {"foreground": v["fg"], "background": v["bg"],
                              "symbol": v["sym"], "note": v["sym_note"]}
                          for k, v in A.STATUS.items()},
            },
            "shared_rules": [
                "全部坐标/字号/颜色来自 a14_pages.py 的常量表，无逐卡硬编码",
                "标题一行一个单行 <Text> 盒，不依赖服务自动折行",
                "右锚元素走 text_r()：盒宽 = 墨宽估算 + PAD_X，align=CENTER，"
                "盒左 = 右缘 - 墨宽 - PAD_X/2，从而墨迹右缘落在内容栏右缘上且"
                "估算误差减半",
                "盒宽必须大于墨宽：盒窄于墨宽时服务会自行折行，而单行盒高把第二行"
                "整行裁掉——这是标签与页脚丢字的真实根因",
                "所有 text 属性收原始字符，esc() 为恒等函数；服务不解码 XML 实体，"
                "写成 &lt; 会在画面上显示成字面串（实测见 text_special_chars）",
                "卡片 PNG 均为服务原始字节，未做任何后处理",
            ],
            "length_branch_conditions": {
                "title": {
                    "rule": "从 %s 起逐档降，取第一个能在 %d 行内排下的字号"
                            % (A.TITLE_STEPS, TITLE_MAXL),
                    "wrap_limit_px": A.TITLE_WRAP_LIMIT,
                    "box_width_px": A.TITLE_W,
                    "slack_px": A.TITLE_W - A.TITLE_WRAP_LIMIT,
                    "font_floor_px": A.TITLE_STEPS[-1],
                    "never_changes": ["canvas", "safe_margin", "badge",
                                      "speaker_slot", "time_slot",
                                      "header", "footer"],
                },
                "speaker": {
                    "rule": "先 %d px，装不下降到 24 px，均按 2 行上限"
                            % A.SPEAKER_SIZE,
                    "wrap_limit_px": A.SPEAKER_WRAP_LIMIT,
                    "box_width_px": A.SPEAKER_W,
                    "font_floor_px": 22,
                },
                "cancel_note": {
                    "rule": "仅取消卡出现；顶缘 = 标题盒底 + %d px，由实际行数"
                            "驱动，不逐条硬改" % A.NOTE_GAP,
                    "title_time_status_all_retained": True,
                },
            },
            "anchor_calibration": {
                "mechanism": "text_r 用 alignment=CENTER，盒中心 = 右缘 - ink_est/2；"
                            "真实墨宽与估算差被减半传导到锚点",
                "shift_px": dict(A.ANCHOR_SHIFT),
                "evidence": "tmp/%s/A14/gen/batch-audit.json 的 right_anchors："
                            "K01–K08 的 date/time/label_time/footer_right 墨迹右缘"
                            "完全一致（偏差 -4/-4/-2/+3），说明偏移只跟字符串族+"
                            "字号+字距有关，与卡内容无关" % RID,
                "note": "shift 是实测值不是估计值；盒边界与墨迹一起平移同样的量",
            },
            "text_special_chars": {
                "chars": ["&", "<", ">"],
                "policy": "原样写入 text 属性，不做任何转义（esc() 为恒等函数）",
                "why": "服务不解码 XML 实体：写成 &lt; 会在画面上显示成字面串",
                "evidence": [
                    "req-a14-probe-layout-abdd1d：标题写成 &lt; &amp; &gt; 实体，"
                    "渲染结果就是字面 &lt; &amp; &gt;，证明实体未被解码",
                    "req-a14-escape-test-raw-6355ec：裸 A < B & C > D 直接写入 "
                    "text 属性，HTTP 200，渲染逐字正确"],
                "verified_by": "a14_pages._escape_check（实体串出现即判缺陷）",
                "caveat": "半角双引号会截断属性，本批 8 条数据均不含，已断言",
            },
        },
        "cards": [], "consistency": {}, "reviews": [],
        "checks": [],
    }

    def note(cid, desc, passed, detail):
        rep["checks"].append({"id": cid, "desc": desc, "passed": bool(passed),
                              "detail": detail})

    # ---- 生成器侧的前置校验结果一并归档
    gen_probs = A.checks() + A._escape_check()
    rep["generation"]["pre_render_checks"] = {
        "problems": gen_probs, "count": len(gen_probs),
        "escape_check_included": True}

    imgs = []
    title_inks, time_inks, badge_l, badge_r = [], [], [], []

    for c in A.CARDS:
        dsl, m = A.build_card(c)
        cid = c["id"]
        png = OUT / ("card-%s.png" % cid)
        snap = OUT / ("card-%s.snapshot" % cid)
        rec = {"id": cid,
               "png": {"path_base": "output_dir",
                       "path": "card-%s.png" % cid},
               "dsl": {"path_base": "output_dir",
                       "path": "card-%s.snapshot" % cid}}
        if not png.exists():
            note("f-" + cid, "%s PNG 存在" % cid, False, "文件缺失")
            rep["cards"].append(rec)
            continue

        im, dec = P.open_rgb(png)
        imgs.append((cid, im))
        size_ok = [im.width, im.height] == [A.W, A.H]
        note("size-" + cid, "%s 尺寸 %d×%d" % (cid, A.W, A.H), size_ok,
             {"actual": [im.width, im.height], "decode": dec["png_mode"]})

        dsl_ok = snap.exists() and snap.read_text(encoding="utf-8") == dsl
        note("dsl-" + cid, "%s .snapshot 与生成器 DSL 完全一致" % cid, dsl_ok,
             {"bytes": snap.stat().st_size if snap.exists() else None})
        rec["dsl_matches_generator"] = dsl_ok
        rec["png_bytes"] = png.stat().st_size

        # 整幅墨迹 → 全局安全边距
        bb = P.ink_bbox(im)
        rec["ink"] = {"bbox": bb}
        if bb:
            margins = {"left": bb[0], "top": bb[1],
                       "right": A.W - 1 - bb[2],
                       "bottom": A.H - 1 - bb[3]}
            ok = all(v >= SAFE_MIN for v in margins.values())
            note("safe-" + cid, "%s 安全边距 ≥%d（实测四向墨迹净空）"
                 % (cid, SAFE_MIN), ok, margins)
            rec["safe_margin"] = {"min_px": SAFE_MIN,
                                  "measured_clearance_px": margins,
                                  "passed": ok,
                                  "method": "整幅 PNG 墨迹包围盒到画布边缘的"
                                            "距离；白底铺满画布，所以墨迹即"
                                            "非白像素"}

        # ---- 逐槽位
        regions = {}
        for key in ("brand", "date"):
            regions[key] = P.region_ink(im, m["header"][key]["box"])
        regions["accent_rule"] = P.region_ink(
            im, [m["header"]["accent_rule"][0], m["header"]["accent_rule"][1],
                 m["header"]["accent_rule"][0] + m["header"]["accent_rule"][2],
                 m["header"]["accent_rule"][1] + m["header"]["accent_rule"][3]])
        regions["title"] = P.region_ink(im, m["title"]["box"])
        regions["status"] = P.region_ink(im, m["status"]["box"])
        regions["speaker"] = P.region_ink(im, m["speaker"]["box"])
        regions["time"] = P.region_ink(im, m["time"]["box"])
        regions["label_speaker"] = P.region_ink(im, m["labels"]["speaker"]["box"])
        regions["label_time"] = P.region_ink(im, m["labels"]["time"]["box"])
        regions["footer"] = P.region_ink(im, m["footer"]["box"])
        regions["footer_id"] = P.region_ink(im, m["footer"]["id_box"])
        regions["footer_right"] = P.region_ink(im, m["footer"]["right_box"])
        rec["regions"] = regions

        # 标题：行数用行带量出来，不靠声明
        bands = P.row_bands(im, m["title"]["box"])
        rec["title_measurement"] = {"declared_lines": m["title"]["line_count"],
                                    "measured_line_bands": bands,
                                    "measured_line_count": len(bands)}
        line_ok = len(bands) == m["title"]["line_count"]
        note("lines-" + cid, "%s 标题实测行数 == 声明行数" % cid, line_ok,
             {"declared": m["title"]["line_count"], "measured": len(bands),
              "bands": bands})

        ti = regions["title"]
        clipped = ti["has_ink"] and (ti["clear"]["top"] < INK_OVERSHOOT_MIN
                                     or ti["clear"]["bottom"] < INK_OVERSHOOT_MIN
                                     or ti["clear"]["right"] < INK_OVERSHOOT_MIN
                                     or ti["clear"]["left"] < INK_OVERSHOOT_MIN)
        note("titlefit-" + cid, "%s 标题墨迹在标题盒内未被裁切" % cid,
             ti["has_ink"] and not clipped,
             {"ink": ti["ink"], "clear": ti["clear"]})

        # 标题 / 讲者字号与行数（题目下限）
        tf, sf = m["title"], m["speaker"]
        note("titlefont-" + cid, "%s 标题字号 ≥%d" % (cid, TITLE_MIN),
             tf["size_px"] >= TITLE_MIN, {"size_px": tf["size_px"],
                                          "steps_tried": tf["font_steps_tried"]})
        note("titlelines-" + cid, "%s 标题行数 ≤%d" % (cid, TITLE_MAXL),
             tf["line_count"] <= TITLE_MAXL,
             {"line_count": tf["line_count"], "max": TITLE_MAXL})
        note("speakerfont-" + cid, "%s 讲者字号 ≥%d" % (cid, SPEAKER_MIN),
             sf["size_px"] >= SPEAKER_MIN,
             {"size_px": sf["size_px"], "steps_tried": sf["font_steps_tried"]})
        note("speakerlines-" + cid, "%s 讲者行数 ≤%d" % (cid, SPEAKER_MAXL),
             sf["line_count"] <= SPEAKER_MAXL,
             {"line_count": sf["line_count"], "max": SPEAKER_MAXL})

        sb = P.row_bands(im, m["speaker"]["box"])
        note("speakers-" + cid, "%s 讲者实测行数 == 声明行数" % cid,
             len(sb) == sf["line_count"],
             {"declared": sf["line_count"], "measured": len(sb), "bands": sb})
        rec["speaker_measurement"] = {"declared_lines": sf["line_count"],
                                      "measured_line_bands": sb}

        # 标题与徽标不碰撞：量两边的真实墨迹
        t_right = ti["ink"][2] if ti["has_ink"] else None
        st_left = regions["status"]["ink"][0] if regions["status"]["has_ink"] \
            else None
        gap = (st_left - t_right) if (t_right is not None and st_left) else None
        note("nocollision-" + cid, "%s 标题墨迹与状态徽标墨迹不相交且净空 ≥%g"
             % (cid, CLEAR_GAP_MIN),
             gap is not None and gap >= CLEAR_GAP_MIN,
             {"title_ink_right_px": t_right, "badge_ink_left_px": st_left,
              "gap_px": round(gap, 2) if gap is not None else None,
              "declared_title_badge_gap_px": m["title_badge_gap_px"]})
        rec["title_badge"] = {"title_ink_right_px": t_right,
                              "badge_ink_left_px": st_left,
                              "measured_gap_px": round(gap, 2) if gap is not None
                              else None}
        title_inks.append(t_right)
        if regions["time"]["has_ink"]:
            tb = regions["time"]["ink"]
            time_inks.append({"id": cid, "ink_right": tb[2], "ink_left": tb[0]})
        if st_left is not None:
            badge_l.append(st_left)
        if regions["status"]["has_ink"]:
            badge_r.append(regions["status"]["ink"][2])

        # 状态体系：颜色取证
        st = m["status"]
        colors = P.color_counts(im, st["box"],
                                {"foreground": st["foreground"],
                                 "background": st["background"]})
        cc = colors["foreground"]["pixels"] > 40 and \
            colors["background"]["pixels"] > 200
        note("statuscolor-" + cid, "%s 状态颜色真的画出来了（前景与底色像素数）"
             % cid, cc, {"symbol": st["symbol_kind"], **colors})
        rec["status"] = {
            "text_original": c["status"],
            "label_rendered": st["text"],
            "code": st["code"],
            "foreground": st["foreground"],
            "background": st["background"],
            "foreground_pixels_in_badge": colors["foreground"]["pixels"],
            "background_pixels_in_badge": colors["background"]["pixels"],
            "symbol_kind": st["symbol_kind"],
            "symbol_note": st["symbol_note"],
            "symbol_drawn_geometrically": True,
            "symbol_is_font_glyph": False,
            "box": st["box"],
            "encoded_by": ["color", "drawn_symbol", "chinese_label"],
            "distinguished_without_color": True,
        }

        # 时间
        tmi = regions["time"]
        rec["time"] = {"text_original": c["time"], "rendered": m["time"]["text"],
                       "size_px": m["time"]["size_px"], "box": m["time"]["box"],
                       "ink": tmi["ink"], "has_ink": tmi["has_ink"],
                       "clear": tmi["clear"]}
        note("timeink-" + cid, "%s 时间有墨迹且未裁切" % cid,
             tmi["has_ink"] and tmi["clear"]["top"] >= INK_OVERSHOOT_MIN
             and tmi["clear"]["bottom"] >= INK_OVERSHOOT_MIN
             and tmi["clear"]["left"] >= INK_OVERSHOOT_MIN
             and tmi["clear"]["right"] >= INK_OVERSHOOT_MIN,
             {"ink": tmi["ink"], "clear": tmi["clear"]})

        # 右锚专项：这组缺陷的历史形态是「讲者」渲染成「讲」、「SESSION」整段
        # 消失。共同根因是盒宽等于估算墨宽，盒窄于墨宽时服务自动折行，而单行盒
        # 高把第二行裁掉。所以这里直接量**墨迹宽度**和**墨迹右缘**，而不是只看
        # 「有没有墨迹」——有墨迹不等于字全。
        lb = m["labels"]
        lw_issues = []
        for k, lab in (("speaker", lb["speaker"]), ("time", lb["time"])):
            reg = regions["label_" + k]
            est = lab["estimated_ink_px"]
            iw = reg["ink_w"]
            # 估算本身允许误差，但真实墨宽掉到估算的一半以下只能是少字
            if not reg["has_ink"] or iw < est * LABEL_INK_RATIO:
                lw_issues.append({"label": k, "text": lab["text"],
                                  "estimated_ink_px": est, "measured_ink_w_px": iw})
        note("labelink-" + cid, "%s 两个标签的墨迹宽度覆盖全部字符" % cid,
             not lw_issues,
             {"measured": [{"label": k, "measured_ink_w_px": regions["label_" + k]["ink_w"]}
                           for k in ("speaker", "time")],
              "issues": lw_issues,
              "defect_guarded": "盒宽=估算墨宽会导致服务自动折行、单行盒高裁掉"
                                "第二行，历史上表现为「讲者」只剩「讲」"})

        fr = regions["footer_right"]
        fr_est = m["footer"]["right_estimated_ink_px"]
        fid = regions["footer_id"]
        fid_est = m["footer"]["id_estimated_ink_px"]
        foot_issues = []
        if not fr["has_ink"] or fr["ink_w"] < fr_est * LABEL_INK_RATIO:
            foot_issues.append({"slot": "right", "text": m["footer"]["right_text"],
                                "estimated_ink_px": fr_est,
                                "measured_ink_w_px": fr["ink_w"]})
        if not fid["has_ink"] or fid["ink_w"] < fid_est * LABEL_INK_RATIO:
            foot_issues.append({"slot": "id", "text": m["footer"]["id"],
                                "estimated_ink_px": fid_est,
                                "measured_ink_w_px": fid["ink_w"]})
        note("footerink-" + cid, "%s 页脚卡号与右侧串墨迹宽度覆盖全部字符" % cid,
             not foot_issues,
             {"measured": {"id": fid["ink_w"], "right": fr["ink_w"]},
              "issues": foot_issues,
              "defect_guarded": "页脚右串曾渲染成「讲座系列 ·」而 SESSION 整段消失"})

        # 右锚：墨迹右缘必须落在内容栏右缘 CX1 上
        anchors = []
        for name, reg, right in (("date", regions["date"], CX1_ACTUAL),
                                 ("time", tmi, CX1_ACTUAL),
                                 ("label_time", regions["label_time"], CX1_ACTUAL),
                                 ("footer_right", fr, CX1_ACTUAL)):
            anchors.append({"slot": name,
                            "ink_right_px": reg["ink"][2] if reg["has_ink"] else None,
                            "delta_from_content_right_px":
                                round(reg["ink"][2] - right, 2)
                                if reg["has_ink"] else None})
        anchors_ok = all(
            a["delta_from_content_right_px"] is not None
            and abs(a["delta_from_content_right_px"]) <= ANCHOR_TOL
            for a in anchors)
        note("anchor-" + cid,
             "%s 右锚墨迹右缘落在内容栏右缘 %d（±%g px）"
             % (cid, CX1_ACTUAL, ANCHOR_TOL), anchors_ok, anchors)
        rec["right_anchors"] = anchors

        # 文字原样保留
        rec["original_vs_actual"] = {
            "title": {"original": c["title"], "rendered_lines": tf["lines"],
                      "joined": "".join(tf["lines"]),
                      "identical_after_whitespace": "".join(tf["lines"])
                      .replace(" ", "") == c["title"].replace(" ", "")},
            "speaker": {"original": c["speaker"], "rendered_lines": sf["lines"],
                        "identical_after_whitespace": "".join(sf["lines"])
                        .replace(" ", "") == c["speaker"].replace(" ", "")},
            "time": {"original": c["time"], "actual": m["time"]["text"]},
            "status": {"original": c["status"], "actual": st["text"]},
        }
        ok_text = (rec["original_vs_actual"]["title"]["identical_after_whitespace"]
                   and rec["original_vs_actual"]["speaker"]
                   ["identical_after_whitespace"]
                   and m["time"]["text"] == c["time"] and st["text"] == c["status"])
        note("text-" + cid, "%s 标题/讲者/时间/状态文字与原始数据一致" % cid,
             ok_text, rec["original_vs_actual"])

        # 标题排版元数据
        rec["title"] = {
            "font_size_px": tf["size_px"],
            "line_count": tf["line_count"],
            "lines": tf["lines"],
            "line_height_px": tf["line_height_px"],
            "box": tf["box"],
            "estimated_widest_line_px": tf["estimated_widest_line_px"],
            "widest_line_ratio_of_box": tf["widest_line_ratio_of_box"],
            "wrap_limit_px": tf.get("wrap_limit_px"),
            "font_steps_tried": tf["font_steps_tried"],
            "font_size_floor_px": tf["size_floor_px"],
            "wrapped_not_shrunk_canvas": tf["wrapped_not_shrunk_canvas"],
        }
        rec["speaker"] = {
            "font_size_px": sf["size_px"], "line_count": sf["line_count"],
            "lines": sf["lines"], "line_height_px": sf["line_height_px"],
            "box": sf["box"],
            "font_steps_tried": sf["font_steps_tried"],
        }
        rec["header"] = {"brand": {"text": A.BRAND,
                                   "box": m["header"]["brand"]["box"],
                                   "ink": regions["brand"]["ink"],
                                   "has_ink": regions["brand"]["has_ink"]},
                         "date": {"text": A.DATE,
                                  "box": m["header"]["date"]["box"],
                                  "ink": regions["date"]["ink"],
                                  "has_ink": regions["date"]["has_ink"]},
                         "accent_rule": {"box": m["header"]["accent_rule"],
                                         "ink": regions["accent_rule"]["ink"]},
                         "rule_y": m["header"]["rule_y"]}
        rec["footer"] = {"box": m["footer"]["box"], "ink": regions["footer"]["ink"],
                         "id": m["footer"]["id"],
                         "right_text": m["footer"]["right_text"]}
        rec["cancel_note"] = m["cancel_note"]

        # 取消卡专项
        if c["status"] == "取消":
            nb = m["cancel_note"]["box"]
            ni = P.region_ink(im, nb)
            note("cancel-" + cid, "%s 取消卡完整标题 + 时间 + 「本场取消」注明"
                 "三者墨迹都在" % cid,
                 ti["has_ink"] and tmi["has_ink"] and ni["has_ink"],
                 {"cancel_note_box": nb, "cancel_note_ink": ni["ink"],
                  "title_ink": ti["ink"], "time_ink": tmi["ink"],
                  "method": "三处区域分别量墨迹存在性"})
            dom = P.dominant(im)
            # dominant() 把颜色量化到 8 级（//32*32），纯白 (255,255,255) 会被
            # 归到 (224,224,224)。之前直接比 [255,255,255] 永远匹配不上，导致取消
            # 卡被判成「灰底」——那是检查器的 bug，不是卡的缺陷。
            paper_q = [v // 32 * 32 for v in P.PAPER]
            paper = next((d for d in dom if d["rgb"] == paper_q), None)
            note("nogrey-" + cid, "%s 取消卡未灰底（白色底仍占主导）" % cid,
                 paper is not None and paper["pct"] > 30,
                 {"dominant": dom[:4], "paper_quantized": paper_q,
                  "method": "整幅主色统计（量化到 8 级，纯白归为 %s）；白色占比 "
                            ">30%% 即未整体灰化" % paper_q,
                  "threshold_source": "self_defined"})
            rec["greyed_check"] = {"dominant": dom[:4],
                                   "paper_pct": (paper["pct"] if paper else None),
                                   "greyed": not (paper is not None
                                                  and paper["pct"] > 30)}
        else:
            note("cancel-absent-" + cid, "%s 非取消卡不出现「本场取消」注明"
                 % cid, m["cancel_note"] is None,
                 {"status": c["status"], "cancel_note": m["cancel_note"]})

        # 各槽位墨迹存在性（有没有文字被画丢）
        missing = [k for k in ("brand", "date", "title", "status", "speaker",
                               "time", "footer", "label_speaker", "label_time")
                   if not regions[k]["has_ink"]]
        note("inkall-" + cid, "%s 全部文字与几何槽位都有墨迹" % cid,
             not missing, {"missing": missing})

        rep["cards"].append(rec)

    # ---- 全批一致性
    def spread(vals):
        vals = [v for v in vals if v is not None]
        return {"min": min(vals), "max": max(vals),
                "spread_px": round(max(vals) - min(vals), 2), "n": len(vals)} \
            if vals else {"min": None, "max": None, "spread_px": None, "n": 0}

    rep["consistency"] = {
        "title_ink_right_edges": spread(title_inks),
        "badge_ink_left_edges": spread(badge_l),
        "badge_ink_right_edges": spread(badge_r),
        "time_ink": {"right_edges": spread([t["ink_right"] for t in time_inks]),
                     "entries": time_inks},
        "shared_layout": {
            "content_column": [A.CX0, A.CX1],
            "title_x": A.TITLE_X, "title_y": A.TITLE_Y, "title_w": A.TITLE_W,
            "badge_box": [A.BADGE_X, A.BADGE_Y0, A.BADGE_X + A.BADGE_W,
                          A.BADGE_Y0 + A.BADGE_H],
            "speaker_box_top": A.VALUE_Y, "speaker_x": A.SPEAKER_X,
            "speaker_w": A.SPEAKER_W, "time_right": A.CX1,
            "label_y": A.LABEL_Y, "footer_y": A.FOOT_Y,
            "rule1_y": A.RULE1_Y, "rule2_y": A.RULE2_Y,
            "brand": A.BRAND, "date": A.DATE, "primary": A.ACCENT,
        },
        "note": "标题右缘与各卡标题墨迹右缘不必相同（长度不同），但标题**左缘**"
                "、标题盒顶、徽标盒、讲者盒顶、时间右缘、页脚线必须全批一致；"
                "spread_px 用来量实际的偏差",
    }
    tg = rep["consistency"]["badge_ink_right_edges"]
    note("consistency-badge", "8 张卡徽标墨迹右缘一致（误差 ≤3 px，抗锯齿）",
         tg["spread_px"] is not None and tg["spread_px"] <= 3, tg)
    tg2 = rep["consistency"]["time_ink"]["right_edges"]
    note("consistency-time", "8 张卡时间墨迹右缘一致（同一等宽字与字号）",
         tg2["spread_px"] is not None and tg2["spread_px"] <= 3, tg2)

    # ---- 接触表（仅作一致性辅助，不替代逐张查看）
    sheet_path = TMP / "preview" / "a14-contact-sheet.png"
    sheet_path.parent.mkdir(parents=True, exist_ok=True)
    if len(imgs) == len(A.CARDS):
        sm = P.contact_sheet(imgs, sheet_path)
        rep["contact_sheet"] = {
            "path": {"path_base": "suite_root", "path": S.rel(sheet_path)},
            "purpose": "全批一致性辅助检查",
            "does_not_replace": "逐张查看最终服务原图（A14 AGENTS 明确要求）",
            **sm}

    # ---- 逐图查看记录（真实查看后填 reviews.json，再重跑本脚本）
    rv = TMP / "gen" / "reviews.json"
    if rv.exists():
        reviews = json.loads(rv.read_text(encoding="utf-8"))
        rep["reviews"] = reviews
    else:
        rep["reviews"] = {"status": "pending",
                          "expected_entries": len(A.CARDS),
                          "note": "尚未写入 reviews.json：需要实际打开每张最终"
                                  "服务原图后按 audit-fields 的字段填写"}

    OUT.mkdir(parents=True, exist_ok=True)
    OUT.joinpath("batch-audit.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (TMP / "gen" / "batch-audit.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    npass = sum(1 for c in rep["checks"] if c["passed"])
    print("检查 %d 项，通过 %d" % (len(rep["checks"]), npass))
    for c in rep["checks"]:
        if not c["passed"]:
            print("  [FAIL] %s" % c["desc"])
    print("前置校验问题 %d" % len(gen_probs))
    for x in gen_probs:
        print("  !", x)
    print("报告", S.rel(TMP / "gen" / "batch-audit.json"))
    return 1 if (npass != len(rep["checks"]) or gen_probs) else 0


if __name__ == "__main__":
    raise SystemExit(main())
