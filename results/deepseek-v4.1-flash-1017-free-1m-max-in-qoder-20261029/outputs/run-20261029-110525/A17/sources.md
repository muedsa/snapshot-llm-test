# A17 文档来源与对应

| 结论 | 实际阅读页面 | 对应示例/页面 |
|---|---|---|
| POST /snapshot、text/plain、成功为图片二进制、错误为 JSON | https://open-snapshot.muedsa.com/ai-guide.md | example-01 / handbook-01 |
| Snapshot 根不含 width/height，画布由布局决定 | https://snapshot.muedsa.com/reference/parser-tags.md#snapshot | example-02 / handbook-02 |
| Row/Column 有界主轴、Expanded、Positioned 父级限制 | https://snapshot.muedsa.com/reference/parser-tags.md#row-与column | example-02 / handbook-02 |
| Parser 不解码实体；Raw 保留空白；Text trim | https://snapshot.muedsa.com/guides/parser.md#文本与-cdata | example-03 / handbook-03 |
| 8 位颜色为 #RRGGBBAA（透明度在末尾） | https://snapshot.muedsa.com/reference/parser-tags.md#颜色 | example-03 / handbook-03 |
| BackdropFilter 背景模糊、ImageFiltered 子树模糊、需裁剪 | https://snapshot.muedsa.com/reference/parser-tags.md#colorfilteredimagefiltered-与-backdropfilter | example-04 / handbook-04 |
| 先渲染再检查、失败响应保留、可复现 | https://open-snapshot.muedsa.com/ai-guide.md#错误处理 | handbook-04 |

字体查询：`GET /fonts` 返回 Inter、Noto Sans CJK SC、Noto Sans Mono CJK SC 等；手册正文/代码均从该列表选择。文档缓存位于 `tmp/run-20261029-110525/_suite/docs/`。
