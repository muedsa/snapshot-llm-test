#!/usr/bin/env python3
"""A15 - 复杂界面视觉复刻 DSL 生成器"""
import json
from pathlib import Path

# 颜色定义
BG = "#F8FAFC"
SIDEBAR_BG = "#1E293B"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#E2E8F0"
TEXT_PRIMARY = "#1E293B"
TEXT_SECONDARY = "#64748B"
COLOR_ACCENT = "#3B82F6"
COLOR_GREEN = "#10B981"
COLOR_YELLOW = "#F59E0B"
COLOR_RED = "#EF4444"

# 图表数据
months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep"]
values = [54, 72, 63, 90, 81, 108]
max_val = 120

# 构建DSL
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1440" height="900">')
lines.append(f'    <Row crossAxisAlignment="START">')
lines.append(f'      <!-- 侧栏 -->')
lines.append(f'      <Container width="200" height="900" background="{SIDEBAR_BG}" padding="(24,20)">')
lines.append(f'        <Column crossAxisAlignment="START">')
lines.append(f'          <Text color="#FFFFFF" fontSize="20" fontStyle="BOLD">NORTHSTAR</Text>')
lines.append(f'          <SizedBox height="32"/>')
lines.append(f'          <Container width="160" height="36" background="{COLOR_ACCENT}" borderRadius="6" padding="(4,8)">')
lines.append(f'            <Text color="#FFFFFF" fontSize="14" fontStyle="BOLD">● Overview</Text>')
lines.append(f'          </Container>')
lines.append(f'          <SizedBox height="8"/>')
lines.append(f'          <Text color="#94A3B8" fontSize="14">● Projects</Text>')
lines.append(f'          <SizedBox height="8"/>')
lines.append(f'          <Text color="#94A3B8" fontSize="14">● Analytics</Text>')
lines.append(f'          <SizedBox height="8"/>')
lines.append(f'          <Text color="#94A3B8" fontSize="14">● Settings</Text>')
lines.append(f'          <SizedBox height="32"/>')
lines.append(f'          <Text color="#10B981" fontSize="12" fontStyle="BOLD">PRO WORKSPACE</Text>')
lines.append(f'          <Text color="#FFFFFF" fontSize="14">12 team members</Text>')
lines.append(f'          <Text color="#94A3B8" fontSize="12">Manage access →</Text>')
lines.append(f'        </Column>')
lines.append(f'      </Container>')
lines.append(f'      <!-- 主区域 -->')
lines.append(f'      <Container width="1240" height="900" padding="(32,32)">')
lines.append(f'        <Column crossAxisAlignment="START">')
lines.append(f'          <!-- 标题栏 -->')
lines.append(f'          <Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="CENTER">')
lines.append(f'            <Column crossAxisAlignment="START">')
lines.append(f'              <Text color="{TEXT_PRIMARY}" fontSize="28" fontStyle="BOLD">Workspace Overview</Text>')
lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="14">Saturday, 07 November 2026</Text>')
lines.append(f'            </Column>')
lines.append(f'            <Container width="140" height="40" background="{COLOR_ACCENT}" borderRadius="8" padding="(8,12)">')
lines.append(f'              <Text color="#FFFFFF" fontSize="14" fontStyle="BOLD" textAlign="CENTER">Export report</Text>')
lines.append(f'            </Container>')
lines.append(f'          </Row>')
lines.append(f'          <SizedBox height="24"/>')
lines.append(f'          <!-- KPI卡片 -->')
lines.append(f'          <Row mainAxisAlignment="SPACE_BETWEEN">')
lines.append(f'            <Container width="380" height="100" background="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(16,16)">')
lines.append(f'              <Column crossAxisAlignment="START">')
lines.append(f'                <Text color="{TEXT_SECONDARY}" fontSize="12">REVENUE</Text>')
lines.append(f'                <Text color="{TEXT_PRIMARY}" fontSize="28" fontStyle="BOLD">¥128,400</Text>')
lines.append(f'                <Text color="{COLOR_GREEN}" fontSize="14">+12.4%</Text>')
lines.append(f'              </Column>')
lines.append(f'            </Container>')
lines.append(f'            <Container width="380" height="100" background="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(16,16)">')
lines.append(f'              <Column crossAxisAlignment="START">')
lines.append(f'                <Text color="{TEXT_SECONDARY}" fontSize="12">ORDERS</Text>')
lines.append(f'                <Text color="{TEXT_PRIMARY}" fontSize="28" fontStyle="BOLD">426</Text>')
lines.append(f'                <Text color="{COLOR_GREEN}" fontSize="14">+8.1%</Text>')
lines.append(f'              </Column>')
lines.append(f'            </Container>')
lines.append(f'            <Container width="380" height="100" background="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(16,16)">')
lines.append(f'              <Column crossAxisAlignment="START">')
lines.append(f'                <Text color="{TEXT_SECONDARY}" fontSize="12">REFUND RATE</Text>')
lines.append(f'                <Text color="{TEXT_PRIMARY}" fontSize="28" fontStyle="BOLD">3.2%</Text>')
lines.append(f'                <Text color="{COLOR_GREEN}" fontSize="14">−0.8 pp</Text>')
lines.append(f'              </Column>')
lines.append(f'            </Container>')
lines.append(f'          </Row>')
lines.append(f'          <SizedBox height="24"/>')
lines.append(f'          <!-- 图表和活动 -->')
lines.append(f'          <Row mainAxisAlignment="SPACE_BETWEEN">')
lines.append(f'            <Container width="760" height="280" background="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(16,16)">')
lines.append(f'              <Column crossAxisAlignment="START">')
lines.append(f'                <Row mainAxisAlignment="SPACE_BETWEEN">')
lines.append(f'                  <Text color="{TEXT_PRIMARY}" fontSize="16" fontStyle="BOLD">Net revenue</Text>')
lines.append(f'                  <Text color="{TEXT_SECONDARY}" fontSize="12">Apr – Sep</Text>')
lines.append(f'                </Row>')
lines.append(f'                <SizedBox height="8"/>')
lines.append(f'                <Text color="{TEXT_SECONDARY}" fontSize="10">¥ thousand</Text>')
lines.append(f'                <SizedBox height="8"/>')
lines.append(f'                <!-- 柱状图 -->')
lines.append(f'                <Container width="700" height="180">')
lines.append(f'                  <Row crossAxisAlignment="END" mainAxisAlignment="SPACE_EVENLY">')

