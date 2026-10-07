"""B04: write sources.json (real access log) and portfolio.json."""
import io
import json
import os
from datetime import datetime, timedelta, timezone

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMP = os.path.join(ROOT, "tmp", RUN, "B04")
OUT = os.path.join(ROOT, "outputs", RUN, "B04")
CST = timezone(timedelta(hours=8))
ACCESS = datetime(2026, 10, 5, 19, 5, 0, tzinfo=CST).isoformat()

S = json.load(io.open(os.path.join(TMP, "render-summary.json"), encoding="utf-8"))
reqs = [json.loads(l) for l in io.open(os.path.join(TMP, "requests.jsonl"),
                                        encoding="utf-8") if l.strip()]
req_by_id = {r["request_id"]: r for r in reqs}

# ----------------------------------------------------------------- sources ---
sources = [
 {"id": "S1", "kind": "primary_data_file", "title":
  "Mauna Loa Observatory annual mean atmospheric CO2 (NOAA GML)",
  "url": "https://www.gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_mlo.txt",
  "access_method": "real GET via snapkit.fetch_doc, HTTP 200",
  "request_id": "B04-req-004", "accessed_at": ACCESS,
  "local_copy": "tmp/%s/B04/research/gml-co2-annmean-mlo.txt" % RUN,
  "reused": False,
  "obtained": "1959–2025 共 67 个年均值与逐年不确定度（0.12 ppm）；"
              "文件头注明 1958-03 至 1974-05 的数据来自 Scripps，"
              "2022-11-29 起 Mauna Loa 因火山喷发停测、2022-12 至 2023-07-04 改用 Maunakea 观测站。",
  "used_by": ["case-01", "case-02"],
  "uncertainty": "文件自带 1σ = 0.12 ppm；本任务未做任何再处理或拟合。"},
 {"id": "S2", "kind": "agency_page", "title":
  "What is Ocean Acidification (NOAA Ocean Acidification Program)",
  "url": "https://oceanacidification.noaa.gov/what-is-ocean-acidification/",
  "access_method": "real GET + 正文抽取, HTTP 200",
  "request_id": "B04-req-010", "accessed_at": ACCESS,
  "local_copy": "tmp/%s/B04/research/noaa-oa-what-is.txt" % RUN, "reused": False,
  "obtained": "过去 250 年海洋平均酸度增加约 26%；碳酸解离与缓冲反应链；"
              "DIC 的三项定义；「碳酸根作为缓冲剂」段落；"
              "「大四指标」pH / pCO2 / TA / DIC，且「测两项即可算出另外两项」。",
  "used_by": ["case-01", "case-03", "case-04", "case-10"],
  "uncertainty": "页面本身是机构科普表述，未给出各数字的不确定度。"},
 {"id": "S3", "kind": "agency_page", "title": "Ocean acidification (NOAA 教育页)",
  "url": "https://www.noaa.gov/education/resource-collections/ocean-coasts/ocean-acidification",
  "access_method": "real GET + 正文抽取, HTTP 200",
  "request_id": "B04-req-007", "accessed_at": ACCESS,
  "local_copy": "tmp/%s/B04/research/noaa-oa-education.txt" % RUN, "reused": False,
  "obtained": "表层 pH 自工业革命以来下降约 0.1 个单位，约等于酸度增加约 30%；"
              "海洋吸收约 30% 的人为 CO2；海洋平均 pH 现约 8.1；"
              "pH 7 为中性；BAU 下世纪末表层 pH 可能约 7.8，"
              "上一次出现是中新世 1400–1700 万年前。",
  "used_by": ["case-01", "case-03", "case-05", "case-10"],
  "uncertainty": "同一机构在 S2 给出「约 26%」，差异来自所取 ΔpH 与取整，图上已注明。"},
 {"id": "S4", "kind": "agency_page", "title":
  "OA Indicators Explained (NOAA Ocean Acidification Program)",
  "url": "https://oceanacidification.noaa.gov/oa-indicators-explained/",
  "access_method": "real GET + 正文抽取, HTTP 200",
  "request_id": "B04-req-008", "accessed_at": ACCESS,
  "local_copy": "tmp/%s/B04/research/noaa-oa-indicators.txt" % RUN, "reused": False,
  "obtained": "7 个大型海洋生态区 / 11 个站位；三个表层指标 pCO2、pH、Ωar；"
              "百分位符号规则（+ 高于第 90 百分位、− 低于第 10 百分位、● 在 10–90 之间）"
              "与 2019–2024 五年趋势箭头规则；阿留申群岛与阿拉斯加湾的逐项状态；"
              "七个区域的英文分类措辞；页面自述的局限（仅表层、SOCAT 船测、高纬季节波动更大）。",
  "used_by": ["case-09", "case-10"],
  "uncertainty": "只有两区在取得文本中有逐项百分位与趋势；其余五区只取到文字分类，"
                "故 case-09 中标注「未取」，未反推符号。"},
 {"id": "S5", "kind": "assessment_report", "title":
  "IPCC AR6 WG1 Summary for Policymakers",
  "url": "https://ipcc.ch/report/ar6/wg1/chapter/summary-for-policymakers/",
  "access_method": "real GET + 正文抽取, HTTP 200",
  "request_id": "B04-req-013", "accessed_at": ACCESS,
  "local_copy": "tmp/%s/B04/research/ipcc-ar6-wg1-spm.txt" % RUN, "reused": False,
  "obtained": "A.1.6「It is virtually certain that human-caused CO2 emissions are the main "
              "driver of current global acidification of the surface open ocean」；"
              "A.2.4「surface open ocean pH as low as recent decades is unusual in the last "
              "2 million years (medium confidence)」；"
              "「过去 5000 万年表层开阔洋 pH 长期上升（high confidence）」；"
              "B.5.1 21 世纪酸化继续增加且百年到千年尺度不可逆。",
  "used_by": ["case-05", "case-09", "case-10"],
  "uncertainty": "原文自带置信度标注（virtually certain / medium confidence / high confidence），"
                "图上照抄而未改写。"},
 {"id": "S6", "kind": "peer_reviewed", "title":
  "Bednaršek et al. 2019, Systematic Review and Meta-Analysis Toward Synthesis of "
  "Thresholds of Ocean Acidification Impacts on Calcifying Pteropods (Front. Mar. Sci.)",
  "url": "https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2019.00227/full",
  "access_method": "real GET + 正文抽取（全文 HTML，1.1 MB）, HTTP 200",
  "request_id": "B04-req-012", "accessed_at": ACCESS,
  "local_copy": "tmp/%s/B04/research/bednarsek-2019.txt" % RUN, "reused": False,
  "obtained": "2097 个数据点 / 15 项研究的元分析与阈值分析；"
              "轻度溶壳 Ωar=1.50（暴露 5 天）、重度溶壳 Ωar=1.20（14 天），置信度 99%；"
              "幼体与成体致死 Ωar=0.95（14 天）；「Ωar 1.5–0.9 提供从预警到致死影响的风险区间」；"
              "牡蛎/贻贝幼体亚致死 Ωar 1.4 与 2、双壳类幼体急性 Ωar 1.2、贻贝 Ωar 1.8；"
              "叠加增温会放大溶壳与存活的敏感度。",
  "used_by": ["case-07", "case-10"],
  "uncertainty": "阈值带暴露时长依赖；原文为单个分类群的共识，外推到其他类群需谨慎。"},
 {"id": "S7", "kind": "assessment_report", "title":
  "IPCC SROCC Chapter 5 (检索结果摘要，未直接抓取全文)",
  "url": "https://www.ipcc.ch/site/assets/uploads/sites/3/2019/11/SROCC_FinalDraft_Chapter5.pdf",
  "access_method": "websearch 结果摘要（PDF 全文未抓取）",
  "request_id": None, "accessed_at": ACCESS, "local_copy": None, "reused": False,
  "obtained": "最近二十年海洋吸收占人为排放 20–30%（very likely）；"
              "1980s 末以来表层 pH 每十年下降 0.017–0.027（virtually certain）；"
              ">95% 近表层开阔海已受影响；2081–2100 相对 2006–2015 的 ΔpH："
              "RCP2.6 −0.036~−0.042、RCP8.5 −0.287~−0.29；"
              "RCP8.5 下北冰洋/南大洋/北太平洋/西北大西洋将变得「腐蚀性」，"
              "RCP2.6 下该后果 virtually certain 可避免；"
              "珊瑚礁在升温 1.5 °C 时面临 very high risk。",
  "used_by": ["case-06", "case-10"],
  "uncertainty": "未直接抓取全文，措辞按检索结果摘要转述；原报告自带 very likely / "
                "virtually certain 等分级，本特辑照抄而未改写。"},
 {"id": "S8", "kind": "peer_reviewed", "title":
  "Jiang et al. 2023, Global Surface Ocean Acidification Indicators From 1750 to 2100 "
  "(J. Adv. Modeling Earth Systems)（检索结果摘要，未直接抓取全文）",
  "url": "https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2022MS003563",
  "access_method": "websearch 结果摘要",
  "request_id": None, "accessed_at": ACCESS, "local_copy": None, "reused": False,
  "obtained": "1750→2010 全球面积平均 pH_T 8.19→8.07（约 −0.12）；"
              "1750→2000 约 −0.11（≈+30% 酸度）；2100 SSP1-1.9 到 8.06（−0.01）、"
              "SSP5-8.5 到 7.68（−0.39）；Ωarag 3.6（1750）→3.0（2010，−17%），"
              "2100 SSP1-1.9 −2% 到 2.9、SSP5-8.5 −47% 到 1.6；"
              "2010 热带 3.4–3.6、极地 1.5–1.9；热带 −16% vs 北极 −24%；"
              "海洋吸收人为 CO2 的 20–30%，若无海洋吸收大气约高 80 ppm。",
  "used_by": ["case-03", "case-04", "case-05", "case-06", "case-07", "case-10"],
  "uncertainty": "未直接抓取全文；SSP2-4.5 与 SSP3-7.0 的 2100 端点本任务未取得，"
                "case-06 标注「未取」，未做插值。"},
 {"id": "S9", "kind": "peer_reviewed", "title":
  "Kroeker et al. 2013, Impacts of ocean acidification on marine organisms: "
  "a systematic review and meta-analysis (Global Change Biology)（检索结果摘要）",
  "url": "https://onlinelibrary.wiley.com/doi/10.1111/gcb.12179",
  "access_method": "websearch 结果摘要",
  "request_id": None, "accessed_at": ACCESS, "local_copy": None, "reused": False,
  "obtained": "珊瑚/球石藻/软体动物钙化 −22~−39%；全部钙化生物生长 −9~−17%；"
              "珊瑚丰度（着底量）−47%；钙化藻光合 −28%、丰度 −80%；"
              "硅藻生长 +22%、肉质藻 +18%；甲壳类钙化与鱼类生长未检出显著效应；"
              "珊瑚钙化 LnRR 的 95% CI 宽度示例约 0.48。",
  "used_by": ["case-08", "case-10"],
  "uncertainty": "未直接抓取全文；范围值是分类群间区间，不是置信区间，图上已注明。"},
 {"id": "S10", "kind": "peer_reviewed", "title":
  "Bednaršek et al. 2014, Dissolution Dominating Calcification Process in Polar "
  "Pteropods Close to the Point of Aragonite Undersaturation (PLOS ONE)（检索结果摘要）",
  "url": "https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0109183",
  "access_method": "websearch 结果摘要",
  "request_id": None, "accessed_at": ACCESS, "local_copy": None, "reused": False,
  "obtained": "Ωar≈0.8 时翼足类每日失壳 1.2–1.4%；净壳增长在 Ωar≈1.03 归零；"
              "南大洋预计约 2038 年出现季节性表层欠饱和。",
  "used_by": ["case-07"],
  "uncertainty": "未直接抓取全文；为单一物种的实验结果。"},
 {"id": "S11", "kind": "agency_interview", "title":
  "NOAA Ocean Today, Ocean as a Lab: Ocean Acidification（该页直接抓取超时；"
  "结论来自检索结果摘要）",
  "url": "https://oceantoday.noaa.gov/oceanasalab_oceanacid/",
  "access_method": "snapkit.fetch_doc 读超时（TimeoutError）；改用 websearch 摘要",
  "request_id": "B04-req-015", "accessed_at": ACCESS,
  "local_copy": "tmp/%s/B04/research/fetch-results-2.json（记录了超时）" % RUN,
  "reused": False,
  "obtained": "每年约 25% 人为 CO2 入海；约每小时 100 万吨 CO2 入海；"
              "酸度较工业革命前增加约 30%；受访者 Francisco Chavez 表示"
              "「减少你的碳足迹是帮助逆转海洋酸化的最好办法」。",
  "used_by": ["case-10"],
  "uncertainty": "**未取得全文**。本特辑只把它用作一条「来源结论」级判定，不作为任何图上数字的依据。"},
 {"id": "S12", "kind": "service_doc", "title":
  "Open Snapshot AI 使用指南（https://open-snapshot.muedsa.com/ai-guide.md）",
  "url": "https://open-snapshot.muedsa.com/ai-guide.md",
  "access_method": "real GET, HTTP 200",
  "request_id": "B04-req-001", "accessed_at": ACCESS,
  "local_copy": "tmp/%s/B04/docs/docs/ai-guide.md" % RUN, "reused": False,
  "obtained": "POST /snapshot 请求体为 UTF-8 纯文本；响应体为图片字节；"
              "颜色 8 位按 #RRGGBBAA；根节点为 <Snapshot>，type 可为 png/jpg/webp；"
              "字体列表由 GET /fonts 提供（同一基址）；错误响应含 code/message/requestId；"
              "建议不要使用 ?errorImage=png。",
  "used_by": ["全部十件的 DSL 生成方式与错误处理"],
  "uncertainty": "服务文档本身不说明 4096 元素上限，该上限来自本题库的 WORK-ORDER。"},
 {"id": "S13", "kind": "service_endpoint", "title":
  "服务字体列表（GET https://open-snapshot.muedsa.com/fonts）",
  "url": "https://open-snapshot.muedsa.com/fonts",
  "access_method": "real GET, HTTP 200",
  "request_id": "B04-req-011", "accessed_at": ACCESS,
  "local_copy": "tmp/%s/B04/fonts-list.txt" % RUN, "reused": False,
  "obtained": "27 个字体族，含 Inter 及其 Black / Extra Bold / Semi Bold 等独立字族、"
              "Noto Sans/Serif CJK SC 等、DejaVu Sans Mono。"
              "本任务据此把字重当作 fontFamily 使用，而非 fontStyle。",
  "used_by": ["全部十件"],
  "uncertainty": "第一次请求误用了 snapshot.muedsa.com/fonts（B04-req-003，HTTP 404），"
                "按 AI 指南改用服务基址后成功。"},
]

