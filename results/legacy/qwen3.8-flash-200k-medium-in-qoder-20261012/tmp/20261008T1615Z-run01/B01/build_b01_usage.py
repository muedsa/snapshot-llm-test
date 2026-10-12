"""Build outputs/<run>/B01/snapshot-usage.md from the real logs.

Run from the suite root:
  python tmp/<run_id>/B01/build_b01_usage.py
"""
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
temp = root / "tmp" / rid / "B01"
out = root / "outputs" / rid / "B01"

jl = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
req = jl(temp / "requests.jsonl")
itn = jl(temp / "iterations.jsonl")
tools = jl(temp / "tool-usage.jsonl")
shared = jl(root / "tmp" / rid / "_suite" / "requests.jsonl")
m = json.loads((out / "task-metrics.json").read_text(encoding="utf-8"))
per = {c["case_id"]: c for c in m["case_metrics"]}
by_req = {r["request_id"]: r for r in req}
case_of = lambda x: (re.match(r"B01-(case-\d\d|probe)-", x).group(1))

DOC_APPLIED = [
    ("https://open-snapshot.muedsa.com/ai-guide.md",
     "UTF-8 纯文本 POST 体、`<Snapshot type=\"png\">` 根标签、错误码与 requestId/Server-Timing 的读法；"
     "确定了 render.py 只保存原始响应字节、错误 JSON 绝不落为 final.png",
     "tmp/<run>/_suite/requests.jsonl `shared-doc-001-guide-ai`；全部 90 次渲染请求"),
    ("https://open-snapshot.muedsa.com/openapi.yaml",
     "接口只有 `/snapshot` 一个渲染端点、请求头 `X-API-Key` 可选、响应 Content-Type 区分 image/png 与错误 JSON；"
     "确认没有字体查询或上传素材接口，因此辅助素材只能以 dataUri 内嵌，而本题最终没有使用",
     "shared-doc-002-openapi"),
    ("https://snapshot.muedsa.com/reference/parser-tags/",
     "标签集合与属性拼写（Container/Positioned/Text/Stack/Transform/ClipRRect/BackdropFilter/"
     "ColorFiltered/WidgetSpan），据此写 dslkit 的 Doc.rect/box/label/line",
     "shared-doc-004-doc-parser-tags；十份 final.snapshot 的标签实际分布见 portfolio.json"),
    ("https://snapshot.muedsa.com/guides/widgets/",
     "布局 widget 的可选性与默认值；确认 `K.T`/kwargs 会把 None 原样序列化成 `fontStyle=\"None\"` 而报 400",
     "shared-doc-005-doc-widgets；踩坑见 §4 的 fontStyle 行"),
    ("https://snapshot.muedsa.com/widgets/layout/container/",
     "Container 的 decoration/border/borderRadius/boxShadow/gradient*/transform/clipBehavior 属性族；"
     "确认 `Doc.rect()` 没有 border 形参，描边必须走 `d.pos(..., d.box(..., border=\"N SOLID #RRGGBB\"))`",
     "shared-doc-006-doc-container；case-07 刊名描边、case-08 卡框"),
    ("https://snapshot.muedsa.com/guides/concepts/",
     "坐标系、层叠顺序与「先绘制在下」的规则；FOREGROUND 装饰在子节点之后绘制的语义由此确认",
     "shared-doc-007-doc-concepts；case-02 空心字压色轮"),
    ("https://snapshot.muedsa.com/guides/layout/",
     "Stack + Positioned 的绝对定位模式；十件作品全部采用 Stack/Positioned 栅格而非 Row/Column 流式",
     "shared-doc-008-doc-layout；所有 final.snapshot 的 Positioned 计数（4204 处）"),
    ("https://snapshot.muedsa.com/guides/painting/",
     "渐变类型与参数族（LINEAR/RADIAL/SWEEP 各自的合法属性）、blendMode、模糊；"
     "RADIAL 的 gradientRadius 是 0~1 比例而非像素",
     "shared-doc-009-doc-painting；probe 与 case-02/06/09/10 的光晕"),
    ("https://snapshot.muedsa.com/guides/media-text/",
     "Text 的 maxLines/overflow/letterSpacing/height 行高/tnum 等；确立「行盒高度 ≥ 1.15×字号」的自检标准",
     "shared-doc-010-doc-media-text；TextFit 自检（dslkit.TextFit）"),
    ("https://snapshot.muedsa.com/guides/rendering/",
     "抗锯齿与半透明叠加的实际合成方式；据此判断 8 位 alpha 矩形重叠会叠加透明度",
     "shared-doc-011-doc-rendering；case-09 竖条纹踩坑"),
    ("https://snapshot.muedsa.com/guides/parser/",
     "错误消息里的 position 与 near 片段如何定位到 DSL 字节偏移，用于把 400 定位回生成器行",
     "shared-doc-012-doc-parser；8 次 400 的定位过程"),
    ("https://snapshot.muedsa.com/widgets/text/rich-text/",
     "Text 嵌套子 Text 的行内混排（不同字号/底色/删除线），用于 case-06 平衡性说明与 case-07 引题",
     "shared-richtext-20261008T145221Z"),
    ("https://snapshot.muedsa.com/widgets/text/text/",
     "foregroundMode=\"STROKE\" + foregroundStrokeWidth 的空心字，以及 Raw 保留首尾空格",
     "shared-textdoc-20261008T145223Z；case-02 196px 主标题"),
    ("https://snapshot.muedsa.com/widgets/painting/clip-rect/",
     "ClipRRect + clipBehavior 与 BackdropFilter 的组合边界（模糊只作用在裁剪区内）",
     "shared-cliprect-20261009T011244Z；case-06 毛玻璃 KPI 条"),
]

