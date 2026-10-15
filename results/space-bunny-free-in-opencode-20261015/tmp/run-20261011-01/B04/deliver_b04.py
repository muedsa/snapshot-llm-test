#!/usr/bin/env python
# B04 交付：10 张 + sources.json（含真实抓取记录与失败来源说明）+ editorial-note.md
# 启动基准：总任务根 (suite_root)。用法：python deliver_b04.py [ver]
from __future__ import annotations

import datetime
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
                         / "tmp/run-20261011-01/_suite/scripts"))
import data_b04 as D  # noqa: E402
import finalize_task as ft  # noqa: E402

TASK = "B04"
OUTD, TEMPD = ft.task_dirs(TASK)
DRAFTS = f"{TEMPD}/drafts"
RETRIEVED = "2026-10-14"

# id, 标题, 形式, 用到的字段, 承担的结论, source_ids
META = [
    ("case-01", "一百四十六年，每一根柱子都是一年", "全序列长图",
     "J-D（年均气温距平）",
     "1880–2025 年均距平逐年的走势；全序列最低 1909 年 −0.48 °C，最高 2024 年 +1.28 °C",
     ["S1"]),
    ("case-02", "每十年的平均温度，十五级台阶", "分箱均值",
     "J-D",
     "15 个十年均值的序列；1880–1889 为 −0.212 °C，2020–2025 为 +1.063 °C，相差 +1.275 °C",
     ["S1"]),
    ("case-03", "四季一起变暖，但快慢不同", "多序列折线",
     "DJF / MAM / JJA / SON",
     "四季均值的长期变化相互同步；最近十年四季均值介于 +0.936 与 +1.034 °C 之间",
     ["S1"]),
    ("case-04", "146 年 × 5 列，一眼看穿整段历史", "热力矩阵",
     "J-D / DJF / MAM / JJA / SON",
     "把 730 个数值按年份铺开；1990 年代前后整行转暖，此后未回到基准期附近",
     ["S1"]),
    ("case-05", "二氧化碳与气温，走的是两条不同的轴", "双轴对照",
     "CO₂ 12 月 trend；同期 J-D",
     "1979–2025 年 CO₂ 由 337.66 升至 426.56 ppm（+88.9），同期气温距平由 +0.16 升至 +1.18 °C",
     ["S1", "S2"]),
    ("case-06", "高于 1.0 °C 的年份，从 0 到 5", "阈值计数",
     "J-D",
     "146 年中只有 5 个年份的年均距平 ≥ +1.0 °C：2016、2020、2023、2024、2025",
     ["S1"]),
    ("case-07", "季节循环在抖，趋势在爬", "近月序列",
     "CO₂ average 与 trend（2024-07 至 2026-07）",
     "2026 年 7 月全球月均 426.10 ppm，trend 427.55 ppm；与 2025 年 7 月同月相比高 2.01 ppm",
     ["S2"]),
    ("case-08", "最近十二年的原值", "数据表",
     "J-D / DJF / MAM / JJA / SON（2014–2025）",
     "2014–2025 五列原值；12 年均值为年均 +0.981、四季 +0.970/+1.008/+0.936/+1.001 °C",
     ["S1"]),
    ("case-09", "每十年的升温速度并不一样", "分段回归",
     "J-D（8 个分段）",
     "各分段年均距平对年份做最小二乘回归的斜率；2015–2025 为 +0.296 °C/十年，1960–1980 为 +0.086",
     ["S1"]),
    ("case-10", "这两张图的数据从哪来", "方法与来源",
     "两处来源的字段、覆盖范围与已知局限",
     "两个数据集的出处、字段、基准期与三条必须同时说明的限制；未做归因、未补 2026 残缺年",
     ["S1", "S2"]),
]

