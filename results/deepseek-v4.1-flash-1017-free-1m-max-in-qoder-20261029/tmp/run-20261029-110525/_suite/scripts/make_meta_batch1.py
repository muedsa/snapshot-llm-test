#!/usr/bin/env python3
"""Write meta.json files for A02-A05 packaging."""
import json, os
from pathlib import Path
SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN = SCRIPT.parents[2].name
T = f"tmp/{RUN}"

def write(task, meta):
    p = SUITE_ROOT / "tmp" / RUN / task / "drafts" / "meta.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("meta", task)

docs_common = [
    {"url": "https://open-snapshot.muedsa.com/ai-guide.md", "knowledge": "POST /snapshot UTF-8 文本请求、图片二进制响应、错误 JSON 与 /fonts", "used_in": "渲染与字体选择"},
    {"url": "https://snapshot.muedsa.com/reference/parser-tags.md", "knowledge": "Container/Stack/Positioned/Row/Column/Transform/Text 属性与限制", "used_in": "全部 DSL"},
    {"url": "https://snapshot.muedsa.com/reference/parser-text.md", "knowledge": "fontSize、fontStyle、maxLines、overflow 与文本换行", "used_in": "文字排版"},
]

write("A02", {
    "task_id": "A02", "title": "三会场密集会议日程", "status": "completed",
    "stop_reason": "需求满足并完成视觉自检",
    "design": "宽图用 09:00–16:00 单一线性时间轴与 A/B/C 三条泳道；块宽严格等于时长×比例（40 分钟=155px，30 分钟=116px），短块只放编号/时间/标题，完整标题、讲者、类别与起止时间放在下方两列编号索引。午休 12:00–13:00 作为跨三泳道的独立色带，不并入任何活动。手机图改为上午/午休/下午分组的 15 行列表，保留编号、标题、会场、起止时间，并注明“讲者详见完整日程”。",
    "requirements": [
        {"text": "1920×1200 泳道日程与 720×1280 手机导览", "evidence": "两张最终 PNG 实际尺寸与 DSL 根 Container 一致"},
        {"text": "块位置/长度按真实起止时间比例；空档保留", "evidence": "scale=3.881 px/min；40 分钟块宽 155.24px；A 会场 09:40–10:00 空档可见"},
        {"text": "午休 12:00–13:00 跨三泳道且不合并为活动", "evidence": "独立色带 x=948.6–1181.4，贯穿三泳道；无活动跨午休"},
        {"text": "15 项活动的编号、标题、讲者、起止时间、类别均可读", "evidence": "宽图编号索引 15 行含全部字段；短块用编号映射"},
        {"text": "注明读图方法与会场容量", "evidence": "页眉注释“块宽=实际时长…”；图例 A 320 人 / B 80 人 / C 160 人"},
        {"text": "手机图保留 15 项编号/标题/会场/起止时间，注明讲者位置", "evidence": "15 行全部可见；页眉写“讲者详见完整日程”"},
        {"text": "schedule-audit.json 含每场时长、各会场空档、冲突检查与两图映射", "evidence": "schedule-audit.json 已生成并核对 conflicts=0"}
    ],
    "files": [
        {"file": "agenda-wide.snapshot", "purpose": "1920×1200 泳道日程 DSL", "dsl": "agenda-wide.png", "status": "完成"},
        {"file": "agenda-wide.png", "purpose": "1920×1200 最终图", "dsl": "agenda-wide.snapshot", "status": "完成"},
        {"file": "agenda-mobile.snapshot", "purpose": "720×1280 手机导览 DSL", "dsl": "agenda-mobile.png", "status": "完成"},
        {"file": "agenda-mobile.png", "purpose": "720×1280 最终图", "dsl": "agenda-mobile.snapshot", "status": "完成"},
        {"file": "schedule-audit.json", "purpose": "时长、空档、冲突、映射审计", "dsl": "-", "status": "完成"}
    ],
    "reviews": [
        {"image": f"outputs/{RUN}/A02/agenda-wide.png", "at": "2026-10-29T11:20:18+0800", "result": "S15 文本溢出、索引只有左列（右列掉到画布外）"},
        {"image": f"outputs/{RUN}/A02/agenda-wide.png", "at": "2026-10-29T11:22:00+0800", "result": "索引双列恢复、S15 仍溢出，改为窄块只放编号/时间/标题"},
        {"image": f"outputs/{RUN}/A02/agenda-mobile.png", "at": "2026-10-29T11:20:18+0800", "result": "时间与编号重叠、底部信息条被裁"},
        {"image": f"outputs/{RUN}/A02/agenda-mobile.png", "at": "2026-10-29T11:23:00+0800", "result": "时间单行、15 行完整体；底部条移除后通过"},
        {"image": f"outputs/{RUN}/A02/agenda-wide.png", "at": "2026-10-29T11:23:03+0800", "result": "S15 与索引完整，通过"}
    ],
    "iterations": [
        {"id": "A02-wide-v1", "type": "baseline", "parent": None, "dsl": f"{T}/A02/drafts/gen_a02.py", "image": f"outputs/{RUN}/A02/agenda-wide.png", "at": "2026-10-29T11:20:18+0800", "problem": "S15 溢出、索引右列掉出画布", "change": "索引改 Row 双列；S15 窄块改堆叠", "result": "第二轮修复，仍需收窄 S15"},
        {"id": "A02-wide-v2", "type": "visual", "parent": "A02-wide-v1", "dsl": f"outputs/{RUN}/A02/agenda-wide.snapshot", "image": f"outputs/{RUN}/A02/agenda-wide.png", "at": "2026-10-29T11:22:00+0800", "problem": "S15 底部文字被裁", "change": "窄块仅保留编号/时间/标题，讲者见索引", "result": "通过"},
        {"id": "A02-mobile-v1", "type": "baseline", "parent": None, "dsl": f"{T}/A02/drafts/gen_a02.py", "image": f"outputs/{RUN}/A02/agenda-mobile.png", "at": "2026-10-29T11:20:18+0800", "problem": "时间/编号重叠、底部条被裁", "change": "时间改单行、收紧行高、移除底部条", "result": "通过"},
        {"id": "A02-mobile-v2", "type": "visual", "parent": "A02-mobile-v1", "dsl": f"outputs/{RUN}/A02/agenda-mobile.snapshot", "image": f"outputs/{RUN}/A02/agenda-mobile.png", "at": "2026-10-29T11:23:00+0800", "problem": "复查", "change": "无", "result": "通过"}
    ],
    "issues": [
        {"type": "visual", "problem": "S15（15:30–16:00，30 分钟）块内文字溢出", "cause": "30 分钟块仅 116px 宽，仍按常规块放讲者/类别", "fix": "窄块只放编号/时间/标题，完整信息进索引", "verify": "最终图 S15 全部可见", "evidence": f"outputs/{RUN}/A02/agenda-wide.png"},
        {"type": "visual", "problem": "索引第二列落在画布外", "cause": "外层用 Column 纵向堆叠了两个 890px 容器", "fix": "改为 Row 双列", "verify": "S01–S15 全部出现在两列中", "evidence": f"outputs/{RUN}/A02/agenda-wide.png"}
    ],
    "notes": "经验：时间比例图先用 scale 计算块宽，再为 30/40 分钟窄块设计降级排版；索引是保证短块信息完整的关键。",
    "docs": docs_common,
})

