"""A17 手册页生成器：4 页 1200×1600 + 4 个 400×240 独立示例。

流程：估算换行 → 批量探针校准（单画布）→ 必要时按实测重排 → 构建 DSL → 渲染。
核心示例子树（a17_examples.EX*_CORE）在手册页与独立示例中逐字节一致，
由 a17_verify.py 对实际落盘文件解析验证。
"""
from __future__ import annotations
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261013-174209")
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "_suite"))
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "A17"))
import render as R  # noqa: E402
from a17_examples import EXAMPLES, standalone_dsl  # noqa: E402

TMP = ROOT / "tmp" / RUN_ID / "A17"
OUT = ROOT / "outputs" / RUN_ID / "A17"
TMP.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

LOG = R.Log(ROOT, RUN_ID, "A17")


def render_retry(dsl_path: Path, out_path: Path, label: str, tries: int = 8, wait: float = 12.0):
    """渲染 + 超时重试（服务间歇故障；每次尝试均如实记录）。"""
    import time
    for i in range(tries):
        res = R.render(dsl_path, out_path, ROOT, LOG, label=label)
        if res["record"]["status"] == "ok":
            return res
        err = res["record"].get("error") or ""
        print(f"  retry {i + 1}/{tries} ({label}): {err[:60]}")
        time.sleep(wait)
    return res

W, H = 1200, 1600
M = 48                       # 安全边距
CW = W - 2 * M               # 内容宽 1104
MONO = "Noto Sans Mono CJK SC"
NOTO = "Noto Sans CJK SC"

C = {
    "bg": "#FFFFFF", "ink": "#0F172A", "body": "#1E293B", "muted": "#64748B",
    "faint": "#94A3B8", "accent": "#245CE4", "line": "#E2E8F0",
    "code_bg": "#0F172A", "code_tx": "#CBD5E1", "code_dim": "#7C8CA1",
    "frame_bd": "#CBD5E1", "chip_bg": "#0F172A",
}

