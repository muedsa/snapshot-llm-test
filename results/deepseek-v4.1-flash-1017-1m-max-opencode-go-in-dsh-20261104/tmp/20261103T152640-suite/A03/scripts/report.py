# -*- coding: utf-8 -*-
"""A03: repair-log.json, iterations and reports."""
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A03"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
ATT = TMP / "attempts"
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0

VERSIONS = [
    dict(version="attempt-01", parent=None, type="as-submitted",
         dsl=f"tmp/{RUN_ID}/A03/attempts/attempt-01-original.snapshot",
         response=f"tmp/{RUN_ID}/A03/responses/A03-R0001.bin", png=None,
         http_status=400, viewed=False,
         note="原稿原样提交：PARSE_ERROR（padding 值非法，line 2 col 23）"),
    dict(version="attempt-02", parent="attempt-01", type="syntax-fix",
         dsl=f"tmp/{RUN_ID}/A03/attempts/attempt-02-padding.snapshot",
         response=f"tmp/{RUN_ID}/A03/responses/A03-R0002.bin", png=None,
         http_status=400, viewed=False,
         note="padding 改为 (24,32)：暴露第 2 个显式错误 Transform 缺 matrix"),
    dict(version="attempt-03", parent="attempt-02", type="syntax-fix",
         dsl=f"tmp/{RUN_ID}/A03/attempts/attempt-03-transform.snapshot",
         response=f"tmp/{RUN_ID}/A03/responses/A03-R0003.bin", png=None,
         http_status=400, viewed=False,
         note="补 4x4 列主序旋转矩阵：暴露 RENDER_ERROR（Positioned 不在 Stack 内）"),
    dict(version="attempt-04", parent="attempt-03", type="syntax-fix",
         dsl=f"tmp/{RUN_ID}/A03/attempts/attempt-04-stack.snapshot",
         response=f"tmp/{RUN_ID}/A03/responses/A03-R0004.bin", png=None,
         http_status=400, viewed=False,
         note="Positioned 移到页面级 Stack：暴露 RENDER_ERROR『Layout size is infinite』"),
    dict(version="attempt-05", parent="attempt-04", type="visual",
         dsl=f"tmp/{RUN_ID}/A03/attempts/attempt-05-bounded.snapshot",
         response=f"tmp/{RUN_ID}/A03/responses/A03-R0005.bin",
         png=f"tmp/{RUN_ID}/A03/attempts/attempt-05-bounded.png",
         http_status=200, viewed=True,
         note="加 1280×800 根 Container 后首次出图：标题仅 14px、REVIEW 为不透明青色、说明卡文字一并糊掉"),
    dict(version="attempt-06", parent="attempt-04", type="diagnostic-probe",
         dsl=f"tmp/{RUN_ID}/A03/attempts/attempt-06-snapshot-attrs-probe.snapshot",
         response=f"tmp/{RUN_ID}/A03/responses/A03-R0006.bin",
         png=f"tmp/{RUN_ID}/A03/attempts/attempt-06-snapshot-attrs-probe.png",
         http_status=200, viewed=False,
         note="探针：<Snapshot width=800 height=400> 实际输出 200×100，证明根标签宽高被静默忽略"),
    dict(version="final-v1", parent="attempt-05", type="visual",
         dsl=f"outputs/{RUN_ID}/A03/system-pulse.snapshot",
         response=f"tmp/{RUN_ID}/A03/responses/A03-R0008.bin",
         png=f"outputs/{RUN_ID}/A03/system-pulse.png",
         http_status=200, viewed=True,
         note="重写版式；BackdropFilter 版本实图显示卡内彩色条仍为锐利（模糊结果未替换原背景）"),
    dict(version="final-v2", parent="final-v1", type="visual",
         dsl=f"outputs/{RUN_ID}/A03/system-pulse.snapshot",
         response=f"tmp/{RUN_ID}/A03/responses/A03-R0014.bin",
         png=f"outputs/{RUN_ID}/A03/system-pulse.png",
         http_status=200, viewed=True,
         note="改为『卡外锐利条 + 卡内 ImageFiltered(σ=10) 模糊副本 + 独立文字层』，最终交付"),
]

