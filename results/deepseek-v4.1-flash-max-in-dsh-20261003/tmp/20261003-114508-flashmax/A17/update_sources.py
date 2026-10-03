"""Append the entity-confirmation and element-budget sections to A17 sources.md."""
import io
p = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\outputs\20261003-114508-flashmax\A17\sources.md"
s = io.open(p, encoding="utf-8").read()
old = "| 解析器**不做 HTML 实体解码**，`&amp;` 会保留为字面量 | <https://snapshot.muedsa.com/reference/parser-errors/>（同上） |"
new = ("| 解析器**不做 HTML 实体解码**，`&amp;` 会保留为字面量 | "
       "<https://snapshot.muedsa.com/reference/parser-errors/>（同上）；**本项目实测**："
       "`tmp/.../A17/entity-probe.png`（请求 `A17-REQ-0085`）里 `A &amp; B` 画出的是 5 个字面字符 "
       "`&amp;`，`A &lt; B` 画出的是 `&lt;`；因此手册与示例一律不用实体写法 |")
assert old in s
s = s.replace(old, new)

extra = """

## 6. 修订依据（子代理实体探针确认后）

2026-10-03 收到并行子代理的实测结论并与本项目自己的探针交叉验证，A17 做了如下修订，全部有真实请求留痕：

| 结论 | 证据 | 对 A17 的影响 |
|---|---|---|
| 解析器不解码实体：`&amp;` 画出 5 个字面字符 | `entity-probe.png`（`A17-REQ-0085`）；与 `/reference/parser-errors/` 的「`&` 不会进行 HTML 实体解码」一致 | 手册正文与 4 个示例已**完全不含** `&lt;`/`&gt;`/`&amp;` 序列；印刷代码改为逐 token CDATA 包装 |
| 代码里含 `<` 必须放在 CDATA 里才能印刷 | 修订前 `handbook-03` 报 `400 PARSE_ERROR Unexpected character '<' in input state [TAG_NAME]`（`A17-REQ-0087`）；改用 `cdata_if_needed()` 后 `A17-REQ-0098..0105` 全部 200 | `hbkit.code()` 现在对每个 token 自动 CDATA 包装 |
| 单文档元素上限 4096（按标签计数） | 服务限制；本项目最大页面 `handbook-01` 为 613 个 `<Tag`，四页分别为 613 / 367 / 534 / 346 | 全部远低于上限，无需拆分 |
| `CENTER` 对齐是盒子两轴中心（不是底部居中） | 子代理实测（60px 盒内文字墨迹 162..176） | A17 未依赖该常量：所有定位都算绝对坐标，`CENTER` 只用在 `Page.code` 的等高行盒里，不影响输出 |

修订后再次渲染全部 8 张最终图（`A17-REQ-0098`–`A17-REQ-0105`，均 200），并逐张复看确认版式未变。
"""
s = s.rstrip("\n") + "\n" + extra
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("sources.md updated")