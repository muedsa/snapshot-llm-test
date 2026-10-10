#!/usr/bin/env python3
"""A17 - 四页可实践的DSL入门手册 DSL 生成器"""
import json
from pathlib import Path

# 颜色定义
BG = "#FFFFFF"
CARD_BG = "#F8FAFC"
CARD_BORDER = "#E2E8F0"
TEXT_PRIMARY = "#1E293B"
TEXT_SECONDARY = "#64748B"
COLOR_ACCENT = "#3B82F6"
COLOR_CODE = "#1E293B"

output_dir = Path("outputs/20261008-a1b2c3/A17")
output_dir.mkdir(parents=True, exist_ok=True)

# 示例DSL
examples = [
    {
        "id": "example-01",
        "title": "基本调用契约",
        "dsl": """<Snapshot type="png">
  <Container width="400" height="240" color="#FFFFFF">
    <Text color="#1E293B" fontSize="24">Hello Snapshot</Text>
  </Container>
</Snapshot>""",
        "purpose": "展示最基本的Snapshot DSL结构"
    },
    {
        "id": "example-02",
        "title": "Row与Column布局",
        "dsl": """<Snapshot type="png">
  <Container width="400" height="240" color="#FFFFFF">
    <Row>
      <Container width="100" height="100" color="#3B82F6"/>
      <Container width="100" height="100" color="#10B981"/>
    </Row>
  </Container>
</Snapshot>""",
        "purpose": "展示Row横向布局"
    },
    {
        "id": "example-03",
        "title": "富文本",
        "dsl": """<Snapshot type="png">
  <Container width="400" height="240" color="#FFFFFF">
    <Text fontSize="24">
      <Text color="#3B82F6" fontStyle="BOLD">富文本</Text>
      <Text color="#64748B">示例</Text>
    </Text>
  </Container>
</Snapshot>""",
        "purpose": "展示富文本嵌套"
    },
    {
        "id": "example-04",
        "title": "滤镜效果",
        "dsl": """<Snapshot type="png">
  <Container width="400" height="240" color="#FFFFFF">
    <ImageFiltered sigmaX="4" sigmaY="4">
      <Container width="200" height="100" color="#3B82F6"/>
    </ImageFiltered>
  </Container>
</Snapshot>""",
        "purpose": "展示高斯模糊滤镜"
    }
]

# 生成4张教学页
pages = [
    {
        "id": "handbook-01",
        "title": "第1页：真实调用契约",
        "content": [
            "Snapshot DSL是一种声明式图片描述语言，通过POST请求发送到服务。",
            "请求体是UTF-8纯文本，不是JSON。",
            "成功时响应体是图片二进制（PNG/JPEG/WebP）。",
            "错误时返回JSON，包含code、message、requestId。",
            "常见错误：400 PARSE_ERROR、413 REQUEST_TOO_LARGE、401未授权、429限流。"
        ],
        "example": 0
    },
    {
        "id": "handbook-02",
        "title": "第2页：布局基础",
        "content": [
            "根节点是<Snapshot>，必须指定width和height。",
            "Container可以设置width、height、color、padding等属性。",
            "Row横向排列子元素，Column纵向排列子元素。",
            "Expanded在Flex中占据剩余空间。",
            "Stack允许子元素重叠，Positioned定位子元素。"
        ],
        "example": 1
    },
    {
        "id": "handbook-03",
        "title": "第3页：文本与富文本",
        "content": [
            "Text标签支持color、fontSize、fontStyle等属性。",
            "Raw标签保留空白字符，不进行trim。",
            "富文本通过嵌套Text实现不同样式。",
            "颜色格式：#RGB、#RRGGBB、#RRGGBBAA（尾部alpha）。",
            "注意：8位颜色按CSS的#RRGGBBAA解析，不是#AARRGGBB。"
        ],
        "example": 2
    },
    {
        "id": "handbook-04",
        "title": "第4页：滤镜与自检",
        "content": [
            "ImageFiltered对子树应用高斯模糊。",
            "BackdropFilter只模糊背景，不影响前景。",
            "ColorFiltered对子树应用颜色混合。",
            "ClipRRect/ClipOval裁剪子树。",
            "视觉自检：必须实际查看渲染结果，不能只检查XML。"
        ],
        "example": 3
    }
]