# 每案例的踩坑叙述从 iterations 的 observed/changed 直接生成，避免手写与日志漂移。
KIND_ZH = {"baseline": "基线", "visual": "视觉迭代", "visual-iteration": "视觉迭代",
           "syntax": "语法/空转", "transport": "传输失败", "first-render": "首次渲染"}

rows_by_case = defaultdict(list)
for i in itn:
    rows_by_case[i["case_id"]].append(i)

L = []
A = L.append
A("# Snapshot 使用情况说明与踩坑记录\n")
A("任务ID：B01（十件真实世界开放作品）")
A("任务名称：B01-ten-real-world-showcases")
A(f"本次运行ID：{rid}")
A("完成状态：完成（10/10 件独立完整主作品）")
A("结束原因：需求满足且逐件完成实际看图与最终整体审查")
A(f"输出目录：`outputs/{rid}/B01/`")
A(f"临时目录：`tmp/{rid}/B01/`")
A("路径基准：`suite_root`（总任务根，即 `SNAPSHOT_TASK_ROOT` 指向的目录）；"
  "Markdown 本地链接相对当前文档。本题输出根内的链接以 `case-NN/…` 开头，"
  "指向临时目录的链接以 `../../../../tmp/…` 相对本题输出根书写。\n")
A("遵循 [PATHS.md](../../../PATHS.md)：文档、DSL、脚本、日志与报告均使用相对基准路径，"
  "不写机器盘符或用户目录。\n")

A("## 1. 最终产物与需求完成情况\n")
A("题目要求：至少 10 件独立完整主作品，尺寸/场景/内容/风格自定；每件在 `case-NN/` 交付 "
  "`final.png`、`final.snapshot`、`case.md`；输出根交付 `portfolio.json`、`portfolio.md`、"
  "`gallery.md`、`snapshot-usage.md`、`task-metrics.json`。逐项对照：\n")
A("| 用例 | final.png | 尺寸（读自 PNG 头） | final.snapshot | case.md | 定稿请求（与 PNG 字节 md5 相同的真实响应） |")
A("|---|---|---|---|---|---|")
for c in sorted(per):
    p = per[c]
    A("| %s | [%s/final.png](%s/final.png) | %d×%d | [final.snapshot](%s/final.snapshot) | [case.md](%s/case.md) | `%s` |"
      % (c, c, c, p["final_dimensions"][0], p["final_dimensions"][1], c, c,
         p["promoted_from_request"]))
A("")
A("- 交付物齐备：`portfolio.json`、`portfolio.md`、`gallery.md`、`snapshot-usage.md`、"
  "`task-metrics.json`、`asset-sources.json` 均在本题输出根。")
A("- 尺寸、文案、数据、效果类要求的满足依据写在每件 `case.md` 的「完成事项 / 反算结果 / 视觉自检」小节，"
  "并由 `portfolio.json` 的 `completion_criteria` 与 `visual_review` 字段逐条映射。")
