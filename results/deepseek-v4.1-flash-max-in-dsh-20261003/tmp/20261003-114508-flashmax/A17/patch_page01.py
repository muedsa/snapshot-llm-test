"""Rewrite page_01 in gen_handbook.py with the final layout (full-width code block)."""
import io

p = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\gen_handbook.py"
src = io.open(p, encoding="utf-8").read()

start = src.index("def page_01(")
end = src.index("# ------------------------------------------------------------------ page 2")

new = '''def page_01(ex_lines, ex_markers, ex_elided) -> str:
    p = Page(1200, 1600, 1, TOTAL_PAGES, "A17 · 01 · 调用契约",
             "从文本到图片：一次真实调用",
             "请求体、响应体与错误分支只有一条规则：成功是图片字节，失败是 JSON。")
    y = 192
    h1 = 276
    p.card(48, y, 1104, h1, "1 · 请求：纯文本 DSL", BLUE)
    p.bullets(64, y + 58, 700, [
        ("方法与路径", "POST /snapshot，没有 JSON 包装，也没有 multipart。"),
        ("请求头", "Content-Type: text/plain; charset=utf-8"),
        ("UTF-8", "本体必须是 UTF-8；带 BOM 会在位置 0 报 Not Support RAWTEXT。"),
        ("请求体", "就是 .snapshot 原文：一棵以 <Snapshot> 为根的元素树。"),
        ("根节点", "只允许一个根子节点；多一个就是 400 PARSE_ERROR。"),
    ], size=22, gap=36)
    fx, fy = 792, y + 58
    p.d.box(fx, fy, 336, 196, "#F8FAFCFF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(fx + 16, fy + 12, "一次调用的四步", 20, INK, weight="BOLD")
    for i, (a, b) in enumerate([("DSL 文本", "UTF-8"), ("Parser 建树", "Widget"),
                                ("布局绘制", "Skia"), ("PNG 字节", "HTTP 200")]):
        sy = fy + 46 + i * 35
        p.d.box(fx + 16, sy, 200, 26, "#FFFFFFFF", radius=6, border=f"1 SOLID {LINE}")
        p.d.text(fx + 26, sy + 4, a, 17, INK, family=MONO)
        p.d.text(fx + 224, sy + 5, b, 14, ACCENT, family=MONO)
        if i < 3:
            p.d.box(fx + 116, sy + 27, 2, 7, "#CBD5E1FF")
    y += h1 + 12
    h2 = 224
    p.card(48, y, 1104, h2, "2 · 响应：两条分支", ACCENT)
    bx, by, bw = 64, y + 58, 520
    p.d.box(bx, by, bw, 146, "#F0FDF9FF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(bx + 16, by + 12, "HTTP 200 · Content-Type: image/png", 20, "#047857FF", weight="BOLD")
    p.bullets(bx + 16, by + 52, bw - 32, ["本体就是 PNG 原始字节，直接写入 .png。",
                                          "响应头带 X-Request-Id，可用来对账。"], size=20, gap=30)
    p.d.box(bx + bw + 24, by, bw, 146, "#FEF2F2FF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(bx + bw + 40, by + 12, "HTTP 400 · Content-Type: application/json", 20, "#B42318FF", weight="BOLD")
    p.bullets(bx + bw + 40, by + 52, bw - 32, ["本体是 {code, message, requestId} 错误对象。",
                                               "绝不能把这份 JSON 存成 .png。"], size=20, gap=30)
    y += h2 + 12
    h3 = 470
    p.card(48, y, 1104, h3, "3 · 最小可运行示例（example-01）", AMBER)
    p.code(64, y + 58, 744, ex_lines, size=20, markers=ex_markers)
    p.d.text(64, y + h3 - 34, "example-01.snapshot → example-01.png（400×240，服务原始字节）", 20, MUTED)
    fx, fy, fw, fh = 840, y + 62, 240, 144
    p.d.box(fx - 8, fy - 8, fw + 16, fh + 16, "#0F172AFF", radius=12)
    for i in range(120):
        t = i / 119.0
        r = int(15 + (29 - 15) * t)
        g = int(23 + (78 - 23) * t)
        b = int(42 + (216 - 42) * t)
        p.d.box(fx, fy + i * (fh / 120.0), fw, fh / 120.0 + 1, f"#{r:02X}{g:02X}{b:02X}FF")
    p.d.text(fx, fy + 54, "Hello Snapshot", 20, "#F8FAFCFF", weight="BOLD", w=fw, align="CENTER_RIGHT")
    p.d.text(fx + 12, fy + 112, "POST /snapshot", 14, "#BFDBFEFF", family=MONO)
    p.d.text(fx, fy + fh + 30, "400×240 · 同一段 DSL 的实际结果，", 19, BODY)
    p.d.text(fx, fy + fh + 56, "内容位置与颜色与实图一致。", 19, BODY)
    y += h3 + 12
    h4 = 1600 - 54 - 10 - y
    p.card(48, y, 1104, h4, "4 · 错误分类与处理", RED)
    rows = [
        ("400 PARSE_ERROR", "语法/属性错误，消息带行列与偏移，改 DSL 后重发。"),
        ("413 REQUEST_TOO_LARGE", "请求体越限：减少嵌套或拆成多次调用。"),
        ("429 / 503", "限流或暂时故障：参考 Retry-After 后重试。"),
        ("401", "需要凭据：放在请求头，不写进 DSL 或提示词。"),
    ]
    for i, (a, b) in enumerate(rows):
        ry = y + 56 + i * 27
        p.d.text(66, ry, a, 20, INK, family=MONO, w=290, align="CENTER_LEFT")
        p.d.text(372, ry, b, 20, BODY)
    return p.finish()


'''

src = src[:start] + new + src[end:]
io.open(p, "w", encoding="utf-8", newline="\n").write(src)
print("rewrote page_01 OK")
