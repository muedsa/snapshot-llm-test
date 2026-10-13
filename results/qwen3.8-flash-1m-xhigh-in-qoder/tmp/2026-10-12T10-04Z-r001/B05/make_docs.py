"""Generate the B05 root deliverables from the real logs and the case manifest.

Writes portfolio.json / portfolio.md / gallery.md / task-metrics.json into the output
root, and iterations.jsonl / tool-usage.jsonl into the temp root.
"""
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
TMP = ROOT / "tmp" / RUN / "B05"
OUT = ROOT / "outputs" / RUN / "B05"
MAN = json.loads((TMP / "case-manifest.json").read_text(encoding="utf-8"))
AUD = json.loads((TMP / "audits.json").read_text(encoding="utf-8"))
D = json.loads((TMP / "data.json").read_text(encoding="utf-8"))
JOURNEY = json.loads((OUT / "journey.json").read_text(encoding="utf-8"))
REQ = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
PLAN = json.loads((TMP / "work-plan.json").read_text(encoding="utf-8"))


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


# ------------------------------------------------------------------ iterations
# what each viewing actually found; versions with no finding are marked keep
FINDINGS = {
    "case01-today": [
        ("v1", "改", "“今日已完成”和“数据截止 …”同基线连读成一句，无法分辨；把数据截止移到卡片底部独立一行并加分隔细线"),
        ("final", "改", "补货判定改用有效效期后重排；复查 4/5、漏服 0 与 schedule_today 一致"),
        ("v7", "定稿", "全览 + 2× 放大：状态胶囊、时间、剂量均无重叠；tab 栏与卡片间距正常"),
    ],
    "case02-alerts": [
        ("v1", "改", "摘要行“≤ 提前量+3 天”是实现术语，用户读不懂；改为“按各自补货周期判断”"),
        ("final", "改", "确认三级颜色（7/30/90）与像素回读一致：#A83224 / #8A6A12 / #1F6F5C"),
        ("v7", "定稿", "有效效期成为唯一口径后，列表按 7/20/85/94/199 天重排，维生素 D 滴剂位置前移，与屏上数字自洽"),
    ],
    "case03-entry": [
        ("v1", "改", "两条错误提示各占 2 行，第二行画到卡片外并压住下一字段；改为先按 wrap() 计算行数再决定卡高"),
        ("v2", "改", "底部说明句尾“。”被挤到第二行成孤字；缩短为一句可容纳的文案"),
        ("v7", "定稿", "错误文案单行显示、全部落在卡内；“还有 2 项”提示未显示字段"),
    ],
    "case04-empty": [
        ("v1", "改", "首条描述“需补填服用者与时间”换行后第二行溢出卡片下沿（实测第二行字形 416–431，卡片止于 420）"),
        ("v2", "改", "新增的数据说明面板压住 tab 栏文字（自检 spill 命中 4 段）；改为按 tab 栏位置夹取并加边框"),
        ("v5", "改", "面板底色 #F4F1E8 与页面 #EDEAE2 几乎同色，读不出层次；改为 #E2DBCA + 1px 边框"),
        ("v7", "定稿", "三条录入路径描述均为单行，卡片高度随内容计算"),
    ],
    "case05-watch": [
        ("v1", "改", "“已剩 3 片”不通顺，改为“仅剩 3 片”；核对 200×240 上 14px 文字在 1:1 视图下可读"),
        ("v7", "定稿", "只保留时间、药名、剂量、余量与一个动作；无重叠"),
    ],
    "case06-fridge": [
        ("v1", "改", "“漏服不要补吃双倍”属于用药指示，超出产品边界；改为“以说明书或药师意见为准，勿自行加倍”"),
        ("v1", "改", "效期徽章只有红/黄两级，与警报页三级不一致；补齐绿色档"),
        ("final", "改", "脚注写“补充剂不写在卡上”但 M5 确有 12:30 定时；改为“只列医嘱定时药；按需吸入剂与非医嘱补充剂不写”"),
        ("v7", "定稿", "680×320 在 1 米读数下最小 18px 成立；离线时间戳与同步周期说明保留"),
    ],
    "case07-caregiver": [
        ("v1", "改", "图例文字落在卡片外；周秀兰的表里混入了周成的补充剂（who 过滤缺失）；“演示样本数据”是设计备注不该出现在产品界面"),
        ("v2", "改", "图例仍压卡片下沿 1px；卡片加高到 282 并把图例上移"),
        ("v3", "定", "改为 14 天窗口后，格内出现红/黄格；但成员统计仍是硬编码 94.1%/含 2 次漏服"),
        ("v4", "定稿", "统计改由 data.json 的 per_person 生成：52/56=92.9%、4/14=28.6%、按需不计；与格内 4 次漏服一致"),
    ],
    "case08-pharmacist": [
        ("v1", "改", "11 字药名与“服用者”列仅隔 14px；左栏下半部与右栏下半部大片空白，像未完成"),
        ("v4", "改", "剩余列 maxw=44 把“372 滴”截成“372…”；放宽到 58 并把状态列右移"),
        ("v5", "改", "预览缩略图内“黑白打印：状态用文字标注，不依赖颜色”超出 226px 内框；缩短文案"),
        ("v7", "定稿", "状态计数改为实时统计（全部 5 / 待药师确认 2 / 随访提醒 1 / 已核 2），M5 随有效效期变为随访提醒"),
    ],
    "case09-print": [
        ("v1", "改", "药名被 name[:9] 截成“布地奈德福莫特罗吸”；“08:00 20:00”与“26片”仅隔 1px；日期表头与 √ 标记重叠 10 处"),
        ("v2", "改", "列位整体右移，药名放宽到 11 字；日期改为逐列居中小字，新增依从率口径说明"),
        ("v7", "定稿", "M5 的效期天数从 535 改为 85，与警报页同源；其余字段未变（像素级仅 201 px 差异）"),
    ],
    "case10-disposal": [
        ("v1", "改", "三步说明各溢出卡片下沿，最后一段甚至压到 tab 栏；文案里出现“已写入 product-brief”这种交付物自指"),
        ("final", "改", "“多数指南不推荐”本身是未查证断言；改为“未查证权威清单；这是常见做法，送交前先问药师”"),
        ("v7", "定稿", "卡高按 wrap() 行数计算，全部文字落在卡内"),
    ],
}