A("- 未满足项：无。遗留问题只出现在过程层（§4、§6）。")
A("- 本题无预置轮次，`task_round=null`；十件作品各为独立用例，无同版式换色/缩放冒充。")
A("- 十件作品的图片与 DSL 均同名成对（`final.png` / `final.snapshot`），"
  "PNG 是服务原始响应字节（`raw_copy_file` 与 `response.bin` 保留），无任何后处理补字。\n")

A("## 2. 文档阅读与实际使用的能力\n")
A("服务基地址：`https://open-snapshot.muedsa.com`（以总 `run-config.json` 为准；"
  "子题 `run-config.json` 的默认地址与其一致）")
A("文档访问日期：2026-10-08（suite 级共享抓取，15 次 document 请求全部 200）与 "
  "2026-10-09（B01 探测）。B01 复用 suite 已下载的文档缓存，未在本题重复请求，"
  "因此 `document_requests=15` 记在共享准备里而不重复计入本题。")
A("下载缓存位置：`tmp/<run>/_suite/docs/`；请求逐条见 `tmp/<run>/_suite/requests.jsonl`。\n")
A("AI 使用指南（`https://open-snapshot.muedsa.com/ai-guide.md`）的实际应用："
  "按其说明使用 UTF-8 纯文本请求体与 `X-API-Key` 头（密钥只经环境变量 `SNAPSHOT_API_KEY` 注入，"
  "不写入 DSL、脚本或日志）；按其说明读取错误体的 `code/message/position/requestId`，"
  "把 8 次 400 逐一定位回生成器；按其说明保存 `Server-Timing`（68 条含 `render;dur=`，"
  "本题最长单次服务渲染约 3.3 s）与 `x-ratelimit-*` 头，"
  "限流额度为 120/min，实际从未触顶（`rate_limit_wait_seconds=0`）。\n")
A("| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |")
A("|---|---|---|")
for u, k, ev in DOC_APPLIED:
    A("| %s | %s | %s |" % (u, k, ev))
A("")
A("### 能力探测（probe）\n")
A("2026-10-09T10:04Z~10:28Z 用两次「十格能力图」实际验证 28 条能力，逐格打开原图与 2x 裁片，"
  "结果写入 `tmp/<run>/B01/capability-findings.json`（含 2 条 addenda）。请求：\n")
cf = json.loads((temp / "capability-findings.json").read_text(encoding="utf-8"))
A("| probe DSL | 成图 | 成功请求 | 服务 requestId | 失败尝试与错误 |")
A("|---|---|---|---|---|")
for p in cf["probes"]:
    fa = p["failed_attempt"]
    A("| `%s` | `%s` | `%s` | `%s` | `%s`：%s |"
      % (p["file"], p["image"], p["request_id"], p["service_request_id"],
         fa["request_id"], fa["error"]))
A("")
A("由此确立并在成品中实际使用的能力（`portfolio.json` 的 `dsl_capabilities` 字段是从 "
  "final.snapshot 正则实提的标签/属性，不是声明）：\n")
A("- 布局与几何：`Stack` + `Positioned`（全套 4204 处）+ `Container`（4227 处）绝对定位栅格；"
  "`Transform matrix`（884 处）做旋转/斜切与雷达式方位；`ClipRRect clipBehavior`（18 处）裁圆与裁区；"
  "`Column` 仅在 case-09 的小倍数标题出现 1 次。")
A("- 文本：`Text` 1295 处；`fontFeatures=\"tnum\"` 64 处（所有看板数字等宽）；"
  "`maxLines` 16 / `overflow` 5 / `letterSpacing` 14；`foregroundColor + foregroundMode=STROKE` "
  "做空心描边大字（case-02 主标题、case-06 Hero）；`textShadow` 3 处（霓虹色散）；"
  "`WidgetSpan` 12 处做行内小控件/行内图形。")
A("- 装饰与颜色：`gradientType` 24 处（LINEAR/RADIAL/SWEEP 三种都用过）、"
  "`gradientColors` 24、`gradientRadius` 12、`gradientCenter` 4、`gradientBegin/End` 各 8；"
  "`boxShadow` 7；`border` 132；`borderRadius` 1339；`ColorFiltered` 3 与 `blendMode` 3；"
  "`BackdropFilter` 2（毛玻璃）；`ImageFiltered sigmaX/sigmaY` 各 2。")