# ---------------- 页面文案 ----------------
PAGES = [
    {
        "num": 1, "sec": "入门手册 · 调用契约", "title": "第一次调用：契约先行",
        "intro": "本页目标：不依赖任何转述，也能正确发出第一次请求。契约只有三件事：发什么、"
                 "收什么、出错时怎么读。右侧示例是一份最小可用文档。",
        "code_label": "印刷代码：example-01.snapshot 第 1–11 行（省略处已标识）",
        "sections": [
            ("请求", "POST /snapshot，请求体是 UTF-8 纯文本 DSL 而非 JSON，Content-Type 为 "
                     "text/plain。根标签 <Snapshot> 全文档仅一次，且必须有根 Widget 子节点。"),
            ("响应", "成功时响应体是图片二进制，格式由根标签 type 决定：png（默认）/ jpg / webp。"
                     "GET /fonts 返回 text/plain，每行一个字体族；"
                     "fontFamily 多字体用英文逗号分隔，逗号后不加空格。"),
            ("错误", "失败通常是 JSON：code / message / requestId，用 X-Request-Id 关联服务日志。"
                     "400 PARSE_ERROR 修 DSL 再提交；413 缩小请求体；429 与 503 按 Retry-After "
                     "重试。不要用 ?errorImage=png：它把错误改成图片，程序读不到。"),
            ("发出前检查单", "确认三件事：根标签只有一个、根 Widget 子节点存在、请求体是 UTF-8 纯文本。"
                            "拿到响应先判断是不是图片二进制，再按根标签 type 决定扩展名。"),
        ],
        "sources": ["open-snapshot.muedsa.com/ai-guide.md",
                    "snapshot.muedsa.com/guides/parser/"],
    },
    {
        "num": 2, "sec": "入门手册 · 布局", "title": "尺寸从布局来：Flex 与 Stack 对照",
        "intro": "画布尺寸不是配置项，而是布局算出来的结果。同一张 400×240 里："
                 "上半弹性分配，下半绝对定位。",
        "code_label": "印刷代码：example-02.snapshot 第 6–9、13–21 行（省略处已标识）",
        "sections": [
            ("根尺寸来自布局", "Container 的 width/height 会收紧 constraints；没有子节点也没有约束的"
                               "空 Container 在无界根约束下收缩为零。父节点传 BoxConstraints，"
                               "子节点在范围内选择尺寸；根出图仍需非零宽高。"),
            ("Flex：Row / Column / Expanded",
             "Row 与 Column 是 Flex 的特化，管 mainAxisAlignment、mainAxisSize、crossAxisAlignment；"
             "只有 STRETCH 才填满交叉轴。Expanded 以紧约束占满主轴剩余空间，Flexible 允许更小；"
             "三者必须是 Flex 直接子节点。主轴无限时先用 SizedBox 给出有限尺寸。"),
            ("Stack / Positioned",
             "Stack 先布局非 Positioned 子节点，再按 left/top/right/bottom/width/height 放置 "
             "Positioned 子节点，同一轴最多两项。默认 clipBehavior 为 HARD_EDGE，越界即裁剪；"
             "设 NONE 允许越界绘制。"),
        ],
        "sources": ["snapshot.muedsa.com/guides/layout/",
                    "snapshot.muedsa.com/reference/parser-tags/"],
    },
    {
        "num": 3, "sec": "入门手册 · 文本与颜色", "title": "Raw / CDATA / 富文本与尾部 alpha",
        "intro": "四个最容易踩的文本与颜色误解，用同一张 400×240 给出反例："
                 "CDATA 保原文、Raw 保空白、Span 可嵌套、alpha 在颜色串末两位。",
        "code_label": "印刷代码：example-03.snapshot 第 1–9、15–17 行（省略处已标识）",
        "sections": [
            ("误解一：实体可以在 DSL 里用",
             "解析器不做 HTML 实体解码；要原样输出 < > &，用 CDATA 包裹："
             "<Text><![CDATA[a < b & c > d]]></Text>。CDATA 未闭合时会把已读内容当文本输出，"
             "与注释的行为不同。"),
            ("误解二：Text 会保留空白",
             "Text 会 trim 首尾空白；要保留首尾空格和换行用 Raw。Raw 支持文本样式属性，"
             "但不支持 textAlign / softWrap 等段落属性，且只能出现在最外层 Text 创建的"
             "行内内容树里。"),
            ("误解三：富文本靠拼字符串",
             "Text 可嵌套 Text / Raw / Emoji / WidgetSpan 组成行内 Span 树，"
             "子 Span 继承父未覆盖的样式；WidgetSpan 必须恰有一个 Widget 子节点。"),
            ("误解四：alpha 在颜色串前面",
             "颜色支持 #RGB / #RGBA / #RRGGBB / #RRGGBBAA，8 位格式的透明度在最后两位："
             "#FF000080 是半透明红。多字体串不会逐项 trim，写成 Noto Sans CJK SC,Inter 时"
             "逗号后不能加空格。"),
        ],
        "sources": ["snapshot.muedsa.com/guides/parser/",
                    "snapshot.muedsa.com/guides/media-text/"],
    },
    {
        "num": 4, "sec": "入门手册 · 效果与交付", "title": "三种滤镜与可复现的自检",
        "intro": "滤镜改变绘制结果，不改变布局尺寸。本页对照三种滤镜，并给出可复现交付的自检纪律。",
        "code_label": "印刷代码：example-04.snapshot 第 4–6、8–11、15–19 行（省略处已标识）",
        "sections": [
            ("ImageFiltered：子树高斯模糊",
             "sigmaX/sigmaY 对子树结果做高斯模糊；Parser 版自动按 sigma 提供模糊输出边界，"
             "嵌进 ColorFiltered 时无需手配 outputBounds。"),
            ("ColorFiltered：子树颜色混合",
             "color 加 blendMode 对子树应用颜色混合，作用范围由子树绘制边界决定，"
             "合法溢出与阴影也包含在内。"),
            ("BackdropFilter：背景高斯模糊",
             "模糊的是背后已绘制的内容，用来做毛玻璃；背后没有内容时没有可见效果，"
             "通常配 ClipRect 或 ClipRRect 限定区域。"),
            ("自检与可复现交付",
             "四层验证由稳到脆：布局断言、像素采样、Golden 比对、人工 Artifact；采样点避开"
             "抗锯齿边缘。可复现：固定字体与 Surface、网络图转本地、不把时间或随机数写进图。"),
        ],
        "sources": ["snapshot.muedsa.com/guides/painting/",
                    "snapshot.muedsa.com/guides/testing/"],
    },
]

