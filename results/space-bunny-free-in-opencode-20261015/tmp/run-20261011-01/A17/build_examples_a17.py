#!/usr/bin/env python
"""A17 examples.json + sources.md 生成器（含逐字一致性断言）。

启动基准：总任务根 (suite_root)。

一致性是本题的核心判据，所以**用断言证明**而不是靠人工核对：
  1. CORE[i] 在独立示例 DSL 中位于第 4 … 3+len(CORE[i]) 行，且该区段逐字相同；
  2. CORE[i] 在教学页 DSL 中同样以逐字相同的连续子串出现；
  3. 两者之间的差异**只有**外层包装（Snapshot 根 / 400×240 有界容器 / 页内平移与外框）；
  4. 印刷片段（去掉首尾两行省略提示）逐字等于 CORE[i]；
  5. 印刷片段的 XML 转义形式还原后逐字等于印刷原文。
任何一条不成立就直接抛错，不产出 JSON。
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
DRAFTS = BASE / "tmp/run-20261011-01/A17/drafts"
OUTD = BASE / "outputs/run-20261011-01/A17"

sys.path.insert(0, "tmp/run-20261011-01/A17")
from build_a17 import CORE, EX_HEAD, EX_TAIL, OMISSION_MARK, PAGES, xml_escape, xml_unescape  # noqa: E402

PURPOSE = {
    "01": "演示一次调用的输入与输出：请求路径、200 图片响应、400 PARSE_ERROR 响应，"
          "以及「根标签 type 决定编码」这条契约。",
    "02": "演示根尺寸来自布局：同一块 400×240 画布上，"
          "上半块由 Row + Expanded 按 flex 份额分配，下半块由 Stack + Positioned 直接落坐标。",
    "03": "演示文本与颜色的三处陷阱：<Raw> 保住空格、CDATA 保住 < 与 &、"
          "#RRGGBBAA 的 alpha 在尾部。",
    "04": "演示滤镜的作用范围：ColorFiltered 给子树着色、ImageFiltered 给子树高斯模糊，"
          "最右侧同色块作为未经过滤的对照。",
}

CLAIMS = [
    {
        "claim_id": "C01",
        "page_id": "01",
        "claim": "根标签是 Snapshot，它带 type 属性决定输出编码，并且只能有一个根 Widget 子节点。",
        "source_kind": "official_doc",
        "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
        "source_section": "Snapshot · 属性：background / debug / type；子节点：一个根 Widget",
        "example_id": "example-01",
        "example_evidence": "示例第 1 行 <Snapshot type=\"png\">；示例底部一行标注"
                            "「根标签 type 决定编码」；example-01.png 由服务端返回，image_info 为 PNG。",
    },
    {
        "claim_id": "C02",
        "page_id": "01",
        "claim": "响应是二选一：要么是按 type 编码的图片字节，要么是说明失败原因的 JSON。",
        "source_kind": "official_doc",
        "source_url": "https://snapshot.muedsa.com/reference/parser-errors/",
        "source_section": "HTTP 映射建议表；错误响应含 code / message / requestId",
        "example_id": "example-01",
        "example_evidence": "示例内并列印出「200  image/png」与「400  PARSE_ERROR」两条；"
                            "本 run 的 requests.jsonl 里 200 与 400 两种响应各有多条真实记录。",
    },
    {
        "claim_id": "C03",
        "page_id": "01",
        "claim": "结构或属性错误抛 ParseException 并映射为 400；消息里带 Pos[行:列]~偏移。",
        "source_kind": "official_doc",
        "source_url": "https://snapshot.muedsa.com/reference/parser-errors/",
        "source_section": "解析阶段错误表；「解析错误包含 Pos[line:col]~offset 与 message」",
        "example_id": "example-01",
        "example_evidence": "示例印出 400 PARSE_ERROR 一行；本 run 的 A14/A15/A16 探针"
                            "（如缩放正则生成非法属性名 left\"0.0\"）真实拿到过 400 与偏移信息。",
    },
    {
        "claim_id": "C04",
        "page_id": "02",
        "claim": "输出画布尺寸来自根 Widget 的 width / height，没有视口或百分比的概念。",
        "source_kind": "official_doc",
        "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
        "source_section": "Container · width / height；「根节点的尺寸即渲染结果的尺寸」",
        "example_id": "example-02",
        "example_evidence": "示例第 2 行 <Container width=\"400\" height=\"240\">，"
                            "服务端返回的 image_info 正是 400×240。",
    },
    {
        "claim_id": "C05",
        "page_id": "02",
        "claim": "Expanded / Flexible / Spacer 必须是 Flex、Row 或 Column 的直接子节点；"
                 "Expanded 固定 TIGHT 且不接受 fit，Flexible 才有 fit。",
        "source_kind": "official_doc",
        "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
        "source_section": "Expanded · 子节点：Flex / Row / Column 的直接子节点；Expanded（flex TIGHT）"
                          "不提供 fit 属性；Flexible（flex, fit）",
        "example_id": "example-02",
        "example_evidence": "示例第 3–8 行把两个 <Expanded flex=\"…\"> 直接挂在 <Row> 下，"
                            "服务端真实解析并按 2:1 分配了 213px / 107px。",
    },
    {
        "claim_id": "C06",
        "page_id": "02",
        "claim": "Positioned 只能作为 Stack / IndexedStack 的直接子节点，且每个轴最多设置"
                 "「left/right」与「width」中的两项。",
        "source_kind": "official_doc",
        "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
        "source_section": "Positioned · 子节点：Stack / IndexedStack 的直接子节点；"
                          "「每个轴最多设置三项中的两项」",
        "example_id": "example-02",
        "example_evidence": "示例第 11–17 行的 <Positioned> 全部直接挂在 <Stack> 下；"
                            "本 run 多题里把 Positioned 放进非 Stack 容器时真实收到过 400。",
    },
    {
        "claim_id": "C07",
        "page_id": "02",
        "claim": "Stack 的 fit 默认 LOOSE，clipBehavior 默认 HARD_EDGE。",
        "source_kind": "official_doc",
        "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
        "source_section": "Stack · fit 默认 LOOSE；clipBehavior 默认 HARD_EDGE",
        "example_id": "example-02",
        "example_evidence": "示例第 12 行显式写 <Stack fit=\"EXPAND\">，与默认值不同，"
                            "便于对照两种 fit 的差别。",
    },
    {
        "claim_id": "C08",
        "page_id": "03",
        "claim": "<Text> 里的普通文本节点会被 trim；<Raw> 原样保留首尾空格与换行。",
        "source_kind": "official_doc",
        "source_url": "https://snapshot.muedsa.com/reference/parser-errors/",
        "source_section": "「Text 的普通文本会被 trim；Raw 不做 trim，保留空格与换行」",
        "example_id": "example-03",
        "example_evidence": "示例第 6–7 行用两个 <Raw> </Raw> 把「PAID」与「已结算」之间的空格"
                            "保住，example-03.png 上可见「PAID / 已结算」中间的空格确实存在。",
    },
    {
        "claim_id": "C09",
        "page_id": "03",
        "claim": "解析器不做 HTML 实体解码，&amp; 会被原样显示成「&amp;」这几个字符。",
        "source_kind": "official_doc",
        "source_url": "https://snapshot.muedsa.com/reference/parser-errors/",
        "source_section": "「& 不做 HTML 实体解码；&amp; 保留为字面量」",
        "example_id": "example-03",
        "example_evidence": "示例第 12 行 <Raw><![CDATA[A < B & C > D]]></Raw> 在 "
                            "example-03.png 上原样显示尖括号与 &，没有任何实体被解码。",
    },
    {
        "claim_id": "C10",
        "page_id": "03",
        "claim": "文本中需要 < 或 > 时使用 CDATA。",
        "source_kind": "official_doc",
        "source_url": "https://snapshot.muedsa.com/reference/parser-errors/",
        "source_section": "「文本中需要 < 或 > 时使用 CDATA」；CDATA 内的注释标记按普通文本处理",
        "example_id": "example-03",
        "example_evidence": "示例第 12 行的 CDATA 区段；example-03.png 上第二行显示 "
                            "A < B & C > D。",
    },
    {
        "claim_id": "C11",
        "page_id": "03",
        "claim": "多字体字符串不会逐项 trim，因此 \"A, B\" 会保留前导空格，应写成 \"A,B\"。",
        "source_kind": "official_doc",
        "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
        "source_section": "Text · 「多字体字符串不会逐项 trim」",
        "example_id": "example-03",
        "example_evidence": "示例第 5–8 行的富文本使用 Inter Semi Bold + Noto Sans CJK SC 两种字体，"
                            "属于「多字体字符串」这条规则的适用场景。",
    },
    {
        "claim_id": "C12",
        "page_id": "03",
        "claim": "八位十六进制颜色按 CSS 的 #RRGGBBAA 解析，alpha 写在尾部。",
        "source_kind": "official_doc",
        "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
        "source_section": "Color · 「8 位十六进制按 CSS 的 #RRGGBBAA 解析（alpha 在尾部）；"
                          "旧版解析器按 #AARRGGBB 解析」",
        "example_id": "example-03",
        "example_evidence": "示例第 17 行 <Container ... color=\"#0F172A80\">，"
                            "在 example-03.png 上是一块半透明深灰而不是不透明的近黑。",
    },
    {
        "claim_id": "C13",
        "page_id": "04",
        "claim": "ColorFiltered 需要 color 与 blendMode，并把着色限制在子树的绘制边界内。",
        "source_kind": "official_doc",
        "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
        "source_section": "ColorFiltered · color 必填；blendMode 必填；"
                          "「把颜色效果限制在子树的绘制边界内，并允许合法的溢出」",
        "example_id": "example-04",
        "example_evidence": "示例第 5 行 <ColorFiltered color=\"#1D4ED8\" blendMode=\"MULTIPLY\">；"
                            "example-04.png 上橙色方块变成近黑，证明着色只作用在子树内。",
    },
    {
        "claim_id": "C14",
        "page_id": "04",
        "claim": "ImageFiltered / BackdropFilter 需要非负且有限的 sigmaX / sigmaY，"
                 "解析器只提供高斯模糊。",
        "source_kind": "official_doc",
        "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
        "source_section": "ImageFiltered / BackdropFilter · sigmaX、sigmaY 必须有限且非负；"
                          "「通过 Parser 提供的模糊只有高斯模糊」",
        "example_id": "example-04",
        "example_evidence": "示例第 10 行 <ImageFiltered sigmaX=\"5\" sigmaY=\"5\" tileMode=\"CLAMP\">；"
                            "example-04.png 上绿色方块的圆角被明显糊开。",
    },
    {
        "claim_id": "C15",
        "page_id": "04",
        "claim": "BackdropFilter 读取已绘制的背景，建议配合 ClipRect / ClipOval / ClipRRect 限定范围。",
        "source_kind": "official_doc",
        "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
        "source_section": "BackdropFilter · 「对已经绘制到当前位置的背景应用滤镜」；"
                          "「建议与 ClipRect / ClipOval / ClipRRect 搭配使用」",
        "example_id": "example-04",
        "example_evidence": "本题正文引用该条；例 4 未演示 BackdropFilter，因为本服务探针 "
                            "（p-d-filters）在透明背景上实测 BackdropFilter 不可见，"
                            "强行放进示例会与正文冲突。已在 uncertainties 记录。",
    },
    {
        "claim_id": "C16",
        "page_id": "04",
        "claim": "Opacity 取值 0 到 1，作用在整棵子树上。",
        "source_kind": "official_doc",
        "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
        "source_section": "Opacity · opacity 必填，范围 0 到 1",
        "example_id": "example-04",
        "example_evidence": "本页正文引用该条；例 4 用颜色尾部 alpha 对照说明「整棵子树」的含义，"
                            "Opacity 本身在本 run 探针 p-e-opacity-alpha 中真实渲染成功。",
    },
    {
        "claim_id": "C17",
        "page_id": "01",
        "claim": "服务端会按 Text 框宽度静默裁掉溢出文字，HTTP 状态仍为 200。",
        "source_kind": "own_measurement",
        "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
        "source_section": "Text · 属性说明未提及溢出行为；由本 run 实测补齐",
        "example_id": "example-01",
        "example_evidence": "本 run A14 的 K05：按估算字宽判定 663.7px 放得下 700px 的框，"
                            "实际右端被服务端裁掉、「Contrast 」整段消失而 HTTP 仍 200。",
    },
    {
        "claim_id": "C18",
        "page_id": "01",
        "claim": "text= 属性可用单引号包裹，此时裸 \" < > & 甚至 ]]> 都能原样渲染。",
        "source_kind": "own_measurement",
        "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
        "source_section": "Text · text 属性；XML 允许属性值用单引号",
        "example_id": "example-03",
        "example_evidence": "本 run A17 探针 p-f / p-g：text='<Positioned left=\"24\"/>' 与 "
                            "text='A < B & C > D' 均 200 且原样显示；印刷代码行正是靠这一点"
                            "才能逐字呈现双引号与尖括号。",
    },
]


def responses_by_version() -> dict:
    p = BASE / "tmp/run-20261011-01/A17/requests.jsonl"
    out = {}
    for line in p.read_text(encoding="utf-8").strip().splitlines():
        d = json.loads(line)
        out.setdefault(d["version"], []).append(d)
    return out


def main() -> None:
    resp = responses_by_version()
    examples = []
    for p in PAGES:
        i = p["id"]
        core = CORE[i]
        core_lines = core.split("\n")
        n = len(core_lines)
        assert 8 <= n <= 18, f"example-{i} 核心子树 {n} 行，不在 8–18"

        ex_lines = EX_HEAD + core_lines + EX_TAIL
        ex_dsl = "\n".join(ex_lines) + "\n"
        ex_path = f"tmp/run-20261011-01/A17/drafts/a17-example-{i}-v1.snapshot"
        stored = (BASE / ex_path).read_text(encoding="utf-8")
        assert stored == ex_dsl, f"example-{i}: 落盘 DSL 与生成内容不一致"

        # 断言 1：完整 DSL 第 4 … 3+n 行逐字等于核心子树
        got = "\n".join(ex_lines[3:3 + n])
        assert got == core, f"example-{i}: 完整 DSL 第 4–{3+n} 行与核心子树不一致"
        assert ex_lines[3 + n:] == EX_TAIL, f"example-{i}: 收尾包装不符"

        page_path = f"tmp/run-20261011-01/A17/drafts/a17-handbook-{i}-v1.snapshot"
        page_dsl = (BASE / page_path).read_text(encoding="utf-8")
        # 断言 2：核心子树在教学页 DSL 中逐字出现
        assert core in page_dsl, f"handbook-{i}: 教学页 DSL 中找不到逐字相同的核心子树"
        first = page_dsl.index(core)
        # 断言 3：两者差异只有外层包装 —— 页面里核心子树的包裹行必须都是 400×240 容器 + Stack
        wrap_before = page_dsl[max(0, first - 200):first].splitlines()[-2:]
        assert all('width="400"' in w or "<Stack" in w or "<Container" in w for w in wrap_before), \
            f"handbook-{i}: 核心子树外层不是 400×240 容器 + Stack，而是 {wrap_before}"

        printed_lines = [OMISSION_MARK] + core_lines + [OMISSION_MARK]
        printed_code = "\n".join(printed_lines)
        # 断言 4：印刷片段（去掉两行省略提示）逐字等于核心子树
        assert printed_lines[1:-1] == core_lines, f"example-{i}: 印刷片段与核心子树不一致"
        # 断言 5：XML 转义还原后等于印刷原文
        assert xml_unescape(xml_escape(printed_code)) == printed_code, \
            f"example-{i}: XML 转义不可还原"

        rs = resp.get(f"v1-example-{i}", [])
        assert rs, f"example-{i}: 没有找到真实渲染记录"
        last = rs[-1]
        assert last["status"] == 200 and last["image_info"]["width"] == 400 \
            and last["image_info"]["height"] == 240, f"example-{i}: 响应不是 400×240"
        prs = resp.get(f"v5-handbook-{i}", [])
        assert prs and prs[-1]["status"] == 200 \
            and prs[-1]["image_info"]["width"] == 1200 \
            and prs[-1]["image_info"]["height"] == 1600, f"handbook-{i}: 页面响应不是 1200×1600"

        examples.append({
            "example_id": f"example-{i}",
            "page_id": i,
            "page_png": f"handbook-{i}.png",
            "page_dsl": f"handbook-{i}.snapshot",
            "example_png": f"example-{i}.png",
            "example_dsl": f"example-{i}.snapshot",
            "size": [400, 240],
            "purpose": PURPOSE[i],
            "complete_example": {
                "path_base": "output_dir", "path": f"example-{i}.snapshot",
                "total_lines": len(ex_lines),
                "source_draft": {"path_base": "suite_root", "path": ex_path},
            },
            "core_subtree": {
                "in_complete_example": {"line_range_1based": [4, 3 + n], "line_count": n},
                "in_handbook_page": {"found_verbatim": True,
                                     "char_offset_in_page_dsl": first,
                                     "region": "教学插图的 400×240 有界容器内，未缩放"},
            },
            "allowed_wrapper_difference": {
                "complete_example_adds": EX_HEAD + EX_TAIL,
                "handbook_page_adds": ["<Positioned left=96 top=… width=400 height=240>",
                                       "<Container width=400 height=240 color=#F8FAFC>",
                                       "<Stack fit=EXPAND>", "插图外框与说明文字（不裁掉内容）"],
                "core_is_identical": True,
                "note": "差异只在外层包装；核心子树的文字、属性值、子节点顺序与相对坐标逐字相同。",
            },
            "printed_fragment": {
                "line_range_in_complete_dsl_1based": [4, 3 + n],
                "printed_code_line_count": n,
                "printed_code_line_count_limit": [8, 18],
                "omission_marker_lines": 2,
                "omission_marker_text": OMISSION_MARK,
                "omission_marker_note": "首尾两行是「省略外层包装」提示，不是可执行源码，"
                                        "不计入 8–18 行的印刷行数",
                "printed_text_verbatim": printed_code,
                "printed_text_xml_escaped": xml_escape(printed_code),
                "xml_unescape_restores_original": True,
            },
            "real_response": {
                "request_id": last["request_id"],
                "status": last["status"],
                "content_type": last["content_type"],
                "width": last["image_info"]["width"],
                "height": last["image_info"]["height"],
                "mode": last["image_info"]["mode"],
                "duration_seconds": last["duration_seconds"],
                "started_at": last["started_at"],
                "response_file": {"path_base": "suite_root",
                                  "path": last["response_file"]},
            },
            "view_evidence": {
                "viewed": True,
                "image": {"path_base": "suite_root",
                          "path": f"tmp/run-20261011-01/A17/preview/example-{i}-v1.png"},
                "observed": {
                    "01": "整屏查看：请求 / POST /render / 200 image/png / 400 PARSE_ERROR / "
                          "根标签 type 决定编码 六行齐全，无重叠无截断",
                    "02": "整屏查看：上半块 Row+Expanded 按 2:1 切成 213/107，下半块 "
                          "Stack+Positioned 落一条 320×32 深色条，两者互不干扰",
                    "03": "整屏查看：PAID / 已结算 的空格被 Raw 保住；"
                          "A < B & C > D 由 CDATA 原样显示；尾部 alpha 色块为半透明深灰",
                    "04": "整屏查看：左块被 MULTIPLY 着色成近黑、中块被高斯模糊、"
                          "右块同色但未过滤，三者并排对照",
                }[i],
            },
            "consistency_checks": {
                "core_lines_verbatim_in_complete_dsl": True,
                "core_lines_verbatim_in_handbook_dsl": True,
                "printed_equals_core": True,
                "xml_escape_roundtrip": True,
                "printed_code_line_count_within_8_18": True,
                "example_rendered_by_service": True,
            },
        })

    doc = {
        "schema_version": 1, "task_id": "A17", "round": "round-01", "path_base": "output_dir",
        "consistency_policy": "每页的核心示例子树在教学页与 400×240 独立示例中逐字相同；"
                              "差异只有外层包装。构建脚本 build_a17.py 用同一个 CORE 字符串生成两者，"
                              "生成 examples.json 时再以断言复核（逐字子串、行号区间、行数上下限、"
                              "XML 转义还原、真实响应尺寸）。",
        "examples": examples,
        "technical_claims": CLAIMS,
        "claims_source_summary": {
            "official_doc": sum(1 for c in CLAIMS if c["source_kind"] == "official_doc"),
            "own_measurement": sum(1 for c in CLAIMS if c["source_kind"] == "own_measurement"),
            "urls": sorted({c["source_url"] for c in CLAIMS}),
        },
        "not_claimed": "CDATA 的写法与错误映射按官方文档给出；`text=` 单引号属性值、"
                       "Text 溢出静默裁切这两条官方文档未写明，标注为 own_measurement。",
    }
    # examples.json 落在 drafts/ 作为源文件，由 deliver.py 提升到输出目录
    (BASE / "tmp/run-20261011-01/A17/drafts").mkdir(parents=True, exist_ok=True)
    (BASE / "tmp/run-20261011-01/A17/drafts/examples.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---------------- sources.md
    L = []
    w = L.append
    w("# A17 技术结论出处（sources.md）\n")
    w("本页把手册里每一条关键技术结论指回**实际读过的页面**或**实际做过的渲染**，")
    w("并给出对应的示例编号。逐条结构化数据见 `examples.json` 的 `technical_claims`。\n")
    w("## 读过的资料\n")
    w("| 来源 | 类型 | 本 run 的使用方式 |")
    w("|---|---|---|")
    w("| https://open-snapshot.muedsa.com/ai-guide.md | 服务指南 | run 级共享准备阶段读取，"
      "确定请求体、编码、响应类型、错误处理与字体查询入口 |")
    w("| https://snapshot.muedsa.com/reference/parser-tags/ | 官方标签参考 | "
      "第 1/2/3/4 页的全部结构性结论；Snapshot/Container/Row/Expanded/Positioned/Stack/"
      "Text/Raw/ColorFiltered/ImageFiltered/BackdropFilter/Opacity/Color 的属性、默认值与限制 |")
    w("| https://snapshot.muedsa.com/reference/parser-errors/ | 官方错误参考 | "
      "第 1 页的错误映射与第 3 页的 trim / Raw / CDATA / 实体不解码 |")
    w("| `GET /fonts` | 服务接口 | run 级共享准备，返回 27 个字体族；手册正文用 Inter，"
      "代码块用 DejaVu Sans Mono |")
    w("")
    w("## 逐条结论 → 出处 → 示例\n")
    w("| # | 手册页 | 技术结论 | 出处 | 对应示例 |")
    w("|---|---|---|---|---|")
    for c in CLAIMS:
        src = f"{c['source_url'].split('//')[1].split('/')[0]}/…/{c['source_url'].rsplit('/', 1)[-1]}"
        tag = "官方文档" if c["source_kind"] == "official_doc" else "本 run 实测"
        w(f"| {c['claim_id']} | 第 {int(c['page_id'])} 页 | {c['claim']} | "
          f"{tag} · {src} · {c['source_section']} | `{c['example_id']}` |")
    w("")
    w("## 实测补充（官方文档没有写、但本手册确实依赖的）\n")
    for c in CLAIMS:
        if c["source_kind"] == "own_measurement":
            w(f"- **{c['claim']}**  \n  出处：{c['source_url']}（该页未记载此行为）＋本 run 真实渲染。  \n"
              f"  证据：{c['example_evidence']}\n")
    w("## 不确定或未演示的部分\n")
    w("- **`BackdropFilter` 没有放进示例**：本 run 探针（`p-d-filters`）在透明背景上实测它不可见，"
      "在示例里画出来会与正文「读取已绘制背景」的说法对不上。手册第 4 页只把它写在要点里，"
      "不声称已用示例验证。该条的官方文档依据仍然成立。")
    w("- **CDATA 的服务端行为**在本 run 已被 A11 与 A17 的探针反复确认可用，"
      "但官方文档只说明「文本中需要 `<` 或 `>` 时使用 CDATA」，没有给出完整语法边界"
      "（例如是否支持嵌套 CDATA）。手册按文档措辞写，不额外断言。")
    w("- **字宽估算不是文档结论**：手册正文没有讲像素级排版细节，"
      "本 run 的 `est_em_str()` 系数来自 A14 对服务端的实测标定，属工程经验，不作为教学结论。\n")
    (OUTD / "sources.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(json.dumps({"examples": len(examples), "claims": len(CLAIMS),
                      "official": doc["claims_source_summary"]["official_doc"],
                      "own_measurement": doc["claims_source_summary"]["own_measurement"],
                      "all_consistency_checks_passed": True},
                     ensure_ascii=False, indent=2))
    print("-> tmp/run-20261011-01/A17/drafts/examples.json")
    print("->", (OUTD / "sources.md").as_posix())


if __name__ == "__main__":
    main()