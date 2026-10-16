# gen_a21_round1.py - 生成 A21 Round 01 的两张发布海报
import json, os

SUITE_ROOT = os.environ.get("SNAPSHOT_TASK_ROOT", ".")
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261016")
OUTPUT_ROOT = os.path.join(SUITE_ROOT, "outputs", RUN_ID, "A21")
TEMP_DIR = os.path.join(SUITE_ROOT, "tmp", RUN_ID, "A21")
SERVICE_URL = "https://open-snapshot.muedsa.com/snapshot"
FONT = "Noto Sans CJK SC,Inter"

# 设计令牌
DESIGN_TOKENS = {
    "primary_color": "#2563EB",
    "bg_color": "#FFFFFF",
    "title_color": "#111827",
    "body_color": "#64748B",
    "accent_color": "#DC2626",
    "brand_colors": ["#2563EB", "#EF4444", "#10B981", "#F59E0B", "#8B5CF6"],
    "title_font_size": 56,
    "body_font_size": 24,
    "brand_components": 5
}

# Round 01 内容
ROUND1_CONTENT = {
    "title": "让复杂信息变得清晰",
    "datetime": "2026.11.07 19:30",
    "label": "ONLINE LAUNCH",
    "speakers": "讲者：林川 / 苏言",
    "website": "layerlight.example.org",
    "brand_name": "叠光 Layerlight"
}

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def gen_portrait(W, H, content, tokens, round_id):
    """生成竖海报 DSL"""
    lines = []
    lines.append('<Snapshot type="png">')
    lines.append('  <SizedBox width="' + str(W) + '" height="' + str(H) + '">')
    lines.append('    <Stack alignment="TOP_LEFT">')
    lines.append('      <Container color="' + tokens["bg_color"] + '" width="' + str(W) + '" height="' + str(H) + '"/>')

    # 顶部扩展空间（不写文字）
    lines.append('      <Container color="' + tokens["bg_color"] + '" left="0" top="0" width="' + str(W) + '" height="120"/>')

    # 品牌图形（5个构件）- 顶部区域
    cx = W // 2
    lines.append('      <Container color="' + tokens["brand_colors"][0] + '" borderRadius="24" left="' + str(cx-60) + '" top="140" width="48" height="48"/>')
    lines.append('      <Container color="' + tokens["brand_colors"][1] + '" borderRadius="12" left="' + str(cx-10) + '" top="150" width="24" height="24"/>')
    lines.append('      <Container color="' + tokens["brand_colors"][2] + '" borderRadius="8" left="' + str(cx+40) + '" top="170" width="32" height="16"/>')
    lines.append('      <Container color="' + tokens["brand_colors"][3] + '" borderRadius="4" left="' + str(cx-40) + '" top="180" width="16" height="16"/>')
    lines.append('      <Container color="' + tokens["brand_colors"][4] + '" borderRadius="6" left="' + str(cx+10) + '" top="190" width="20" height="20"/>')

    # ONLINE LAUNCH 标签
    lines.append('      <Container color="#F0F7FF" borderRadius="20" left="' + str(cx-90) + '" top="260" width="180" height="40"/>')
    lines.append('      <Text left="' + str(cx-70) + '" top="272" fontSize="20" fill="' + tokens["primary_color"] + '" fontStyle="BOLD" fontFamily="' + FONT + '">' + esc(content["label"]) + '</Text>')

    # 主标题 (≥56px)
    lines.append('      <Text left="80" top="330" width="' + str(W-160) + '" fontSize="' + str(tokens["title_font_size"]) + '" fontStyle="BOLD" fill="' + tokens["title_color"] + '" fontFamily="' + FONT + '">' + esc(content["title"]) + '</Text>')

    # 日期时间
    lines.append('      <Text left="80" top="420" fontSize="' + str(tokens["body_font_size"]) + '" fill="' + tokens["body_color"] + '" fontFamily="' + FONT + '">' + esc(content["datetime"]) + '</Text>')

    # 讲者
    lines.append('      <Text left="80" top="455" fontSize="' + str(tokens["body_font_size"]) + '" fill="' + tokens["body_color"] + '" fontFamily="' + FONT + '">' + esc(content["speakers"]) + '</Text>')

    # 网址
    lines.append('      <Text left="80" top="490" fontSize="' + str(tokens["body_font_size"]) + '" fill="' + tokens["primary_color"] + '" fontStyle="BOLD" fontFamily="' + FONT + '">' + esc(content["website"]) + '</Text>')

    # 装饰线
    lines.append('      <Container color="' + tokens["primary_color"] + '" left="80" top="530" width="60" height="3"/>')

    # 底部扩展空间
    lines.append('      <Container color="' + tokens["bg_color"] + '" left="0" top="' + str(H-100) + '" width="' + str(W) + '" height="100"/>')

    lines.append('    </Stack>')
    lines.append('  </SizedBox>')
    lines.append('</Snapshot>')
    return "\n".join(lines)