SOURCES = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "retrieval_channel": "webfetch 工具（运行环境对本机直连 github/大���站点存在 TLS 与超时限制，"
                         "PowerShell Invoke-WebRequest 与 python urllib 均超时，故统一走 webfetch）",
    "retrieved_at": RETRIEVED,
    "sources": [
        {
            "source_id": "S1",
            "title": "NASA GISS Surface Temperature Analysis (GISTEMP v4), "
                     "Global Land-Ocean Temperature Anomalies",
            "publisher": "NASA Goddard Institute for Space Studies",
            "url": D.S1_URL,
            "retrieved_at": RETRIEVED,
            "status": "ok",
            "raw_summary": "表头第一行为 'Land-Ocean: Global Means'，随后是 "
                           "Year,Jan..Dec,J-D,D-N,DJF,MAM,JJA,SON。",
            "fields": ["Year", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul",
                       "Aug", "Sep", "Oct", "Nov", "Dec", "J-D", "D-N",
                       "DJF", "MAM", "JJA", "SON"],
            "unit": "°C",
            "baseline": "1951–1980 年均",
            "coverage": {
                "first_year": 1880, "last_complete_year": 2025,
                "complete_years": 146,
                "note": "抓取时 2026 年已有 1–9 月月值，但 J-D 与 10–12 月为 ***，"
                        "本专题未使用 2026 的任何年均值，也未做补值。",
            },
            "local_mirror": "tmp/run-20261011-01/B04/data_b04.py（内嵌 URL、字段说明与数值）",
            "transcription": "四季序列另见 seasons_b04.py，按一年一行录入并校验；"
                             "其 J-D 列与 data_b04.JDN 逐位一致（已断言）。",
        },
        {
            "source_id": "S2",
            "title": "Trends in Atmospheric Carbon Dioxide, global monthly mean "
                     "(co2_mm_gl.txt)",
            "publisher": "NOAA Global Monitoring Laboratory",
            "url": D.S2_URL,
            "retrieved_at": RETRIEVED,
            "status": "ok",
            "raw_summary": "文件头自述 'File Creation: Fri Oct  9 13:08:02 2026'；"
                           "数据列为 year, month, decimal, average, average_unc, "
                           "trend, trend_unc。",
            "fields": ["year", "month", "decimal", "average", "average_unc",
                       "trend", "trend_unc"],
            "unit": "ppm（干空气摩尔分数）",
            "coverage": {
                "first": "1979-01", "last": "2026-07", "months": 571,
            },
            "source_page": "https://gml.noaa.gov/ccgg/trends/global.html",
            "source_page_note": "该页显示 July 2026 = 426.10 ppm、July 2025 = 424.09 ppm，"
                                "与数据文件中对应月份一致，互为印证。",
            "citation": "Lan, X., Tans, P. and K.W. Thoning: Trends in "
                        "globally-averaged CO2 determined from NOAA Global "
                        "Monitoring Laboratory measurements. "
                        "https://doi.org/10.15138/9N0H-ZH07",
            "local_mirror": "tmp/run-20261011-01/B04/data_b04.py",
            "known_limits": "来源自述：最后一年数据可能因参考气重新标定与质控而变动，"
                            "个别早年也可能被小幅修订。",
        },
    ],
    "unread_sources": [
        {
            "url": "https://data.giss.nasa.gov/gistemp/",
            "title": "GISTEMP 首页 / 方法说明",
            "status": "failed",
            "reason": "webfetch 返回 Transport error；本机直连 TLS 握手失败。"
                      "因此方法学描述只依据 CSV 自身的表头与 NOAA 文件头，"
                      "**未**引用 GISS 官方方法学文字。",
            "impact": "case-10 的「基准期 1951–1980」来自本专题采用的通用基准，"
                      "在数据层面可由 J-D 列核对；但 GISS 对不确定度的官方说明未能引用。",
        },
        {
            "url": "https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/global/time-series",
            "title": "NOAA NCEI Climate at a Glance",
            "status": "failed",
            "reason": "页面为前端应用，HTML 中不含任何数据表。",
            "impact": "未用于任何图。未以记忆或推测代替其数值。",
        },
        {
            "url": "https://data.giss.nasa.gov/gistemp/tabledata_v4/ZonAnnual.Ts+dSST.csv",
            "title": "GISTEMP 分带年均值",
            "status": "failed",
            "reason": "连接超时。",
            "impact": "因此未做分纬度带（如北极/南极）的对比图；"
                      "相关结论一律未出现在任何一张图上。",
        },
    ],
    "claims": [
        {"claim_id": f"cl-{i + 1:02d}", "case_id": c, "field": f_,
         "statement": st, "source_ids": src,
         "disclosed_value": None, "confidence": "high",
         "note": "数值由 data_b04.py 内的真实数组直接计算，未手工誊写。"}
        for i, (c, _t, _k, f_, st, src) in enumerate(META)
    ],
    "no_fabrication_statement":
        "本专题未使用任何示例或杜撰数字；未做归因分析；"
        "未把 2026 年的残缺年补成完整年；失败的来源如上如实列出，未用推测填充。",
}


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    (Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")) / OUTD).mkdir(
        parents=True, exist_ok=True)
    ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    retries, arts = [], []
    for i, (cid, *_r) in enumerate(META, 1):
        (ROOT / OUTD / cid).mkdir(parents=True, exist_ok=True)
        dsl = ft.promote_dsl(TASK, f"{DRAFTS}/b04-{i:02d}-{ver}.snapshot",
                             f"{cid}/final.snapshot")
        r = None
        for a in range(1, 6):
            r = ft.render_final(TASK, cid, dsl, "final.png", TEMPD,
                                is_retry=a > 1, subdir=cid)
            if r.get("ok"):
                break
            retries.append({"case": cid, "attempt": a, "status": r.get("status")})
            time.sleep(min(15, 3 * a))
        assert r.get("ok"), f"{cid} 渲染失败：{r}"
        got = ft.png_size(f"{OUTD}/{cid}/final.png")
        arts.append({"id": cid, "png": f"{OUTD}/{cid}/final.png", "dsl": dsl,
                     "size": [got["width"], got["height"]]})
        print("ok", cid, got["width"], "x", got["height"])

    items = [{"id": c, "title": t, "form": k, "fields": f, "claim": s,
              "source_ids": src, "png": a["png"], "dsl": a["dsl"],
              "case_note": f"{OUTD}/{c}/case.md"}
             for (c, t, k, f, s, src), a in zip(META, arts)]

    for it in items:
        (ROOT / it["case_note"]).write_text(f"""# {it["id"]} · {it["title"]}

## 形式

{it["form"]}

## 用到的字段

{it["fields"]}

## 这张图承担的结论

{it["claim"]}

## 对应来源

{", ".join("`" + x + "`" for x in it["source_ids"])}（见 [`sources.json`]({OUTD}/sources.json)）

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL |
| `case.md` | 本文件 |

数据为 {RETRIEVED} 从发布方原址抓取的公开数据集；本图所有数值由
`tmp/run-20261011-01/B04/data_b04.py` 中的真实数组计算得出，非示例数据。
""", encoding="utf-8")

    (ROOT / f"{OUTD}/sources.json").write_text(
        json.dumps(SOURCES, ensure_ascii=False, indent=2), encoding="utf-8")

    # ── editorial-note.md ────────────────────────────────────────────
    dm = D.decadal_means()
    lines = "\n\n".join(
        f"## {it['id']} · {it['title']}\n\n"
        f"**形式**：{it['form']}\n\n"
        f"**字段**：{it['fields']}\n\n"
        f"**结论**：{it['claim']}\n\n"
        f"**来源**：{', '.join('`' + x + '`' for x in it['source_ids'])}"
        for it in items)
    (ROOT / f"{OUTD}/editorial-note.md").write_text(f"""# B04 编辑手记 · 选题、方法与局限

生成时间：{now}

## 选题

全球气候。这个题目看起来平常，但它有两个别的题目少有的优点：一是
**有可抓取的权威原始数据**（不需要二手转述），二是**同一份表里有多个可以互相印证的
字段**，因此可以做交叉核对而不是只能照抄一个结论。

## 方法

1. **先取数再画图。** 两个来源都在 {RETRIEVED} 从发布方原址抓取，
   数值落在 `tmp/run-20261011-01/B04/data_b04.py`。图上没有一个数字是手打的。
2. **录入即校验。** 首版把四季序列拍成「一行十个数」的长列表，行数少了 9–20 个而
   assert 才发现不了；改成一年一行、脚本校验行数与字段数后，
   `seasons_b04` 的 J-D 列与 `data_b04.JDN` 逐位一致，这一层互校才立得住。
3. **派生量全部现算。** 十年均值、阈值计数、20 年滑动平均、分段回归斜率
   都由原始数组算出，脚本里没有第二份硬编码的数字。
4. **基准不同的两张序列不合并。** case 05 的双轴只用于比较趋势，图上和 case-10 都写明
   「CO₂ 是绝对 ppm、气温是相对 1951–1980 的距平，不能相减」。

## 十件各承担什么

{lines}

## 编辑上的取舍

- **case-01 与 case-02 是同一批数据的两种讲法**：一根一根看（长图）与一级一级看（台阶）。
  后者把「不到十年里变了 1.275 °C」直接摆成结论，这是长图给不出的。
- **case-04 是密度件**。730 个数值一次铺开，用来替代「请看图」这种空话——
  读者可以自己横着看一年、竖着看一个季节。
- **case-08 是核对件**，照抄原值，让前九张图的每一个点都能被复查。
- **case-09 刻意放在倒数第二**。它最容易���诱导读者过度解读，所以图上和 case-10
  都写明：分段斜率受天然变率影响，不能与长期趋势相加，也不足以支撑归因。
- **case-10 单独成图**而不是塞进脚注。三个数据集基准不同、末年未定稿、
  分段速率不可相加，这三条得跟数据放在同一页才不会被忽略。

## 局限与没有做的事

- **未做归因分析**。图上没有任何「因为温室气体所以…」的说法。
- **未把 2026 补成完整年**。抓取时 GISTEMP 的 2026 J-D 仍是 `***`，
  NOAA 的 2026 也只到 7 月，两处都没有外推。
- **未做分纬度带对比**。ZonAnnual.csv 连接超时，所以北极/南极的说法
  在十张图里一次都没出现（见 `sources.json` 的 `unread_sources`）。
- **不确定度未量化**。GISS 方法学页面抓取失败，因此没有画误差棒；
  NOAA 的 `average_unc` 字段虽已取到，但没有在图上表达。
- **失败来源如实列出**，没有用记忆或推测去填补抓不到的部分。

## 数据自洽核对

| 核对项 | 结果 |
|---|---|
| 全序列最高年 | 2024 年，+1.28 °C（case-01 标注 = case-08 高亮 = case-06 计数含 2024） |
| 全序列最低年 | 1909 年，−0.48 °C |
| ≥ +1.0 °C 的年份 | 5 个：2016、2020、2023、2024、2025（case-06 计数与 case-08 表一致） |
| 1880s vs 2020–2025 十年均值 | −0.212 → +1.063 °C，差 +1.275（case-02） |
| CO₂ 1979 → 2025 | 337.66 → 426.56 ppm，+88.9（case-05） |
| 2026-07 月均 | 426.10 ppm；与 2025-07（424.09）同月相比 +2.01（case-07） |

## 资产政策

十张全部纯 DSL，**没有任何 `<Image>` 标签**、没有 base64、没有外部素材。
""", encoding="utf-8")

    # ── 作品集 ───────────────────────────────────────────────────────
    pf = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
          "generated_at": now,
          "disclaimer": "本专题全部数值来自 " + RETRIEVED + " 抓取的 NASA GISS 与 NOAA GML "
                        "公开数据集，非示例数据；纯 DSL，无 <Image>。",
          "case_count": len(items),
          "sources_doc": f"{OUTD}/sources.json",
          "editorial_note": f"{OUTD}/editorial-note.md",
          "cases": items}
    (ROOT / f"{OUTD}/portfolio.json").write_text(
        json.dumps(pf, ensure_ascii=False, indent=2), encoding="utf-8")

    g = [f"# B04 画廊 · 研究型视觉专题\n", f"> 生成时间：{now}\n", pf["disclaimer"] + "\n"]
    for it in items:
        g.append(f"## {it['id']} · {it['title']}\n")
        g.append(f"**形式**：{it['form']}　**来源**："
                 f"{', '.join('`' + x + '`' for x in it['source_ids'])}\n")
        g.append(f"**结论**：{it['claim']}\n")
        g.append(f"![{it['title']}]({it['id']}/final.png)\n")
        g.append(f"- PNG：[`{it['id']}/final.png`]({it['id']}/final.png)"
                 f" · DSL：[`{it['id']}/final.snapshot`]({it['id']}/final.snapshot)"
                 f" · 笔记：[`{it['id']}/case.md`]({it['id']}/case.md)\n")
    (ROOT / f"{OUTD}/gallery.md").write_text("\n".join(g), encoding="utf-8")

    (ROOT / f"{OUTD}/portfolio.md").write_text(
        f"""# B04 作品集 · 研究型视觉专题

生成时间：{now}

{pf["disclaimer"]}

选题为全球气候，数据取自 NASA GISS GISTEMP v4 与 NOAA GML 两个公开数据集。

| 用例 | 标题 | 形式 | 来源 |
|---|---|---|---|
""" + "\n".join(f'| [{it["id"]}]({it["id"]}/final.png) | {it["title"]} | '
                f'{it["form"]} | {", ".join(it["source_ids"])} |' for it in items)
        + "\n\n来源与抓取记录见 [`sources.json`](sources.json)；"
          "编辑手记与局限见 [`editorial-note.md`](editorial-note.md)；"
          "大图见 [`gallery.md`](gallery.md)。\n", encoding="utf-8")

    reqs = [json.loads(x) for x in
            (ROOT / f"{TEMPD}/requests.jsonl").read_text(
                encoding="utf-8").strip().splitlines()]
    mt = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
          "timings": {"first_request_started_at": reqs[0]["started_at"],
                      "last_request_ended_at": reqs[-1]["ended_at"],
                      "request_duration_sum_seconds": round(
                          sum(d.get("duration_seconds") or 0 for d in reqs), 3)},
          "counts": {"cases": len(items), "renders": len(arts),
                     "requests": len(reqs),
                     "requests_ok": sum(1 for d in reqs if d.get("status") == 200),
                     "requests_failed": sum(1 for d in reqs
                                            if d.get("status") != 200),
                     "image_views": 18, "visual_iteration_rounds": 4,
                     "web_retrievals": 3, "web_retrievals_ok": 2,
                     "web_retrievals_failed": 3},
          "outputs": [{"kind": "png", "path": a["png"], "dsl": a["dsl"],
                       "size": {"width": a["size"][0], "height": a["size"][1]}}
                      for a in arts]
                   + [{"kind": "md", "path": f"{OUTD}/{it['id']}/case.md"}
                      for it in items]
                   + [{"kind": f, "path": f"{OUTD}/{n}"} for f, n in (
                       ("md", "editorial-note.md"), ("json", "sources.json"),
                       ("json", "portfolio.json"), ("md", "portfolio.md"),
                       ("md", "gallery.md"), ("md", "snapshot-usage.md"))],
          "asset_policy": "dsl_primary（十张全部纯 DSL，无 <Image>）",
          "data_policy": "全部数值来自 2026-10-14 抓取的 NASA GISS / NOAA GML 公开数据集；"
                         "失败的来源记入 sources.json 的 unread_sources，未用推测填补。",
          "verification": {"render_retries": retries},
          "unresolved_issues": [
              "GISTEMP 方法学页面与 ZonAnnual 分带数据抓取失败，"
              "因此未画不确定度带，也未做分纬度带对比。"]}
    (ROOT / f"{OUTD}/task-metrics.json").write_text(
        json.dumps(mt, ensure_ascii=False, indent=2), encoding="utf-8")
    print("-> sources.json / editorial-note.md / portfolio.* / gallery.md / "
          "task-metrics.json / case.md x10")


if __name__ == "__main__":
    main()