"""Append the revision addendum to A17 snapshot-usage.md."""
import io
p = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\outputs\20261003-114508-flashmax\A17\snapshot-usage.md"
s = io.open(p, encoding="utf-8").read()
add = """

---

## 8. 修订记录（2026-10-03，子代理实体探针确认后）

并行子代理用真实请求确认了两条服务事实，本项目用自己的探针交叉验证后做了修订：

1. **解析器不解码 XML 实体**。`entity-probe.png`（`A17-REQ-0085`）显示 `A &amp; B` 画出的是 5 个字面字符 `&amp;`，
   `A &lt; B` 画出 `&lt;`，而 `A & B`、`<Raw><![CDATA[A < B > C]]></Raw>` 正常。
   这与 `/reference/parser-errors/`「`&` 不会进行 HTML 实体解码」一致。
   - 影响：旧版手册第 3 页正文与 example-03 曾出现 `&lt;`/`&gt;` 写法，会在图上被逐字画出。
   - 修订：**全部正文与 4 个示例已不含任何实体序列**（`examples.json` 里 `contains_entity_sequence` 全为 `false`）；
     教学点改为「实体写法按原文逐字画出，尖括号要写进 CDATA 才生效」，并在第 3 页给出实测错误串。
2. **代码印刷必须逐 token CDATA 包装**。`escape=False` 只做到“不转义”，但文本节点里的裸 `<` 会被当成标签：
   修订前 `handbook-03` 报 `400 PARSE_ERROR Unexpected character '<' in input state [TAG_NAME]`（`A17-REQ-0087`）。
   修订后 `hbkit.cdata_if_needed()` 对每个 token 自动包裹 CDATA，8 张最终图在 `A17-REQ-0098`–`0105` 全部 200。
3. **元素预算**。单文档上限 4096 个元素（按标签计），四页实测 `<Tag` 计数为 613 / 367 / 534 / 346，余量充足。
4. `CENTER` 对齐语义修正为「盒子两轴中心」。本题不依赖该常量：所有元素用绝对坐标定位，
   `CENTER` 只出现在代码块的等高行盒里（单行文本，竖直居中不影响结果）。

**修订后的真实消耗**：渲染请求累计 **105 次**（成功 96 / 失败 9，无 429）；DSL 版本 33 组（`v1`–`v24`、探针、`v2`–`v5` 修订版、`v9` 最终版）；
看图 **38 次**（含本次修订的 handbook-03、example-03 复看）。失败明细增加了 1 条：

- `A17-REQ-0087`：印刷代码未包 CDATA 导致的 `TAG_NAME` 解析错误（已修复，见上）。

**关于 `requests.jsonl`**：执行过程中曾为“清空日志便于阅读”误删了前 85 条记录，
后用每次请求都保留的 `.rawmeta` / `.rawheaders` / `.rawbody` 逐条重建（文件内 `log_rebuilt_from` 字段标明来源），
序号沿用共享脚本持久化的 `reqseq-A17-REQ.txt`（未重置），因此顺序与计数可信；
其中 9 条因同一 DSL 用不同 `-OutPath` 重复渲染而侧车文件被覆盖，`http_status` 依据当次结果与保留下来的输出 PNG 重建，并在字段中注明。
"""
io.open(p, "w", encoding="utf-8", newline="\n").write(s.rstrip("\n") + "\n" + add)
print("snapshot-usage.md addendum appended")