# ---------------- 换行（估算 + 探针校准） ----------------
# 实测（probe-glyph）：Noto Sans Mono CJK SC@20 → ASCII/空格 0.5em，CJK 与全角标点 1.0em；
# Noto Sans CJK SC@20 → CJK 与全角标点 1.0em，ASCII 字母数字约 0.58em。
WIDE_PUNCT = set("—–‘’“”…、。，；：？！（）《》【】〈〉「」")
for _cp in range(0x2010, 0x2030):        # 通用标点（破折号、引号、省略号）
    WIDE_PUNCT.add(chr(_cp))
for _cp in range(0x3000, 0x303F):        # CJK 符号与标点
    WIDE_PUNCT.add(chr(_cp))
for _cp in range(0xFF01, 0xFF66):        # 全角 ASCII 与半角片假名
    WIDE_PUNCT.add(chr(_cp))


def est_w(s: str, size: float, mono: bool) -> float:
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o >= 0x2E80 or ch in WIDE_PUNCT:
            w += size * 1.0
        elif ch == " ":
            w += size * 0.5
        elif ch.isascii() and ch.isalnum():
            w += size * (0.5 if mono else 0.58)
        else:
            w += size * (0.5 if mono else 0.45)
    return w


def wrap(text: str, size: float, max_w: float, mono: bool = False, scale: float = 1.0) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9_/.@:\-]+|\s+|.", text, flags=re.S)
    lines, cur, cur_w = [], [], 0.0
    for t in tokens:
        if t.isspace():
            if cur:
                cur.append(" ")
                cur_w += est_w(" ", size, mono) * scale
            continue
        tw = est_w(t, size, mono) * scale
        if cur and cur_w + tw > max_w:
            lines.append("".join(cur).rstrip())
            cur, cur_w = [], 0.0
        cur.append(t)
        cur_w += tw
    if cur:
        lines.append("".join(cur).rstrip())
    return lines


# ---------------- 探针 ----------------
def probe_lines(items: list[dict], tag: str) -> dict:
    """items: [{key,text,size,family,style}]；按画布上限分块批量测墨迹宽。返回 {key: ink_w}"""
    BAND, PADX, PADT = 40, 10, 10
    PER = 60                     # 60*40+20 = 2420 < 4096
    out = {}
    for ci in range(0, len(items), PER):
        chunk = items[ci:ci + PER]
        n = len(chunk)
        Wp, Hp = 1400, PADT + n * BAND + 10
        parts = [f'<Snapshot type="png" background="transparent">'
                 f'<Container width="{Wp}" height="{Hp}">'
                 f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">']
        for i, it in enumerate(chunk):
            y = PADT + i * BAND
            parts.append(
                f'<Positioned left="{PADX}" top="{y}" width="1300" height="{BAND}">'
                f'<Container color="transparent" alignment="TOP_LEFT">'
                f'<Text fontSize="{it["size"]}" fontFamily="{it["family"]}" fontStyle="{it["style"]}" '
                f'textAlign="LEFT" softWrap="false" maxLines="1">{cdata(it["text"])}</Text>'
                f'</Container></Positioned>')
        parts.append("</Stack></Container></Snapshot>")
        f = TMP / f"probe-{tag}-{ci // PER}.snapshot"
        f.write_text("".join(parts), encoding="utf-8")
        res = render_retry(f, TMP / f"probe-{tag}-{ci // PER}.png",
                           f"A17-probe-{tag}#{ci // PER}({n})", tries=6, wait=10.0)
        if res["record"]["status"] != "ok":
            print("PROBE FAILED:", res["record"].get("error"))
            sys.exit(1)
        from PIL import Image  # noqa: E402
        im = Image.open(TMP / f"probe-{tag}-{ci // PER}.png").convert("RGBA")
        px = im.load()
        iw, ih = im.size
        for i, it in enumerate(chunk):
            y0, y1 = PADT + i * BAND, PADT + (i + 1) * BAND
            xs = [x for y in range(y0, min(y1, ih)) for x in range(iw) if px[x, y][3] > 0]
            out[it["key"]] = (max(xs) - min(xs) + 1) if xs else 0
    return out


def cdata(s: str) -> str:
    if "]]>" not in s:
        return f"<![CDATA[{s}]]>"
    parts = s.split("]]>")
    return "<![CDATA[" + "]]]]><![CDATA[>".join(parts) + "]]>"


# ---------------- DSL 构件 ----------------
def rect(x, y, w, h, color, r=None, border=None):
    if border:
        return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
                f'<Container color="{color}" border="1 SOLID {border}" borderRadius="{r}"/></Positioned>')
    rb = f' borderRadius="{r}"' if r else ""
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Container color="{color}"{rb}/></Positioned>')


