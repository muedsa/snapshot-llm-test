#!/usr/bin/env python3
"""A05 - 不规则采样与缺测的仪表报告 DSL 生成器"""
import json
from pathlib import Path

# 数据
readings = [
    {"time": "08:00", "temp": 19.2, "humidity": 41, "pressure": 0.2},
    {"time": "08:10", "temp": 19.6, "humidity": 40, "pressure": 0.4},
    {"time": "08:35", "temp": 20.1, "humidity": 39, "pressure": 0.7},
    {"time": "09:00", "temp": 21.0, "humidity": 38, "pressure": 1.1},
    {"time": "09:15", "temp": None, "humidity": 37, "pressure": 1.3},
    {"time": "09:40", "temp": 21.9, "humidity": None, "pressure": -0.2},
    {"time": "10:10", "temp": 22.3, "humidity": 35, "pressure": -0.8},
    {"time": "10:50", "temp": 23.1, "humidity": 34, "pressure": -0.3},
    {"time": "11:00", "temp": 22.8, "humidity": 35, "pressure": 0.1},
    {"time": "11:40", "temp": None, "humidity": 36, "pressure": 0.6},
    {"time": "12:10", "temp": 22.0, "humidity": 37, "pressure": 0.3},
    {"time": "12:30", "temp": 21.7, "humidity": 38, "pressure": 0.0},
]

# 时间转分钟
def time_to_min(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m

start_min = time_to_min("08:00")
end_min = time_to_min("12:30")
total_min = end_min - start_min  # 270分钟

# 计算统计
valid_temps = [r["temp"] for r in readings if r["temp"] is not None]
valid_humidity = [r["humidity"] for r in readings if r["humidity"] is not None]
valid_pressure = [r["pressure"] for r in readings if r["pressure"] is not None]

stats = {
    "temperature": {"valid_count": len(valid_temps), "min": min(valid_temps), "max": max(valid_temps)},
    "humidity": {"valid_count": len(valid_humidity), "min": min(valid_humidity), "max": max(valid_humidity)},
    "pressure": {"valid_count": len(valid_pressure), "min": min(valid_pressure), "max": max(valid_pressure)}
}

# 保存normalized-data.json
normalized = {
    "readings": readings,
    "time_range": {"start": "08:00", "end": "12:30", "total_minutes": total_min},
    "stats": stats,
    "missing_data": {
        "temperature": ["09:15", "11:40"],
        "humidity": ["09:40"],
        "pressure": []
    }
}

output_dir = Path("outputs/20261008-a1b2c3/A05")
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "normalized-data.json", "w", encoding="utf-8") as f:
    json.dump(normalized, f, ensure_ascii=False, indent=2)

# 颜色定义
BG = "#0F172A"
CARD_BG = "#1E293B"
CARD_BORDER = "#334155"
TEXT_PRIMARY = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
COLOR_TEMP = "#EF4444"
COLOR_HUMIDITY = "#3B82F6"
COLOR_PRESSURE = "#10B981"
COLOR_GRID = "#334155"
COLOR_MISSING = "#F59E0B"