A("- 明确**不使用**的能力：`Image repeat`（探测判为 unreliable）、`Border` 标签的渐变描边"
  "（探测中 does-not-appear，原因未确认，改用双层 Container）、"
  "外部素材 `Image dataUri`（能力可用，但本题十件均为纯 DSL，最终 `<Image>` 标签数为 0）。\n")

A("## 3. 迭代过程、服务调用与图像检查\n")
tm = m["timings"]
cc = m["counts"]
A("请求记录：`tmp/<run>/B01/requests.jsonl`（90 条逐请求，含原始请求体/响应头/bin 文件路径）")
A("迭代记录：`tmp/<run>/B01/iterations.jsonl`（69 条，逐版本带 `image_viewed_at`）")
A("工具记录：`tmp/<run>/B01/tool-usage.jsonl`（23 条）；计划与修订：`tmp/<run>/B01/PLAN.md`（v1→v8）\n")
A("| 项 | 数值 | 口径 |")
A("|---|---|---|")
A("| 渲染请求总数 | %d | requests.jsonl 全部条目（含 probe 4 条） |" % cc["snapshot_requests"])
A("| 成功 | %d | http_status=200 | " % cc["successful_snapshot_requests"])
A("| 失败 | %d | 其中 400 语法/参数错误 %d 次（http_status=400）、传输失败 %d 次（http_status=0，无响应体）、"
  "响应截断 %d 次（Content-Length 不符，http_status 记 null） |"
  % (cc["failed_snapshot_requests"], sum(1 for r in req if r["http_status"] == 400),
     sum(1 for r in req if r["http_status"] == 0),
     sum(1 for r in req if r["http_status"] is None)))
A("| 重试请求 | %d | attempt_note 含 retry，均为传输失败后同 DSL 重试 |" % cc["retry_requests"])
A("| DSL 版本 | %d | case-01..10 共 72 个 + probe 4 个 |" % cc["dsl_versions"])
A("| 实际看图 | %d | 每个版本都有 image_viewed_at；长图/超宽屏先等高裁带再逐带看，疑似缺陷另做 2x 放大 |" % cc["image_views"])
A("| 完整视觉迭代 | %d | 看旧图→改 DSL→重渲染→看新图比较 |" % cc["completed_visual_iterations"])
A("| 未完成/非视觉迭代 | %d | syntax（含 case-10 v03 空转）与 transport |" % cc["incomplete_visual_iterations"])
A("| 其他接口查询 | 0 | 无字体查询、无上传接口调用；素材相关请求为 0 |")
A("| 共享文档请求 | %d | suite 级，本题复用不重复计 |" % cc["document_requests"])
A("")
A("基线（首次生成并查看）不计为改进迭代；400 语法修复与传输重试单列，不混入视觉迭代。")
A("看图时间字段说明：下表的 `查看时间(UTC)` 是**日志追加时刻**，不是逐张图的观看秒表。"
  "case-01..04、case-06、case-08..10 的迭代记录是在一轮复核结束后整批写入的，所以同一用例内多行"
  "共享同一时间戳（case-05、case-07 分两批写入，各有两个时间戳）。真实的逐版观看发生在各版本渲染"
  "之后、下一次修改之前，可用逐版 PNG 与 `qa-*` 裁片的文件时间交叉核对。"
  "本报告不谎称持有逐秒的观看计时，也不回溯改写已追加的日志。\n")
A("### 逐用例的看图与修改轨迹\n")
for c in sorted(rows_by_case):
    p = per[c]
    A("#### %s（版本 %d · 请求 %d · 成功 %d · 400 %d · 传输失败 %d · 看图 %d · 完整视觉迭代 %d）\n"
      % (c, p["dsl_versions"], p["render_requests"], p["successful"],
         p["parse_errors_400"], p["transport_failures"], p["image_views"],
         p["completed_visual_iterations"]))
    A("| 迭代ID | 版本 | 父版本 | 类型 | 渲染请求 | 查看时间(UTC) | 看到的问题 / 采取的修改 |")
    A("|---|---|---|---|---|---|---|")
    for i in rows_by_case[c]:
        r = by_req.get(i["render_request_id"], {})
        obs = (i["observed"] + " → " + i["changed"]).replace("\n", " ")
        A("| `%s` | %s | %s | %s | `%s`（%s） | %s | %s |"
          % (i["iteration_id"], i["version"], i["parent_version"] or "—",
             KIND_ZH.get(i["kind"], i["kind"]), i["render_request_id"],
             r.get("http_status", "?"), (i["image_viewed_at"] or "")[:19] + "Z", obs))
    qa = [t for t in tools if c in str(t.get("affects", ""))]
    if qa:
        A("")
        A("相关工具记录：`" + "`, `".join(t["id"] for t in qa) + "`")
    A("")