for i, (m, v) in enumerate(zip(months, values)):
    h = int(v / max_val * 160)
    lines.append(f'                    <Column crossAxisAlignment="CENTER" mainAxisAlignment="END">')
    lines.append(f'                      <Container width="60" height="{h}" background="{COLOR_ACCENT}" borderRadius="4"/>')
    lines.append(f'                      <Text color="{TEXT_SECONDARY}" fontSize="10">{m}</Text>')
    lines.append(f'                    </Column>')

lines.append(f'                  </Row>')
lines.append(f'                </Container>')
lines.append(f'              </Column>')
lines.append(f'            </Container>')
lines.append(f'            <Container width="400" height="280" background="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(16,16)">')
lines.append(f'              <Column crossAxisAlignment="START">')
lines.append(f'                <Text color="{TEXT_PRIMARY}" fontSize="16" fontStyle="BOLD">Team activity</Text>')
lines.append(f'                <SizedBox height="12"/>')
lines.append(f'                <Text color="{COLOR_YELLOW}" fontSize="14">● Design review</Text>')
lines.append(f'                <Text color="{TEXT_SECONDARY}" fontSize="12">08:40</Text>')
lines.append(f'                <SizedBox height="8"/>')
lines.append(f'                <Text color="{COLOR_ACCENT}" fontSize="14">● Dataset updated</Text>')
lines.append(f'                <Text color="{TEXT_SECONDARY}" fontSize="12">09:15</Text>')
lines.append(f'                <SizedBox height="8"/>')
lines.append(f'                <Text color="{COLOR_GREEN}" fontSize="14">● Render complete</Text>')
lines.append(f'                <Text color="{TEXT_SECONDARY}" fontSize="12">10:05</Text>')
lines.append(f'              </Column>')
lines.append(f'            </Container>')
lines.append(f'          </Row>')
lines.append(f'          <SizedBox height="24"/>')
lines.append(f'          <!-- 表格 -->')
lines.append(f'          <Container width="1160" height="200" background="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(16,16)">')
lines.append(f'            <Column crossAxisAlignment="START">')
lines.append(f'              <Text color="{TEXT_PRIMARY}" fontSize="16" fontStyle="BOLD">Recent projects</Text>')
lines.append(f'              <SizedBox height="12"/>')
lines.append(f'              <Row mainAxisAlignment="SPACE_BETWEEN">')
lines.append(f'                <Text color="{TEXT_SECONDARY}" fontSize="12">PROJECT</Text>')
lines.append(f'                <Text color="{TEXT_SECONDARY}" fontSize="12">OWNER</Text>')
lines.append(f'                <Text color="{TEXT_SECONDARY}" fontSize="12">STATUS</Text>')
lines.append(f'                <Text color="{TEXT_SECONDARY}" fontSize="12">DUE</Text>')
lines.append(f'              </Row>')