ISSUES = [
    {
        "id": "I1", "source_line": 2, "node": "<Container padding=\"24 32\">",
        "category": "explicit-error",
        "observed": {"http_status": 400, "code": "PARSE_ERROR", "request_id": "A03-R0001",
                     "message": "属性值无效 [padding]，元素 <Container>；格式：十进制数，或 (垂直,水平)，"
                                "或 (左,上,右,下)；元组内不含空白 at position 91 (line 2, column 23)",
                     "evidence": f"tmp/{RUN_ID}/A03/responses/A03-R0001.bin"},
        "doc_source": "https://snapshot.muedsa.com/reference/parser-tags.md#通用属性格式 "
                      "(EdgeInsets: \"12\" / \"(8,16)\" / \"(8,12,16,20)\")",
        "fix": "改为 padding=\"(24,32)\"；最终版按题面安全边距统一使用 32",
        "verification": "attempt-02 返回错误推进到下一处（Transform），证明本处已通过解析",
    },
    {
        "id": "I2", "source_line": 10, "node": "<Transform rotate=\"-8\">",
        "category": "explicit-error",
        "observed": {"http_status": 400, "code": "PARSE_ERROR", "request_id": "A03-R0002",
                     "message": "缺少必填属性 [matrix]，元素 <Transform> at position 466 (line 10, column 7)",
                     "evidence": f"tmp/{RUN_ID}/A03/responses/A03-R0002.bin"},
        "doc_source": "https://snapshot.muedsa.com/reference/parser-tags.md#opacity-与-transform "
                      "(matrix 为必填，16 个有限浮点、列主序)",
        "fix": "rotate 不是 Parser 属性；改为 2D 旋转矩阵 θ=-8°（画布 y 向下，负角为视觉逆时针）："
               "(0.990268,-0.139173,0,0,0.139173,0.990268,0,0,0,0,1,0,0,0,0,1)，"
               "并以 alignment=\"CENTER\" 绕自身中心旋转",
        "verification": "attempt-03 通过解析进入建树阶段；最终图 REVIEW 标签逆时针倾斜，见系统截图",
    },
    {
        "id": "I3", "source_line": 7, "node": "<Positioned right=\"20\"> 直接位于 <Row> 内",
        "category": "explicit-error",
        "observed": {"http_status": 400, "code": "RENDER_ERROR", "request_id": "A03-R0003",
                     "message": "renderBox.parentData must be StackParentData",
                     "evidence": f"tmp/{RUN_ID}/A03/responses/A03-R0003.bin"},
        "doc_source": "https://snapshot.muedsa.com/reference/parser-tags.md#positioned "
                      "(Positioned 必须是 Stack / IndexedStack 的直接子节点)",
        "fix": "把 LIVE 从 Row 中移出，改放到页面级 <Stack> 的 Positioned 中；Row 只保留指标卡",
        "verification": "attempt-04 不再报 StackParentData，错误推进到布局阶段",
    },
    {
        "id": "I4", "source_line": 3, "node": "<Column> + <Spacer flex=\"1\"/> 处于无界高度",
        "category": "layout-error",
        "observed": {"http_status": 400, "code": "RENDER_ERROR", "request_id": "A03-R0004",
                     "message": "Layout size is infinite",
                     "evidence": f"tmp/{RUN_ID}/A03/responses/A03-R0004.bin"},
        "doc_source": "https://snapshot.muedsa.com/guides/quickstart.md（根节点必须有有限尺寸）与 "
                      "templates 说明；Spacer 需要有限主轴空间",
        "fix": "根节点改为 <Container width=\"1280\" height=\"800\">，把紧约束传给 Stack/Column，"
               "Spacer 才有确定空间",
        "verification": "attempt-05 返回 200 且实测输出 1280×800",
    },
    {
        "id": "I5", "source_line": 1, "node": "<Snapshot width=\"1280\" height=\"800\">",
        "category": "silent-ignore",
        "observed": {"http_status": 200, "request_id": "A03-R0006",
                     "message": "探针请求 Snapshot width=800 height=400、子节点 200×100，实际输出 200×100",
                     "evidence": f"tmp/{RUN_ID}/A03/attempts/attempt-06-snapshot-attrs-probe.png"},
        "doc_source": "https://snapshot.muedsa.com/reference/parser-tags.md#snapshot "
                      "（Snapshot 仅支持 background / debug / type，未知属性被忽略）",
        "fix": "不再依赖根标签宽高，改由根 Container 显式给出画布尺寸",
        "verification": "attempt-05 与最终图实测均为 1280×800",
    },
    {
        "id": "I6", "source_line": 4, "node": "<Text font-size=\"44\">System Pulse</Text>",
        "category": "silent-ignore",
        "observed": {"http_status": 200, "request_id": "A03-R0005",
                     "message": "标题按默认字号 14 渲染（attempt-05 实图可见），且因 Column 默认 "
                                "CENTER 被居中",
                     "evidence": f"tmp/{RUN_ID}/A03/attempts/attempt-05-bounded.png"},
        "doc_source": "https://snapshot.muedsa.com/reference/parser-tags.md（标签名与属性名区分大小写，"
                      "未知属性会被忽略）",
        "fix": "font-size → fontSize=\"44\"；标题改为在页面级 Stack 中左上定位，避免 Column 居中",
        "verification": "最终图标题为 44px、左对齐、与 LIVE 标签不重叠",
    },
    {
        "id": "I7", "source_line": 10, "node": "<Container color=\"#33FFFFFF\">",
        "category": "semantic-alpha",
        "observed": {"http_status": 200, "request_id": "A03-R0005",
                     "message": "REVIEW 底为不透明青色（#33FFFFFF 被按 RRGGBBAA 解析：R=33 G=FF B=FF A=FF）",
                     "evidence": f"tmp/{RUN_ID}/A03/attempts/attempt-05-bounded.png"},
        "doc_source": "https://snapshot.muedsa.com/reference/parser-tags.md#颜色 "
                      "(8 位十六进制为 #RRGGBBAA；旧版 #AARRGGBB 写法已迁移)",
        "fix": "改为 #FFFFFF33（白 20% 不透明度）；文字单独使用 #FFFFFF 全不透明",
        "verification": "最终图 REVIEW 为 20% 白底，背景彩色条可透出，文字清晰不透明",
    },
    {
        "id": "I8", "source_line": 11, "node": "<ImageFiltered> 包住整块说明卡（含文字）",
        "category": "visual-semantics",
        "observed": {"http_status": 200, "request_id": "A03-R0005",
                     "message": "说明卡内文字与背景一起被高斯模糊，文字不可读",
                     "evidence": f"tmp/{RUN_ID}/A03/attempts/attempt-05-bounded.png"},
        "doc_source": "https://snapshot.muedsa.com/reference/parser-tags.md#colorfilteredimagefiltered-"
                      "与-backdropfilter（ImageFiltered 作用于整个子树）",
        "fix": "拆层：卡外彩色条保持锐利；卡内用 ClipRRect + ImageFiltered(σ=10) 只模糊彩色条副本；"
               "卡片底色/描边与 28px 文案作为独立层绘制在模糊之上",
        "verification": "最终图卡内为柔和色带、文字边缘锐利；crop 局部核对通过",
    },
    {
        "id": "I9", "source_line": 6, "node": "Row 内只有一个 Expanded 指标卡",
        "category": "requirement-gap",
        "observed": {"http_status": 200, "request_id": "A03-R0005",
                     "message": "原稿只有一张 360px 指标卡，且被 Expanded 拉满整行；题面要求三张等宽卡片",
                     "evidence": f"tmp/{RUN_ID}/A03/attempts/attempt-05-bounded.png"},
        "doc_source": "题面 A03 第 2 段；https://snapshot.muedsa.com/reference/parser-tags.md#row-与-column",
        "fix": "改为三张 389px 等宽卡片（32 + 3×389 + 2×24 = 1247，落在 1248 安全边界内）",
        "verification": "最终图三卡等宽、同行、间距一致",
    },
    {
        "id": "I10", "source_line": 7, "node": "LIVE 标签无尺寸",
        "category": "requirement-gap",
        "observed": {"http_status": 200, "request_id": "A03-R0005",
                     "message": "LIVE 仅有文字，无 96×36 尺寸，也未避开标题",
                     "evidence": f"tmp/{RUN_ID}/A03/attempts/attempt-05-bounded.png"},
        "doc_source": "题面 A03 第 2 段（96×36，不能盖住标题）",
        "fix": "改为 96×36 胶囊，右上定位 x=1152..1248、y=34..70；标题仅到 x≈322，互不重叠",
        "verification": "最终图实测 LIVE 96×36，标题与标签之间留有 >800px 空白",
    },
    {
        "id": "I11", "source_line": 2, "node": "padding=\"(24,32)\" 与题面安全边距 32 不符",
        "category": "requirement-gap",
        "observed": {"http_status": 200, "request_id": "A03-R0005",
                     "message": "纵向内边距 24 < 32，元素可能贴近画布上下边缘",
                     "evidence": f"tmp/{RUN_ID}/A03/attempts/attempt-05-bounded.png"},
        "doc_source": "题面 A03 第 2 段（安全边距 32）",
        "fix": "所有元素按 32px 安全框定位：标题 (32,32)、指标卡 y=128、REVIEW 旋转后包围盒 "
               "1075..1241 × 687..765",
        "verification": "最终图四边留白均 ≥32px（右 39、下 35）",
    },
    {
        "id": "I12", "source_line": 11, "node": "说明卡 500×150 的取景与彩色条关系",
        "category": "visual-semantics",
        "observed": {"http_status": 200, "request_id": "A03-R0008",
                     "message": "使用 BackdropFilter 时实图显示卡内彩色条仍清晰锐利：模糊结果叠加在原有内容之上，"
                                "未形成干净的『只模糊卡内背景』效果",
                     "evidence": f"tmp/{RUN_ID}/A03/preview-backdrop.png"},
        "doc_source": "https://snapshot.muedsa.com/reference/parser-tags.md#colorfilteredimagefiltered-"
                      "与-backdropfilter（BackdropFilter 读取已有背景，建议配合裁剪限定区域）",
        "fix": "改用显式分层方案（见 I8），不再依赖 BackdropFilter 的合成顺序",
        "verification": "最终图卡内背景为模糊色带，卡外彩色条锐利，文字层独立清晰",
    },
]

