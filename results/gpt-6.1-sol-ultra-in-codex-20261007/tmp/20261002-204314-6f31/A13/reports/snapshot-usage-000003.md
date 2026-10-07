# A13 · 品牌标志到完整活动应用

Final status: completed. Root actual image review and required-file audit both passed. Earlier production-stage notes are superseded by this closing result.

同一运行 20261002-204314-6f31。四张最终候选原服务PNG均由root实际打开，并完成512/32缩略视觉审查及独立几何/像素审查；归档完成后继续A14。

交付symbol-color512×512、symbol-black512×512透明图标，brand-banner1200×400横幅、launch-poster1080×1350海报及同名完整.snapshot。brand-system.json记录色彩/比例/构件/留白/四应用映射与真实证据；rationale.md共159字，说明两个真实方向、选择及小尺寸修改；brand-audit.json追加独立证据。

## 有证据的方向与迭代

先真实render两个512透明方向：A两错位空心圆角方框共2主要构件；B六切向条组成径向六角光圈共6构件，几何真正不同。各512原图及实际32缩略先看后选，direction-selection-v001.json记录选择时间，早于build-finals-v002.cjs及4成品构造。A直接表达层叠信息、中央共同开口，B更接近一般徽章；32的A笔画较细，因此同方案笔画32→40、圆角40→48。真正重render并查看512和32，轮廓更稳、中心112源像素约7px空窗仍开放。1完整视觉迭代，B探索另计alternative，不制造额外修改。

## 几何、文字、透明与小尺寸

同一symbol函数生成四应用，两图标几何完全相同：框256、偏移64、笔画40、圆角48，总边界320；应用按frame.8/offset.2/stroke.125/radius.15同比生成，留白至少1笔画。无Text充当图标，无Image或外部/现成logo。两图标原RGBA边界均[96,96,416,416]，外缘alpha0；非透明黑像素62420个全部RGB0。原alpha数组精确相等=false，154像素不同，差值最大1，含8处0→1抗锯齿边缘；154差点距实际DSL圆角边界≤0.617588px，无alpha255差异、alpha≥128轮廓一致。原失败判定保留；该精确字节条件比本题几何同一要求更强，题目允许AA alpha，独立audit量化差异并核对相同DSL几何，未改最终字节。

root实际views13–16覆盖四最终响应；17白底黑512、18/19实际32彩黑、20/21最近邻放大板进一步检查黑图与小尺寸。原黑PNG工具背景为黑，实际又打开白底QA才判轮廓；不能从黑背景猜alpha。QA白底/缩略/放大仅保存在tmp，最终PNG保留响应原字节。生产者和独立审查者也逐图真看，完整ids在views.jsonl。

横幅左标志右56px字标与32px完整口号；海报为独立竖向构图，OPEN BETA、64px字标、34px口号、中央大符号、底部日期与网站分区。原串“叠光 Layerlight”“把复杂信息，组织成清晰画面”“2026.11.07 · ONLINE”“OPEN BETA”“layerlight.example.org”完整可见。网站为输入演示地址，品牌为任务虚构；没有外部真实商标声称。

## 实际文档工具、过程与消耗

复用真实共享服务指南、parser-tags的Snapshot/Container/Border/Stack/Positioned/Text/Raw、实际fonts缓存与A11文字文档；新文档/fonts请求0，不重复计HTTP。Node生成全部纯DSL几何/Raw文字；真实POST UTF-8 text/plain，保留响应PNG、headers、requestId/Server-Timing、所有版本及独立PythonRGBA量化。view_image实际看512/32及QA，对最终图无后处理。

本题6render均成功，0HTTP失败/重试，6DSL版本，1完整视觉迭代，1方案探索，0语法修复，实际看图37次（关闭后以指标为准）。两预览不计最终PNG；四最终为A题交付页，不计B独立作品。每次实体字节/请求耗时/墙钟按真实日志测量；token/图像输入计费/费用未知为null，不按字数或文件字节推造。

独立审查初始预览view元数据版本/is_preview误写，真实图像与时间未变；追加view-metadata-corrections-v001.jsonl纠正，原日志保留，不追加假的物理查看。独立alpha脚本首次因else0缺空格发生本地SyntaxError，v002修复后测量成功，原失败保存，非HTTP失败、不新增渲染。精确alpha不同保留false及原audit，最终判断依据题目几何、AA许可与真实图像；原因未确认。输出 D:\workspaces\gpt-6.1-sol-ultra\outputs\20261002-204314-6f31\A13；全部草稿/预览/脚本/日志/失败测量在 D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\A13。全套最终审查仍待剩余题完成。


## Root final review

A13-view-000013: 彩色原512图两错位框笔画比预览更稳，中央共同负空间仍开放；偏移、外形清晰。

A13-view-000014: 原512透明纯黑PNG已打开，工具黑底使轮廓不可见；另实际打开白底QA512及32确认两叠框轮廓与中心开口，alpha/RGB另独立测量。

A13-view-000015: 实际1200×400横幅左图标右字标，叠光 Layerlight及整句口号清楚，字形无裁切，紫线保持横向结构。

A13-view-000016: 实际1080×1350海报为独立竖向发布构图：OPEN BETA、双语字标、完整口号，上下留白与居中大叠框；日期ONLINE及网站完整可读。
