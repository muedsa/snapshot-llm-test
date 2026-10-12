"""B03 wrap-up (final): log iterations from real evidence, run wrapup, fix B-track counts.

Row sources, nothing invented:
  * successful final renders  <- tmp/20261004-182918/B03/requests.jsonl
  * failed renders             <- same file (image_file = null, kind = syntax-fix /
                                  service-error, never counted as visual iterations)
  * diagnoses and fixes        <- each case's own case.md 「迭代过程」 section
  * the three wrap-up review fixes <- performed and verified in this session

viewed_at is the render's response completion time. The viewing action happened
immediately afterwards in the same session but was not separately timestamped, so
the render completion time stands in; this is stated in every visual row's text
rather than passed off as a precise click time.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMP = os.path.join(ROOT, "tmp", RUN, "B03")
OUT = os.path.join(ROOT, "outputs", RUN, "B03")
DRAFTS = os.path.join(TMP, "drafts")
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))

import wrapup  # noqa: E402

VIEW_CAVEAT = ("viewed_at = 该响应/渲染的完成时间（requests.jsonl 的 ended_at）；"
               "看图紧随其后但未单独打点，故用完成时间代替。")

# kind: "V" = a version that produced an image, "F" = a request that failed and
# produced no image (never counted as a visual iteration).
# Each entry: (kind, observed_issue, changes)
ITERS = {
    "case-01": [
        ("V", "每个面板的内容整体偏移了面板原点（把画布绝对坐标当成了面板局部坐标）",
         "改用 wlib.Frame 的面板局部坐标；随后发现 Frame 又加了一次原点，修 Frame"),
        ("V", "5 处排版问题：表头 kicker 压状态 chip、罗盘说明压读数行、"
              "潮位面板 x 轴末端「时」与刻度打架、面板底部 4 行信息溢出、"
              "底部波高条幅度太小", "逐条改坐标与行距"),
        ("V", "状态 chip 文字被裁（est_width 用 0.55em 拉丁估算，DejaVu Sans Mono "
              "实际 0.605em）；低潮标签压住曲线",
         "wlib.chip 增加 mono=True 走真实 advance；低潮标签移到点位右上空白处"),
        ("V", "复查 crops/final-c01-tidezoom.png，高低潮标签与刻度清晰", "保留，仅复看确认"),
        ("V", "收尾复审：标签写「亏凸月 · 照亮 72%」而画面是约 20% 的右侧蛾眉，"
              "且与本页时间戳的真实月相（37.0% 残月）也不符",
         "删掉硬编码 MOON_ILLUM=0.72，改由 Meeus 平距角实算 k；晨昏线改用 ClipOval + "
         "176 行 1px 细条按 R(1−2k) 半椭圆填充，逐行 LINEAR 渐变给 Lambert 明暗；"
         "页脚注明月相为真实算出"),
    ],
    "case-02": [
        ("F", "ClipOval 里并列渐变盘与文字 → PARSE_ERROR Tag ClipOval only can have "
              "one child", "改成 ClipOval > Stack(EXPAND) > [Container, Text]"),
        ("F", "borderLeft=\"14 SOLID\" 少写颜色 → PARSE_ERROR Failed requirement",
         "补 #RRGGBBAA"),
        ("V", "票面用 Stack fit=\"LOOSE\" + alignment，所有非定位子节点按 alignment "
              "叠在���一处", "改用 Column crossAxisAlignment=\"STRETCH\"（正解，不是打补丁）"),
        ("F", "dim_v 把 Positioned 塞进 Container > Transform → RENDER_ERROR "
              "renderBox.parentData must be StackParentData；尺寸线还用绝对坐标被 "
              "Frame 又加了一次原点", "尺寸线全改面板局部坐标，Positioned 移回 Stack 层"),
        ("V", "票面 Column 内容比可用高度多约 37 px",
         "收紧 SizedBox 间距、票号 34→30、padding 24→18"),
        ("V", "底部约 300 px 空白；尺寸表被 sheet 的 Stack HARD_EDGE 裁掉；"
              "尺寸标注按 0.55em 估算宽度会被截成 \"250 px = 90\"",
         "调整稿面高度与画布高度；尺寸标注按等宽字体 0.605em 重算宽度"),
        ("V", "收尾复审：B 牌印「合计 86 元」而三行是 32+18+12=62 元（差 24）；"
              "票面还写着「外带 TAKEAWAY / 堂食」，与本稿标题和尺寸表的「取餐牌 B」矛盾",
         "给 B 牌单独 ORDER_B 明细并用 sum() 求和；副标题统一成「取餐牌 PICKUP / "
         "台号 T-07 · 预计 11 分钟」"),
    ],
    "case-03": [
        ("F", "作业卡写 ELEVATION_16 + 自定义阴影混写 → PARSE_ERROR elevation only "
              "allow use ^ELEVATION_(\\d+)$；探针第 3 行的 INNER/SOLID 两条 "
              "blurRadius 都是 0，触发同一边界",
         "作业卡改成纯自定义双阴影；探针的 INNER/SOLID 给出非零 blurRadius"),
        ("V", "探针里 Stack 与 ClipRRect 两个视口看起来一样，因为卡片离视口边缘还有 "
              "100 多像素，投影根本没越界",
         "视口改成 254×96、卡片 226×70，只差 14/13 px，两者差别立刻可见"),
        ("V", "作业卡右上「需 6 箱」「已拣 2」被卡片右边缘切掉",
         "用 probe_09 的 8 组对照排除服务端 textAlign 语义，定位为自己的坐标层级错"
         "（在卡片自己的 Stack 里用了面板局部坐标）→ 改卡片局部坐标"),
        ("V", "候选列表标题与触控按钮底边差 2 px 打架", "按钮上移 8 px、标题下移 2 px"),
    ],
    "case-04": [
        ("V", "首版渲染完成，作为基线打开查看", "—"),
        ("V", "主视角矩阵透视项 0.0021 把整图甩到左上并出血；缩略图因 bw=(w−120)·s 在 "
              "145 px 盒里算成 25 px，排缩成一列小点；行标签互相压",
         "行距计入 label_h；margin 改自适应 min(120, w·0.30)（同时修掉 minWidth must be "
         "between 0 and maxWidth）；透视项降到 0.0004"),
        ("V", "行标签仍压住上一排（y += rh + gap 漏了 label_h）；主视角仍有明显斜切感；"
              "「确认选座」按钮被面板裁掉",
         "y += rh + gap + label_h；旋转 −4.5°→−3.0°、透视 0.0006→0.0004；按钮上移压缩"),
        ("V", "复查四个缩略图，四种矩阵在同一份几何上产生了肉眼可辨的差异且都无出血",
         "保留，仅复看确认"),
    ],
    "case-05": [
        ("V", "圆形镜头几乎全黑——不是裁剪失效，而是选的放大窗口 09:00–12:12 正好在群"
              "包络最低点（env≈0.12）；ClipRRect 内嵌说明文字压在网格上读不出来",
         "窗口换到 15:24–18:36；说明文字移到卡片下方，缩略图缩到 156×100"),
        ("F", "clipBehavior=\"SAVE_LAYER\" → PARSE_ERROR No enum constant "
              "ClipBehavior.SAVE_LAYER",
         "只能用全称 ANTI_ALIAS_WITH_SAVE_LAYER（图上仍用短标签显示）"),
        ("V", "①全景的「时/h」轴名与第一个刻度「00」重叠", "轴名左移到 x=GX−44"),
        ("V", "复查三视图：全景看出两次能量峰、镜头看清主峰横向漂移、圆角卡的对角圆角与"
              "内嵌层都成立", "保留，仅复看确认"),
    ],
    "case-06": [
        ("F", "RENDER_ERROR Document contains more than 4096 elements，定位到雷达的 "
              "12 条辐条（W.seg 用点链画斜线，每条约 200 个元素）",
         "换成两条轴对齐十字线 + 12 个边缘刻度（各 1 个元素）"),
        ("V", "对照卡①文字原本画在 ImageFiltered 外面所以是锐的，与「字也糊」的标题矛盾；"
              "对照卡③用 SCREEN + 很浅染色，模糊几乎不可见",
         "把文字挪进滤镜内部；改用 blendMode=DIFFERENCE"),
        ("V", "方位标签用雷达区局部坐标调用了面板级 Frame.at，整体少加了一个 (RX, RY)，"
              "N 跑到面板外面", "补上偏移，并从环外移到环内"),
        ("V", "放大核对主卡，确认「背景糊 / 读数不糊」成立", "保留，仅复看确认"),
    ],
    "case-07": [
        ("V", "首版渲染完成，作为基线打开查看",
         "按「ColorFiltered 能读背景」的假设做的第一版"),
        ("V", "看图发现 ColorFiltered(color=M, MULTIPLY, Container(color=M)) 渲染出的是 "
              "M×M（#DA004D）而不是「M 压在青上」；v1 的矩阵格把两版并排画，根本没重叠",
         "用探针做决定性实验（子=C、滤=M、MULTIPLY）确认是子×滤；矩阵格改成"
         "「下版满格 + 上版盖右半」"),
        ("V", "梯子四格 220 px 宽却按 180 px 步进，互相压在一起",
         "版面改成三个轴对齐矩形区域，让每个区域的 under 都是纯色；归一化坐标 + "
         "SQ=168 使四格独立"),
        ("V", "矩阵 96 px 格导致最后一行压住说明文字", "收到 88 px"),
    ],
    "case-08": [
        ("F", "ROSE + \"80\" 拼出 11 位 hex → PARSE_ERROR；a.r(x, y, w, 1, color=…) 与 "
              "Frame.r 的位置参数冲突 → TypeError",
         "改 ROSE[:7] + \"80\" 与 a.r(x, y, w, color=…, h=1)"),
        ("F", "探针里把 Positioned 塞进 <Opacity> → RENDER_ERROR renderBox.parentData "
              "must be StackParentData（Opacity 不是 Stack，不接受定位子节点）",
         "新增 plate()（不带 Positioned 的纯 Container）供 Opacity 内部使用"),
        ("V", "叠加实验里的条纹画在色块上面，把两个 Opacity 组糊成一片；边界四条溢出面板",
         "把条纹移到最底层；边界收到面板的第二行"),
        ("V", "图例行高 40 px 让底部四条实测结论被裁", "行高改 36，并把结论移出图例"),
    ],
    "case-09": [
        ("F", "写 #9CA3AFF（9 位 hex）→ PARSE_ERROR Attr [color] color must be …；"
              "另一个 text= 属性里塞了 0B0B0F 占位文本被 dsllib 宽度检查报警",
         "改 8 位 #RRGGBBAA；清掉占位文本"),
        ("V", "右栏兼容性矩阵最后一列被推出画布右缘；变更清单第 12 条落在摘要带底下",
         "矩阵改独立标签列 + 5 个等宽数据列；变更行距 56→50"),
        ("V", "迁移 diff 两段代码各被截 1–2 行（按 1.2em 估行高，实际 DejaVu Sans Mono "
              "段落行距约 1.55em）；类型标注最后一行也被切",
         "每段盒子 72→80 px；类型标注去掉一个空行、盒子 106→114 px"),
        ("V", "「本版数字」标题与时间轴最后一行重叠；右下角装饰线语义的两行说明撞面板底边",
         "时间轴行距 38→34、标题下移到 730、统计区起点 788；装饰线行距 36、注释压成一行"),
        ("V", "4× 裁切发现 SOLID 装饰线几乎看不见（1.6 px 在 14 px 字上太细）",
         "每行给不同 decorationThickness（2.6/2.0/2.4/2.0）；类型标注最后一行缩短到不折行"),
        ("V", "收尾复审：对着变更清单数 chip 得 BREAKING 2 / DEPRECATED 2 / ADDED 3 / "
              "FIXED 5 = 12，与表头 12 ENTRIES 一致；但摘要写「没有引入新的破坏性变更，"
              "仅有两项弃用与七项修复」",
         "三个数字改为从 CHANGES 实算（_CNT）并加 assert 四类之和 = 12；文案改为"
         "「12 条变更里 2 条破坏性变更、2 条弃用、3 条新增、5 条修复」"),
    ],
    "case-10": [
        ("F", "daylen() 里把 acos() 的弧度当角度用（漏 degrees()），12 个月昼长全变 "
              "0.24 h → 柱高为负 → PARSE_ERROR minHeight must be between 0 and maxHeight；"
              "lo/hi 设成 10.4/14.2 时 12 月的 9.97 h 仍落在下界外",
         "改 2·degrees(acos(−tanφ·tanδ))/15；lo/hi 改 9.8/14.2"),
        ("F", "FractionallySizedBox 直接作为 Row 的子节点 → PARSE_ERROR widthFactor "
              "needs a finite maximum size（Row 给非 flex 子节点无界宽度）",
         "每根条包一层 Flexible(flex=1, fit=\"LOOSE\")"),
        ("V", "看图发现剖面被压成 12 px 高的一条线（把「米」当成像素，层高 3.15 px）",
         "引入 SCALE = 17 px/m，四层 214 px、窗带 25.5 px，补 1 px = 0.0588 m 比例注记"),
        ("F", "wlib.seg() 返回 list 被我用 k.append() 塞进去 → Python TypeError "
              "sequence item 153: expected str instance, list found", "改成 k += "),
        ("V", "太阳光线从建筑右上角往右上画、长度 130 px，压穿了右侧进深条的标题与第一行",
         "起点贴到建筑边缘、长度收到 96 px，说明文字移到地面线下方"),
        ("V", "逐时表第 7 行（15:00）压在脚注上；「三个代表日」两行脚注第二行被裁；"
              "缩略图里「冬至」标签压在日轨圆点上",
         "表行距 24→22、脚注上移并拆成两行独立文字；标签从圆心下方移到顶部，"
         "日轨半径 54→46"),
        ("V", "F1–F4 四行各自重复「最大 09:00 → 4.03 m」，底部两行脚注撞出面板",
         "每行只留 09:00 数值，「各层同值（南立面无遮挡）」集中写在下面；"
         "行距 82→80，整体上提 8 px"),
    ],
}

# The last visual entry of each case is the version that produced the delivered
# PNG and was re-viewed after the change, so only that one is claimed as a
# complete visual iteration unless the counts line up exactly.
ALIGNED = {}  # filled below


def load_jsonl(path):
    out = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
    return out


REQS = load_jsonl(os.path.join(TMP, "requests.jsonl"))


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def case_requests(case):
    rows = []
    for r in REQS:
        if r.get("request_type") != "render":
            continue
        f = (r.get("response_file") or "").replace("\\", "/")
        if "/outputs/%s/B03/%s/final.png" % (RUN, case) in f:
            rows.append(r)
    rows.sort(key=lambda r: r["started_at"])
    return rows


def drafts_for(case):
    hits = [os.path.join(DRAFTS, n) for n in os.listdir(DRAFTS)
            if n.endswith("-%s.snapshot" % case)]
    hits.sort(key=os.path.getmtime)
    return hits


GENERIC = ("第 %d 版渲染完成并打开查看。本件 case.md 的「迭代过程」按版本系列记录"
           "诊断与修改，而本次运行成功渲染了 %d 次（requests.jsonl 可逐条查），"
           "两者的对应关系无法从留下的证据里一一还原，因此这一行不把某一条诊断"
           "硬套到这一版上；该件的完整诊断—修改—复看序列见 case.md 与 "
           "snapshot-usage.md 第 6.1 节。")

rows = []
for case in ["case-%02d" % i for i in range(1, 11)]:
    reqs = case_requests(case)
    vis = [e for e in ITERS[case] if e[0] == "V"]
    dr = drafts_for(case)
    exact = len(vis) == len(reqs)
    ALIGNED[case] = exact
    vpos = 0
    prev = None
    for i, r in enumerate(reqs):
        vid = "B03-%s-r%02d" % (case, i + 1)
        is_last = (i == len(reqs) - 1)
        if exact:
            obs, chg = vis[i][1], vis[i][2]
            complete = i > 0
        elif is_last:
            obs, chg = vis[-1][1], vis[-1][2]
            complete = True
        elif i == 0:
            obs, chg = ("首版成功渲染，作为基线打开查看。本件后续的诊断—修改—复看"
                        "共 %d 个阶段，见 case.md「迭代过程」。" % len(vis)), "—"
            complete = False
        else:
            obs = GENERIC % (i + 1, len(reqs))
            chg = ("该版 DSL 见 dsl_file（若无独立副本则见 outputs 目录里的交付版 "
                   "final.snapshot）；早前运行的 draft 计数器每个进程从 v001 重新"
                   "开始，同名副本被后续进程覆盖，所以并非每一版的历史 DSL 都可恢复。")
            complete = False
        dsl = rel(dr[vpos]) if vpos < len(dr) else \
            "outputs/%s/B03/%s/final.snapshot" % (RUN, case)
        vpos += 1
        rows.append((vid, prev, "baseline" if i == 0 else "visual-iteration", dsl,
                     "outputs/%s/B03/%s/final.png" % (RUN, case),
                     r["ended_at"], obs, chg, complete))
        prev = vid

# failed renders that belong to a case's iteration story (no image produced)
FAILS = {
    "case-02": [0, 1, 2], "case-03": [0], "case-05": [0], "case-06": [0],
    "case-08": [0, 1], "case-09": [0], "case-10": [0, 1, 2],
}
for case, idxs in FAILS.items():
    vis = [e for e in ITERS[case] if e[0] == "V"]
    fails = [e for e in ITERS[case] if e[0] == "F"]
    for n, k in enumerate(idxs):
        obs, chg = fails[k][1], fails[k][2]
        vid = "B03-%s-syntax%02d" % (case, k + 1)
        rows.append((vid, "B03-%s-r%02d" % (case, min(len(vis), 9)),
                     "syntax-fix", None, None, None, obs, chg, False))
rows.sort(key=lambda t: (t[5] or ""))

now = datetime.now().astimezone().isoformat(timespec="milliseconds")

ARTIFACTS = [
    "outputs/%s/B03/portfolio.json" % RUN, "outputs/%s/B03/portfolio.md" % RUN,
    "outputs/%s/B03/gallery.html" % RUN, "outputs/%s/B03/technique-notes.md" % RUN,
    "outputs/%s/B03/snapshot-usage.md" % RUN, "outputs/%s/B03/task-metrics.json" % RUN,
] + ["outputs/%s/B03/%s/%s" % (RUN, c, a)
     for c in sorted(ALIGNED) for a in ("final.png", "final.snapshot", "case.md")]

EVIDENCE = ["tmp/%s/B03/%s" % (RUN, p) for p in (
    "crops/final-review-c01-moon.png", "crops/final-review2-c01-moon.png",
    "crops/final-review-c02-cardA.png", "crops/final-review-c02-cardB.png",
    "crops/final-review-c02-vert-rot2.png", "crops/final-review-c04-row05.png",
    "crops/final-review-c07-Krow.png", "crops/final-review-c10-depthlabels.png",
    "crops/final-review-c10-depthrows.png",
    "crops/final-review2-c02-ticketB.png", "crops/final-review2-c02-total.png",
    "crops/final-review2-c09-summary.png", "pre-final-review/")]

UNRESOLVED = [
    "服务侧 INTERNAL_ERROR: Snapshot rendering failed 出现 8 次（B03-req-050/051/063/"
    "082/086/087/089/157，HTTP 400，无更细信息）；同一份 DSL 重发即成功，判定为瞬时"
    "故障，原因未确认（标为推测），未因此改 DSL",
    "reference_enums 与实际接受集合不一致：PaintStrokeCap 无 BEVEL、decorationLineStyle "
    "无 DASHED、blendMode 无 ADD、clipBehavior 无 SAVE_LAYER（真名 "
    "ANTI_ALIAS_WITH_SAVE_LAYER）、BorderStyle 无 DASHED/DOTTED；textHeightMode 与 "
    "fontEdging 试遍所有可想到取值全部 400，判定本版本不可用",
    "softWrap=false 未生效；fontFeatures 的 tnum 无效（等宽数字做不到）",
    "Text height 与 strutLeading 会让整段文字空白（HTTP 200 但不绘制），行高只能手工排",
    "没有位图合成、没有交互与动画：服务只出静态 PNG",
    "精度近似（逐件写在 case.md 遗留里）：月面明暗是 Lambert 近似；海面剖面是三个正弦"
    "的示意叠加；陷印只是画面示意；MULTIPLY 是逐通道 sRGB 乘法；日照只有几何没有遮挡/"
    "反射/透光率；断面是横向断面",
    "token / 图像用量 / 费用一律 null：服务未暴露任何计费指标接口，聊天平台也未回报"
    "逐请求 token 或费用，未按字数或字节估算",
    "排队等待时间 null：264 次成功响应的 Server-Timing 均无 queue 段，无法测得",
    "iterations.jsonl 的粒度限制：每件成功渲染一行，但早前运行按版本系列记录诊断"
    "（且 draft 计数器每个进程从 v001 重启、部分历史 DSL 副本被同名覆盖），"
    "因此中间各版不做逐版诊断断言；只有每件的最后一版（交付版）计为完整视觉迭代，"
    "除 case-02/case-04/case-09 三件的成功渲染数与阶段数正好相等、可严格对齐",
]

NOTES_TXT = (
    "十件作品在一次被平台中断的运行里全部渲染完成；收尾阶段只做复审与文档："
    "逐张重新打开 10 张 final.png 做整体策展审查，改脚本重渲染了 3 张"
    "（case-01 月相、case-02 票面金额与身份、case-09 摘要计数），另排除 3 处疑似"
    "缺陷（case-02 竖排尺寸标注、case-04 本排座位放大条、case-10 的 ± 标高）。"
    "被替换的旧版 PNG/DSL 保留在 tmp/%s/B03/pre-final-review/。"
    "本文件（log_review.py）是第一次运行时按错误对齐方式生成的，已改名保留为 "
    "iterations.superseded-01.jsonl。" % RUN)

ITER_PATH = os.path.join(TMP, "iterations.jsonl")
if os.path.exists(ITER_PATH):
    shutil.move(ITER_PATH, os.path.join(TMP, "iterations.superseded-01.jsonl"))

m = wrapup.wrapup(
    task_id="B03", started="2026-10-05T05:14:56.342+08:00",
    first_image="2026-10-05T05:20:27.882+08:00", ended=now, iterations=rows,
    artifacts=ARTIFACTS, visual_evidence=EVIDENCE, unresolved=UNRESOLVED,
    notes=NOTES_TXT, status="completed",
    rounds=["round-01", "wrap-up-review"], cases=sorted(ALIGNED))

# finalize.py counts PNGs directly inside outputs/<run>/<task>; B-track works live
# in per-case sub-folders, so correct the two fields here rather than in the shared
# library (which other tasks' metrics already depend on).
mp = os.path.join(OUT, "task-metrics.json")
with open(mp, encoding="utf-8") as fh:
    mm = json.load(fh)
pngs = []
for case in sorted(ALIGNED):
    for f in sorted(os.listdir(os.path.join(OUT, case))):
        if f.lower().endswith(".png"):
            pngs.append("%s/%s" % (case, f))
mm["counts"]["final_pngs"] = len(pngs)
mm["counts"]["final_png_files"] = pngs
mm["counts"]["final_png_note"] = (
    "B 类交付的最终图放在每个 case 子目录下，finalize.build 的计数只扫 "
    "outputs/<run>/<task>/ 顶层所以先给了 0；这两个字段在 wrapup 之后按 case "
    "子目录重新统计。共享库未改动，以免影响其他题已写出的指标。")
mm["case_alignment"] = {
    c: {"successful_final_renders": len(case_requests(c)),
        "documented_visual_stages": len([e for e in ITERS[c] if e[0] == "V"]),
        "strict_1to1": ALIGNED[c]} for c in sorted(ALIGNED)}
with open(mp, "w", encoding="utf-8") as fh:
    json.dump(mm, fh, ensure_ascii=False, indent=2)

print(json.dumps(mm["counts"], ensure_ascii=False, indent=2))
print("iterations logged:", len(rows))
print("aligned strictly:", [c for c in sorted(ALIGNED) if ALIGNED[c]])