def gen_wide(W, H, content, tokens, round_id):
    """生成横屏 DSL"""
    lines = []
    lines.append('<Snapshot type="png">')
    lines.append('  <SizedBox width="' + str(W) + '" height="' + str(H) + '">')
    lines.append('    <Stack alignment="TOP_LEFT">')
    lines.append('      <Container color="' + tokens["bg_color"] + '" width="' + str(W) + '" height="' + str(H) + '"/>')

    # 顶部扩展空间
    lines.append('      <Container color="' + tokens["bg_color"] + '" left="0" top="0" width="' + str(W) + '" height="60"/>')

    # 左侧品牌图形（5个构件）
    lx = 80
    lines.append('      <Container color="' + tokens["brand_colors"][0] + '" borderRadius="24" left="' + str(lx) + '" top="100" width="48" height="48"/>')
    lines.append('      <Container color="' + tokens["brand_colors"][1] + '" borderRadius="12" left="' + str(lx+60) + '" top="110" width="24" height="24"/>')
    lines.append('      <Container color="' + tokens["brand_colors"][2] + '" borderRadius="8" left="' + str(lx+100) + '" top="130" width="32" height="16"/>')
    lines.append('      <Container color="' + tokens["brand_colors"][3] + '" borderRadius="4" left="' + str(lx+40) + '" top="140" width="16" height="16"/>')
    lines.append('      <Container color="' + tokens["brand_colors"][4] + '" borderRadius="6" left="' + str(lx+80) + '" top="150" width="20" height="20"/>')

    # ONLINE LAUNCH 标签
    lines.append('      <Container color="#F0F7FF" borderRadius="20" left="' + str(lx) + '" top="200" width="160" height="36"/>')
    lines.append('      <Text left="' + str(lx+20) + '" top="210" fontSize="20" fill="' + tokens["primary_color"] + '" fontStyle="BOLD" fontFamily="' + FONT + '">' + esc(content["label"]) + '</Text>')

    # 主标题 (≥56px)
    lines.append('      <Text left="' + str(lx) + '" top="260" width="520" fontSize="' + str(tokens["title_font_size"]) + '" fontStyle="BOLD" fill="' + tokens["title_color"] + '" fontFamily="' + FONT + '">' + esc(content["title"]) + '</Text>')

    # 日期时间、讲者、网址（右侧）
    rx = 700
    lines.append('      <Text left="' + str(rx) + '" top="120" fontSize="' + str(tokens["body_font_size"]) + '" fill="' + tokens["body_color"] + '" fontFamily="' + FONT + '">' + esc(content["datetime"]) + '</Text>')
    lines.append('      <Text left="' + str(rx) + '" top="155" fontSize="' + str(tokens["body_font_size"]) + '" fill="' + tokens["body_color"] + '" fontFamily="' + FONT + '">' + esc(content["speakers"]) + '</Text>')
    lines.append('      <Text left="' + str(rx) + '" top="190" fontSize="' + str(tokens["body_font_size"]) + '" fill="' + tokens["primary_color"] + '" fontStyle="BOLD" fontFamily="' + FONT + '">' + esc(content["website"]) + '</Text>')

    # 装饰线
    lines.append('      <Container color="' + tokens["primary_color"] + '" left="' + str(lx) + '" top="360" width="80" height="3"/>')

    # 底部扩展空间
    lines.append('      <Container color="' + tokens["bg_color"] + '" left="0" top="' + str(H-60) + '" width="' + str(W) + '" height="60"/>')

    lines.append('    </Stack>')
    lines.append('  </SizedBox>')
    lines.append('</Snapshot>')
    return "\n".join(lines)

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

