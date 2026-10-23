"""A17 干跑检查：不联网，验证 DSL 生成、印刷行数、行宽与版面余量。

检查项：
  * 8 个 DSL 都以 <Snapshot 开头、</Snapshot> 结尾；
  * 每页实际印出的代码行 8–18 行；
  * 所有印刷行长度不超过 86 字符（fontSize 20 的 DejaVu Sans Mono
    在 1104-44=1060 的内容宽内约 88 字符上限，留 2 字符余量）；
  * 版面游标：要点区不越过 1600-48；
  * 印刷片段逐字等于独立示例 DSL 对应行号区间（防止印刷与运行两套代码）；
  * 省略提示行里标注的行号区间，恰好覆盖印刷区间之外的全部行、不重不漏。
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))

from a17_core import (CONTENT_W, CORES, MARGIN, PAGES, SEGMENTS,
                      core_file_range, printed_ranges, seg, illustration_frame,
                      independent_dsl)
from a17_page import CODE_LINE_H, CODE_PAD_V, ILUS_W, layout, page_dsl
from a17_build import CONTENT, FILES

RANGE_RE = re.compile(r"第\s*(\d+)(?:\s*[–-]\s*(\d+))?\s*行")
ATTR_PAIR_RE = re.compile(r'(\w+)\s*=\s*"([^"]*)"')
ATTR_PAIR_RE = re.compile(r'(\w+)\s*=\s*"([^"]*)"')
FLEX_TAGS = {"Row", "Column"}
FLEX_CHILD_TAGS = {"Expanded", "Flexible"}


def _tag_close(dsl: str, i: int) -> int:
    """从 '<' 起返回本标签结束 '>' 的下标；跳过双引号内的 '>' 与 '<'。"""
    j, n = i, len(dsl)
    while j < n:
        ch = dsl[j]
        if ch == '"':
            k = dsl.find('"', j + 1)
            if k < 0:
                return n - 1
            j = k + 1
            continue
        if ch == ">":
            return j
        j += 1
    return n - 1


def tokenize(dsl):
    """极简词法扫描，尊重 CDATA 与属性引号。

    返回 [(kind, value)]，kind ∈ {"cdata", "text", "tag_open", "tag_end"}。
    两处必须小心：印刷代码块的 CDATA 里含有字面 <Raw>、</Raw>、<Positioned>
    等文本，跨 CDATA 找标签会误配对；属性值可能含 '<' 或 '>'（如
    text="a < b && b > a"），必须跳过引号内的定界符。
    """
    out, i, n = [], 0, len(dsl)
    while i < n:
        if dsl.startswith("<![CDATA[", i):
            j = dsl.find("]]>", i + 9)
            if j < 0:
                out.append(("cdata", dsl[i:]))
                break
            out.append(("cdata", dsl[i + 9:j]))
            i = j + 3
        elif dsl[i] == "<":
            j = _tag_close(dsl, i)
            if dsl.startswith("</", i):
                out.append(("tag_end", dsl[i + 2:j].strip()))
            else:
                out.append(("tag_open", dsl[i + 1:j].strip()))
            i = j + 1
        else:
            j = dsl.find("<", i)
            j = n if j < 0 else j
            if dsl[i:j].strip():
                out.append(("text", dsl[i:j]))
            i = j
    return out


def build_tree(tokens):
    """把词法流建成带 parent 指针的树，返回 (root, 未闭合/错配标签列表)。"""
    root = {"tag": None, "attrs": {}, "children": [], "texts": [],
            "self_closing": False, "parent": None}
    stack = [root]
    problems = []
    for kind, val in tokens:
        cur = stack[-1]
        if kind in ("cdata", "text"):
            # 区分两种文本：CDATA 内的 '<' 是数据，裸文本里的 '<' 会被当标签
            cur["texts"].append((kind, val))
            continue
        if kind == "tag_open":
            if not val:
                continue
            self_closing = val.endswith("/")
            body = val[:-1] if self_closing else val
            node = {"tag": body.split(None, 1)[0], "attrs": {},
                    "children": [], "texts": [],
                    "self_closing": self_closing, "parent": cur}
            for m in ATTR_PAIR_RE.finditer(body):
                node["attrs"][m.group(1)] = m.group(2)
            cur["children"].append(node)
            if not self_closing:
                stack.append(node)
        else:
            if len(stack) < 2:
                problems.append("多余的闭合标签 </%s>" % val[:60])
                continue
            top = stack.pop()
            if top["tag"] != val:
                problems.append("标签错配: <%s> 却以 </%s> 闭合"
                                % (top["tag"], val[:60]))
    for still in stack[1:]:
        problems.append("未闭合标签 <%s>" % still["tag"])
    return root, problems


def walk(node, out):
    out.append(node)
    for c in node["children"]:
        walk(c, out)


def scan_dsl(tag, dsl):
    """静态检查，返回问题列表。全部规则都来自 A17 真实 400/RENDER_ERROR 响应。

    * <Container> 最多一个子元素（否则 400 PARSE_ERROR「Tag Container only can
      have one child」，req-a17-handbook-01..04 首版实测）；
    * 属性值不得含 '<' 或 '&'（本服务不做实体解码，'<' 在裸元素内容里触发
      TAG_OPEN，req-a17-handbook-03-8730d7 实测）；
    * <Raw> 不能有元素子节点，字面 '<' 必须放在 CDATA 里（同上）；
    * <Positioned> 的父节点必须是 <Stack>（否则 RENDER_ERROR「Layout size is
      infinite」，req-a17-handbook-02-0215ae / handbook-04-20aa16 实测）；
    * <Expanded>/<Flexible> 的父节点必须是 Row 或 Column。
    """
    root, problems = build_tree(tokenize(dsl))
    nodes = []
    walk(root, nodes)
    for node in nodes:
        name = node["tag"]
        if name == "Container" and len(node["children"]) > 1:
            problems.append("%s Container 有 %d 个子元素（只允许 1 个）"
                            % (tag, len(node["children"])))
        for k, v in node["attrs"].items():
            if "<" in v or "&" in v:
                problems.append("%s <%s %s> 属性值含 < 或 & : %r"
                                % (tag, name, k, v[:50]))
        if name == "Raw":
            if node["children"]:
                problems.append("%s <Raw> 含有元素子节点" % tag)
            plain = "".join(v for kind, v in node["texts"]
                            if kind == "text" and "<" in v)
            if plain:
                problems.append("%s <Raw> 裸文本含字面 < 且未走 CDATA: %r"
                                % (tag, plain[:50]))
        if name == "Positioned":
            parent = node["parent"]["tag"]
            if parent != "Stack":
                problems.append("%s <Positioned> 的父节点是 <%s>，必须是 <Stack>"
                                % (tag, parent))
        if name in FLEX_CHILD_TAGS:
            parent = node["parent"]["tag"]
            if parent not in FLEX_TAGS:
                problems.append("%s <%s> 的父节点是 <%s>，必须是 Row 或 Column"
                                % (tag, name, parent))
    return problems


def main() -> int:
    # python -I 会忽略 PYTHONIOENCODING，控制台是 GBK，需显式改成 UTF-8
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ok = True
    report = {}
    for page in range(1, PAGES + 1):
        n_lines = len(CORES[page].split("\n"))
        ranges, n_printed = printed_ranges(page)
        n_ell = sum(1 for k, _ in SEGMENTS[page] if k == "ellipsis")
        rendered = n_printed + n_ell

        # 印刷行逐字取出并检查长度
        lines_out = []
        for kind, val in SEGMENTS[page]:
            if kind == "range":
                lines_out.extend(seg(page, [val]).split("\n"))
            else:
                lines_out.append(val)
        too_long = [(i, len(l), l) for i, l in enumerate(lines_out, 1)
                    if len(l) > 86]

        # 印刷片段必须逐字等于核心子树对应行（防止印刷与运行不一致）
        mismatch = []
        for kind, val in SEGMENTS[page]:
            if kind == "range":
                want = seg(page, [val])
                got = "\n".join(CORES[page].split("\n")[val[0] - 1:val[1]])
                if want != got:
                    mismatch.append(val)

        if not (8 <= n_printed <= 18):
            ok = False
            print("  ✗ 印刷行数越界 page%d: %d" % (page, n_printed))
        if too_long:
            ok = False
            print("  ✗ 行过宽 page%d: %s" % (page, too_long))
        if mismatch:
            ok = False
            print("  ✗ 印刷与核心子树不一致 page%d: %s" % (page, mismatch))

        # 印刷片段必须逐字等于独立示例 DSL 的对应行
        dsl_ex_text = independent_dsl(page)
        dsl_ex_lines = dsl_ex_text.split("\n")
        total = len(dsl_ex_lines) - (1 if dsl_ex_lines[-1] == "" else 0)
        for r in ranges:
            fl, fh = core_file_range(*r)
            want = seg(page, [r])
            got = "\n".join(dsl_ex_lines[fl - 1:fh])
            if want != got:
                ok = False
                print("  ✗ 印刷与独立 DSL 不一致 page%d %s: %r" % (page, r, got))

        # 省略提示标注的行号区间必须恰好覆盖印刷区间之外的全部行
        printed_set = set()
        for lo, hi in ranges:
            flo, fhi = core_file_range(lo, hi)
            printed_set.update(range(flo, fhi + 1))
        noted = set()
        for kind, val in SEGMENTS[page]:
            if kind != "ellipsis":
                continue
            for m in RANGE_RE.finditer(val):
                a = int(m.group(1))
                b = int(m.group(2)) if m.group(2) else a
                if not (1 <= a <= b <= total):
                    ok = False
                    print("  ✗ 省略提示行号越界 page%d: %s" % (page, val))
                    continue
                noted.update(range(a, b + 1))
                if a in printed_set:
                    ok = False
                    print("  ✗ 省略提示与印刷区间重叠 page%d: %s" % (page, val))
        omitted = set(range(1, total + 1)) - printed_set
        if noted != omitted:
            ok = False
            print("  ✗ 省略覆盖不全 page%d 缺少%s 多余%s"
                  % (page, sorted(omitted - noted), sorted(noted - omitted)))

        hb, ex, *_ = FILES[page]
        c = CONTENT[page]
        dsl_page = page_dsl(page, c["chapter"], c["title"], c["intro"],
                            "印刷代码片段", "教学插图（本页 DSL 构件直接绘制）",
                            c["keys"])
        dsl_ex = independent_dsl(page)
        for tag, d in ((hb, dsl_page), (ex, dsl_ex)):
            if not (d.startswith("<Snapshot") and d.rstrip().endswith("</Snapshot>")):
                ok = False
                print("  ✗ DSL 首尾异常 %s" % tag)
            for prob in scan_dsl(tag, d):
                ok = False
                print("  ✗ %s" % prob)
        for prob in scan_dsl("core-%d" % page, CORES[page]):
            ok = False
            print("  ✗ %s" % prob)
        # 教学页里必须逐字包含核心子树
        if CORES[page] not in dsl_page:
            ok = False
            print("  ✗ 教学页未逐字包含核心子树 page%d" % page)
        if CORES[page] not in dsl_ex:
            ok = False
            print("  ✗ 独立示例未逐字包含核心子树 page%d" % page)
        if illustration_frame(page, MARGIN + (CONTENT_W - ILUS_W) // 2,
                              layout(rendered, c["keys"], 2)["illus"]) not in dsl_page:
            ok = False
            print("  ✗ 教学页外框未逐字复用 page%d" % page)

        pos = layout(rendered, c["keys"], 2)
        keys_bottom = pos["keys_bottom"]
        if keys_bottom > 1552:
            ok = False
            print("  ✗ 要点区越界 page%d: %d" % (page, keys_bottom))

        report[page] = {
            "core_lines": n_lines,
            "printed_line_count": n_printed,
            "ellipsis_count": n_ell,
            "rendered_lines": rendered,
            "printed_segments": [list(r) for r in ranges],
            "printed_segments_file_lines": [list(core_file_range(*r))
                                            for r in ranges],
            "keys_bottom": keys_bottom,
            "keys_margin": 1552 - keys_bottom,
            "code_h": rendered * CODE_LINE_H + 2 * CODE_PAD_V,
        }
        print("page %d: core=%2d 印刷=%2d 省略=%d 渲染=%2d "
              "keys_bottom=%4d 余量=%3d"
              % (page, n_lines, n_printed, n_ell, rendered,
                 keys_bottom, 1552 - keys_bottom))

    print(json.dumps({"ok": ok, "pages": report}, ensure_ascii=False, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