write("A03", {
    "task_id": "A03", "title": "多层语义故障恢复", "status": "completed",
    "stop_reason": "需求满足并完成视觉自检",
    "design": "按原稿逐层修复：先真实提交 broken.snapshot 保存 400，再依次修复 padding、Transform.matrix、Positioned 父级，最后重建为 1280×800 深色监控卡。说明卡用 ClipRRect + BackdropFilter 只模糊卡内背景，彩色细条从卡左 260px 延伸到 1020px、穿过两侧边界，文字绘制在滤镜之后。REVIEW 用 -8° 列主序旋转矩阵、20% 白底与不透明文字。",
    "requirements": [
        {"text": "原稿原样提交并保存响应，修复显式错误且不删区块", "evidence": f"{T}/A03/drafts/broken-original.png.http400.txt；repair-log.json 记录 10 项问题"},
        {"text": "1280×800、#0B1220、安全边距 32、标题 44", "evidence": "最终 PNG 1280×800；标题 44，页边距 32"},
        {"text": "三张等宽 KPI：USAGE 72% / LATENCY 148 ms / SUCCESS 99.2%，字号 28", "evidence": "392×168×3，值 28px；LIVE 96×36 不压标题"},
        {"text": "中央说明卡 500×150、圆角 24；彩条穿两侧；只模糊卡内背景", "evidence": "BackdropFilter σ14 + ClipRRect；条纹 x=260–1020、300–1000、330–950 穿过卡 390–890"},
        {"text": "REVIEW 160×56、逆时针 8°、白底 20%、文字不透明 24", "evidence": "矩阵 rotation=-8°，#FFFFFF33 底、#FFFFFF 字 24px"},
        {"text": "repair-log.json 对应位置、依据、修改与验证", "evidence": "repair-log.json 含 10 项 issue 与 3 次失败响应记录"}
    ],
    "files": [
        {"file": "system-pulse.snapshot", "purpose": "修复后的 1280×800 DSL", "dsl": "system-pulse.png", "status": "完成"},
        {"file": "system-pulse.png", "purpose": "1280×800 最终图", "dsl": "system-pulse.snapshot", "status": "完成"},
        {"file": "repair-log.json", "purpose": "问题→依据→修改→验证", "dsl": "-", "status": "完成"}
    ],
    "reviews": [
        {"image": f"{T}/A03/drafts/broken-original.png.http400.txt", "at": "2026-10-29T11:19:32+0800", "result": "400 PARSE_ERROR padding（非图片）"},
        {"image": f"outputs/{RUN}/A03/system-pulse.png", "at": "2026-10-29T11:24:27+0800", "result": "结构完整；实体转义文字与卡内条纹可见度需修"},
        {"image": f"outputs/{RUN}/A03/system-pulse.png", "at": "2026-10-29T11:24:47+0800", "result": "条纹穿过卡内虚化背景、文字锐利；通过"}
    ],
    "iterations": [
        {"id": "A03-v1", "type": "baseline", "parent": None, "dsl": f"{T}/A03/drafts/broken-original.snapshot", "image": f"{T}/A03/drafts/broken-original.png.http400.txt", "at": "2026-10-29T11:19:32+0800", "problem": "padding 400", "change": "改 (24,32)", "result": "进入 Transform.matrix 错误"},
        {"id": "A03-v2", "type": "syntax-fix", "parent": "A03-v1", "dsl": f"{T}/A03/drafts/broken-v1-padding.snapshot", "image": f"{T}/A03/drafts/broken-v1-padding.png.http400.txt", "at": "2026-10-29T11:19:43+0800", "problem": "Transform 缺 matrix", "change": "补 -8° 矩阵", "result": "进入 Positioned 父级错误"},
        {"id": "A03-v3", "type": "syntax-fix", "parent": "A03-v2", "dsl": f"{T}/A03/drafts/broken-v2-transform.snapshot", "image": f"{T}/A03/drafts/broken-v2-transform.png.http400.txt", "at": "2026-10-29T11:19:50+0800", "problem": "Positioned 在 Row 中导致 RENDER_ERROR", "change": "重建 Stack 层级", "result": "渲染成功"},
        {"id": "A03-v4", "type": "visual", "parent": "A03-v3", "dsl": f"outputs/{RUN}/A03/system-pulse.snapshot", "image": f"outputs/{RUN}/A03/system-pulse.png", "at": "2026-10-29T11:24:27+0800", "problem": "实体未解码、卡内条纹过暗", "change": "改文案；降低遮罩 alpha", "result": "通过"}
    ],
    "issues": [
        {"type": "parse_error", "problem": "padding=\"24 32\"", "cause": "EdgeInsets 格式非法", "fix": "(24,32)", "verify": "后续错误推进", "evidence": "repair-log.json"},
        {"type": "parse_error", "problem": "Transform 缺 matrix", "cause": "rotate 不是 Parser 属性", "fix": "16 值矩阵", "verify": "通过解析", "evidence": "repair-log.json"},
        {"type": "render_error", "problem": "Positioned 在 Row 内", "cause": "父级必须是 Stack", "fix": "重建层级", "verify": "200", "evidence": "repair-log.json"},
        {"type": "visual_only", "problem": "卡内条纹不可见、文字被一起模糊", "cause": "遮罩过暗；原稿 ImageFiltered 包住文字", "fix": "BackdropFilter + 低 alpha 遮罩 + 文本后绘", "verify": "最终图条纹可见且文字锐利", "evidence": f"outputs/{RUN}/A03/system-pulse.png"}
    ],
    "notes": "经验：BackdropFilter 必须放在裁剪容器内，且遮罩要半透明才能看见被模糊的背景；Parser 不做 HTML 实体解码，文本里的 < 要避开或用 CDATA。",
    "docs": docs_common + [{"url": "https://snapshot.muedsa.com/reference/parser-errors.md", "knowledge": "PARSE_ERROR 的 diagnostic 字段与 RENDER_ERROR 区分", "used_in": "A03 修复记录"}],
})

