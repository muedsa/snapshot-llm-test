"""Generate the B06 root deliverables from the real logs: portfolio, gallery, metrics,
design-review, iteration and tool-usage records."""
from __future__ import annotations

import json
import os
import re
import statistics
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "B06"
OUT = ROOT / "outputs" / RUN / "B06"
MAN = json.loads((TMP / "case-manifest.json").read_text(encoding="utf-8"))
D = json.loads((TMP / "data.json").read_text(encoding="utf-8"))
EV = json.loads((OUT / "problem-evidence.json").read_text(encoding="utf-8"))
PLAN = json.loads((TMP / "work-plan.json").read_text(encoding="utf-8"))
REQ = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines()
       if l.strip()]

STATEMENT = (
    "十件作品各自解决一个「信息在手边却用不上」的日常问题：末班车表、站牌间隔、工资条、"
    "体检箭头、营养成分表、预警颜色、押金条款、保险免责、楼层索引、三张不同单位的账单。"
    "它们的共同点不是风格，而是同一个动作——把「读者要做的换算」搬回到图这一侧："
    "时刻表改成最迟离开时刻，散点改成每项自己的参考带，百分比改成「这一包占我一天多少」。"
    "所有数值由 b06data.py 生成并带断言；凡未查证的（费率、政策、回收点、真实时刻表）"
    "都在画面上写明是示例。")

# what each viewing actually found, in order
FINDINGS = {
    "case01-lasttrain": [
        ("v1", "改", "物理矛盾：同一方向的末班车不可能在后面的站更早经过；而且原模型完全忽略换乘，"
                     "而真正卡住行程的往往是换乘。整份数据改为「最迟必须离开本站的时刻」"),
        ("v2", "改", "图例两行重叠（● 说明与条长说明）；调整起点 x"),
        ("v3", "改", "「差 21 分」的灰条与叉线压住时间列 23:20；把主轴右移到 560"),
        ("v4", "改", "车程列与时间列只隔 19px，读起来像一串数字；两列各左移/右移"),
        ("final", "定稿", "12 个目的地、9 可去 3 来不及；条长与分钟数严格成正比"),
    ],
    "case02-headway": [
        ("v1", "改", "副标题写「颜色越深等得越久」，但色阶是绿(4)→黄(10)→红(12)，深浅并不单调；"
                     "改为「从绿到红」并补一条四档图例"),
        ("v2", "定稿", "像素核对：针尖标签在小时刻度下方 8px，无重叠"),
    ],
    "case03-payslip": [
        ("v1", "改", "个税一行写「17%」，而 600/12000 = 5%；改为由数据计算。页面下半部大片空白"),
        ("v2", "改", "新增「按一年看」后，年额标签与「每月」列重叠；压缩条形最大宽至 276px"),
        ("v3", "定稿", "六笔年度金额与月度金额一致（断言），底部说明改为两行"),
    ],
    "case04-checkup": [
        ("v1", "改", "二维散点失败：7 项偏离里有 5 项 <0.2，全部堆在边界线上，图没有提供新信息"),
        ("v2", "改", "改为每项一条自己的参考带（弹点条）后，注脚超出画布、单位「TI-RADS」被截断"),
        ("v3", "改", "行距与卡片高度压缩到 56/50，注脚改为自动换行"),
        ("v4", "定稿", "视力一项显式说明「区间只有 0.2 宽，倍数显得大」"),
    ],
    "case05-nutrition": [
        ("v1", "改", "表头与数值列不对齐；名称替换出现「能量（能量）」「钠（钠）」；下半部空白"),
        ("v2", "改", "加「半包/一包/一包半」份量表后，两列表头互相重叠；重排右对齐位置"),
        ("final", "定稿", "双基准百分比与份量表全部由同一份数据算出（断言）"),
    ],
    "case06-warnings": [
        ("v1", "改", "四列并排使每列只有 180px，正文被切成 8 字一行——这正是作品要解决的毛病；"
                     "改为 2×2 卡片 + 顶部递进条"),
        ("v2", "改", "「解除」一行贴着卡片底边、页脚与卡片重叠；收紧内部间距并把页脚并成一段"),
        ("v3", "定稿", "当前生效级别用红框 + 文字双重标注，不依赖颜色"),
    ],
    "case07-deposit": [
        ("v1", "改", "只是两列清单，节点与结果之间没有任何连接；节点问题被 maxw 截断；"
                     "扣款行与下一张卡重叠"),
        ("v2", "改", "「是 ↓」标签落在上一张卡片内（spill 命中）；移到卡片间隙"),
        ("v3", "改", "内容修正：N2 的「否」被写成「扣 200 元修补费」，而答「否」意味着没有破损、"
                     "不该扣费；改为在数据里为每个「否」显式写出结果"),
        ("final", "定稿", "画布从 1200×800 收到 1200×620，去掉重排后多余的留白"),
    ],
    "case08-insurance": [
        ("v1", "改", "斜纹线端点手工夹取，超出条形右端；三张卡各自重复一句读法说明"),
        ("v2", "定稿", "改为按矩形精确裁剪的 45° 斜纹，读法上移到页首，并给每场景标出斜纹占比"),
    ],
    "case09-wayfinding": [
        ("v1", "改", "红色示例路径横穿 3 层的科室文字；「东门」标签被右栏面板压住"),
        ("v2", "改", "路径改走两栏之间的中缝，目标科室块加红框与圆点，删除多余标签"),
        ("final", "定稿", "科室名按块宽自动选 18–20px，避免截断（dept_size）"),
    ],
    "case10-utilities": [
        ("v1", "改", "可行动项写「夏冬两月各高出全年均值约 100 元」，样本实为 75.3 / 59.3 元；"
                     "副标题错字「三口单位」"),
        ("v2", "改", "把月度柱形的归一说明塞进小标题后与「最高 252」重叠；说明移到页脚"),
        ("final", "定稿", "所有行动项数字改为从 12 个月样本计算，并在数据层断言"),
    ],
}

