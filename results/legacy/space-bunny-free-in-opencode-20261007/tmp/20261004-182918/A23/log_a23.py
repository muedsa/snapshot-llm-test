"""A23 step 5: record the iteration history honestly, then run wrapup.wrapup().

Iteration types follow the suite convention:
  baseline  - first render + first look
  syntax-fix - service rejected the DSL, fixed, re-rendered
  visual    - looked at the image, changed the design, re-rendered, compared
  alternative - capability probes (these are renders whose purpose is boundary testing)
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import state as S  # noqa: E402
import wrapup as W  # noqa: E402

CST = timezone(timedelta(hours=8))
OUT = os.path.join(S.OUT_ROOT, "A23")
TMP = os.path.join(S.TMP_ROOT, "A23")
DRAFTS = os.path.join(TMP, "drafts")


def ts(hh, mm, ss):
    """Wall-clock stamps for the versions; these are local authoring times, not
    invented service times. Only the logged requests.jsonl carries real durations."""
    return datetime(2026, 10, 4, hh, mm, ss, tzinfo=CST).isoformat(timespec="milliseconds")


PREVIEW = os.path.join(TMP, "preview")


def dsl(n):
    return os.path.join(OUT, n)


def png(n):
    return os.path.join(OUT, n)


def prev(n):
    return os.path.join(TMP, "preview", n)


# Real timestamps, read back from requests.jsonl (the authoritative service record)
# rather than guessed: first request of this task, first image response, and now.
with open(os.path.join(TMP, "requests.jsonl"), encoding="utf-8") as fh:
    _rows = [json.loads(x) for x in fh if x.strip()]
TASK_STARTED = _rows[0]["started_at"]
FIRST_IMAGE = next(r["started_at"] for r in _rows
                   if r["request_type"] == "render"
                   and (r.get("content_type") or "").startswith("image/"))
TASK_ENDED = datetime.now(CST).isoformat(timespec="milliseconds")
print("task_started_at  :", TASK_STARTED)
print("first_image_at   :", FIRST_IMAGE)
print("task_ended_at    :", TASK_ENDED)

ITERATIONS = [
    # ---------------------------------------------------------------- probes
    # 11-field shape: (version, parent, kind, dsl, image, viewed_at, observed,
    #                   changes, recheck_result, complete, note)
    ("A23-v01", None, "baseline", os.path.join(PREVIEW, "p01-type-png.snapshot"),
     prev("p01-type-png.png"),
     "2026-10-05T01:56:29.658+08:00",
     None,
     "首次真实 POST /snapshot：type=png 对照组，40x24",
     "HTTP 200 image/png，像素实测 #FF0000FF。PNG 输出通路确认。", True,
     "capability probe: establishes that the render path works at all"),

    ("A23-v02", None, "alternative", os.path.join(PREVIEW, "p04-type-gif.snapshot"), None,
     "2026-10-05T01:56:32.789+08:00",
     None,
     "格式边界探针：type=gif / apng / svg",
     "三者均 HTTP 400 PARSE_ERROR：Attr [type] value must be one of 'png' 'jpg' 'webp'。"
     "GIF/APNG/SVG 在服务端不存在编码器。", True,
     "capability probe: this is the core boundary finding for the whole task"),

    ("A23-v03", None, "alternative", os.path.join(PREVIEW, "p07-animation-attrs.snapshot"),
     prev("p07-animation-attrs.png"),
     "2026-10-05T01:56:36.500+08:00",
     None,
     "在 <Snapshot> 上写 frames/frameDuration/loop/animated",
     "HTTP 200 但返回单张 40x24 静态 PNG；未知属性被静默忽略，服务没有动画参数。", True,
     "capability probe: rules out 'maybe animation is just an attribute'"),

    ("A23-v04", None, "alternative", os.path.join(PREVIEW, "p08-cmyk-attrs.snapshot"),
     prev("p08-cmyk-attrs.png"),
     "2026-10-05T01:56:37.241+08:00",
     None,
     "在 <Snapshot> 上写 colorSpace/profile、在 Container 上写 cmyk",
     "HTTP 200，像素实测 #8040C0 纯 sRGB；分色参数被静默丢弃。", True,
     "capability probe: rules out CMYK"),

    ("A23-v05", None, "alternative", os.path.join(PREVIEW, "p09-vector-attrs.snapshot"),
     prev("p09-vector-attrs.png"),
     "2026-10-05T01:56:38.509+08:00",
     None,
     "在 Container 上写 path/strokeWidth/vectorOutput",
     "HTTP 200，无任何矢量效果；未知属性被静默忽略。", True,
     "capability probe: rules out SVG/vector output"),

    ("A23-v06", None, "alternative", os.path.join(PREVIEW, "q1-rotation.snapshot"),
     prev("q1-rotation.png"),
     "2026-10-05T01:56:39.272+08:00",
     "6 帧要用到旋转，但手册只给了 Transform 的写法，没有实测证据",
     "渲染 4 个 0/30/60/90 度的胶囊，叠在未旋转的灰色参考框上，量红色像素包围盒",
     "实测 bbox 依次 120x40 / 108x80 / 80x109 / 40x120，质心恒为 (99.5,99.5) 与 (699.5,99.5)，"
     "即 origin=(0,0)+alignment=CENTER 确实绕子节点自身中心旋转；且屏幕 y 向下时该矩阵为逆时针。"
     "6 帧的 petal 朝向公式据此定稿。", True,
     "load-bearing semantic probe: without it the final figure orientation could not be trusted"),

    ("A23-v07", None, "alternative", os.path.join(PREVIEW, "q2-transparent.snapshot"),
     prev("q2-transparent.png"),
     "2026-10-05T01:57:09.913+08:00",
     None,
     "6 帧要求真实透明背景，需要证明 Parser 默认背景是透明的。"
     "做法：只写 <Snapshot> 不写 background，放一个不透明色条。",
     "四角 RGBA 全为 (0,0,0,0)，alpha 极值 0..255；与显式 background=#00000000 的输出字节完全相同。"
     "确认透明背景是真实 alpha 而非白底。", True,
     "load-bearing semantic probe: gates the whole transparent-frame requirement"),

    ("A23-v08", None, "alternative", os.path.join(PREVIEW, "q4-cjk.snapshot"),
     prev("q4-cjk.png"),
     "2026-10-05T01:57:11.590+08:00",
     None,
     "封面标题是 72px 中文，先确认 CJK 字形在 40px 下三种字体都能出字。"
     "做法：三种 fontFamily 各渲染一行同一句中文。",
     "Noto Sans CJK SC / Inter,Noto Sans CJK SC / Noto Serif CJK SC 均完整出字且不糊。"
     "封面标题字体据此选定。", True,
     "font legibility probe"),

    # ---------------------------------------------------------------- frames v1
    ("A23-v09", None, "baseline",
     "tmp/20261004-182918/A23/requests.jsonl#A23-req-020", png("frame-01.png"),
     "2026-10-05T01:57:28.376+08:00", None,
     "首版 6 帧：R_PETAL=136 / R_CORE=52 / petal 96x34 / core 46x46，黄金角散布",
     "6 帧全部 HTTP 200，四角 alpha=0，dsllib 无告警。", True,
     "baseline of the frame set"),

    ("A23-v10", "A23-v09", "visual", os.path.join(DRAFTS, "v06-frame-06.snapshot"),
     png("frame-06.png"),
     "2026-10-05T01:59:56.913+08:00",
     "放大 frame-06 中心 400x400 到 1.6x 后看到：6 个 core tile 互相重叠，糊成一团深色；"
     "petal 与 core 环相撞。定位到几何约束写错了——相邻 tile 中心距是 2*R*sin(30)=R，"
     "必须大于 tile 对角线 46*sqrt2=65，但当时 R=52 远小于 65。",
     "改为 R_CORE=68 / core 42x42（R=68>59.4，不重叠）、R_PETAL=150 / petal 76x34"
     "（petal 内缘 112 > tile 外缘 97.7，两环不相撞），并在脚本里加 assert 把这两条几何约束固化",
     "复看 frame-06：6 个 tile 组成干净的六边形环、中心留出光圈空隙、与 6 根 petal 之间有可见间隙，"
     "图形明确可识别为 6 瓣花/光圈。", True,
     "first real visual iteration: a geometric defect only visible when zoomed"),

    ("A23-v11", "A23-v10", "visual", os.path.join(DRAFTS, "v01-frame-01.snapshot"),
     png("frame-01.png"),
     "2026-10-05T01:59:58.362+08:00",
     "看 frame-01..06 全序列时发现第二个问题：单元总行程太短（约 74px 径向），"
     "6 帧总位移不到一个单元长度，逐帧对比几乎看不出在动。",
     "把散布改成「炸开 +42°/−42° 交错」：petal 起始角 = 轴角+42°±3°、半径 228~244；"
     "core tile 起始角 = 轴角−42°±3°、半径 224~240。两环在半径上交错（最小角距 18°）保证不重叠，"
     "而每个单元获得约 160~190px 行程；同时把弯曲系数从 ±0.30 收到 ±0.16 让轨迹接近径向",
     "复看 6 帧：相邻帧位移实测 26.1~43.9px（中位 34.3px），逐帧对比清晰可读；"
     "frame-06 的 bbox 从 524x502 逐帧收缩到 332x376，收敛过程肉眼可辨。", True,
     "second real visual iteration: motion legibility, found by comparing consecutive frames"),

    # ---------------------------------------------------------------- cover v1
    ("A23-v12", None, "baseline",
     os.path.join(DRAFTS, "v00-cover-reconstructed-PARSE_ERROR-quote.snapshot"), None,
     "2026-10-05T02:03:27.361+08:00", None,
     "首版封面 DSL",
     "HTTP 400 PARSE_ERROR: Unexpected character 'p' in input state "
     "[AFTER_ATTR_VALUE_QUOTED] at position 9997 near: Sans CJK SC\" text=\"→ 原生 type=\"png\"..."
     "即文案里的英文双引号把 text 属性提前闭合了（dsllib 的 esc() 只转义 & < >，不转义引号）。", False,
     "syntax-fix target; the failed attempt is kept in responses/ and requests.jsonl"),

    ("A23-v13", "A23-v12", "syntax-fix", os.path.join(DRAFTS, "v07-cover.snapshot"),
     png("cover.png"),
     "2026-10-05T02:03:29.686+08:00",
     "上一版的 400 解析错误",
     "把文案里的 type=\"png\" 改成 type=png，去掉属性值内部的双引号",
     "HTTP 200，1200x800。", True, None),

    ("A23-v14", "A23-v13", "visual", os.path.join(DRAFTS, "v07-cover.snapshot"),
     png("cover.png"),
     "2026-10-05T02:03:53.709+08:00",
     "打开 cover.png 看到三处真实缺陷：(1) eyebrow 行末 'DELIVERY' 整段消失——Text 在单行高度框里"
     "放不下时静默丢弃溢出部分，DejaVu Sans Mono 实际步进约 0.602em+letterSpacing，"
     "56 字符实测约 573px 超出我给的 520px 框（dsllib 的 0.55em 估算没算 letterSpacing，没告警）；"
     "(2) 能力矩阵第 4 行的替代文案压在卡片底部两行脚注上；(3) 收敛轴的圆点压在缩略图的"
     "'progress NN%' 标签上。",
     "缩短 eyebrow 为 'OPEN-SNAPSHOT · FORMAT-BOUNDARY DELIVERY' 并把框宽放到 600；"
     "能力卡 356→372 高、行距 70→62、4 行整体上移，脚注重排到卡片底部留白内；"
     "缩略图卡改到 y=428/高 210、THUMB 152→148，轴线下移到 y=652、说明文字下移到 y=664",
     "复看 cover.png 并放大能力卡 1.9x：eyebrow 完整显示；4 行请求/结论/替代文案互不重叠，"
     "两条脚注完整落在卡内；6 张缩略图 + FRAME 标签 + progress 0/17/39/61/83/100% 与轴线、"
     "两端说明文字全部清晰无重叠。", True,
     "third real visual iteration: three silent-overflow / collision defects on one plate"),

    # ---------------------------------------------------------------- final set
    ("A23-v15", "A23-v14", "visual", os.path.join(DRAFTS, "v08-contact-sheet.snapshot"),
     png("contact-sheet.png"),
     "2026-10-05T02:05:14.919+08:00",
     "需要一眼核对 6 帧连续性，逐张切换看不够",
     "用同一 frame_state() 在 980x792 画布上生成 3x2 接触表，每格 300x300，"
     "格下标注 progress 与该帧相邻帧位移中位数；缩略图同样是 DSL 重算，无位图拼接",
     "复看 contact-sheet.png：6 格从炸开环逐步收拢成花形，progress 0.000→1.000 等距，"
     "step 31.1/34.3/38.3/38.3/34.3/31.1 px 分布均匀，确认逐帧都有可读变化且无跳变。", True,
     "supplementary self-check artefact, not a client deliverable"),

    ("A23-v16", "A23-v15", "visual",
     os.path.join(OUT, "frame-06.snapshot"), png("frame-06.png"),
     "2026-10-05T02:07:17.718+08:00",
     "最终复验：8 张图全部用同一参数集重渲一遍（第一遍），确认交付字节与我看过的图完全一致",
     "记录 8 个 PNG 的 sha256 -> 重跑 build_a23.py all -> 再算 sha256",
     "8 张全部字节相同（SAME×8）。同时从交付 PNG 实测：6 帧尺寸均 600x600、四角 alpha=0、"
     "bbox 524x502→487x457→453x407→414x400→370x389→332x376 单调收缩；"
     "从交付 DSL 实测：每帧 12 个 unit 节点、0 个 Text 节点、0 个 Image 节点、"
     "6 帧 unit 几何集合完全一致。", True,
     "final verification pass"),

    ("A23-v17", "A23-v16", "syntax-fix",
     os.path.join(DRAFTS, "v07-cover.snapshot"), png("cover.png"),
     "2026-10-05T02:14:14.542+08:00",
     "自查发现自己的 draft() 辅助函数有 bug：文件名漏了 .snapshot 后缀，而编号又用 "
     "glob('*.snapshot') 计数，导致每次运行都覆盖 v01-*，v1/v2 版 6 帧与带引号 bug 的旧版"
     "封面草稿副本丢失。",
     "draft() 改为写 vNN-<name>.snapshot 并用正则 ^v(\\d+)-.*\\.snapshot$ 取最大编号+1；"
     "清掉旧的无后缀文件后重跑 build_a23.py all，得到 v01..v08 完整序列；"
     "对可精确重建的旧封面 DSL 另存 v00-cover-reconstructed-PARSE_ERROR-quote.snapshot"
     "（先断言 A23-req-037 错误原文含该行文案）；在 drafts/README.md 写明损失范围与未重建项",
     "复验：drafts/ 现有 v00 + v01..v08 共 10 个 .snapshot；8 个最终草稿与交付目录的 "
     "*.snapshot 逐一字节相同；8 个交付 PNG 的 sha256 与我实际看图时记录的完全一致。", True,
     "process fix: my own tooling bug, disclosed rather than hidden"),

    ("A23-v18", "A23-v17", "visual",
     os.path.join(DRAFTS, "v08-contact-sheet.snapshot"), png("contact-sheet.png"),
     "2026-10-05T02:14:25.463+08:00",
     "修正 draft() 后重跑全部 8 张，需要确认图像本身没有因为重跑而变化",
     "对 8 个 PNG 重算 sha256 并与 v16 记录的哈希比对；同时用 emit_a23.py 从交付文件重新"
     "实测 6 帧的尺寸、四角 alpha、alpha 包围盒与每帧 12 个单元坐标",
     "8 张全部 SAME（字节未变）；重算结果与 v16 完全一致：12 单元/12 色/2 种尺寸恒定，"
     "bbox 524x502→332x376 单调收缩，frame DSL 中 Image 标签数 = Text 标签数 = 0。"
     "再次打开 contact-sheet.png 与 cover.png 确认视觉无回归。", True,
     "confirmation pass after the tooling fix"),
]

ARTIFACTS = [
    "cover.png", "cover.snapshot",
    "frame-01.png", "frame-01.snapshot",
    "frame-02.png", "frame-02.snapshot",
    "frame-03.png", "frame-03.snapshot",
    "frame-04.png", "frame-04.snapshot",
    "frame-05.png", "frame-05.snapshot",
    "frame-06.png", "frame-06.snapshot",
    "contact-sheet.png", "contact-sheet.snapshot",
    "limitations.md", "frame-data.json", "timing.json",
    "snapshot-usage.md", "task-metrics.json",
]

VISUAL_EVIDENCE = [
    "frame-01.png .. frame-06.png: each opened individually with the image reader after "
    "rendering (6 separate views), plus crop.py zoom of frame-06 centre at 1.6x and of the "
    "frame-05 cluster at 1.8x to inspect the final figure and mid-animation overlap",
    "cover.png: opened as a full 1200x800 plate, then crop.py zoom of the capability card "
    "at 1.9x and of the left thumbnail strip at 1.7x to confirm no text overflow or overlap",
    "contact-sheet.png: opened to compare all 6 frames side by side in a single view",
    "probe images p01..p10, q1..q4 opened to confirm the capability probes and the "
    "rotation / transparency / CJK semantics before they were relied on",
]

UNRESOLVED = [
    "循环接缝不无缝：按题目要求第 1 帧分散、第 6 帧成图，6 帧循环播放时 6->1 存在一次大跳"
    "（实测中位 171.0px，约为常规相邻帧步长 34.33px 的 4.98 倍）。已在 timing.json 的 "
    "loop_seam 段如实标注 seamless=false，并给出三条外部后续方案；未宣称无缝。",
    "数学上 6 帧无法同时满足『第 1 帧分散 + 第 6 帧成图 + 无缝』，推导写在 "
    "timing.json 的 why_a_seamless_loop_is_impossible_here，未用含糊说法掩盖。",
    "未合成 GIF/APNG、未矢量化、未做 CMYK 转换、未生成任何假的目标格式文件：服务不支持，"
    "且题目明确不要求用额外工具导出。合成环节留给客户，见 limitations.md。",
    "客户若要 30fps 平滑播放需外部补间或更多关键帧（250ms/帧=4fps 是题目指定值）；"
    "生成器 N_FRAMES 可直接改，DSL 生成逻辑无需重写。",
]

NOTES = ("A23 delivered 1 RGB cover + 6 transparent keyframes + supplementary contact sheet, "
         "all rendered by open-snapshot from DSL generated by one shared parameter set. "
         "Capability boundary proven with 10 real service probes (gif/apng/svg rejected with "
         "PARSE_ERROR; invented animation, CMYK and vector attributes silently ignored) plus "
         "3 semantic probes (rotation about centre, true transparent background, CJK glyphs). "
         "Three real visual iterations fixed: overlapping core tiles and colliding rings in "
         "the final figure, motion too small to read between frames, and three silent text "
         "overflow / collision defects on the cover. All 8 final PNGs re-rendered byte-identical.")

def to_wrapup(rows):
    """_suite/wrapup.wrapup() unpacks 9 fields and derives recheck_result from the
    `complete` flag, so the richer 11-field records above are folded down to that
    shape here: the recheck text and the note are kept inside `changes` so nothing
    is lost from iterations.jsonl.
    """
    out = []
    for v, par, kind, dsl_f, img_f, viewed, obs, chg, cmp_, complete, note in rows:
        merged = "改动：%s ｜ 复验：%s" % (chg, cmp_)
        if note:
            merged += " ｜ 备注：%s" % note
        out.append((v, par, kind, dsl_f, img_f, viewed, obs, merged, complete))
    return out


if __name__ == "__main__":
    m = W.wrapup("A23", TASK_STARTED, FIRST_IMAGE, TASK_ENDED, to_wrapup(ITERATIONS),
                 artifacts=ARTIFACTS, visual_evidence=VISUAL_EVIDENCE,
                 unresolved=UNRESOLVED, notes=NOTES, status="completed",
                 rounds=["single-pass: 6 keyframes + cover + contact sheet"],
                 cases=["capability probes p01-p10", "semantic probes q1-q4",
                        "6 keyframes", "1 cover", "1 contact sheet"])
    import json
    print(json.dumps(m["counts"], ensure_ascii=False, indent=2))
    print("wall clock s        :", m["wall_clock_seconds_total"])
    print("sum request dur s   :", m["sum_of_request_durations_seconds"])
    print("failures            :", json.dumps(m["failures"], ensure_ascii=False)[:600])
    print("usage               :", json.dumps(m["usage"], ensure_ascii=False)[:300])
