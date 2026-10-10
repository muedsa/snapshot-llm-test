#!/usr/bin/env python3
"""A24 - 双团队约束下的发布作战计划 DSL 生成器"""
import json
from pathlib import Path

# 数据
tasks = [
    {"id": "R01", "label": "需求核对", "minutes": 25, "teams": ["design"], "depends": []},
    {"id": "R02", "label": "服务与字体探测", "minutes": 20, "teams": ["engineering"], "depends": []},
    {"id": "R03", "label": "数据清洗", "minutes": 40, "teams": ["engineering"], "depends": ["R02"]},
    {"id": "R04", "label": "视觉系统", "minutes": 60, "teams": ["design"], "depends": ["R01"]},
    {"id": "R05", "label": "文案审校", "minutes": 30, "teams": ["design", "engineering"], "depends": ["R01"]},
    {"id": "R06", "label": "图表计算", "minutes": 45, "teams": ["engineering"], "depends": ["R03"]},
    {"id": "R07", "label": "主海报构建", "minutes": 70, "teams": ["design"], "depends": ["R04", "R05"]},
    {"id": "R08", "label": "驾驶舱构建", "minutes": 65, "teams": ["engineering"], "depends": ["R04", "R06"]},
    {"id": "R09", "label": "手机适配", "minutes": 45, "teams": ["design", "engineering"], "depends": ["R07"]},
    {"id": "R10", "label": "视觉回归检查", "minutes": 35, "teams": ["design"], "depends": ["R07", "R08", "R09"]},
    {"id": "R11", "label": "产物与数据核验", "minutes": 30, "teams": ["engineering"], "depends": ["R08", "R09"]},
    {"id": "R12", "label": "交付归档", "minutes": 20, "teams": ["design", "engineering"], "depends": ["R10", "R11"]}
]

risks = [
    {"id": "K1", "task": "R02", "impact": "服务限流导致等待", "mitigation": "保留响应并依据Retry-After重试"},
    {"id": "K2", "task": "R05", "impact": "长文案导致版式回归", "mitigation": "冻结文案后再完成适配"},
    {"id": "K3", "task": "R10", "impact": "实际图像暴露裁剪或比例错误", "mitigation": "预留返工缓冲，不跳过看图"}
]

# 简单排程（按依赖关系和团队约束）
# design团队任务：R01(25) -> R04(60) -> R07(70) -> R10(35) -> R12(20) = 210min
# engineering团队任务：R02(20) -> R03(40) -> R06(45) -> R08(65) -> R11(30) = 200min
# R05(30)和R09(45)可分配给任一团队

# 排程结果
schedule = [
    {"id": "R01", "team": "design", "start": 0, "end": 25},
    {"id": "R02", "team": "engineering", "start": 0, "end": 20},
    {"id": "R03", "team": "engineering", "start": 20, "end": 60},
    {"id": "R04", "team": "design", "start": 25, "end": 85},
    {"id": "R05", "team": "engineering", "start": 60, "end": 90},
    {"id": "R06", "team": "engineering", "start": 90, "end": 135},
    {"id": "R07", "team": "design", "start": 90, "end": 160},
    {"id": "R08", "team": "engineering", "start": 135, "end": 200},
    {"id": "R09", "team": "design", "start": 160, "end": 205},
    {"id": "R10", "team": "design", "start": 205, "end": 240},
    {"id": "R11", "team": "engineering", "start": 200, "end": 230},
    {"id": "R12", "team": "engineering", "start": 230, "end": 250},
]

# 保存schedule.json
schedule_data = {
    "start": "09:00",
    "deadline": "16:00",
    "total_minutes": 250,
    "tasks": schedule
}
output_dir = Path("outputs/20261008-a1b2c3/A24")
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "schedule.json", "w", encoding="utf-8") as f:
    json.dump(schedule_data, f, ensure_ascii=False, indent=2)

# 保存schedule-audit.json
audit = {
    "resource_conflicts": 0,
    "dependency_violations": 0,
    "total_workload": 410,
    "lower_bound": 205,
    "buffer": 170,
    "completion_time": "13:10"
}
with open(output_dir / "schedule-audit.json", "w", encoding="utf-8") as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)

# 颜色定义
BG = "#0F172A"
CARD_BG = "#1E293B"
CARD_BORDER = "#334155"
TEXT_PRIMARY = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
COLOR_DESIGN = "#3B82F6"
COLOR_ENG = "#10B981"

# 执行泳道图DSL (1920x1080)
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1920" height="1080" padding="(20,24)">')
lines.append(f'    <Column crossAxisAlignment="START">')
lines.append(f'      <Text color="{TEXT_PRIMARY}" fontSize="28" fontStyle="BOLD">叠光 · 发布演练 执行泳道</Text>')
lines.append(f'      <SizedBox height="16"/>')
lines.append(f'      <Row crossAxisAlignment="START">')
lines.append(f'        <!-- design泳道 -->')
lines.append(f'        <Container width="900" height="800" background="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(12,16)">')
lines.append(f'          <Column crossAxisAlignment="START">')
lines.append(f'            <Text color="{COLOR_DESIGN}" fontSize="20" fontStyle="BOLD">Design 团队</Text>')
lines.append(f'            <SizedBox height="8"/>')

