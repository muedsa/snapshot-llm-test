# 最终审查脚本
import json, os

SUITE_ROOT = os.environ.get("SNAPSHOT_TASK_ROOT", ".")
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261016")
OUTPUTS = os.path.join(SUITE_ROOT, "outputs", RUN_ID)
SUITE_DIR = os.path.join(OUTPUTS, "_suite")

print("=" * 60)
print("最终审查 - Snapshot 全套任务")
print("=" * 60)

# 1. suite-state.json
state_path = os.path.join(SUITE_DIR, "suite-state.json")
with open(state_path, "r", encoding="utf-8") as f:
    state = json.load(f)
tasks = state["tasks"]
completed = [t for t in tasks if t["status"] == "completed"]
pending = [t for t in tasks if t["status"] != "completed"]
print(f"\n任务状态: {len(completed)}/30 完成")
if pending:
    print("  待完成:", [t["id"] for t in pending])
else:
    print("  所有30任务均已完成 ✓")

# 2. 总交付文件
suite_files = ["index.md", "gallery.md", "snapshot-usage.md", "task-metrics.json", "suite-state.json"]
print(f"\n总交付文件 (_suite/):")
for f in suite_files:
    path = os.path.join(SUITE_DIR, f)
    exists = os.path.exists(path)
    print(f"  {f}: {'存在' if exists else '缺失!'} {'✓' if exists else '✗'}")

# 3. .gitignore
gitignore = os.path.join(SUITE_ROOT, ".gitignore")
print(f"\n.gitignore: {'存在' if os.path.exists(gitignore) else '缺失!'}")

# 4. 每个任务产物完整性
print(f"\n各任务产物检查:")
all_ok = True
for t in tasks:
    tid = t["id"]
    out_dir = os.path.join(OUTPUTS, tid)
    if not os.path.isdir(out_dir):
        print(f"  {tid}: 目录缺失 ✗")
        all_ok = False
        continue
    files = os.listdir(out_dir)
    pngs = [f for f in files if f.endswith(".png")]
    snaps = [f for f in files if f.endswith(".snapshot")]
    # 检查 PNG 和 snapshot 配对
    for p in pngs:
        snap = p[:-4] + ".snapshot"
        if snap not in files:
            print(f"  {tid}: {p} 缺少对应 .snapshot ✗")
            all_ok = False
    if t["id"].startswith("B"):
        cases = [d for d in files if d.startswith("case-") and os.path.isdir(os.path.join(out_dir, d))]
        print(f"  {tid}: {len(cases)} 个案例, {len(pngs)} 张PNG")
    elif t["id"] in ["A21", "A22"]:
        rounds = [d for d in files if d.startswith("round-")]
        print(f"  {tid}: {len(rounds)} 轮, {len(pngs)} 张PNG")
    else:
        print(f"  {tid}: {len(pngs)} 张PNG, {len(snaps)} 张DSL ✓")

if all_ok:
    print("\n  所有 PNG 与 .snapshot 配对完整 ✓")

# 5. B 类作品数量
b_cases = 0
for t in tasks:
    if t["id"].startswith("B"):
        out_dir = os.path.join(OUTPUTS, t["id"])
        cases = [d for d in os.listdir(out_dir) if d.startswith("case-") and os.path.isdir(os.path.join(out_dir, d))]
        b_cases += len(cases)
print(f"\nB 类作品总数: {b_cases} 件 (要求 ≥60) {'✓' if b_cases >= 60 else '✗ 不足'}")

# 6. A21/A22 轮次
for tid in ["A21", "A22"]:
    out_dir = os.path.join(OUTPUTS, tid)
    rounds = [d for d in os.listdir(out_dir) if d.startswith("round-") and os.path.isdir(os.path.join(out_dir, d))]
    print(f"  {tid}: {len(rounds)} 轮 (要求 3) {'✓' if len(rounds) >= 3 else '✗'}")

print("\n" + "=" * 60)
print("最终审查完成")
print("=" * 60)