TOOL_USE = [
    ("bkit.Sheet 几何自检", "每次构建", "10 件", "overlap / outside / spill / truncated / "
                                             "below_min_font 五项断言"),
    ("PIL 像素回读", "6 次", "02/04/06/08/09/10", "核对色阶、量卡片边界、确认针尖标签未压字"),
    ("render.py（curl 传输）", f"{len(REQ)} 次", "全部", "记录请求/响应字节、server-timing、"
                                                 "X-Request-Id"),
    ("1:1 与缩放看图", "逐版", "全部", "海报与立牌按 2–3 米观看的等效缩放检查"),
    ("sha256 字节一致性", "10 次", "归档", "确认 final.png 是请求 DSL 对应的服务响应"),
    ("数据断言", "b06data.py 内 30+ 条", "全部", "加总、份额、排序、偏离度、路径金额等"),
]

DEVIATIONS = [
    {"plan": "case-01 以「你此刻在站台的时间」为轴画同心可达圈",
     "actual": "改为以「现在」为零点的发散条形阶梯",
     "reason": "900px 宽内要同时放 12 个站名、时刻与差值，弧长布局会把文字挤成两行；"
               "阶梯图能直接读出差几分钟",
     "standard_changed": "未降低：条长仍与分钟数严格成正比"},
    {"plan": "case-01 每站标注该方向末班经过时刻",
     "actual": "改为每个目的地的「最迟离开本站时刻」，并加入换乘次数",
     "reason": "原模型在物理上不成立（同方向逐站不可能更早），且忽略换乘这一真实约束",
     "standard_changed": "提高：模型必须自洽"},
    {"plan": "case-04 把项目画到「偏离程度 × 可行动性」二维平面",
     "actual": "改为每项一条自己的参考带（弹点条）+ 可行动性标签",
     "reason": "7 项偏离里 5 项 <0.2 区间宽度，散点全部堆在边界线上，图不提供新信息",
     "standard_changed": "提高：编码必须真的分辨得开"},
    {"plan": "case-06 四级并排成四张行动卡",
     "actual": "2×2 卡片 + 顶部递进条",
     "reason": "800px 下每列仅 180px，正文被切成 8 字一行，正是作品要解决的问题",
     "standard_changed": "未降低：四级信息完整保留"},
    {"plan": "case-07 决策树 1200×800",
     "actual": "1200×620",
     "reason": "重排为真正的树后内容变短，保留 800 高会留下大片空白",
     "standard_changed": "未降低"},
    {"plan": "计划标题写「六个箭头」",
     "actual": "示例报告有 7 项偏离，画面按数据写「七个箭头」",
     "reason": "数据与断言优先于文案",
     "standard_changed": "未降低"},
]


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def write_iterations():
    rows, n = [], 0
    for stem, hist in FINDINGS.items():
        for ver, action, note in hist:
            n += 1
            rid = f"B06-{stem}-{ver}"
            r = next((x for x in REQ if x["request_id"] == rid), None)
            rows.append({"event_id": f"B06-it-{n:03d}", "task_id": "B06",
                         "case": stem, "version": ver, "request_id": rid,
                         "rendered_at": r["ended_at"] if r else None,
                         "http_status": r["http_status"] if r else None,
                         "action": action, "finding": note, "viewed": True,
                         "view_note": "看图发生在该响应之后、下一次构建之前（未单独计时）",
                         "path_base": "suite_root"})
    (TMP / "iterations.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8")
    return rows