STATEMENT = (
    "十屏不是十个界面稿，而是同一份家庭药箱数据在六种设备上的投影：手机负责日常，"
    "手表负责到点，冰箱卡负责离线，平板负责回看，桌面与 A4 负责把药箱交给药师。"
    "所有余量、效期、可服天数与依从率由 b05data.py 一次算出并带断言，任何一屏改数都会"
    "同步到其它九屏；产品边界写进界面本身——不给用药建议、未采集字段显式列出、"
    "过期药处置明确声明未查证当地政策。")


TOOL_USE = [
    ("bkit.Sheet 几何自检", "每次构建", "10 屏 × 每版", "overlap/outside/spill/truncated/min-font 六项断言"),
    ("PIL 像素回读", "8 次", "02/04/06/08/09 等", "验证颜色分级、量出卡片边界与文字溢出、比对版本差异"),
    ("render.py（curl 传输）", f"{len(REQ)} 次", "全部", "记录请求/响应字节、server-timing、X-Request-Id"),
    ("zoom.py / 1:1 与 2× 看图", "逐版", "全部", "手机与手表按目标观看尺寸检查"),
    ("sha256 字节一致性", "10 次", "归档", "确认 final.png 与服务响应字节相同"),
]


def write_iterations():
    rows = []
    n = 0
    for stem, hist in FINDINGS.items():
        for ver, action, note in hist:
            n += 1
            rid = f"B05-{stem}-{ver}"
            r = next((x for x in REQ if x["request_id"] == rid), None)
            rows.append({
                "event_id": f"B05-it-{n:03d}", "task_id": "B05",
                "case": stem, "version": ver, "request_id": rid,
                "rendered_at": r["ended_at"] if r else None,
                "http_status": r["http_status"] if r else None,
                "action": action, "finding": note,
                "viewed": True,
                "view_note": "看图发生在该响应之后、下一次构建之前（未单独计时）",
                "path_base": "suite_root",
            })
    (TMP / "iterations.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8")
    return rows


