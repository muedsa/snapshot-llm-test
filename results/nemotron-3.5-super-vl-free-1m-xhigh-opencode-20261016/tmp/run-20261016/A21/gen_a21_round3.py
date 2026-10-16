# gen_a21_round3.py - 生成 A21 Round 03 的两张发布海报
import json, os

SUITE_ROOT = os.environ.get("SNAPSHOT_TASK_ROOT", ".")
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261016")
OUTPUT_ROOT = os.path.join(SUITE_ROOT, "outputs", RUN_ID, "A21")
TEMP_DIR = os.path.join(SUITE_ROOT, "tmp", RUN_ID, "A21")
SERVICE_URL = "https://open-snapshot.muedsa.com/snapshot"
FONT = "Noto Sans CJK SC,Inter"

# Round 03 设计令牌（浅色主题，白色背景）
DESIGN_TOKENS = {
    "primary_color": "#2563EB",
    "bg_color": "#FFFFFF",
    "title_color": "#111827",
    "body_color": "#64748B",
    "accent_color": "#DC2626",
    "brand_colors": ["#2563EB", "#EF4444", "#10B981", "#F59E0B", "#8B5CF6"],
    "title_font_size": 48,
    "body_font_size": 24,
    "brand_components": 5
}

# Round 03 内容（基于 Round 02，新增英语句）
ROUND3_CONTENT = {
    "title_lines": [
        "当所有信息都想成为标题：",
        "让复杂信息变得清晰",
        "的结构化方法"
    ],
    "english_line": "Clarity through structure",
    "datetime": "2026.11.07 19:30",
    "label": "ONLINE LAUNCH",
    "speakers": "讲者：林川 / 苏言",
    "website": "layerlight.example.org",
    "brand_name": "叠光 Layerlight",
    "sponsor1": "Northstar Research / 云构工具",
    "sponsor2": "免费参加 · 无需报名"
}

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def gen_portrait(W, H, content, tokens):
    lines = []
    lines.append('<Snapshot type="png">')
    lines.append('  <SizedBox width="' + str(W) + '" height="' + str(H) + '">')
    lines.append('    <Stack alignment="TOP_LEFT">')
    lines.append('      <Container color="' + tokens["bg_color"] + '" width="' + str(W) + '" height="' + str(H) + '"/>')

    # 顶部扩展空间
    lines.append('      <Container color="' + tokens["bg_color"] + '" left="0" top="0" width="' + str(W) + '" height="100"/>')

    # 品牌图形（5个构件）- 顶部
    cx = W // 2
    lines.append('      <Container color="' + tokens["brand_colors"][0] + '" borderRadius="24" left="' + str(cx-60) + '" top="120" width="48" height="48"/>')
    lines.append('      <Container color="' + tokens["brand_colors"][1] + '" borderRadius="12" left="' + str(cx-10) + '" top="130" width="24" height="24"/>')
    lines.append('      <Container color="' + tokens["brand_colors"][2] + '" borderRadius="8" left="' + str(cx+40) + '" top="150" width="32" height="16"/>')
    lines.append('      <Container color="' + tokens["brand_colors"][3] + '" borderRadius="4" left="' + str(cx-40) + '" top="160" width="16" height="16"/>')
    lines.append('      <Container color="' + tokens["brand_colors"][4] + '" borderRadius="6" left="' + str(cx+10) + '" top="170" width="20" height="20"/>')

    # ONLINE LAUNCH 标签
    lines.append('      <Container color="#F0F7FF" borderRadius="20" left="' + str(cx-90) + '" top="230" width="180" height="40"/>')
    lines.append('      <Text left="' + str(cx-70) + '" top="242" fontSize="20" fill="' + tokens["primary_color"] + '" fontStyle="BOLD" fontFamily="' + FONT + '">' + esc(content["label"]) + '</Text>')

    # 主标题（3行，≥48px）
    ty = 300
    for line in content["title_lines"]:
        lines.append('      <Text left="60" top="' + str(ty) + '" width="' + str(W-120) + '" fontSize="' + str(tokens["title_font_size"]) + '" fontStyle="BOLD" fill="' + tokens["title_color"] + '" fontFamily="' + FONT + '">' + esc(line) + '</Text>')
        ty += 60

    # 英语新增句（在网址上方，≥24px）
    lines.append('      <Text left="60" top="' + str(ty+10) + '" fontSize="' + str(tokens["body_font_size"]) + '" fill="' + tokens["primary_color"] + '" fontStyle="BOLD" fontFamily="' + FONT + '">' + esc(content["english_line"]) + '</Text>')

    # 日期时间
    lines.append('      <Text left="60" top="' + str(ty+45) + '" fontSize="' + str(tokens["body_font_size"]) + '" fill="' + tokens["body_color"] + '" fontFamily="' + FONT + '">' + esc(content["datetime"]) + '</Text>')

    # 讲者
    lines.append('      <Text left="60" top="' + str(ty+80) + '" fontSize="' + str(tokens["body_font_size"]) + '" fill="' + tokens["body_color"] + '" fontFamily="' + FONT + '">' + esc(content["speakers"]) + '</Text>')

    # 网址
    lines.append('      <Text left="60" top="' + str(ty+115) + '" fontSize="' + str(tokens["body_font_size"]) + '" fill="' + tokens["primary_color"] + '" fontStyle="BOLD" fontFamily="' + FONT + '">' + esc(content["website"]) + '</Text>')

    # 赞助方
    lines.append('      <Text left="60" top="' + str(ty+150) + '" fontSize="' + str(tokens["body_font_size"]) + '" fill="' + tokens["body_color"] + '" fontFamily="' + FONT + '">' + esc(content["sponsor1"]) + '</Text>')
    lines.append('      <Text left="60" top="' + str(ty+185) + '" fontSize="' + str(tokens["body_font_size"]) + '" fill="' + tokens["body_color"] + '" fontFamily="' + FONT + '">' + esc(content["sponsor2"]) + '</Text>')

    # 装饰线
    lines.append('      <Container color="' + tokens["primary_color"] + '" left="60" top="' + str(ty+225) + '" width="60" height="3"/>')

    # 底部扩展空间
    lines.append('      <Container color="' + tokens["bg_color"] + '" left="0" top="' + str(H-100) + '" width="' + str(W) + '" height="100"/>')

    lines.append('    </Stack>')
    lines.append('  </SizedBox>')
    lines.append('</Snapshot>')
    return "\n".join(lines)

