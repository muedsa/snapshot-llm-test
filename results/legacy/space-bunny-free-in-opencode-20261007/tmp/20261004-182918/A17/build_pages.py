"""A17 step 3: build and render the four 1200x1600 handbook pages.

One parameterised page builder produces all four pages: identical header rule,
title block, section rhythm, code-block styling, illustration frame and footer;
only the content of a page changes.  The printed code is sliced verbatim out of
example-0N.snapshot, and the illustration is redrawn from page DSL primitives
(no <Image> anywhere).
"""
from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A17"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
sys.path.insert(0, HERE)
import snapkit  # noqa: E402
import hb  # noqa: E402
import examples as X  # noqa: E402

snapkit.configure(TASK, OUT, TMP)
DRAFTS = os.path.join(TMP, "drafts")
os.makedirs(DRAFTS, exist_ok=True)

K = 1.35                      # illustration scale: 400x240 -> 540x324
ART_W, ART_H = 400 * K, 240 * K
PANEL_W = ART_W + 40
NOTES_X = hb.MARGIN + PANEL_W + 24
NOTES_W = hb.RIGHT - NOTES_X

CODE_SIZE, CODE_LH = 20, 27
PANEL_HEAD = 44
CAPTION_H = 30
CAPTION_SIZE = 17
MARK_W = 18
# exposed so verify.py can assert the type scale without duplicating it
hb.BUILD_CODE_SIZE = CODE_SIZE
hb.CAPTION_SIZE_AT_BUILD = CAPTION_SIZE


# --------------------------------------------------------------- art emitter
def art_parts(art, x, y, k=K):
    out = []
    for it in art:
        t = it["t"]
        bx, by, bw, bh = it["box"]
        X0, Y0, Wd, Ht = x + bx * k, y + by * k, bw * k, bh * k
        if t == "rect":
            r = it.get("radius")
            out.append(hb.rect(X0, Y0, Wd, Ht, fill=it.get("fill"),
                               radius=(r * k if r else None),
                               border=it.get("border")))
        elif t == "text":
            fs = round(it["size"] * k, 2)
            out.append(hb.ctext(it["s"], X0, Y0, fs, it["color"],
                                w=round(Wd + 10 * k, 2),
                                font=hb.MONO if it.get("font") == "mono" else hb.UI,
                                align=it.get("align"),
                                style="BOLD" if it.get("bold") else None))
        elif t == "blur_backdrop":
            sigma = round(it["sigma"] * k, 2)
            rad = round(it["radius"] * k, 2)
            out.append(
                '<Positioned left="%s" top="%s" width="%s" height="%s">\n'
                '  <ClipRRect borderRadius="%s" clipBehavior="ANTI_ALIAS">\n'
                '    <Container width="%s" height="%s">\n'
                '      <Stack fit="EXPAND">\n'
                '        <Positioned left="0" top="0" width="%s" height="%s">\n'
                '          <BackdropFilter sigmaX="%s" sigmaY="%s">\n'
                '            <Container width="%s" height="%s" color="%s" />\n'
                '          </BackdropFilter>\n'
                '        </Positioned>\n'
                '      </Stack>\n'
                '    </Container>\n'
                '  </ClipRRect>\n'
                '</Positioned>'
                % (round(X0, 2), round(Y0, 2), round(Wd, 2), round(Ht, 2), rad,
                   round(Wd, 2), round(Ht, 2), round(Wd, 2), round(Ht, 2),
                   sigma, sigma, round(Wd, 2), round(Ht, 2), it["tint"]))
        elif t == "blur_subtree":
            sigma = round(it["sigma"] * k, 2)
            rad = round(it["radius"] * k, 2)
            ix, iy, iw, ih = it["inset"]
            IX, IY = X0 + ix * k, Y0 + iy * k
            IW, IH = iw * k, ih * k
            out.append(
                '<Positioned left="%s" top="%s" width="%s" height="%s">\n'
                '  <ClipRRect borderRadius="%s" clipBehavior="ANTI_ALIAS">\n'
                '    <Container width="%s" height="%s">\n'
                '      <Stack fit="EXPAND">\n'
                '        <Positioned left="0" top="0" width="%s" height="%s">\n'
                '          <ImageFiltered sigmaX="%s" sigmaY="%s">\n'
                '            <Container width="%s" height="%s">\n'
                '              <Stack fit="EXPAND">\n'
                '                <Positioned left="0" top="0" width="%s" height="%s">\n'
                '                  <Container color="%s" />\n'
                '                </Positioned>\n'
                '                <Positioned left="%s" top="%s" width="%s" height="%s">\n'
                '                  <Text fontSize="%s" fontFamily="%s" color="%s">'
                '<![CDATA[%s]]></Text>\n'
                '                </Positioned>\n'
                '              </Stack>\n'
                '            </Container>\n'
                '          </ImageFiltered>\n'
                '        </Positioned>\n'
                '      </Stack>\n'
                '    </Container>\n'
                '  </ClipRRect>\n'
                '</Positioned>'
                % (round(X0, 2), round(Y0, 2), round(Wd, 2), round(Ht, 2), rad,
                   round(Wd, 2), round(Ht, 2), round(Wd, 2), round(Ht, 2),
                   sigma, sigma, round(Wd, 2), round(Ht, 2),
                   round(Wd, 2), round(Ht, 2), it["plate"],
                   round(IX - X0, 2), round(IY - Y0, 2), round(IW, 2), round(IH, 2),
                   round(it["size"] * k, 2),
                   hb.MONO if it.get("font") == "mono" else hb.UI,
                   it["color"], it["s"]))
        else:
            raise ValueError("unknown art item %r" % t)
    return out


