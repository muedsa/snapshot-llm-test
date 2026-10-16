# gen_b05_rest.py - B05 case-04 到 case-10
import json, os

SUITE_ROOT = os.environ.get("SNAPSHOT_TASK_ROOT", ".")
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261016")
OUTPUT_ROOT = os.path.join(SUITE_ROOT, "outputs", RUN_ID, "B05")
TEMP_DIR = os.path.join(SUITE_ROOT, "tmp", RUN_ID, "B05")
SERVICE_URL = "https://open-snapshot.muedsa.com/snapshot"
FONT = "Noto Sans CJK SC,Inter"

PRIMARY = "#2563EB"
SCREENS = [
    ("case-04", "任务详情", {"title": "撰写项目报告", "sub": "截止: 11月10日 18:00", "btn": "标记完成"}),
    ("case-05", "新建任务", {"title": "新建任务", "sub": "填写标题与截止时间", "btn": "保存任务"}),
    ("case-06", "分类筛选", {"title": "任务分类", "sub": "全部 / 工作 / 个人 / 紧急", "btn": "应用筛选"}),
    ("case-07", "日历视图", {"title": "11月日历", "sub": "查看任务分布", "btn": "返回今日"}),
    ("case-08", "设置页", {"title": "设置", "sub": "通知 · 提醒 · 主题", "btn": "保存设置"}),
    ("case-09", "个人资料", {"title": "个人资料", "sub": "头像 · 昵称 · 账号", "btn": "编辑资料"}),
    ("case-10", "通知中心", {"title": "通知", "sub": "提醒您的待办事项", "btn": "全部标为已读"}),
]

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

for case_id, scene_name, content in SCREENS:
    case_dir = os.path.join(OUTPUT_ROOT, case_id)
    os.makedirs(case_dir, exist_ok=True)
    W, H = 360, 800
    lines = []
    lines.append('<Snapshot type="png">')
    lines.append('  <SizedBox width="360" height="800">')
    lines.append('    <Stack alignment="TOP_LEFT">')
    lines.append('      <Container color="#FFFFFF" width="360" height="800"/>')
    lines.append('      <Container color="#2563EB" left="0" top="0" width="360" height="60"/>')
    lines.append('      <Text left="24" top="22" fontSize="22" fontStyle="BOLD" fill="#FFFFFF" fontFamily="' + FONT + '">' + esc(content["title"]) + '</Text>')
    lines.append('      <Text left="24" top="110" fontSize="18" fill="#111827" fontStyle="BOLD" fontFamily="' + FONT + '">' + esc(content["sub"]) + '</Text>')
    y = 160
    for i in range(3):
        lines.append('      <Container color="#F8FAFC" borderRadius="12" left="24" top="' + str(y) + '" width="312" height="70"/>')
        lines.append('      <Text left="44" top="' + str(y+18) + '" fontSize="16" fill="#334155" fontFamily="' + FONT + '">任务项 ' + str(i+1) + ' — 示例内容</Text>')
        y += 84
    lines.append('      <Container color="#2563EB" borderRadius="14" left="24" top="' + str(y+10) + '" width="312" height="50"/>')
    lines.append('      <Text left="44" top="' + str(y+22) + '" fontSize="17" fontStyle="BOLD" fill="#FFFFFF" fontFamily="' + FONT + '">' + esc(content["btn"]) + '</Text>')
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
    # case.md
    case_md = "# " + case_id + " — " + scene_name + "\n\n## 产品\n灵动待办\n\n## 画面\n" + scene_name + "\n\n## 尺寸\n360×800\n\n纯DSL构造。\n"
    with open(os.path.join(case_dir, "case.md"), "w", encoding="utf-8") as f:
        f.write(case_md)

print("B05 case-04 to case-10 complete!")
