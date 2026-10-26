import xml.etree.ElementTree as ET
from pathlib import Path

dsl = Path("tmp/run-20261013-174209/A09/transform-atlas.snapshot").read_text(encoding="utf-8")
try:
    root = ET.fromstring(dsl)
    print("XML well-formed. root =", root.tag)
    # 统计 body Stack
    stacks = [e for e in root.iter() if e.tag == "Stack"]
    print("Stack count:", len(stacks))
    with_tf = [s for s in stacks if "transform" in s.attrib]
    print("Stacks with transform:", len(with_tf))
    for s in with_tf[:4]:
        print("   ", s.attrib.get("transform"))
except ET.ParseError as e:
    print("PARSE ERROR:", e)
    # 找错误位置
    line, col = e.position
    lines = dsl.splitlines()
    if line - 1 < len(lines):
        print("line", line, ":", lines[line - 1][:200])