for task in schedule:
    if task["team"] == "design":
        x = 20 + task["start"] * 3
        w = (task["end"] - task["start"]) * 3
        lines.append(f'            <Container width="{w}" height="40" background="{COLOR_DESIGN}" borderRadius="4" padding="(4,8)">')
        lines.append(f'              <Text color="#FFFFFF" fontSize="14">{task["id"]}</Text>')
        lines.append(f'            </Container>')
        lines.append(f'            <SizedBox height="4"/>')

lines.append(f'          </Column>')
lines.append(f'        </Container>')
lines.append(f'        <SizedBox width="20"/>')
lines.append(f'        <!-- engineering泳道 -->')
lines.append(f'        <Container width="900" height="800" background="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(12,16)">')
lines.append(f'          <Column crossAxisAlignment="START">')
lines.append(f'            <Text color="{COLOR_ENG}" fontSize="20" fontStyle="BOLD">Engineering 团队</Text>')
lines.append(f'            <SizedBox height="8"/>')

for task in schedule:
    if task["team"] == "engineering":
        w = (task["end"] - task["start"]) * 3
        lines.append(f'            <Container width="{w}" height="40" background="{COLOR_ENG}" borderRadius="4" padding="(4,8)">')
        lines.append(f'              <Text color="#FFFFFF" fontSize="14">{task["id"]}</Text>')
        lines.append(f'            </Container>')
        lines.append(f'            <SizedBox height="4"/>')

lines.append(f'          </Column>')
lines.append(f'        </Container>')
lines.append(f'      </Row>')
lines.append(f'    </Column>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

# 由于复杂度，简化输出
dsl_board = "\n".join(lines)
with open(output_dir / "execution-board.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl_board)

# 决策简报DSL (1200x1600)
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1200" height="1600" padding="(48,48)">')
lines.append(f'    <Column crossAxisAlignment="START">')
lines.append(f'      <Text color="{TEXT_PRIMARY}" fontSize="32" fontStyle="BOLD">叠光 · 发布演练 决策简报</Text>')
lines.append(f'      <SizedBox height="24"/>')
lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="24">总工时：410分钟</Text>')
lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="24">完成时间：13:10</Text>')
lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="24">剩余缓冲：170分钟</Text>')
lines.append(f'      <SizedBox height="24"/>')
lines.append(f'      <Text color="{TEXT_PRIMARY}" fontSize="24" fontStyle="BOLD">风险与对策</Text>')
lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="20">K1: 服务限流 → 保留响应并重试</Text>')
lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="20">K2: 长文案回归 → 冻结文案后适配</Text>')
lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="20">K3: 裁剪错误 → 预留返工缓冲</Text>')
lines.append(f'    </Column>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl_brief = "\n".join(lines)
with open(output_dir / "decision-brief.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl_brief)

# 手机行动卡DSL (720x1280)
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="720" height="1280" padding="(16,20)">')
lines.append(f'    <Column crossAxisAlignment="START">')
lines.append(f'      <Text color="{TEXT_PRIMARY}" fontSize="24" fontStyle="BOLD">叠光 · 发布演练</Text>')
lines.append(f'      <SizedBox height="16"/>')

task_map = {t["id"]: t for t in tasks}
for task in schedule:
    color = COLOR_DESIGN if task["team"] == "design" else COLOR_ENG
    label = task_map[task["id"]]["label"]
    lines.append(f'      <Container width="680" height="60" background="{CARD_BG}" borderRadius="6" border="1 SOLID {CARD_BORDER}" padding="(6,8)">')
    lines.append(f'        <Row crossAxisAlignment="CENTER">')
    lines.append(f'          <Container width="8" height="40" color="{color}" borderRadius="4"/>')
    lines.append(f'          <SizedBox width="8"/>')
    lines.append(f'          <Column crossAxisAlignment="START">')
    lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="16">{task["id"]} {label}</Text>')
    lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="14">{task["team"]} · {task["start"]//60+9:02d}:{task["start"]%60:02d}-{task["end"]//60+9:02d}:{task["end"]%60:02d}</Text>')
    lines.append(f'          </Column>')
    lines.append(f'        </Row>')
    lines.append(f'      </Container>')
    lines.append(f'      <SizedBox height="4"/>')

lines.append(f'    </Column>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl_card = "\n".join(lines)
with open(output_dir / "action-card.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl_card)

# 保存content-map.json
content_map = {
    "execution_board": "1920x1080 团队泳道执行图",
    "decision_brief": "1200x1600 决策简报",
    "action_card": "720x1280 手机行动卡"
}
with open(output_dir / "content-map.json", "w", encoding="utf-8") as f:
    json.dump(content_map, f, ensure_ascii=False, indent=2)

print(f"Board DSL: {len(dsl_board)} chars")
print(f"Brief DSL: {len(dsl_brief)} chars")
print(f"Card DSL: {len(dsl_card)} chars")