# 构建DSL
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1440" height="1000" padding="(20,24)">')
lines.append(f'    <Column crossAxisAlignment="START">')
lines.append(f'')
lines.append(f'      <!-- 标题 -->')
lines.append(f'      <Container width="1392" height="40" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(10,14)">')
lines.append(f'        <Text color="{TEXT_PRIMARY}" fontSize="20" fontStyle="BOLD">实验舱 · 08:00–12:30 三联趋势报告</Text>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'      <SizedBox height="10"/>')
lines.append(f'')
lines.append(f'      <!-- 统计信息 -->')
lines.append(f'      <Row mainAxisAlignment="SPACE_BETWEEN">')
lines.append(f'        <Container width="440" height="50" color="{CARD_BG}" borderRadius="6" border="1 SOLID {CARD_BORDER}" padding="(8,10)">')
lines.append(f'          <Column crossAxisAlignment="START">')
lines.append(f'            <Text color="{COLOR_TEMP}" fontSize="12" fontStyle="BOLD">温度 °C</Text>')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="11">有效{stats["temperature"]["valid_count"]}次 · {stats["temperature"]["min"]}–{stats["temperature"]["max"]}</Text>')
lines.append(f'          </Column>')
lines.append(f'        </Container>')
lines.append(f'        <Container width="440" height="50" color="{CARD_BG}" borderRadius="6" border="1 SOLID {CARD_BORDER}" padding="(8,10)">')
lines.append(f'          <Column crossAxisAlignment="START">')
lines.append(f'            <Text color="{COLOR_HUMIDITY}" fontSize="12" fontStyle="BOLD">湿度 %</Text>')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="11">有效{stats["humidity"]["valid_count"]}次 · {stats["humidity"]["min"]}–{stats["humidity"]["max"]}</Text>')
lines.append(f'          </Column>')
lines.append(f'        </Container>')
lines.append(f'        <Container width="440" height="50" color="{CARD_BG}" borderRadius="6" border="1 SOLID {CARD_BORDER}" padding="(8,10)">')
lines.append(f'          <Column crossAxisAlignment="START">')
lines.append(f'            <Text color="{COLOR_PRESSURE}" fontSize="12" fontStyle="BOLD">压差 kPa</Text>')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="11">有效{stats["pressure"]["valid_count"]}次 · {stats["pressure"]["min"]}–{stats["pressure"]["max"]}</Text>')
lines.append(f'          </Column>')
lines.append(f'        </Container>')
lines.append(f'      </Row>')
lines.append(f'')
lines.append(f'      <SizedBox height="10"/>')
lines.append(f'')
lines.append(f'      <!-- 三联趋势图 -->')
lines.append(f'      <Row mainAxisAlignment="SPACE_BETWEEN">')
lines.append(f'')
lines.append(f'        <!-- 温度图 -->')
lines.append(f'        <Container width="440" height="400" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(10,12)">')
lines.append(f'          <Column crossAxisAlignment="START">')
lines.append(f'            <Text color="{COLOR_TEMP}" fontSize="14" fontStyle="BOLD">温度 (°C)</Text>')
lines.append(f'            <SizedBox height="8"/>')
lines.append(f'            <Container width="416" height="320">')
lines.append(f'              <Column crossAxisAlignment="START">')
lines.append(f'                <!-- Y轴 -->')
lines.append(f'                <Row crossAxisAlignment="CENTER">')
lines.append(f'                  <Container width="40" height="280">')
lines.append(f'                    <Column mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="END">')
lines.append(f'                      <Text color="{TEXT_SECONDARY}" fontSize="10">24</Text>')
lines.append(f'                      <Text color="{TEXT_SECONDARY}" fontSize="10">22</Text>')
lines.append(f'                      <Text color="{TEXT_SECONDARY}" fontSize="10">20</Text>')
lines.append(f'                      <Text color="{TEXT_SECONDARY}" fontSize="10">18</Text>')
lines.append(f'                    </Column>')
lines.append(f'                  </Container>')
lines.append(f'                  <SizedBox width="6"/>')
lines.append(f'                  <!-- 图表区域 -->')
lines.append(f'                  <Container width="370" height="280">')
lines.append(f'                    <Stack>')

# 温度数据点
temp_points = [(i, r) for i, r in enumerate(readings) if r["temp"] is not None]
for idx, (i, r) in enumerate(temp_points):
    x = (time_to_min(r["time"]) - start_min) / total_min * 370
    y = (r["temp"] - 18) / (24 - 18) * 280
    y = 280 - y  # 翻转Y轴
    lines.append(f'                      <Positioned left="{x}" top="{y}" width="6" height="6">')
    lines.append(f'                        <Container width="6" height="6" color="{COLOR_TEMP}" borderRadius="3"/>')
    lines.append(f'                      </Positioned>')

lines.append(f'                    </Stack>')
lines.append(f'                  </Container>')
lines.append(f'                </Row>')
lines.append(f'                <!-- X轴 -->')
lines.append(f'                <Row crossAxisAlignment="CENTER">')
lines.append(f'                  <Container width="40" height="20"/>')
lines.append(f'                  <SizedBox width="6"/>')
lines.append(f'                  <Container width="370" height="20">')
lines.append(f'                    <Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="CENTER">')
for t in ["08:00", "09:00", "10:00", "11:00", "12:00"]:
    lines.append(f'                      <Text color="{TEXT_SECONDARY}" fontSize="10">{t}</Text>')
lines.append(f'                    </Row>')
lines.append(f'                  </Container>')
lines.append(f'                </Row>')
lines.append(f'              </Column>')
lines.append(f'            </Container>')
lines.append(f'          </Column>')
lines.append(f'        </Container>')
lines.append(f'')
lines.append(f'        <!-- 湿度图 -->')
lines.append(f'        <Container width="440" height="400" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(10,12)">')
lines.append(f'          <Column crossAxisAlignment="START">')
lines.append(f'            <Text color="{COLOR_HUMIDITY}" fontSize="14" fontStyle="BOLD">湿度 (%)</Text>')
lines.append(f'            <SizedBox height="8"/>')
lines.append(f'            <Container width="416" height="320">')
lines.append(f'              <Column crossAxisAlignment="START">')
lines.append(f'                <!-- Y轴 -->')
lines.append(f'                <Row crossAxisAlignment="CENTER">')
lines.append(f'                  <Container width="40" height="280">')
lines.append(f'                    <Column mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="END">')
lines.append(f'                      <Text color="{TEXT_SECONDARY}" fontSize="10">42</Text>')
lines.append(f'                      <Text color="{TEXT_SECONDARY}" fontSize="10">40</Text>')
lines.append(f'                      <Text color="{TEXT_SECONDARY}" fontSize="10">38</Text>')
lines.append(f'                      <Text color="{TEXT_SECONDARY}" fontSize="10">36</Text>')
lines.append(f'                      <Text color="{TEXT_SECONDARY}" fontSize="10">34</Text>')
lines.append(f'                    </Column>')
lines.append(f'                  </Container>')
lines.append(f'                  <SizedBox width="6"/>')
lines.append(f'                  <!-- 图表区域 -->')
lines.append(f'                  <Container width="370" height="280">')
lines.append(f'                    <Stack>')

# 湿度数据点
humidity_points = [(i, r) for i, r in enumerate(readings) if r["humidity"] is not None]
for idx, (i, r) in enumerate(humidity_points):
    x = (time_to_min(r["time"]) - start_min) / total_min * 370
    y = (r["humidity"] - 34) / (42 - 34) * 280
    y = 280 - y
    lines.append(f'                      <Positioned left="{x}" top="{y}" width="6" height="6">')
    lines.append(f'                        <Container width="6" height="6" color="{COLOR_HUMIDITY}" borderRadius="3"/>')
    lines.append(f'                      </Positioned>')

lines.append(f'                    </Stack>')
lines.append(f'                  </Container>')
lines.append(f'                </Row>')
lines.append(f'                <!-- X轴 -->')
lines.append(f'                <Row crossAxisAlignment="CENTER">')
lines.append(f'                  <Container width="40" height="20"/>')
lines.append(f'                  <SizedBox width="6"/>')
lines.append(f'                  <Container width="370" height="20">')
lines.append(f'                    <Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="CENTER">')
for t in ["08:00", "09:00", "10:00", "11:00", "12:00"]:
    lines.append(f'                      <Text color="{TEXT_SECONDARY}" fontSize="10">{t}</Text>')
lines.append(f'                    </Row>')
lines.append(f'                  </Container>')
lines.append(f'                </Row>')
lines.append(f'              </Column>')
lines.append(f'            </Container>')
lines.append(f'          </Column>')
lines.append(f'        </Container>')
lines.append(f'')
lines.append(f'        <!-- 压差图 -->')
lines.append(f'        <Container width="440" height="400" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(10,12)">')
lines.append(f'          <Column crossAxisAlignment="START">')
lines.append(f'            <Text color="{COLOR_PRESSURE}" fontSize="14" fontStyle="BOLD">压差 (kPa)</Text>')
lines.append(f'            <SizedBox height="8"/>')
lines.append(f'            <Container width="416" height="320">')
lines.append(f'              <Column crossAxisAlignment="START">')
lines.append(f'                <!-- Y轴 -->')
lines.append(f'                <Row crossAxisAlignment="CENTER">')
lines.append(f'                  <Container width="40" height="280">')
lines.append(f'                    <Column mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="END">')
lines.append(f'                      <Text color="{TEXT_SECONDARY}" fontSize="10">1.5</Text>')
lines.append(f'                      <Text color="{TEXT_SECONDARY}" fontSize="10">1.0</Text>')
lines.append(f'                      <Text color="{TEXT_SECONDARY}" fontSize="10">0.5</Text>')
lines.append(f'                      <Text color="{TEXT_SECONDARY}" fontSize="10">0</Text>')
lines.append(f'                      <Text color="{TEXT_SECONDARY}" fontSize="10">-0.5</Text>')
lines.append(f'                      <Text color="{TEXT_SECONDARY}" fontSize="10">-1.0</Text>')
lines.append(f'                    </Column>')
lines.append(f'                  </Container>')
lines.append(f'                  <SizedBox width="6"/>')
lines.append(f'                  <!-- 图表区域 -->')
lines.append(f'                  <Container width="370" height="280">')
lines.append(f'                    <Stack>')

# 零线
zero_y = (0 - (-1.0)) / (1.5 - (-1.0)) * 280
lines.append(f'                      <Positioned left="0" top="{zero_y}" width="370" height="2">')
lines.append(f'                        <Container width="370" height="2" color="{COLOR_GRID}"/>')
lines.append(f'                      </Positioned>')

# 压差数据点
for r in readings:
    x = (time_to_min(r["time"]) - start_min) / total_min * 370
    y = (r["pressure"] - (-1.0)) / (1.5 - (-1.0)) * 280
    y = 280 - y
    lines.append(f'                      <Positioned left="{x}" top="{y}" width="6" height="6">')
    lines.append(f'                        <Container width="6" height="6" color="{COLOR_PRESSURE}" borderRadius="3"/>')
    lines.append(f'                      </Positioned>')

lines.append(f'                    </Stack>')
lines.append(f'                  </Container>')
lines.append(f'                </Row>')
lines.append(f'                <!-- X轴 -->')
lines.append(f'                <Row crossAxisAlignment="CENTER">')
lines.append(f'                  <Container width="40" height="20"/>')
lines.append(f'                  <SizedBox width="6"/>')
lines.append(f'                  <Container width="370" height="20">')
lines.append(f'                    <Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="CENTER">')
for t in ["08:00", "09:00", "10:00", "11:00", "12:00"]:
    lines.append(f'                      <Text color="{TEXT_SECONDARY}" fontSize="10">{t}</Text>')
lines.append(f'                    </Row>')
lines.append(f'                  </Container>')
lines.append(f'                </Row>')
lines.append(f'              </Column>')
lines.append(f'            </Container>')
lines.append(f'          </Column>')
lines.append(f'        </Container>')
lines.append(f'')
lines.append(f'      </Row>')
lines.append(f'')
lines.append(f'      <SizedBox height="10"/>')
lines.append(f'')
lines.append(f'      <!-- 数据表 -->')
lines.append(f'      <Container width="1392" height="180" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(10,12)">')
lines.append(f'        <Column crossAxisAlignment="START">')
lines.append(f'          <Text color="{TEXT_PRIMARY}" fontSize="14" fontStyle="BOLD">全部12时点数据</Text>')
lines.append(f'          <SizedBox height="6"/>')
lines.append(f'          <Row mainAxisAlignment="SPACE_BETWEEN">')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="11">时间</Text>')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="11">温度°C</Text>')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="11">湿度%</Text>')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="11">压差kPa</Text>')
lines.append(f'          </Row>')

