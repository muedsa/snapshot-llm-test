import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suitekit as s

run_id, _, _ = s.init_suite()
state_path = s.ROOT / s.CONFIG["output_root"] / run_id / "_suite" / "suite-state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
completed = [task["id"] for task in state["tasks"] if task["status"] == "completed"]

rechecks = {
    "A01": (
        "operations.png",
        "无视觉缺陷；四 KPI、三张图、六行表和管理结论清晰可读，末月标签完整。",
        "逐月重算净收入、利润、退款率、转化率及汇总，核对零起点、独立单位和管理结论引用。",
    ),
    "A03": (
        "system-pulse.png",
        "无视觉缺陷；1280×800、三指标、LIVE、REVIEW、背景模糊卡片和安全边距均符合要求。",
        "核对七类修复、原稿首次失败、逐版本证据、旋转角度、透明底与卡内/卡外模糊差异。",
    ),
    "A04": (
        "conversion-story.png",
        "无视觉缺陷；1600×1000、三组证据、六行核对表、结论与因果限制清晰可读。",
        "逐行复算四组率、两期加权总率、80/20 与 20/80 构成及 9.4 个百分点变化，核对共用零起点和等长构成图。",
    ),
    "A05": (
        "sensor-report.png",
        "无视觉缺陷；1440×1000、三联趋势、12 时点表、缺测图例和负压实测点说明完整可读。",
        "核对 33 个有效采样、真实分钟比例、null 两侧断线、三个负压实测点、独立纵轴和观测范围。",
    ),
    "A06": (
        "dependency-map.png",
        "无视觉缺陷；1600×1000、14 节点、16 条先决边、2 条反馈边和两条中文反馈语义完整清晰。",
        "重算拓扑层和 11 节点最长路径，核对反馈不参与 DAG、方向箭头、绕行及无连接点交叉。",
    ),
    "A07": (
        "network-map.png",
        "无视觉缺陷；1600×1000 全网图与 720×1280 路线卡的 16 站、三线、换乘和无障碍替代均清晰可读。",
        "独立打开两张最终图，复核 Q1=6/1、Q2 普通 6/1 与无障碍 6/2、Q3=4/1，核对 S05 不可换乘及 S08/S04 替代换乘。",
    ),
    "A08": (
        "wayfinding.png",
        "无视觉缺陷；1560×1080 展馆网格、双路线、共享通道、方向箭头、地标、侧栏与图例完整清晰。",
        "独立打开最终图并核对 paths.json：26×16、44px 方格、R1=35步/70米、R2=47步/94米、共享9+8步、唯一最短和四邻接。",
    ),
}

for task_id, (filename, observed, compared) in rechecks.items():
    if task_id not in completed:
        continue
    output, temp = s.task_dirs(run_id, task_id)
    version_id = "independent-final-recheck"
    log_path = temp / "iterations.jsonl"
    existing = s.read_jsonl(log_path)
    kept, duplicates, seen = [], [], False
    for item in existing:
        if item.get("version_id") == version_id:
            if seen:
                duplicates.append(item)
            else:
                kept.append(item)
                seen = True
        else:
            kept.append(item)
    if duplicates:
        correction_dir = temp / "log-corrections"
        correction_dir.mkdir(parents=True, exist_ok=True)
        backup = correction_dir / f"duplicate-rechecks-{s.now().strftime('%H%M%S%f')}.jsonl"
        backup.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in duplicates), encoding="utf-8")
        replacement = log_path.with_suffix(".jsonl.tmp")
        replacement.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in kept), encoding="utf-8")
        replacement.replace(log_path)
        print(json.dumps({"task_id": task_id, "archived_duplicate_rechecks": s.rel(backup)}, ensure_ascii=False))
    if not seen:
        s.record_iteration(
            run_id, task_id, version_id, output / filename,
            "audit_visual_recheck", observed,
            "仅独立复核，不改动最终 PNG、DSL 或业务审计。", compared,
        )

for task_id in completed:
    result = s.metrics(run_id, task_id)
    print(json.dumps({
        "task_id": task_id,
        "status": result["status"],
        "image_views": result["image_views"],
        "completed_visual_iterations": result["completed_visual_iterations"],
        "incomplete_visual_iterations": result["incomplete_visual_iterations"],
        "alternative_visual_iterations": result["alternative_visual_iterations"],
        "syntax_or_retry_iterations": result["syntax_or_retry_iterations"],
        "wall_clock_seconds": result["wall_clock_seconds"],
    }, ensure_ascii=False))