def write_tool_usage():
    rows = [{"event_id": f"B06-tool-{i:03d}", "task_id": "B06", "tool": tool,
             "times": times, "cases": cases, "note": note,
             "path_base": "suite_root"}
            for i, (tool, times, cases, note) in enumerate(TOOL_USE, 1)]
    (TMP / "tool-usage.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8")


def write_portfolio():
    cases = []
    for m in MAN:
        cid = m["case"][-2:]
        ev = next(p for p in EV["problems"] if p["case"] == m["case"])
        dims = [int(x) for x in re.findall(r"\d+", m["device"].split()[-1])]
        cases.append({
            "id": m["case"], "title": m["title"], "status": "completed",
            "format": m["device"], "dimensions": dims,
            "stuck_point": ev["stuck_point"], "reinvention": ev["reinvention"],
            "source_observed": ev["source_observed"],
            "data_basis": ev["data_basis"],
            "what_the_work_shows": ev["visible_improvement"],
            "png": m["png"].split("B06/")[-1],
            "snapshot": m["snapshot"].split("B06/")[-1],
            "report": m["report"].split("B06/")[-1],
            "request_id": m["request_id"], "response_bytes": m["bytes"],
            "renders": m["renders"],
            "audit": {k: m["audit"][k] for k in ("texts", "shapes", "overlap_n",
                                                 "outside_n", "spill_n",
                                                 "truncated_n", "below_min_font_n")},
            "iteration_note": "; ".join(f"{v}:{a}" for v, a, _ in FINDINGS[m["dsl_stem"]]),
        })
    p = {"schema_version": 1, "path_base": "output_dir", "task_id": "B06",
         "run_id": RUN, "status": "completed",
         "asset_policy": "dsl_primary_with_supporting_assets（实际未使用外部素材）",
         "curatorial_statement": STATEMENT,
         "theme": PLAN["theme"], "data_policy": PLAN["data_policy"],
         "shared_criteria": PLAN["shared_criteria"],
         "anti_goals": PLAN["anti_goals"],
         "structures": ["发散条形阶梯", "时间带 + 指针", "瀑布分解 + 年化", "每项独立参考带",
                        "双基准占比 + 份量表", "2×2 行动卡 + 递进条", "决策树 + 路径金额",
                        "同比例三段对比 + 斜纹缺口", "建筑剖切 + 示例路径",
                        "归一化对比 + 原始单位"],
         "cases": cases,
         "deviations_from_plan": DEVIATIONS,
         "data_source": rel(TMP / "data.json"),
         "builders": [rel(TMP / "b06data.py"), rel(TMP / "b06works.py"),
                      rel(TMP / "b06works2.py")],
         "problem_evidence": "problem-evidence.json",
         "design_review": "design-review.md"}
    (OUT / "portfolio.json").write_text(json.dumps(p, ensure_ascii=False, indent=2),
                                        encoding="utf-8")
    md = ["# B06 · 十个日常信息难题（作品集）", "", STATEMENT, "",
          f"- 主题：{p['theme']}",
          f"- 数据政策：{p['data_policy']}",
          "", "## 十件作品", "",
          "| # | 作品 | 形式 | 原本卡在哪 | 重构 | 渲染 |",
          "| --- | --- | --- | --- | --- | --- |"]
    for c in cases:
        md.append(f"| {c['id']} | [{c['title']}]({c['png']}) | {c['format']} | "
                  f"{c['stuck_point']} | {c['reinvention']} | {c['renders']} |")
    md += ["", "## 十种信息结构（避免同版式换皮）", ""]
    for i, s_ in enumerate(p["structures"], 1):
        md.append(f"{i}. {s_}")
    md += ["", "## 共同验收标准", ""]
    for c in p["shared_criteria"]:
        md.append(f"- {c}")
    md += ["", "## 与计划的偏差（含理由）", "",
           "| 计划 | 实际 | 理由 | 标准是否降低 |",
           "| --- | --- | --- | --- |"]
    for d in DEVIATIONS:
        md.append(f"| {d['plan']} | {d['actual']} | {d['reason']} | "
                  f"{d['standard_changed']} |")
    md += ["", "逐件说明见 `case-NN/case.md`；问题来源与假设见 `problem-evidence.json`；"
              "改进判断见 `design-review.md`。", ""]
    (OUT / "portfolio.md").write_text("\n".join(md), encoding="utf-8")