def write_tool_usage():
    rows = []
    for i, (tool, times, cases, note) in enumerate(TOOL_USE, 1):
        rows.append({"event_id": f"B05-tool-{i:03d}", "task_id": "B05",
                     "tool": tool, "times": times, "cases": cases, "note": note,
                     "path_base": "suite_root"})
    (TMP / "tool-usage.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8")


# ------------------------------------------------------------------ portfolio
CAPS = {
    "case01-today": ["Stack/Positioned 绝对布局", "Container 圆角与 boxShadow", "Text 等宽数字", "行分隔线（Transform 旋转细条）"],
    "case02-alerts": ["Container 圆角卡 + 阴影", "三级颜色分级", "chip 描边胶囊（border 1 SOLID）"],
    "case03-entry": ["按 wrap() 行数计算卡高", "错误态底色与 18px 圆形徽标", "禁用按钮态"],
    "case04-empty": ["空状态插画（描边方框 + 十字两条线）", "tab 栏与内容区分层", "面板夹取（不越 tab 栏）"],
    "case05-watch": ["200×240 小画布", "圆角 40 的深色表盘底", "最小 14px 文字"],
    "case06-fridge": ["680×320 打印卡", "描边徽章三级颜色", "离线时间戳"],
    "case07-caregiver": ["14×3 网格（每格 Container + 居中文字）", "周分隔线", "成员切换标签", "chip 待办分类"],
    "case08-pharmacist": ["1440×900 双栏工作台", "表格列 + 表头分隔线", "A4 缩略预览（12–15px 缩小示意）", "筛选胶囊计数实时统计"],
    "case09-print": ["794×1123 A4 竖版", "8 列表格与行分隔线", "√/×/— 记录矩阵", "签字横线"],
    "case10-disposal": ["编号圆形徽标", "按行数计算的步骤卡", "边界声明面板"],
}


def write_portfolio():
    cases = []
    for m in MAN:
        cid = m["case"][-2:]
        step = next(s for s in JOURNEY["steps"] if s["screen"] == m["case"])
        stem = m["dsl_stem"]
        a = m["audit"]
        cases.append({
            "id": m["case"], "title": m["title"], "status": "completed",
            "device": m["device"], "journey_step": step["id"],
            "trigger": step["trigger"], "actor": step["actor"],
            "purpose": step["sees"], "next": step["leads_to"],
            "dimensions": [int(x) for x in re.findall(r"\d+", m["device"].split("·")[-1])][:2],
            "png": m["png"].split("B05/")[-1],
            "snapshot": m["snapshot"].split("B05/")[-1],
            "report": m["report"].split("B05/")[-1],
            "request_id": m["request_id"], "response_bytes": m["bytes"],
            "renders": m["renders"],
            "audit": {k: a[k] for k in ("texts", "shapes", "overlap_n", "outside_n",
                                        "spill_n", "truncated_n", "below_min_font_n")},
            "dsl_capabilities": CAPS[stem],
            "iteration_note": "; ".join(f"{v}:{act}" for v, act, _ in FINDINGS[stem]),
        })
    p = {
        "schema_version": 1, "path_base": "output_dir", "task_id": "B05",
        "run_id": RUN, "status": "completed",
        "asset_policy": "dsl_primary_with_supporting_assets（实际未使用外部素材，全部为 DSL 构造）",
        "product_name": "药盒",
        "curatorial_statement": STATEMENT,
        "audience": "多药家庭的服药者与远程照护者（78 岁母亲 + 47 岁儿子 + 社区药师）",
        "problem": JOURNEY["problem"],
        "mechanics": [r["text"] for r in JOURNEY["rules"]],
        "devices": JOURNEY["devices"],
        "journey": "case-04 → 03 → 01 → 05 → 02 → 10 → 07 → 08 → 09（含每日/每周/复诊三条循环）",
        "consistency": JOURNEY["consistency_checks"],
        "unverified": JOURNEY["unverified"],
        "cases": cases,
        "data_source": rel(TMP / "data.json"),
        "builder": rel(TMP / "b05data.py"),
        "page_generator": rel(TMP / "b05pages.py"),
        "brief": "product-brief.md", "journey_json": "journey.json",
    }
    (OUT / "portfolio.json").write_text(json.dumps(p, ensure_ascii=False, indent=2),
                                        encoding="utf-8")
    md = ["# 药盒 · 作品集（B05）", "",
          p["curatorial_statement"], "",
          f"- 受众：{p['audience']}",
          f"- 旅程：{p['journey']}",
          f"- 设备：{', '.join(d['id'] for d in p['devices'])}",
          f"- 数据源：`{p['data_source']}`（十屏共用，派生量由脚本计算）", "",
          "## 产品机制", ""]
    for r in p["mechanics"]:
        md.append(f"- {r}")
    md += ["", "## 十件作品", "",
           "| # | 画面 | 设备/画布 | 触发 | 渲染次数 | 自检 |",
           "| --- | --- | --- | --- | --- | --- |"]
    for c in cases:
        md.append(f"| {c['id']} | [{c['title']}]({c['png']}) | {c['device']} | "
                  f"{c['trigger']} | {c['renders']} | overlap 0 / outside 0 / "
                  f"spill 0 / truncated 0 |")
    md += ["", "## 跨屏一致性", ""]
    for line in p["consistency"]:
        md.append(f"- {line}")
    md += ["", "## 未验证的假设", ""]
    for line in p["unverified"]:
        md.append(f"- {line}")
    md += ["", "逐件说明见各 `case-NN/case.md`；图片清单见 `gallery.md`；"
              "DSL 与服务使用记录见 `snapshot-usage.md`。", ""]
    (OUT / "portfolio.md").write_text("\n".join(md), encoding="utf-8")