for r in readings:
    temp_str = f"{r['temp']}" if r["temp"] is not None else "—"
    humidity_str = f"{r['humidity']}" if r["humidity"] is not None else "—"
    pressure_str = f"{r['pressure']}"
    lines.append(f'          <Row mainAxisAlignment="SPACE_BETWEEN">')
    lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="11">{r["time"]}</Text>')
    lines.append(f'            <Text color="{COLOR_TEMP}" fontSize="11">{temp_str}</Text>')
    lines.append(f'            <Text color="{COLOR_HUMIDITY}" fontSize="11">{humidity_str}</Text>')
    lines.append(f'            <Text color="{COLOR_PRESSURE}" fontSize="11">{pressure_str}</Text>')
    lines.append(f'          </Row>')

lines.append(f'        </Column>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'      <!-- 图例 -->')
lines.append(f'      <Container width="1392" height="30" color="{CARD_BG}" borderRadius="6" border="1 SOLID {CARD_BORDER}" padding="(6,10)">')
lines.append(f'        <Row crossAxisAlignment="CENTER">')
lines.append(f'          <Container width="12" height="12" color="{COLOR_MISSING}" borderRadius="2"/>')
lines.append(f'          <SizedBox width="4"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="11">缺测（断线）</Text>')
lines.append(f'          <SizedBox width="16"/>')
lines.append(f'          <Container width="12" height="12" color="{COLOR_TEMP}" borderRadius="2"/>')
lines.append(f'          <SizedBox width="4"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="11">温度</Text>')
lines.append(f'          <SizedBox width="16"/>')
lines.append(f'          <Container width="12" height="12" color="{COLOR_HUMIDITY}" borderRadius="2"/>')
lines.append(f'          <SizedBox width="4"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="11">湿度</Text>')
lines.append(f'          <SizedBox width="16"/>')
lines.append(f'          <Container width="12" height="12" color="{COLOR_PRESSURE}" borderRadius="2"/>')
lines.append(f'          <SizedBox width="4"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="11">压差</Text>')
lines.append(f'        </Row>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'    </Column>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl = "\n".join(lines)
with open(output_dir / "sensor-report.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl)

print(f"DSL generated: {len(dsl)} chars")
print(f"Stats: {stats}")
