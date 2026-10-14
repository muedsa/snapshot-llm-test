import json
from pathlib import Path

OUTPUT_BASE = Path('outputs/20261011-suite')
TEMP_BASE = Path('tmp/20261011-suite')

# B03: DSL创意边界 - 10种不同视觉探索
b03_cases = [
    {"id": "case-01", "title": "渐变光谱", "size": [1080, 1080], "desc": "探索渐变的无限可能"},
    {"id": "case-02", "title": "几何构成", "size": [1200, 800], "desc": "基础形状的艺术组合"},
    {"id": "case-03", "title": "层次叠加", "size": [1000, 1000], "desc": "透明度与深度的游戏"},
    {"id": "case-04", "title": "动态平衡", "size": [1440, 900], "desc": "不对称中的和谐"},
    {"id": "case-05", "title": "节奏重复", "size": [800, 1200], "desc": "韵律与重复之美"},
    {"id": "case-06", "title": "空间深度", "size": [1200, 800], "desc": "阴影与立体感"},
    {"id": "case-07", "title": "色彩对话", "size": [1080, 1080], "desc": "对比色与情感"},
    {"id": "case-08", "title": "极简主义", "size": [1000, 1000], "desc": "少即是多"},
    {"id": "case-09", "title": "复杂系统", "size": [1440, 900], "desc": "精密结构的魅力"},
    {"id": "case-10", "title": "抽象表现", "size": [1200, 1200], "desc": "自由形态的探索"},
]

# B04: 视觉特辑 - 以"城市夜景"为主题
b04_cases = [
    {"id": "case-01", "title": "天际线", "size": [1920, 1080], "desc": "城市轮廓"},
    {"id": "case-02", "title": "街道灯光", "size": [1080, 1350], "desc": "温暖街灯"},
    {"id": "case-03", "title": "车流轨迹", "size": [1440, 900], "desc": "光的轨迹"},
    {"id": "case-04", "title": "建筑立面", "size": [800, 1200], "desc": "垂直空间"},
    {"id": "case-05", "title": "夜市繁华", "size": [1200, 800], "desc": "人声鼎沸"},
    {"id": "case-06", "title": "雨中倒影", "size": [1080, 1080], "desc": "镜面反射"},
    {"id": "case-07", "title": "屋顶花园", "size": [1200, 900], "desc": "绿洲"},
    {"id": "case-08", "title": "地铁站台", "size": [800, 600], "desc": "交通枢纽"},
    {"id": "case-09", "title": "广告牌", "size": [1080, 1350], "desc": "光影交错"},
    {"id": "case-10", "title": "黎明前", "size": [1920, 1080], "desc": "破晓时分"},
]

# B05: 从零构想产品 - "智能水瓶"
b05_cases = [
    {"id": "case-01", "title": "产品发布海报", "size": [1080, 1350], "desc": "HydraSmart 智能水瓶"},
    {"id": "case-02", "title": "功能展示图", "size": [1200, 800], "desc": "核心功能一目了然"},
    {"id": "case-03", "title": "APP界面", "size": [375, 667], "desc": "移动端体验"},
    {"id": "case-04", "title": "数据追踪", "size": [1200, 900], "desc": "饮水数据可视化"},
    {"id": "case-05", "title": "提醒通知", "size": [375, 667], "desc": "智能提醒"},
    {"id": "case-06", "title": "配色方案", "size": [1000, 1000], "desc": "多色选择"},
    {"id": "case-07", "title": "包装展示", "size": [800, 1200], "desc": "环保包装"},
    {"id": "case-08", "title": "使用场景", "size": [1200, 800], "desc": "办公室/户外"},
    {"id": "case-09", "title": "技术规格", "size": [1440, 900], "desc": "详细参数"},
    {"id": "case-10", "title": "品牌故事", "size": [1080, 1350], "desc": "健康理念"},
]