A("## 4. 修改记录与踩坑\n")
A("下表只收「渲染成功但视觉不合格」以外的**技术性**与跨案例可复用的坑；"
  "逐版本的视觉问题已在 §3 的表格中按实际 observed/changed 完整列出，不重复。\n")
A("| 迭代/请求ID | 类型 | 问题或现象 | 原因及确认依据 | 采取的修改 | 验证结果与剩余问题 |")
A("|---|---|---|---|---|---|")
PIT = [
 ("`B01-probe-caps-01-20261009T100455Z`", "语法(400)",
  "`gradientType=\"RADIAL\"` 配 `gradientBegin/End` 报 `Attr [gradientBegin] is not supported by this gradient type`",
  "文档 painting 页 + 探测：RADIAL 只接受 gradientColors/gradientRadius/gradientCenter/gradientFocal",
  "probe-caps-02 去掉 begin/end，改用 `gradientRadius=\"0.5\"`",
  "200；此后所有径向渐变按类型分参数族写"),
 ("`B01-probe-caps2-01-20261009T101801Z`", "语法(400)",
  "`gradientBegin=\"LEFT_CENTER\"` 报 value format error",
  "枚举名不存在，正确是 `CENTER_LEFT` 等九方位",
  "改为 `CENTER_LEFT/CENTER_RIGHT`",
  "200；同时把「枚举拼写」记进 b01kit 注释"),
 ("`B01-case-05-v01-20261010T005527Z`", "语法(400)",
  "同一 gradientBegin 枚举错误在成品首版复发",
  "生成器把 LINEAR 渐变参数封装时沿用了 RADIAL 的写法",
  "在 `b01kit.K` 里按 gradientType 分支只输出合法属性",
  "v02 起 200；此后未再复发同类错误"),
 ("`B01-case-05-v07/v08`", "语法(400)",
  "`Attr [fontStyle] value is invalid: Unexpected font style None`，随后 `REGULAR` 同样被拒",
  "`dslkit` 的 kwargs 透传把显式 `fontStyle=None` 序列化成字面量；服务端只接受 Italic 等真实枚举，`REGULAR` 也不是合法值",
  "可选属性一律「不传就不写」，删除所有显式 None；helper 里用条件字典而非默认参数",
  "v09 起 200；case-08 又独立复现一次（v02/v03），同样修法"),
 ("`B01-case-08-v01-20261010T023723Z`", "语法(400)",
  "卡面 RADIAL 光晕又混用 begin/end",
  "新写生成器未复用修好的 K 封装",
  "复用 `b01kit.K`",
  "200；教训：能力结论必须落到共享封装，不能只写在笔记里"),
 ("`B01-case-08-v04..v05`", "视觉",
  "`panel()` 默认宽度取整块内宽，导致 5 个统计格后面 4 个被最后一段矩形整体盖住，右侧计数器面板也被推出卡面",
  "读图 + DSL 字节确认：同一 Container 全宽绘制顺序覆盖前者；不是渲染问题而是生成器默认值",
  "在 `panel()` 内 `assert` 必须显式给 `x=`/`w=`；所有子列面板改为显式坐标",
  "v06 起完整；此规则写进 PLAN v?→后续所有题的公共约定"),
 ("`B01-case-09-v02-20261010T034413Z`", "视觉",
  "逐列矩形面积图出现竖向条纹/栅栏感",
  "8 位 alpha 矩形相邻列重叠处透明度叠加（`x-ratelimit` 无关；`mix()` 前后对比证实）",
  "新增 `mix(hex6, a, over)` 预合成实色后再填充，重叠只用于消除抗锯齿缝",
  "v03 起面平滑；同规则记为 `B01-tool-019`"),
 ("`B01-case-09-v03`", "视觉(文案与数据矛盾)",
  "手写结论文案「除步行外每种方式都在增加」与图内数据矛盾（步行 15→16 同样在增加）",
  "读图时把文案与 06 板块表逐条核对发现的",
  "量化措辞改为由 `max()/all()` 生成；成对条第二个系列改用空心/实心而非第二种颜色",
  "v04 定稿；标准记进 PLAN v7"),
 ("case-10 v03 系列（`B01-case-10-v03-20261010T040201Z`）", "空转/语法",
  "响应 541,962 字节与 v02 完全相同，md5 亦为 `51b34b029e6c88b2543d821683d1465f`",
  "生成器在写盘前抛 `KeyError('取消')`，渲染脚本把上一版 DSL 又发了一次；HTTP 200 但零视觉变化",
  "状态取值改 `.get(f['st'], \"\")`；并把「渲染后比对 size+md5」定为固定动作",
  "v04 真实生效并定稿；该记录保留且**不计入视觉迭代**"),
 ("`B01-case-05-v11-*`、`B01-case-07-v02/v03-*`、`B01-case-08-v05/v08/v10/v12-*`", "传输",
  "http_status=0，无响应体：curl (28) SSL/TLS connection timeout、(56) Send failure: Connection was reset、(52) Empty reply from server；服务未给 `Retry-After`",
  "同一 DSL 裁切请求立即 200 → 判定为链路抖动而非 DSL/服务端错误（case-05 v11 的 3 连败即此证据）",
  "保留每条失败记录，按相同 DSL 直接重试；不把它算作视觉迭代，也不谎称一次成功",
  "全部重试成功；`rate_limit_wait_seconds=0`、`queue_wait_seconds=null`（排队不可测）"),
 ("`B01-case-08-v16-20261010T030415Z`", "截断",
  "`truncated response body: got 213,792 of 332,564 bytes (Content-Length mismatch)`，http_status 记 None",
  "响应头 Content-Length 与实际字节不符（服务端/链路截断，原因未完全确认，倾向推测为传输中断）",
  "不保存半图；同 DSL 重发直到取回完整 332,564 字节，再以完整响应定稿",
  "`B01-case-08-v16-20261010T030819Z` 完整，final.png 与该响应 md5 相同"),
 ("case-05 v13（`B01-case-05-v13-20261010T013905Z`）", "视觉(逻辑自相矛盾)",
  "页眉写「登陆 10-10 07:00」，右下又写「转移截止 10-10 19:00 = 登陆前 12h」，两者相差 +12h 而非 −12h",
  "`clock()` 的日期进位只算了 `h//24`，漏掉起始 08 时，跨日少进一天",
  "改为 `t=h0+h` 后取 `t//24`/`t%24` 并补月份回退",
  "三处时刻统一为「登陆 10-11 07:00 · 截止 10-10 19:00」；教训：跨日/时区运算必须有反算表"),
 ("`B01-case-10-v01` 起（TextFit）", "语法/自检",
  "时区带城市名两行标签报 `est 97x42 > box 100x24`",
  "行盒高度只有字号的 1.06 倍，低于自定的 1.15 倍标准；`Doc.label` 的 `x` 恒为盒左边界，右对齐需自己减宽",
  "列宽 100→112 并同步右移 `band_x`；右对齐统一 `x = 右边界 − w`",
  "最终 TextFit 172 项 0 问题；case-09 177 项 0 问题"),
 ("看图（非请求）", "工具",
  "Read 工具会把高/宽图下采样：1080×3292、1200×3645、2880×1080 整看会丢小字",
  "对照服务原图字节与本地 PIL 解码结果确认是查看侧下采样，不是渲染缺陷",
  "固定动作：等高裁带（1220px 带）+ 局部 2x LANCZOS 放大，裁片全部留存为 qa-* 证据；"
  "case-10 曾疑似「洛杉矶被裁」，放大后确认是低对比+下采样假象，未改 DSL",
  "裁带只作看图证据，交付仍是服务原始响应字节；记为 `B01-tool-020`"),
]
for r in PIT:
    A("| " + " | ".join(r) + " |")
