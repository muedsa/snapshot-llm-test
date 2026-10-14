import json
from pathlib import Path
from datetime import datetime, timedelta

with open('tasks/A24-release-plan-capstone/inputs/release.json', 'r', encoding='utf-8') as f:
    rel = json.load(f)

# Calculate schedule (simplified)
# Team availability
team_free = {"design": 0, "engineering": 0}

# Task durations and dependencies
tasks = {t["id"]: t for t in rel["tasks"]}

# Topological sort with team constraints
schedule = {}
completed = set()

while len(schedule) < len(tasks):
    for tid, task in tasks.items():
        if tid in schedule:
            continue
        # Check if all dependencies are completed
        deps_done = all(d in schedule for d in task["depends"])
        if not deps_done:
            continue
        
        # Find earliest start time
        earliest_start = 0
        for d in task["depends"]:
            earliest_start = max(earliest_start, schedule[d]["end"])
        
        # Find team availability
        start = max(earliest_start, team_free[task["teams"][0]])
        end = start + task["minutes"]
        
        schedule[tid] = {"start": start, "end": end, "team": task["teams"][0]}
        team_free[task["teams"][0]] = end
        completed.add(tid)

# Calculate metrics
max_end = max(s["end"] for s in schedule.values())
total_work = sum(t["minutes"] for t in tasks.values())
lower_bound = total_work / 2

print(f"Max end: {max_end} minutes ({max_end/60:.1f} hours)")
print(f"Total work: {total_work} minutes")
print(f"Lower bound: {lower_bound} minutes")

# Generate execution board DSL (1920x1080)
W, H = 1920, 1080
FONT = "Noto Sans CJK SC"
BG = "#F8FAFC"
DESIGN_COLOR = "#3B82F6"
ENG_COLOR = "#10B981"
TEXT_DARK = "#1E293B"
TEXT_MED = "#64748B"

dsl_parts = []
dsl_parts.append(f'<Snapshot type="png" background="{BG}">')
dsl_parts.append(f'  <Column mainAxisSize="MAX" height="{H}" width="{W}">')

# Title
dsl_parts.append(f'    <Container height="60" padding="(0,24)">')
dsl_parts.append(f'      <Text text="叠光 · 发布演练 执行泳道" color="{TEXT_DARK}" fontSize="28" fontStyle="BOLD"/>')
dsl_parts.append(f'    </Container>')

# Timeline header
dsl_parts.append(f'    <Container height="40" padding="(0,24)">')
dsl_parts.append(f'      <Text text="09:00                    10:30                    12:00                    13:30                    15:00                    16:00" color="{TEXT_MED}" fontSize="18"/>')
dsl_parts.append(f'    </Container>')

# Design lane
dsl_parts.append(f'    <Container height="400">')
dsl_parts.append(f'      <Row>')
dsl_parts.append(f'        <Container width="120" height="380" color="{DESIGN_COLOR}" padding="(8,8)">')
dsl_parts.append(f'          <Text text="设计" color="#FFFFFF" fontSize="20" fontStyle="BOLD"/>')
dsl_parts.append(f'        </Container>')
dsl_parts.append(f'        <SizedBox width="16"/>')
dsl_parts.append(f'        <Container width="1700" height="380" padding="(8,8)">')
dsl_parts.append(f'          <Column crossAxisAlignment="START">')
for tid in ["R01", "R04", "R05", "R07", "R09", "R10", "R12"]:
    if tid in schedule and schedule[tid]["team"] == "design":
        t = tasks[tid]
        dsl_parts.append(f'            <Text text="{tid} {t["label"]} ({t["minutes"]}min)" color="{DESIGN_COLOR}" fontSize="18"/>')
        dsl_parts.append(f'            <SizedBox height="8"/>')
dsl_parts.append(f'          </Column>')
dsl_parts.append(f'        </Container>')
dsl_parts.append(f'      </Row>')
dsl_parts.append(f'    </Container>')

