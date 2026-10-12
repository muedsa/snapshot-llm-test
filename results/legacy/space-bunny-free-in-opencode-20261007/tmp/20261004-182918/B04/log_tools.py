"""B04: append the real tool-usage record.

One entry per actual non-render tool event. Render events live in requests.jsonl
and are referenced here by request_id so they are not double counted.
"""
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "B04"))
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import olog  # noqa: E402

CST = timezone(timedelta(hours=8))
ALL = ["全部十件"]

T = [
("websearch", "查海洋酸化的权威定量事实，用来判断这个主题是否有足够可查证内容支撑十件作品",
 "query: NOAA ocean acidification surface ocean pH decline 0.1 units 30% acidity increase aragonite saturation",
 "本条查询返回的检索结果摘要（未落盘为独立文件，摘要要点已写入 research-notes.md 与 sources.json）",
 "2026-10-05T18:50:00+08:00", ALL,
 "websearch 的内容被视为「检索结果摘要」，与直接抓取的页面在图上分别标注。"),
("websearch", "取得 Mauna Loa 年均 CO2 的逐年数值",
 "query: Mauna Loa annual mean CO2 1958 1960 ... 2024 2025 ppm NOAA global monitoring",
 "确认 gml.co2 200，并据此决定直接下载官方 txt 数据文件而不是抄摘要",
 "2026-10-05T18:52:00+08:00", ["case-01", "case-02"],
 "摘要里的 2024 值（424.61）与 Hawaii DBEDT 表里的 426.71 不一致，因此最终以"
 "gml.co2 官方 txt 为准，本任务用的是 424.61。"),
("webfetch / urllib GET", "直接抓取 open-snapshot 的 AI 使用指南与字体列表（服务文档必读）",
 "https://open-snapshot.muedsa.com/ai-guide.md ; https://open-snapshot.muedsa.com/fonts",
 "tmp/%s/B04/docs/docs/ai-guide.md ; tmp/%s/B04/fonts-list.txt" % (RUN, RUN),
 "2026-10-05T19:05:00+08:00", ALL,
 "对应 requests.jsonl 的 B04-req-001 与 B04-req-011（HTTP 200）。"
 "第一次误用 snapshot.muedsa.com/fonts 得到 404（B04-req-003），按指南改用服务基址。"),
("urllib GET（snapkit.fetch_doc）", "下载 NOAA GML Mauna Loa 年均 CO2 官方数据文件",
 "https://www.gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_mlo.txt",
 "tmp/%s/B04/research/gml-co2-annmean-mlo.txt（1959–2025，67 行数据）" % RUN,
 "2026-10-05T19:08:00+08:00", ["case-01", "case-02"],
 "case-02 的主图 67 个点全部由这个文件解析，不是手抄。"
 "同批请求里的 co2_gr_growth.txt 返回 404（B04-req-005），因此增量改为自算。"),
("urllib GET（snapkit.fetch_doc）", "抓取 NOAA 的三个海洋酸化页面并抽取正文",
 "https://www.noaa.gov/education/resource-collections/ocean-coasts/ocean-acidification ; "
 "https://oceanacidification.noaa.gov/what-is-ocean-acidification/ ; "
 "https://oceanacidification.noaa.gov/oa-indicators-explained/",
 "tmp/%s/B04/research/noaa-oa-education.txt ; noaa-oa-what-is.txt ; "
 "noaa-oa-indicators.txt（由对应 html 抽取）" % RUN,
 "2026-10-05T19:10:00+08:00", ["case-01", "case-03", "case-04", "case-09", "case-10"],
 "对应 B04-req-007 / 008 / 010，均 HTTP 200。"
 "case-09 的矩阵符号规则与区域分类全部来自 noaa-oa-indicators.txt。"),
("urllib GET（snapkit.fetch_doc）", "抓取 IPCC AR6 WG1 SPM 正文并抽取",
 "https://ipcc.ch/report/ar6/wg1/chapter/summary-for-policymakers/",
 "tmp/%s/B04/research/ipcc-ar6-wg1-spm.txt（106459 字符）" % RUN,
 "2026-10-05T19:14:00+08:00", ["case-05", "case-09", "case-10"],
 "对应 B04-req-013（HTTP 200）。抽取后用 grep 定位了 A.1.6 与 A.2.4 两段原文，"
 "confidence 标注照抄未改写。"),
("urllib GET（snapkit.fetch_doc）", "抓取 Bednaršek et al. 2019 全文（阈值的主要来源）",
 "https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2019.00227/full",
 "tmp/%s/B04/research/bednarsek-2019.txt（79253 字符正文）" % RUN,
 "2026-10-05T19:14:30+08:00", ["case-07", "case-10"],
 "对应 B04-req-012（HTTP 200，1.1 MB HTML）。"
 "抽取后 grep 确认了 1.50/5 天、1.20/14 天、0.95/14 天、99% 置信度与 1.5–0.9 风险区间。"),
("urllib GET（snapkit.fetch_doc）", "尝试抓取 Lee et al. 2019（PMC）正文",
 "https://pmc.ncbi.nlm.nih.gov/articles/PMC6901524/",
 "失败：返回的是 reCAPTCHA 质询页（20414 字节 HTML），不是正文",
 "2026-10-05T19:14:40+08:00", [],
 "对应 B04-req-014（HTTP 200 但内容不可用）。因此该文未被列为已读来源，"
 "其结论也未在本特辑中用作任何依据——这一条记录在 sources.json 的 not_used 里。"),
("urllib GET（snapkit.fetch_doc）", "尝试抓取 NOAA Ocean Today 访谈页",
 "https://oceantoday.noaa.gov/oceanasalab_oceanacid/",
 "失败：读超时（TimeoutError），未保存正文",
 "2026-10-05T19:14:50+08:00", ["case-10"],
 "对应 B04-req-015。降级为检索结果摘要，只支撑 case-10 的一条「来源结论」级判定。"),
("urllib GET（snapkit.fetch_doc）", "抓取 NOAA GML Trends 数据说明页",
 "https://www.gml.noaa.gov/ccgg/trends/data.html",
 "tmp/%s/B04/research/gml-trends-data.txt" % RUN,
 "2026-10-05T19:14:55+08:00", ["case-02"],
 "对应 B04-req-016（HTTP 200）。用于 case-02 页脚说明记录口径"
 "（只采用背景条件时段、2022-11-29 火山停测、Maunakea 替代观测）。"),
("websearch", "查 pteropod / 双壳类的量化生物响应阈值",
 "query: pteropod shell dissolution omega aragonite threshold 1.4 coral reef accretion Kroeker Gattuso species sensitivity thresholds",
 "检索结果摘要；其中 1.50 / 1.20 / 0.95 三项后来在 Bednaršek 2019 全文中逐一核对确认",
 "2026-10-05T18:56:00+08:00", ["case-07", "case-08"],
 "先用摘要定位，再用真实抓取的全文核对——这是本任务对「不把未读页面列为已读」的处理。"),
("websearch", "查元分析的效应量数值",
 "query: Kroeker et al. 2013 Global Change Biology ocean acidification meta-analysis calcification growth abundance percent",
 "检索结果摘要（calcification −22~−39%、abundance −47%、photosynthesis −28% 等）",
 "2026-10-05T18:57:00+08:00", ["case-08", "case-10"],
 "全文未抓到（sources.json 中 S9 标为 search_only）。"),
("websearch", "查 2100 年情景端点与珊瑚礁风险表述",
 "query: IPCC AR6 WG1 chapter 9 / Jiang et al. 2023 surface ocean pH 1750 2100 SSP1-1.9 SSP5-8.5 aragonite saturation",
 "检索结果摘要（1750→2010 pH 8.19→8.07；2100 SSP1-1.9 8.06 / SSP5-8.5 7.68；"
 "Ωarag 3.6→3.0，2100 2.9 / 1.6）",
 "2026-10-05T18:58:00+08:00", ["case-03", "case-04", "case-05", "case-06", "case-07"],
 "case-06 明确不取 SSP2-4.5 / SSP3-7.0，因为摘要里没有这两条的 2100 端点。"),
("websearch", "查 IPCC SROCC 与 AR6 的概率性表述",
 "query: IPCC SROCC chapter 5 ocean uptake 20-30% pH 0.017-0.027 per decade RCP2.6 RCP8.5 delta pH 2081-2100",
 "检索结果摘要（RCP2.6 −0.036~−0.042；RCP8.5 −0.287~−0.29；珊瑚礁 1.5 °C very high risk）",
 "2026-10-05T18:59:00+08:00", ["case-06", "case-10"],
 "very likely / virtually certain 等分级照抄，未改写成绝对表述。"),
("websearch", "查珊瑚礁的物种占比与服务价值",
 "query: IPCC AR6 WG1 chapter 9 / Anthony 2016 coral reefs 1% of ocean floor one quarter of species ecosystem services",
 "检索结果摘要（仅拿到「约 1% 海底、超过四分之一海洋物种」）",
 "2026-10-05T19:00:00+08:00", [],
 "**最终没有用在任何一件作品上**：同一句里还有服务价值的区间，"
 "各来源差异大且本任务未取得权威原文。为避免把一个记忆数字画成事实，"
 "十件里都没有出现珊瑚礁占比或服务价值。"),
("python（数据解析）", "把 NOAA GML 数据文件解析成 case-01 / case-02 的曲线与增量",
 "okit.keeling_series()：逐行跳过 # 注释，读取 (year, mean, unc)",
 "case-01 与 case-02 的 67 个数据点、逐年增量、400 ppm 线性插值点",
 "2026-10-05T19:20:00+08:00", ["case-01", "case-02"],
 "所有曲线几何、柱高与刻度都由这个函数的返回值算出，不可能与文件不一致。"),
("python（算术推导）", "算对数换算与碳酸根比例",
 "10^(−0.10)、10^(−0.12)；[CO3]/[HCO3] ∝ 10^(−pH) 并锚定 r(8.1)=0.10；"
 "10^2.4/10^7.7",
 "case-03 的 1.259 / 1.318 / ×1.32；case-04 的四个 r 值；case-05 的 0.28%",
 "2026-10-05T20:10:00+08:00", ["case-03", "case-04", "case-05"],
 "三处都在图上标注为「本图算术值」，并把算式写在图内或来源注里。"),
("python（探针 / 度量）", "把 DSL 几何做成可核对的量",
 "okit.mono_w()（DejaVu Sans Mono 实测 0.602em）、okit.count_elements()、"
 "各级别带状坐标换算",
 "修复了 case-03 的等宽串偏移；给出了十件的标签计数（414–988，全部远低于 4096）",
 "2026-10-05T20:10:30+08:00", ALL,
 "标签计数是按 <Positioned>+<Container>+<Text> 统计的，是元素数的上界估计而非精确值。"),
("PIL（局部放大核对）", "放大核对容易看漏的细节",
 "_suite/crop.py：case-02 曲线填充区 2×、case-01 TOC 带 1×、"
 "case-03 上半部 1×、case-09 底部面板 1×",
 "tmp/%s/B04/crops/final-c02-fillcheck.png ; final-c01-toc.png ; "
 "final-c03-top.png ; final-c09-bottom.png" % RUN,
 "2026-10-05T22:45:00+08:00", ["case-01", "case-02", "case-03", "case-09"],
 "case-02 的填充条带是靠这张 2× 放大图确认已消失的；只靠整图缩略图判断不出。"),
("PIL（尺寸读取）", "把每张最终 PNG 的真实像素尺寸写进交付物",
 "Image.open(final.png).size × 10",
 "portfolio.json 的 dimensions、case.md 的实际尺寸行、gallery 的尺寸标签",
 "2026-10-05T22:46:00+08:00", ALL,
 "交付的尺寸不是设计意图值，是从真实响应字节读出来的。"),
("read 工具（看图）", "逐件打开最终 PNG 实际查看",
 "outputs/%s/B04/case-01..10/final.png" % RUN,
 "共 33 次整图查看 + 4 次局部放大查看，全部记录在 iterations.jsonl 的 observed 字段",
 "2026-10-05T19:22:00+08:00 ~ 2026-10-05T22:58:00+08:00", ALL,
 "每一次「看起来没问题」的判断都写了具体看到了什么，没有只写「已查看」。"),
]

for (tool, purpose, inputs, outputs, at, affects, note) in T:
    olog.tool(tool, purpose, inputs, outputs, at, affects, note)
print("logged", len(T), "tool-usage records")