def t_node(s, x, y, w, size, family, style, color, align="LEFT", h=None):
    hh = f' height="{h:.2f}"' if h else ""
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}"{hh}>'
            f'<Container color="transparent" alignment="TOP_LEFT">'
            f'<Text fontSize="{size}" fontFamily="{family}" fontStyle="{style}" color="{color}" '
            f'textAlign="{align}" softWrap="false" maxLines="1">{cdata(s)}</Text>'
            f'</Container></Positioned>')


def raw_node(s, x, y, w, size, family, color):
    """代码行显示：Raw 只能作为 Text 的行内子节点（服务约束），用于保留缩进空白。"""
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{size + 8:.2f}">'
            f'<Container color="transparent" alignment="TOP_LEFT">'
            f'<Text fontSize="{size}" fontFamily="{family}" color="{color}" '
            f'softWrap="false" maxLines="1">'
            f'<Raw fontSize="{size}" fontFamily="{family}" color="{color}">{cdata(s)}</Raw>'
            f'</Text></Container></Positioned>')


def centered_text(s, cx, y, w, size, family, style, color, h):
    return (f'<Positioned left="{cx - w / 2:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Container color="transparent" alignment="CENTER">'
            f'<Text fontSize="{size}" fontFamily="{family}" fontStyle="{style}" color="{color}" '
            f'textAlign="CENTER" softWrap="false" maxLines="1">{cdata(s)}</Text>'
            f'</Container></Positioned>')


