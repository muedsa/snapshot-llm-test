# -*- coding: utf-8 -*-
"""A09 wrap-up: iteration log + task-metrics.json + suite state."""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
SUITE = os.path.join(ROOT, "tmp", "20261004-182918", "_suite")
sys.path.insert(0, SUITE)
import wrapup  # noqa: E402

T = os.path.join(ROOT, "tmp", "20261004-182918", "A09")
D = lambda n: os.path.join(T, "drafts", n)  # noqa: E731
P = lambda n: os.path.join(T, "preview", n)  # noqa: E731
OUTREL = r"outputs\20261004-182918\A09"

STARTED = "2026-10-04T21:12:00+08:00"
FIRST_IMAGE = "2026-10-04T21:18:26.709+08:00"

ITERS = [
    # ---------------------------------------------------------------- probes --
    ("A09-v01", None, "alternative", D("v01-probe1.snapshot"), P("probe1.png"),
     "2026-10-04T21:19:10+08:00",
     "探针图：8 个面板比较 L（纯线性）与 M（已绕 pivot 合成）两种矩阵，配合 "
     "origin/alignment 的不同写法，验证矩阵列序、pivot 语义与顺时针方向",
     "先用本任务输入的印章做 120x120 对照面板，背景画出未变换的 120 框与 pivot 十字",
     "P1(L,origin=(0,0),CENTER) 与探针预期完全一致：红条由左侧转到顶部，"
     "即矩阵是列主序且顺时针为 a=cos,b=sin,c=-sin,d=cos；P2(M) 出现整体 +120,+120 位移，"
     "说明 origin=(0,0) 不改变 pivot，pivot 仍是子节点中心；P4 确认 mirror_horizontal 是左右翻转",
     False),
    ("A09-v02", "A09-v01", "alternative", D("v02-probe2.snapshot"), P("probe2.png"),
     "2026-10-04T21:21:30+08:00",
     "第一次 probe2 整张 400 PARSE_ERROR：Attr [alignment] value format error（alignment=\"null\" 不合法）",
     "去掉 alignment=\"null\" 的两个面板，改用 (0,0)/TOP_LEFT/CENTER 与省略 alignment 的组合重渲",
     "关键结论：alignment=\"TOP_LEFT\" 把矩阵作用在子节点左上角，因此可以直接把"
     "「绕 pivot 合成后的完整矩阵」写进 matrix；P8(省略 alignment) 与 TOP_LEFT 表现一致。"
     "于是 12 个标本都写成 origin=\"(0,0)\" alignment=\"TOP_LEFT\" + 完整组合矩阵",
     False),
    # ------------------------------------------------------------- baseline --
    ("A09-v03", "A09-v02", "baseline", D("v03-atlas.snapshot"),
     os.path.join(T, "preview", "transform-atlas.png"),
     "2026-10-04T21:30:05+08:00",
     "第一版整图：12 格几何全部正确（旋转方向、镜像、非等比缩放、圆点变椭圆都对），"
     "但图例首行 4 个色块标签互相压字、图例第二行超出卡片右边界、底部说明第 4 行与脚注重叠、"
     "T12 的 x 刻度数字压到矩阵数字",
     "首版按分析几何排版，没有先估算文字宽度",
     "12 格主体与矩阵全部正确，其余为排版问题，进入迭代修复",
     False),
    ("A09-v04", "A09-v03", "visual", D("v04-atlas.snapshot"),
     os.path.join(T, "preview", "transform-atlas.png"),
     "2026-10-04T21:34:20+08:00",
     "v03 看到的 4 处排版问题",
     "图例色块改为固定 296px 槽位并加宽读图行；x 刻度数字统一上移到表头下方一排；"
     "底部说明改为 3 列 × 3 行、脚注单独一行",
     "图例首行不再互压；但读图行文字仍被 1264px 框截断（第二行被丢弃）",
     True),
    ("A09-v05", "A09-v04", "visual", D("v05-atlas.snapshot"),
     os.path.join(T, "preview", "transform-atlas.png"),
     "2026-10-04T21:36:10+08:00",
     "dsllib 报出 3 条容量告警：图例读图行、组合规则第 1、2 行估算宽度超过给定框宽",
     "缩短读图行文案；底部三列改成不等宽（464 / 364 / 388）并逐行给 w,h 让告警生效",
     "告警清零，图例与底部说明全部完整显示",
     True),
    ("A09-v06", "A09-v05", "visual", D("v06-atlas.snapshot"),
     os.path.join(T, "preview", "transform-atlas.png"),
     "2026-10-04T21:37:50+08:00",
     "放大图例后发现 R2/R3 的 @(36,72)、@(64,8) 不见了：Text 在单行高度框里放不下时静默换行，"
     "第二行被静默丢弃（正是手册第 3 节的静默行为）",
     "去掉色块标签的 width/height，让 Text 用自然宽度，并改用 296px 固定槽位排布",
     "R1 的 @(8,8) 恢复了，但 262px 仍比 R2/R3 的实际宽度略窄",
     True),
    ("A09-v07", "A09-v06", "visual", D("v07-atlas.snapshot"),
     os.path.join(T, "preview", "transform-atlas.png"),
     "2026-10-04T21:39:30+08:00",
     "R2/R3 的坐标尾部仍被截断；同时发现图例第二行整行不见了",
     "色块标签完全不给宽度（自然宽度），槽位放到 300px",
     "R2/R3 恢复完整；图例第二行消失是我改脚本时把该行连同旧代码一起替换掉了（自查 DSL 文本发现 "
     "没有「读图」二字），不是渲染问题",
     True),
    ("A09-v08", "A09-v07", "visual", D("v08-atlas.snapshot"),
     P("v08-atlas.png"),
     "2026-10-04T21:41:40+08:00",
     "v07 的两处遗留：读图行缺失、R3 与圆角色块间距偏紧",
     "补回读图行；槽位改 312px；y 轴刻度数字框宽 36→42",
     "图例两行完整、四个色块互不压字；12 格全部无重叠",
     True),
    # ------------------------------------------------------- pixel checking --
    ("A09-v09", "A09-v08", "requirement-change", D("v09final-atlas.snapshot"),
     P("v09final-atlas.png"),
     "2026-10-04T21:52:00+08:00",
     "像素核对脚本两次判 FAIL：先是 T05/T09 的红/蓝外框被 60 的颜色距离容差误判"
     "（靛蓝色徽章与蓝色距离 57），改成 25 后又发现灰描边会把变换后的主体切成多块，"
     "改用「全部命中像素取并集」；旋转矩形的面积比要用真实面积（w·h·|det|）而不是外接框面积",
     "图例读图行补一句「T01 恒等变换，描边与实色重合」；核对脚本改为 DIST=25 + 并集 + 真实面积",
     "48 项测量（12 格 × 3 矩形外框 + 1 圆点中心）全部通过，最大偏差 1.22px ≤ 1.5px；"
     "最终 PNG 即交付文件",
     True),
]