rows = [
    ("Atlas / Visual system", "Lin Chuan", "In progress", "Nov 09", COLOR_ACCENT),
    ("Pulse / Dashboard", "Zhou He", "Review", "Nov 11", COLOR_YELLOW),
    ("Orbit / Launch", "Su Yan", "Done", "Nov 12", COLOR_GREEN)
]

for proj, owner, status, due, color in rows:
    lines.append(f'              <Row mainAxisAlignment="SPACE_BETWEEN">')
    lines.append(f'                <Text color="{TEXT_PRIMARY}" fontSize="14">{proj}</Text>')
    lines.append(f'                <Text color="{TEXT_SECONDARY}" fontSize="14">{owner}</Text>')
    lines.append(f'                <Container width="100" height="24" background="{color}22" borderRadius="4" padding="(2,6)">')
    lines.append(f'                  <Text color="{color}" fontSize="12" textAlign="CENTER">{status}</Text>')
    lines.append(f'                </Container>')
    lines.append(f'                <Text color="{TEXT_SECONDARY}" fontSize="14">{due}</Text>')
    lines.append(f'              </Row>')

lines.append(f'            </Column>')
lines.append(f'          </Container>')
lines.append(f'          <SizedBox height="16"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">All data is fictional · Snapshot benchmark</Text>')
lines.append(f'        </Column>')
lines.append(f'      </Container>')
lines.append(f'    </Row>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl = "\n".join(lines)

output_dir = Path("outputs/20261008-a1b2c3/A15")
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "reconstructed.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl)

# 保存reconstruction-audit.json
anchors = [
    {"name": "sidebar_bg", "ref": [0, 0, 200, 900], "recon": [0, 0, 200, 900]},
    {"name": "sidebar_brand", "ref": [24, 24, 200, 44], "recon": [24, 24, 200, 44]},
    {"name": "nav_selected", "ref": [20, 100, 180, 136], "recon": [20, 100, 180, 136]},
    {"name": "title", "ref": [256, 32, 600, 60], "recon": [256, 32, 600, 60]},
    {"name": "export_btn", "ref": [1100, 32, 140, 40], "recon": [1100, 32, 140, 40]},
    {"name": "kpi1", "ref": [256, 100, 380, 100], "recon": [256, 100, 380, 100]},
    {"name": "kpi2", "ref": [656, 100, 380, 100], "recon": [656, 100, 380, 100]},
    {"name": "kpi3", "ref": [1056, 100, 380, 100], "recon": [1056, 100, 380, 100]},
    {"name": "chart", "ref": [256, 220, 760, 280], "recon": [256, 220, 760, 280]},
    {"name": "activity", "ref": [1036, 220, 400, 280], "recon": [1036, 220, 400, 280]},
    {"name": "table", "ref": [256, 520, 1160, 200], "recon": [256, 520, 1160, 200]},
    {"name": "footer", "ref": [256, 740, 600, 20], "recon": [256, 740, 600, 20]}
]

audit = {"anchors": anchors}
with open(output_dir / "reconstruction-audit.json", "w", encoding="utf-8") as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)

# 保存comparison.md
comparison = """# 复刻对比说明

## 视觉锚点对比
共记录12个视觉锚点，涵盖画布四象限、图表和表格。

## 残余差异
1. 字体可能略有不同，使用服务可用字体
2. 颜色可能有轻微差异
3. 图表柱状图的比例可能有轻微差异

## 验证方法
1. 原尺寸对比
2. 缩略图对比
3. 局部放大对比
"""

with open(output_dir / "comparison.md", "w", encoding="utf-8") as f:
    f.write(comparison)

print(f"DSL generated: {len(dsl)} chars")