write("A04", {
    "task_id": "A04", "title": "分组改善与总体下降的数据解释", "status": "completed",
    "stop_reason": "需求满足并完成视觉自检",
    "design": "用同一 0–100% 尺度画四根渠道柱，直观看到 30→35、10→12 的双升；右侧用两期等长的 100% 堆叠条展示访问构成从 80/20 反转为 20/80；下方用总体 26.00%→16.60% 对照与原始分子/分母表锁定口径。结论给出精确分解：构成效应 −12.0pp、渠道内改善 +2.6pp、合计 −9.4pp，并明确观测数据不能证明因果。",
    "requirements": [
        {"text": "1600×1000 信息图，两渠道两期率、构成、总体", "evidence": "conversion-story.png 1600×1000，三部分齐全"},
        {"text": "率图同一 0–100% 尺度，不平均渠道比例", "evidence": "30.00/10.00/35.00/12.00 四柱同一轴；总体 2600/10000 与 1660/10000"},
        {"text": "构成图每期等长、分段按真实占比", "evidence": "两期均 540px=100%，80/20 与 20/80 分段"},
        {"text": "总体对照与精确加权公式", "evidence": "26.00%→16.60%，公式与 −9.40pp 可见"},
        {"text": "所有原始分母/分子小表可核对", "evidence": "4 渠道行 + 2 合计行，访问/成交/转化率齐全"},
        {"text": "主结论与不可证明因果的限制", "evidence": "结论卡明确“不能证明渠道调整导致下降”"},
        {"text": "正文≥22、图标注≥18", "evidence": "正文 22、表体 22、图注 18、轴 18"},
        {"text": "analysis.json 精确分数、显示百分比、加权公式与依据", "evidence": "analysis.json 含 rows/totals/weights/decomposition"}
    ],
    "files": [
        {"file": "conversion-story.snapshot", "purpose": "1600×1000 DSL", "dsl": "conversion-story.png", "status": "完成"},
        {"file": "conversion-story.png", "purpose": "最终图", "dsl": "conversion-story.snapshot", "status": "完成"},
        {"file": "analysis.json", "purpose": "分数、加权公式与分解", "dsl": "-", "status": "完成"}
    ],
    "reviews": [
        {"image": f"outputs/{RUN}/A04/conversion-story.png", "at": "2026-10-29T11:25:47+0800", "result": "后期构成图例被裁、率图周期标签缺失"},
        {"image": f"outputs/{RUN}/A04/conversion-story.png", "at": "2026-10-29T11:26:12+0800", "result": "图例恢复；前期/后期标签贴底被裁"},
        {"image": f"outputs/{RUN}/A04/conversion-story.png", "at": "2026-10-29T11:26:29+0800", "result": "标签完整、表格 22px；通过"}
    ],
    "iterations": [
        {"id": "A04-v1", "type": "syntax-fix", "parent": None, "dsl": f"{T}/A04/drafts/gen_a04.py", "image": f"{T}/A04/drafts/conversion-story.png.http400.txt", "at": "2026-10-29T11:25:27+0800", "problem": "宽度属性出现未插值 {bar_w-w1}", "change": "改成 f-string 计算 w2", "result": "渲染成功"},
        {"id": "A04-v2", "type": "visual", "parent": "A04-v1", "dsl": f"outputs/{RUN}/A04/conversion-story.snapshot", "image": f"outputs/{RUN}/A04/conversion-story.png", "at": "2026-10-29T11:25:47+0800", "problem": "构成图例被裁、周期标签缺失", "change": "调整行距、加图例与周期标签", "result": "周期标签仍被裁"},
        {"id": "A04-v3", "type": "visual", "parent": "A04-v2", "dsl": f"outputs/{RUN}/A04/conversion-story.snapshot", "image": f"outputs/{RUN}/A04/conversion-story.png", "at": "2026-10-29T11:26:29+0800", "problem": "复查", "change": "baseline 上移、表体 22", "result": "通过"}
    ],
    "issues": [
        {"type": "syntax", "problem": "DSL 中 width=\"{bar_w-w1:.1f}\" 原样出现", "cause": "拼接了非 f-string 片段", "fix": "先算 w2 再插值", "verify": "200 渲染", "evidence": "requests.jsonl"},
        {"type": "visual", "problem": "构成图第二行图例被裁", "cause": "卡片内容高 222px、图例结束 230px", "fix": "行距 82→76，卡片 270→280", "verify": "图例完整", "evidence": f"outputs/{RUN}/A04/conversion-story.png"},
        {"type": "visual", "problem": "率图 前期/后期 标签贴底被裁", "cause": "基线下移后标签超出内容框", "fix": "baseline 338，标签上移", "verify": "两标签完整", "evidence": f"outputs/{RUN}/A04/conversion-story.png"}
    ],
    "notes": "经验：百分比图统一 0–100% 轴能直接呈现“双升”，而堆叠构成条是解释辛普森悖论的关键；结论必须写出可复算的构成/渠道内分解。",
    "docs": docs_common,
})