# wrapup.unpack expects 9 fields per record; keep the recheck result as part of
# the "changes" text so nothing is lost in iterations.jsonl
ITERS9 = [(v, par, kind, dsl, img, viewed, obs, chg + " ｜复验：" + recheck, comp)
          for (v, par, kind, dsl, img, viewed, obs, chg, recheck, comp) in ITERS]

m = wrapup.wrapup(
    "A09", STARTED, FIRST_IMAGE, "2026-10-04T21:56:00+08:00", ITERS9,
    artifacts=[
        OUTREL + r"\transform-atlas.png (1600x1200, 257005 bytes, 服务原始响应)",
        OUTREL + r"\transform-atlas.snapshot (135232 bytes, 与 PNG 完全对应的完整 DSL)",
        OUTREL + r"\geometry-audit.json (92009 bytes)",
        OUTREL + r"\snapshot-usage.md",
        OUTREL + r"\task-metrics.json",
    ],
    visual_evidence=[
        "probe1.png / probe2.png：对照探针确认矩阵列序、pivot 语义与顺时针方向（1x 查看）",
        "transform-atlas.png：v03/v04/v05/v06/v07/v08 整图逐版查看（1x）",
        "crops/transform-atlas-legend-v06.png、legend-v08.png：图例放大 1.5x 核对标签完整性",
        "crops/transform-atlas-cell-T01.png、T07.png、T11.png、T12.png：单格放大 2.6x 核对",
        "crops/transform-atlas-notes-final.png：底部说明放大 1.5x 核对",
        "pixel-verification-final.json：对交付 PNG 做 48 项像素测量，最大偏差 1.22px",
    ],
    unresolved=[
        "服务在 A09-req-008 出现过一次「HTTP 200 头已到达但读取响应体超时（180s）」的瞬时故障；"
        "同一 DSL 原样重发即成功，未修改任何内容，最终 PNG 来自成功的那次响应。",
        "v03–v07 的整图 PNG 被预览脚本按同一文件名覆盖，没有逐版单独留档；"
        "每版 DSL 已按版本号保存在 tmp/20261004-182918/A09/drafts/，"
        "v08 与最终版另存为 preview/v08-atlas.png、preview/v09final-atlas.png。",
    ],
    notes="12 个标本全部用 Transform.matrix（origin=(0,0) alignment=TOP_LEFT）渲染完整组合矩阵；"
          "像素核对 48/48 通过，最大偏差 1.22px。",
    cases=[],
)
print("counts:", m["counts"])
print("wall:", m["wall_clock_seconds_total"], "s; first image:", m["wall_clock_seconds_to_first_usable_image"], "s")
print("failures:", m["failures"])
print("paths:", m["paths"])