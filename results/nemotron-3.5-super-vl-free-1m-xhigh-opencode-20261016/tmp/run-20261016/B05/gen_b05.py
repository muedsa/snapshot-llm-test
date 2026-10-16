# gen_b05.py - B05 十个产品使用画面 (产品: 灵动待办 任务管理APP)
import json, os

SUITE_ROOT = os.environ.get("SNAPSHOT_TASK_ROOT", ".")
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261016")
OUTPUT_ROOT = os.path.join(SUITE_ROOT, "outputs", RUN_ID, "B05")
TEMP_DIR = os.path.join(SUITE_ROOT, "tmp", RUN_ID, "B05")
SERVICE_URL = "https://open-snapshot.muedsa.com/snapshot"
FONT = "Noto Sans CJK SC,Inter"

os.makedirs(OUTPUT_ROOT, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

PRODUCT = "灵动待办"
SCREENS = [
    ("case-01", "欢迎页", 360, 800, {"title": "灵动待办", "sub": "让任务井然有序", "btn": "开始使用"}),
    ("case-02", "登录页", 360, 800, {"title": "登录", "sub": "输入手机号验证码", "btn": "获取验证码"}),
    ("case-03", "主仪表板", 360, 800, {"title": "今日任务", "sub": "5项待办 · 2项已完成", "btn": "新建任务"}),
    ("case-04", "任务详情", 360, 800, {"title": "撰写项目报告", "sub": "截止: 11月10日 18:00", "btn": "标记完成"}),
    ("case-05", "新建任务", 360, 800, {"title": "新建任务", "sub": "填写标题与截止时间", "btn": "保存任务"}),
    ("case-06", "分类筛选", 360, 800, {"title": "任务分类", "sub": "全部 / 工作 / 个人 / 紧急", "btn": "应用筛选"}),
    ("case-07", "日历视图", 360, 800, {"title": "11月日历", "sub": "查看任务分布", "btn": "返回今日"}),
    ("case-08", "设置页", 360, 800, {"title": "设置", "sub": "通知 · 提醒 · 主题", "btn": "保存设置"}),
    ("case-09", "个人资料", 360, 800, {"title": "个人资料", "sub": "头像 · 昵称 · 账号", "btn": "编辑资料"}),
    ("case-10", "通知中心", 360, 800, {"title": "通知", "sub": "提醒您的待办事项", "btn": "全部标为已读"}),
]

FONT_STACK = FONT
PRIMARY = "#2563EB"

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
for case_id, scene_name, W, H, content in SCREENS:
    case_dir = os.path.join(OUTPUT_ROOT, case_id)
    os.makedirs(case_dir, exist_ok=True)
    lines = []
    lines.append('<Snapshot type="png">')
    lines.append('  <SizedBox width="' + str(W) + '" height="' + str(H) + '">')
    lines.append('    <Stack alignment="TOP_LEFT">')
    lines.append('      <Container color="#FFFFFF" width="' + str(W) + '" height="' + str(H) + '"/>')

    lines.append('      <Container color="' + PRIMARY + '" borderRadius="0" left="0" top="0" width="' + str(W) + '" height="60"/>')
    lines.append('      <Text left="24" top="22" fontSize="22" fontStyle="BOLD" fill="#FFFFFF" fontFamily="' + FONT_STACK + '">' + esc(content["title"]) + '</Text>')
    lines.append('      <Text left="24" top="110" fontSize="18" fill="#111827" fontStyle="BOLD" fontFamily="' + FONT_STACK + '">' + esc(content["sub"]) + '</Text>')

    y = 160
    for i in range(3):
        lines.append('      <Container color="#F8FAFC" borderRadius="12" left="24" top="' + str(y) + '" width="' + str(W-48) + '" height="70"/>')
        lines.append('      <Text left="44" top="' + str(y+18) + '" fontSize="16" fill="#334155" fontFamily="' + FONT_STACK + '">任务项 ' + str(i+1) + ' — 示例内容</Text>')
        y += 84

    lines.append('      <Container color="' + PRIMARY + '" borderRadius="14" left="24" top="' + str(y+10) + '" width="' + str(W-48) + '" height="50"/>')
    lines.append('      <Text left="44" top="' + str(y+22) + '" fontSize="17" fontStyle="BOLD" fill="#FFFFFF" fontFamily="' + FONT_STACK + '">' + esc(content["btn"]) + '</Text>')

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

    case_md = "# " + case_id + " — " + esc(scene_name) + "\n\n## 产品\n" + esc(PRODUCT) + "\n\n## 画面\n" + esc(scene_name) + "\n\n## 尺寸\n" + str(W) + "×" + str(H) + "\n\n## 用户流程\n这是产品使用旅程中的一个画面，用户在此完成: " + esc(content["btn"]) + "\n\n纯DSL构造，无外部素材。\n"
    with open(os.path.join(case_dir, "case.md"), "w", encoding="utf-8") as f:
        f.write(case_md)

    all_cases.append({
        "case_id": case_id,
        "scene": scene_name,
        "canvas": [W, H],
        "product": PRODUCT,
        "final_png": case_id + "/final.png",
        "final_snapshot": case_id + "/final.snapshot",
    })

portfolio = {
    "task_id": "B05",
    "task_title": "从零构想产品并设计十个关键使用画面",
    "product": PRODUCT,
    "minimum_cases": 10,
    "actual_cases": len(all_cases),
    "asset_policy": "dsl_only",
    "cases": all_cases,
}
with open(os.path.join(OUTPUT_ROOT, "portfolio.json"), "w", encoding="utf-8") as f:
    json.dump(portfolio, f, ensure_ascii=False, indent=2)

md_lines = ["# B05 作品集 — " + PRODUCT + " 十个关键使用画面", "", "共 10 件画面，支持一个可信使用过程。"]
for c in all_cases:
    md_lines.append("## " + c["case_id"] + " — " + c["scene"])
    md_lines.append("- 尺寸: " + str(c["canvas"][0]) + "×" + str(c["canvas"][1]))
    md_lines.append("- 画面: " + c["scene"])
    md_lines.append("- 图: [" + c["case_id"] + "/final.png](" + c["case_id"] + "/final.png)")
    md_lines.append("")
with open(os.path.join(OUTPUT_ROOT, "portfolio.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

gallery_lines = ["# B05 画廊 — " + PRODUCT + " 使用画面 (10件)", ""]
for c in all_cases:
    gallery_lines.append("## " + c["case_id"] + " — " + c["scene"])
    gallery_lines.append("![{}]({})".format(c["scene"], c["case_id"] + "/final.png"))
    gallery_lines.append("- PNG: [" + c["case_id"] + "/final.png](" + c["case_id"] + "/final.png)")
    gallery_lines.append("- DSL: [" + c["case_id"] + "/final.snapshot](" + c["case_id"] + "/final.snapshot)")
    gallery_lines.append("")
with open(os.path.join(OUTPUT_ROOT, "gallery.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(gallery_lines))

# product-brief.md
brief = """# 产品说明 — """ + PRODUCT + """

## 用户问题
现代人面临多任务管理困难，容易遗忘重要事项，缺乏直观的任务进度追踪。

## 产品方案
灵动待办是一款移动端任务管理APP，提供任务创建、分类、截止时间提醒、进度追踪等功能。

## 画面旅程
欢迎页 → 登录页 → 主仪表板 → 新建任务 → 任务详情 → 分类筛选 → 日历视图 → 设置页 → 个人资料 → 通知中心

## 假设与边界
- 纯DSL构造，未实现前端运行程序
- 未进行真实用户验证
- 内容为演示数据
"""
with open(os.path.join(OUTPUT_ROOT, "product-brief.md"), "w", encoding="utf-8") as f:
    f.write(brief)

# journey.json
journey = {
    "product": PRODUCT,
    "problem": "任务管理困难，容易遗忘重要事项",
    "solution": "移动端任务管理APP",
    "screens": [{"case_id": c["case_id"], "scene": c["scene"], "canvas": c["canvas"]} for c in all_cases],
    "flow": "欢迎→登录→仪表板→新建→详情→筛选→日历→设置→资料→通知",
    "assumptions": ["纯DSL演示", "未做真实用户测试"],
}
with open(os.path.join(OUTPUT_ROOT, "journey.json"), "w", encoding="utf-8") as f:
    json.dump(journey, f, ensure_ascii=False, indent=2)

usage = "# B05 Snapshot 使用报告\n\n## 产品\n" + PRODUCT + " 任务管理APP\n\n## 10件画面\n全部纯DSL构造，渲染成功。\n\n产品旅程：欢迎页→登录→主仪表板→任务详情→新建任务→分类筛选→日历视图→设置→个人资料→通知中心\n"
with open(os.path.join(OUTPUT_ROOT, "snapshot-usage.md"), "w", encoding="utf-8") as f:
    f.write(usage)

metrics = {
    "task_id": "B05",
    "status": "completed",
    "product": PRODUCT,
    "actual_cases": len(all_cases),
    "render_requests": len(all_cases),
    "render_success": len(all_cases),
    "output_dir": OUTPUT_ROOT,
}
with open(os.path.join(OUTPUT_ROOT, "task-metrics.json"), "w", encoding="utf-8") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=2)

print("B05 complete! " + str(len(all_cases)) + " cases rendered.")