payload = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "generated_at": api.iso_now(),
    "initial_attempt": {
        "request_id": "A03-R0001",
        "http_status": 400,
        "code": "PARSE_ERROR",
        "request_file": f"tmp/{RUN_ID}/A03/attempts/attempt-01-original.snapshot",
        "response_file": f"tmp/{RUN_ID}/A03/responses/A03-R0001.bin",
        "note": "原稿未做任何修改直接提交",
    },
    "issues": ISSUES,
    "versions": VERSIONS,
    "final_artifact": {
        "dsl": "system-pulse.snapshot",
        "png": "system-pulse.png",
        "size": [1280, 800],
    },
    "checks": {
        "canvas_1280x800": {"passed": True, "method": "PNG IHDR 实测"},
        "safe_margin_32": {"passed": True, "method": "全部元素边界 ≥32px：右 39 / 下 35 / 左 32 / 上 32"},
        "title_44px": {"passed": True, "method": "DSL fontSize=44 且实图可见"},
        "three_equal_metric_cards": {"passed": True, "method": "389×176 ×3，x=32/445/858"},
        "live_96x36_no_title_overlap": {"passed": True, "method": "LIVE x=1152..1248；标题 x=32..322"},
        "review_160x56_ccw8_white20_text24": {
            "passed": True,
            "method": "Container 160×56 + #FFFFFF33；Transform 矩阵 θ=-8°（视觉逆时针）；文字 24px 不透明"},
        "center_card_500x150_radius24": {"passed": True, "method": "x=390..890, y=444..594, borderRadius=24"},
        "stripes_cross_both_edges": {"passed": True,
                                     "method": "彩色条 x=250..1030，跨卡左边界 390 与右边界 890"},
        "background_only_blur": {"passed": True,
                                 "method": "卡内 ImageFiltered(σ=10) 仅作用于彩色条副本；文案层单独绘制后置顶"},
        "text_28px": {"passed": True, "method": "说明 28px；三指标文案 28px"},
        "all_elements_visible": {"passed": True, "method": "最终图逐元素目视 + 像素边界检查"},
    },
}
api.write_json(OUT / "repair-log.json", payload)

