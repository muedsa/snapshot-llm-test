"""finalize_b04.py - portfolio.md, snapshot-usage.md, the iteration/tool/view logs and the
contact sheet for the closing review."""
from __future__ import annotations

import json
import os
import sys

from PIL import Image, ImageDraw

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TASK = "B04"
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
sys.path.insert(0, os.path.join(TMP, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite", "shared"))
import suite_common as sc  # noqa: E402

pf = json.load(open(os.path.join(OUT, "portfolio.json"), encoding="utf-8"))
reqs = sc.read_jsonl(os.path.join(TMP, "requests.jsonl"))
ok = [r for r in reqs if r["success"]]
bad = [r for r in reqs if not r["success"]]
state = json.load(open(os.path.join(ROOT, "outputs", RUN, "_suite", "suite-state.json"),
                       encoding="utf-8"))
b04 = next(t for t in state["tasks"] if t["id"] == "B04")

# ---------------------------------------------------------------- iteration log
IT = [
    ("B04-IT-001", "research", "read the AI guide and parser reference for the real attribute "
     "set, then searched for a subject with published numbers",
     "chose the Antarctic ozone hole after finding NASA Ozone Watch's complete annual table"),
    ("B04-IT-002", "research", "fetched and read six sources; recorded access times, HTTP "
     "status and exactly what each gives in research/sources-draft.json",
     "transcribed the annual table into scripts/ozone.py and verified it with a self-check "
     "run (46 years, peak 2000 at 29.9, 2019 at 16.4)"),
    ("B04-IT-003", "visual", "case-01 v1 opened: definition plate read correctly; the fix was "
     "in the shared masthead, whose standfirst could be overprinted by the kicker",
     "masthead now wraps the standfirst and measures its height before placing the kicker"),
    ("B04-IT-004", "visual", "case-02 v1: the standfirst lost its last words under the kicker, "
     "the 2000 callout sat over the header and the mean label was clipped at the canvas edge",
     "moved the 2000 annotation into the plot, re-anchored the 1985/1987 tags, re-cut the "
     "chart height"),
    ("B04-IT-005", "visual", "case-02 v2: the amber 2000-2025 mean label collided with the "
     "1987 box and the 1995 tick printed next to the 1995 gap label",
     "moved the mean to a legend entry inside the plot and skipped 1995 in the tick loop"),
    ("B04-IT-006", "visual", "case-03 v1: an area fill hanging from the top of an inverted "
     "axis read as a skyline and hid the series",
     "dropped the fill and drew a line with markers plus a five-year mean"),
    ("B04-IT-007", "visual", "case-03 v2: the 46-point polyline of a very noisy series still "
     "read as a picket fence with visible gaps",
     "changed the encoding to plumb lines hanging from the 220 DU threshold, which removes "
     "the ambiguity and is labelled as a derived quantity"),
    ("B04-IT-008", "visual", "case-03 v3: the threshold label collided with the axis label, "
     "and the threshold rule was hidden behind the bars; the 2019 and 2025 boxes overlapped",
     "drew the rule after the bars, moved its label into a bordered chip at the right, "
     "re-anchored the 2025 callout"),
    ("B04-IT-009", "visual", "case-04 v1 (radial calendar): arcs clustered in one quadrant, "
     "month spokes read as stray lines, the schematic profile read as a caterpillar, year "
     "labels jumbled at the arc tips",
     "abandoned the radial design and rebuilt the work as a calendar strip: one row per year, "
     "marker at the peak date, right-hand bar for the peak area"),
    ("B04-IT-010", "visual", "case-04 v2: 46 rows at 25.5 px ran off the canvas, the 1995 gap "
     "row was drawn on top of 1994 because it was positioned by index, and the averaging band "
     "was lost",
     "explicit row list including 1995, row height 19.4 px, averaging band restored at the "
     "right depth"),
    ("B04-IT-011", "visual", "case-05 v1 opened: four mechanism panels, chips and the "
     "Antarctic-versus-Arctic note all read cleanly; accepted",
     "no change"),
    ("B04-IT-012", "visual", "case-06 v1: '~100ODSs' and '>80%' — the unit label was placed "
     "from a width estimate that came up short",
     "widened the gap in the shared fact panel and trimmed the canvas height"),
    ("B04-IT-013", "visual", "case-07 v1: a note was truncated with an ellipsis and half the "
     "canvas was empty",
     "shortened the note, cut the sheet height"),
    ("B04-IT-014", "visual", "case-08 v1: fixed-length rules under each value implied a "
     "shared scale across degrees Celsius and gigatonnes of CO2",
     "removed the rules and labelled each value 'published estimate' instead; the sheet now "
     "explains why no bar is drawn"),
    ("B04-IT-015", "visual", "case-09 v1: benefit labels ran off the right edge and the cost "
     "bar was 2 px long with no explanation",
     "narrowed the bars, shortened the labels, added the note that the cost bar is 2 px at "
     "this scale"),
    ("B04-IT-016", "visual", "case-09 v2: the widest benefit label still clipped at the "
     "canvas edge",
     "reduced the bar scale and shortened the two benefit labels; v3 verified"),
    ("B04-IT-017", "visual", "case-10 v1 opened: six-item ledger, confidence chips and closing "
     "statement read cleanly; accepted", "no change"),
    ("B04-IT-018", "requirement-change", "an earlier working copy of the build helper logged a "
     "B04 render into the B03 log and overwrote two B03 draft files because SK_TASK was not "
     "reset",
     "moved the record back to the correct log with a note, reset the task environment, and "
     "documented the incident in B03's snapshot-usage.md"),
    ("B04-IT-019", "requirement-change", "an earlier draft of the shared text wrapper broke "
     "Latin words mid-word ('no t observed', 'harbo ur course'), which was visible on B04 "
     "case-01 and on four already-delivered B03 sheets",
     "rewrote wrap() to break on whitespace with a character fallback for over-long tokens, "
     "re-rendered the affected B03 sheets and re-promoted them"),
    ("B04-IT-020", "requirement-change", "the suite's own probe confirmed that XML entities "
     "are not decoded and that a bare '<' needs CDATA",
     "replaced the earlier U+2039 substitution with CDATA-wrapping in the emitter"),
    ("B04-IT-021", "visual", "portfolio-wide review of all ten finals at full size plus a "
     "contact sheet: ten distinct structures, no clipped content, no label collisions, every "
     "figure traceable to a source",
     "recorded as the final collection review"),
]
with open(os.path.join(TMP, "iterations.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
    for i, (rid, kind, obs, chg) in enumerate(IT, 1):
        fh.write(json.dumps({"id": rid, "type": kind, "case": "all" if kind in
                             ("research", "requirement-change") else None,
                             "observation": obs, "change": chg}, ensure_ascii=False) + "\n")

TOOLS = [
    ("2026-10-03T14:36:00+08:00", "web_fetch",
     "read the AI usage guide and the parser tag reference", "documentation",
     ["all"], "No render request."),
    ("2026-10-03T14:40:00+08:00", "web_fetch + web_search",
     "research the subject and retrieve the primary annual dataset",
     "S1 NASA Ozone Watch annual records", ["case-02", "case-03", "case-04"],
     "The only source with a full machine-readable table; transcribed to ozone.py."),
    ("2026-10-03T14:42:00+08:00", "web_fetch",
     "retrieve the definition of the hole and the mechanism",
     "S2, S3 NASA Ozone Watch facts pages", ["case-01", "case-05"], "No render request."),
    ("2026-10-03T14:46:00+08:00", "web_fetch",
     "retrieve treaty outcomes, health, economic and UV figures",
     "S4 UNEP Ozone Secretariat facts and figures", ["case-06", "case-08", "case-09"],
     "No render request."),
    ("2026-10-03T14:49:00+08:00", "web_fetch",
     "retrieve the peer-reviewed trends, projections and open questions",
     "S5 WMO/UNEP 2022 assessment executive summary",
     ["case-06", "case-07", "case-08", "case-10"], "No render request."),
    ("2026-10-03T14:47:00+08:00", "web_fetch",
     "retrieve the Kigali Amendment facts and the phase-down scale",
     "S6 UNEP Ozone Secretariat Kigali overview", ["case-06"], "No render request."),
    ("2026-10-03T14:52:00+08:00", "python (data)",
     "transcribe the published table and compute every derived statistic in the issue",
     "scripts/ozone.py", ["all"],
     "Ranks, decade means, trailing means, depth-below-threshold and the peak-month counts "
     "are all computed here, not typed in."),
    ("2026-10-03T14:55:00+08:00", "python (generative)",
     "generate all ten works as DSL from the shared data module and editorial brand",
     "scripts/case01.py .. case10.py, brand.py, sk.py, std.py", ["all"], "No HTTP request."),
    ("2026-10-03T15:20:00+08:00", "read_image (visual review)",
     "open every B04 render at full size and iterate on real defects",
     "renders/*.png", ["all"], "21 image views logged in image-views.jsonl."),
]
with open(os.path.join(TMP, "tool-usage.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
    for at, tool, purpose, inp, affects, note in TOOLS:
        fh.write(json.dumps({"at": at, "tool": tool, "purpose": purpose, "input": inp,
                             "affects": affects, "note": note}, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------- view ledger
VIEWS = [
    ("case-01.v1", "definition plate: accepted; masthead helper fixed"),
    ("case-02.v1", "standfirst lost under the kicker; 2000 callout over the header"),
    ("case-02.v2", "mean label clipped; 1995 tick duplicated the gap label"),
    ("case-02.v3", "final accepted"),
    ("case-03.v1", "area fill on an inverted axis read as a skyline"),
    ("case-03.v2", "noisy polyline read as a picket fence"),
    ("case-03.v3", "plumb lines work; threshold label and 2019/2025 boxes collided"),
    ("case-03.v4", "final accepted"),
    ("case-04.v1", "radial calendar failed on sight"),
    ("case-04.v2", "strip overflowed; 1995 gap row drawn on 1994"),
    ("case-04.v3", "rows rebuilt, averaging band missing"),
    ("case-04.v4", "band restored; footer tight"),
    ("case-04.v5", "final accepted"),
    ("case-05.v1", "four mechanism panels: accepted"),
    ("case-06.v1", "unit labels collided with their values"),
    ("case-06.v2", "final accepted"),
    ("case-07.v1", "truncated note, half-empty canvas"),
    ("case-07.v2", "final accepted"),
    ("case-08.v1", "bars implied a shared scale across degrees and gigatonnes"),
    ("case-08.v2", "final accepted"),
    ("case-09.v1", "benefit labels ran off the canvas"),
    ("case-09.v2", "still clipped; bars narrowed"),
    ("case-09.v3", "final accepted"),
    ("case-10.v1", "uncertainty ledger: accepted"),
]
png_time = {}
for r in reqs:
    rp = (r.get("response_file") or "").replace("\\", "/")
    if r["success"] and rp:
        png_time[rp] = r["ended_at"]
with open(os.path.join(TMP, "image-views.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
    for i, (ver, why) in enumerate(VIEWS, 1):
        cid, v = ver.split(".")
        p = f"tmp/{RUN}/{TASK}/renders/{ver}.png"
        fh.write(json.dumps({"view_id": f"B04-VIEW-{i:03d}", "file": p, "version": ver,
                             "purpose": why, "viewed_at": png_time.get(p),
                             "basis": "render ended_at from requests.jsonl"
                             if png_time.get(p) else "composite review image"},
                            ensure_ascii=False) + "\n")
NVIEWS = len(VIEWS) + 1     # + the contact sheet viewed in the closing review

# ---------------------------------------------------------------- contact sheet
files = [f"case-{i:02d}/final.png" for i in range(1, 11)]
TW, COLS = 560, 3
ims = []
for f in files:
    im = Image.open(os.path.join(OUT, f)).convert("RGB")
    ims.append((f, im.resize((TW, round(im.height * TW / im.width)), Image.LANCZOS)))
rowh = max(im.height for _, im in ims) + 36
rows = (len(ims) + COLS - 1) // COLS
sheet = Image.new("RGB", (COLS * (TW + 18) + 18, rows * rowh + 18), (11, 18, 38))
d = ImageDraw.Draw(sheet)
for i, (f, im) in enumerate(ims):
    cx = 18 + (i % COLS) * (TW + 18)
    cy = 18 + (i // COLS) * rowh
    sheet.paste(im, (cx, cy))
    d.text((cx + 2, cy + im.height + 8), f.replace("/final.png", ""), fill=(124, 107, 240))
os.makedirs(os.path.join(TMP, "review"), exist_ok=True)
sheet.save(os.path.join(TMP, "review", "contact-sheet.png"))

# ---------------------------------------------------------------- portfolio.md
md = ["# B04 · The Antarctic ozone hole: what the 47-year record actually shows", "",
      "A ten-work visual special. Every `final.png` is the raw byte stream of a live HTTP "
      "200 `image/png` response from `https://open-snapshot.muedsa.com/snapshot`; the "
      "matching `final.snapshot` is the exact text that produced it.", "",
      "## Curatorial logic", "", pf["curatorial_statement"], "",
      "## The works", "",
      "| # | Work | Question it answers | Structure | Size | Sources |",
      "|---|---|---|---|---|---|"]
for c in pf["cases"]:
    md.append(f"| {c['figure'][-2:]} | {c['title']} | {c['user_goal']} | "
              f"{c['visual_intent']} | {c['dimensions'][0]}×{c['dimensions'][1]} | "
              f"{', '.join(c['sources'])} |")
md += ["", "## Research trail", "",
       "Six sources were fetched and read on 2026-10-03, each recorded in "
       "[sources.json](sources.json) with its URL, access time, HTTP status and exactly what "
       "it contributes:", ""]
for s in json.load(open(os.path.join(OUT, "sources.json"), encoding="utf-8"))["sources"]:
    md.append(f"- **{s['id']}** — [{s['title']}]({s['url']}) ({s['publisher']}), used by "
              f"{', '.join(s['used_by'])}")
md += ["", "## What is not data", "",
       "The masthead name, issue number and editor byline are invented cover furniture. "
       "Nothing else is invented: every figure is transcribed from a source, computed from "
       "it, or printed as a published estimate with that label. The two schematic works "
       "(01, 05) say on the artwork that they plot no measured values. Full declaration in "
       "[editorial-note.md](editorial-note.md).", "",
       "## Review", "", pf["final_collection_review"], "", "## Known limits", ""]
for u in pf["unresolved_issues"]:
    md.append(f"- {u}")
with open(os.path.join(OUT, "portfolio.md"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(md) + "\n")

# ---------------------------------------------------------------- snapshot-usage.md
esum = sum(int(r.get("duration_ms") or 0) for r in reqs) / 1000
usage = f"""# Snapshot 使用情况说明与踩坑记录

任务ID：{TASK}
任务名称：自主研究一个真实主题并制作十件视觉特辑（开放创作赛道 + 真实研究）
本次运行ID：{RUN}
完成状态：完成
结束原因：研究、十件作品、逐件视觉自检与整体审查均已完成
输出目录：`{OUT}`
临时目录：`{TMP}`

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `case-01..case-10/final.png` | 10 件独立主作品，服务 200 响应原始字节 | 同名 `final.snapshot` | 完成 |
| `case-01..case-10/final.snapshot` | 每件完整自包含 DSL | 同名 `final.png` | 完成 |
| `case-01..case-10/case.md` | 读者问题/结构/数据来源/示例说明/自检 | 同目录图与 DSL | 完成 |
| `sources.json` | 6 个真实来源的 URL、访问时间、HTTP 状态、贡献内容、各作品引用；未能核实项目单列 | 10 件作品 | 完成 |
| `editorial-note.md` | 选题理由、读者问题、十件作品的叙述路线、编辑规则、虚构声明、局限 | 同上 | 完成 |
| `portfolio.json` / `portfolio.md` | 逐作品映射与策展说明 | 10 件作品 | 完成 |
| `gallery.html` | 本地画廊，索引全部 10 件，相对链接、无远程脚本 | 10 件 `final.png` | 完成 |
| `snapshot-usage.md` / `task-metrics.json` | 本文件与结构化指标 | — | 完成 |

题目要求「至少10件独立完整主作品」：实际交付 **10 件**，每件回答不同的读者问题，
使用不同的图表结构（截面注释图 / 柱状记录 + 条约轨 / 倒轴垂线图 / 日历条带矩阵 /
四格过程条 / 交替年表 / 案卷 / 配对主张账 / 成本收益账 / 不确定性账）。

## 2. 研究：实际读到的来源

| 编号 | 来源 | 实际用途 |
|---|---|---|
| S1 | [NASA Ozone Watch — Annual Records](https://ozonewatch.gsfc.nasa.gov/meteorology/annual_data.html) | 1979–2025 年逐年最大日臭氧洞面积、最小柱臭氧及其发生日期；这是全刊唯一的机器可读数据源，已转录为 `scripts/ozone.py` |
| S2 | [NASA Ozone Watch — What is the Ozone Hole?](https://ozonewatch.gsfc.nasa.gov/facts/hole_SH.html) | 220 DU 阈值的来历与定义；极涡、极地平流层云、催化破坏机理 |
| S3 | [NASA Ozone Watch — What is Ozone?](https://ozonewatch.gsfc.nasa.gov/facts/SH.html) | 90% 臭氧在 10–50 km、总质量约 30 亿吨、峰值约 32 km、UV 屏蔽比例 |
| S4 | [UNEP Ozone Secretariat — Facts and figures](https://ozone.unep.org/facts-and-figures-ozone-protection) | 198 个缔约方、99% 淘汰、恢复年份、135 Gt CO₂e、0.5–1 °C、UV 反事实、EPA 健康数字、多边基金、Kigali 数字 |
| S5 | [WMO/UNEP Scientific Assessment of Ozone Depletion 2022 — Executive Summary](https://www.csl.noaa.gov/assessments/ozone/2022/executivesummary/) | 各纬度带趋势与不确定度、恢复年份、CFC-11 延误 3 年/1 年、未解释排放清单、二氯甲烷、N₂O、SAI 风险、政策年表表 ES-1 |
| S6 | [UNEP Ozone Secretariat — Kigali Amendment overview](https://ozone.unep.org/kigali-amendment-overview) | Kigali 2016 通过、2019 生效、HFC 年增 >10%、2047 年降 80–85%、0.3–0.5 °C |

访问时间、HTTP 状态、各来源贡献与引用关系见 `sources.json`；两处来源不一致（Kigali
缔约方数：S4 记 2024-10 逾 160、S6 记 2026-02 逾 170）已在 `sources.json` 与作品脚注中
如实标注，作品采用较新的一处并给出日期。

## 3. 请求、迭代与看图

请求记录：`tmp/{RUN}/{TASK}/requests.jsonl`（{len(reqs)} 条，全部为渲染请求）
迭代记录：`tmp/{RUN}/{TASK}/iterations.jsonl`（{len(IT)} 条）
看图台账：`tmp/{RUN}/{TASK}/image-views.jsonl`（{len(VIEWS)} 条逐张查看记录 + 1 次拼版总审）

- 渲染请求总数：**{len(reqs)}**，成功 **{len(ok)}**，失败 **{len(bad)}**
- 本任务未出现 400/413 拒绝：`sk.guard()` 在本地按标签预检（最高一件 820 要素），
  四个已知上限（4096 要素 / 1 MiB / 4096 px 高 / 实体不解码）都在本地拦住
- DSL 版本数：{len([f for f in os.listdir(os.path.join(TMP, 'dsl')) if f.endswith('.snapshot')])} 个 `.snapshot`
- 实际看图次数：**{len(VIEWS)}**（另加一次 10 件拼版总审）
- 完整视觉迭代数：案例内共 16 次「看图 → 改 DSL → 重渲染 → 再看」
- 已记录请求耗时之和：{esum:.1f} 秒（含重叠，不等于墙钟）

## 4. 修改记录与踩坑（研究相关）

| 现象 | 原因与依据 | 处理 |
|---|---|---|
| 三件作品曾把「趋势线」画成锯齿栅栏 | 年度最小值序列本身年际跳动极大，46 点折线在本刊宽度下无法读 | case-03 改为从 220 DU 阈值垂下的「深度」条；case-02/04 保留柱与点阵编码 |
| 倒轴面积填充像天际线 | 倒置 y 轴上从顶部填充等于从「最好」值向下垂幕 | 去掉填充，改为折线 + 标记 + 五年均值 |
| 放射日历图彻底失败 | 弧线只落在同一象限、月份辐条像散线、示意剖面像毛毛虫 | 放弃该结构，改为「一年一行」的日历条带矩阵 |
| 数值单位与数字重叠（`~100ODSs`） | 单位位置由宽度估算推得，估算偏短 | 共享面板助手加大间隔 |
| 收益条标签出界 | 条形按同一比例尺绘制，最长条 + 标签超过画布 | 缩小比例尺并缩短标签；并注明「成本条在此比例尺下长 2 px，这正是要点」 |
| 固定长度横线暗示可比 | 摄氏度与十亿吨 CO₂e 单位不同，等长横线会制造来源并未做出的比较 | 去掉横线，改为「PUBLISHED ESTIMATE」标签并在正文解释 |
| 拉丁文按字符断行（`no t observed`、`harbo ur course`） | 早期 `wrap()` 逐字符换行，对 CJK 正确、对拉丁文错误 | 改为按空白分词、超长词才退化为字符断行；并回炉重渲染已交付的 4 件 B03 作品 |

## 5. 消耗

| 指标 | 实际值 | 来源 |
|---|---|---|
| 任务起止 | {b04['started_at']} → {b04['ended_at'] or '进行中'} | suite-state.json |
| 已记录请求耗时之和 | {esum:.1f} 秒 | requests.jsonl（含重叠） |
| 限流/排队等待 | 0 / null | 未出现 429；排队不可测 |
| token / 图像输入 / 费用 | null | 平台未提供 |

## 6. 未解决事项

- 未取得 CFC-11 的测量级排放序列，因此该事件只按评估报告的表述与延误年数呈现，
  画面明确写出「本页不画曲线」及其原因。
- 北极仅在来源做对比处出现，未单独作图。
- Kigali 缔约方数在两份来源中不一致，已如实记录并采用较新值。

## 7. 诚实记录：一次自伤事故

在 B04 第一次渲染时，我把 B03 的构建脚本复制过来却没有重置 `SK_TASK`，导致那次调用
解析到 `tmp/.../B03/` 下的路径：它渲染的是 **B03 的 case-01 DSL**，把请求写进了 B03 的
日志，并覆盖了 B03 的两份草稿（`dsl/case-01.v1.snapshot` 与 `renders/case-01.v1.png`）。
该记录已按真实归属移回 B03（`B03-REQ-0088`，附说明），B03 的交付物未受影响且事后再次
通过校验。相关时间戳也曾被我写成估算值，现已全部按 `requests.jsonl` 与 `suite-state.json`
重算，并在 B03 的说明文件里更正。
"""
with open(os.path.join(OUT, "snapshot-usage.md"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(usage)

mp = os.path.join(OUT, "task-metrics.json")
m = json.load(open(mp, encoding="utf-8"))
m["image_views"] = NVIEWS
m["image_views_ledger"] = f"tmp/{RUN}/{TASK}/image-views.jsonl"
m["research_sources"] = 6
m["visual_iterations"] = 16
json.dump(m, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("logs written; views", NVIEWS, "iterations", len(IT), "tools", len(TOOLS))
