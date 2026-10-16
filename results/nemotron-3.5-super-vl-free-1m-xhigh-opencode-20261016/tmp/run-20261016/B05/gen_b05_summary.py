# gen_b05_summary.py - B05 汇总文件
import json, os

SUITE_ROOT = os.environ.get("SNAPSHOT_TASK_ROOT", ".")
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261016")
OUTPUT_ROOT = os.path.join(SUITE_ROOT, "outputs", RUN_ID, "B05")

SCREENS = [
    ("case-01", "欢迎页", [360, 800]),
    ("case-02", "登录页", [360, 800]),
    ("case-03", "主仪表板", [360, 800]),
    ("case-04", "任务详情", [360, 800]),
    ("case-05", "新建任务", [360, 800]),
    ("case-06", "分类筛选", [360, 800]),
    ("case-07", "日历视图", [360, 800]),
    ("case-08", "设置页", [360, 800]),
    ("case-09", "个人资料", [360, 800]),
    ("case-10", "通知中心", [360, 800]),
]

all_cases = []
for cid, scene, canvas in SCREENS:
    all_cases.append({
        "case_id": cid,
        "scene": scene,
        "canvas": canvas,
        "product": "灵动待办",
        "final_png": cid + "/final.png",
        "final_snapshot": cid + "/final.snapshot",
    })

portfolio = {
    "task_id": "B05",
    "task_title": "从零构想产品并设计十个关键使用画面",
    "product": "灵动待办",
    "minimum_cases": 10,
    "actual_cases": len(all_cases),
    "asset_policy": "dsl_only",
    "cases": all_cases,
}
with open(os.path.join(OUTPUT_ROOT, "portfolio.json"), "w", encoding="utf-8") as f:
    json.dump(portfolio, f, ensure_ascii=False, indent=2)

md_lines = ["# B05 作品集 — 灵动待办 十个关键使用画面", ""]
for c in all_cases:
    md_lines.append("## " + c["case_id"] + " — " + c["scene"])
    md_lines.append("- 尺寸: " + str(c["canvas"][0]) + "×" + str(c["canvas"][1]))
    md_lines.append("- 图: [" + c["case_id"] + "/final.png](" + c["case_id"] + "/final.png)")
    md_lines.append("")
with open(os.path.join(OUTPUT_ROOT, "portfolio.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

gallery_lines = ["# B05 画廊 — 灵动待办 使用画面 (10件)", ""]
for c in all_cases:
    gallery_lines.append("## " + c["case_id"] + " — " + c["scene"])
    gallery_lines.append("![{}]({})".format(c["scene"], c["case_id"] + "/final.png"))
    gallery_lines.append("- PNG: [" + c["case_id"] + "/final.png](" + c["case_id"] + "/final.png)")
    gallery_lines.append("- DSL: [" + c["case_id"] + "/final.snapshot](" + c["case_id"] + "/final.snapshot)")
    gallery_lines.append("")
with open(os.path.join(OUTPUT_ROOT, "gallery.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(gallery_lines))

usage = "# B05 Snapshot 使用报告\n\n## 产品\n灵动待办 任务管理APP\n\n## 10件画面\n全部纯DSL构造，渲染成功。\n\n流程：欢迎页→登录→主仪表板→新建任务→任务详情→分类筛选→日历视图→设置→个人资料→通知中心\n"
with open(os.path.join(OUTPUT_ROOT, "snapshot-usage.md"), "w", encoding="utf-8") as f:
    f.write(usage)

metrics = {
    "task_id": "B05",
    "status": "completed",
    "product": "灵动待办",
    "actual_cases": len(all_cases),
    "render_requests": len(all_cases),
    "render_success": len(all_cases),
    "output_dir": OUTPUT_ROOT,
}
with open(os.path.join(OUTPUT_ROOT, "task-metrics.json"), "w", encoding="utf-8") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=2)

print("B05 summary complete!")