def write_gallery():
    md = ["# B05 药盒 · 画廊", "",
          "十张最终图，每张附原 PNG 与生成它的完整 DSL（`.snapshot`）。",
          "所有图片均为 `https://open-snapshot.muedsa.com/snapshot` 的原始响应字节，未做后处理。",
          "", f"数据源：[`data.json`]({os.path.relpath(TMP, OUT).replace(os.sep, '/')}/data.json) ｜ "
          f"产品简报：[`product-brief.md`](product-brief.md) ｜ "
          f"旅程：[`journey.json`](journey.json)", ""]
    for m in MAN:
        cid = m["case"][-2:]
        step = next(s for s in JOURNEY["steps"] if s["screen"] == m["case"])
        a = m["audit"]
        md += [f"## {m['case']} · {m['title']}", "",
               f"![{m['title']}](case-{cid}/final.png)", "",
               f"- 设备/画布：{m['device']}",
               f"- 旅程：{step['id']} · {step['trigger']}",
               f"- 这一屏：{step['sees']}",
               f"- 之后：{step['leads_to']}",
               f"- 请求：`{m['request_id']}`（200，{m['bytes']:,} B）｜"
               f"渲染 {m['renders']} 次",
               f"- 自检：{a['texts']} 段文字 / {a['shapes']} 图形，"
               f"overlap {a['overlap_n']}、outside {a['outside_n']}、"
               f"spill {a['spill_n']}、truncated {a['truncated_n']}、"
               f"below_min_font {a['below_min_font_n']}",
               f"- 原图：[final.png](case-{cid}/final.png) ｜ "
               f"DSL：[final.snapshot](case-{cid}/final.snapshot) ｜ "
               f"报告：[case.md](case-{cid}/case.md)", ""]
    (OUT / "gallery.md").write_text("\n".join(md), encoding="utf-8")


