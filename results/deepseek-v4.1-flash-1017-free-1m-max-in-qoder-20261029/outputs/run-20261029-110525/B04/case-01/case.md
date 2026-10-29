# 01 · 请求：从文本到图片

- 受众：初次接入 Snapshot 的服务端开发者
- 使用场景：接入评审会的单页说明，或新成员入职资料
- 用户目标：十分钟内弄清请求体、成功响应与失败响应的类型
- 内容依据：ai-guide.md 的最小示例与错误处理；本套件真实 /snapshot 请求记录
- 视觉意图：从左到右的请求流程图：深色输入、品牌绿服务、赭色输出；留白给讲稿
- 主图：`final.png`（1200×1500，服务真实响应）
- DSL：`final.snapshot`
- DSL 能力：Stack/Positioned、Transform 旋转连线、Container 圆角与边框、Column 文本块
- 查看状态：已按最终尺寸实际查看；属第 4 轮修订后的版本。

## 图示读法

先读左栏两段，再沿右图从左到右：文本 DSL → POST /snapshot → PNG。两条灰色小字分别说明失败结构与重试边界。

## 依据条目

- `C01`（S1 · 最小示例；错误处理）：请求体是 UTF-8 纯文本 DSL；成功响应为图片二进制，失败响应为带 code、message、requestId 的 JSON。
- `C12`（S1 · 错误处理）：400 PARSE_ERROR 应修正 DSL；429 与部分 503 可参考 Retry-After 延迟重试，不要原样重试格式错误。

## 文件

- [final.png](final.png)
- [final.snapshot](final.snapshot)
- [sources.json](../sources.json)
- [editorial-note.md](../editorial-note.md)