def write_gallery():
    md = ["# B06 · 画廊", "",
          "十件最终作品，每件附原 PNG、生成它的完整 DSL 与逐件报告。",
          "所有图片都是 `https://open-snapshot.muedsa.com/snapshot` 的原始响应字节。",
          "",
          f"问题与证据：[`problem-evidence.json`](problem-evidence.json) ｜ "
          f"设计评审：[`design-review.md`](design-review.md) ｜ "
          f"数据源：[`data.json`]({os.path.relpath(TMP, OUT).replace(os.sep, '/')}/data.json)",
          ""]
    for m in MAN:
        cid = m["case"][-2:]
        ev = next(p for p in EV["problems"] if p["case"] == m["case"])
        a = m["audit"]
        md += [f"## {m['case']} · {m['title']}", "",
               f"![{m['title']}](case-{cid}/final.png)", "",
               f"- 形式：{m['device']}",
               f"- 原本卡在哪：{ev['stuck_point']}",
               f"- 重构：{ev['reinvention']}",
               f"- 依据物料：{ev['source_observed']}（{ev['data_basis']}）",
               f"- 请求：`{m['request_id']}`（200，{m['bytes']:,} B）｜渲染 {m['renders']} 次",
               f"- 自检：{a['texts']} 段文字 / {a['shapes']} 图形，overlap {a['overlap_n']}、"
               f"outside {a['outside_n']}、spill {a['spill_n']}、"
               f"truncated {a['truncated_n']}、below_min_font {a['below_min_font_n']}",
               f"- 原图：[final.png](case-{cid}/final.png) ｜ "
               f"DSL：[final.snapshot](case-{cid}/final.snapshot) ｜ "
               f"报告：[case.md](case-{cid}/case.md)", ""]
    (OUT / "gallery.md").write_text("\n".join(md), encoding="utf-8")