write("A05", {
    "task_id": "A05", "title": "不规则采样与缺测的仪表报告", "status": "completed",
    "stop_reason": "需求满足并完成视觉自检",
    "design": "三张纵向堆叠的趋势图共享同一条 08:00–12:30 真实时间轴（x=120+分钟/270×1250），半小时间隔网格贯穿三图。每个真实读数画独立空心圆标记；缺失点画灰色 × 与竖线，线段只在相邻两个实测点之间连接，缺测处断开。压差图中性零线加深，09:40–10:50 用浅琥珀带标出三个负值实测点，并明确“仅采样点为负”。下方 12 时点表分两栏，缺测写“—”。",
    "requirements": [
        {"text": "1440×1000 三联趋势与真实时间比例共享横轴", "evidence": "三图 x 映射一致；08:00–12:30 标签齐全"},
        {"text": "温度/湿度缺测处线段断开、不补值", "evidence": "温度在 09:15、11:40 断；湿度在 09:40 断；图中 × 与图例"},
        {"text": "压差可正可负、零线清晰、标注负值区段", "evidence": "零线加深；09:40–10:50 三个负样本带注释"},
        {"text": "每个真实读数有独立标记", "evidence": "10+11+12 个空心圆标记"},
        {"text": "各指标有效数与观测 min/max", "evidence": "KPI：10/12、11/12、12/12 与范围"},
        {"text": "全部 12 时点简表，缺测以 —", "evidence": "两栏 6+6 行，09:15 温度与 09:40 湿度为 —"},
        {"text": "图例含缺测与断线；正文≥20、轴/表≥18", "evidence": "图例在页眉；正文 20、轴 18、表 18/19"},
        {"text": "normalized-data.json 含分钟偏移、null、范围、有效数、连接段", "evidence": "normalized-data.json 完整"}
    ],
    "files": [
        {"file": "sensor-report.snapshot", "purpose": "1440×1000 DSL", "dsl": "sensor-report.png", "status": "完成"},
        {"file": "sensor-report.png", "purpose": "最终图", "dsl": "sensor-report.snapshot", "status": "完成"},
        {"file": "normalized-data.json", "purpose": "分钟偏移、缺测、范围与连接段", "dsl": "-", "status": "完成"}
    ],
    "reviews": [
        {"image": f"outputs/{RUN}/A05/sensor-report.png", "at": "2026-10-29T11:27:08+0800", "result": "三图空白（坐标被裁剪）、页眉副标题被 KPI 压住"},
        {"image": f"outputs/{RUN}/A05/sensor-report.png", "at": "2026-10-29T11:27:31+0800", "result": "趋势可见；湿度缺测 × 不明显、12:30 轴标签缺失"},
        {"image": f"outputs/{RUN}/A05/sensor-report.png", "at": "2026-10-29T11:28:09+0800", "result": "对齐、缺测、负值带与 12 行表全部完整；通过"}
    ],
    "iterations": [
        {"id": "A05-v1", "type": "baseline", "parent": None, "dsl": f"{T}/A05/drafts/gen_a05.py", "image": f"outputs/{RUN}/A05/sensor-report.png", "at": "2026-10-29T11:27:08+0800", "problem": "图表内容被卡片裁剪、页眉重叠", "change": "图表改页面级坐标；页眉压缩", "result": "趋势可见"},
        {"id": "A05-v2", "type": "visual", "parent": "A05-v1", "dsl": f"outputs/{RUN}/A05/sensor-report.snapshot", "image": f"outputs/{RUN}/A05/sensor-report.png", "at": "2026-10-29T11:27:31+0800", "problem": "湿度缺测标记弱、12:30 缺标签", "change": "加深 ×；补 12:30；调整绘图区顶部", "result": "通过"}
    ],
    "issues": [
        {"type": "visual", "problem": "三张图全空白", "cause": "卡片内 Stack 使用页面绝对坐标，内容被裁剪", "fix": "所有图表元素提升到页面级 Stack", "verify": "趋势、网格、标记全部显示", "evidence": f"outputs/{RUN}/A05/sensor-report.png"},
        {"type": "visual", "problem": "12:30 轴标签与缺测标记不可见", "cause": "标签被卡片背景覆盖；× 颜色过浅", "fix": "标签后绘、× 改深灰", "verify": "最终图可见", "evidence": f"outputs/{RUN}/A05/sensor-report.png"}
    ],
    "notes": "经验：共享时间轴必须统一 x 映射并让网格线在三图内重复绘制；缺测用“断线 + × + 图例”三重编码，避免被读成 0。",
    "docs": docs_common,
})