A("")
A("文档提到但本次未触发的注意事项：`Image repeat` 图案平铺（探测判 unreliable，成品未用）、"
  "`Border` 标签渐变描边（探测未出现，改用双层 Container）、字体查询接口（本服务未提供，未声称查过字体）。\n")

A("## 5. 任务耗时与请求统计\n")
A("结构化指标：[task-metrics.json](task-metrics.json)（含 `case_metrics` 逐用例指标与 `counting_notes` 口径说明）\n")
A("| 指标 | 实际值 | 单位 | 数据来源与统计范围 |")
A("|---|---|---|---|")
A("| 任务开始 / 结束 | %s / %s | UTC 时刻 | suite-state 的 B01.started_at 与 task-metrics.timings.ended_at |"
  % (tm["started_at"], tm["ended_at"]))
A("| 总墙钟时间 | %.1f（约 %.2f h） | 秒 | 起止之差，含被挂起/用户不在的空档 |"
  % (tm["elapsed_seconds"], tm["elapsed_seconds"] / 3600))
A("| 有效工时（active_seconds） | %.1f（约 %.2f h） | 秒 | 墙钟减去归类为 idle 的空档，见下 |"
  % (tm.get("active_seconds", 0.0), tm.get("active_seconds", 0.0) / 3600))