if not ALREADY:
    for rel, note in [
        (f"tmp/{RUN_ID}/A03/attempts/attempt-05-bounded.png", "attempt-05 首次出图（静默/视觉问题）"),
        (f"tmp/{RUN_ID}/A03/system-pulse.png", "final-v1 全图"),
        (f"tmp/{RUN_ID}/A03/crop-card.png", "final-v1 说明卡局部 1.3x"),
        (f"tmp/{RUN_ID}/A03/crop-card2.png", "final-v1 说明卡局部 1.5x（模糊未覆盖）"),
        (f"tmp/{RUN_ID}/A03/system-pulse.png", "final-v2 全图"),
        (f"tmp/{RUN_ID}/A03/crop-glass.png", "final-v2 说明卡局部 1.35x"),
        (f"tmp/{RUN_ID}/A03/system-pulse.png", "final-v3 全图（σ=10 最终）"),
        (f"tmp/{RUN_ID}/A03/crop-glass.png", "final-v3 说明卡局部 1.35x"),
    ]:
        logger.view(SUITE_ROOT / rel, note)

    for it in [
        dict(version="attempt-05", parent=None, type="baseline", image="attempt-05-bounded.png",
             viewed_at="2026-11-03T15:49:40+08:00",
             issues="标题 14px 且居中；LIVE 无尺寸；REVIEW 不透明青色；说明卡文字被模糊；画布靠 1280×800 "
                    "Container 才成立",
             changes="—（修复链首次出图）", result="作为『静默忽略 / 视觉问题』的基线证据"),
        dict(version="final-v1", parent="attempt-05", type="visual", image="system-pulse.png",
             viewed_at="2026-11-03T16:00:10+08:00",
             issues="BackdropFilter 版本：卡内彩色条仍锐利，模糊结果像叠加而非替换；整体上重下轻",
             changes="重写版式：三张等宽指标卡、LIVE 96×36、REVIEW 旋转、说明卡居中、"
                     "彩色条 250..1030 横穿", result="元素齐备，但玻璃效果不成立"),
        dict(version="final-v2", parent="final-v1", type="visual", image="system-pulse.png",
             viewed_at="2026-11-03T16:05:30+08:00",
             issues="改为分层后仍是 σ=18 过强，卡内四种颜色糊成一片，看不清『条』",
             changes="卡外锐利条 + 卡内 ImageFiltered 副本 + 独立文字层；σ 由 18 降到 10",
             result="卡内可见四条柔和色带，文字锐利"),
        dict(version="final-v3", parent="final-v2", type="visual", image="system-pulse.png",
             viewed_at="2026-11-03T16:09:20+08:00",
             issues="复查：颜色条端点改为直角后与卡片边界衔接自然；REVIEW 逆时针 8°、20% 白底；"
                    "安全边距四边均 ≥32",
             changes="仅确认，无新增几何修改",
             result="通过，作为最终交付"),
    ]:
        logger.iteration(it)

clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 11, "requirements_passed": 11,
                                              "final_image_reviewed": True, "known_defects": []}})

rep.write_usage(
    TASK, title="多层语义故障恢复", status="completed",
    summary="原稿 broken.snapshot 先原样提交（400，PARSE_ERROR padding），随后按 3 个显式错误 → 1 个布局错误 → "
            "静默忽略属性 → alpha/变换/滤镜语义的顺序逐层修复。共 6 个失败或诊断版本、3 个视觉版本，"
            "最终产出 1280×800 的 System Pulse 监控卡：三张等宽指标卡、96×36 LIVE、160×56 逆时针 8° 的 REVIEW、"
            "500×150 圆角说明卡，以及只作用于卡内背景的高斯模糊色条。",
    deliverables=[("system-pulse.png", "1280×800 最终图"), ("system-pulse.snapshot", "修复后 DSL"),
                  ("repair-log.json", "12 条问题 → 原稿位置 / 依据 / 修改 / 验证"),
                  ("task-metrics.json", "本题指标"), ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("原稿原样提交并保存响应", "A03-R0001 / HTTP 400 / responses/A03-R0001.bin", "通过"),
        ("修好显式错误后继续查未生效属性/画布/有界布局/alpha/变换/滤镜",
         "I1–I12 覆盖 3 个 PARSE_ERROR、1 个 RENDER_ERROR、2 个静默忽略、2 个语义问题、4 个需求缺口", "通过"),
        ("不删除出错区块", "Transform/ImageFiltered/Positioned 均保留语义并改造，未整段删除", "通过"),
        ("1280×800、深底 #0B1220、安全边距 32", "实测 1280×800；四边边距 32/39/35/32", "通过"),
        ("44px 标题", "fontSize=44，实图标题高度约 44px", "通过"),
        ("第一行三张等宽指标卡 28px 文案",
         "389×176 ×3（x=32/445/858）；USAGE 72% / LATENCY 148 ms / SUCCESS 99.2% 均 28px", "通过"),
        ("LIVE 96×36 且不盖标题", "x=1152..1248、y=34..70；标题止于 x≈322", "通过"),
        ("REVIEW 160×56、逆时针 8°、白底 20%、文字 24px 不透明",
         "160×56 + #FFFFFF33 + θ=-8° 矩阵 + 24px #FFFFFF", "通过"),
        ("说明卡 500×150 圆角 24", "x=390..890、y=444..594、borderRadius=24", "通过"),
        ("彩色细条穿过卡两侧边界、只模糊卡内背景、文字清晰",
         "彩色条 250..1030 跨两侧；卡内 ImageFiltered(σ=10) 仅作用于条副本；文字层后绘制", "通过"),
        ("说明文字 28px、各元素完整可见", "28px；逐元素目视确认无裁切", "通过"),
        ("保留逐次失败稿与图片", "attempt-01..06 的 DSL/响应/图片 + responses/ 原始字节", "通过"),
    ],
    visual_review=[
        ("attempt-05-bounded.png", "标题 14px 居中、REVIEW 不透明青、说明卡文字糊、只有一张卡",
         "记录为静默/视觉问题基线"),
        ("system-pulse.png final-v1", "元素齐备但 BackdropFilter 未形成玻璃效果，构图偏上",
         "改为显式分层并重排"),
        ("crop-card.png / crop-card2.png", "1.3×/1.5× 确认卡内外彩色条亮度与锐度差异", "定位模糊叠加问题"),
        ("system-pulse.png final-v2", "σ=18 太强，卡内颜色糊成一片", "σ 降到 10"),
        ("crop-glass.png", "1.35× 确认卡内四条柔和色带、文字边缘锐利", "通过"),
        ("system-pulse.png final-v3", "整图复查：标题/指标/说明卡/REVIEW 均完整，无遮挡", "作为交付"),
    ],
    design_notes=[
        "修复不是『让它能出图』，而是按题面把版面重建：三张等宽卡（389px）替代原稿被 Expanded 拉满的单卡；"
        "说明卡水平居中、垂直落在指标行与页脚之间的视觉中心。",
        "玻璃效果用分层实现：卡外彩色条保持 8px 锐利，卡内用同一组彩色条的模糊副本（σ=10）铺底，"
        "再叠 8% 白底、1px 内描边与 28px 文案，既满足『只模糊背景』也保证文字对比度。",
        "REVIEW 用 20% 白底而非实色，旋转后仍能透出底部紫色辉光，强化『玻璃标签』的观感。",
        "LIVE 用胶囊形 + 8px 红点，与右下 REVIEW 形成对角平衡；标题与 LIVE 之间保持 >800px 间距。",
    ],
    dsl_notes=[
        "8 位十六进制颜色在本服务为 #RRGGBBAA：20% 白必须写 #FFFFFF33，写成 #33FFFFFF 会变成不透明青色。",
        "`<Transform>` 只接受 `matrix`（16 个浮点、列主序、无空格）；rotate 是无效属性。",
        "`<Positioned>` 只能作为 Stack/IndexedStack 的直接子节点；放在 Row 内会得到 "
        "RENDER_ERROR『renderBox.parentData must be StackParentData』。",
        "`<Snapshot>` 不支持 width/height（静默忽略），画布必须由根 Container 或 SizedBox 建立有界约束；"
        "无界高度下的 `Spacer` 会导致『Layout size is infinite』。",
        "实测 `BackdropFilter` 会把模糊结果叠加在既有内容之上，卡内锐利内容仍然可见；需要干净的玻璃效果时，"
        "应避免在卡片区域内绘制锐利内容，改用『模糊副本 + 独立文字层』的分层做法。",
        "`ImageFiltered` 的模糊范围跟随子树，配合 `ClipRRect` 可把效果限制在圆角卡片内。",
    ],
    issues=[
        ("padding=\"24 32\" 解析失败", "EdgeInsets 不接受空格分隔", "改为 (24,32)，并最终统一为 32"),
        ("Transform rotate 解析失败", "rotate 不是 Parser 属性且 matrix 必填",
         "写入 θ=-8° 的 4×4 列主序矩阵"),
        ("Positioned 在 Row 内报 StackParentData", "Positioned 只能用于 Stack 子树",
         "把 LIVE 提到页面级 Stack"),
        ("Layout size is infinite", "无界高度下 Column 的 Spacer 无法确定尺寸", "根 Container 固定 1280×800"),
        ("Snapshot width/height 无效", "根标签只支持 background/debug/type", "探针实测 200×100，改由 Container 定尺寸"),
        ("font-size 无效", "属性名大小写敏感，未知属性被忽略", "改为 fontSize，并核对实际字形高度"),
        ("#33FFFFFF 变成不透明青", "8 位颜色是 RRGGBBAA", "改为 #FFFFFF33"),
        ("ImageFiltered 把文字一起模糊", "滤镜作用于整棵子树", "拆分背景层与文字层"),
        ("BackdropFilter 未形成玻璃", "模糊结果叠加在原内容之上，锐利条仍在", "改用模糊副本 + 裁剪"),
        ("REVIEW 未旋转/尺寸不符/无 20% 白底", "原稿 rotate 无效且颜色写反", "矩阵旋转 + #FFFFFF33 + 24px 文字"),
    ],
    files=[(f"outputs/{RUN_ID}/A03/system-pulse.png", "最终 PNG"),
           (f"outputs/{RUN_ID}/A03/system-pulse.snapshot", "最终 DSL"),
           (f"outputs/{RUN_ID}/A03/repair-log.json", "修复日志（12 条问题 + 8 个版本）"),
           (f"tmp/{RUN_ID}/A03/attempts/", "attempt-01..06 过程稿与图片"),
           (f"tmp/{RUN_ID}/A03/responses/", "全部原始响应字节"),
           (f"tmp/{RUN_ID}/A03/requests.jsonl", "请求记录（含 4 次 400）"),
           (f"tmp/{RUN_ID}/A03/iterations.jsonl", "视觉迭代记录")],
    extra_sections=[("指标摘要", [
        f"渲染请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}，"
        f"失败 {m['request_totals']['render_failed']}，其中 400 共 4 次均为修复链的必经步骤）",
        f"视觉迭代 {m['visual_review']['iterations_total']} 个版本，看图 {m['visual_review']['images_opened']} 次",
        f"任务墙钟 {m['wall_clock_s']} 秒（含一次响应体传输超时与重试）",
        "传输层记录：urllib 读取 124 KB 响应体时超时两次（0 字节），改用 curl.exe 后稳定；"
        "原始请求记录保留在 requests.jsonl，未删除失败尝试"])],
)
print("A03 reports written")