def illustration_panel(page, art, caption, source_label):
    x, y = hb.MARGIN, page.y
    h = PANEL_HEAD + ART_H + CAPTION_H
    page.parts.append(hb.rect(x, y, PANEL_W, h, fill=hb.C["panel"], radius=16,
                              border="1 SOLID " + hb.C["rule_soft"]))
    page.parts.append(hb.ctext(source_label, x + 20, y + 13, 20, hb.C["ink"],
                               font=hb.MONO, style="BOLD", w=PANEL_W - 40))
    page.parts.append(hb.rect(x + 20, y + PANEL_HEAD - 10, ART_W, ART_H,
                              fill="#0B1220FF"))
    page.parts.extend(art_parts(art, x + 20, y + PANEL_HEAD - 10, K))
    hb.check_fit("caption@p%d" % page.index, caption, CAPTION_SIZE, ART_W)
    page.parts.append(hb.ctext(caption, x + 20, y + PANEL_HEAD - 10 + ART_H + 7,
                               CAPTION_SIZE, hb.C["muted"], w=ART_W))
    return h


def notes_box(page, title, items):
    """items = [(kind, text)] with kind in {'ok','bad','warn','plain','code'}.

    Line breaks inside an item are treated as *one* paragraph: continuation
    lines are indented under the item's marker so four red lines do not read as
    eight separate bullets.  Code items get their own tinted chip per line.
    """
    x, y = NOTES_X, page.y
    pad = 20
    inner = NOTES_W - pad * 2
    h = pad * 2 + 38
    laid = []          # (kind, text, is_first, lh)
    for kind, text in items:
        size = 17 if kind == "code" else T_NOTE
        indent = 16 if kind == "code" else MARK_W
        lines = hb.wrap(text, size, inner - indent, mono=(kind == "code"))
        lh = 23 if kind == "code" else T_NOTE_LH
        for i, ln in enumerate(lines):
            hb.check_fit("notes@p%d" % page.index, ln, size, inner - indent,
                         mono=(kind == "code"))
            laid.append((kind, ln, i == 0, lh))
            h += lh
        h += 14 if kind != "code" else 8
    h += pad - 26
    page.parts.append(hb.rect(x, y, NOTES_W, h, fill=hb.C["panel_alt"], radius=16,
                              border="1 SOLID " + hb.C["rule_soft"]))
    page.parts.append(hb.rect(x + pad, y + pad + 4, 3, 20, fill=page.accent, radius=2))
    page.parts.append(hb.ctext(title, x + pad + 12, y + pad, 22, hb.C["ink"],
                               style="BOLD", w=inner - 12))
    cy = y + pad + 40
    colours = {"ok": "#047857FF", "bad": "#B91C1CFF", "warn": "#B45309FF",
               "plain": hb.C["ink_2"], "code": "#334155FF"}
    for kind, ln, first, lh in laid:
        if kind == "code":
            page.parts.append(hb.rect(x + pad, cy - 4, inner, lh + 7,
                                      fill="#E3E9F0FF", radius=6))
            page.parts.append(hb.ctext(ln, x + pad + 9, cy, size, colours["code"],
                                       font=hb.MONO, w=inner - 18))
            cy += lh + 4
        else:
            if first:
                page.parts.append(hb.rect(x + pad + 2, cy + 8, 7, 7,
                                          fill=colours.get(kind, hb.C["ink_2"]),
                                          radius=2))
            page.parts.append(hb.ctext(ln, x + pad + MARK_W, cy, size,
                                       colours.get(kind, hb.C["ink_2"]),
                                       w=inner - MARK_W))
            cy += lh
    return h


T_NOTE, T_NOTE_LH = 20, 28