A("| 归类为 idle 的空档 | %.1f（约 %.2f h） | 秒 | 2026-10-09T11:40:51Z→2026-10-10T00:55:27Z："
  "case-04 定稿后到 case-05 首个渲染请求之间，无任何请求/看图/工具记录，会话挂起、未开展工作 |"
  % (tm.get("idle_gap_seconds", 0.0), tm.get("idle_gap_seconds", 0.0) / 3600))
A("| 首次可用图耗时 | %.1f | 秒 | started_at→首个 http 200 请求开始时刻（`B01-case-01-v01-20261009T104051Z` 之前还有能力探测） |"
  % tm["first_usable_image_seconds"])
A("| 等待用户反馈 | 0 | 秒 | 本题为单轮任务，无外部反馈等待 |")
A("| 限流等待 | 0 | 秒 | 未触顶（x-ratelimit-remaining 始终 >0），无 429 |")
A("| 排队等待 | null | 秒 | 服务未提供可测队列指标 |")
A("| 已记录请求耗时之和 | %.2f | 秒 | requests.jsonl 的 curl 端到端 duration_seconds 求和（成功请求），"
  "与墙钟不可比，也不等于服务渲染耗时 |" % tm["request_duration_sum_seconds"])
A("| 服务侧渲染耗时 | 68 条含 `render;dur=` | ms | 实际取得的 Server-Timing 头，最大约 3.3 s（case-05/06 大画布） |")
A("| 成功/失败/重试 | %d / %d / %d | 次 | requests.jsonl |"
  % (cc["successful_snapshot_requests"], cc["failed_snapshot_requests"], cc["retry_requests"]))
A("| 看图/完整视觉迭代 | %d / %d | 次 | iterations.jsonl 的 image_viewed_at 与 kind |"
  % (cc["image_views"], cc["completed_visual_iterations"]))
A("")
A("逐用例时间跨度、请求数与版本数见 `task-metrics.json` 的 `case_metrics`；共享准备（15 次文档请求 + "
  "4 次 probe 请求）单列在 `shared_preparation`，不重复累加进任何一件作品。"
  "各用例的 span 之和小于墙钟，墙钟又因 idle 空档远大于有效工时——三者口径不同，不互相换算。\n")

A("## 6. 设计选择、经验与未解决事项\n")
A("### 关键设计选择（由实际预览驱动）\n")
A("- **三米屏 vs 手机屏决定字号与密度**：case-04/05/10 的时刻列用 40~70px 粗体 tnum，"
  "case-06/09 靠分块与小标题层级而不是绝对字号；这个差别是看 v01 缩略后定的，不是先验设定。")
A("- **状态必须多重冗余**：case-10 的「延误/登机中/取消」用色条 + 文字胶囊 + 倒计时 + 计划删除线四重编码；"
  "读图时发现有色盲风险的远看场景后加的删除线，成为本题最有效的改动之一。")
A("- **不要和程序化几何硬拼**：case-07 曾用大量矩形堆「摄影感」海面失败，改为分层色带 + "
  "少量高光条 + 反射柱后成立；case-08 的盐壳同理（v08~v12 四次失败尝试都保留）。")
A("- **数据类作品先建可反算表**：case-03/04/05/06/07/08/09/10 的所有可见数字都由一个生成模型派生，"
  "结论句用 `max()/all()` 生成；case-09 的手写句与数据矛盾是直接促成这条标准的案例。")