for page in pages:
    ex = examples[page["example"]]
    lines = []
    lines.append(f'<Snapshot background="{BG}" type="png">')
    lines.append(f'  <Container width="1200" height="1600" padding="(48,48)">')
    lines.append(f'    <Column crossAxisAlignment="START">')
    lines.append(f'      <Text color="{TEXT_PRIMARY}" fontSize="32" fontStyle="BOLD">{page["title"]}</Text>')
    lines.append(f'      <SizedBox height="24"/>')
    
    for content in page["content"]:
        lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="24">{content}</Text>')
        lines.append(f'      <SizedBox height="12"/>')
    
    lines.append(f'      <SizedBox height="24"/>')
    lines.append(f'      <Text color="{TEXT_PRIMARY}" fontSize="24" fontStyle="BOLD">示例：{ex["title"]}</Text>')
    lines.append(f'      <SizedBox height="12"/>')
    lines.append(f'      <Container width="400" height="240" background="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}"/>')
    lines.append(f'      <SizedBox height="12"/>')
    lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="20">完整示例见 {ex["id"]}.png</Text>')
    lines.append(f'    </Column>')
    lines.append(f'  </Container>')
    lines.append(f'</Snapshot>')
    
    dsl = "\n".join(lines)
    with open(output_dir / f'{page["id"]}.snapshot', "w", encoding="utf-8") as f:
        f.write(dsl)

# 生成4张示例图
for ex in examples:
    lines = []
    lines.append(f'<Snapshot type="png">')
    lines.append(f'  <Container width="400" height="240" color="#FFFFFF">')
    
    if ex["id"] == "example-01":
        lines.append(f'    <Text color="#1E293B" fontSize="24">Hello Snapshot</Text>')
    elif ex["id"] == "example-02":
        lines.append(f'    <Row>')
        lines.append(f'      <Container width="100" height="100" color="#3B82F6"/>')
        lines.append(f'      <Container width="100" height="100" color="#10B981"/>')
        lines.append(f'    </Row>')
    elif ex["id"] == "example-03":
        lines.append(f'    <Text fontSize="24">')
        lines.append(f'      <Text color="#3B82F6" fontStyle="BOLD">富文本</Text>')
        lines.append(f'      <Text color="#64748B">示例</Text>')
        lines.append(f'    </Text>')
    elif ex["id"] == "example-04":
        lines.append(f'    <ImageFiltered sigmaX="4" sigmaY="4">')
        lines.append(f'      <Container width="200" height="100" color="#3B82F6"/>')
        lines.append(f'    </ImageFiltered>')
    
    lines.append(f'  </Container>')
    lines.append(f'</Snapshot>')
    
    dsl = "\n".join(lines)
    with open(output_dir / f'{ex["id"]}.snapshot', "w", encoding="utf-8") as f:
        f.write(dsl)

# 保存examples.json
examples_data = []
for ex in examples:
    examples_data.append({
        "id": ex["id"],
        "title": ex["title"],
        "purpose": ex["purpose"],
        "dsl": ex["dsl"]
    })

with open(output_dir / "examples.json", "w", encoding="utf-8") as f:
    json.dump(examples_data, f, ensure_ascii=False, indent=2)

# 保存sources.md
sources = """# 技术来源

## 服务指南
- URL: https://open-snapshot.muedsa.com/ai-guide.md
- 内容：API调用方式、请求体格式、错误处理

## DSL文档
- URL: https://snapshot.muedsa.com/
- 内容：Widget树、布局、绘制

## 标签参考
- URL: https://snapshot.muedsa.com/reference/parser-tags/
- 内容：所有支持的标签和属性

## 示例
- 第1页：基本调用契约
- 第2页：Row与Column布局
- 第3页：富文本
- 第4页：滤镜效果
"""

with open(output_dir / "sources.md", "w", encoding="utf-8") as f:
    f.write(sources)

print("All DSLs generated")
