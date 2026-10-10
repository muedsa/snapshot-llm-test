#!/usr/bin/env python3
"""A04 - 分组改善与总体下降的数据解释 DSL 生成器"""
import json
from pathlib import Path

# 数据
data = [
    {"period": "前期", "channel": "直接访问", "visits": 8000, "conversions": 2400},
    {"period": "前期", "channel": "推广访问", "visits": 2000, "conversions": 200},
    {"period": "后期", "channel": "直接访问", "visits": 2000, "conversions": 700},
    {"period": "后期", "channel": "推广访问", "visits": 8000, "conversions": 960},
]

# 计算转化率
for d in data:
    d["rate"] = d["conversions"] / d["visits"] * 100

# 前期数据
pre_direct = data[0]
pre_promo = data[1]
pre_total_visits = pre_direct["visits"] + pre_promo["visits"]
pre_total_conversions = pre_direct["conversions"] + pre_promo["conversions"]
pre_total_rate = pre_total_conversions / pre_total_visits * 100

# 后期数据
post_direct = data[2]
post_promo = data[3]
post_total_visits = post_direct["visits"] + post_promo["visits"]
post_total_conversions = post_direct["conversions"] + post_promo["conversions"]
post_total_rate = post_total_conversions / post_total_visits * 100

# 保存analysis.json
analysis = {
    "data": data,
    "calculations": {
        "pre_direct_rate": f"{pre_direct['conversions']}/{pre_direct['visits']} = {pre_direct['rate']:.2f}%",
        "pre_promo_rate": f"{pre_promo['conversions']}/{pre_promo['visits']} = {pre_promo['rate']:.2f}%",
        "post_direct_rate": f"{post_direct['conversions']}/{post_direct['visits']} = {post_direct['rate']:.2f}%",
        "post_promo_rate": f"{post_promo['conversions']}/{post_promo['visits']} = {post_promo['rate']:.2f}%",
        "pre_total_rate": f"{pre_total_conversions}/{pre_total_visits} = {pre_total_rate:.2f}%",
        "post_total_rate": f"{post_total_conversions}/{post_total_visits} = {post_total_rate:.2f}%"
    },
    "weighted_formula": "总体转化率 = 总成交数 / 总访问数",
    "conclusion": "分组转化率均提升（直接访问30%→35%，推广访问10%→12%），但总体转化率下降（26%→16.6%），原因是访问构成从直接访问为主（80%）转变为推广访问为主（80%）",
    "limitation": "不能由该数据证明因果，只能说明相关性"
}

output_dir = Path("outputs/20261008-a1b2c3/A04")
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "analysis.json", "w", encoding="utf-8") as f:
    json.dump(analysis, f, ensure_ascii=False, indent=2)

# 颜色定义
BG = "#0F172A"
CARD_BG = "#1E293B"
CARD_BORDER = "#334155"
TEXT_PRIMARY = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
COLOR_DIRECT = "#3B82F6"
COLOR_PROMO = "#F59E0B"
COLOR_PRE = "#10B981"
COLOR_POST = "#EF4444"

