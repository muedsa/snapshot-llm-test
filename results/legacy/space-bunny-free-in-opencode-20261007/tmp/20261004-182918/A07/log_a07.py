# -*- coding: utf-8 -*-
"""A07 wrap-up: log every version to iterations.jsonl, build task-metrics.json and
update the suite state.  Must be executed last."""
from __future__ import annotations

import io
import json
import os
import sys
from datetime import datetime

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import wrapup  # noqa: E402

TASK = "A07"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", TASK)
TMP = os.path.join(ROOT, "tmp", "20261004-182918", TASK)
MAP_PNG = os.path.join(OUT, "network-map.png")
CARD_PNG = os.path.join(OUT, "travel-card.png")
MAP_DSL = os.path.join(OUT, "network-map.snapshot")
CARD_DSL = os.path.join(OUT, "travel-card.snapshot")
PROBE = os.path.join(TMP, "preview", "probe-01.png")
PROBE_DSL = os.path.join(TMP, "drafts", "probe-01.snapshot")


def reqs():
    out = []
    with io.open(os.path.join(TMP, "requests.jsonl"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln:
                out.append(json.loads(ln))
    return out


R = reqs()
renders = [r for r in R if r["request_type"] == "render"]
ok_imgs = [r for r in renders if (r.get("content_type") or "").startswith("image/")]
STARTED = R[0]["started_at"]
FIRST_IMAGE = ok_imgs[0]["ended_at"]
ENDED = datetime.now().astimezone().isoformat(timespec="milliseconds")

# request_id -> timestamps, so every iteration can carry the real view time
T = {r["request_id"]: (r["started_at"], r["ended_at"]) for r in R}
MAP_REQ = [r for r in renders if r.get("response_file", "").endswith("network-map.png")]
CARD_REQ = [r for r in renders if r.get("response_file", "").endswith("travel-card.png")]


def mv(i):
    """viewed_at of the i-th map render (1-based)"""
    return T[MAP_REQ[i - 1]["request_id"]][1]


def cv(i):
    return T[CARD_REQ[i - 1]["request_id"]][1]


ITERS = [
    # ---- capability probe -------------------------------------------------
    ("A07-v01", None, "alternative", PROBE_DSL, PROBE, T["A07-req-006"][1],
     "探针图：验证 Transform 列主序 matrix 的旋转方向（E/S/NE/SW 四个方向是否与"
     "atan2 推导一致）、Container 的 shape=CIRCLE 与 border 是否同时生效、"
     "DejaVu Sans / Noto Sans CJK SC / Inter 是否含 U+2713 与 U+2715 字形。",
     "900x560 探针：4 条从 (200,200) 出发的旋转条 + 2 种圆形 + 3 组字形探测。",
     "全部通过：θ=-atan2(dy,dx)、a=cosθ,b=-sinθ,c=sinθ,d=cosθ 在屏幕上确为视觉逆时针；"
     "shape=CIRCLE 与 borderRadius=20 渲染一致；✓ ✕ 在三种字体下均有字形（无豆腐块）。"
     "据此决定用 matrix 画 45° 线段、用旋转矩形画 ✓/✕ 不必要（直接用字体字形）。", True),

    # ---- network-map.png --------------------------------------------------
    ("A07-v02", "A07-v01", "baseline", MAP_DSL, MAP_PNG, mv(1),
     "首张全网示意图。肉眼可见问题：(1) 用琥珀色包边高亮 3 条旅程后，整张图多出第四条"
     "线路的观感，黄色块在 S04/S05/S08 处堆叠；(2) S06 与 S12 的标签框重叠（脚本报告 "
     "label collisions: [('S06','S12')]）；(3) 图例区左上角“图例”二字与第一列表头"
     "“线路（颜色 + 字母）”重叠成“图例（颜色 + 字母）”；(4) D.warnings() 报 2 条文字"
     "溢出：图例“跨线交叉（缺口＝不断线，不可换乘）”被截断为“…不可换”，图面说明"
     "“· 区间数 = 站数 − 1；换乘 = 改乘另一条线”估算需 2 行。",
     "首版 DSL：1600x1000，269 个 Positioned；线路用 Transform matrix 旋转矩形，"
     "站点为圆，站名标签带半透明白底 chip，交叉处按 UNDER 优先级在低层线留 22px 缺口。",
     "首版结构成立，但高亮层与标签重叠必须修；两条文字溢出必须清零。", True),

    ("A07-v03", "A07-v02", "visual", MAP_DSL, MAP_PNG, mv(2),
     "上一版的问题已在渲染前用脚本定位并逐条处理：删除琥珀色旅程高亮（改为在右侧"
     "“全网总览”里用编号徽标交叉引用三条旅程）；合并图例首列表头；缩短交叉示例文字；"
     "把交叉注释从交叉点正上方（楔形只有 80px 宽）移到下方楔形区（y≈500 处宽 230px）"
     "并加引线；S06 标签锚点由 SE 改为 W。",
     "重排图例四列、加入“旅行卡上的三条旅程”小节、交叉注释下移、S06 改 W 锚点。",
     "重渲染后仍有 1 条文字溢出（信息面板“站间区间 16 段 · 双向可走 · 转折 45°/90°”），"
     "并且 S06 标签仍然压住红线斜段 —— 说明 W 锚点的纵向偏移算错了。", True),

    ("A07-v04", "A07-v03", "syntax-fix", MAP_DSL, MAP_PNG, mv(3),
     "定位到 label_box() 的锚点分支有运算符优先级与语义双重错误："
     "`cx + 11 + gap - 26 if d == \"E\" else cx + 8` 被三元运算符整体吞掉；"
     "且 W 落进了 y = cy + 11 + gap 的“下方”分支，导致 W 锚点的标签与站点同高以下，"
     "正好压在 S05→S06 的 45° 斜段上（D.est_width 报告 S06/S12 标签碰撞已消失，"
     "但斜段压字是看图才发现的）。",
     "重写锚点几何：E/W 纵向居中 y=cy-h/2，N/NE/NW 在上，S/SE/SW 在下，"
     "并把信息面板溢出串缩短为“站间区间 16 段 · 双向可走”。",
     "复渲染并放大 S06/S12 区域确认：斜段不再穿过 S06 标签；D.warnings() 清零；"
     "label collisions: []。", True),

    ("A07-v05", "A07-v04", "visual", MAP_DSL, MAP_PNG, mv(4),
     "放大交叉点 (700,390) 后发现：绿线缺口 22px 偏长，且绿线字母徽标正好落在缺口"
     "右上沿，看起来像绿线在那里“起站”，与终点大徽标混淆。",
     "缺口半长 11→8（总 16px）；绿线 C→S05 段徽标比例 0.65→0.78、蓝线 S04→S09 段"
     "0.25、红线 S05→S06 段 0.62，使所有字母徽标离交叉点 ≥99px；“换乘”药丸由 19px 高"
     "改为 24px 高、字号 17 的基线按手册经验值下移，文字不再溢出药丸。",
     "再次放大交叉点确认：绿线断开、蓝线连续、字母徽标远离缺口；药丸内“换乘”两字完整。", True),

    ("A07-v06", "A07-v05", "requirement-change", MAP_DSL, MAP_PNG, mv(5),
     "逐条核对 TASK.md“地图标签≥20”时发现信息面板行是 18/19px、交叉注释 19px、"
     "脚注 18px，不满足硬指标。",
     "把信息面板全部行、交叉注释、两行脚注统一提到 20px，并相应缩短 4 条文案；"
     "末尾留 28px 空白。",
     "出现 1 条新的溢出：信息面板“西港 → 研究所　4区间·1换乘”（全角空格占 20px）。", True),

    ("A07-v07", "A07-v06", "visual", MAP_DSL, MAP_PNG, mv(6),
     "信息面板第三条旅程行仍溢出（全角空格 + 中点导致估算 265px > 264px 框宽）。",
     "把分隔符由全角空格改为普通空格并去掉中点：'%s → %s %d区间 %d换乘'。",
     "D.warnings() 清零；label collisions: []；全图 16 个站名与编号、3 处换乘标记、"
     "1 处跨线交叉缺口、图例四列全部肉眼可读。", True),

    ("A07-v08", "A07-v07", "visual", MAP_DSL, MAP_PNG, mv(7),
     "补一次内容微调：页脚第二行下移 2px 使两行脚注行距均匀。此版与 v07 视觉等价。",
     "footnote 行 y 932→934。",
     "复渲染确认与 v07 无可见差异（同一 DSL 结构，仅坐标微调）。", True),

    ("A07-v09", "A07-v08", "visual", MAP_DSL, MAP_PNG, mv(8),
     "为满足留痕要求，给两个生成脚本加上 archive()：每次渲染前把 DSL 另存一份"
     "不可覆盖的 drafts/<tag>-vNN.snapshot。本次是加归档后的最终重渲染。",
     "build_map_a07.py 增加 archive()；本版 DSL 存为 drafts/map-v09-final.snapshot。",
     "最终 network-map.png：D.warnings() 为空，label collisions 为空，"
     "几何校验 0 问题（a07_common.validate）。", True),

    # ---- travel-card.png --------------------------------------------------
    ("A07-v10", "A07-v09", "baseline", CARD_DSL, CARD_PNG, cv(1),
     "首张 720x1280 行程卡。渲染成功但内容大面积缺失：只有页眉、站序链、"
     "无障碍结论行和页脚出现，三张白卡背景、序号徽标、标题、线路 chip 行、"
     "换乘行全部消失。",
     "首版 DSL：每条 query 一张卡，逐段列线路徽标 + 站序链 + 换乘行 + 无障碍判定。",
     "定位为 Python 变量遮蔽：render_card() 里的 `out, _ = chain_kids(...)` 把累积了"
     "整张卡的 out 列表整个覆盖掉，返回的只剩最后一个 chain 之后的元素。"
     "服务返回 200，不会有任何报错提示，只能靠看图发现。", True),

    ("A07-v11", "A07-v10", "syntax-fix", CARD_DSL, CARD_PNG, cv(2),
     "修复变量遮蔽（chain 结果改用 ck 接收），并把 chip 行重排为"
     "“线路名靠左 + 上车→下车·区间数靠右”，去掉与线路名重叠的第 N 段文字。",
     "修 out/ck 命名；chip 行左右分栏；无障碍判定与提示合并前的双行版本。",
     "整卡结构恢复。D.warnings() 仍有 5 条：替代路线标题右侧串 1 条、页脚 4 条全部"
     "估算需 2 行。", True),

    ("A07-v12", "A07-v11", "visual", CARD_DSL, CARD_PNG, cv(3),
     "压缩版面：页眉 168→158、卡间距 12→10、页脚 4 条文案缩短并把可用宽度从 628 "
     "放宽到 644。",
     "调整 HEAD_H / GAP / 页脚文案。",
     "页脚溢出从 4 条降到 1 条（第 1 条仍超 4px）。", True),

    ("A07-v13", "A07-v12", "visual", CARD_DSL, CARD_PNG, cv(4),
     "用 measure_card_a07.py 扫描 PNG 白色像素带，实测三张卡高 238/360/238px，"
     "而 card_metrics() 返回 260/382/260 —— 差值正好 28px，即无障碍提示行的高度"
     "在 card_metrics 里漏加了。后果是第一张卡的提示文字压在白卡下边框上"
     "（放大 crops/travel-card-card1-bottom.png 可见文字骑在圆角边框上）。",
     "修正 card_metrics()：把提示行的 28px 计入；同时把“判定 + 提示”合并成一行"
     "（chip + 加粗判定 + 灰色细节），行高 34，再把卡片上下留白调回 18、卡间距 14。",
     "重渲染后 D.warnings() 清零；实测白色带 169-406 / 443-802 / 839-1076，"
     "与 card_metrics 一致；页脚 1104-1254，底部留 28px。", True),

    ("A07-v14", "A07-v13", "requirement-change", CARD_DSL, CARD_PNG, cv(5),
     "复核“手机正文≥20”：页脚与页眉已是 20px，但替代路线的换乘竖线间距 16px "
     "偏挤，且“· 途经非无障碍站 书院、花园，可乘车经过”估算 385px > 376px 框宽。",
     "换乘竖线前后留白 16→22px；细节文案改为“· 经过非无障碍站 书院、花园（可乘车）”；"
     "不可行时改为“· 受限换乘站 东桥 S05（非无障碍）”；页眉元素上移到 y=20/66/106。",
     "最终 travel-card.png：D.warnings() 为空；三张卡 + 4 行页脚全部完整显示；"
     "琥珀色站名（公园/书院/东桥/花园）与 ✓/✕ 徽标在图上均正确对应 network.json 的 "
     "accessible 字段。", True),
]

# wrapup.wrapup takes 9-tuples; fold the re-check text into the `changes` field so the
# observed issue and the verification outcome stay together in iterations.jsonl.
ITERS = [it[:8] + ("改动：%s\n复验：%s" % (it[8], it[9]),) + it[10:] for it in ITERS]

m = wrapup.wrapup(
    TASK, STARTED, FIRST_IMAGE, ENDED, ITERS,
    artifacts=[
        {"file": "network-map.png", "kind": "final_png", "size": "1600x1000",
         "bytes": os.path.getsize(MAP_PNG), "dsl": "network-map.snapshot",
         "note": "服务真实响应原始字节，未做任何后处理"},
        {"file": "network-map.snapshot", "kind": "dsl", "bytes": os.path.getsize(MAP_DSL)},
        {"file": "travel-card.png", "kind": "final_png", "size": "720x1280",
         "bytes": os.path.getsize(CARD_PNG), "dsl": "travel-card.snapshot",
         "note": "服务真实响应原始字节，未做任何后处理"},
        {"file": "travel-card.snapshot", "kind": "dsl", "bytes": os.path.getsize(CARD_DSL)},
        {"file": "routes.json", "kind": "analysis",
         "bytes": os.path.getsize(os.path.join(OUT, "routes.json")),
         "note": "3 条 query 的最短路线、线路段、边数、换乘次数、无障碍判定与替代路线，"
                 "含 32 项自检"},
        {"file": "snapshot-usage.md", "kind": "report"},
        {"file": "task-metrics.json", "kind": "metrics"},
    ],
    visual_evidence=[
        {"image": "network-map.png", "views": 9, "reviewed_at": mv(9),
         "how": "read 工具整图查看 6 次 + crop.py 放大交叉点与 S06/S12 区域 3 次"},
        {"image": "travel-card.png", "views": 5, "reviewed_at": cv(5),
         "how": "read 工具整图查看 3 次 + crop.py 放大第一张卡下边缘与第二张卡替代路线块 2 次"},
        {"image": "preview/probe-01.png", "views": 1, "reviewed_at": T["A07-req-006"][1],
         "how": "read 工具整图查看，用于确认旋转矩阵方向与字形覆盖"},
    ],
    unresolved=[
        "迭代 v03~v08（地图）与 v02~v04（卡片）当时直接渲染到最终输出路径，"
        "同名 .snapshot 被后续版本覆盖，因此 drafts/ 只保留了探针与两个最终版本的 DSL；"
        "每一版的可观察问题与具体改动都记录在 iterations.jsonl 与 snapshot-usage.md 中，"
        "但中间版本的 DSL 文本本身没有留存。这是留痕上的实际缺口，如实说明。",
        "平台未提供任何 token / 图片用量 / 费用指标，task-metrics.json 中相关字段一律为 null，"
        "未按字符数或余额估算。",
    ],
    notes="A07 完成：1600x1000 network-map.png + 720x1280 travel-card.png + routes.json。"
          "地图站名/编号 16 个齐全，线路按站序真正连通，转折全部 45°/90°，"
          "1 处纯线条交叉用缺口+注释显式声明不可换乘，3 个换乘站用双环标记并带“换乘”药丸，"
          "线路用颜色+字母双重编码，各站无障碍状态逐站标注并在图例解释；"
          "卡片展示 3 条最少区间旅程及无障碍可行性，并给出 Q2 的无障碍最短替代（区间数相同、"
          "换乘 +1）。",
)
print(json.dumps({k: m[k] for k in ("task_id", "wall_clock_seconds_total",
                                    "sum_of_request_durations_seconds", "counts")},
                 ensure_ascii=False, indent=2))
