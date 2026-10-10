#!/usr/bin/env python3
"""A16 - 从错误图表恢复可信叙事 DSL 生成器"""
import json
from pathlib import Path

# 数据
data = [
    {"quarter": "Q1", "revenue": 120, "cost": 90},
    {"quarter": "Q2", "revenue": 135, "cost": 108},
    {"quarter": "Q3", "revenue": 128, "cost": 96},
    {"quarter": "Q4", "revenue": 180, "cost": 126},
]

# 计算利润
for d in data:
    d["profit"] = d["revenue"] - d["cost"]

# 保存corrected-data.json
corrected_data = {
    "data": data,
    "total_revenue": sum(d["revenue"] for d in data),
    "total_cost": sum(d["cost"] for d in data),
    "total_profit": sum(d["profit"] for d in data),
    "max_profit_quarter": max(data, key=lambda x: x["profit"])["quarter"],
    "chart_max": 200
}

output_dir = Path("outputs/20261008-a1b2c3/A16")
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "corrected-data.json", "w", encoding="utf-8") as f:
    json.dump(corrected_data, f, ensure_ascii=False, indent=2)

# 保存findings.json
findings = [
    {
        "id": "F001",
        "location": "标题",
        "phenomenon": "标题说'Q3利润最高'",
        "source_check": "Q4利润54万元最高，Q3利润32万元",
        "impact": "误导读者关注错误季度",
        "fix": "改为'Q4利润最高'",
        "verified": True
    },
    {
        "id": "F002",
        "location": "副标题",
        "phenomenon": "副标题说'收入持续上升'",
        "source_check": "Q3收入128万元比Q2的135万元低",
        "impact": "误导读者认为收入单调增长",
        "fix": "改为'收入整体上升，Q4最高'",
        "verified": True
    },
    {
        "id": "F003",
        "location": "图表Q1柱状图",
        "phenomenon": "Q1收入柱（90）和成本柱（120）位置颠倒",
        "source_check": "Q1收入120万元，成本90万元",
        "impact": "图表显示收入低于成本，与数据矛盾",
        "fix": "交换Q1收入与成本柱位置",
        "verified": True
    },
    {
        "id": "F004",
        "location": "图表Q4柱状图",
        "phenomenon": "Q4收入柱（180）和成本柱（126）位置颠倒",
        "source_check": "Q4收入180万元，成本126万元",
        "impact": "图表显示收入低于成本，与数据矛盾",
        "fix": "交换Q4收入与成本柱位置",
        "verified": True
    },
    {
        "id": "F005",
        "location": "利润明细",
        "phenomenon": "Q3利润显示42万元",
        "source_check": "Q3利润=128-96=32万元",
        "impact": "利润数据错误",
        "fix": "改为32万元",
        "verified": True
    },
    {
        "id": "F006",
        "location": "重点观察",
        "phenomenon": "重点观察说'Q3利润最高'",
        "source_check": "Q4利润54万元最高",
        "impact": "误导读者关注错误季度",
        "fix": "改为'Q4利润最高'",
        "verified": True
    }
]

with open(output_dir / "findings.json", "w", encoding="utf-8") as f:
    json.dump(findings, f, ensure_ascii=False, indent=2)

# 颜色定义
BG = "#F8FAFC"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#E2E8F0"
TEXT_PRIMARY = "#1E293B"
TEXT_SECONDARY = "#64748B"
COLOR_REVENUE = "#F59E0B"
COLOR_COST = "#3B82F6"

