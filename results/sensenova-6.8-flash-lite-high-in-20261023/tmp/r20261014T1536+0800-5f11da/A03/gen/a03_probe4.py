"""A03 步骤 5：补做「只修语法」基线，并顺带提交 v1 预览。

p7  修正 p6 的一个自身缺陷后重做：p6 插入外层 Container 时少写了 </Container>，
    嵌套被打乱，无法作为干净的「只修语法」基线。
    p7 保持原稿嵌套不变，把画布尺寸改到**根 Container** 上（<Snapshot> 没有
    width/height），只修 5 处语法项，不动任何结构。
p8  p7 加 debug="true"，用服务端的布局调试覆盖层看实际盒子位置，
    判定「哪些元素不可见、为什么」。
v1  最终监控卡首版预览。

启动基准：总任务根（cwd）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a03_io as IO  # noqa: E402
import a03_build as B  # noqa: E402

SRC = IO.ROOT / "tasks" / "A03-semantic-debugging" / "inputs" / "broken.snapshot"


def p7(debug: bool = False) -> str:
    """保持原稿嵌套与全部区块，只修 5 处语法项。"""
    v = SRC.read_text(encoding="utf-8")
    # 1) <Snapshot> 没有 width/height（文档：只有 background/debug/type），
    #    画布尺寸改到根 Container 上
    v = v.replace('<Snapshot width="1280" height="800" background="#0B1220" type="png">',
                  '<Snapshot background="#0B1220" type="png"'
                  + (' debug="true"' if debug else '') + '>')
    v = v.replace('<Container padding="24 32" borderRadius="24">',
                  '<Container width="1280" height="800" color="#0B1220" '
                  'padding="(32,32)" borderRadius="24">')
    # 2) kebab 属性名 → 驼峰（属性名大小写敏感）
    v = v.replace('<Text font-size="44" color="#FFFFFF">',
                  '<Text fontSize="44" color="#FFFFFF">')
    # 3) <Positioned> 必须是 Stack 的直接子节点
    v = v.replace('        <Positioned right="20"><Text color="white">LIVE</Text></Positioned>',
                  '        <Stack fit="EXPAND" clipBehavior="NONE">\n'
                  '          <Positioned right="20" top="0"><Text color="white">LIVE</Text>'
                  '</Positioned>\n        </Stack>')
    # 4) <Transform> 没有 rotate；用列主序 4×4 矩阵（外层必须有括号）
    v = v.replace('<Transform rotate="-8">',
                  f'<Transform matrix="{B.ROT}" alignment="CENTER">')
    return v


def main() -> None:
    tmp = IO.dirs()[1]
    res = {}

    for name, dsl in (("p7", p7(False)), ("p8", p7(True))):
        rec = IO.submit(dsl, label=f"A03 只修语法基线 {name}",
                        rid=f"req-a03-probe4-{name}", out_png=None,
                        kind="render", dsl_version=f"probe4-{name}")
        res[name] = {"request_id": rec["request_id"], "http_status": rec["http_status"],
                     "content_type": rec["content_type"],
                     "response_bytes": rec["response_bytes"], "ok": rec["_ok"],
                     "error": rec["_error_json"]}
        (tmp / "preview" / f"probe4-{name}.png").write_bytes(
            (tmp / "responses" / f"req-a03-probe4-{name}.body").read_bytes())
        print(name, rec["http_status"], rec["content_type"], rec["response_bytes"])

    dsl = B.build()
    rec = IO.submit(dsl, label="A03 System Pulse v1 预览",
                    rid="req-a03-v1-preview", out_png=None,
                    kind="render", dsl_version="v1")
    res["v1"] = {"request_id": rec["request_id"], "http_status": rec["http_status"],
                 "content_type": rec["content_type"],
                 "response_bytes": rec["response_bytes"], "ok": rec["_ok"],
                 "error": rec["_error_json"]}
    if rec["_ok"]:
        (tmp / "preview" / "v1.png").write_bytes(
            (tmp / "responses" / "req-a03-v1-preview.body").read_bytes())
    print("v1", rec["http_status"], rec["content_type"], rec["response_bytes"],
          "" if rec["_ok"] else rec["_error_json"])

    (tmp / "probe4.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
