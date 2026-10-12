# A12 · 四断点完整内容视觉系统

运行 20261002-204314-6f31。四个原始PNG候选已通过root真实逐图查看和独立字段/布局审查；实际失败及所有诊断保留。

交付mobile360×800、tablet768×1024、desktop1440×900、stage1920×1080及四份同名完整.snapshot，均服务实际响应、不后处理；design-tokens.json与content-map.json记录完整设计规则和25叶字段×4的100处坐标/原串/字号/保留证据，responsive-audit.json另存独立约束/看图证据。所有主title/subtitle/date/time/location/cta/website、六card.id/title/detail逐字保留，无缩写/省略；CTA为原文字，不伪造QR，example.org为输入演示网站。

## 同一系统与完整布局

纸色#F5F4EE、深墨#192F35、青绿#0A8686、酸橙#D8F079，白卡与细边线，源字段独立Raw/CDATA。Inter,Noto Sans CJK SC正文、DejaVu Sans Mono数字/ID/网站均从真实共享fonts缓存选用。相同两交错框由Container/Border纯DSL构造，可随断点重排/缩放；无Image、外部素材、整体截图拉伸或裁切适配。

手机：主标题40自然两行、正文16、卡标题18、16安全边距，单列六62px卡、间8；完整CTA与网站底部仍可读。平板：主标题64、正文最低20、卡标题26，32边距，两列三行，横/纵间16。桌面：主标题78、正文最低22、卡标题30，48边距，左信息/行动、右两列三行卡，横24纵16。大屏：主标题88、正文最低24、卡标题32，64边距，左信息/行动、右三列两行卡，横26纵24。所有实际文字盒逐对审查，每布局25盒/300对，四布局1200对无正面积重叠，原文字在各盒完整可见。设计tokens记录各位置/组件规则与真实字号，不以不同文字替换内容。

## 真看图与视觉迭代

root最终真实view为mobile000005、tablet000006、desktop000011、stage000015；另外真看过首成功stage000012。手机/平板/桌面完整原文、等级与元数据联系清楚，无裁切；大屏首成功图C1/C2/C6detail出现单字孤立尾行，按实际观察将detail移到卡全宽302、badge与title对齐。重render并再看，原文/26px字号不变，尾字孤行消除，完成1次实际视觉迭代。生产者/独立审查者完整图和局部真看记录均在views.jsonl。

## 真实500诊断和恢复

最初desktop/stage各HTTP500 INTERNAL_ERROR Snapshot rendering failed（不是PNG，不作最终图）；无Retry-After。两次相同DSL重试仍500，替换唯一Transform分隔线的两个诊断仍500，因此没有将它归因Transform；桌面去掉全部25Text仍500、只保留78px标题诊断200。然后从原完整两DSL只改motif圆角3→8，desktop/stage均200；真实受控改动相关性明确，服务内部根因未确认，不能声称已读服务堆栈或证明内部负半径实现。最终motif半径mobile/tablet3、desktop/stage8，边宽2/3/4/5；避免半径小于边宽。所有原失败/重试/诊断/首图与版本均完整保留。

v004最初误用syntax-fix标签，实际HTTP500并非PARSE_ERROR；已追加实际alternative分类修正记录，原标签记录保留。最终统计语法修复0，不把服务几何恢复伪称语法修复或完整视觉迭代。

## 文档、工具、请求与消耗

实际复用共享服务guide、parser的Container/border/radius/Stack/Positioned/Text/Raw、fonts及A11真实Text/RichText文档缓存；本题新增文档/fonts请求0，复用不重复计新HTTP。Node生成四全DSL、逐字段map和tokens；真实POST UTF-8 text/plain，成功原PNG、失败原JSON/headers完整留存；view_image真正逐图查看，独立代码检查文字盒/源串/无Image，必要QA裁片只存临时。

实际13render：6成功、7失败，含2同DSL重试；13归档版本、6探索/诊断版本、1完整视觉迭代、语法修复0，实际看图16次（以最终指标为准）。四最终响应字节74134/105031/126079/140879；标题诊断及首stage另计成功请求，但不算最终作品。每次真实requestId/Server-Timing、请求耗时/字节与墙钟在task-metrics.json；未知token/图像输入计费/费用用null，文件字节不是计费代理。

输出 D:\workspaces\gpt-6.1-sol-ultra\outputs\20261002-204314-6f31\A12，临时 D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\A12。未缺交付；服务内部错误原因仍未知但实际恢复已完成。单题关闭后继续A13，全套最终审查尚未完成。


独立审计JSON组装另有4次真实本地命令/脚本失败（数字开头key、PowerShell行内转义、缺脚本），由审查者明确报告并在independent-analysis/assembly-failures-v001/v002等版本证据留存；修复后的最终JSON通过。它们不影响真实PNG、不计HTTP失败或视觉迭代，未删除旧尝试。共享publish-reviewed-set.cjs在本题首次实际用于4图及JSON发布，publication-result-v001.json保存实际结果；此前只做过--help。


## Root final review

A12-view-000005: Root actually viewed360×800 mobile: Structure / Vision naturally wraps into two40px lines without shortening; fullsubtitle/date/time/location/CTA/website and allC1–C6 ids/titles/details readable. Six single-columncards,body16/cardtitle18,amplecardgaps,allcontent intact and no overlap. Sameink/cream/teal/lime two-frame motif,CTA connects towebsite.

A12-view-000006: Root actually viewed768×1024 tablet: fulltitle64px andsubtitle,metadata,all6cards in2×3 complete withoriginalids/detail;body≥20,consistentcream/teal/lime/ink motif andCTA/website. Fields safely arranged withnonecut,nooverlap,legible typographic hierarchy.

A12-view-000011: Root actual1440×900 full desktop recovered image: fulltitle/subtitle/metadata/CTA/website andall6 original cardIDs/titles/details intact,body≥20 safe48; coherent2×3card composition withleftinformation. Motifradius8 retains double-frame identity; no visual defect.

A12-view-000015: Root actual1920×1080 finalstage compared with firstsuccessfulstage: full-width302px detailboxes now display C1/C2/C6 complete single lines,orphan tail characters removed withoutwordrewrite/fontreduction; badges aligned withtitle row. All25original fields intact,3×2 cards/metadata/CTA/website coherent,sharedpalette/two-frame motif retained,safe64px and nooverlap/cut. Allfour actual finalsizes rootreviewed.