# ---------------- 主流程 ----------------
def main():
    log = R.Log(ROOT, RUN_ID, "A17")

    # ---------- 1. 独立示例 DSL 落盘（tmp，随后复制到 outputs） ----------
    for ex in EXAMPLES:
        (TMP / f"{ex['id']}.snapshot").write_text(standalone_dsl(ex), encoding="utf-8")

    # ---------- 2. 换行（估算） ----------
    page_lines = {}   # page_num -> list of (kind, text, size, family, style, color)
    for pg in PAGES:
        items = []
        for para in [pg["intro"]] + [p for _, p in pg["sections"]]:
            for ln in wrap(para, 24, CW):
                items.append(("body", ln, 24, NOTO, "NORMAL", C["body"]))
        for h, _ in pg["sections"]:
            items.append(("head", h, 26, NOTO, "BOLD", C["ink"]))
        items.append(("title", pg["title"], 38, NOTO, "BOLD", C["ink"]))
        items.append(("sec", pg["sec"], 24, NOTO, "BOLD", C["accent"]))
        items.append(("codelabel", pg["code_label"], 20, NOTO, "BOLD", C["accent"]))
        # 印刷代码行 + 省略行
        ex = EXAMPLES[pg["num"] - 1]
        dsl_lines = standalone_dsl(ex).splitlines()
        for kind, val in ex["print_spec"]:
            if kind == "code":
                items.append(("code", dsl_lines[val - 1], 20, MONO, "NORMAL", C["code_tx"]))
            else:
                items.append(("omit", f"…………{val}…………", 20, MONO, "NORMAL", C["code_dim"]))
        items.append(("caption", ex["caption"], 20, NOTO, "NORMAL", C["muted"]))
        items.append(("foot", f"Snapshot DSL 入门手册 · 第 {pg['num']} / 4 页 · run-{RUN_ID}",
                      18, NOTO, "NORMAL", C["faint"]))
        items.append(("foot", "来源：" + " ；".join(pg["sources"]),
                      18, NOTO, "NORMAL", C["faint"]))
        page_lines[pg["num"]] = items

    # ---------- 3. 探针校准 ----------
    scales = {}   # (family,size,style) -> scale
    all_items = []
    for pg in PAGES:
        for idx, (kind, txt, size, fam, st, col) in enumerate(page_lines[pg["num"]]):
            all_items.append({"key": f"p{pg['num']}-{idx}", "text": txt, "size": size,
                              "family": fam, "style": st})
    measured = probe_lines(all_items, "all")

    # 每个 (family,size) 的最大实测/估算比 → 缩放因子
    from collections import defaultdict
    ratios = defaultdict(list)
    for pg in PAGES:
        for idx, (kind, txt, size, fam, st, col) in enumerate(page_lines[pg["num"]]):
            key = f"p{pg['num']}-{idx}"
            est = est_w(txt, size, fam == MONO)
            if est > 0 and measured[key] > 0:
                ratios[(fam, size)].append(measured[key] / est)
    for k, v in ratios.items():
        scales[k] = max(v) * 1.04
    print("scales:", {f"{k[0]}@{k[1]}": round(v, 3) for k, v in scales.items()})

    # 用校准因子重排正文（代码行不重排，只验证可容纳）
    for pg in PAGES:
        sc = scales.get((NOTO, 24), 1.0)
        items = []
        for para in [pg["intro"]] + [p for _, p in pg["sections"]]:
            for ln in wrap(para, 24, CW, scale=sc):
                items.append(("body", ln, 24, NOTO, "NORMAL", C["body"]))
        for h, _ in pg["sections"]:
            items.append(("head", h, 26, NOTO, "BOLD", C["ink"]))
        items.append(("title", pg["title"], 38, NOTO, "BOLD", C["ink"]))
        items.append(("sec", pg["sec"], 24, NOTO, "BOLD", C["accent"]))
        items.append(("codelabel", pg["code_label"], 20, NOTO, "BOLD", C["accent"]))
        ex = EXAMPLES[pg["num"] - 1]
        dsl_lines = standalone_dsl(ex).splitlines()
        for kind, val in ex["print_spec"]:
            if kind == "code":
                items.append(("code", dsl_lines[val - 1], 20, MONO, "NORMAL", C["code_tx"]))
            else:
                items.append(("omit", f"…………{val}…………", 20, MONO, "NORMAL", C["code_dim"]))
        items.append(("caption", ex["caption"], 20, NOTO, "NORMAL", C["muted"]))
        items.append(("foot", f"Snapshot DSL 入门手册 · 第 {pg['num']} / 4 页 · run-{RUN_ID}",
                      18, NOTO, "NORMAL", C["faint"]))
        items.append(("foot", "来源：" + " ；".join(pg["sources"]),
                      18, NOTO, "NORMAL", C["faint"]))
        page_lines[pg["num"]] = items

    # 二次探针：确认重排后每行实测宽度可容纳
    all_items2 = []
    for pg in PAGES:
        for idx, (kind, txt, size, fam, st, col) in enumerate(page_lines[pg["num"]]):
            all_items2.append({"key": f"p{pg['num']}-{idx}", "text": txt, "size": size,
                               "family": fam, "style": st})
    measured2 = probe_lines(all_items2, "all2")
    over = []
    for pg in PAGES:
        for idx, (kind, txt, size, fam, st, col) in enumerate(page_lines[pg["num"]]):
            key = f"p{pg['num']}-{idx}"
            mw = measured2[key]
            if kind == "code":
                # 探针用 Text 会 trim 缩进；实际显示用 Raw 保留。等宽空格实测 0.5em。
                indent = len(txt) - len(txt.lstrip(" "))
                mw += indent * 0.5 * size
                limit = CW - 40
            else:
                limit = CW - 4
            if mw > limit:
                over.append((pg["num"], kind, txt[:34], round(mw, 1), limit))
    if over:
        print("!! OVERWIDE LINES:")
        for o in over:
            print("   ", o)
    else:
        print("all lines fit (2nd probe)")

    # ---------- 4. 构建页面 DSL ----------
    # 版面度量（画布 1200×1600，安全边距 48）
    HDR = 124                              # 页眉总高
    INTRO_PITCH, INTRO_GAP = 32, 10        # 导读
    LBL_H = 28                             # 小节标签行高
    ILLUS_H, ILLUS_GAP = 304, 16           # 教学插图（400×240 + 32 留白）
    CODE_PITCH, CODE_PAD, CODE_GAP = 26, 24, 16
    HEAD_H, HEAD_GAP = 34, 38              # 详情小节标题
    BODY_PITCH, SEC_GAP = 32, 10           # 详情小节正文
    FOOT_H = 68                            # 分隔线 + 两行页脚

    layout_record = {}
    for pg in PAGES:
        sc = scales.get((NOTO, 24), 1.0)
        ex = EXAMPLES[pg["num"] - 1]
        dsl_lines = standalone_dsl(ex).splitlines()
        printed = []
        for kind, val in ex["print_spec"]:
            if kind == "code":
                printed.append(("code", dsl_lines[val - 1]))
            else:
                printed.append(("omit", f"…………{val}…………"))

        nodes = [rect(0, 0, W, H, C["bg"])]
        y = M
        # ---- 页眉 ----
        nodes.append(rect(M, y, 132, 40, C["chip_bg"], r=8))
        nodes.append(centered_text(f"0{pg['num']} / 04", M + 66, y, 132, 20, "Inter Semi Bold",
                                   "NORMAL", "#FFFFFF", 40))
        nodes.append(t_node(pg["sec"], M + 152, y + 6, CW - 152, 24, NOTO, "BOLD", C["accent"]))
        nodes.append(t_node(pg["title"], M, y + 50, CW, 38, NOTO, "BOLD", C["ink"], h=48))
        nodes.append(rect(M, y + 112, CW, 1, C["line"]))
        y += HDR

        # ---- 导读 ----
        intro_lines = wrap(pg["intro"], 24, CW, scale=sc)
        for ln in intro_lines:
            nodes.append(t_node(ln, M, y, CW, 24, NOTO, "NORMAL", C["body"], h=32))
            y += INTRO_PITCH
        y += INTRO_GAP

        # ---- 教学插图：外框 + core（与独立示例同一子树，1:1 400×240） ----
        nodes.append(t_node("教学插图（由本页 DSL 直接渲染，非嵌入图片）", M, y, CW, 20,
                            NOTO, "BOLD", C["accent"], h=LBL_H))
        y += LBL_H
        core = ex["core"]
        nodes.append(
            f'<Positioned left="{M}" top="{y}" width="464" height="{ILLUS_H}">'
            f'<Container color="#FFFFFF" border="1 SOLID {C["frame_bd"]}" borderRadius="10" '
            f'padding="32">'
            f"<!-- CORE-BEGIN -->{core}<!-- CORE-END -->"
            f"</Container></Positioned>")
        cap_x = M + 464 + 32
        cap_w = W - M - cap_x
        cap_lines = wrap(ex["caption"], 20, cap_w)
        cap_y = y + (ILLUS_H - (len(cap_lines) * 28 + 28)) / 2
        nodes.append(t_node("渲染结果", cap_x, cap_y, cap_w, 20, NOTO, "BOLD", C["ink"], h=LBL_H))
        cap_y += 30
        for ln in cap_lines:
            nodes.append(t_node(ln, cap_x, cap_y, cap_w, 20, NOTO, "NORMAL", C["muted"], h=28))
            cap_y += 28
        y += ILLUS_H + ILLUS_GAP

        # ---- 印刷代码块 ----
        nodes.append(t_node(pg["code_label"], M, y, CW, 20, NOTO, "BOLD", C["accent"], h=LBL_H))
        y += LBL_H
        blk_h = len(printed) * CODE_PITCH + CODE_PAD
        nodes.append(rect(M, y, CW, blk_h, C["code_bg"], r=10, border="#1E293B"))
        cy = y + CODE_PAD // 2
        for kind, txt in printed:
            col = C["code_tx"] if kind == "code" else C["code_dim"]
            nodes.append(raw_node(txt, M + 20, cy, CW - 40, 20, MONO, col))
            cy += CODE_PITCH
        y += blk_h + CODE_GAP

        # ---- 详情小节 ----
        n_body = 0
        for head, body in pg["sections"]:
            nodes.append(t_node(head, M, y, CW, 26, NOTO, "BOLD", C["ink"], h=HEAD_H))
            y += HEAD_GAP
            for ln in wrap(body, 24, CW, scale=sc):
                nodes.append(t_node(ln, M, y, CW, 24, NOTO, "NORMAL", C["body"], h=32))
                y += BODY_PITCH
                n_body += 1
            y += SEC_GAP

        # ---- 页脚（两行短文本，避免右侧长来源行超宽） ----
        nodes.append(rect(M, y, CW, 1, C["line"]))
        nodes.append(t_node(f"Snapshot DSL 入门手册 · 第 {pg['num']} / 4 页 · run-{RUN_ID}",
                            M, y + 12, CW, 18, NOTO, "NORMAL", C["faint"], h=24))
        nodes.append(t_node("来源：" + " ；".join(pg["sources"]),
                            M, y + 40, CW, 18, NOTO, "NORMAL", C["faint"], h=24))
        y += FOOT_H

        layout_record[pg["num"]] = {
            "end_y": y, "bottom_margin": H - y,
            "intro_lines": len(intro_lines), "body_lines": n_body,
            "code_rows": len(printed),
        }
        dsl = (f'<Snapshot type="png" background="{C["bg"]}">'
               f'<Container width="{W}" height="{H}">'
               f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
               + "".join(nodes) + "</Stack></Container></Snapshot>")
        (TMP / f"handbook-0{pg['num']}.snapshot").write_text(dsl, encoding="utf-8")
        r = layout_record[pg["num"]]
        print(f"page {pg['num']}: end_y={y} bottom={H - y} intro={r['intro_lines']} "
              f"body={n_body} code_rows={len(printed)}")

    print(json.dumps(layout_record, indent=1))

    # ---------- 5. 渲染 ----------
    for ex in EXAMPLES:
        f = TMP / f"{ex['id']}.snapshot"
        png = TMP / f"{ex['id']}.png"
        if png.exists() and png.stat().st_mtime >= f.stat().st_mtime:
            print(ex["id"], "skip (png newer than dsl)")
            continue
        res = render_retry(f, png, f"A17-{ex['id']}")
        print(ex["id"], res["record"]["status"], res["record"].get("error") or "")
    for pg in PAGES:
        f = TMP / f"handbook-0{pg['num']}.snapshot"
        res = render_retry(f, TMP / f"handbook-0{pg['num']}.png", f"A17-handbook-0{pg['num']}")
        print(f"handbook-0{pg['num']}", res["record"]["status"], res["record"].get("error") or "")

    # 行数据留档（供 verify 用）
    with open(TMP / "a17_lines.json", "w", encoding="utf-8") as fh:
        json.dump({str(k): v for k, v in page_lines.items()}, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
