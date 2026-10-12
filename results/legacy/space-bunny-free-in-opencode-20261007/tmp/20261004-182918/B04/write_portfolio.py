"""B04: write portfolio.json / portfolio.md / gallery.html from real artifacts."""
import io
import json
import os

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMP = os.path.join(ROOT, "tmp", RUN, "B04")
OUT = os.path.join(ROOT, "outputs", RUN, "B04")
S = json.load(io.open(os.path.join(TMP, "render-summary.json"), encoding="utf-8"))
CM = json.load(io.open(os.path.join(TMP, "case-meta.json"), encoding="utf-8"))

cases = []
for i in range(1, 11):
    cid = "case-%02d" % i
    s, m = S[cid], CM[cid]
    cases.append({
        "id": cid,
        "title": m["title"],
        "audience": m["audience"],
        "use_context": m["context"],
        "user_goal": m["goal"],
        "content_basis": m["basis_short"],
        "sources": m["sources"],
        "visual_intent": m["intent"],
        "png": "%s/final.png" % cid,
        "snapshot": "%s/final.snapshot" % cid,
        "case_note": "%s/case.md" % cid,
        "dimensions": s["dimensions"],
        "png_bytes": s["bytes"],
        "dsl_bytes": s["dsl_bytes"],
        "element_tags_estimate": s["element_tags"],
        "supporting_assets": [],
        "asset_policy_note": "run-config.json 的 asset_policy 为 "
                             "dsl_primary_with_supporting_assets；本件未使用任何外部素材、"
                             "无 <Image> 节点，主体与全部文字由 DSL 构造。",
        "dsl_capabilities": m["dsl"],
        "completion_criteria": m["crit"],
        "visual_review": m["review"],
        "render_attempts": s["attempts"],
        "successful_renders": s["ok"],
        "failed_renders": [f["request_id"] for f in s["failed"]],
        "request_ids": s["successful_request_ids"],
        "final_request_id": s["final_request_id"],
        "iteration_ids": m["iterations"],
        "draft_scripts": ["tmp/%s/B04/build_%s.py" % (RUN, cid)],
        "unresolved_issues": [m["left"]],
    })

portfolio = {
    "schema_version": 1,
    "task_id": "B04",
    "run_id": RUN,
    "status": "completed",
    "asset_policy": "dsl_primary_with_supporting_assets (no supporting assets used)",
    "topic": "海洋酸化（ocean acidification）：「0.1」这个数字到底意味着什么",
    "curatorial_statement":
        "这不是十张同版式卡片的换色，而是一条十步的阅读路径：01–03 建立「对数尺」"
        "这件工具（先给矛盾、再给可信度、再给尺子），04–07 是主体"
        "（碳酸根为什么被吃掉 / 现在有多异常 / 2100 会怎样 / 一个 Ω 读数意味着什么），"
        "08–09 转向「谁受损」与「谁在测」，10 把整套编辑纪律交出来——"
        "一份带五级判定的核查卡。全本统一一套色板与版式头，但三处例外是有意的："
        "01 用珊瑚红出题、06 用一条暖色地平线带提示「分岔」是唯一带预测性质的作品、"
        "10 的判定色标故意不复用主色板（否则「目前不足」会被误读成「很严重」）。"
        "每张图都区分四种东西：实测、来源结论、本图算术值、未取到的空缺；"
        "投影一律用虚线并注明「不是预测，也不是承诺」。",
    "reading_order_rationale":
        "顺序不是时间线也不是定义集，而是「先建立尺子 → 再给账本 → 再给后果 → "
        "最后交出判定标准」。06 放在 07 之前是有意的：先看到分岔再看落点，"
        "读者才知道阈值不是宿命。10 放最后因为它需要前九件的上下文才能被评估。",
    "cases": cases,
    "final_collection_review": {
        "independence_check":
            "十件服务十种不同的使用任务（封面 / 可引用数据页 / 概念解剖 / 技术附录 / "
            "尺度参照 / 情景判断 / 阈值查询 / 效应量比较 / 监测状态 / 事实核查），"
            "画布尺寸覆盖 1200×1600、1300×1820、1500×1100、1600×1000、1600×1050、"
            "1600×1060、1600×1080、1700×1000、1700×1050、1700×1210、1800×1000；"
            "没有两件同版式，没有一件是另一件的裁切或缩放。",
        "cross_piece_consistency":
            "跨件复核过的三组数字：1750 pH 8.19 / 2010 pH 8.07（case-03、04、05、06 一致）；"
            "2100 SSP1-1.9 8.06 与 SSP5-8.5 7.68（case-04、05、06 一致）；"
            "Ωarag 2010 全球 3.0、热带 3.4–3.6、极地 1.5–1.9、2100 2.9 / 1.6"
            "（case-06 与 case-07 一致）。",
        "honesty_rules_held":
            "投影全部虚线且注明非预测；两处主动留空（SSP2-4.5 与 SSP3-7.0 的 2100 端点、"
            "case-05 的恢复时间）；三处算术值明确标注为本任务计算；"
            "case-09 有五行标注「未取」且页脚说明「未取不是 NOAA 的分类」。",
        "residual_weaknesses": [
            "case-08 与 case-06 的核心文献（Jiang 2023、Kroeker 2013）本任务只拿到"
            "检索结果摘要，若取得全文可能需要按全文再核对一次口径。",
            "case-09 只有两行有完整符号，矩阵视觉上偏空——这是记录状态，不是数据缺失。",
            "case-07 的阈值主导来源是翼足类，外推到其他钙化生物的不确定度未量化。",
        ],
    },
    "unresolved_issues": [
        "四篇核心文献（Jiang 2023 / Kroeker 2013 / Bednaršek 2014 / IPCC SROCC 第5章）"
        "只取得 websearch 摘要，未直接抓取全文。",
        "pmc.ncbi.nlm.nih.gov/PMC6901524 返回 reCAPTCHA 质询页，已排除出已读来源。",
        "NOAA Ocean Today 页抓取超时，仅保留摘要，只支撑一条来源结论级判定。",
        "化学式使用 ASCII 记法而非下标，因为 DejaVu Sans Mono 的下标字符未在本任务验证。",
    ],
}
io.open(os.path.join(OUT, "portfolio.json"), "w", encoding="utf-8",
        newline="\n").write(json.dumps(portfolio, ensure_ascii=False, indent=2))
print("wrote portfolio.json with", len(cases), "cases")
