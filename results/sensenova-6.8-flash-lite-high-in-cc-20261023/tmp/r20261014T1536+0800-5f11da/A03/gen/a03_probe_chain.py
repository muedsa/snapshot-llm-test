"""A03 步骤 1：语法级错误逐项修复链。

每一版只修前一个版本暴露的那一个报错，重新提交，看服务报下一个错。
这样每个问题都拿到服务的真实报错作为证据（区分「真实报错」与「静默忽略」）。

启动基准：总任务根（cwd）。SNAPSHOT_RUN_ID 需已设置。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a03_io as IO  # noqa: E402

ORIGINAL = """<Snapshot width="1280" height="800" background="#0B1220" type="png">
  <Container padding="24 32" borderRadius="24">
    <Column>
      <Text font-size="44" color="#FFFFFF">System Pulse</Text>
      <Row>
        <Expanded flex="1"><Container width="360" height="200" color="#334155"><Text fontSize="28">USAGE 72%</Text></Container></Expanded>
        <Positioned right="20"><Text color="white">LIVE</Text></Positioned>
      </Row>
      <Spacer flex="1"/>
      <Transform rotate="-8"><Container width="160" height="56" color="#33FFFFFF"><Text color="white">REVIEW</Text></Container></Transform>
      <ImageFiltered sigmaX="10" sigmaY="10"><Container width="500" height="150" color="#FFFFFF44"><Text color="white" fontSize="28">Background-only blur</Text></Container></ImageFiltered>
    </Column>
  </Container>
</Snapshot>"""

# 每版只改一处，改动点写进 label 与记录


def variants() -> list[tuple[str, str, str]]:
    """返回 [(版本, 改动说明, DSL)]，链式累加。"""
    out: list[tuple[str, str, str]] = []
    v = ORIGINAL

    v = v.replace('padding="24 32"', 'padding="(24,32)"')
    out.append(("p1", "仅修 padding 格式：\"24 32\" → \"(24,32)\"", v))

    v = v.replace('<Snapshot width="1280" height="800" background="#0B1220" type="png">',
                  '<Snapshot background="#0B1220" type="png">')
    out.append(("p2", "仅移除 <Snapshot> 上不存在的 width/height（文档：Snapshot 只有 "
                      "background/debug/type，画布尺寸由布局决定）", v))

    v = v.replace('<Text font-size="44" color="#FFFFFF">',
                  '<Text fontSize="44" color="#FFFFFF">')
    out.append(("p3", "仅修 kebab 属性名：font-size → fontSize（属性大小写敏感）", v))

    v = v.replace(
        '        <Expanded flex="1"><Container width="360" height="200" color="#334155"><Text fontSize="28">USAGE 72%</Text></Container></Expanded>\n'
        '        <Positioned right="20"><Text color="white">LIVE</Text></Positioned>',
        '        <Expanded flex="1"><Container width="360" height="200" color="#334155"><Text fontSize="28">USAGE 72%</Text></Container></Expanded>\n'
        '        <Stack fit="EXPAND"><Positioned right="20"><Text color="white">LIVE</Text></Positioned></Stack>')
    out.append(("p4", "仅把 <Positioned> 包进 <Stack>（必须是 Stack 直接子节点）", v))

    v = v.replace('<Transform rotate="-8">', '<Transform>')
    out.append(("p5", "仅移除 <Transform> 上不存在的 rotate 属性（文档：Transform 用 "
                      "matrix 属性给 4×4 矩阵，无 rotate）", v))

    return out


def main() -> None:
    results = []
    for i, (ver, note, dsl) in enumerate(variants(), 1):
        rid = f"req-a03-probe-{ver}"
        rec = IO.submit(dsl, label=f"A03 语法修复链 {ver}：{note}",
                        rid=rid, out_png=None, kind="render", dsl_version=ver)
        rec_out = {"version": ver, "change": note, "request_id": rid,
                   "http_status": rec["http_status"],
                   "content_type": rec["content_type"],
                   "error": rec["_error_json"],
                   "response_body": rec["response_path"]}
        results.append(rec_out)
        print(json.dumps({k: rec_out[k] for k in
                          ("version", "http_status", "content_type")},
                         ensure_ascii=True))
        if rec_out["http_status"] == 200:
            print("  FIRST SUCCESS at", ver)
            break

    IO.dirs()[1].joinpath("probe-chain.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("probes:", len(results))


if __name__ == "__main__":
    main()
