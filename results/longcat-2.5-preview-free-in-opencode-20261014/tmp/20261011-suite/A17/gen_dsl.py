from pathlib import Path

W, H = 1200, 1600
MARGIN = 48
FONT = "Noto Sans CJK SC"
BG = "#FFFFFF"
CODE_BG = "#F1F5F9"
TEXT_DARK = "#1E293B"
TEXT_MED = "#64748B"
BLUE = "#3B82F6"

pages = [
    ("01", "真实调用契约", "POST /snapshot 请求体是UTF-8纯文本DSL，响应是图片二进制。", "error handling"),
    ("02", "根尺寸与有界布局", "Column/Row需要父级有界约束，Stack用Positioned定位。", "layout"),
    ("03", "Raw与富文本", "Raw保留空白，Text自动trim，富文本用嵌套Text。", "text"),
    ("04", "滤镜与视觉自检", "BackdropFilter只模糊背景，ImageFiltered模糊子树。", "filter"),
]

output_dir = Path('outputs/20261011-suite/A17')
output_dir.mkdir(parents=True, exist_ok=True)

for num, title, desc, topic in pages:
    dsl_parts = []
    dsl_parts.append(f'<Snapshot type="png" background="{BG}">')
    dsl_parts.append(f'  <Column mainAxisSize="MAX" height="{H}" width="{W}">')

    # Header
    dsl_parts.append(f'    <Container height="100" padding="({MARGIN},{MARGIN})">')
    dsl_parts.append(f'      <Column crossAxisAlignment="START">')
    dsl_parts.append(f'        <Text text="从文字到图片 · Snapshot DSL入门" color="{TEXT_DARK}" fontSize="32" fontStyle="BOLD"/>')
    dsl_parts.append(f'        <Text text="第{num}页：{title}" color="{BLUE}" fontSize="28"/>')
    dsl_parts.append(f'      </Column>')
    dsl_parts.append(f'    </Container>')

    # Description
    dsl_parts.append(f'    <Container height="80" padding="({MARGIN},{MARGIN})">')
    dsl_parts.append(f'      <Text text="{desc}" color="{TEXT_DARK}" fontSize="24"/>')
    dsl_parts.append(f'    </Container>')

    # Code example
    dsl_parts.append(f'    <Container height="400" color="{CODE_BG}" borderRadius="8" padding="(16,16)">')
    dsl_parts.append(f'      <Column crossAxisAlignment="START">')
    dsl_parts.append(f'        <Text text="示例DSL（8-12行）" color="{TEXT_MED}" fontSize="20"/>')
    dsl_parts.append(f'        <SizedBox height="16"/>')
    dsl_parts.append(f'        <Text text="&lt;Snapshot type=&quot;png&quot;&gt;" color="{TEXT_DARK}" fontSize="20"/>')
    dsl_parts.append(f'        <Text text="  &lt;Column&gt;" color="{TEXT_DARK}" fontSize="20"/>')
    dsl_parts.append(f'        <Text text="    &lt;Container width=&quot;400&quot; height=&quot;240&quot; color=&quot;#3B82F6&quot;&gt;" color="{TEXT_DARK}" fontSize="20"/>')
    dsl_parts.append(f'        <Text text="      &lt;Text text=&quot;Hello&quot; color=&quot;#FFFFFF&quot; fontSize=&quot;32&quot;/&gt;" color="{TEXT_DARK}" fontSize="20"/>')
    dsl_parts.append(f'        <Text text="    &lt;/Container&gt;" color="{TEXT_DARK}" fontSize="20"/>')
    dsl_parts.append(f'        <Text text="  &lt;/Column&gt;" color="{TEXT_DARK}" fontSize="20"/>')
    dsl_parts.append(f'        <Text text="&lt;/Snapshot&gt;" color="{TEXT_DARK}" fontSize="20"/>')
    dsl_parts.append(f'      </Column>')
    dsl_parts.append(f'    </Container>')

    # Rendered result placeholder
    dsl_parts.append(f'    <SizedBox height="24"/>')
    dsl_parts.append(f'    <Container height="300" color="{CODE_BG}" borderRadius="8" padding="(16,16)">')
    dsl_parts.append(f'      <Column crossAxisAlignment="START">')
    dsl_parts.append(f'        <Text text="渲染结果" color="{TEXT_MED}" fontSize="20"/>')
    dsl_parts.append(f'        <SizedBox height="16"/>')
    dsl_parts.append(f'        <Container width="400" height="240" color="{BLUE}" borderRadius="8">')
    dsl_parts.append(f'          <Column crossAxisAlignment="CENTER">')
    dsl_parts.append(f'            <Text text="Hello" color="#FFFFFF" fontSize="32"/>')
    dsl_parts.append(f'          </Column>')
    dsl_parts.append(f'        </Container>')
    dsl_parts.append(f'      </Column>')
    dsl_parts.append(f'    </Container>')

    # Footer
    dsl_parts.append(f'    <Container height="60" padding="({MARGIN},{MARGIN})">')
    dsl_parts.append(f'      <Text text="页码 {num}/4" color="{TEXT_MED}" fontSize="20"/>')
    dsl_parts.append(f'    </Container>')

    dsl_parts.append('  </Column>')
    dsl_parts.append('</Snapshot>')

    dsl = '\n'.join(dsl_parts)
    with open(f'tmp/20261011-suite/A17/handbook-{num}.snapshot', 'w', encoding='utf-8') as f:
        f.write(dsl)