def gen_wide(W, H, content, tokens):
    lines = []
    lines.append('<Snapshot type="png">')
    lines.append('  <SizedBox width="' + str(W) + '" height="' + str(H) + '">')
    lines.append('    <Stack alignment="TOP_LEFT">')
    lines.append('      <Container color="' + tokens["bg_color"] + '" width="' + str(W) + '" height="' + str(H) + '"/>')

    # 顶部扩展空间
    lines.append('      <Container color="' + tokens["bg_color"] + '" left="0" top="0" width="' + str(W) + '" height="60"/>')

    # 左侧品牌图形
    lx = 80
    lines.append('      <Container color="' + tokens["brand_colors"][0] + '" borderRadius="24" left="' + str(lx) + '" top="90" width="48" height="48"/>')
    lines.append('      <Container color="' + tokens["brand_colors"][1] + '" borderRadius="12" left="' + str(lx+60) + '" top="100" width="24" height="24"/>')
    lines.append('      <Container color="' + tokens["brand_colors"][2] + '" borderRadius="8" left="' + str(lx+100) + '" top="120" width="32" height="16"/>')
    lines.append('      <Container color="' + tokens["brand_colors"][3] + '" borderRadius="4" left="' + str(lx+40) + '" top="130" width="16" height="16"/>')
    lines.append('      <Container color="' + tokens["brand_colors"][4] + '" borderRadius="6" left="' + str(lx+80) + '" top="140" width="20" height="20"/>')

    # ONLINE LAUNCH 标签
    lines.append('      <Container color="#F0F7FF" borderRadius="20" left="' + str(lx) + '" top="190" width="160" height="36"/>')
    lines.append('      <Text left="' + str(lx+20) + '" top="200" fontSize="20" fill="' + tokens["primary_color"] + '" fontStyle="BOLD" fontFamily="' + FONT + '">' + esc(content["label"]) + '</Text>')

    # 主标题（3行，≥48px）
    ty = 250
    for line in content["title_lines"]:
        lines.append('      <Text left="' + str(lx) + '" top="' + str(ty) + '" width="600" fontSize="' + str(tokens["title_font_size"]) + '" fontStyle="BOLD" fill="' + tokens["title_color"] + '" fontFamily="' + FONT + '">' + esc(line) + '</Text>')
        ty += 60

    # 英语新增句
    lines.append('      <Text left="' + str(lx) + '" top="' + str(ty+10) + '" fontSize="' + str(tokens["body_font_size"]) + '" fill="' + tokens["primary_color"] + '" fontStyle="BOLD" fontFamily="' + FONT + '">' + esc(content["english_line"]) + '</Text>')

    # 右侧信息
    rx = 720
    lines.append('      <Text left="' + str(rx) + '" top="110" fontSize="' + str(tokens["body_font_size"]) + '" fill="' + tokens["body_color"] + '" fontFamily="' + FONT + '">' + esc(content["datetime"]) + '</Text>')
    lines.append('      <Text left="' + str(rx) + '" top="145" fontSize="' + str(tokens["body_font_size"]) + '" fill="' + tokens["body_color"] + '" fontFamily="' + FONT + '">' + esc(content["speakers"]) + '</Text>')
    lines.append('      <Text left="' + str(rx) + '" top="180" fontSize="' + str(tokens["body_font_size"]) + '" fill="' + tokens["primary_color"] + '" fontStyle="BOLD" fontFamily="' + FONT + '">' + esc(content["website"]) + '</Text>')
    lines.append('      <Text left="' + str(rx) + '" top="215" fontSize="' + str(tokens["body_font_size"]) + '" fill="' + tokens["body_color"] + '" fontFamily="' + FONT + '">' + esc(content["sponsor1"]) + '</Text>')
    lines.append('      <Text left="' + str(rx) + '" top="250" fontSize="' + str(tokens["body_font_size"]) + '" fill="' + tokens["body_color"] + '" fontFamily="' + FONT + '">' + esc(content["sponsor2"]) + '</Text>')

    # 装饰线
    lines.append('      <Container color="' + tokens["primary_color"] + '" left="' + str(lx) + '" top="350" width="80" height="3"/>')

    # 底部扩展空间
    lines.append('      <Container color="' + tokens["bg_color"] + '" left="0" top="' + str(H-60) + '" width="' + str(W) + '" height="60"/>')

    lines.append('    </Stack>')
    lines.append('  </SizedBox>')
    lines.append('</Snapshot>')
    return "\n".join(lines)