by_case = {
 "case-01": {"S1", "S2", "S3", "S12", "S13"},
 "case-02": {"S1", "S12", "S13"},
 "case-03": {"S2", "S3", "S8", "S12", "S13"},
 "case-04": {"S2", "S8", "S12", "S13"},
 "case-05": {"S3", "S5", "S8", "S12", "S13"},
 "case-06": {"S7", "S8", "S12", "S13"},
 "case-07": {"S6", "S8", "S10", "S12", "S13"},
 "case-08": {"S9", "S12", "S13"},
 "case-09": {"S4", "S12", "S13"},
 "case-10": {"S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S11", "S12", "S13"},
}
for k, v in by_case.items():
    for sid in v:
        for s in sources:
            if s["id"] == sid and k not in s["used_by"]:
                s["used_by"].append(k)
for s in sources:
    s["used_by"] = sorted(set(s["used_by"]))

src_doc = {
 "schema_version": 1,
 "task_id": "B04",
 "run_id": RUN,
 "topic": "海洋酸化（ocean acidification）：0.1 这个数字到底意味着什么",
 "compiled_at": datetime.now(CST).isoformat(timespec="seconds"),
 "access_summary": {
   "real_page_fetches_ok": len([r for r in reqs
                               if r["request_type"] in ("document", "research_source",
                                                       "research_data", "font_list")
                               and r["http_status"] == 200]),
   "failed_or_degraded_fetches": len([r for r in reqs
                                      if r["request_type"] in ("document",
                                                              "research_source",
                                                              "research_data",
                                                              "font_list")
                                      and r["http_status"] != 200]),
   "search_only_sources": [s["id"] for s in sources if s["request_id"] is None],
   "note": "search_only_sources 表示该来源的内容来自 websearch 返回的检索结果摘要，"
           "本任务没有直接抓取其页面正文；这些来源在图上均标注为「检索结果摘要」。",
 },
 "sources": sources,
 "per_case_source_map": {k: sorted(v) for k, v in by_case.items()},
 "demonstration_and_uncertain_content": [
   {"item": "case-01 / case-03 的 1.259、1.318、×1.32",
    "type": "本任务计算的算术值",
    "basis": "按 10^(−ΔpH) 计算；不是任何来源公布的数字。",
    "shown_as": "图上写明「本图两个换算卡的算式由本任务计算」。"},
   {"item": "case-03 / case-07 / case-06 中 0.12/0.10 与 26%/30% 并列",
    "type": "两个来源数字的差异",
    "basis": "NOAA 自身在不同页面对同一现象给出不同取整；case-03 专门用一张图解释这件事。",
    "shown_as": "两张换算卡并列，不取其一。"},
   {"item": "case-04 的 0.0813 / 0.1072 / 0.1096 / 0.2630",
    "type": "本任务推算值",
    "basis": "按 [CO3^2-]/[HCO3-] ∝ 10^(−pH)，常数锚定在来源给出的 9%/90% = 0.10 @ pH 8.1。",
    "shown_as": "面板标题与来源注均写明「本图算术值，来源未直接公布」。"},
   {"item": "case-05 的 0.28%",
    "type": "本任务计算的算术比值",
    "basis": "10^2.4 年 / 10^7.7 年。",
    "shown_as": "图上标「本图算术值」。"},
   {"item": "case-05 的「恢复需要多久」",
    "type": "无数据的空缺",
    "basis": "来源只给出「近几十年水平在 200 万年中罕见（medium confidence）」这一定性判断，"
             "未给出恢复时间尺度；本任务也没有取得恢复模型的可引用结果。",
    "shown_as": "画布上有一块明确写着「本图没有数字可以给」的紫色面板。"},
   {"item": "case-06 的 SSP2-4.5 与 SSP3-7.0",
    "type": "未取到数值",
    "basis": "本任务未取得这两个情景的可引用 2100 端点。",
    "shown_as": "情景表中标注「未取」，不做任何插值或外推。"},
   {"item": "case-09 的五行「未取」",
    "type": "本任务的记录状态",
    "basis": "只有阿留申群岛与阿拉斯加湾的逐项百分位与趋势出现在取得的页面文本中。",
    "shown_as": "矩阵中留白并写「未取」；页脚说明「未取不是 NOAA 的分类」。"},
   {"item": "case-08 未绘出置信区间",
    "type": "主动省略",
    "basis": "原文给出的是 LnRR 的 95% CI 宽度，直接换算到百分比轴会引入新的不精确。",
    "shown_as": "副标题写明「本页只画原文报告的平均效应量，不画置信区间」。"},
   {"item": "case-10 的十条判定",
    "type": "本特辑的编辑判断",
    "basis": "五级判定色标是本特辑自定的分类法，不是任何来源自身的分级。",
    "shown_as": "图上与页脚都写明这一点。"},
   {"item": "S11（NOAA Ocean Today）",
    "type": "未取得全文",
    "basis": "直接抓取读超时；仅用检索结果摘要，且只支撑一条「来源结论」级判定。",
    "shown_as": "case-10 中该条判为「来源结论」而非「已证实」，并注明本特辑未找到量级数据。"},
   {"item": "S7 / S8 / S9 / S10",
    "type": "未直接抓取全文",
    "basis": "四篇文献均只有 websearch 返回的摘要文本。",
    "shown_as": "各件来源注均写「检索结果摘要，未直接抓取全文」。"},
 ],
 "not_used": [
   {"url": "https://www.pmel.noaa.gov/co2/story/What+is+Ocean+Acidification",
    "status": "HTTP 404（两次尝试）",
    "replacement": "改用 NOAA 的两个可访问页面取得同样事实，并在图上标注真实来源。"},
   {"url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6901524/",
    "status": "HTTP 200 但返回 reCAPTCHA 质询页而非正文",
    "replacement": "**不列为已读来源**；该文结论未在本特辑中作为依据使用。"},
   {"url": "https://www.gml.noaa.gov/webdata/ccgg/trends/co2/co2_gr_growth.txt",
    "status": "HTTP 404",
    "replacement": "逐年增量改为直接由年均值文件逐年相减得到，并说明这是算术派生量。"},
   {"url": "https://www.pmel.noaa.gov/co2/story/The+pH+Scale",
    "status": "HTTP 404",
    "replacement": "pH 对数刻度说明改用 NOAA 教育页与 OA Program 页的表述。"},
 ],
}
io.open(os.path.join(OUT, "sources.json"), "w", encoding="utf-8",
        newline="\n").write(json.dumps(src_doc, ensure_ascii=False, indent=2))
print("wrote sources.json", len(sources), "sources")