# ---------------------------------------------------------------- page content
PAGES = [
    dict(
        index=1, kicker="CHAPTER 01 · CONTRACT",
        title="调用契约：请求、响应与错误",
        standfirst="先约定接口，再谈画面：一次成功渲染和一次失败响应的真实报文，都在这里。",
        accent="#2563EBFF",
        bullets=[
            "POST /snapshot，请求体是 UTF-8 纯文本 DSL，不是 JSON；成功响应体是图片字节，"
            "Content-Type 为 image/png、image/jpeg 或 image/webp。",
            "所有响应都带 X-Request-Id；失败时返回 JSON，字段固定为 code、message、requestId，"
            "message 里带出错位置。",
            "curl 即使 --fail-with-body 也可能把 JSON 写进 result.png：先看 HTTP 状态和 "
            "Content-Type，再决定能不能用这张图。",
        ],
        ex=1, code_windows=None,
        code_title="example-01.snapshot",
        notes_title="本次真实响应（POST /snapshot）",
        notes=[
            ("code", "400 PARSE_ERROR"),
            ("code", "padding=\"24 32\" 不是 EdgeInsets"),
            ("code", "413 REQUEST_TOO_LARGE"),
            ("code", "400 EMPTY_REQUEST 空请求体"),
            ("code", "429 带 Retry-After，503 分 QUEUE_*"),
            ("plain", "以上 code 与字段名取自 /openapi.yaml 的 ApiError 枚举，"
                      "报文形态取自本次实际响应文件。"),
        ],
        caption="教学插图：由本页 DSL 构件重绘 example-01.png 的同一批组件",
    ),
    dict(
        index=2, kicker="CHAPTER 02 · LAYOUT",
        title="根尺寸来自布局，不是根标签属性",
        standfirst="布局协议与 Flutter 相同：父节点给约束，子节点选尺寸，画布由布局算出。",
        accent="#0891B2FF",
        bullets=[
            "根节点 <Snapshot> 只认 type / background / debug；给 width、height 完全无效，"
            "尺寸必须由最外层 Container 产生。",
            "Row / Column 是 Flex 的特化，Expanded 等价于 Flexible(fit=TIGHT)；"
            "主轴必须先有界，否则剩余空间无法计算。",
            "Positioned 只能是 Stack 或 IndexedStack 的直接子节点，同一轴最多给三项中的两项。",
        ],
        ex=2, code_windows=None,
        code_title="example-02.snapshot",
        notes_title="本页三个已实测的响应",
        notes=[
            ("bad", "colour=\"#38BDF8\" 拼错 → HTTP 200，照常出图 200×80，属性被忽略。"),
            ("bad", "根下两个 Container → PARSE_ERROR: Tag Snapshot only can have one child。"),
            ("bad", "根节点无界 → RENDER_ERROR: Layout size is empty。"),
            ("plain", "所以“看起来没生效”必须用一张对照探针图证明，不能只看 HTTP 200。"),
        ],
        caption="教学插图：左 Row/Expanded，右 Stack/Positioned，本页 DSL 绘制",
    ),
    dict(
        index=3, kicker="CHAPTER 03 · TEXT & COLOUR",
        title="文本三坑与尾部 alpha",
        standfirst="解析器不做 HTML 实体解码：空格归谁、尖括号怎么写、八位色从哪一位算起。",
        accent="#7C3AEDFF",
        bullets=[
            "文本里要出现 < 或 > 就用 CDATA；解析器不识别 HTML 实体，也不会把 &amp; 还原成 &。",
            "Text 会裁剪首尾空白，要保留原始空白就嵌套 Raw；Raw 的 textAlign、softWrap 等"
            "段落属性不生效。",
            "八位十六进制现在按 CSS 的 #RRGGBBAA 解析：旧的 #AARRGGBB 半透明红 #80FF0000 "
            "应写成 #FF000080，否则颜色会变。",
        ],
        ex=3, code_windows=None,
        code_title="example-03.snapshot",
        notes_title="为什么右边那块看不见",
        notes=[
            ("plain", "#80FF0000 按 #RRGGBBAA 读，等于 RGB(128,255,0) 且 alpha=00，"
                      "整块完全透明，只剩描边。"),
            ("ok", "#FF000080 → RGB(255,0,0) alpha=80，就是左块那层半透明红。"),
            ("warn", "Kotlin DSL 里的颜色 Int 仍用 0xAARRGGBB，不受这条迁移影响。"),
            ("plain", "本页示例把两种写法并排画出来，用的是同一套边框，只为让差异可见。"),
        ],
        caption="教学插图：CDATA / Raw / 行内富文本 / 两个色块，均由本页 DSL 绘制",
    ),
    dict(
        index=4, kicker="CHAPTER 04 · FILTER / SHIP",
        title="滤镜的作用范围，以及交付的自检",
        standfirst="BackdropFilter 只处理背后已画的像素，ImageFiltered 处理整棵子树。",
        accent="#059669FF",
        bullets=[
            "BackdropFilter 背后必须已经有内容才看得见效果，通常配合 ClipRect 或 ClipRRect "
            "限定区域；Parser 只支持高斯模糊。",
            "ImageFiltered 会对子树结果整体模糊，文字跟着糊；它会自动按 sigma 提供模糊输出边界。",
            "自检循环：渲染 → 读告警 → 打开 PNG 看 → 改脚本 → 再渲染；PNG 与同名 .snapshot "
            "一起交付，原始字节不做后处理。",
        ],
        ex=4, code_windows=None,
        code_title="example-04.snapshot",
        notes_title="本页交付清单",
        notes=[
            ("ok", "4 张手册页 1200×1600 + 4 张示例 400×240，均为服务真实响应。"),
            ("ok", "8 份同名 .snapshot，与最终渲染逐字一致。"),
            ("code", "sources.md  每条结论 → 文档或响应文件"),
            ("code", "examples.json  4 示例 / 用途 / 印刷片段"),
            ("warn", "token 与费用：平台未提供，指标里一律 null，不估算。"),
        ],
        caption="教学插图：左 BackdropFilter，右 ImageFiltered，滤镜为真实标签",
    ),
]


