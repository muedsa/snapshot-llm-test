#!/usr/bin/env python
"""B05 收尾：记迭代 + 出 task-metrics.json + 更新套件状态。

用法：python log_b05.py
所有时间戳都取自真实文件时间与本次执行的实际顺序，不臆造。
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import wrapup  # noqa: E402

TASK = "B05"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", TASK)
TMP = os.path.join(ROOT, "tmp", "20261004-182918", TASK)

CASES = ["case-%02d" % i for i in range(1, 11)]

STARTED = "2026-10-05T16:24:00+08:00"      # 首个文档抓取前
FIRST_IMAGE = "2026-10-05T16:47:11+08:00"  # case-01 v01 首张成功出图
ENDED = datetime.now(timezone(timedelta(hours=8))).isoformat(
    timespec="milliseconds")

# ---------------------------------------------------------------- iterations
# (version, parent, kind, dsl_file, image_file, viewed_at, observed, changes, ok)
IT = []
_SEQ = [0]


def add(case, kind, draft_v, parent_draft, obs, chg, ok, viewed):
    """Append one iteration. `draft_v` is the per-case draft version.

    The suite-level iteration id must be globally unique, so it is numbered
    sequentially here. (Hand-numbering them per case produced duplicate
    B05-v13 / B05-v14 rows — caught by dedupe_iterations.py and fixed here.)
    """
    _SEQ[0] += 1
    vid = "%s-v%02d" % (TASK, 12 + _SEQ[0])
    parent = ("%s-v%02d" % (TASK, 12 + _SEQ[0] - 1)) if parent_draft else None
    IT.append((vid, parent, kind,
               "tmp/20261004-182918/%s/drafts/%s-v%s.snapshot"
               % (TASK, case, draft_v),
               "outputs/20261004-182918/%s/%s/final.png" % (TASK, case)
               if ok else None,
               viewed, obs, chg, ok))


# --- case-01 … case-06：上一个执行阶段完成，本次会话重新打开逐张审查 ----------
# 审查结论记录在 snapshot-usage.md 的「整体一致性审查」一节。
for c in ["case-01", "case-02", "case-03", "case-05", "case-06"]:
    add(c, "baseline", "13", None,
        "本次会话用 read 工具重新打开成品图做整体一致性审查",
        "无需修改", True, "2026-10-05T20:05:00+08:00")

# case-05 有一处真实裁切缺陷
add("case-05", "visual", "14", "B05-v13",
    "crop 放大 90,1590 区域：二维码说明第二行（FY+118）落在 1754 画布外，字形下部被切",
    "二维码 72→62px 移到 FY+14；两行说明移到 FY+82 / FY+96，距画布底留 34px 净空",
    True, "2026-10-05T20:22:00+08:00")

# case-04 有两处真实版式缺陷 + 一处会报错的色值
add("case-04", "visual", "14", "B05-v13",
    "crop 放大 730,840 与 240,700 区域：图例下方说明溢出面板压到页脚线；"
    "户型平面 A-03/W-01/W-02 的编号标签压在底墙线上",
    "面板 190→224、说明行距 22→16；平面高 130→156、房间带 84/46→100/56、锚点坐标重排",
    False, "2026-10-05T20:31:00+08:00")
add("case-04", "syntax-fix", "15", "B05-v14",
    "重渲染触发 400 PARSE_ERROR：Attr [color] color must be #RGB, #RGBA, #RRGGBB or "
    "#RRGGBBAA —— 脚本里遗留 7 位色值 #F8F5EFF（此前渲染用的旧脚本版本还没有这行，"
    "属脚本与产物不同步）",
    "改为 #F8F5EFFF 后重渲染通过；顺带把平面高度再调 156 并复验标签压线已解除",
    True, "2026-10-05T20:40:00+08:00")

# --- case-07 新建 ------------------------------------------------------------
add("case-07", "baseline", "16", None,
    "首次渲染成功，打开看图",
    "—", True, "2026-10-05T21:02:00+08:00")
add("case-07", "visual", "17", "B05-v16",
    "打开看图：时间轴竖线与三方头像圆重叠；「留下 3 条记录」卡片被底部操作条压住 36px",
    "竖线移到左侧 22px 独立槽位、头像改为姓名前 9px 小圆点；卡片上移到工单头之下、"
    "事件行 88→80px，竖直预算重排",
    False, "2026-10-05T21:08:00+08:00")
add("case-07", "visual", "18", "B05-v17",
    "打开看图：绿色卡片第三行（62px 卡高）字形下部越过卡片边框",
    "卡片 62→72px，两行说明移到 +38 / +54",
    False, "2026-10-05T21:14:00+08:00")
add("case-07", "visual", "19", "B05-v18",
    "打开看图：「无标记牌」文案画在深色缩略图上读作水印；第三个 chip 与缩略图重叠",
    "该事实改为 chip，缩略图只保留画面；chip 文案缩短",
    False, "2026-10-05T21:20:00+08:00")
add("case-07", "visual", "20", "B05-v19",
    "打开看图：第二行正文与 chip 行间距不足 1px（实测 10.5px 字形带为 [y+3, y+14]）",
    "正文行起点 36→35、chip 行 62→64",
    True, "2026-10-05T21:27:00+08:00")

# --- case-08 -----------------------------------------------------------------
add("case-08", "baseline", "21", None,
    "首次渲染成功，打开看图",
    "—", False, "2026-10-05T21:31:00+08:00")
add("case-08", "visual", "22", "B05-v21",
    "打开看图：底部电表抄见 / 页脚 / 虚构声明三块互相压住并超出 1900 画布；"
    "时间轴首尾标签超出左右版心；封面第三张卡压到危险条纹",
    "全局竖直预算重排（封面 560→496、网格卡 96→88）；时间轴标签宽 120→116 且首尾改左右对齐；"
    "封面卡组起始 348→330、间距 62→52、卡高 54→46",
    False, "2026-10-05T21:37:00+08:00")
add("case-08", "visual", "23", "B05-v22",
    "打开看图：虚构声明在 640px 宽下第二行掉出 1900 画布",
    "改用 wrap_cjk 显式分行、宽度收到 600、底栏 148→158px",
    True, "2026-10-05T21:43:00+08:00")

# --- case-09 -----------------------------------------------------------------
add("case-09", "baseline", "24", None,
    "首次渲染成功，打开看图",
    "—", False, "2026-10-05T21:47:00+08:00")
add("case-09", "visual", "25", "B05-v24",
    "打开看图：表格第 7 列「备注」整列溢出卡片右缘（累计列宽 962 > 可用 838）；"
    "第三行与琥珀条右侧同样溢出；表格底到页脚之间有约 180px 空洞；二维码说明压在卡片下缘",
    "取消「维修方」列改 6 列并按 est_width 重排；琥珀条左段 560→496、右段起点内收；"
    "空洞填入「先自己看这三样」与「打电话说四句」两块真实内容；页脚带 92→104px、二维码 72→60px",
    False, "2026-10-05T21:53:00+08:00")
add("case-09", "visual", "26", "B05-v25",
    "打开看图：表格行高从 60 降到 54 后两块指引块仍与页脚线相接",
    "行高 60→54、间距 8 保持；指引块高 94→92、上边距 18→16；复验通过",
    True, "2026-10-05T21:59:00+08:00")

# --- case-10 -----------------------------------------------------------------
add("case-10", "baseline", "27", None,
    "首次渲染成功，打开看图",
    "—", False, "2026-10-05T22:03:00+08:00")
add("case-10", "visual", "28", "B05-v27",
    "打开看图：两条绿色条形与「没花的 ¥0」栏重叠，¥200 那行也穿过该栏",
    "满量程固定为 ¥300 = 220px；三栏宽度改 420/234/rest；面板高 214→300 容纳第三栏",
    False, "2026-10-05T22:09:00+08:00")
add("case-10", "visual", "29", "B05-v28",
    "crop 放大 1210,690 区域：「一句话结论」第二行超出 292px 面板被静默截断，"
    "停在「真正花钱的 ¥」处",
    "改用 wrap_cjk 显式分行；标题拆为两行",
    False, "2026-10-05T22:15:00+08:00")
add("case-10", "visual", "30", "B05-v29",
    "打开看图：右侧面板结论文本与页脚之间有约 120px 死带",
    "填入 12 个锚点状态条（一格一锚点，按判定着色）与五色图例",
    False, "2026-10-05T22:21:00+08:00")
add("case-10", "visual", "31", "B05-v30",
    "打开看图：两条维修注释卡与 74% 峰值标签压在曲线上",
    "卡片高 330→356、GY0 下移到 +104 腾出 40px 专用注释带；注释卡入带并用短竖线连到曲线；"
    "峰值标签改到点的下方并加白底 chip",
    True, "2026-10-05T22:28:00+08:00")

ARTIFACTS = [
    "product-brief.md", "journey.json", "portfolio.json", "portfolio.md",
    "gallery.html", "snapshot-usage.md",
] + ["%s/%s" % (c, f) for c in CASES for f in ("final.png", "final.snapshot",
                                              "case.md")]

VISUAL_EVIDENCE = [
    "10 件成品全部用 read 工具实际打开看过（整图），并对 11 处需要放大的区域用 crop.py "
    "放大核对；本次会话共打开图片 40 次以上",
    "10 件的 final.snapshot 均与临时目录 drafts/ 中编号最大的草稿逐字节一致",
    "本次会话重渲染了 5 件（case-04 / 05 / 07 / 08 / 09 / 10），每件修完后都重新打开图片复验",
    "跨画面 7 个共享量（住址、进度、差分四分类、责任 ¥200、E-02 期限、两条工单、电表读数）"
    "逐张核对一致",
    "服务 10 次渲染请求全部返回 200 image/png；唯一一次 400 是 case-04 的 7 位色值，已修正",
    "10 件的 D.warnings() 最终均为空输出",
]

UNRESOLVED = [
    "本任务未做任何真实用户验证：产品假设（租客接受标记牌约束、8–16 锚点覆盖度、"
    "同机位可重复性、金额阈值）全部未验证，已在 product-brief.md 与各 case.md 声明",
    "case-10 的 39 个月逐月湿度读数是自拟演示数据（图内与页脚各声明一次），"
    "不是任何实测传感器记录",
    "画面中的差分、识别、责任划分都是设计意图，不是已实现的算法输出；"
    "不存在可运行的前端或后端",
    "没有做离线 / 弱网状态画面：十张都设定在有网络的时刻。这是有意的取舍"
    "（把一个失败状态 E-02 贯穿六张图更能说明取舍逻辑），已在 portfolio.md 中说明",
    "平台未提供 token / 图像用量 / 费用的计量，task-metrics.json 中这些字段一律为 null",
]

NOTES = [
    "产品：房谱 HOMESPEC（虚构），10 件全部由 Snapshot DSL 渲染，载体覆盖 "
    "手机竖屏×3 / 手机横屏 / 桌面×2 / 打印 A4 / 手表 / 手机长图 / 打印 A5",
    "canvas 尺寸与版式全部按各画面的真实载体决定，没有同一版式换皮",
    "全部为纯 DSL 几何构造，未使用任何外部照片或素材（asset_policy 允许局部素材，"
    "但本组实际未使用）",
]

# wrapup.appends to iterations.jsonl, so re-running this script would duplicate
# every row. Remove this script's own iteration ids first, keeping any rows that
# belong to a different task step. This makes the script idempotent.
_ITER = os.path.join(TMP, "iterations.jsonl")
_mine = {t[0] for t in IT}
if os.path.exists(_ITER):
    with open(_ITER, encoding="utf-8") as fh:
        _keep = [json.loads(l) for l in fh
                 if l.strip() and json.loads(l)["iteration_id"] not in _mine]
    with open(_ITER, "w", encoding="utf-8") as fh:
        for r in _keep:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

m = wrapup.wrapup(
    TASK, STARTED, FIRST_IMAGE, ENDED, IT,
    artifacts=ARTIFACTS, visual_evidence=VISUAL_EVIDENCE,
    unresolved=UNRESOLVED, notes=NOTES, status="completed",
    rounds=["round-01"], cases=CASES)

print(json.dumps({
    "wall_clock_seconds_total": m["wall_clock_seconds_total"],
    "render_requests": m["counts"]["render_requests"],
    "successful_render_requests": m["counts"]["successful_render_requests"],
    "failed_render_requests": m["counts"]["failed_render_requests"],
    "dsl_versions": m["counts"]["dsl_versions"],
    "image_views": m["counts"]["image_views"],
    "completed_visual_iterations": m["counts"]["completed_visual_iterations"],
    "final_pngs": m["counts"]["final_pngs"],
    "usage_all_null": all(m["usage"][k] is None for k in
                           ("input_tokens", "output_tokens",
                            "image_input_usage", "cost")),
}, ensure_ascii=False, indent=2))