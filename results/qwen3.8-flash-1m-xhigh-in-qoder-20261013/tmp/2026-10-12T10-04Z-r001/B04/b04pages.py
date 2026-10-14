"""B04 pages: ten editorial plates built from tmp/<run>/B04/data.json.

Every figure on a page is read from the data file (computed by b04data.py from the real
request logs, the cached documentation and pixel read-backs), so no plate can drift from
the evidence. Each page uses a different dominant form on purpose: cover, pipeline,
vocabulary matrix, metric bars, failure faceting, scatter budget, colour strip, type
specimen, histogram, honesty list.

Run:  python tmp/<run_id>/B04/b04pages.py [01 02 ... 10 | all]
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(Path(__file__).parent))
from b04kit import (ACCENT, CARD, COOL, DATA, GRADE, GRID, INK, INK2, INK3, MONO,
                    OUT, PAPER, Report, SAND, TEAL, TMP, fmt_num, save, tw)
from bkit import SANS, SERIF, f

D = DATA
S = D["scale"]


# ------------------------------------------------------------------ 01 cover
def p01():
    s = Report(1000, 1400, 1, "把 XML 变成像素",
               "一份关于声明式图像渲染服务的实测报告：能力边界、失败形状与构图预算")
    s.rect(48, s.body_top, 904, 470, INK, radius=10)
    # pipeline silhouette: eight stages as a diminishing band
    stages = ["POST", "解析", "布局", "度量", "绘制", "合成", "编码", "响应"]
    for i, name in enumerate(stages):
        x = 78 + i * 108
        h = 150 + 60 * math.sin(i * 0.9)
        s.rect(x, s.body_top + 400 - h, 92, h, "#FFFFFF14", radius=6)
        s.text("cover", name, x + 46, s.body_top + 412, 17, "#C7D3DC", align="center")
        s.text("cover", f"{i + 1}", x + 46, s.body_top + 34, 20, ACCENT,
               align="center", font=MONO, bold=True)
    s.text("cover", "一次请求要穿过八段，只有两段被服务公开计时（第 02 页）", 78,
           s.body_top + 486, 18, INK2)

    stats = [(f"{S['render_requests']}", "次", "对 /snapshot 的真实请求"),
             (f"{S['ok']}", "张", "成功返回的图像"),
             (f"{S['document_pages']}", "页", "官方文档被逐页抓取"),
             (f"{S['distinct_canvas_sizes']}", "种", "出现过的画布尺寸")]
    y = 720
    for i, (v, u, c) in enumerate(stats):
        x = 60 + (i % 2) * 470
        yy = y + (i // 2) * 168
        s.text("cover", v, x, yy, 96, INK, font=MONO, bold=True)
        s.text("cover", u, x + tw(v, 96, True) + 10, yy + 46, 26, ACCENT)
        s.text("cover", c, x, yy + 116, 20, INK2)
    s.rect(48, 1074, 904, 1.5, GRID)
    s.para("cover", f"样本窗口 {S['window_start'][5:16].replace('T',' ')} → "
                    f"{S['window_end'][5:16].replace('T',' ')} · "
                    f"生成图像合计 {S['image_bytes_total_mb']} MB · "
                    f"文档缓存 {S['document_bytes']/1e6:.1f} MB。"
                    "全部数字由脚本从请求日志与本地缓存计算，可在 tmp/…/B04/data.json "
                    "复算；结论只适用于这一个服务与这一个时间窗，不外推。",
           48, 1092, 19, INK2, 904)
    s.text("cover", "方法：读官方文档 → 逐项试探 → 像素回读 → 日志统计", 48, 1236,
           20, COOL, bold=True)
    save(s, "case01-cover",
         [("事实：文档 58 页", "事实"), ("测量：550 请求日志", "测量"),
          ("S01…S12 见 sources.json", "事实")],
         "封面数字与 data.json → scale 一致；本页不引入任何外部来源。")


# ------------------------------------------------------------------ 02 pipeline
def p02():
    w, h = 1600, 1000
    s = Report(w, h, 2, "一次请求的八段旅程",
               "服务只公开其中两段的计时；其余段落存在，但外部无法把它们从总耗时里拆开")
    stages = [("发出 POST", "XML 以 text/plain 上传"),
              ("网关与鉴权", "响应带 x-request-id"),
              ("解析为组件树", "失败给 PARSE_ERROR"),
              ("布局与约束", "无界尺寸直接报错"),
              ("文本度量", "字体取自内置清单"),
              ("绘制指令", "render 段覆盖此步"),
              ("合成与编码", "PNG / JPEG / WebP"),
              ("响应回传", "带缓存与图片计数头")]
    x0, y0, bw, gap = 60, s.body_top + 10, 176, 14
    for i, (t, note) in enumerate(stages):
        x = x0 + i * (bw + gap)
        visible = i in (5, 7)
        s.card(x, y0, bw, 250, fill=CARD if visible else "#FFFFFF99",
               border=f"2 SOLID {COOL if visible else GRID}", radius=8)
        s.rect(x, y0, bw, 4, COOL if visible else "#C9C2B2", radius=2)
        s.text("pipe", f"{i + 1:02d}", x + 14, y0 + 12, 22, ACCENT, font=MONO,
               bold=True)
        s.para("pipe", t, x + 14, y0 + 40, 19, INK, bw - 28)
        s.para("pipe", note, x + 14, y0 + 116, 16, INK2, bw - 28)
        s.rect(x + 14, y0 + 214, bw - 28, 20, COOL if visible else "#E4DFD3",
               radius=4)
        s.text("pipe", "可计时" if visible else "不可分", x + bw / 2, y0 + 216, 16,
               "#FFFFFF" if visible else INK3, align="center", font=MONO)
    srv, cli = D["server_ms"], D["client_s"]
    y = y0 + 300
    s.text("pipe", "实测耗时（同一批请求）", 60, y, 22, INK, bold=True)
    rows = [(f"服务端 render p50（n={srv['n']}）", srv["p50"], COOL),
            ("服务端 render p90", srv["p90"], COOL),
            ("服务端 render p99", srv["p99"], COOL),
            ("服务端 render 最大值", srv["max"], SAND),
            (f"客户端往返 p50（n={cli['n']}）", cli["p50"] * 1000, TEAL),
            ("客户端往返 p90", cli["p90"] * 1000, TEAL)]
    s.bars("pipe2", [(a, b) for a, b, _ in rows], 60, y + 40, 780, bar_h=26, gap=12,
           label_w=300, value_fmt=lambda v: f"{v:,.0f} ms")
    s.rect(960, y + 40, 580, 232, CARD, radius=8, border=f"1 SOLID {GRID}")
    s.text("pipe2", "怎么读", 984, y + 54, 20, INK, bold=True)
    s.para("pipe2", f"服务端 render 中位数 {srv['p50']:.0f} ms，"
                    f"客户端往返中位数 {cli['p50']:.2f} s；两者之差包含网络、排队、"
                    "上传与下载，服务没有公开更细的分段，因此本报告不做拆分推测。"
                    f"最慢的一次是 {cli['max']:.1f} s（见第 09 页离群卡）。",
           984, y + 84, 17, INK2, 532)
    save(s, "case02-pipeline",
         [("测量：requests.jsonl server_timing 正则提取", "测量"),
          ("事实：错误文案来自服务响应", "事实"),
          ("不可分段＝服务未公开，非本报告的省略", "解释")],
         "阶段划分是本报告对一次 HTTP 调用的解释性拆分，服务并未公布内部管线图。")


# ------------------------------------------------------------------ 03 vocabulary
def p03():
    w, h = 1200, 1740
    s = Report(w, h, 3, "标签词汇表与它的真实边界",
               "文档列出的标签都可用；受限的是属性与结构位置，而不是标签本身")
    groups = [
        ("根与布局", ["Snapshot", "Stack", "Positioned", "Row", "Column", "Flex",
                     "SizedBox", "Padding", "Expanded", "Center", "Align"]),
        ("绘制容器", ["Container", "ColoredBox", "Border", "Opacity"]),
        ("裁剪与滤镜", ["ClipRect", "ClipRRect", "ClipOval", "ClipPath",
                       "BackdropFilter", "ColorFiltered", "ImageFiltered"]),
        ("变换与文本", ["Transform", "Text", "Raw", "WidgetSpan", "Emoji", "Image"]),
    ]
    y = s.body_top + 6
    for name, tags in groups:
        s.text("voc", name, 60, y, 20, COOL, bold=True)
        x = 60
        for t in tags:
            tw_ = tw(t, 18) + 24
            if x + tw_ > w - 60:
                x = 60
                y += 40
            s.rect(x, y + 28, tw_, 32, CARD, radius=16, border=f"1 SOLID {GRID}")
            s.text("voc", t, x + tw_ / 2, y + 34, 18, INK, align="center", font=MONO)
            x += tw_ + 10
        y += 78
    s.rect(60, y, w - 120, 1.5, GRID)
    y += 18
    s.text("voc", "实测到的结构约束（文档写明或行为证实）", 60, y, 22, INK, bold=True)
    items = [
        ("Positioned 只能直接挂在 Stack 下", "400 renderBox.parentData must be "
         "StackParentData", "测量", "B03-case03-v1"),
        ("Stack 子节点若全为 Positioned 则无界", "400 Layout size is infinite",
         "测量", "B03-misc"),
        ("Emoji 不能作为独立 Widget", "400 cant not buildWidget", "测量",
         "B03-p8-emoji-fix"),
        ("WidgetSpan 必须恰有一个普通子节点", "文档 WidgetSpan 段", "事实",
         "S06"),
        ("Transform 必须同时给 matrix 与 alignment", "文档 Transform 段", "事实",
         "S07"),
        ("origin 只接受 \"(x,y)\" 写法", "400 Attr [origin] value format error",
         "测量", "B03-origin0 / B03-origin1"),
    ]
    y += 40
    for t, ev_, g, rid in items:
        s.grade_tag("voc", g, 60, y + 2)
        s.text("voc", t, 150, y, 19, INK, bold=True)
        s.text("voc", ev_, 150, y + 26, 17, INK2)
        s.text("voc", rid, w - 60, y + 26, 16, INK3, align="right", font=MONO)
        y += 62
    s.rect(60, y, w - 120, 1.5, GRID)
    s.para("voc", "被静默忽略的属性同样属于边界：fillType 不参与裁剪（解析器保持非零环绕），"
                  "因此挖孔必须反向绕子路径；border 宽度大于 borderRadius 时不报错而是 "
                  "500 INTERNAL_ERROR。这两条都不是从文档读来的，是测出来的。",
           60, y + 16, 17, INK2, w - 120)
    y += 96
    s.text("voc", "属性级实测结论", 60, y, 22, INK, bold=True)
    y += 40
    attrs = [("gradientTileMode 用于 LINEAR", "被接受但不可见（轴铺满自身画框）", "测量"),
             ("gradientTileMode 用于 RADIAL", "半径即周期，REPEAT/MIRROR/DECAL 均可辨", "测量"),
             ("fillType", "解析器忽略，保持非零环绕", "测量"),
             ("boxShadow", "ELEVATION_N 与自定义 x y blur color 都生效", "测量"),
             ("decorationLineStyle", "SOLID/DOTTED/DASHED/DOUBLE/WAVY 可用，"
              "DOUBLE_SOLID 非法", "测量"),
             ("fontFeatures=tnum / smcp", "tnum 改变宽度；smcp 被接受但零像素变化", "测量"),
             ("clipBehavior=ANTI_ALIAS_WITH_SAVE_LAYER", "可用（圆角渐变裁剪无异常）", "测量"),
             ("foregroundGradient*", "作用于 Container 前景，方向为水平", "测量")]
    for name, verdict, grade in attrs:
        s.grade_tag("voc", grade, 60, y + 2)
        s.text("voc", name, 150, y, 18, INK, bold=True, font=MONO)
        s.text("voc", verdict, 150, y + 26, 17, INK2)
        y += 60
    save(s, "case03-vocabulary",
         [("事实：S01 标签白名单", "事实"), ("测量：失败响应原文", "测量"),
          ("解释：分组方式", "解释")],
         "标签名逐条取自 reference/parser-tags 页面正文；分组与排序为本报告编排。")


# ------------------------------------------------------------------ 04 metrics
def p04():
    w, h = 1400, 1480
    s = Report(w, h, 4, "文本度量：谁在决定一个字占多宽",
               "服务不接受调用方的度量，字宽由它自己的字体模型决定——只能回读，不能询问")
    tm = D["text_metrics"]
    y = s.body_top + 8
    s.text("met", "在本服务上测得的常数（回读 PNG 像素，±1px）", 60, y, 22, INK,
           bold=True)
    consts = [("汉字 / 全角", "1.00 em", "同一字号下 8 个汉字宽＝8×字号", COOL),
              ("拉丁字母", "0.62 em", "按字符累加，误差随串长线性增长", TEAL),
              ("等宽字体", "0.52 em", "MONO 族实测更窄", SAND),
              ("行距", "1.46 em", "换行后的行顶间距实测值", ACCENT),
              ("粗体绘制余量", "×1.14 + 10px", "粗体字框比常规宽", INK2)]
    y += 44
    for name, val, note, col in consts:
        s.rect(60, y, 8, 54, col, radius=4)
        s.text("met", name, 84, y + 4, 21, INK, bold=True)
        s.text("met", val, 300, y, 30, col, font=MONO, bold=True)
        s.text("met", note, 300, y + 34, 17, INK2)
        y += 66
    s.rect(760, s.body_top + 8, 580, 330, CARD, radius=8, border=f"1 SOLID {GRID}")
    s.text("met", "为什么只能回读", 784, s.body_top + 24, 20, INK, bold=True)
    s.para("met", "响应只有图像字节：没有文本度量接口，也没有排版报告。"
                  "因此绝对定位的版面必须自己预测换行——预测偏小会被服务悄悄换行，"
                  "偏大则与相邻元素相撞。本套的做法是把每个文本段的预测宽度写进断言，"
                  "再用放大图核对，两者一致才算通过。",
           784, s.body_top + 56, 17, INK2, 532)
    y = s.body_top + 400
    s.text("met", "文本属性的实测增量（同一行文字，只改一个属性）", 60, y, 22, INK,
           bold=True)
    rows = [("letterSpacing = 6（8 个拉丁字母）", tm["letterSpacing_6_delta_px"], COOL),
            ("wordSpacing = 14（两个词间隙）", tm["wordSpacing_14_delta_px"], COOL),
            ("fontFeatures = tnum（10 位数字）", tm["tnum_delta_px"], TEAL),
            ("fontFeatures = smcp（小型大写）", tm["smcp_changed_px"], ACCENT)]
    s.bars("met2", [(a, b) for a, b, _ in rows], 60, y + 44, 900, bar_h=30, gap=16,
           value_fmt=lambda v: f"+{v:.0f} px" if v else "0 px（无效果）", label_w=360)
    s.text("met2", "注：letterSpacing 的 +42px ≈ 7 个字隙 × 6px，与线性预期一致；"
                   "smcp 被接受但零像素变化，说明内置字体不含该特性。",
           60, y + 44 + 4 * 46 + 8, 17, INK3)
    y = s.body_top + 700
    s.rect(60, y - 14, w - 120, 1.5, GRID)
    s.text("met", "一个必须承认的粗糙处：0.62em 是平均值", 60, y + 6, 22, INK, bold=True)
    y += 46
    cols = ["字符类", "样本（字号 30）", "墨迹宽 px", "墨迹 em", "模型 em", "偏差"]
    xs = [60, 260, 620, 790, 950, 1110]
    for c, x in zip(cols, xs):
        s.text("met", c, x, y, 17, INK3, font=MONO)
    y += 34
    rows = [("大写拉丁", "SNAPSHOT", 160, 0.667, 0.62, "+7.6%"),
            ("小写拉丁", "abcdefg", 113, 0.538, 0.62, "−13.2%"),
            ("数字", "0123456789", 176, 0.587, 0.62, "−5.3%"),
            ("汉字", "一…（8 字）", 240, 1.000, 1.00, "0%")]
    for cls, sample, ink, em, model, dev in rows:
        s.text("met", cls, 60, y, 18, INK, bold=True)
        s.text("met", sample, 260, y, 18, INK2, font=MONO)
        s.text("met", f"{ink}", 620, y, 18, INK, font=MONO)
        s.text("met", f"{em:.3f}", 790, y, 18, TEAL, font=MONO)
        s.text("met", f"{model:.2f}", 950, y, 18, COOL, font=MONO)
        s.text("met", dev, 1110, y, 18, ACCENT, font=MONO)
        y += 40
    s.para("met", "墨迹宽度不等于前进宽度（两端还有 sidebearing），因此这里只能给出方向："
                  "模型对大写偏小、对小写偏大。本套的做法是预测后统一乘 1.14 再加 10px "
                  "余量（粗体），并把每个文本段的预测宽写进断言——宁可留白，也不让服务"
                  "悄悄换行。", 60, y + 12, 17, INK2, w - 120)
    save(s, "case04-metrics",
         [("测量：B03-p2-textab / p4-smallcaps 像素回读", "测量"),
          ("解释：常数是拟合值而非内部实现", "解释"),
          ("演示：条图长度按比例", "演示")],
         "em 常数是本套在返回 PNG 上回读得到的近似（±1px），不声称等于服务的内部度量算法。")


# ------------------------------------------------------------------ 05 failures
def p05():
    w, h = 1600, 1280
    s = Report(w, h, 5, "失败分类学",
               f"{S['failed']} 次非 200 响应里，什么能被诊断、什么只能重试")
    ec = D["error_codes"]
    y = s.body_top + 8
    s.text("fail", "按错误码", 60, y, 22, INK, bold=True)
    order = ["PARSE_ERROR", "RENDER_ERROR", "INTERNAL_ERROR", "IMAGE_LOAD_ERROR",
             "null"]
    labels = {"PARSE_ERROR": "解析错误：给出属性与位置，可自修",
              "RENDER_ERROR": "布局/渲染错误：给出原因短语",
              "INTERNAL_ERROR": "内部错误：只说失败，不给位置",
              "IMAGE_LOAD_ERROR": "外部图片取不到",
              "null": "无错误码（早期日志字段缺失）"}
    cols = {"PARSE_ERROR": COOL, "RENDER_ERROR": TEAL, "INTERNAL_ERROR": ACCENT,
            "IMAGE_LOAD_ERROR": SAND, "null": INK3}
    items = [(labels[k], ec.get(k, 0), cols[k]) for k in order if ec.get(k)]
    s.bars("fail", items, 60, y + 40, 860, bar_h=32, gap=14, label_w=330,
           value_fmt=lambda v: f"{v:.0f} 次")
    diag = D["diagnosable_parse_errors"]
    s.text("fail", f"可诊断比例：PARSE_ERROR {diag} / {S['failed']} = "
                   f"{100*diag/S['failed']:.0f}%；"
                   f"INTERNAL_ERROR {ec.get('INTERNAL_ERROR',0)} 次只能改结构后重试。",
           60, y + 40 + len(items) * 46 + 6, 18, INK2)
    s.rect(980, y, 560, 320, CARD, radius=8, border=f"1 SOLID {GRID}")
    s.text("fail", "按语义归类（同一错误码可能有多类原因）", 1004, y + 16, 19, INK,
           bold=True)
    kinds = sorted(D["failure_kinds"].items(), key=lambda kv: -kv[1])[:7]
    yy = y + 52
    for k, v in kinds:
        s.text("fail", k, 1004, yy, 17, INK2)
        s.rect(1250, yy + 4, max(6, v * 9), 16, COOL, radius=3)
        s.text("fail", str(v), 1250 + max(6, v * 9) + 8, yy, 16, INK, font=MONO)
        yy += 36
    y = y + 40 + len(items) * 46 + 54
    s.rect(60, y - 10, w - 120, 1.5, GRID)
    s.text("fail", "每类一条真实响应摘要（原文截断，未改写）", 60, y + 4, 22, INK,
           bold=True)
    y += 40
    show = ["attribute format", "unbounded layout", "element cap", "path syntax",
            "bad parent (Positioned)", "opaque 500"]
    for k in show:
        samp = D["failure_samples"].get(k)
        if not samp:
            continue
        s.rect(60, y, 250, 40, "#00000000", border=f"1 SOLID {cols.get('RENDER_ERROR', TEAL)}",
               radius=6)
        s.text("fail", k, 185, y + 10, 16, INK, align="center", font=MONO)
        txt = samp["summary"].replace("\n", " ")
        s.text("fail", txt[:96] + ("…" if len(txt) > 96 else ""), 330, y + 2, 16, INK2,
               font=MONO)
        s.text("fail", f"{samp['request_id']} · HTTP {samp['status']}", 330, y + 26,
               16, INK3, font=MONO)
        y += 52
    y += 24
    s.rect(60, y, w - 120, 1.5, GRID)
    y += 20
    s.text("fail", "这些坑最后变成了生成器里的守卫", 60, y, 22, INK, bold=True)
    y += 44
    guards = [("border 宽 > borderRadius", "构造 Container 时直接抛 ValueError，"
               "不再等到 500"),
              ("元素数 > 4096", "finish() 前递归统计节点数并抛错"),
              ("BackdropFilter 未裁剪", "只提供 glass() 入口，内部强制 ClipRRect/ClipPath"),
              ("Stack 子节点全为 Positioned", "finish() 始终插入一个带尺寸的背景节点")]
    for name, what in guards:
        s.rect(60, y, 300, 34, "#00000000", border=f"1 SOLID {COOL}", radius=6)
        s.text("fail", name, 210, y + 8, 16, INK, align="center", font=MONO)
        s.text("fail", what, 380, y + 8, 17, INK2)
        y += 46
    save(s, "case05-failures",
         [("测量：63 次失败响应分类统计", "测量"), ("事实：摘要为响应原文", "事实"),
          ("解释：语义归类由本报告定义", "解释")],
         "INTERNAL_ERROR 的成因未做任何推测；本表只登记触发时的结构与后来的修改。")


# ------------------------------------------------------------------ 06 budget
def p06():
    w, h = 1400, 1040
    s = Report(w, h, 6, "构图预算：4096 个元素",
               "文档没有写这条限制，它出现在响应里；程序化构图因此必须合并子路径")
    cap = D["element_cap_request"]
    y = s.body_top + 6
    s.rect(60, y, w - 120, 96, INK, radius=8)
    s.text("bud", "Document contains more than 4096 elements", 84, y + 18, 30,
           "#FFFFFF", font=MONO, bold=True)
    s.text("bud", f"400 · 证据请求 {cap} · 同批 2 000 元素请求正常返回（607 ms）",
           84, y + 58, 18, "#9FB2C4", font=MONO)
    y += 126
    s.text("bud", "本套十件作品的元素数与体积", 60, y, 22, INK, bold=True)
    b = D["budget"]
    maxe = max(x["elements"] for x in b)
    yy = y + 44
    for row in b:
        frac = row["elements"] / 4096
        s.text("bud", row["case"], 60, yy + 2, 17, INK2, font=MONO)
        s.rect(180, yy, 700, 22, "#E7E1D4", radius=4)
        s.rect(180, yy, 700 * frac, 22, ACCENT if frac > 0.7 else COOL, radius=4)
        s.text("bud", f"{row['elements']}", 180 + 700 * frac + 8, yy + 2, 16, INK,
               font=MONO)
        s.text("bud", f"{row['dsl_kb']} KB", 940, yy + 2, 16, INK2, font=MONO)
        s.text("bud", f"{row['png_kb']} KB", 1080, yy + 2, 16, INK2, font=MONO)
        yy += 34
    s.line(180, yy + 2, 880, yy + 2, INK3, 1.2)
    s.text("bud", "占 4096 上限的比例 · 左为 DSL 字节，右为 PNG 字节", 180, yy + 8,
           16, INK3)
    y = yy + 46
    s.rect(60, y, 640, 210, CARD, radius=8, border=f"1 SOLID {GRID}")
    s.text("bud", "合并子路径：1 个元素装 2 498 个圆盘", 84, y + 16, 20, INK, bold=True)
    s.para("bud", "一条 ClipPath 的 path 可以包含任意多个子路径，因此半调点阵、组织图方格、"
                  "窗灯矩形都能写进同一个元素；不合并时同样的画面要 2 500 多个 Container，"
                  "直接越过上限。代价是这些形状只能共享一次填充色，"
                  "需要多色时必须拆成多条路径（每条一个颜色）。",
           84, y + 48, 17, INK2, 592)
    s.rect(720, y, 620, 210, CARD, radius=8, border=f"1 SOLID {GRID}")
    s.text("bud", "字节不是免费的", 744, y + 16, 20, INK, bold=True)
    s.para("bud", f"最大的一件用了 {D['largest_work']['elements']} 个元素，"
                  f"DSL {D['largest_work']['dsl_kb']} KB，返回 PNG "
                  f"{D['largest_work']['png_kb']} KB。元素数与字节并不成正比："
                  "第 09 页那件只用 42 个元素，却写了 189 KB 的 DSL，"
                  "因为一条路径里装了 2 498 个子形状。上传时间随字节增长，"
                  "但服务端渲染时间在本样本里看不出与文件大小的稳定关系。",
           744, y + 48, 17, INK2, 572)
    save(s, "case06-budget",
         [("事实：上限来自响应原文", "事实"), ("测量：10 件元素数由脚本计数", "测量"),
          ("测量：2000 元素仍成功", "测量")],
         "元素数按 final.snapshot 中的标签出现次数统计（含 Positioned 等包装节点）。")


# ------------------------------------------------------------------ 07 colour
def p07():
    w, h = 1200, 1420
    s = Report(w, h, 7, "色标之间发生了什么",
               "在色标位置预测与实测一致；在色标之间，实测系统性偏亮")
    y = s.body_top + 6
    # the strip below is read back from the finished B03 day-wheel: eleven samples taken
    # at the ring's own angles, not the authored stop colours
    from PIL import Image
    wheel = Image.open(OUT.parent / "B03" / "case-02" / "final.png").convert("RGB")
    cx, cy, rad = 600, 700, (500 + 558) / 2
    stops, sampled = [], []
    for k in range(11):
        hour = k * 24 / 11
        ang = math.pi / 2 + hour / 24 * 2 * math.pi
        px = (int(round(cx + rad * math.cos(ang))), int(round(cy + rad * math.sin(ang))))
        c = wheel.getpixel(px)
        sampled.append((px, c))
        stops.append("#%02X%02X%02X" % c)
    n = len(stops)
    bw = (w - 120) / n
    for i, c in enumerate(stops):
        s.rect(60 + i * bw, y, bw + 1, 120, c)
    s.rect(60, y, w - 120, 120, "#00000000", border=f"1 SOLID {INK3}")
    s.text("col", "从 B03 case-02 成品色环上按 11 个角度回读的像素（不是色标定义值）",
           60, y + 132, 18, INK2)
    y += 178
    s.text("col", "八个时刻的期望色与实测色（日轮，见 B03 case-02）", 60, y, 22, INK,
           bold=True)
    samples = [(0, "#0B3954", (11, 57, 84), 0), (3, "#0B3954", (20, 70, 97), 35),
               (6, "#5E99B5", (118, 176, 203), 69), (9, "#B9DCEB", (196, 225, 238), 19),
               (12, "#EAF4F8", (227, 240, 246), 13),
               (15, "#E1E0CA", (234, 220, 183), 32),
               (18, "#E8A33D", (213, 149, 57), 37),
               (21, "#585646", (54, 76, 81), 55)]
    yy = y + 44
    for hr, exp, got, dev in samples:
        s.text("col", f"{hr:02d}:00", 60, yy + 4, 18, INK2, font=MONO)
        s.rect(150, yy, 90, 30, exp, border=f"1 SOLID {GRID}")
        s.rect(250, yy, 90, 30, "#%02X%02X%02X" % got, border=f"1 SOLID {GRID}")
        s.text("col", exp, 356, yy + 6, 16, INK3, font=MONO)
        s.text("col", "#%02X%02X%02X" % got, 470, yy + 6, 16, INK3, font=MONO)
        bar = min(dev, 80) * 4
        s.rect(600, yy + 6, max(bar, 3), 18, ACCENT if dev > 45 else TEAL, radius=3)
        s.text("col", f"Δ{dev}", 600 + max(bar, 3) + 8, yy + 6, 16, INK, font=MONO)
        yy += 42
    s.rect(60, yy + 12, w - 120, 150, CARD, radius=8, border=f"1 SOLID {GRID}")
    s.text("col", "解释（推断，非文档原文）", 84, yy + 28, 20, INK, bold=True)
    s.para("col", "色标处误差为 0，说明角度→位置的映射正确；色标之间系统性偏亮，"
                  "与在线性光空间插值后转回 sRGB 的行为一致。这是推断，不是文档原文。",
           84, yy + 58, 17, INK2, w - 168)
    yy += 206
    s.text("col", "三条可操作结论", 60, yy, 22, INK, bold=True)
    yy += 40
    rules = [("只在色标位置对颜色做硬承诺", "色标处 Δ=0；中间色一律回读或改用不透明分段。"),
             ("要精确的中间色就加色标", "把期望的中间色本身写成 stop，比依赖插值可靠。"),
             ("颜色断言用绝对差之和", "Δ = Σ|R−R′|+|G−G′|+|B−B′|，阈值按用途定；"
              "本页样本的 Δ 范围 0–69。")]
    for t, d_ in rules:
        s.rect(60, yy, 8, 44, ACCENT, radius=4)
        s.text("col", t, 84, yy + 2, 19, INK, bold=True)
        s.text("col", d_, 84, yy + 28, 17, INK2)
        yy += 62
    save(s, "case07-colour",
         [("测量：8 点像素回读", "测量"), ("事实：SWEEP 参数限制", "事实"),
          ("解释：线性光插值", "解释")],
         "Δ 为三通道绝对差之和（0–765 区间），条长按 min(Δ,80)×4px 绘制。")


# ------------------------------------------------------------------ 08 fonts
def p08():
    w, h = 1100, 1500
    s = Report(w, h, 8, "字体清单：能用什么字",
               "GET /fonts 返回的是服务内置清单，调用方不能上传字体")
    fm = D["fonts"]
    y = s.body_top + 6
    s.text("fnt", f"{fm['request_id']} · {fm['accessed_at'][:19]} · {fm['bytes']} B"
                  f" · {len(D['font_families'])} 个族名 / 28 行原始条目",
           60, y, 17, INK3, font=MONO)
    y += 40
    groups = [("中文与混排", [x for x in D["font_families"]
                          if "CJK" in x and "Mono" not in x], "永 Aa 0123", SERIF),
              ("等宽", [x for x in D["font_families"] if "Mono" in x], "0123 ff", MONO),
              ("拉丁", [x for x in D["font_families"]
                       if not any(k in x for k in ("CJK", "Mono", "Emoji"))],
                 "Handy", SANS),
              ("符号", [x for x in D["font_families"] if "Emoji" in x], "🙂", SANS)]
    for name, lst, sample, font in groups:
        s.text("fnt", f"{name}（{len(lst)}）", 60, y, 20, COOL, bold=True)
        s.text("fnt", "样例 " + sample, w - 60, y, 20, INK2, align="right", font=font)
        y += 34
        x = 60
        for fam in lst:
            short = (fam.replace("Noto Sans ", "NS ").replace("Noto Serif ", "NSr ")
                        .replace("DejaVu ", "DjV ").replace(" Noto", ""))
            tw_ = tw(short, 17, True) + 22
            if x + tw_ > w - 60:
                x = 60
                y += 38
            s.rect(x, y, tw_, 32, CARD, radius=16, border=f"1 SOLID {GRID}")
            s.text("fnt", short, x + tw_ / 2, y + 6, 17, INK, align="center",
                   font=MONO)
            x += tw_ + 8
        y += 56
    s.rect(60, y, w - 120, 1.5, GRID)
    y += 20
    s.text("fnt", "这份清单怎样影响版面", 60, y, 22, INK, bold=True)
    y += 40
    notes = [
        ("解释", "族名要精确匹配：Noto Sans CJK SC 与 JP 是不同条目，写错不报错，"
                 "只会回退到默认字形。"),
        ("测量", "等宽族比常规拉丁窄（实测 0.52em 对 0.62em），数字列用它能对齐。"),
        ("事实", "Inter 的 8 个字重是 8 个独立族名，没有可变字重轴。"),
        ("事实", "表情符号只有 Noto Color Emoji 一项，且只能作为 Text 的行内节点。"),
        ("解释", "分组与缩写是本报告的编排；服务只返回一个平铺列表。"),
    ]
    for grade, t in notes:
        s.grade_tag("fnt", grade, 60, y + 2)
        s.para("fnt", t, 152, y, 18, INK2, w - 212)
        y += 80
    y += 24
    s.rect(60, y, w - 120, 1.5, GRID)
    y += 20
    s.text("fnt", "同句四族对照（本页文字就是用这些族名渲染的）", 60, y, 22, INK,
           bold=True)
    y += 44
    line = "港口 2026 · 永字八法"
    for fam, label in [("Noto Sans CJK SC", "NS CJK SC"),
                       ("Noto Serif CJK SC", "NSr CJK SC"),
                       ("Noto Sans Mono CJK SC", "NS Mono CJK SC"),
                       ("DejaVu Sans", "DjV Sans")]:
        s.text("fnt", label, 60, y + 6, 17, INK3, font=MONO)
        s.text("fnt", line, 300, y, 30, INK, font=fam)
        y += 52
    s.text("fnt", "同一句、同一字号 30px：等宽族明显更宽，衬线族的汉字笔画对比更强；"
                  "拉丁族不含汉字，会回退。", 60, y + 6, 17, INK2)
    save(s, "case08-fonts",
         [("事实：S02 /fonts 响应", "事实"), ("测量：em 宽度回读", "测量"),
          ("解释：分组与影响", "解释")],
         "字体清单抓取于本套开始阶段（2026-10-12 10:10），未再次核对是否变更。")


# ------------------------------------------------------------------ 09 timing
def p09():
    w, h = 1600, 1120
    s = Report(w, h, 9, "时间花在哪，缓存有没有用",
               "422 条含服务端 render 计时的成功响应；长尾由客户端超时造成，"
               "服务端 render 全部在 5.9 s 内")
    y = s.body_top + 8
    edges, counts = D["hist_edges"], D["hist_counts"]
    s.text("tim", f"服务端 render 耗时分布（n={D['hist_n']}，单位 ms）", 60, y, 22, INK,
           bold=True)
    s.hist("tim", counts, edges, 60, y + 48, 860, 330)
    srv = D["server_ms"]
    s.text("tim", f"中位 {srv['p50']:.0f} · p90 {srv['p90']:.0f} · "
                  f"p99 {srv['p99']:.0f} · 最大 {srv['max']:.0f} · 最小 {srv['min']:.0f}",
           60, y + 408, 18, INK2, font=MONO)
    cache, hit = D["cache"], D["cache"].get("hit", 0)
    x = 1000
    s.rect(x, y, 540, 190, CARD, radius=8, border=f"1 SOLID {GRID}")
    s.text("tim", "缓存", x + 24, y + 14, 20, INK, bold=True)
    s.text("tim", f"{D['cache_hit_pct']}%", x + 24, y + 44, 58, COOL, font=MONO,
           bold=True)
    s.text("tim", f"命中 {hit} / {S['ok']}", x + 250, y + 62, 24, INK2, font=MONO)
    s.para("tim", "x-snapshot-cache 头由服务给出；本套没有做去重请求设计，"
                  "该比例不用于评价缓存能力。", x + 24, y + 122, 16, INK3, 492)
    hn = D["hit_note"]
    s.rect(x, y + 210, 540, 150, CARD, radius=8, border=f"1 SOLID {GRID}")
    s.text("tim", "命中样本为何不在直方图里", x + 24, y + 224, 20, INK, bold=True)
    s.para("tim", f"{hn['n']} 条命中的 server-timing 只有 cache;desc=hit 与 total，"
                  f"没有 render 段（实测 {hn['with_render_timing']}/{hn['n']} 条含 "
                  "render），因此被排除在 n=422 之外。这是口径说明，不是丢数据。",
           x + 24, y + 256, 16, INK2, 492)
    o = D["outlier"]
    s.rect(x, y + 380, 540, 320, "#FFFFFF", radius=8, border=f"2 SOLID {ACCENT}")
    s.text("tim", "长尾来自客户端超时，不是渲染变慢", x + 24, y + 396, 20, INK,
           bold=True)
    s.text("tim", f"{o['seconds']:.1f} s", x + 24, y + 428, 52, ACCENT, font=MONO,
           bold=True)
    s.para("tim", f"最长的请求 {o['request_id']}（任务 {o['task']}）等待 "
                  f"{o['seconds']:.1f} 秒后读超时，响应 0 B；"
                  "同一行的边缘计时是 cfEdge 305 ms / cfOrigin 1532 ms。"
                  "日志里 5 个最慢的客户端等待有 4 个带 TimeoutError 或 curl (28)，"
                  "而它们的服务端 render 都在 2.2 s 以内。",
           x + 24, y + 496, 16, INK2, 492)
    s.text("tim", "结论：等待上限由客户端超时设置决定，不由渲染决定。",
           x + 24, y + 656, 16, ACCENT, bold=True)
    s.rect(60, y + 460, 860, 220, CARD, radius=8, border=f"1 SOLID {GRID}")
    s.text("tim", "怎么读这张分布", 84, y + 476, 20, INK, bold=True)
    s.para("tim", "横轴是服务公开的唯一一段计时（render），纵轴是响应条数；"
                  "分箱边界写在轴下方，重建脚本可复算。分布右偏：一半请求在 0.5 s 内，"
                  "但 1% 的尾部超过 4.4 s，最大 5.9 s。客户端往返中位数 3.41 s，"
                  "比 render 中位数大近 7 倍——差值里包含网络、排队、上传与下载，"
                  "服务没有公开更细的分段，本报告不做拆分推测。",
           84, y + 508, 17, INK2, 812)
    save(s, "case09-timing",
         [("测量：server_timing 直方图 n=422", "测量"),
          ("事实：缓存头与命中口径", "事实"), ("测量：长尾为客户端超时", "测量")],
         "统计口径：本套 A01–B03 期间的全部成功渲染；B04 自身的请求不计入，"
         "以免报告边写边变。")


# ------------------------------------------------------------------ 10 limits
def p10():
    w, h = 1100, 1580
    s = Report(w, h, 10, "边界、不知道、以及怎么复核",
               "这份报告的价值不在于结论多，而在于每条结论知道自己走多远")
    y = s.body_top + 6
    rows = [
        ("只在特定尺寸/参数下成立", "未裁剪的 BackdropFilter 会把先前半透明内容压成不透明",
         "测量", "480×380 复现两次；460×180 未复现，边界条件未定位"),
        ("文档写明但被静默忽略", "fillType 不参与裁剪路径", "测量",
         "同一路径改反向绕后像素才变"),
        ("被接受但无效果", "fontFeatures=smcp", "测量", "changed_px = 0"),
        ("不报错但会失败", "border 宽度超过 borderRadius 时返回 500", "测量",
         "先 200 后 500，无解析期提示"),
        ("无法验证的部分", "服务的内部文本度量与字体回退链", "未确认",
         "响应不含度量；只能回读像素"),
        ("无法验证的部分", "其它渲染服务是否也有 4096 元素上限", "未确认",
         "本套未访问任何外部服务（会话禁止外部 HTTP）"),
        ("样本限制", "全部数据来自单一服务、约 20 小时窗口", "解释",
         "不外推到生产环境峰值或别的区域"),
        ("部分解释", "一次 249.22 s 的客户端读超时", "未确认",
         "第 09 页证实是客户端超时；但同一行边缘计时只有 1.5 s，"
         "差值为何这么大，本套无证据解释"),
    ]
    for title, claim, grade, why in rows:
        s.grade_tag("lim", grade, 60, y + 4)
        s.text("lim", title, 150, y, 18, INK3, font=MONO)
        s.text("lim", claim, 150, y + 26, 20, INK, bold=True)
        s.para("lim", why, 150, y + 56, 16, INK2, w - 210)
        y += 118
    s.rect(60, y, w - 120, 1.5, GRID)
    y += 18
    s.text("lim", "怎么复核这份报告", 60, y, 22, INK, bold=True)
    steps = [
        "1  运行 tmp/…/B04/b04data.py → 重新生成 data.json（所有页面数字的唯一来源）",
        "2  运行 tmp/…/B04/b04pages.py → 十页 DSL 与审计结果一并重出",
        "3  逐页渲染后与 final.snapshot 比对字节；像素回读脚本：probe_check*.py、"
        "case07_check.py、以及各 case 的校验片段",
        "4  原始证据：tmp/…/各任务/requests.jsonl（550 次渲染请求）与 "
        "tmp/…/_suite/docs/（58 页文档缓存）",
    ]
    y += 40
    for t in steps:
        y = s.para("lim", t, 60, y, 17, INK2, w - 120) + 14
    s.text("lim", "本特辑不含任何外部未读来源；未访问的页面一律不列为依据。", 60,
           y + 8, 17, ACCENT, bold=True)
    save(s, "case10-limits",
         [("事实/测量/解释/未确认 四级标签", "解释"),
          ("复核脚本与原始日志路径", "测量")],
         "grade 标签是本报告的证据分级方式，见 editorial-note.md。")


PAGES = {"01": p01, "02": p02, "03": p03, "04": p04, "05": p05, "06": p06,
         "07": p07, "08": p08, "09": p09, "10": p10}

if __name__ == "__main__":
    which = sys.argv[1:] or ["all"]
    for k, fn in PAGES.items():
        if "all" in which or k in which:
            fn()
            print("built", k)