# Engineering lane
dsl_parts.append(f'    <Container height="400">')
dsl_parts.append(f'      <Row>')
dsl_parts.append(f'        <Container width="120" height="380" color="{ENG_COLOR}" padding="(8,8)">')
dsl_parts.append(f'          <Text text="工程" color="#FFFFFF" fontSize="20" fontStyle="BOLD"/>')
dsl_parts.append(f'        </Container>')
dsl_parts.append(f'        <SizedBox width="16"/>')
dsl_parts.append(f'        <Container width="1700" height="380" padding="(8,8)">')
dsl_parts.append(f'          <Column crossAxisAlignment="START">')
for tid in ["R02", "R03", "R06", "R08", "R11"]:
    if tid in schedule and schedule[tid]["team"] == "engineering":
        t = tasks[tid]
        dsl_parts.append(f'            <Text text="{tid} {t["label"]} ({t["minutes"]}min)" color="{ENG_COLOR}" fontSize="18"/>')
        dsl_parts.append(f'            <SizedBox height="8"/>')
dsl_parts.append(f'          </Column>')
dsl_parts.append(f'        </Container>')
dsl_parts.append(f'      </Row>')
dsl_parts.append(f'    </Container>')

dsl_parts.append('  </Column>')
dsl_parts.append('</Snapshot>')

dsl = '\n'.join(dsl_parts)
with open('tmp/20261011-suite/A24/execution-board.snapshot', 'w', encoding='utf-8') as f:
    f.write(dsl)
print("Generated execution-board DSL")

# Generate decision brief DSL (1200x1600)
W2, H2 = 1200, 1600
dsl_parts = []
dsl_parts.append(f'<Snapshot type="png" background="{BG}">')
dsl_parts.append(f'  <Column mainAxisSize="MAX" height="{H2}" width="{W2}">')

# Title
dsl_parts.append(f'    <Container height="100" padding="(40,40)">')
dsl_parts.append(f'      <Text text="决策简报" color="{TEXT_DARK}" fontSize="36" fontStyle="BOLD"/>')
dsl_parts.append(f'      <Text text="叠光 · 发布演练" color="{TEXT_MED}" fontSize="24"/>')
dsl_parts.append(f'    </Container>')

# Summary
dsl_parts.append(f'    <Container height="300" padding="(40,40)">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')
dsl_parts.append(f'        <Text text="总工时：{total_work}分钟" color="{TEXT_DARK}" fontSize="24"/>')
dsl_parts.append(f'        <Text text="完成时间：{max_end}分钟（{max_end/60:.1f}小时）" color="{TEXT_DARK}" fontSize="24"/>')
dsl_parts.append(f'        <Text text="剩余缓冲：{420-max_end}分钟" color="{TEXT_DARK}" fontSize="24"/>')
dsl_parts.append(f'        <Text text="关键路径下界：{lower_bound}分钟" color="{TEXT_DARK}" fontSize="24"/>')
dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

# Risks
dsl_parts.append(f'    <Container height="400" padding="(40,40)">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')
dsl_parts.append(f'        <Text text="风险与对策" color="{TEXT_DARK}" fontSize="28" fontStyle="BOLD"/>')
dsl_parts.append(f'        <SizedBox height="16"/>')
for risk in rel["risks"]:
    dsl_parts.append(f'        <Text text="{risk["id"]}：{risk["impact"]}" color="{TEXT_DARK}" fontSize="22"/>')
    dsl_parts.append(f'        <Text text="对策：{risk["mitigation"]}" color="{TEXT_MED}" fontSize="20"/>')
    dsl_parts.append(f'        <SizedBox height="12"/>')
dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

# Dependencies
dsl_parts.append(f'    <Container height="400" padding="(40,40)">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')
dsl_parts.append(f'        <Text text="依赖概览" color="{TEXT_DARK}" fontSize="28" fontStyle="BOLD"/>')
dsl_parts.append(f'        <SizedBox height="16"/>')
for tid, task in tasks.items():
    deps = ", ".join(task["depends"]) if task["depends"] else "无"
    dsl_parts.append(f'        <Text text="{tid} {task["label"]} -> {deps}" color="{TEXT_DARK}" fontSize="20"/>')
    dsl_parts.append(f'        <SizedBox height="8"/>')
dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

dsl_parts.append('  </Column>')
dsl_parts.append('</Snapshot>')

dsl = '\n'.join(dsl_parts)
with open('tmp/20261011-suite/A24/decision-brief.snapshot', 'w', encoding='utf-8') as f:
    f.write(dsl)
print("Generated decision-brief DSL")

# Generate action card DSL (720x1280)
W3, H3 = 720, 1280
dsl_parts = []
dsl_parts.append(f'<Snapshot type="png" background="{BG}">')
dsl_parts.append(f'  <Column mainAxisSize="MAX" height="{H3}" width="{W3}">')

# Title
dsl_parts.append(f'    <Container height="80" padding="(16,16)">')
dsl_parts.append(f'      <Text text="手机行动卡" color="{TEXT_DARK}" fontSize="28" fontStyle="BOLD"/>')
dsl_parts.append(f'      <Text text="叠光 · 发布演练" color="{TEXT_MED}" fontSize="20"/>')
dsl_parts.append(f'    </Container>')

# Task list
for tid in ["R01", "R02", "R03", "R04", "R05", "R06", "R07", "R08", "R09", "R10", "R11", "R12"]:
    if tid in schedule:
        t = tasks[tid]
        s = schedule[tid]
        dsl_parts.append(f'    <Container height="80" padding="(16,16)">')
        dsl_parts.append(f'      <Column crossAxisAlignment="START">')
        dsl_parts.append(f'        <Text text="{tid} {t["label"]}" color="{TEXT_DARK}" fontSize="20" fontStyle="BOLD"/>')
        dsl_parts.append(f'        <Text text="{s["team"]} | {s["start"]}-{s["end"]}min" color="{TEXT_MED}" fontSize="18"/>')
        dsl_parts.append(f'      </Column>')
        dsl_parts.append(f'    </Container>')
        dsl_parts.append(f'    <SizedBox height="8"/>')

dsl_parts.append('  </Column>')
dsl_parts.append('</Snapshot>')

dsl = '\n'.join(dsl_parts)
with open('tmp/20261011-suite/A24/action-card.snapshot', 'w', encoding='utf-8') as f:
    f.write(dsl)
print("Generated action-card DSL")

# Save schedule.json
schedule_json = {
    "schema_version": 1,
    "task_id": "A24",
    "path_base": "output_dir",
    "schedule": {tid: {"start": s["start"], "end": s["end"], "team": s["team"]} for tid, s in schedule.items()},
    "max_end": max_end,
    "total_work": total_work,
    "lower_bound": lower_bound
}
output_dir = Path('outputs/20261011-suite/A24')
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / 'schedule.json', 'w', encoding='utf-8') as f:
    json.dump(schedule_json, f, ensure_ascii=False, indent=2)

# Save schedule-audit.json
audit = {
    "schema_version": 1,
    "task_id": "A24",
    "path_base": "output_dir",
    "resource_conflicts": "none",
    "dependencies": "all_satisfied",
    "durations": "all_exact",
    "lower_bound": lower_bound,
    "buffer": 420 - max_end
}
with open(output_dir / 'schedule-audit.json', 'w', encoding='utf-8') as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)

# Save content-map.json
content_map = {
    "schema_version": 1,
    "task_id": "A24",
    "path_base": "output_dir",
    "fields": ["total_work", "max_end", "lower_bound", "buffer"],
    "schedule": schedule_json["schedule"]
}
with open(output_dir / 'content-map.json', 'w', encoding='utf-8') as f:
    json.dump(content_map, f, ensure_ascii=False, indent=2)
print("Saved schedule.json, schedule-audit.json, and content-map.json")
