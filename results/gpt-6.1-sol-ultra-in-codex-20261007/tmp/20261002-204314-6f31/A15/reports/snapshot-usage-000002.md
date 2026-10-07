# A15 · 复杂界面视觉复刻

同一运行 20261002-204314-6f31，复刻原1440×900界面。最终 reconstructed.png 是真实HTTP200服务原始PNG，配对完整 reconstructed.snapshot，无后处理、无Image标签、未嵌参考或裁片。保留220px深蓝侧栏、选中Overview、三KPI、导出按钮、六柱收入图、活动、三行项目表和左下workspace/页脚。54处原文逐叶Raw CDATA完整保留，参考仅用于观察与测量；输入未改。

## 比例、锚点与真实视觉审查

root及制作/独立审查者真实查看参考原图、720缩略和图表/表格局部，也查看最终原图与同类QA。root最终原图 A15-view-000034，缩略/局部 A15-view-000036/A15-view-000037/A15-view-000038。reconstruction-audit.json包含root初始27估计与独立18实测锚点，涵盖四象限、图表/表格，结构最大误差0px（允许±8）。像素边界核心/AA与几何计算区分：0–120轴144px，每千元1.2px；五grid y405/441/477/513/549，六bar高度64.8/86.4/75.6/108/97.2/129.6，Apr–Sep比例与标记正确。3行Atlas/Pulse/Orbit，owner/due和蓝In progress/琥珀Review/绿Done均原样。

首次真实查看发现主title宽20px、section宽11–14px，进行一次真实字体迭代：main/KPI34→32px、section24→22px，微调y/墨色；卡片/bar几何不变。再次render、实际看图与旧/reference比较，选取标题字墨框已匹配，3KPI y低1px。不同阈值/纯墨方法的文字边缘支持差异留原证据，不用子集匹配声称全图逐像素相同。comparison.md明确颜色、次要字形和AA残差；整图pixel residual未计算为null。

## 文档、工具与实际消耗

复用真实共享服务指南、fonts与Container/Border/Stack/Positioned/Text/Raw/Transform文档，font选真实列表Inter。Node生成完整纯DSL与几何；Python/Pillow只读采样/连通域/bbox及QA缩略裁片，最终PNG不改；view_image逐图真实视觉检查。缓存复用不重计HTTP；本题新增文档/fonts0。

当前2渲染，2成功、0失败、0重试；2版本，1完整视觉迭代，38实际查看事件。以关闭后指标为最终统计。未发生Snapshot服务失败，不补造错误；所有baseline/脚本/请求headers/响应/QA/审计保存。token、图像输入使用与费用平台未提供，null；墙钟、请求耗时与实际字节分别记录，不估计账单。

输出 D:\workspaces\gpt-6.1-sol-ultra\outputs\20261002-204314-6f31\A15；临时 D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\A15。本题内容审查无缺项，文件发布审计后立即A16；全套最终审查仍待后续完成。


## Root final review

A15-view-000034: 恢复后重新实际打开1440×900 v002并与再次实际打开reference比较：主标题/三section字体宽度贴近，侧栏/选中导航、三KPI、6柱图、活动、3表行及状态/页脚完整；未見裁切重叠。保持真实比例与关键边界，细微字形/AA及KPI y约1px残差如实保留。