# 构建DSL
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1600" height="1000" padding="(24,28)">')
lines.append(f'    <Column crossAxisAlignment="START">')
lines.append(f'')
lines.append(f'      <!-- 标题 -->')
lines.append(f'      <Container width="1544" height="50" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(12,16)">')
lines.append(f'        <Text color="{TEXT_PRIMARY}" fontSize="24" fontStyle="BOLD">转化变化，为什么不能只看平均？</Text>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'      <SizedBox height="12"/>')
lines.append(f'')
lines.append(f'      <!-- 三图区域 -->')
lines.append(f'      <Row mainAxisAlignment="SPACE_BETWEEN">')
lines.append(f'')
lines.append(f'        <!-- 图1：渠道分组率图 -->')
lines.append(f'        <Container width="480" height="400" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(12,14)">')
lines.append(f'          <Column crossAxisAlignment="START">')
lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="16" fontStyle="BOLD">渠道分组转化率</Text>')
lines.append(f'            <SizedBox height="8"/>')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="12">同一0-100%尺度</Text>')
lines.append(f'            <SizedBox height="12"/>')
lines.append(f'            <!-- 直接访问 -->')
lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="14" fontStyle="BOLD">直接访问</Text>')
lines.append(f'            <SizedBox height="6"/>')
lines.append(f'            <Row crossAxisAlignment="CENTER">')
lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="12">前期</Text>')
lines.append(f'              <SizedBox width="8"/>')
lines.append(f'              <Container width="200" height="24" color="{COLOR_PRE}" borderRadius="4"/>')
lines.append(f'              <SizedBox width="8"/>')
lines.append(f'              <Text color="{TEXT_PRIMARY}" fontSize="14">{pre_direct["rate"]:.1f}%</Text>')
lines.append(f'            </Row>')
lines.append(f'            <SizedBox height="6"/>')
lines.append(f'            <Row crossAxisAlignment="CENTER">')
lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="12">后期</Text>')
lines.append(f'              <SizedBox width="8"/>')
lines.append(f'              <Container width="210" height="24" color="{COLOR_POST}" borderRadius="4"/>')
lines.append(f'              <SizedBox width="8"/>')
lines.append(f'              <Text color="{TEXT_PRIMARY}" fontSize="14">{post_direct["rate"]:.1f}%</Text>')
lines.append(f'            </Row>')
lines.append(f'            <SizedBox height="16"/>')
lines.append(f'            <!-- 推广访问 -->')
lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="14" fontStyle="BOLD">推广访问</Text>')
lines.append(f'            <SizedBox height="6"/>')
lines.append(f'            <Row crossAxisAlignment="CENTER">')
lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="12">前期</Text>')
lines.append(f'              <SizedBox width="8"/>')
lines.append(f'              <Container width="60" height="24" color="{COLOR_PRE}" borderRadius="4"/>')
lines.append(f'              <SizedBox width="8"/>')
lines.append(f'              <Text color="{TEXT_PRIMARY}" fontSize="14">{pre_promo["rate"]:.1f}%</Text>')
lines.append(f'            </Row>')
lines.append(f'            <SizedBox height="6"/>')
lines.append(f'            <Row crossAxisAlignment="CENTER">')
lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="12">后期</Text>')
lines.append(f'              <SizedBox width="8"/>')
lines.append(f'              <Container width="72" height="24" color="{COLOR_POST}" borderRadius="4"/>')
lines.append(f'              <SizedBox width="8"/>')
lines.append(f'              <Text color="{TEXT_PRIMARY}" fontSize="14">{post_promo["rate"]:.1f}%</Text>')
lines.append(f'            </Row>')
lines.append(f'          </Column>')
lines.append(f'        </Container>')
lines.append(f'')
lines.append(f'        <!-- 图2：访问构成堆叠图 -->')
lines.append(f'        <Container width="480" height="400" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(12,14)">')
lines.append(f'          <Column crossAxisAlignment="START">')
lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="16" fontStyle="BOLD">访问构成</Text>')
lines.append(f'            <SizedBox height="8"/>')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="12">每期等长，分段按真实占比</Text>')
lines.append(f'            <SizedBox height="12"/>')
lines.append(f'            <!-- 前期 -->')
lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="14" fontStyle="BOLD">前期</Text>')
lines.append(f'            <SizedBox height="6"/>')
lines.append(f'            <Row crossAxisAlignment="CENTER">')
lines.append(f'              <Container width="320" height="32" color="{COLOR_DIRECT}" borderRadius="4"/>')
lines.append(f'              <Container width="80" height="32" color="{COLOR_PROMO}" borderRadius="4"/>')
lines.append(f'            </Row>')
lines.append(f'            <SizedBox height="4"/>')
lines.append(f'            <Row crossAxisAlignment="CENTER">')
lines.append(f'              <Text color="{COLOR_DIRECT}" fontSize="12">直接访问 80%</Text>')
lines.append(f'              <SizedBox width="16"/>')
lines.append(f'              <Text color="{COLOR_PROMO}" fontSize="12">推广访问 20%</Text>')
lines.append(f'            </Row>')
lines.append(f'            <SizedBox height="16"/>')
lines.append(f'            <!-- 后期 -->')
lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="14" fontStyle="BOLD">后期</Text>')
lines.append(f'            <SizedBox height="6"/>')
lines.append(f'            <Row crossAxisAlignment="CENTER">')
lines.append(f'              <Container width="80" height="32" color="{COLOR_DIRECT}" borderRadius="4"/>')
lines.append(f'              <Container width="320" height="32" color="{COLOR_PROMO}" borderRadius="4"/>')
lines.append(f'            </Row>')
lines.append(f'            <SizedBox height="4"/>')
lines.append(f'            <Row crossAxisAlignment="CENTER">')
lines.append(f'              <Text color="{COLOR_DIRECT}" fontSize="12">直接访问 20%</Text>')
lines.append(f'              <SizedBox width="16"/>')
lines.append(f'              <Text color="{COLOR_PROMO}" fontSize="12">推广访问 80%</Text>')
lines.append(f'            </Row>')
lines.append(f'          </Column>')
lines.append(f'        </Container>')
lines.append(f'')
lines.append(f'        <!-- 图3：总体对照 -->')
lines.append(f'        <Container width="480" height="400" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(12,14)">')
lines.append(f'          <Column crossAxisAlignment="START">')
lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="16" fontStyle="BOLD">总体转化率对照</Text>')
lines.append(f'            <SizedBox height="8"/>')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="12">总体 = 总成交数 / 总访问数</Text>')
lines.append(f'            <SizedBox height="12"/>')
lines.append(f'            <!-- 前期 -->')
lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="14" fontStyle="BOLD">前期</Text>')
lines.append(f'            <SizedBox height="6"/>')
lines.append(f'            <Row crossAxisAlignment="CENTER">')
lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="12">成交</Text>')
lines.append(f'              <SizedBox width="8"/>')
lines.append(f'              <Container width="156" height="28" color="{COLOR_PRE}" borderRadius="4"/>')
lines.append(f'              <SizedBox width="8"/>')
lines.append(f'              <Text color="{TEXT_PRIMARY}" fontSize="14">{pre_total_conversions}</Text>')
lines.append(f'            </Row>')
lines.append(f'            <SizedBox height="4"/>')
lines.append(f'            <Row crossAxisAlignment="CENTER">')
lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="12">访问</Text>')
lines.append(f'              <SizedBox width="8"/>')
lines.append(f'              <Container width="300" height="28" color="{COLOR_PRE}" borderRadius="4"/>')
lines.append(f'              <SizedBox width="8"/>')
lines.append(f'              <Text color="{TEXT_PRIMARY}" fontSize="14">{pre_total_visits}</Text>')
lines.append(f'            </Row>')
lines.append(f'            <SizedBox height="4"/>')
lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="16" fontStyle="BOLD">总体转化率：{pre_total_rate:.1f}%</Text>')
lines.append(f'            <SizedBox height="16"/>')
lines.append(f'            <!-- 后期 -->')
lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="14" fontStyle="BOLD">后期</Text>')
lines.append(f'            <SizedBox height="6"/>')
lines.append(f'            <Row crossAxisAlignment="CENTER">')
lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="12">成交</Text>')
lines.append(f'              <SizedBox width="8"/>')
lines.append(f'              <Container width="100" height="28" color="{COLOR_POST}" borderRadius="4"/>')
lines.append(f'              <SizedBox width="8"/>')
lines.append(f'              <Text color="{TEXT_PRIMARY}" fontSize="14">{post_total_conversions}</Text>')
lines.append(f'            </Row>')
lines.append(f'            <SizedBox height="4"/>')
lines.append(f'            <Row crossAxisAlignment="CENTER">')
lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="12">访问</Text>')
lines.append(f'              <SizedBox width="8"/>')
lines.append(f'              <Container width="300" height="28" color="{COLOR_POST}" borderRadius="4"/>')
lines.append(f'              <SizedBox width="8"/>')
lines.append(f'              <Text color="{TEXT_PRIMARY}" fontSize="14">{post_total_visits}</Text>')
lines.append(f'            </Row>')
lines.append(f'            <SizedBox height="4"/>')
lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="16" fontStyle="BOLD">总体转化率：{post_total_rate:.1f}%</Text>')
lines.append(f'          </Column>')
lines.append(f'        </Container>')
lines.append(f'')
lines.append(f'      </Row>')
lines.append(f'')
lines.append(f'      <SizedBox height="12"/>')
lines.append(f'')
lines.append(f'      <!-- 结论 -->')
lines.append(f'      <Container width="1544" height="120" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(12,16)">')
lines.append(f'        <Column crossAxisAlignment="START">')
lines.append(f'          <Text color="{TEXT_PRIMARY}" fontSize="16" fontStyle="BOLD">结论</Text>')
lines.append(f'          <SizedBox height="6"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="14">分组转化率均提升（直接访问30%→35%，推广访问10%→12%），但总体转化率下降（26%→16.6%）。</Text>')
lines.append(f'          <SizedBox height="4"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="14">原因是访问构成从直接访问为主（80%）转变为推广访问为主（80%）。</Text>')
lines.append(f'          <SizedBox height="4"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="14">限制：不能由该数据证明因果，只能说明相关性。</Text>')
lines.append(f'        </Column>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'      <!-- 数据表 -->')
lines.append(f'      <Container width="1544" height="120" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(12,14)">')
lines.append(f'        <Column crossAxisAlignment="START">')
lines.append(f'          <Text color="{TEXT_PRIMARY}" fontSize="14" fontStyle="BOLD">原始数据</Text>')
lines.append(f'          <SizedBox height="6"/>')
lines.append(f'          <Row mainAxisAlignment="SPACE_BETWEEN">')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="12">期间</Text>')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="12">渠道</Text>')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="12">访问数</Text>')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="12">成交数</Text>')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="12">转化率</Text>')
lines.append(f'          </Row>')

for d in data:
    lines.append(f'          <Row mainAxisAlignment="SPACE_BETWEEN">')
    lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="12">{d["period"]}</Text>')
    lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="12">{d["channel"]}</Text>')
    lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="12">{d["visits"]}</Text>')
    lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="12">{d["conversions"]}</Text>')
    lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="12">{d["rate"]:.1f}%</Text>')
    lines.append(f'          </Row>')

lines.append(f'        </Column>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'    </Column>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl = "\n".join(lines)
with open(output_dir / "conversion-story.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl)

print(f"DSL generated: {len(dsl)} chars")
print(f"Pre total rate: {pre_total_rate:.2f}%")
print(f"Post total rate: {post_total_rate:.2f}%")
