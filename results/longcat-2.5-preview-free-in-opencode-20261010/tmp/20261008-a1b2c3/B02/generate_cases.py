#!/usr/bin/env python3
"""B02 - GreenLeaf 有机食品 视觉生态 DSL 生成器"""
import json
from pathlib import Path

output_dir = Path("outputs/20261008-a1b2c3/B02")
output_dir.mkdir(parents=True, exist_ok=True)

cases = [
    {"id": "case-01", "title": "GreenLeaf 品牌标识", "scenario": "品牌核心标识，用于所有触点", "w": 800, "h": 800, "bg": "#F0FDF4", "a1": "#16A34A", "a2": "#F59E0B", "content": ["GreenLeaf", "有机 · 自然 · 新鲜"]},
    {"id": "case-02", "title": "产品包装", "scenario": "有机蔬菜包装盒设计", "w": 600, "h": 900, "bg": "#FFFFFF", "a1": "#16A34A", "a2": "#F59E0B", "content": ["有机西兰花", "500g", "¥29.9"]},
    {"id": "case-03", "title": "社交媒体海报", "scenario": "Instagram产品宣传", "w": 1080, "h": 1080, "bg": "#F0FDF4", "a1": "#16A34A", "a2": "#DC2626", "content": ["新品上市", "有机草莓", "限时8折"]},
    {"id": "case-04", "title": "官网首页", "scenario": "电子商务网站首页Banner", "w": 1440, "h": 600, "bg": "#FFFFFF", "a1": "#16A34A", "a2": "#0EA5E9", "content": ["GreenLeaf", "从农场到餐桌", "立即购买"]},
    {"id": "case-05", "title": "移动应用", "scenario": "手机端购物界面", "w": 390, "h": 844, "bg": "#F0FDF4", "a1": "#16A34A", "a2": "#F59E0B", "content": ["今日推荐", "有机蔬菜礼盒", "¥199"]},
    {"id": "case-06", "title": "电子邮件", "scenario": "促销邮件Header", "w": 600, "h": 400, "bg": "#FFFFFF", "a1": "#16A34A", "a2": "#DC2626", "content": ["限时特惠", "全场满199减50"]},
    {"id": "case-07", "title": "线下海报", "scenario": "超市促销海报", "w": 800, "h": 1200, "bg": "#F0FDF4", "a1": "#16A34A", "a2": "#F59E0B", "content": ["周末特惠", "有机水果买二送一"]},
    {"id": "case-08", "title": "会员卡", "scenario": "会员积分卡背面", "w": 856, "h": 540, "bg": "#16A34A", "a1": "#FFFFFF", "a2": "#F59E0B", "content": ["GreenLeaf Member", "积分兑换好礼"]},
    {"id": "case-09", "title": "配送箱", "scenario": "外卖配送箱贴纸", "w": 500, "h": 500, "bg": "#FFFFFF", "a1": "#16A34A", "a2": "#16A34A", "content": ["GreenLeaf", "冷链配送 · 新鲜直达"]},
    {"id": "case-10", "title": "季度报告", "scenario": "品牌季度销售报告封面", "w": 1200, "h": 800, "bg": "#F0FDF4", "a1": "#16A34A", "a2": "#0EA5E9", "content": ["2026 Q3 报告", "销售增长 +23%"]},
]

portfolio = []
for case in cases:
    case_dir = output_dir / case["id"]
    case_dir.mkdir(parents=True, exist_ok=True)
    w, h, bg, a1, a2 = case["w"], case["h"], case["bg"], case["a1"], case["a2"]
    lines = []
    lines.append(f'<Snapshot background="{bg}" type="png">')
    lines.append(f'  <Container width="{w}" height="{h}" padding="(40,40)">')
    lines.append(f'    <Column crossAxisAlignment="START">')
    lines.append(f'      <Text color="{a1}" fontSize="42" fontStyle="BOLD">{case["content"][0]}</Text>')
    lines.append(f'      <SizedBox height="16"/>')
    lines.append(f'      <Text color="{a2}" fontSize="28">{case["content"][1]}</Text>')
    if len(case["content"]) > 2:
        lines.append(f'      <Text color="{a1}" fontSize="22">{case["content"][2]}</Text>')
    lines.append(f'      <SizedBox height="32"/>')
    lines.append(f'      <Container width="{w-80}" height="150" background="{a1}22" borderRadius="10" border="2 SOLID {a1}">')
    lines.append(f'        <Column crossAxisAlignment="CENTER" mainAxisAlignment="CENTER">')
    lines.append(f'          <Text color="{a1}" fontSize="28" fontStyle="BOLD">GreenLeaf</Text>')
    lines.append(f'        </Column>')
    lines.append(f'      </Container>')
    lines.append(f'    </Column>')
    lines.append(f'  </Container>')
    lines.append(f'</Snapshot>')
    dsl = "\n".join(lines)
    with open(case_dir / "final.snapshot", "w", encoding="utf-8") as f:
        f.write(dsl)
    case_md = f"""# {case['title']}

## 场景
{case['scenario']}

## 尺寸
{w}×{h}
"""
    with open(case_dir / "case.md", "w", encoding="utf-8") as f:
        f.write(case_md)
    portfolio.append({"id": case["id"], "title": case["title"], "scenario": case["scenario"], "width": w, "height": h, "file": f"{case['id']}/final.png"})

with open(output_dir / "portfolio.json", "w", encoding="utf-8") as f:
    json.dump(portfolio, f, ensure_ascii=False, indent=2)

brief = """# GreenLeaf 有机食品 项目简报

## 项目定位
GreenLeaf是一家专注于有机食品配送的社区电商，服务对象为注重健康生活的城市家庭。

## 视觉生态
10件作品覆盖品牌标识、产品包装、社交媒体、官网、移动应用、邮件、线下海报、会员卡、配送箱和季度报告。

## 设计系统
- 主色：#16A34A（有机绿）
- 辅色：#F59E0B（活力橙）
- 背景：#F0FDF4（浅绿白）
- 字体：无衬线，层次清晰
"""
with open(output_dir / "project-brief.md", "w", encoding="utf-8") as f:
    f.write(brief)

design_system = {"colors": {"primary": "#16A34A", "secondary": "#F59E0B", "background": "#F0FDF4"}, "fonts": {"title": 42, "subtitle": 28, "body": 22}, "border_radius": 10}
with open(output_dir / "design-system.json", "w", encoding="utf-8") as f:
    json.dump(design_system, f, ensure_ascii=False, indent=2)

touchpoints = [{"case": f"case-{i+1:02d}", "touchpoint": cases[i]["scenario"]} for i in range(10)]
with open(output_dir / "touchpoint-map.json", "w", encoding="utf-8") as f:
    json.dump(touchpoints, f, ensure_ascii=False, indent=2)

print(f"Generated {len(cases)} cases")