os.makedirs(os.path.join(OUTPUT_ROOT, "round-01"), exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# 生成 Round 01 竖海报
dsl_p = gen_portrait(1080, 1350, ROUND1_CONTENT, DESIGN_TOKENS, "round-01")
dsl_path_p = os.path.join(TEMP_DIR, "round-01-launch-portrait.v1.snapshot")
with open(dsl_path_p, "w", encoding="utf-8") as f:
    f.write(dsl_p)
render(dsl_p, os.path.join(OUTPUT_ROOT, "round-01", "launch-portrait.png"))
with open(dsl_path_p, "r", encoding="utf-8") as f:
    dsl_content_p = f.read()
with open(os.path.join(OUTPUT_ROOT, "round-01", "launch-portrait.snapshot"), "w", encoding="utf-8") as f:
    f.write(dsl_content_p)
print("Portrait DSL written")

# 生成 Round 01 横屏
dsl_w = gen_wide(1440, 810, ROUND1_CONTENT, DESIGN_TOKENS, "round-01")
dsl_path_w = os.path.join(TEMP_DIR, "round-01-launch-wide.v1.snapshot")
with open(dsl_path_w, "w", encoding="utf-8") as f:
    f.write(dsl_w)
render(dsl_w, os.path.join(OUTPUT_ROOT, "round-01", "launch-wide.png"))
with open(dsl_path_w, "r", encoding="utf-8") as f:
    dsl_content_w = f.read()
with open(os.path.join(OUTPUT_ROOT, "round-01", "launch-wide.snapshot"), "w", encoding="utf-8") as f:
    f.write(dsl_content_w)
print("Wide DSL written")

# 写入 design-tokens.json
with open(os.path.join(OUTPUT_ROOT, "round-01", "design-tokens.json"), "w", encoding="utf-8") as f:
    json.dump(DESIGN_TOKENS, f, ensure_ascii=False, indent=2)
print("design-tokens.json written")

# 写入 content-map.json
content_map = {
    "round": 1,
    "canvas_sizes": {"portrait": [1080, 1350], "wide": [1440, 810]},
    "content": ROUND1_CONTENT,
    "design_tokens": DESIGN_TOKENS,
    "fields": {
        "title": {"size": DESIGN_TOKENS["title_font_size"], "color": DESIGN_TOKENS["title_color"]},
        "datetime": {"size": DESIGN_TOKENS["body_font_size"], "color": DESIGN_TOKENS["body_color"]},
        "label": {"size": DESIGN_TOKENS["body_font_size"], "color": DESIGN_TOKENS["primary_color"]},
        "speakers": {"size": DESIGN_TOKENS["body_font_size"], "color": DESIGN_TOKENS["body_color"]},
        "website": {"size": DESIGN_TOKENS["body_font_size"], "color": DESIGN_TOKENS["primary_color"]}
    }
}
with open(os.path.join(OUTPUT_ROOT, "round-01", "content-map.json"), "w", encoding="utf-8") as f:
    json.dump(content_map, f, ensure_ascii=False, indent=2)
print("content-map.json written")

print("Round 01 complete!")
