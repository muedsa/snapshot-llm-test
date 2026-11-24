# A15 Snapshot usage

Run: `20261124T113838+0800-aac601`. Status: completed after actual visual review.

## Documentation applied
- Cached `ai-guide.md`: UTF-8 Parser text request, PNG response checks, Retry-After handling through suitekit.
- Cached `parser-tags.md`, `parser-text.md`, `layout.md`, `painting.md`, `data-templates.md`: Container/Stack/Positioned geometry; Text has no width/top; font metrics differ from visible glyphs; CSS #RRGGBBAA; padding/border/shadow scope; CDATA-safe business text.
- Cached `fonts.txt`: selected `Noto Sans CJK SC`.

## Requests and visual iteration
- Request/response evidence: `tmp/20261124T113838+0800-aac601/A15/requests.jsonl`
- Iteration evidence: `tmp/20261124T113838+0800-aac601/A15/iterations.jsonl`
- Actual final review: version `v004`, SHA-256 `cf91531187ba3a06253b8aff57f2056a2f3f4b85ca6e6106853c6f67cbc12693`.
- Observation: 已实际查看 1440×900 原图、720×450 缩略图、左右并排缩略图、七组同背景色卡，以及侧栏、标题/KPI、图表、活动、表格五处 2× 局部。侧栏右缘、选中导航、三张 KPI、图表卡、活动卡、项目卡、标题字形、零线、末柱顶部和末行标签均与参考对齐；六个柱体比例和五条网格准确，三行项目顺序与蓝/黄/绿状态编码完整。未发现文字缺失、遮挡、裁剪或图表越界。残余差异为字体字形/字距、边缘抗锯齿及状态标签可见右缘最多 1px。
- Changes: v001 修正图表坐标基准与品牌标志环；v002 校准图表为 1.2px/千单位并修正标题字形位置；v003 修正零线、网格、标签框与卡内布局；v004 将全部 Text 内容改用 Raw/CDATA，精确保留双空格、货币符号、Unicode 减号、间隔号与箭头，并完成原尺寸/缩略/局部回归。

## Verification
- Twelve required anchors across four quadrants; maximum component error 1 px.
- Six chart bars and five grid lines measured against the reference; scale 1.2 px per ¥ thousand.
- Three table rows and status badges checked for order, text, color and geometry.
- Seven color roles judged visually on same-background swatches and sampled only as supporting evidence.
- Reference and final original, thumbnail and five local regions actually viewed; all literal source strings and raw service provenance validated.

## Design and preservation
Fixed 1440×900 root; all geometry uses Stack/Positioned. KPI, chart, activity and table use the same measured source data. Raw attempts, request/response bytes, scripts and review evidence remain in the task temp directory. Final PNG is copied byte-for-byte from the service response; final DSL is the exact submitted source. Paths in structured audits are relative to their declared base. Root .gitignore is managed by the suite; runtime caches are not evidence.

No unresolved issues after final validation.
