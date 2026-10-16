import json, os, re

W, H = 1200, 1600
M = 48
FONT = "Noto Sans CJK SC,Inter"
FONT_I = "Inter"

EXAMPLES = [
    {
        "id": "ex-01",
        "title": "示例 1：提交 DSL 并获取图片",
        "subtitle": "POST /snapshot 发送纯文本 DSL，服务返回图片二进制",
        "dsl": '''<Snapshot background="#FFFFFF" type="png">
  <Container width="400" height="240" color="#F3F6FB" borderRadius="16" alignment="CENTER">
    <Stack alignment="CENTER">
      <Text color="#1E3A8A" fontSize="32" fontStyle="BOLD">Hello</Text>
      <Text color="#475569" fontSize="18">Snapshot PNG</Text>
    </Stack>
  </Container>
</Snapshot>''',
        "explanation": "把类 DOM 文本作为 UTF-8 纯文本 POST 到 /snapshot，服务返回图片二进制（PNG）。Content-Type 为 text/plain; charset=utf-8，不要发送 JSON。",
    },
    {
        "id": "ex-02",
        "title": "示例 2：Stack 与 Positioned 定位",
        "subtitle": "Stack 层叠，Positioned 用 left/top 绝对定位子节点",
        "dsl": '''<Snapshot background="#FFFFFF" type="png">
  <Container width="400" height="240" color="#FFFFFF">
    <Stack alignment="TOP_LEFT">
      <Positioned left="20" top="20" width="80" height="60">
        <Container color="#2563EB" borderRadius="8"/>
      </Positioned>
      <Positioned left="120" top="40" width="80" height="60">
        <Container color="#3B82F6" borderRadius="8"/>
      </Positioned>
      <Positioned left="220" top="60" width="80" height="60">
        <Container color="#60A5FA" borderRadius="8"/>
      </Positioned>
      <Positioned left="280" top="100" width="80" height="60">
        <Container color="#93C5FD" borderRadius="8"/>
      </Positioned>
    </Stack>
  </Container>
</Snapshot>''',
        "explanation": "Stack 按层叠顺序绘制子节点，Positioned 用 left/top 精确放置。适合仪表盘、驾驶舱等固定位置布局。",
    },
    {
        "id": "ex-03",
        "title": "示例 3：Raw 与 CDATA 保留原文",
        "subtitle": "Raw 不做首尾空白修剪；CDATA 包裹包含 &lt; &gt; 的原始文本",
        "dsl": '''<Snapshot background="#FFFFFF" type="png">
  <Container width="400" height="240" color="#F8F9FC" padding="20" borderRadius="12">
    <Stack alignment="TOP_LEFT">
      <Text color="#14233C" fontSize="20" fontStyle="BOLD">代码片段</Text>
      <Text color="#0F172A" fontSize="16">
        <Raw>&lt;Snapshot&gt;&lt;/Snapshot&gt;</Raw>
      </Text>
      <Text color="#64748B" fontSize="14">尖括号原样保留，不做 HTML 实体解码。</Text>
    </Stack>
  </Container>
</Snapshot>''',
        "explanation": "Raw 保留空白与原始字符；CDATA 包裹包含 &lt; &gt; 的原始文本，不做 HTML 实体解码，适合展示代码片段。",
    },
    {
        "id": "ex-04",
        "title": "示例 4：半透明白底卡片",
        "subtitle": "半透明白底容器与圆角，适合卡片式布局",
        "dsl": '''<Snapshot background="#1E3A8A" type="png">
  <SizedBox width="400" height="240">
    <Stack alignment="TOP_LEFT">
      <Positioned left="60" top="60" width="280" height="120">
        <Container color="#FFFFFF44" borderRadius="16">
          <Text color="#FFFFFF" fontSize="22" fontStyle="BOLD" textAlign="CENTER">半透明卡片</Text>
        </Container>
      </Positioned>
    </Stack>
  </SizedBox>
</Snapshot>''',
        "explanation": "半透明白底容器（#FFFFFF44）配合圆角边框，可在深色背景上形成卡片层次感，适合卡片式 UI 设计。",
    },
]

def escape_for_xml(text):
    return (text.replace("&", "&amp;")
              .replace("<", "&lt;")
              .replace(">", "&gt;"))

