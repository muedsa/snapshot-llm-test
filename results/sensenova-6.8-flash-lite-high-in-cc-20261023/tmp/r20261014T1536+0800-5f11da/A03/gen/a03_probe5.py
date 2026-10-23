"""A03 步骤 6：定位「只修语法后只剩标题」的静默丢子节点原因。

p7/p8 显示：<Column> 里 <Row> 及其之后的所有子节点都没有被布局/绘制，
而服务返回 200 + 正常 PNG，debug 覆盖层里也只有根容器与标题两个盒子。
TASK.md 要求继续查「有界布局」，所以用一张图四个象限做二分定位：

  T1  Column > [Text, Row > Expanded > Container(360×200) > Text]
  T2  Column > [Text, Row > Stack(fit=EXPAND) > Positioned > Text]
  T3  Column > [Text, Row > Container(120×80)]
  T4  Column > [Text, Spacer, Transform(matrix) > Container, ImageFiltered > Container]

每格是固定尺寸容器（576×336），模拟原稿 Column 的父级约束。

启动基准：总任务根（cwd）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a03_io as IO  # noqa: E402
import a03_build as B  # noqa: E402

CELL_W, CELL_H = 576, 336
XL, XR, YT, YB = 32, 672, 32, 400
BOX = "#334155"          # 原稿指标卡的颜色
TAG = '<Text fontFamily="Inter" fontSize="20" color="#94A3B8">'


def cell(x: int, y: int, name: str, body: str) -> str:
    return f'''      <Positioned left="{x}" top="{y}">
        <Container width="{CELL_W}" height="{CELL_H}" borderRadius="16"
                   color="#0F172A" border="1 SOLID #1E293B">
          <Column>
            {TAG}>{name}</Text>
            <Container width="1" height="10" color="transparent"/>
{body}
          </Column>
        </Container>
      </Positioned>'''


def build() -> str:
    t1 = (f'          <Row>\n'
          f'            <Expanded flex="1"><Container width="360" height="200" '
          f'color="{BOX}"><Text fontSize="28">USAGE 72%</Text></Container>'
          f'</Expanded>\n          </Row>')
    t2 = (f'          <Row>\n'
          f'            <Stack fit="EXPAND" clipBehavior="NONE">'
          f'<Positioned right="20" top="0"><Text color="white">LIVE</Text>'
          f'</Positioned></Stack>\n          </Row>')
    t3 = (f'          <Row>\n'
          f'            <Container width="120" height="80" color="{BOX}"/>\n'
          f'          </Row>')
    t4 = (f'          <Spacer flex="1"/>\n'
          f'          <Transform matrix="{B.ROT}" alignment="CENTER">'
          f'<Container width="160" height="56" color="#33FFFFFF">'
          f'<Text color="white">REVIEW</Text></Container></Transform>\n'
          f'          <ImageFiltered sigmaX="10" sigmaY="10">'
          f'<Container width="500" height="150" color="#FFFFFF44">'
          f'<Text color="white" fontSize="28">Background-only blur</Text>'
          f'</Container></ImageFiltered>')

    return f'''<Snapshot background="#0B1220" type="png">
  <Container width="1280" height="800" color="#0B1220" padding="(32,32)">
    <Stack fit="EXPAND" clipBehavior="NONE">

{cell(XL, YT, "T1 Row+Expanded", t1)}
{cell(XR, YT, "T2 Row+Stack", t2)}
{cell(XL, YB, "T3 Row+Container", t3)}
{cell(XR, YB, "T4 Spacer+Transform+ImageFiltered", t4)}

    </Stack>
  </Container>
</Snapshot>'''


def main() -> None:
    out, tmp = IO.dirs()
    dsl = build()
    rec = IO.submit(dsl, label="A03 有界布局二分探针 t1..t4",
                    rid="req-a03-probe5-layout", out_png=None,
                    kind="render", dsl_version="probe5-layout")
    if rec["_ok"]:
        (tmp / "preview" / "probe5-layout.png").write_bytes(
            (tmp / "responses" / "req-a03-probe5-layout.body").read_bytes())
    (tmp / "probe5.json").write_text(json.dumps(
        {"request_id": rec["request_id"], "http_status": rec["http_status"],
         "content_type": rec["content_type"], "response_bytes": rec["response_bytes"],
         "ok": rec["_ok"], "error": rec["_error_json"],
         "dsl": rec["request_path"]}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(rec["http_status"], rec["content_type"], rec["response_bytes"],
          "" if rec["_ok"] else rec["_error_json"])


if __name__ == "__main__":
    main()
