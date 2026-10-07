# A23 临时草稿目录说明（drafts/）

本目录保存每次渲染使用的完整 DSL 草稿，按 `vNN-<图名>.snapshot` 递增编号，不覆盖旧版本。

## 一个必须如实说明的失误

**最初的 `build_a23.py` 里的 `draft()` 辅助函数有 bug**：写出的文件名是
`v01-<图名>`，**漏了 `.snapshot` 后缀**，而编号逻辑又用
`len(glob("*.snapshot")) + 1` 来算下一个编号。由于目录里永远没有 `.snapshot`
文件，编号恒为 1，于是**每次运行都把 `v01-*` 覆盖掉**。

- 影响范围：A23 迭代过程中 v1/v2 版 6 帧 DSL、以及带引号 bug 的旧版封面 DSL
  的**草稿副本**被覆盖。
- 未受影响、仍然完整留存的权威记录：
  - `../requests.jsonl`：48 条请求的真实记录（requestId、HTTP 状态、
    Content-Type、耗时、错误原文、响应文件路径），覆盖每一版；
  - `../responses/`：所有非图片响应体（4 次 400 的完整 JSON 错误原文）；
  - `../preview/`：10 张能力探针图 + 4 张语义探针图的 PNG 与 DSL；
  - `../iterations.jsonl`：迭代台账（观察到的现象、改了什么、复验结果）；
  - `../crops/`：4 张放大核对图。
- 已修复：`draft()` 现在写 `.snapshot` 后缀并用 `^v(\d+)-.*\.snapshot$` 正则
  取已有最大编号 +1。
- 已重建：`v00-cover-reconstructed-PARSE_ERROR-quote.snapshot`。这是**重建**而非
  原件保留——它与最终 `cover.snapshot` 只差 2 个字节（文案里两个英文双引号），
  而那行文案在 `requests.jsonl` 的 `A23-req-037` 错误原文中被逐字引用，
  因此重建是精确的，`recover_draft.py` 里也对该引用做了断言校验。
- **未重建**：v1 版 6 帧 DSL。旧版的散点算法（黄金角散布）与弯曲系数只被部分记录，
  凭记忆补一个 `.snapshot` 并冒充历史请求体是不诚实的，因此不做；
  该版本的权威记录是 `requests.jsonl` 中 `A23-req-020` … `A23-req-025`。
  旧版的具体缺陷（core tile 互相重叠、两环相撞、逐帧位移过小）已在
  `iterations.jsonl` 的 `A23-v10` / `A23-v11` 中完整记录。

## 当前内容

| 文件 | 说明 |
|---|---|
| `v00-cover-reconstructed-PARSE_ERROR-quote.snapshot` | 重建的、触发 400 的旧版封面 DSL |
| `v01-frame-01.snapshot` … `v06-frame-06.snapshot` | 最终 6 张关键帧的完整 DSL |
| `v07-cover.snapshot` | 最终封面 DSL |
| `v08-contact-sheet.snapshot` | 最终接触表 DSL |

最终交付目录 `outputs/20261004-182918/A23/` 里的 `*.snapshot` 与上表对应文件
字节一致，都是**服务真实响应对应的原始请求体**，未做任何后处理。