A("- **区间图形画成「一整块 + 挖出例外」**：case-10 时区带从 24 段离散小方块改成夜底挖昼窗 + 同源游标后才读得出昼夜。")
A("### 可复用经验\n")
A("1. 能力结论必须落到共享封装（`b01kit.K` / `dslkit`），写在笔记里一定复发——case-08 v01 又踩了 RADIAL 混参。")
A("2. 渲染成功 ≠ 画面更新：**每版比对 size + md5**，与上一版相同即空转（case-10 v03 就是这么发现的）。")
A("3. 看图要看原图：长图等高裁带、可疑处 2x 放大；把「查看侧下采样」当成渲染缺陷会白白烧掉一次迭代。")
A("4. 生成器崩溃要在写盘前拦截：DSL 未更新时渲染脚本仍会发出合法请求并返回合法 PNG，日志会误报成功。")
A("5. 超宽/超高看板用「显式列宽 + 末列求余」；逐列自适应必然跨行错位。")
A("6. 半透明大面积填充一律预合成实色（`mix()`），8 位 alpha 重叠会叠出条纹。")
A("### 未解决 / 遗留\n")
A("- 服务无矢量 `path` 图元：case-05 海岸线与 case-09 折线面积用逐列矩形 + `K.polyline` 近似，"
  "曲率细节受此限制，无法进一步平滑（属平台边界，不是未完成项）。")
A("- `fontFeatures=\"tnum\"` 在当前渲染环境是否与系统默认等宽数字有可见差异，探测结论为 inconclusive；"
  "成品保留该属性但不宣称视觉差异已被验证。")
A("- `Border` 标签的渐变描边为何未出现，原因未确认（推测其绘制路径与 Container border 不同），"
  "已用双层 Container 替代。")
A("- 传输抖动（curl 28/52/56 与一次 Content-Length 截断）无法从客户端根除，只能保留失败留痕后重试；"
  "服务端未提供 Retry-After，等待时长不可测。")
A("- 日志字段的一处历史不一致：早期用例的 `iteration_id` 形如 "
  "`20261008T1615Z-run01-case-01-v01`，后期形如 `…-case-10-case-10-v04`（版本名自带前缀导致重复）。"
  "日志为追加式历史记录，不改写；引用时以 `case_id + version` 为准。")
A("### 结束依据\n")
A("十件作品逐件完成「实际看图 → 修改 → 重渲染 → 再比较」，最终版本 0 TextFit 问题，"
  "final.png 与某次 http 200 服务响应的 md5 相同，final.snapshot 为同名完整 DSL，"
  "case.md 记录了场景/数据反算/自检；整体终审见 `portfolio.json` 的 `final_collection_review`。"
  "达到题目要求，非因请求或迭代次数用尽而停止。\n")
A("### 留痕确认\n")
A("临时目录保留：`PLAN.md`（v1→v8）、`capability-findings.json`、`probe/`（能力图与 20 张裁片）、"
  "生成器 `case0X_*.py` / `case10_fids.py`、`b01kit.py`、`promote.py`、`log_c04.py`/`log_c05.py`、"
  "`build_b01_metrics.py`/`build_b01_portfolio.py`/`build_b01_usage.py`（本报告生成器）、"
  "`requests.jsonl`/`iterations.jsonl`/`tool-usage.jsonl`、每个 `case-NN/` 的全部版本 PNG、"
  "请求体 `.body.txt`、响应头与 `response.bin`（含 400 错误 JSON 与截断响应）、以及 qa 裁带/放大图。"
  "失败尝试、备选方案与空转渲染均未清理、未覆盖。")
A("运行时缓存 `tmp/<run>/B01/__pycache__/` 属于工具字节码，按 run-config 的 `runtime_cache_policy` "
  "不作为留痕，也不列入产物。总任务根 `.gitignore` 已在启动时创建并只维护一份，"
  "规则与全套核对见总报告 `outputs/<run>/_suite/snapshot-usage.md`（全套收尾时产出，故此处不用相对链接）；已确认 `tmp/`、`outputs/` "
  "与实际过程证据未被忽略。")
A("密钥未写入任何 DSL、脚本、日志或交付文件；API Key 仅经 `SNAPSHOT_API_KEY` 环境变量注入请求头。")
A("参考图/输入 PNG 仅作观察，未嵌入或裁切为素材，也未对最终图做后处理遮掩 DSL 问题"
  "（`<Image>` 标签数为 0，可复核 `asset-sources.json`）。")

(out / "snapshot-usage.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print((out / "snapshot-usage.md").relative_to(root).as_posix(), len("\n".join(L)))