# B06: 日常信息重塑
b06_cases = [
    {"id": "case-01", "title": "天气预报卡片", "size": [800, 600], "desc": "今日天气一目了然"},
    {"id": "case-02", "title": "待办事项清单", "size": [600, 800], "desc": "高效任务管理"},
    {"id": "case-03", "title": "日历视图", "size": [1200, 900], "desc": "月度日程安排"},
    {"id": "case-04", "title": "健身计划", "size": [800, 1200], "desc": "每周训练安排"},
    {"id": "case-05", "title": "食谱卡片", "size": [1080, 1350], "desc": "美味与健康"},
    {"id": "case-06", "title": "预算追踪", "size": [1200, 800], "desc": "收支可视化"},
    {"id": "case-07", "title": "阅读清单", "size": [800, 1000], "desc": "书单推荐"},
    {"id": "case-08", "title": "旅行清单", "size": [800, 1200], "desc": "出行准备"},
    {"id": "case-09", "title": "情绪日记", "size": [600, 800], "desc": "每日心情记录"},
    {"id": "case-10", "title": "周总结报告", "size": [1200, 900], "desc": "数据驱动的复盘"},
]

def gen_case_dsl(case, palette):
    cid = case["id"]
    title = case["title"]
    w, h = case["size"]
    desc = case["desc"]
    bg = palette["bg"]
    primary = palette["primary"]
    secondary = palette["secondary"]
    text = palette["text"]

    dsl = f'''<Snapshot type="png" width="{w}" height="{h}" background="{bg}">
  <Column mainAxisSize="MAX" height="{h}" width="{w}">
    <Container height="100" padding="(32,32)">
      <Column crossAxisAlignment="START">
        <Text text="{title}" color="{text}" fontSize="36" fontStyle="BOLD"/>
        <Text text="{desc}" color="{secondary}" fontSize="18"/>
      </Column>
    </Container>
    <Container height="{h-180}" padding="(32,32)">
      <Column crossAxisAlignment="CENTER">
        <Container width="200" height="200" color="{primary}" borderRadius="16"/>
        <SizedBox height="20"/>
        <Container width="160" height="160" color="{secondary}" borderRadius="12"/>
      </Column>
    </Container>
  </Column>
</Snapshot>'''
    return dsl

palettes = [
    {"bg": "#0F172A", "primary": "#3B82F6", "secondary": "#10B981", "text": "#FFFFFF"},
    {"bg": "#FFFFFF", "primary": "#8B5CF6", "secondary": "#F59E0B", "text": "#1E293B"},
    {"bg": "#1E293B", "primary": "#EF4444", "secondary": "#06B6D4", "text": "#F8FAFC"},
]

all_tasks = [("B03", b03_cases), ("B04", b04_cases), ("B05", b05_cases), ("B06", b06_cases)]

for task_id, cases in all_tasks:
    task_dir = OUTPUT_BASE / task_id
    temp_dir = TEMP_BASE / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    for i, case in enumerate(cases):
        cid = case["id"]
        case_dir = task_dir / cid
        case_dir.mkdir(parents=True, exist_ok=True)
        temp_case_dir = temp_dir / cid
        temp_case_dir.mkdir(parents=True, exist_ok=True)

        palette = palettes[i % len(palettes)]
        dsl = gen_case_dsl(case, palette)

        with open(temp_case_dir / 'final.snapshot', 'w', encoding='utf-8') as f:
            f.write(dsl)

        case_md = f"""# {case["title"]}
## 场景：{case["desc"]}
## 色彩方案：{palette["primary"]}
"""
        with open(case_dir / 'case.md', 'w', encoding='utf-8') as f:
            f.write(case_md)

    # Save portfolio.json
    portfolio = {
        "schema_version": 1,
        "task_id": task_id,
        "path_base": "output_dir",
        "cases": [{"id": c["id"], "title": c["title"], "size": c["size"]} for c in cases]
    }
    with open(task_dir / 'portfolio.json', 'w', encoding='utf-8') as f:
        json.dump(portfolio, f, ensure_ascii=False, indent=2)

    print(f"Generated {task_id}: {len(cases)} cases")

print("All B03-B06 cases generated")