def build_handbook_page(idx, ex):
    el = []
    el.append('<Snapshot background="#FFFFFF" type="png">')
    el.append(f'  <SizedBox width="{W}" height="{H}">')
    el.append('    <Stack alignment="TOP_LEFT" clipBehavior="NONE">')
    el.append(f'      <Positioned left="{M}" top="{M}" width="{W-2*M}" height="56">')
    el.append(f'        <Text color="#14233C" fontSize="34" fontStyle="BOLD" fontFamily="{FONT}">{escape_for_xml(ex["title"])}</Text>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{M}" top="{M+64}" width="{W-2*M}" height="30">')
    el.append(f'        <Text color="#64748B" fontSize="20" fontFamily="{FONT}">{escape_for_xml(ex["subtitle"])}</Text>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{W-M-100}" top="{H-48}" width="100">')
    el.append(f'        <Text color="#94A3B8" fontSize="18" fontFamily="{FONT}" textAlign="RIGHT">第{idx+1}页</Text>')
    el.append(f'      </Positioned>')
    code_x = M
    code_y = M + 110
    code_w = W - 2*M - 320
    code_h = 320
    el.append(f'      <Positioned left="{code_x}" top="{code_y}" width="{code_w}" height="{code_h}">')
    el.append(f'        <Container color="#F8F9FC" border="1 SOLID #E2E8F0" borderRadius="10"/>')
    el.append(f'      </Positioned>')
    code_lines = ex["dsl"].split("\n")
    display_lines = code_lines[:18]
    if len(code_lines) > 18:
        display_lines.append("      ... 省略外层包装 ...")
    y = code_y + 16
    for line in display_lines:
        escaped = escape_for_xml(line)
        el.append(f'        <Positioned left="{code_x+16}" top="{y}" width="{code_w-32}" height="18">')
        el.append(f'          <Text color="#1E293B" fontSize="15" fontFamily="{FONT_I}">{escaped}</Text>')
        el.append(f'        </Positioned>')
        y += 18
    ex_x = W - M - 310
    ex_y = M + 110
    el.append(f'      <Positioned left="{ex_x}" top="{ex_y}" width="400" height="240">')
    el.append(f'        <Container color="#FFFFFF" border="1 SOLID #CBD5E1" borderRadius="10"/>')
    el.append(f'      </Positioned>')
    m = re.search(r'<Snapshot[^>]*>(.*)</Snapshot>', ex["dsl"], re.DOTALL)
    inner_content = m.group(1).strip() if m else ex["dsl"]
    el.append(f'      <Positioned left="{ex_x+10}" top="{ex_y+20}" width="380" height="220">')
    el.append(f'        <Container color="#FFFFFF" borderRadius="8">')
    el.append(f'          <Stack alignment="TOP_LEFT">')
    el.append(inner_content)
    el.append(f'          </Stack>')
    el.append(f'        </Container>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{M}" top="{code_y+code_h+40}" width="{W-2*M}" height="26">')
    el.append(f'        <Text color="#14233C" fontSize="22" fontStyle="BOLD" fontFamily="{FONT}">关键点</Text>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{M}" top="{code_y+code_h+74}" width="{W-2*M}" height="130">')
    el.append(f'        <Text color="#334155" fontSize="20" fontFamily="{FONT}" softWrap="true">{escape_for_xml(ex["explanation"])}</Text>')
    el.append(f'      </Positioned>')
    el.append('    </Stack>')
    el.append('  </SizedBox>')
    el.append('</Snapshot>')
    return "\n".join(el)

os.makedirs("tmp/run-20261016/A17", exist_ok=True)
os.makedirs("outputs/run-20261016/A17", exist_ok=True)

examples_json = []
for i, ex in enumerate(EXAMPLES):
    page_name = f"handbook-{i+1:02d}"
    ex_name = f"example-{i+1:02d}"
    dsl = build_handbook_page(i, ex)
    with open(f"tmp/run-20261016/A17/{page_name}.v1.snapshot", "w", encoding="utf-8") as f:
        f.write(dsl)
    with open(f"tmp/run-20261016/A17/{ex_name}.v1.snapshot", "w", encoding="utf-8") as f:
        f.write(ex["dsl"])
    examples_json.append({
        "page": page_name,
        "example": ex_name,
        "example_dsl": f"{ex_name}.v1.snapshot",
        "page_dsl": f"{page_name}.v1.snapshot",
        "title": ex["title"],
    })
print("Generated", len(EXAMPLES), "pairs")