# 对比度计算（sRGB → 线性 → 相对亮度 → 对比度）
def srgb_to_linear(c):
    c = c / 255.0
    if c <= 0.04045:
        return c / 12.92
    else:
        return ((c + 0.055) / 1.055) ** 2.4

def relative_luminance(r, g, b):
    Rl = srgb_to_linear(r)
    Gl = srgb_to_linear(g)
    Bl = srgb_to_linear(b)
    return 0.2126 * Rl + 0.7152 * Gl + 0.0722 * Bl

def contrast_ratio(L1, L2):
    if L1 > L2:
        return (L1 + 0.05) / (L2 + 0.05)
    else:
        return (L2 + 0.05) / (L1 + 0.05)

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def render(dsl_content, out_path):
    import urllib.request
    req = urllib.request.Request(
        SERVICE_URL,
        data=dsl_content.encode("utf-8"),
        headers={"Content-Type": "text/plain; charset=utf-8", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    with open(out_path, "wb") as f:
        f.write(data)
    print("Rendered", out_path, len(data), "bytes")

os.makedirs(os.path.join(OUTPUT_ROOT, "round-03"), exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# 计算对比度（白色背景 #FFFFFF，不同文字颜色）
bg_rgb = hex_to_rgb(DESIGN_TOKENS["bg_color"])
bg_L = relative_luminance(*bg_rgb)

contrast_samples = []
for label, color_hex in [
    ("主标题 #111827", DESIGN_TOKENS["title_color"]),
    ("正文 #64748B", DESIGN_TOKENS["body_color"]),
    ("主色文字 #2563EB", DESIGN_TOKENS["primary_color"]),
    ("标签文字 #2563EB", DESIGN_TOKENS["primary_color"]),
    ("英文句 #2563EB", DESIGN_TOKENS["primary_color"]),
    ("赞助方 #64748B", DESIGN_TOKENS["body_color"]),
]:
    fg_rgb = hex_to_rgb(color_hex)
    fg_L = relative_luminance(*fg_rgb)
    ratio = contrast_ratio(fg_L, bg_L)
    contrast_samples.append({
        "text": label,
        "foreground": color_hex,
        "background": DESIGN_TOKENS["bg_color"],
        "fg_luminance": round(fg_L, 6),
        "bg_luminance": round(bg_L, 6),
        "contrast_ratio": round(ratio, 4),
        "pass_4_5": ratio >= 4.5
    })

# 渲染竖海报
dsl_p = gen_portrait(1080, 1350, ROUND3_CONTENT, DESIGN_TOKENS)
dsl_path_p = os.path.join(TEMP_DIR, "round-03-launch-portrait.v1.snapshot")
with open(dsl_path_p, "w", encoding="utf-8") as f:
    f.write(dsl_p)
render(dsl_p, os.path.join(OUTPUT_ROOT, "round-03", "launch-portrait.png"))
with open(dsl_path_p, "r", encoding="utf-8") as f:
    with open(os.path.join(OUTPUT_ROOT, "round-03", "launch-portrait.snapshot"), "w", encoding="utf-8") as fo:
        fo.write(f.read())
print("Portrait DSL written")

# 渲染横屏
dsl_w = gen_wide(1440, 810, ROUND3_CONTENT, DESIGN_TOKENS)
dsl_path_w = os.path.join(TEMP_DIR, "round-03-launch-wide.v1.snapshot")
with open(dsl_path_w, "w", encoding="utf-8") as f:
    f.write(dsl_w)
render(dsl_w, os.path.join(OUTPUT_ROOT, "round-03", "launch-wide.png"))
with open(dsl_path_w, "r", encoding="utf-8") as f:
    with open(os.path.join(OUTPUT_ROOT, "round-03", "launch-wide.snapshot"), "w", encoding="utf-8") as fo:
        fo.write(f.read())
print("Wide DSL written")

# design-tokens.json
with open(os.path.join(OUTPUT_ROOT, "round-03", "design-tokens.json"), "w", encoding="utf-8") as f:
    json.dump(DESIGN_TOKENS, f, ensure_ascii=False, indent=2)
print("design-tokens.json written")

# content-map.json
content_map = {
    "round": 3,
    "canvas_sizes": {"portrait": [1080, 1350], "wide": [1440, 810]},
    "content": ROUND3_CONTENT,
    "design_tokens": DESIGN_TOKENS,
    "changes_from_round2": [
        "浅色主题（白色背景），普通文字与背景对比度≥4.5:1",
        "新增英语句：Clarity through structure (≥24px)",
        "保留全部第二轮文案和品牌图形",
        "赞助方信息保留"
    ]
}
with open(os.path.join(OUTPUT_ROOT, "round-03", "content-map.json"), "w", encoding="utf-8") as f:
    json.dump(content_map, f, ensure_ascii=False, indent=2)
print("content-map.json written")

# contrast-audit.json（每图至少6处）
contrast_audit = {
    "round": 3,
    "theme": "light",
    "background": DESIGN_TOKENS["bg_color"],
    "background_luminance": round(bg_L, 6),
    "contrast_threshold": 4.5,
    "calculation_method": "sRGB normalize → linearize → relative luminance → contrast ratio (WCAG)",
    "formula": "L = 0.2126*R_linear + 0.7152*G_linear + 0.0722*B_linear; contrast = (max(L1,L2)+0.05)/(min(L1,L2)+0.05)",
    "samples": contrast_samples,
    "all_pass": all(s["pass_4_5"] for s in contrast_samples),
    "notes": "所有文字颜色在白色背景上的对比度均超过4.5:1，满足Round 03要求。"
}
with open(os.path.join(OUTPUT_ROOT, "round-03", "contrast-audit.json"), "w", encoding="utf-8") as f:
    json.dump(contrast_audit, f, ensure_ascii=False, indent=2)
print("contrast-audit.json written")

print("Round 03 complete!")
