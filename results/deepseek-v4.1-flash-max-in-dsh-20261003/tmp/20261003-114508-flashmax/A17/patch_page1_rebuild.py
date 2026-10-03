"""Rebuild page 1 with a single source of truth: CARD1..CARD4 heights, all measured.

Constraint chain (bottom-up, page height 1600, footer band starts at 1546):
  card1 wants 280      (5 bullets, 1 line each, gap 30)
  card2 wants 244      (2 boxes, 2 bullets each, gap 26)
  card3 wants 456      (code block 356 + caption 36 + label band 32 + padding)
  card4 wants 160      (title 44 + 4 rows x 25 + bottom pad)
  192 + 280 + 10 + 244 + 10 + 456 + 10 + 160 = 1362 < 1536  -> fits with slack
"""
import io

p = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\gen_handbook.py"
s = io.open(p, encoding="utf-8").read()

start = s.index("# ------------------------------------------------------------------ page 1")
end = s.index("# ------------------------------------------------------------------ page 2")

new = '''# ------------------------------------------------------------------ page 1
def page_01(ex_lines, ex_markers, ex_elided) -> str:
    p = Page(1200, 1600, 1, TOTAL_PAGES, "A17 · 01 · 调用契约",
             "从文本到图片：一次真实调用",
             "请求体、响应体与错误分支只有一条规则：成功是图片字节，失败是 JSON。")
    y = 192
    h1, h2, h3 = 280, 244, 456
    p.card(48, y, 1104, h1, "1 · 请求：纯文本 DSL", BLUE)
    p.bullets(64, y + 58, 1072, [
        ("方法与路径", "POST /snapshot，没有 JSON 包装。"),
        ("请求头", "Content-Type: text/plain; charset=utf-8"),
        ("UTF-8", "带 BOM 会在位置 0 报错 Not Support RAWTEXT。"),
        ("请求体", "就是 .snapshot 原文，以 Snapshot 为根。"),
        ("根节点", "多一个根子节点就是 400 PARSE_ERROR。"),
    ], size=22, gap=30, limit=y + h1 - 12)
    y += h1 + 10
    p.card(48, y, 1104, h2, "2 · 响应：两条分支", ACCENT)
    bx, by, bw = 64, y + 58, 520
    p.d.box(bx, by, bw, 174, "#F0FDF9FF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(bx + 16, by + 12, "HTTP 200 · Content-Type: image/png", 20, "#047857FF", weight="BOLD")
    p.bullets(bx + 16, by + 52, bw - 32, ["本体就是 PNG 原始字节，直接写入 .png。",
                                          "响应头带 X-Request-Id，可用来对账。"], size=20, gap=26, limit=by + 166)
    p.d.box(bx + bw + 24, by, bw, 174, "#FEF2F2FF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(bx + bw + 40, by + 12, "HTTP 400 · Content-Type: application/json", 20, "#B42318FF", weight="BOLD")
    p.bullets(bx + bw + 40, by + 52, bw - 32, ["本体是 {code, message, requestId} 错误对象。",
                                               "绝不能把这份 JSON 存成 .png。"], size=20, gap=26, limit=by + 166)
    y += h2 + 10
    p.card(48, y, 1104, h3, "3 · 最小可运行示例（example-01）", AMBER)
    ch = p.code(64, y + 56, 748, ex_lines, size=18, markers=ex_markers, limit=y + h3 - 62)
    p.d.text(64, y + 70 + ch, "example-01.snapshot → example-01.png（400×240，服务原始字节）", 18, MUTED)
    fx, fy, fw, fh = 848, y + 58, 240, 144
    p.d.box(fx - 8, fy - 8, fw + 16, fh + 16, "#0F172AFF", radius=12)
    for i in range(120):
        t = i / 119.0
        r = int(15 + (29 - 15) * t)
        g = int(23 + (78 - 23) * t)
        b = int(42 + (216 - 42) * t)
        p.d.box(fx, fy + i * (fh / 120.0), fw, fh / 120.0 + 1, f"#{r:02X}{g:02X}{b:02X}FF")
    p.d.text(fx, fy + 54, "Hello Snapshot", 20, "#F8FAFCFF", weight="BOLD", w=fw, align="CENTER_RIGHT")
    p.d.text(fx + 12, fy + 112, "POST /snapshot", 14, "#BFDBFEFF", family=MONO)
    p.d.text(fx, fy + fh + 30, "400×240 · 同一段 DSL 的实际结果，", 17, BODY)
    p.d.text(fx, fy + fh + 56, "内容位置与颜色与实图一致。", 17, BODY)
    p.d.text(fx, fy + fh + 92, "右图用同一套 Container / Stack /", 17, BODY)
    p.d.text(fx, fy + fh + 118, "Text 构件把示例结果直接画出来。", 17, BODY)
    y += h3 + 10
    h4 = 1600 - 54 - 10 - y
    assert h4 >= 150, f"page 1 error card too short: {h4}"
    p.card(48, y, 1104, h4, "4 · 错误分类与处理", RED)
    rows = [
        ("400 PARSE_ERROR", "语法/属性错误，消息带行列与偏移，改 DSL 后重发。"),
        ("413 REQUEST_TOO_LARGE", "请求体越限：减少嵌套或拆成多次调用。"),
        ("429 / 503", "限流或暂时故障：参考 Retry-After 后重试。"),
        ("401", "需要凭据：放在请求头，不写进 DSL 或提示词。"),
    ]
    for i, (a, b) in enumerate(rows):
        ry = y + 54 + i * 25
        assert ry + 26 <= y + h4, f"error row {i} escapes the card"
        assert 362 + text_w(b, 20) <= 1152 - 16, f"error row {i} text too wide"
        p.d.text(66, ry, a, 20, INK, family=MONO, w=280, align="CENTER_LEFT")
        p.d.text(362, ry, b, 20, BODY)
    return p.finish()


'''

s = s[:start] + new + s[end:]
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("page 1 rebuilt")