def build(page_spec):
    ex = [e for e in X.EXAMPLES if e["n"] == page_spec["ex"]][0]
    p = hb.Page(page_spec["index"], 4, page_spec["kicker"], page_spec["title"],
                page_spec["standfirst"], accent=page_spec["accent"])
    p.title_block(page_spec["title"], page_spec["standfirst"])
    p.h2("本页结论")
    for b in page_spec["bullets"]:
        p.bullet(b)
    p.h2("示例程序（节选）", page_spec["code_title"])

    lines = ex["dsl"].rstrip("\n").split("\n")
    wins = page_spec["code_windows"] or ex["windows"]
    rows = []
    for i, (a, bnd) in enumerate(wins):
        if i:
            prev_end = wins[i - 1][1]
            rows.append(("⋯", None,
                         "⋯⋯ 印刷省略 第 %d–%d 行（共 %d 行）；完整文档见 %s"
                         % (prev_end + 1, bnd - 1, bnd - 1 - prev_end,
                            page_spec["code_title"])))
        for n in range(a, bnd + 1):
            rows.append((str(n), hb.excerpt(ex["dsl"], n, n)[0], None))
    code_lines = len([r for r in rows if r[1] is not None])
    cb, cb_h = hb.code_block(hb.MARGIN, p.y, hb.CW, rows, size=CODE_SIZE, lh=CODE_LH,
                             title="%s · 完整 %d 行，本页印 %d 行"
                                   % (page_spec["code_title"], len(lines), code_lines))
    p.parts.extend(cb)
    p.y += cb_h + 26
    panel_h = illustration_panel(p, ex["art"], page_spec["caption"],
                                 "example-%02d.png  400×240" % ex["n"])
    notes_h = notes_box(p, page_spec["notes_title"], page_spec["notes"])
    p.y += max(panel_h, notes_h)
    p.footer("资料：ai-guide.md、openapi.yaml、snapshot.muedsa.com/guides/、/reference/parser-tags/")
    return p, ex, code_lines, len(rows)


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    meta = []
    for spec in PAGES:
        if only and spec["index"] != int(only):
            continue
        p, ex, code_lines, nrows = build(spec)
        dsl = p.dsl()
        name = "handbook-%02d.png" % spec["index"]
        dsl_name = "handbook-%02d.snapshot" % spec["index"]
        with open(os.path.join(DRAFTS, "v01-%s" % dsl_name), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write(dsl)
        r = snapkit.render(dsl, name, dsl_name, final=True)
        print("handbook-%02d ok=%s status=%s bytes=%s bottom=%.0f rows=%d warn=%d %s"
              % (spec["index"], r.get("ok"), r.get("status"), r.get("bytes"),
                 p.bottom(), nrows, len(hb.warnings()), (r.get("error") or "")[:300]))
        meta.append({"page": spec["index"], "name": name, "ok": bool(r.get("ok")),
                     "status": r.get("status"), "bytes": r.get("bytes"),
                     "bottom": p.bottom(), "printed_code_lines": code_lines,
                     "block_rows": nrows})
    json.dump(meta, open(os.path.join(TMP, "probe", "page-renders.json"), "w",
                         encoding="utf-8"), ensure_ascii=False, indent=2)
    for w in hb.warnings():
        print("WARN", w)


if __name__ == "__main__":
    main()