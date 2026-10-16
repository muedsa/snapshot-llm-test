# gen_b02.py - B02 一个自选项目的视觉生态 (10件)
import json, os

SUITE_ROOT = os.environ.get("SNAPSHOT_TASK_ROOT", ".")
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261016")
OUTPUT_ROOT = os.path.join(SUITE_ROOT, "outputs", RUN_ID, "B02")
TEMP_DIR = os.path.join(SUITE_ROOT, "tmp", RUN_ID, "B02")
SERVICE_URL = "https://open-snapshot.muedsa.com/snapshot"
FONT = "Noto Sans CJK SC,Inter"

os.makedirs(OUTPUT_ROOT, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

PROJECT = "绿叶社区图书馆"
PROJECT_EN = "Green Leaf Community Library"

TOUCHPOINTS = [
    ("case-01", "外墙招牌", 1000, 400, {"main": PROJECT_EN, "sub": "Community Hub", "cta": "开放时间 9:00-21:00"}),
    ("case-02", "会员卡", 850, 540, {"main": "会员卡", "sub": PROJECT_EN, "cta": "卡号: GL-2026-001"}),
    ("case-03", "借阅收据", 300, 500, {"main": "借阅凭条", "sub": PROJECT_EN, "cta": "3本书 · 30天 · 免费"}),
    ("case-04", "活动海报", 600, 800, {"main": "绿叶读书会", "sub": "每周六 14:00", "cta": "免费参与 · 名额有限"}),
    ("case-05", "图书书签", 150, 550, {"main": "绿叶", "sub": "READ • GROW • SHARE", "cta": "归还日期: ___/__/__"}),
    ("case-06", "还书提醒卡片", 400, 250, {"main": "还书提醒", "sub": PROJECT_EN, "cta": "请于 11月20日 前归还"}),
    ("case-07", "志愿者胸卡", 350, 220, {"main": "志愿者", "sub": PROJECT_EN, "cta": "编号: VOL-07 · 工作时段 10:00-16:00"}),
    ("case-08", "捐赠箱贴纸", 300, 300, {"main": "爱心捐赠", "sub": "支持社区图书馆", "cta": "扫码捐赠 · 任何金额"}),
    ("case-09", "社区公告板模板", 700, 500, {"main": "社区公告", "sub": PROJECT_EN, "cta": "张贴时间: ___ · 联系: ___"}),
    ("case-10", "手机小程序界面", 375, 812, {"main": "绿叶图书馆", "sub": "小程序", "cta": "搜索图书 · 预约座位 · 续借"}),
]

FONT_STACK = FONT
PRIMARY = "#16653A"
ACCENT = "#D97706"

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

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

all_cases = []
for case_id, scene_name, W, H, content in TOUCHPOINTS:
    case_dir = os.path.join(OUTPUT_ROOT, case_id)
    os.makedirs(case_dir, exist_ok=True)
    lines = []
    lines.append('<Snapshot type="png">')
    lines.append('  <SizedBox width="' + str(W) + '" height="' + str(H) + '">')
    lines.append('    <Stack alignment="TOP_LEFT">')
    lines.append('      <Container color="#F0FDF4" width="' + str(W) + '" height="' + str(H) + '"/>')
    lines.append('      <Container color="' + PRIMARY + '" borderRadius="12" left="0" top="0" width="' + str(W) + '" height="70"/>')
    lines.append('      <Text left="20" top="22" fontSize="22" fontStyle="BOLD" fill="#FFFFFF" fontFamily="' + FONT_STACK + '">' + esc(content["main"]) + '</Text>')
    lines.append('      <Text left="20" top="50" fontSize="14" fill="#D1FAE5" fontFamily="' + FONT_STACK + '">' + esc(content["sub"]) + '</Text>')
    y = 100
    for item in [content["cta"]]:
        lines.append('      <Text left="20" top="' + str(y) + '" fontSize="18" fill="#111827" fontStyle="BOLD" fontFamily="' + FONT_STACK + '">' + esc(item) + '</Text>')
    lines.append('      <Container color="' + ACCENT + '" borderRadius="8" left="20" top="' + str(y+40) + '" width="' + str(W-40) + '" height="40"/>')
    lines.append('      <Text left="40" top="' + str(y+52) + '" fontSize="16" fill="#FFFFFF" fontStyle="BOLD" fontFamily="' + FONT_STACK + '">点击查看详情</Text>')
    lines.append('    </Stack>')
    lines.append('  </SizedBox>')
    lines.append('</Snapshot>')
    dsl = "\n".join(lines)
    dsl_path = os.path.join(TEMP_DIR, case_id + ".v1.snapshot")
    with open(dsl_path, "w", encoding="utf-8") as f:
        f.write(dsl)
    render(dsl, os.path.join(case_dir, "final.png"))
    with open(dsl_path, "r", encoding="utf-8") as f:
        with open(os.path.join(case_dir, "final.snapshot"), "w", encoding="utf-8") as fo:
            fo.write(f.read())
    case_md = "# " + case_id + " — " + esc(scene_name) + "\n\n## 项目\n" + esc(PROJECT) + "\n\n## 触点\n" + esc(scene_name) + "\n\n## 尺寸\n" + str(W) + "×" + str(H) + "\n\n## 视觉\n主色: " + PRIMARY + " · 强调色: " + ACCENT + "\n\n纯DSL构造，无外部素材。\n"
    with open(os.path.join(case_dir, "case.md"), "w", encoding="utf-8") as f:
        f.write(case_md)
    all_cases.append({
        "case_id": case_id,
        "scene": scene_name,
        "canvas": [W, H],
        "project": PROJECT,
        "final_png": case_id + "/final.png",
        "final_snapshot": case_id + "/final.snapshot",
    })

portfolio = {
    "task_id": "B02",
    "task_title": "为一个自选项目设计完整视觉生态",
    "project": PROJECT,
    "project_en": PROJECT_EN,
    "minimum_cases": 10,
    "actual_cases": len(all_cases),
    "asset_policy": "dsl_only",
    "cases": all_cases,
}
with open(os.path.join(OUTPUT_ROOT, "portfolio.json"), "w", encoding="utf-8") as f:
    json.dump(portfolio, f, ensure_ascii=False, indent=2)

md_lines = ["# B02 作品集 — " + PROJECT + " 视觉生态", "", "共 10 件触点作品。"]
for c in all_cases:
    md_lines.append("## " + c["case_id"] + " — " + c["scene"])
    md_lines.append("- 尺寸: " + str(c["canvas"][0]) + "×" + str(c["canvas"][1]))
    md_lines.append("- 触点: " + c["scene"])
    md_lines.append("- 图: [" + c["case_id"] + "/final.png](" + c["case_id"] + "/final.png)")
    md_lines.append("")
with open(os.path.join(OUTPUT_ROOT, "portfolio.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

gallery_lines = ["# B02 画廊 — " + PROJECT + " 视觉生态 (10件)", ""]
for c in all_cases:
    gallery_lines.append("## " + c["case_id"] + " — " + c["scene"])
    gallery_lines.append("![{}]({})".format(c["scene"], c["case_id"] + "/final.png"))
    gallery_lines.append("- PNG: [" + c["case_id"] + "/final.png](" + c["case_id"] + "/final.png)")
    gallery_lines.append("- DSL: [" + c["case_id"] + "/final.snapshot](" + c["case_id"] + "/final.snapshot)")
    gallery_lines.append("")
with open(os.path.join(OUTPUT_ROOT, "gallery.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(gallery_lines))

# project-brief.md
brief = """# 项目说明 — """ + PROJECT + """

## 项目问题
社区图书馆缺乏统一的视觉识别系统，用户在不同接触点（外墙、会员卡、收据、海报等）上难以快速识别图书馆品牌。

## 解决方案
为绿叶社区图书馆设计一套10件作品的视觉生态，涵盖线下和线上所有主要触点。

## 视觉系统
- 主色: """ + PRIMARY + " (森林绿)" + """
- 强调色: """ + ACCENT + " (麦穗橙)" + """
- 背景: #F0FDF4 (浅绿)
- 字体: """ + FONT_STACK + """

## 触点清单
""" + "\n".join("- " + c["scene"] + " (" + str(c["canvas"][0]) + "×" + str(c["canvas"][1]) + ")" for c in all_cases) + """

## 假设与边界
- 纯DSL构造，无外部图片
- 未进行真实用户测试
"""
with open(os.path.join(OUTPUT_ROOT, "project-brief.md"), "w", encoding="utf-8") as f:
    f.write(brief)

# design-system.json
ds = {
    "project": PROJECT,
    "primary_color": PRIMARY,
    "accent_color": ACCENT,
    "bg_color": "#F0FDF4",
    "font": FONT_STACK,
    "components": ["header_bar", "cta_button", "body_text"],
}
with open(os.path.join(OUTPUT_ROOT, "design-system.json"), "w", encoding="utf-8") as f:
    json.dump(ds, f, ensure_ascii=False, indent=2)

# touchpoint-map.json
tm = {
    "project": PROJECT,
    "touchpoints": [{"case_id": c["case_id"], "scene": c["scene"], "canvas": c["canvas"]} for c in all_cases],
}
with open(os.path.join(OUTPUT_ROOT, "touchpoint-map.json"), "w", encoding="utf-8") as f:
    json.dump(tm, f, ensure_ascii=False, indent=2)

usage = "# B02 Snapshot 使用报告\n\n## 项目\n" + PROJECT + "\n\n## 10件触点\n" + "\n".join("- " + c["case_id"] + ": " + c["scene"] + " (" + str(c["canvas"][0]) + "×" + str(c["canvas"][1]) + ")" for c in all_cases) + "\n\n纯DSL构造，所有作品渲染成功。\n"
with open(os.path.join(OUTPUT_ROOT, "snapshot-usage.md"), "w", encoding="utf-8") as f:
    f.write(usage)

metrics = {
    "task_id": "B02",
    "status": "completed",
    "project": PROJECT,
    "actual_cases": len(all_cases),
    "render_requests": len(all_cases),
    "render_success": len(all_cases),
    "output_dir": OUTPUT_ROOT,
}
with open(os.path.join(OUTPUT_ROOT, "task-metrics.json"), "w", encoding="utf-8") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=2)

print("B02 complete! " + str(len(all_cases)) + " cases rendered.")
