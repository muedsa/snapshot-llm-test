#!/usr/bin/env python
"""A14 审计收尾：把像素核验结果与 22 次看图记录并入 batch-audit-raw.json。

启动基准：总任务根 (suite_root)。随后重跑 deliver_a14.py 生成最终 batch-audit.json。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
T = BASE / "tmp/run-20261011-01/A14"
OUT = "outputs/run-20261011-01/A14"

REVIEWS = [
    # (阶段, 图, 缩放, 观察, 改动, 结论)
    ("v1", "preview/contact-sheet-v1.png", "整屏",
     "接触表首版服务 400（缩放正则漏等号，生成非法属性名 left\"0.0\"），"
     "修正替换式后出图并打开：8 张卡的页眉/眉题/标题带/讲者行位置一致，"
     "四种状态的颜色与形状已可区分",
     "修正缩放正则后重渲（见 candidates 里的 400 响应）", "辅助证据；体系一致但单张仍有缺陷"),
    ("v1", "preview/card-K01-v1.png", "整屏",
     "① 品牌标记内只画出「S/」，V 被裁；② 1 行标题下对齐到 456px，眉题与标题之间约 300px 死区；"
     "③ 讲者文本框底边 594px 越过 590px 安全下边距",
     "记录 3 项缺陷", "不合格，需重排"),
    ("v1", "preview/card-K04-v1.png", "整屏",
     "尖括号与 & 正确显示为字面量（A < B & C > D），没有变成 &lt; 实体；换行落在「本」前可接受",
     "无需改动", "文字保真通过"),
    ("v1", "preview/card-K06-v1.png", "整屏",
     "取消卡：完整标题、13:40、红色叉号徽标与「本场取消」注记都在，底色仍是统一深蓝不是灰底；"
     "但右上斜纹带压在「2026.11.07」后面",
     "记录斜纹压字", "内容通过，装饰需让位"),
    ("v1", "preview/card-K08-v1.png", "整屏",
     "3 行标题排布正常，中文弯引号「“ ”」显示正确，右侧层格条为 3 条与行数一致",
     "无需改动", "通过"),
    ("v1", "preview/card-K07-v1.png", "整屏",
     "长讲者「Northstar Research · 林川」26px 下一行容下；破折号「——」正常；"
     "候选紫色圆环符号与开放/取消的实心圆、叉号形状可分",
     "记录两行讲者分支未触发", "通过"),
    ("probe-width", "preview/probe-width.png", "整屏 + 逐像素量测",
     "12 行 100px 样张；用 PIL 逐列量墨迹宽，发现 ASCII 类系统性偏小："
     "「A < B & C > D」偏 18%、「Color, Alpha & Contrast 」偏 8%，"
     "而纯中文行实测 0.98–1.0em（模型是对的）。两行超框样张被裁，未参与拟合",
     "据实测值重写 char_em() 系数", "标定完成"),
    ("v2", "preview/card-K01-v2.png", "整屏",
     "死区消失（标题带内居中）；斜纹与讲者下边距已处理；但 S/V 字标**整段消失**",
     "定位为内层 Positioned 坐标基准写错", "新引入缺陷"),
    ("v3", "preview/card-K01-v3.png", "整屏",
     "S/V 恢复完整；标题居中；讲者墨迹下缘回到安全边距内",
     "内层坐标改回标记方块内的相对值", "通过"),
    ("v3", "preview/card-K06-v3.png", "整屏",
     "斜纹移到最右侧 110px 竖带且压到 5% 不透明度，日期清晰；标题/时间/注记完整",
     "无需改动", "通过"),
    ("v4", "preview/card-K02-v4.png", "整屏",
     "末行只剩「约束」两个字，主标题末尾出现孤字",
     "加入孤字判据（末行 < 栏宽 25% 即降档）", "K02 变 56px 单行"),
    ("v4", "preview/card-K03-v4.png", "整屏", "冒号未落在行首，避头尾生效；2 行排布正常", "无", "通过"),
    ("v4", "preview/card-K04-v4.png", "整屏", "换行点变化但文字完整", "无", "通过"),
    ("v4", "preview/card-K05-v4.png", "整屏",
     "**标题丢词**：画面只剩「Color, Alpha &」，「Contrast 」被服务端按框宽裁掉，"
     "第二行是「/ 从颜色到可读性」。HTTP 仍 200、image_info 正常",
     "触发字宽标定与 T3 兜底降档", "不合格"),
    ("v4", "preview/card-K01-v4.png", "整屏", "与 v3 一致，无回归", "无", "通过"),
    ("v5", "preview/card-K05-v5.png", "整屏",
     "换系数后 K05 取 56px 两行，「Color, Alpha & Contrast /」与「从颜色到可读性」完整显示",
     "无", "通过"),
    ("v5", "preview/card-K01-v5.png", "整屏", "S/V、标题、徽标、讲者、时间全部正确", "无", "通过"),
    ("v5", "preview/card-K02-v5.png", "整屏", "单行 56px，无孤字；满额琥珀方块符号清晰", "无", "通过"),
    ("v5", "preview/card-K03-v5.png", "整屏", "2 行 56px，候补紫色圆环符号清晰", "无", "通过"),
    ("v5", "preview/card-K04-v5.png", "整屏", "2 行 64px，尖括号与 & 仍为字面量", "无", "通过"),
    ("v5", "preview/card-K06-v5.png", "整屏",
     "取消卡：完整标题 + 13:40 + 红色叉号徽标 + 「本场取消」注记；统一底色未被替换为灰底", "无", "通过"),
    ("v5", "preview/card-K07-v5.png", "整屏", "2 行 48px，讲者「Northstar Research · 林川」完整", "无", "通过"),
    ("v5", "preview/card-K08-v5.png", "整屏",
     "3 行 56px，弯引号完整，层格条 3 条；标题 56px 大于时间 40px，层级正确", "无", "通过"),
    ("v5-sheet", "preview/contact-sheet-v5.png", "整屏",
     "最终接触表：8 张的页眉、标题带、层格条数量随行数联动（1/1/2/2/2/2/2/3）、"
     "四种状态三通道区分一致；仅作辅助证据，8 张原图已各自单独打开",
     "无", "辅助证据，不替代 8 张原图"),
]


def text_fidelity(audit: dict, src: dict) -> dict:
    rows = []
    for c in audit["cards"]:
        cid = c["id"]
        s = src[cid]
        rt = c["rendered_text"]
        joined_title = "".join(rt["title_lines"])
        joined_sp = "".join(rt["speaker_lines"])
        rows.append({
            "id": cid,
            "title_source": s["title"],
            "title_rendered_joined": joined_title,
            "title_strict_equal": joined_title == s["title"],
            "title_equal_ignoring_spaces": joined_title.replace(" ", "") == s["title"].replace(" ", ""),
            "speaker_source": s["speaker"],
            "speaker_rendered_joined": joined_sp,
            "speaker_equal": joined_sp == s["speaker"],
            "time_source": s["time"], "time_rendered": rt["time"], "time_equal": rt["time"] == s["time"],
            "status_source": s["status"], "status_rendered": rt["status"],
            "status_equal": rt["status"] == s["status"],
        })
    return {
        "method": "把 DSL 实际发出的每一行 Text 拼回整串，与 inputs/cards.json 的源字段比对；"
                  "换行只是排版，不应增删任何字符",
        "note": "断行点处可能出现被排版吞掉的行尾空格，因此同时给出严格相等与"
                "「忽略空格后相等」两个判定",
        "rows": rows,
        "all_equal_ignoring_spaces": all(r["title_equal_ignoring_spaces"] and r["speaker_equal"]
                                         and r["time_equal"] and r["status_equal"] for r in rows),
        "all_strict_equal": all(r["title_strict_equal"] and r["speaker_equal"]
                                and r["time_equal"] and r["status_equal"] for r in rows),
    }


def main() -> None:
    p = T / "drafts/batch-audit-raw.json"
    audit = json.loads(p.read_text(encoding="utf-8"))
    verify = json.loads((T / "drafts/verify.json").read_text(encoding="utf-8"))
    calib = json.loads((T / "drafts/width-calibration.json").read_text(encoding="utf-8"))
    src = {c["id"]: c for c in json.loads(
        (BASE / "tasks/A14-content-stress-batch/inputs/cards.json").read_text(encoding="utf-8"))}

    vmap = {r["id"]: r for r in verify["cards"]}
    for c in audit["cards"]:
        v = vmap[c["id"]]
        c["measured"] = {
            "title_lines_measured": v["title_lines_measured"],
            "title_line_ink": v["title_line_ink"],
            "title_ink_bbox": v["title_ink_bbox"],
            "title_right_edge_px": v["title_ink_bbox"][2],
            "title_column_right_edge": v["title_column_right_edge"],
            "title_line_pitch_px": v["title_line_pitch_px"],
            "title_line_pitch_declared": v["title_line_pitch_declared"],
            "badge_left_edge_px": v["badge_left_edge_px"],
            "title_badge_gap_px": v["title_badge_gap_px"],
            "no_collision": v["no_collision"],
            "content_ink_bbox": v["content_ink_bbox"],
            "within_safe_margin": v["within_safe_margin"],
            "status_color_on_canvas": v["status_color_on_canvas"],
            "symbol_fill_ratio": v["symbol_fill_ratio"],
            "symbol_center_fill_ratio": v["symbol_center_fill_ratio"],
            "passed": v["passed"],
            "source": f"{OUT}/card-{c['id']}.png",
        }

    audit["reviews"] = [
        {"stage": r[0], "image": {"path_base": "suite_root", "path": f"tmp/run-20261011-01/A14/{r[1]}"},
         "zoom": r[2], "observed": r[3], "change": r[4], "conclusion": r[5],
         "is_final_card": r[0] == "v5" and r[1].startswith("preview/card-")}
        for r in REVIEWS
    ]
    audit["review_summary"] = {
        "total_image_views": len(REVIEWS),
        "final_card_views": sum(1 for r in REVIEWS
                                if r[0] == "v5" and r[1].startswith("preview/card-")),
        "final_card_ids_viewed": sorted({r[1].split("card-")[1].split("-")[0] for r in REVIEWS
                                         if r[0] == "v5" and r[1].startswith("preview/card-")}),
        "contact_sheet_views": sum(1 for r in REVIEWS if "sheet" in r[1]),
        "contact_sheet_role": "辅助证据，只在临时目录；8 张原图各自单独打开，接触表不替代它们",
        "claim_rule": "8 张定稿每张各有独立查看条目后才写 all_passed；没有查看过的卡不会被计入",
    }
    audit["verification"] = {
        "pixel_checks": verify,
        "text_fidelity": text_fidelity(audit, src),
        "width_calibration": calib,
        "all_passed": (verify["all_passed"]
                       and text_fidelity(audit, src)["all_equal_ignoring_spaces"]
                       and len(audit["review_summary"]["final_card_ids_viewed"]) == 8),
    }
    audit["all_passed"] = audit["verification"]["all_passed"]

    p.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "reviews": len(audit["reviews"]),
        "final_card_views": audit["review_summary"]["final_card_views"],
        "pixel_all_passed": verify["all_passed"],
        "text_all_equal": audit["verification"]["text_fidelity"]["all_equal_ignoring_spaces"],
        "all_passed": audit["all_passed"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()