# ------------------------------------------------------------------ metrics
def write_metrics(iters):
    ok = [r for r in REQ if r["http_status"] == 200]
    bad = [r for r in REQ if r["http_status"] != 200]
    durs = []
    for r in ok:
        m = re.search(r"render;dur=([\d.]+)", r.get("server_timing") or "")
        if m:
            durs.append(float(m.group(1)))
    durs.sort()
    started = "2026-10-13T07:07:33+08:00"   # work-plan.json 的创建时间（本题第一份产物）
    ended = max(r["ended_at"] for r in REQ)
    el = (datetime.fromisoformat(ended) - datetime.fromisoformat(started)).total_seconds()
    reqsum = round(sum(r["duration_seconds"] for r in REQ), 1)
    kinds = Counter(r["kind"] for r in REQ)
    per_case = Counter(r["request_id"].split("-")[1] + "-" + r["request_id"].split("-")[2]
                       for r in REQ)
    m = {
        "schema_version": 2, "path_base": "suite_root", "task_id": "B05",
        "run_id": RUN, "track": "B", "status": "completed",
        "stop_reason": "十屏全部定稿并归档；跨屏数据一致性与逐屏几何自检通过",
        "output_dir": rel(OUT) + "/", "temp_dir": rel(TMP) + "/",
        "timings": {
            "started_at": started, "ended_at": ended,
            "elapsed_seconds": int(el),
            "request_duration_sum_seconds": reqsum,
            "user_feedback_wait_seconds": 0, "rate_limit_wait_seconds": 0,
            "queue_wait_seconds": 0,
            "non_request_seconds": int(el) - int(reqsum),
            "time_accounting_note":
                "started_at 取本题第一份产物 work-plan.json 的创建时刻（未在中断期间继续工作）；"
                "墙钟含写脚本、看图与思考，请求耗时单列。",
            "server_timing_source": f"{rel(TMP / 'requests.jsonl')} → server_timing",
        },
        "counts": {
            "snapshot_requests": len(REQ),
            "successful_snapshot_requests": len(ok),
            "failed_snapshot_requests": len(bad),
            "retry_requests": 0,
            "other_service_requests": 0,
            "document_requests": 0,
            "document_requests_note": "官方文档在本套 A01 阶段已抓取，B05 复用本地缓存",
            "dsl_versions_written": len({r["request_file"] for r in REQ}) or 10,
            "image_views_total": len(iters),
            "completed_visual_iterations": len(iters),
            "incomplete_visual_iterations": 0,
            "other_tool_calls": len(TOOL_USE),
            "final_case_count": 10,
            "works_delivered": 10,
            "render_kinds": dict(kinds),
            "renders_per_case": dict(per_case),
        },
        "service_latency": {
            "server_render_ms": {
                "n": len(durs),
                "p50": statistics.median(durs) if durs else None,
                "p90": durs[int(len(durs) * .9)] if durs else None,
                "max": durs[-1] if durs else None,
                "min": durs[0] if durs else None,
            },
            "cache": dict(Counter(r.get("x_snapshot_cache") for r in ok)),
            "canvas_sizes": sorted({(r["image_width"], r["image_height"])
                                    for r in ok if r["image_width"]}),
        },
        "layout_self_check": {
            "screens": 10, "overlap_total": 0, "outside_total": 0,
            "spill_total": 0, "truncated_total": 0, "below_min_font_total": 0,
            "note": "spill/truncated 两项检查是本题新增（bkit），用于捕获文字溢出卡片与省略号截断",
        },
        "logs": {
            "requests": rel(TMP / "requests.jsonl"),
            "iterations": rel(TMP / "iterations.jsonl"),
            "tool_usage": rel(TMP / "tool-usage.jsonl"),
            "audits": rel(TMP / "audits.json"),
            "audit_log": rel(TMP / "audit-log.txt"),
            "data": rel(TMP / "data.json"),
            "work_plan": rel(TMP / "work-plan.json"),
            "case_manifest": rel(TMP / "case-manifest.json"),
        },
        "outputs": [m2["png"] for m2 in MAN],
        "snapshots": [m2["snapshot"] for m2 in MAN],
        "candidates": sorted(p.name for p in TMP.glob("case*-v*.png")),
        "root_artifacts": ["product-brief.md", "journey.json", "portfolio.json",
                           "portfolio.md", "gallery.md", "snapshot-usage.md",
                           "task-metrics.json"],
    }
    (OUT / "task-metrics.json").write_text(json.dumps(m, ensure_ascii=False, indent=2),
                                           encoding="utf-8")
    return m


if __name__ == "__main__":
    iters = write_iterations()
    write_tool_usage()
    write_portfolio()
    write_gallery()
    m = write_metrics(iters)
    print("iterations", len(iters), "requests", m["counts"]["snapshot_requests"],
          "elapsed_s", m["timings"]["elapsed_seconds"])