# 构建DSL
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1280" height="900" padding="(32,32)">')
lines.append(f'    <Column crossAxisAlignment="START">')
lines.append(f'')
lines.append(f'      <!-- 标题 -->')
lines.append(f'      <Text color="{TEXT_PRIMARY}" fontSize="28" fontStyle="BOLD">季度复盘：Q4利润最高</Text>')
lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="16">收入整体上升，Q4最高</Text>')
lines.append(f'')
lines.append(f'      <SizedBox height="16"/>')
lines.append(f'')
lines.append(f'      <!-- 图表 -->')
lines.append(f'      <Container width="1216" height="400" background="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(16,16)">')
lines.append(f'        <Column crossAxisAlignment="START">')
lines.append(f'          <Row mainAxisAlignment="SPACE_BETWEEN">')
lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="18" fontStyle="BOLD">收入与成本对比</Text>')
lines.append(f'            <Row crossAxisAlignment="CENTER">')
lines.append(f'              <Container width="16" height="16" background="{COLOR_COST}" borderRadius="2"/>')
lines.append(f'              <SizedBox width="4"/>')
lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="14">成本</Text>')
lines.append(f'              <SizedBox width="16"/>')
lines.append(f'              <Container width="16" height="16" background="{COLOR_REVENUE}" borderRadius="2"/>')
lines.append(f'              <SizedBox width="4"/>')
lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="14">收入</Text>')
lines.append(f'            </Row>')
lines.append(f'          </Row>')
lines.append(f'          <SizedBox height="8"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">单位：万元</Text>')
lines.append(f'          <SizedBox height="8"/>')
lines.append(f'          <!-- 柱状图 -->')
lines.append(f'          <Container width="1160" height="300">')
lines.append(f'            <Row crossAxisAlignment="END" mainAxisAlignment="SPACE_EVENLY">')

for d in data:
    rev_h = int(d["revenue"] / 200 * 240)
    cost_h = int(d["cost"] / 200 * 240)
    lines.append(f'              <Column crossAxisAlignment="CENTER" mainAxisAlignment="END">')
    lines.append(f'                <Row crossAxisAlignment="END">')
    lines.append(f'                  <Container width="50" height="{cost_h}" background="{COLOR_COST}" borderRadius="4"/>')
    lines.append(f'                  <SizedBox width="8"/>')
    lines.append(f'                  <Container width="50" height="{rev_h}" background="{COLOR_REVENUE}" borderRadius="4"/>')
    lines.append(f'                </Row>')
    lines.append(f'                <SizedBox height="8"/>')
    lines.append(f'                <Text color="{TEXT_PRIMARY}" fontSize="14" fontStyle="BOLD">{d["quarter"]}</Text>')
    lines.append(f'              </Column>')

lines.append(f'            </Row>')
lines.append(f'          </Container>')
lines.append(f'        </Column>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'      <SizedBox height="16"/>')
lines.append(f'')
lines.append(f'      <!-- 利润明细 -->')
lines.append(f'      <Container width="1216" height="120" background="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(16,16)">')
lines.append(f'        <Column crossAxisAlignment="START">')
lines.append(f'          <Text color="{TEXT_PRIMARY}" fontSize="18" fontStyle="BOLD">利润明细</Text>')
lines.append(f'          <SizedBox height="12"/>')
lines.append(f'          <Row mainAxisAlignment="SPACE_BETWEEN">')

for d in data:
    lines.append(f'            <Column crossAxisAlignment="START">')
    lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="14">{d["quarter"]}</Text>')
    lines.append(f'              <Text color="{TEXT_PRIMARY}" fontSize="24" fontStyle="BOLD">{d["profit"]} 万元</Text>')
    lines.append(f'            </Column>')

lines.append(f'          </Row>')
lines.append(f'        </Column>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'      <SizedBox height="16"/>')
lines.append(f'')
lines.append(f'      <!-- 重点观察 -->')
lines.append(f'      <Container width="1216" height="80" background="#FEF3C7" borderRadius="8" border="1 SOLID #F59E0B" padding="(12,16)">')
lines.append(f'        <Column crossAxisAlignment="START">')
lines.append(f'          <Text color="#92400E" fontSize="16" fontStyle="BOLD">重点观察 · Q4</Text>')
lines.append(f'          <Text color="#92400E" fontSize="14">Q4利润最高（54万元），收入最高（180万元）。</Text>')
lines.append(f'        </Column>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'      <SizedBox height="16"/>')
lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="12">虚构数据 · 修正后报告</Text>')
lines.append(f'')
lines.append(f'    </Column>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl = "\n".join(lines)
with open(output_dir / "corrected-report.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl)

print(f"DSL generated: {len(dsl)} chars")
print(f"Total profit: {corrected_data['total_profit']}")
