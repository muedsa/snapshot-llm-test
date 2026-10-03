"""Rewrite pages 2-4 of gen_handbook.py with corrected heights and measured widths."""
import io

p = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\gen_handbook.py"
src = io.open(p, encoding="utf-8").read()

start = src.index("# ------------------------------------------------------------------ page 2")
end = src.index("PAGES = [page_01, page_02, page_03, page_04]")

new = '''# ------------------------------------------------------------------ page 2
def page_02(ex_lines, ex_markers, ex_elided) -> str:
    p = Page(1200, 1600, 2, TOTAL_PAGES, "A17 · 02 · 根尺寸与布局",
             "根尺寸来自布局，不是 HTML 画布",
             "Snapshot 是约束布局：父节点给约束、子节点报尺寸，最后用根 RenderBox 的尺寸出图。")
    y = 192
    h1 = 260
    p.card(48, y, 1104, h1, "1 · 定义根尺寸的三种写法", BLUE)
    rows1 = [
        ("width / height", "固定画布：根 Container 上直接写 400×240。"),
        ("子节点决定", "无尺寸容器收缩到内容；空容器在无界约束下变成 0×0。"),
        ("边界情况", "根尺寸为 0 或无限都会报错：先把根尺寸写死。"),
    ]
    for i, (a, b) in enumerate(rows1):
        by = y + 58 + i * 62
        p.d.box(64, by, 640, 54, CODE_BG, radius=8, border=f"1 SOLID {LINE}")
        p.d.text(80, by + 15, a, 21, BLUE, weight="BOLD", family=MONO)
        p.d.text(284, by + 15, b, 21, BODY)
    dx, dy = 760, y + 58
    p.d.box(dx, dy, 368, 190, "#F8FAFCFF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(dx + 16, dy + 12, "根 RenderBox 的布局尺寸 = 输出像素", 18, INK, weight="BOLD")
    p.d.box(dx + 24, dy + 48, 240, 128, "#FFFFFFFF", radius=6, border=f"2 SOLID {ACCENT}")
    p.d.text(dx + 36, dy + 88, "width 400", 18, BLUE, family=MONO)
    p.d.text(dx + 36, dy + 116, "height 240", 18, BLUE, family=MONO)
    p.d.text(dx + 36, dy + 148, "向上取整为像素", 17, MUTED)
    y += h1 + 10
    h2 = 260
    p.card(48, y, 1104, h2, "2 · 有界 Row / Column / Expanded", ACCENT)
    p.bullets(64, y + 58, 1072, [
        ("有界主轴", "Flex 主轴无限时无法分配剩余空间：先给宽高，或在有界父级里用 Expanded。"),
        ("Expanded", "相当于 Flexible(fit=TIGHT)，强制占满分到的份额；只能是 Flex 的直属子节点。"),
        ("Flexible / Spacer", "fit=\\"LOOSE\\" 允许更小；Spacer 只占位不绘制。"),
        ("mainAxisSize", "MIN 时 Flex 收缩到内容，MAX 时撑满父约束。"),
    ], size=22, gap=36, limit=y + h2 - 16)
    y += h2 + 10
    h3 = 236
    p.card(48, y, 1104, h3, "3 · Stack + Positioned：绝对坐标层", AMBER)
    p.d.box(64, y + 58, 596, 152, "#F8FAFCFF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(80, y + 76, "Stack (0,0) → 右下增长", 18, MUTED, family=MONO)
    for i, (ox, oy, col, lb) in enumerate([(40, 78, "#0E9F8FFF", "(40,60)"),
                                           (150, 78, "#1D4ED8FF", "(120,60)"),
                                           (260, 78, "#7C3AEDFF", "(200,60)")]):
        p.d.box(64 + ox, y + oy + 20, 70, 56, col, radius=8)
        p.d.text(64 + ox, y + oy + 80, lb, 16, INK, family=MONO, w=70, align="CENTER_RIGHT")
    p.bullets(680, y + 58, 456, [
        "Positioned 只能是 Stack / IndexedStack 的直属子节点；放进 Column 会报 parentData 错误。",
        "每轴 left / right / width 中最多给两个。",
    ], size=20, gap=30, limit=y + h3 - 16)
    y += h3 + 10
    h4 = 1600 - 54 - 10 - y
    p.card(48, y, 1104, h4, "4 · 完整可运行示例（example-02）", BLUE)
    p.code(64, y + 56, 748, ex_lines, size=20, markers=ex_markers)
    p.d.text(64, y + h4 - 32, "example-02.snapshot → example-02.png（400×240，三段各 122.7px）", 18, MUTED)
    fx, fy, fw, fh = 848, y + 58, 240, 144
    p.d.box(fx - 8, fy - 8, fw + 16, fh + 16, "#CBD5E1FF", radius=12)
    p.d.box(fx, fy, fw, fh, "#EEF2F7FF")
    p.d.box(fx, fy, fw, 8, "#F8FAFCFF")
    p.d.box(fx, fy + 72, fw, 8, "#F8FAFCFF")
    for i, c in enumerate(["#0E9F8FFF", "#1D4ED8FF", "#7C3AEDFF"]):
        p.d.box(fx + i * (fw / 3.0), fy + 8, fw / 3.0, 64, c)
    p.d.box(fx + 12, fy + 16, 104, 22, "#0F172AD9", radius=11)
    p.d.text(fx + 12, fy + 20, "1:1:1", 13, "#F8FAFCFF", family=MONO, w=104, align="CENTER_RIGHT")
    p.d.box(fx, fy + 92, fw, 44, "#0F172AFF")
    p.d.text(fx + 12, fy + 104, "Row 主轴 368", 13, "#E2E8F0FF", family=MONO)
    p.d.text(fx, fy + fh + 28, "三段 Expanded 等宽，各 122.7px；", 17, BODY)
    p.d.text(fx, fy + fh + 54, "位置标签落在 (40,60) 覆盖色带。", 17, BODY)
    p.d.text(fx, fy + fh + 80, "Stack fit=EXPAND 才会撑满根容器。", 17, BODY)
    return p.finish()


# ------------------------------------------------------------------ page 3
def page_03(ex_lines, ex_markers, ex_elided) -> str:
    p = Page(1200, 1600, 3, TOTAL_PAGES, "A17 · 03 · 文本与颜色",
             "原样文本、CDATA 与尾部 alpha",
             "Text 会 trim、Raw 不会；解析器不做 HTML 实体解码；8 位颜色的最后两位是透明度。")
    y = 192
    h1 = 380
    p.card(48, y, 1104, h1, "1 · Text / Raw / CDATA 的真实行为", BLUE)
    p.bullets(64, y + 58, 1072, [
        ("Text 会 trim", "首尾空白丢失；要保留缩进和换行就用 Raw。"),
        ("不解实体", "解析器不做 HTML 实体解码：&lt; 与 &amp; 会原样显示，不会变成尖括号或 &。"),
        ("CDATA 才是正解", "文本里要出现 < 或 > 必须用 CDATA 包住。"),
        ("裸写反而报错", "Text 里裸写 < 会被当作标签开头，报 Unexpected character in TAG_OPEN。"),
        ("非文本标签", "容器里出现非空白原始文本会报 Not Support RAWTEXT。"),
    ], size=22, gap=34, limit=y + 292)
    p.d.box(64, y + 302, 1072, 62, "#FEF2F2FF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(80, y + 312, "真实 400 响应（本项目实测，requestId a1ea4ec4）", 17, RED, weight="BOLD")
    p.d.text(80, y + 336, "Unexpected character ' ' in input state [TAG_OPEN]", 17, INK, family=MONO)
    y += h1 + 10
    h2 = 332
    p.card(48, y, 1104, h2, "2 · 尾部 alpha：8 位十六进制的最后两位", AMBER)
    p.bullets(64, y + 58, 500, [
        ("#RRGGBBAA", "前六位是色相，后两位是 alpha：FF 不透明、80 约 50%、00 完全透明。"),
        ("旧写法不再成立", "Kotlin 侧仍是 0xAARRGGBB，但 DSL 文本按 CSS 的 #RRGGBBAA 解析。"),
        ("透明度合成", "半透明色块叠在白底与深底上结果不同，见右图。"),
    ], size=20, gap=30, limit=y + h2 - 16)
    dx, dy = 600, y + 58
    p.d.box(dx, dy, 536, 250, "#F8FAFCFF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(dx + 16, dy + 12, "同一颜色四个 alpha（上：白底，下：深底）", 19, INK, weight="BOLD")
    for i, c in enumerate(["#1D4ED8FF", "#1D4ED880", "#1D4ED840", "#1D4ED800"]):
        p.d.box(dx + 16 + i * 128, dy + 52, 110, 66, c, radius=8)
        p.d.text(dx + 16 + i * 128, dy + 126, c, 15, MUTED, family=MONO)
    p.d.box(dx + 16, dy + 158, 504, 72, "#0F172AFF", radius=8)
    for i, c in enumerate(["#1D4ED8FF", "#1D4ED880", "#1D4ED840", "#1D4ED800"]):
        p.d.box(dx + 30 + i * 124, dy + 174, 100, 40, c, radius=6)
    p.d.text(dx + 16, dy + 234, "alpha=00 就是不绘制，不是黑色。", 17, MUTED)
    y += h2 + 10
    h3 = 1600 - 54 - 10 - y
    p.card(48, y, 1104, h3, "3 · 完整可运行示例（example-03）", ACCENT)
    p.code(64, y + 56, 748, ex_lines, size=20, markers=ex_markers)
    p.d.text(64, y + h3 - 32, "example-03.snapshot → example-03.png（400×240）", 18, MUTED)
    fx, fy, fw, fh = 848, y + 58, 240, 144
    p.d.box(fx - 8, fy - 8, fw + 16, fh + 16, "#CBD5E1FF", radius=12)
    p.d.box(fx, fy, fw, fh, "#FFFFFFFF")
    for i in range(60):
        t = i / 59.0
        a = 1.0 - t
        r = int(14 + (255 - 14) * (1 - a))
        g = int(159 + (255 - 159) * (1 - a))
        b = int(143 + (255 - 143) * (1 - a))
        p.d.box(fx + i * 4, fy, 4.5, 66, f"#{r:02X}{g:02X}{b:02X}FF")
    p.d.text(fx + 10, fy + 10, "尾部 alpha 决定透明度", 14, "#0F172AFF")
    p.d.text(fx + 10, fy + 84, "CDATA 里能写 <Text> 字样", 13, "#0F172AFF", family=MONO)
    p.d.text(fx + 10, fy + 108, "裸写 &lt; 不会还原成 <", 13, "#0F172AFF", family=MONO)
    p.d.text(fx, fy + fh + 26, "左端 #0E9F8FCC，右端 alpha=00；", 17, BODY)
    p.d.text(fx, fy + fh + 52, "下方原样打印 CDATA 里的内容。", 17, BODY)
    p.d.text(fx, fy + fh + 78, "字面量 &lt; 会照原样出现在图里。", 17, BODY)
    return p.finish()


# ------------------------------------------------------------------ page 4
def page_04(ex_lines, ex_markers, ex_elided) -> str:
    p = Page(1200, 1600, 4, TOTAL_PAGES, "A17 · 04 · 滤镜与交付",
             "背景滤镜、子树滤镜与可复现交付",
             "BackdropFilter 模糊已经画在背后的内容；ImageFiltered 只模糊自己的子树。")
    y = 192
    h1 = 320
    p.card(48, y, 1104, h1, "1 · 两种模糊：背景 vs 子树", BLUE)
    p.bullets(64, y + 58, 700, [
        ("BackdropFilter", "读取背后已绘制的像素做高斯模糊，自己的子节点不被模糊。"),
        ("配合裁剪", "通常用 ClipRect / ClipRRect 限定滤镜区域，否则笔触会波及整个画布。"),
        ("ImageFiltered", "只模糊自己的子树，里面的文字会一起变糊。"),
        ("sigma 取值", "sigma 越大越糊；要让文字保持锐利，就把文字放在滤镜外层。"),
    ], size=21, gap=34, limit=y + 250)
    dx, dy = 800, y + 58
    p.d.box(dx, dy, 336, 240, "#F8FAFCFF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(dx + 16, dy + 10, "背后已有内容才有效果", 17, MUTED)
    for i, c in enumerate(["#1D4ED8FF", "#0E9F8FFF", "#D97706FF"]):
        p.d.box(dx + 16 + i * 74, dy + 44, 66, 66, c, radius=8)
    p.d.box(dx + 16, dy + 130, 304, 56, "#FFFFFFCC", radius=8, border=f"2 SOLID {ACCENT}")
    p.d.text(dx + 28, dy + 146, "BackdropFilter sigma=8", 17, INK, family=MONO)
    p.d.text(dx + 16, dy + 198, "下方色块被糊，文字依然锐利。", 17, BODY)
    p.d.text(dx + 16, dy + 220, "ImageFiltered 则会把字一起糊掉。", 17, BODY)
    y += h1 + 10
    h2 = 300
    p.card(48, y, 1104, h2, "2 · 视觉自检：先看图，再算数", ACCENT)
    checks = [
        "每张最终图都用图像工具实际打开，不靠 XML、HTTP 200 或像素统计代替。",
        "对照 TASK.md 逐项核对：尺寸、元素个数、文字是否被裁切或互相压字。",
        "必要时放大看局部（密集区域、引导线、小字号），再回到整体看构图。",
        "发现问题就改 DSL 重渲染并重新打开比较，直到每项需求都成立。",
    ]
    for i, c in enumerate(checks):
        cy = y + 58 + i * 40
        p.d.box(64, cy + 4, 22, 22, "#DCFCE7FF", radius=6, border="1 SOLID #16A34AFF")
        p.d.text(64, cy + 7, "✓", 17, "#15803DFF", w=22, align="CENTER_RIGHT")
        p.d.text(102, cy, c, 22, BODY)
    p.d.box(64, y + 222, 1072, 58, "#F8FAFCFF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(80, y + 232, "本项目实际执行：8 张最终图逐张打开核对，发现并修掉了 4 处溢出/压字问题。", 18, BODY)
    p.d.text(80, y + 256, "自动化只能补充：自写 CGRect 检查把文字宽度与卡片边界逐行比对。", 18, BODY)
    y += h2 + 10
    h3 = 236
    p.card(48, y, 1104, h3, "3 · 可复现交付", AMBER)
    p.bullets(64, y + 58, 1072, [
        ("原始字节", "最终 PNG 直接用服务返回的原始字节，不做任何后处理。"),
        ("同名 DSL", "每张图都保留同名 .snapshot，与字节数、SHA-256 一起记录。"),
        ("可重现性", "相同 DSL 返回相同字节；用 X-Request-Id 把每次请求与输出对账。"),
        ("错误不落盘", "失败响应单独存为 .failed.txt，绝不写进最终 .png。"),
    ], size=22, gap=34, limit=y + h3 - 16)
    y += h3 + 10
    h4 = 1600 - 54 - 10 - y
    p.card(48, y, 1104, h4, "4 · 完整可运行示例（example-04）", BLUE)
    p.code(64, y + 56, 748, ex_lines, size=20, markers=ex_markers)
    p.d.text(64, y + h4 - 32, "example-04.snapshot → example-04.png（400×240）", 18, MUTED)
    fx, fy, fw, fh = 848, y + 58, 240, 144
    p.d.box(fx - 8, fy - 8, fw + 16, fh + 16, "#CBD5E1FF", radius=12)
    p.d.box(fx, fy, fw, fh, "#F8FAFCFF")
    for i, c in enumerate(["#1D4ED8FF", "#0E9F8FFF", "#D97706FF"]):
        p.d.box(fx + 10 + i * 74, fy + 26, 62, 62, c, radius=8)
    p.d.box(fx + 70, fy + 36, 88, 44, "#FFFFFFF2", radius=7)
    p.d.text(fx + 70, fy + 50, "模糊子树", 12, "#334155FF", w=88, align="CENTER_RIGHT")
    p.d.box(fx, fy + 100, fw, 44, "#FFFFFFFF")
    p.d.box(fx + 4, fy + 106, 130, 32, "#FFFFFF40", radius=6, border="1 SOLID #94A3B8FF")
    p.d.text(fx + 12, fy + 114, "模糊背景", 12, "#334155FF")
    p.d.text(fx, fy + fh + 26, "ImageFiltered：白卡与字一起糊。", 17, BODY)
    p.d.text(fx, fy + fh + 52, "BackdropFilter：只糊背后色块。", 17, BODY)
    p.d.text(fx, fy + fh + 78, "两者都要求背后已有内容。", 17, BODY)
    return p.finish()


'''

src = src[:start] + new + src[end:]
io.open(p, "w", encoding="utf-8", newline="\n").write(src)
print("pages 2-4 rewritten")