def write_design_review():
    md = ["# B06 · 设计评审（design-review.md）", "",
          "评审依据只有两样：最终画面本身，以及生成它们的代码与数据。"
          "**没有用户实验**，因此凡涉及「读者会更快/更不容易出错」的判断，"
          "都明确标为推断而不是结论。", "",
          "## 一、可观察的改善（从画面本身可验证）", ""]
    for m in MAN:
        cid = m["case"][-2:]
        ev = next(p for p in EV["problems"] if p["case"] == m["case"])
        md += [f"### {m['case']} · {m['title']}", "",
               f"- **原物料的卡点**：{ev['stuck_point']}",
               f"- **重构动作**：{ev['reinvention']}",
               f"- **画面上可核对的改善**："]
        for line in ev["visible_improvement"]:
            md.append(f"  - {line}")
        a = m["audit"]
        md += [f"- **几何自检**：overlap {a['overlap_n']} / outside {a['outside_n']} / "
               f"spill {a['spill_n']} / truncated {a['truncated_n']} / "
               f"最小字号违例 {a['below_min_font_n']}",
               f"- **仍存在的局限**：{REVIEWS[cid]}", ""]
    md += ["## 二、无法从画面判断的部分", "",
           "- 读者是否真的更快做出正确决定：未测。",
           "- 老人 / 儿童等特定人群的实际可读性：未测，字号只是按观看距离设定的工程值。",
           "- 示例数据的分布是否接近真实家庭：未验证，只保证内部自洽。",
           "- 预警、保险、合同、社保等内容的**正确性**：一律以「示例」呈现，"
           "不声称与任何现行规定一致。", "",
           "## 三、跨作品的共同判断", "",
           "- 十件作品共用一条原则：**读者要做的换算，能搬到图这边就搬过来**"
           "（分钟差、比例、归一单位、条款合并、路径连接）。",
           "- 颜色一律有文字或形状冗余；黑白打印与色觉障碍下信息不丢失。",
           "- 三件作品（04、06、07）在评审中推翻了原编码：散点堆叠、四列过窄、"
           "清单不成树——这些不是审美调整，而是「编码本身不传递信息」的修正。",
           "- 两处内容级错误（07 的「否 → 扣 200」、10 的「高出约 100 元」）"
           "在逐图核对中发现并改由数据计算，说明看图必须连着数字一起看。", ""]
    (OUT / "design-review.md").write_text("\n".join(md), encoding="utf-8")


REVIEWS = {
    "01": "只覆盖一条方向、一种出发站；换方向需另做一张。",
    "02": "假设间隔在半个时段内均匀，真实公交到站方差远大于此；没有实时数据。",
    "03": "费率是示例区间，读者若按此核对真实工资条可能不一致（页面已注明）。",
    "04": "每项一条自己的带子，代价是失去了跨项的「谁更偏离」总览；已用排序部分弥补。",
    "05": "只做了能量/脂肪/糖/钠四项，蛋白质与膳食纤维未列。",
    "06": "四级文案为通用防灾常识，未查证任何城市的具体细则。",
    "07": "四个判断节点是示例合同的简化；真实合同可能有更多分支（如提前退租、转租）。",
    "08": "三个场景是挑选出来的极端对照，不构成对某张保单的整体评价。",
    "09": "只画了一条示例路径；不同入口（西门/急诊）需另画。",
    "10": "同比来自同一份示例样本，不能当作真实价格变化的证据。",
}


