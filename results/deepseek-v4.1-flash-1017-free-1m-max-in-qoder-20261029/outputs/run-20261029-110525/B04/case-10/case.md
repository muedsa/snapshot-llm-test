# 10 · 错误、重试与可复现交付

- 受众：发布与 QA 工程师
- 使用场景：交付检查清单页
- 用户目标：按 code 分类处理错误，并把失败证据与最终图一起归档
- 内容依据：ai-guide.md 的错误处理；本套件失败响应的实际留档
- 视觉意图：深色终端风格错误 JSON，配三条处置说明
- 主图：`final.png`（1200×1500，服务真实响应）
- DSL：`final.snapshot`
- DSL 能力：等宽字体 Noto Sans Mono CJK SC、深色代码块、Column 行距
- 查看状态：已按最终尺寸实际查看；属第 4 轮修订后的版本。

## 图示读法

深色块是失败响应示例；三行说明依次是错误分类、证据保留与重试边界。

## 依据条目

- `C01`（S1 · 最小示例；错误处理）：请求体是 UTF-8 纯文本 DSL；成功响应为图片二进制，失败响应为带 code、message、requestId 的 JSON。
- `C12`（S1 · 错误处理）：400 PARSE_ERROR 应修正 DSL；429 与部分 503 可参考 Retry-After 延迟重试，不要原样重试格式错误。

## 文件

- [final.png](final.png)
- [final.snapshot](final.snapshot)
- [sources.json](../sources.json)
- [editorial-note.md](../editorial-note.md)