print("Generated 4 handbook pages")

# Generate 4 examples
examples = [
    ("01", "error_handling", '<Snapshot type="png" width="400" height="240" background="#FFFFFF">\n  <Column>\n    <Container width="400" height="240" color="#3B82F6" borderRadius="8">\n      <Text text="Hello" color="#FFFFFF" fontSize="32"/>\n    </Container>\n  </Column>\n</Snapshot>'),
    ("02", "layout", '<Snapshot type="png" width="400" height="240" background="#FFFFFF">\n  <Column>\n    <Container width="400" height="120" color="#10B981" borderRadius="8">\n      <Text text="Top" color="#FFFFFF" fontSize="24"/>\n    </Container>\n    <Container width="400" height="120" color="#F59E0B" borderRadius="8">\n      <Text text="Bottom" color="#FFFFFF" fontSize="24"/>\n    </Container>\n  </Column>\n</Snapshot>'),
    ("03", "text", '<Snapshot type="png" width="400" height="240" background="#FFFFFF">\n  <Column>\n    <Container width="400" height="240" color="#1E293B" borderRadius="8">\n      <Text text="Raw text" color="#FFFFFF" fontSize="24"/>\n    </Container>\n  </Column>\n</Snapshot>'),
    ("04", "filter", '<Snapshot type="png" width="400" height="240" background="#FFFFFF">\n  <Column>\n    <Container width="400" height="240" color="#8B5CF6" borderRadius="8">\n      <Text text="Filter" color="#FFFFFF" fontSize="24"/>\n    </Container>\n  </Column>\n</Snapshot>'),
]

for num, topic, dsl in examples:
    with open(f'tmp/20261011-suite/A17/example-{num}.snapshot', 'w', encoding='utf-8') as f:
        f.write(dsl)

print("Generated 4 examples")

# Save examples.json
import json
ex_json = {
    "schema_version": 1,
    "task_id": "A17",
    "path_base": "output_dir",
    "examples": [
        {"page": 1, "file": "example-01.png", "topic": "error_handling"},
        {"page": 2, "file": "example-02.png", "topic": "layout"},
        {"page": 3, "file": "example-03.png", "topic": "text"},
        {"page": 4, "file": "example-04.png", "topic": "filter"}
    ]
}
with open(output_dir / 'examples.json', 'w', encoding='utf-8') as f:
    json.dump(ex_json, f, ensure_ascii=False, indent=2)
print("Saved examples.json")