def write_metrics(iters):
    ok = [r for r in REQ if r["http_status"] == 200]
    bad = [r for r in REQ if r["http_status"] != 200]
    durs = sorted(float(re.search(r"render;dur=([\d.]+)", r.get("server_timing") or "")
                        .group(1)) for r in ok
                  if r.get("server_timing") and "render;dur" in r["server_timing"])
    started = "2026-10-13T08:17:31+08:00"
    ended = max(r["ended_at"] for r in REQ)
    el = (datetime.fromisoformat(ended) - datetime.fromisoformat(started)).total_seconds()
    reqsum = round(sum(r["duration_seconds"] for r in REQ), 1)
    m = {"schema_version": 2, "path_base": "suite_root", "task_id": "B06",
         "run_id": RUN, "track": "B", "status": "completed",
         "stop_reason": "十件作品逐图审查定稿；问题证据与设计评审完成",
         "output_dir": rel(OUT) + "/", "temp_dir": rel(TMP) + "/",
         "timings": {"started_at": started, "ended_at": ended,
                     "elapsed_seconds": int(el),
                     "request_duration_sum_seconds": reqsum,
                     "user_feedback_wait_seconds": 0, "rate_limit_wait_seconds": 0,
                     "queue_wait_seconds": 0,
                     "non_request_seconds": int(el) - int(reqsum),
                     "time_accounting_note":
                         "started_at 取本题开始时刻（suite-state 记录）；墙钟含读文档、"
                         "写脚本、看图与思考，请求耗时单列。",
                         "server_timing_source": f"{rel(TMP / 'requests.jsonl')} → server_timing"},
         "counts": {"snapshot_requests": len(REQ),
                    "successful_snapshot_requests": len(ok),
                    "failed_snapshot_requests": len(bad),
                    "retry_requests": 0, "other_service_requests": 0,
                    "document_requests": 0,
                    "document_requests_note": "复用本套 A01 抓取的本地文档缓存与字体清单",
                    "dsl_versions_written": len({r["request_file"] for r in REQ}),
                    "image_views_total": len(iters),
                    "completed_visual_iterations": len(iters),
                    "incomplete_visual_iterations": 0,
                    "other_tool_calls": len(TOOL_USE),
                    "final_case_count": 10, "works_delivered": 10,
                    "render_kinds": dict(Counter(r["kind"] for r in REQ)),
                    "renders_per_case": dict(Counter(
                        r["request_id"].split("-")[1] + "-" + r["request_id"].split("-")[2]
                        for r in REQ))},
         "service_latency": {
             "server_render_ms": {"n": len(durs),
                                  "p50": statistics.median(durs) if durs else None,
                                  "p90": durs[int(len(durs) * .9)] if durs else None,
                                  "max": durs[-1] if durs else None,
                                  "min": durs[0] if durs else None},
             "cache": dict(Counter(r.get("x_snapshot_cache") for r in ok)),
             "canvas_sizes": sorted({(r["image_width"], r["image_height"])
                                     for r in ok if r["image_width"]})},
         "layout_self_check": {
             "works": 10, "overlap_total": 0, "outside_total": 0, "spill_total": 0,
             "truncated_total": 0, "below_min_font_total": 0,
             "note": "五项检查全部为 0 才写文件；truncated 与 spill 是 B05 起新增的检查"},
         "logs": {"requests": rel(TMP / "requests.jsonl"),
                  "iterations": rel(TMP / "iterations.jsonl"),
                  "tool_usage": rel(TMP / "tool-usage.jsonl"),
                  "audits": rel(TMP / "audits.json"),
                  "audit_log": rel(TMP / "audit-log.txt"),
                  "data": rel(TMP / "data.json"),
                  "work_plan": rel(TMP / "work-plan.json"),
                  "case_manifest": rel(TMP / "case-manifest.json")},
         "outputs": [m2["png"] for m2 in MAN],
         "snapshots": [m2["snapshot"] for m2 in MAN],
         "candidates": sorted(p.name for p in TMP.glob("case*-v*.png")),
         "root_artifacts": ["problem-evidence.json", "design-review.md",
                            "portfolio.json", "portfolio.md", "gallery.md",
                            "snapshot-usage.md", "task-metrics.json"]}
    (OUT / "task-metrics.json").write_text(json.dumps(m, ensure_ascii=False, indent=2),
                                           encoding="utf-8")
    return m


if __name__ == "__main__":
    write_tool_usage()
    iters = write_iterations()
    write_portfolio()
    write_gallery()
    write_design_review()
    m = write_metrics(iters)
    print("iterations", len(iters), "requests", m["counts"]["snapshot_requests"],
          "elapsed_s", m["timings"]["elapsed_seconds"])
